/*---
thehive:
  name: alertFeeder_SOCRadar_incidents
  mode: Enabled
  definition: function_Feeder_alertFromSOCRadar
  description: Ingests SOCRadar XTI alarms from the Incident API v4 as TheHive alerts, deduplicated on company_id:alarm_id
  type: Feeder
  vendor: SOCRadar
  kind: function
  version: 1.0.0
  author: Burak Goger, SOCRadar Cyber Intelligence Inc.
---*/

// ---- Settings: edit these when you create the function --------------------
// One alert feeder (every 5 minutes) runs this function. It alternates between:
// - recent passes: alarms created since the newest alarm already seen, page
//   after page, so a burst of new alarms is ingested in one go;
// - a lookback pass every LOOKBACK_INTERVAL_MINUTES: every page of the last
//   LOOKBACK_DAYS days, which catches alarms that became visible in SOCRadar
//   after a delay (for example, late approval).
//
// A feeder URL is static and a run reads one page, so the function writes the
// next request URL to a cursor alert. A notification on that cursor alert updates
// the feeder URL through the TheHive API, which runs the feeder again right away.
// Without that notification the function only ingests the page the feeder
// requests and raises a daily health alert.
const COMPANY_ID = "<company_id>";
const API_BASE = "https://platform.socradar.com/api";
// Optional filters appended to every request, e.g. "&severities=HIGH&severities=CRITICAL"
const EXTRA_QUERY = "";
const PAGE_SIZE = 100;
const LOOKBACK_DAYS = 5;
const LOOKBACK_INTERVAL_MINUTES = 60;
// A feeder run must finish within 1 minute or TheHive rolls back everything it
// created. Alarms over this cap are created on the next run.
const MAX_NEW_ALERTS_PER_RUN = 200;
// ----------------------------------------------------------------------------

// Field limits enforced by TheHive on alert creation (POST /api/v1/alert).
// The SOCRadar API does not truncate any field, so every value is clipped here.
const LIMITS = {
  title: 512,
  description: 1048576,
  sourceRef: 128,
  externalLink: 4096,
  tag: 128,
  observableData: 4096,
};
// Keep room for the sections that follow the long free-text fields
const SECTION_LIMIT = 200000;
const CONTENT_LIMIT = 300000;
// Alarm content is a free-form dict whose shape depends on the alarm type. It is
// copied in full, but each long string and long list is shortened and marked.
const MAX_VALUE_CHARS = 2000;
const MAX_LIST_ITEMS = 100;
const MAX_DEPTH = 10;

const SOURCE = "SOCRadar";
const ALERT_TYPE = "socradar-alarm";
const ALARM_LINK =
  "https://socradar.com/app/company/{company_id}/alarm-management?tab=approved&field=alarmId&operator=equals&value={alarm_id}";

const severityMap = { LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };

// Keys whose values are never copied into TheHive (leaked credentials)
const SENSITIVE_KEYS = /^(password|passwd|pass|pwd|secret|token|cookie|cookies)$/i;

function clip(value, max) {
  if (value === undefined || value === null) return "";
  const str = String(value);
  if (str.length <= max) return str;
  const marker = "... [truncated]";
  return str.slice(0, Math.max(0, max - marker.length)) + marker;
}

function toList(value) {
  if (value === undefined || value === null || value === "") return [];
  return Array.isArray(value) ? value : [value];
}

function toText(value) {
  if (value === undefined || value === null) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

// SOCRadar returns "YYYY-MM-DD HH:MM:SS" in UTC without a timezone suffix
function parseDate(value) {
  if (!value) return null;
  let str = String(value).trim();
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?$/.test(str)) str = str.replace(" ", "T") + "Z";
  const ts = new Date(str).getTime();
  return isNaN(ts) ? null : ts;
}

// Redacts credentials and shortens long values, keeping the structure readable
function protect(value, depth) {
  depth = depth || 0;
  if (typeof value === "string") {
    if (value.length <= MAX_VALUE_CHARS) return value;
    return value.slice(0, MAX_VALUE_CHARS) + "... [truncated, " + value.length + " characters total]";
  }
  if (value === null || typeof value !== "object") return value;
  if (depth >= MAX_DEPTH) return "[truncated, nested deeper than " + MAX_DEPTH + " levels]";
  if (Array.isArray(value)) {
    const out = value.slice(0, MAX_LIST_ITEMS).map((v) => protect(v, depth + 1));
    if (value.length > MAX_LIST_ITEMS) out.push("[truncated, " + (value.length - MAX_LIST_ITEMS) + " more items]");
    return out;
  }
  const out = {};
  Object.keys(value).forEach((key) => {
    out[key] = SENSITIVE_KEYS.test(key) && value[key] ? "[REDACTED]" : protect(value[key], depth + 1);
  });
  return out;
}

function jsonSection(heading, value) {
  if (value === undefined || value === null) return "";
  if (typeof value === "object" && !Object.keys(value).length) return "";
  return "## " + heading + "\n\n" +
    "Credential values are redacted. Values over " + MAX_VALUE_CHARS + " characters and lists over " + MAX_LIST_ITEMS +
    " items are shortened and marked [truncated].\n\n```json\n" +
    clip(JSON.stringify(protect(value), null, 2), CONTENT_LIMIT) + "\n```\n\n";
}

// Alarm fields already rendered in the summary table or their own sections
const SHOWN_FIELDS = ["alarm_id", "company_id", "company_name", "alarm_risk_level", "status", "alarm_asset", "date",
  "last_notification_date", "alarm_text", "alarm_response", "alarm_related_assets", "alarm_related_entities", "tags",
  "content", "alarm_type_details"];
const SHOWN_DETAILS = ["alarm_main_type", "alarm_sub_type", "alarm_generic_title", "alarm_default_mitigation_plan",
  "alarm_detection_and_analysis", "alarm_compliance_list"];

function otherFields(alarm, details) {
  const out = {};
  Object.keys(alarm).forEach((key) => { if (SHOWN_FIELDS.indexOf(key) < 0) out[key] = alarm[key]; });
  const extraDetails = {};
  Object.keys(details).forEach((key) => { if (SHOWN_DETAILS.indexOf(key) < 0) extraDetails[key] = details[key]; });
  if (Object.keys(extraDetails).length) out.alarm_type_details = extraDetails;
  return out;
}

// Responses are either { data: [...] } or, with include_total_records=true, { data: { alarms: [...] } }
function extractAlarms(input) {
  if (Array.isArray(input)) return input;
  if (!input || typeof input !== "object") return [];
  if (input.is_success === false) {
    throw new Error("SOCRadar API error: " + (input.message || "unknown error") + " (response_code " + input.response_code + ")");
  }
  if (input.error) throw new Error("SOCRadar API error: " + input.error);
  const data = input.data;
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.alarms)) return data.alarms;
  if (Array.isArray(input.alarms)) return input.alarms;
  return [];
}

// include_total_records=true adds total_pages next to the alarms
function extractTotalPages(input) {
  const data = input && input.data;
  return data && typeof data.total_pages === "number" ? data.total_pages : null;
}

function inferDataType(value) {
  if (/^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/.test(value)) return "ip";
  if (/^[0-9a-f:]+$/i.test(value) && value.includes(":") && value.split(":").length > 2) return "ip";
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return "mail";
  if (/^https?:\/\//i.test(value)) return "url";
  if (/^([a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64})$/i.test(value)) return "hash";
  if (/^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/i.test(value)) return "domain";
  return "other";
}

// Related assets and entities come as { key, value } objects, where value is a
// string, a number or a list. Keys mapped to null (brand keywords, DNS record
// changes, ports, internal IDs) stay in the description only: as observables
// they would link unrelated alerts together.
const RELATED_KEY_TYPES = {
  domain: "domain",
  hostname: "hostname",
  url: "url",
  effective_url: "url",
  ip: "ip",
  ip_address: "ip",
  email: "mail",
  cert_serial_number: "other",
  keyword: null,
  port: null,
};

function relatedItems(list) {
  const items = [];
  toList(list).forEach((entry) => {
    if (entry && typeof entry === "object" && !Array.isArray(entry) && "value" in entry) {
      toList(entry.value).forEach((v) => items.push({ key: toText(entry.key), value: toText(v) }));
    } else {
      items.push({ key: "", value: toText(entry) });
    }
  });
  return items.filter((i) => i.value);
}

function relatedDataType(key, value) {
  if (Object.prototype.hasOwnProperty.call(RELATED_KEY_TYPES, key)) return RELATED_KEY_TYPES[key];
  const inferred = inferDataType(value);
  return inferred === "other" ? null : inferred;
}

// Related assets/entities give context; they are never flagged as IOCs
function buildObservables(alarm, skipped) {
  const observables = [];
  const seen = {};
  const add = (dataType, value, tags) => {
    if (!dataType || !value) return;
    if (value.length > LIMITS.observableData) {
      skipped.push(value.slice(0, 80) + "...");
      return;
    }
    const id = dataType + "|" + value;
    if (seen[id]) {
      tags.forEach((t) => { if (seen[id].tags.indexOf(t) < 0) seen[id].tags.push(t); });
      return;
    }
    const observable = { dataType: dataType, data: value, ioc: false, tags: ["SOCRadar"].concat(tags) };
    seen[id] = observable;
    observables.push(observable);
  };
  // The alarm asset is often a company or brand name; only technical values are kept
  toList(alarm.alarm_asset).forEach((v) => {
    const value = toText(v);
    const dataType = inferDataType(value);
    if (dataType !== "other") add(dataType, value, ["alarm-asset"]);
  });
  relatedItems(alarm.alarm_related_assets).forEach((i) =>
    add(relatedDataType(i.key, i.value), i.value, ["related-asset"].concat(i.key ? [clip(i.key, LIMITS.tag)] : [])));
  relatedItems(alarm.alarm_related_entities).forEach((i) =>
    add(relatedDataType(i.key, i.value), i.value, ["related-entity"].concat(i.key ? [clip(i.key, LIMITS.tag)] : [])));
  return observables;
}

function buildTags(alarm, details) {
  const tags = [
    "SOCRadar",
    details.alarm_main_type && "main-type:" + details.alarm_main_type,
    details.alarm_sub_type && "sub-type:" + details.alarm_sub_type,
    alarm.alarm_risk_level && "severity:" + alarm.alarm_risk_level,
    alarm.status && "status:" + alarm.status,
    ...toList(alarm.tags).map(toText),
  ];
  const unique = [];
  tags.forEach((tag) => {
    const value = clip(toText(tag), LIMITS.tag);
    if (value && unique.indexOf(value) < 0) unique.push(value);
  });
  return unique;
}

function section(heading, body) {
  const text = toText(body);
  return text ? "## " + heading + "\n\n" + clip(text, SECTION_LIMIT) + "\n\n" : "";
}

function buildDescription(alarm, details, link, skipped) {
  const compliance = toList(details.alarm_compliance_list)
    .map((c) => "- **" + toText(c.name) + "** " + toText(c.control_item) + (c.description ? ": " + toText(c.description) : ""))
    .join("\n");
  const line = (label) => (i) => "- " + label + (i.key ? " (" + i.key + ")" : "") + ": " + i.value;
  const related = [
    ...relatedItems(alarm.alarm_related_assets).map(line("Asset")),
    ...relatedItems(alarm.alarm_related_entities).map(line("Entity")),
  ].join("\n");

  const summary =
    "| Field | Value |\n|---|---|\n" +
    "| Alarm ID | " + alarm.alarm_id + " |\n" +
    "| Risk level | " + toText(alarm.alarm_risk_level || "N/A") + " |\n" +
    "| Status | " + toText(alarm.status || "N/A") + " |\n" +
    "| Main type | " + toText(details.alarm_main_type || "N/A") + " |\n" +
    "| Sub type | " + toText(details.alarm_sub_type || "N/A") + " |\n" +
    "| Asset | " + toText(alarm.alarm_asset || "N/A").replace(/\|/g, "\\|") + " |\n" +
    "| Created (UTC) | " + toText(alarm.date || "N/A") + " |\n" +
    "| Last notification (UTC) | " + toText(alarm.last_notification_date || "N/A") + " |\n\n" +
    "[Open in SOCRadar](" + link + ")\n\n";

  const content = jsonSection("Alarm content", alarm.content) + jsonSection("Other alarm fields", otherFields(alarm, details));

  const description =
    summary +
    section("Alarm details", alarm.alarm_text) +
    section("Mitigation", alarm.alarm_response || details.alarm_default_mitigation_plan) +
    section("Detection and analysis", details.alarm_detection_and_analysis) +
    section("Related assets and entities", related) +
    section("Compliance", compliance) +
    (skipped.length ? section("Values not added as observables (over 4096 characters)", skipped.map((v) => "- " + v).join("\n")) : "") +
    content;
  return clip(description, LIMITS.description);
}

function buildAlert(alarm, companyId, alarmId, sourceRef, date) {
  const details = alarm.alarm_type_details || {};
  const link = companyId
    ? clip(ALARM_LINK.replace("{company_id}", encodeURIComponent(companyId)).replace("{alarm_id}", encodeURIComponent(alarmId)), LIMITS.externalLink)
    : "";
  const firstLine = toText(alarm.alarm_text).split("\n")[0];
  const name = toText(details.alarm_generic_title) || toText(alarm.title) || firstLine || "Alarm " + alarmId;
  const skipped = [];
  const observables = buildObservables(alarm, skipped);
  const tags = buildTags(alarm, details);
  if (!companyId) tags.push("socradar:missing-company-id");

  const alert = {
    type: ALERT_TYPE,
    source: SOURCE,
    sourceRef: sourceRef,
    title: clip("[SOCRadar] " + name, LIMITS.title),
    description: buildDescription(alarm, details, link || "https://socradar.com/app", skipped),
    severity: severityMap[toText(alarm.alarm_risk_level).toUpperCase()] || 2,
    date: date || Date.now(),
    tags: tags,
    observables: observables,
  };
  if (link) alert.externalLink = link;
  return alert;
}

// One query per chunk instead of one alert.find per alarm: 1000 lookups take
// well under a second this way, against ~20 seconds one by one.
function existingSourceRefs(sourceRefs, context) {
  const existing = {};
  for (let i = 0; i < sourceRefs.length; i += 250) {
    const chunk = sourceRefs.slice(i, i + 250);
    const found = context.query.execute([
      { _name: "listAlert" },
      { _name: "filter", _and: [{ _field: "source", _value: SOURCE }, { _in: { _field: "sourceRef", _values: chunk } }] },
      { _name: "page", from: 0, to: chunk.length * 2 },
    ]);
    (found || []).forEach((a) => { existing[a.sourceRef] = true; });
  }
  return existing;
}

// ---- Paging cursor -----------------------------------------------------------
// The cursor alert stores the next request URL in its description and the paging
// state in its summary. A description update triggers the notification that
// applies the URL to the feeder; a summary-only update doesn't. Updating the
// description with the same URL triggers it again, which is how a lost hop is
// retried.
const CURSOR_TYPE = "socradar-feeder";
// A hop runs the feeder within seconds. A run that starts later is a scheduled
// run, so the hop was not applied. Keep it below the feeder interval.
const HOP_TIMEOUT_MS = 45 * 1000;
const HOP_RETRIES_BEFORE_ALERT = 3;

function cursorRef() {
  return clip("socradar-cursor:" + COMPANY_ID, LIMITS.sourceRef);
}

function requestUrl(state) {
  return API_BASE + "/company/" + encodeURIComponent(COMPANY_ID) + "/incidents/v4?limit=" + PAGE_SIZE + "&page=" + state.page +
    "&include_company_id=true&include_total_records=true&start_date=" + state.startDate + EXTRA_QUERY;
}

function readCursor(context) {
  const found = context.alert.find([{ _name: "filter", _and: [
    { _field: "source", _value: SOURCE }, { _field: "sourceRef", _value: cursorRef() }] }]);
  if (!found || !found.length) return { alert: null, state: {} };
  let state = {};
  try { state = JSON.parse(found[0].summary || "{}"); } catch (e) { state = {}; }
  return { alert: found[0], state: state };
}

function lookbackPass(now) {
  return { pass: "lookback", page: 1, startDate: Math.floor((now - LOOKBACK_DAYS * 86400000) / 1000) };
}

// Decides the next request from the state and the page just received. Recent
// passes restart after the newest alarm seen, so with no new data the request
// returns nothing, the URL stays the same and the hop loop stops; only new data
// or a due lookback moves it.
function nextState(state, alarms, totalPages, now) {
  const newest = alarms.reduce((max, a) => Math.max(max, parseDate(a.date) || 0), 0);
  const hwm = Math.max(state.hwm || 0, newest);
  const keep = { hwm: hwm, lookbackEndedAt: state.lookbackEndedAt || 0 };
  if (!state.pass) return Object.assign(keep, lookbackPass(now));
  const page = state.page || 1;
  if (alarms.length >= PAGE_SIZE && (totalPages === null || page < totalPages)) {
    return Object.assign(keep, { pass: state.pass, page: page + 1, startDate: state.startDate });
  }
  if (state.pass === "lookback") keep.lookbackEndedAt = now;
  else if (now - keep.lookbackEndedAt >= LOOKBACK_INTERVAL_MINUTES * 60000) return Object.assign(keep, lookbackPass(now));
  // Start one second after the newest alarm: alarms of that second were read in
  // this pass, and an inclusive start would loop when 100+ share that second.
  // An alarm stored later within the same second is caught by the lookback pass.
  const startDate = hwm ? Math.floor(hwm / 1000) + 1 : Math.floor((now - LOOKBACK_DAYS * 86400000) / 1000);
  return Object.assign(keep, { pass: "recent", page: 1, startDate: startDate });
}

// Alarms older than the requested start_date mean the feeder ran an outdated URL,
// for example when another feeder update overwrote the hop
function staleRequest(state, alarms) {
  if (!state.startDate) return false;
  return alarms.some((a) => {
    const d = parseDate(a.date);
    return d !== null && d < state.startDate * 1000 - 1000;
  });
}

function reportBrokenPaging(state, now, context) {
  const day = new Date(now).toISOString().slice(0, 10);
  try {
    context.alert.create({
      type: CURSOR_TYPE,
      source: SOURCE,
      sourceRef: clip("socradar-health:" + COMPANY_ID + ":" + day, LIMITS.sourceRef),
      title: "[SOCRadar] Paging isn't applied to the SOCRadar feeder",
      description:
        "The SOCRadar feeder function asked " + (state.hopRetries || 0) + " times for its next page, last at " +
        new Date(state.requestedAt).toISOString() + ", but the feeder URL wasn't updated. The feeder only reads the page " +
        "it is configured with, so alarms can be missed.\n\n" +
        "Check the notification that applies the cursor `" + cursorRef() + "` to the feeder: it must be enabled, " +
        "its TheHive API key must be valid, and its URL must point to this feeder. This alert is created at most once per day.",
      severity: 2,
      date: now,
      tags: ["SOCRadar", "feeder-health"],
    });
  } catch (e) {
    if (String(e).indexOf("already exists") < 0) console.log("SOCRadar feeder: health alert failed: " + String(e));
  }
}

function writeCursor(cursor, state, retry, now, context) {
  const url = requestUrl(state);
  const current = cursor.alert ? cursor.alert.description : "";
  const hop = retry || url !== current;
  const saved = Object.assign({}, state, { lastRunAt: now },
    hop ? { requestedAt: now, pendingHop: true, hopRetries: retry ? (cursor.state.hopRetries || 0) + 1 : 0 }
      : { pendingHop: false, hopRetries: 0 });
  const summary = JSON.stringify(saved);
  if (!cursor.alert) {
    context.alert.create({
      type: CURSOR_TYPE, source: SOURCE, sourceRef: cursorRef(), status: "Ignored", severity: 1, date: now,
      title: "[SOCRadar] Feeder cursor", description: url, summary: summary, tags: ["SOCRadar", "feeder-cursor"],
    });
  } else if (hop) {
    context.alert.update(cursor.alert._id, { description: url, summary: summary });
  } else {
    // Summary only: doesn't trigger the notification, so the feeder rests
    context.alert.update(cursor.alert._id, { summary: summary });
  }
  return { hop: hop, url: url, retries: saved.hopRetries };
}

function handle(input, context) {
  const alarms = extractAlarms(input);
  const totalPages = extractTotalPages(input);
  const now = Date.now();
  const cursor = readCursor(context);
  const horizon = now - LOOKBACK_DAYS * 86400000;
  const candidates = [];
  const seen = {};
  let outOfRange = 0;

  alarms.forEach((alarm) => {
    if (!alarm || alarm.alarm_id === undefined || alarm.alarm_id === null) return;
    // Disapproved alarms keep their alarm_id and can still be returned
    if (alarm.is_approved === false) return;
    const date = parseDate(alarm.date);
    if (date !== null && date < horizon) {
      outOfRange++;
      return;
    }
    const companyId = alarm.company_id !== undefined && alarm.company_id !== null ? String(alarm.company_id) : "";
    const alarmId = String(alarm.alarm_id);
    const sourceRef = clip((companyId || "unknown-company") + ":" + alarmId, LIMITS.sourceRef);
    if (seen[sourceRef]) return;
    seen[sourceRef] = true;
    candidates.push({ alarm: alarm, companyId: companyId, alarmId: alarmId, sourceRef: sourceRef, date: date });
  });

  // Deduplication
  const existing = existingSourceRefs(candidates.map((c) => c.sourceRef), context);
  const pending = candidates.filter((c) => !existing[c.sourceRef]);
  // Oldest first, so alarms deferred by the cap don't age out of the window
  pending.sort((a, b) => (a.date === null ? now : a.date) - (b.date === null ? now : b.date));

  let created = 0;
  let duplicates = 0;
  let failed = 0;
  pending.slice(0, MAX_NEW_ALERTS_PER_RUN).forEach((c) => {
    try {
      context.alert.create(buildAlert(c.alarm, c.companyId, c.alarmId, c.sourceRef, c.date));
      created++;
    } catch (e) {
      // Never rethrow: an uncaught error rolls back every alert created in this run
      if (String(e).indexOf("already exists") >= 0) {
        duplicates++;
      } else {
        failed++;
        console.log("SOCRadar feeder: alarm " + c.sourceRef + " not created: " + String(e));
      }
    }
  });
  const deferred = Math.max(0, pending.length - MAX_NEW_ALERTS_PER_RUN);

  // Written last: a timeout or error rolls back the cursor together with the alerts
  const state = cursor.state;
  const lostHop = state.pendingHop && state.requestedAt && now - state.requestedAt > HOP_TIMEOUT_MS;
  const retry = lostHop || deferred > 0 || staleRequest(state, alarms);
  if (lostHop && (state.hopRetries || 0) + 1 >= HOP_RETRIES_BEFORE_ALERT) reportBrokenPaging(state, now, context);
  // On a retry the feeder didn't read the requested page: ask for it again
  const next = retry && state.pass ? Object.assign({}, state) : nextState(state, alarms, totalPages, now);
  const result = writeCursor(cursor, next, retry && !!state.pass, now, context);

  console.log(
    "SOCRadar feeder (" + (state.pass || "start") + " pass, page " + (state.page || 1) + "): received " + alarms.length +
    (totalPages !== null ? " of " + totalPages + " pages" : "") + ", older than " + LOOKBACK_DAYS + " days " + outOfRange +
    ", already in TheHive " + (candidates.length - pending.length) + ", created " + created + ", deferred to next run " + deferred +
    ", duplicates " + duplicates + ", failed " + failed +
    (result.hop ? (retry ? ", retrying request " : ", next request ") + result.url : ", resting")
  );
}
