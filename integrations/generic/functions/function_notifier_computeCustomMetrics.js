/*---
thehive:
  name: computeCustomMetrics
  mode: Enabled
  author: Fabien Bloume, StrangeBee
  definition: function_notifier_computeCustomMetrics
  description: |
    Computes two incident response metrics on TheHive cases and writes them as custom fields.

    ## Metrics

    **Time-to-Respond (TTR)**
    How long (in minutes) between the case start date and the *earliest* started task in the
    "Communication", "Containment", or "Eradication" task groups.
    Answers: "How quickly did we begin responding?"

    **Time-to-Contain (TTC)**
    How long (in minutes) between the case start date and the *latest* started task in the
    "Containment" task group.
    Answers: "How long until the threat was fully contained?"

    ## Modes

    - **Event-driven** (recommended): Attach as a Notifier to a case/task update notification.
      Computes metrics for the notified case only. A good example is to trigger the function based on CaseClosed event.
    - **Batch**: Call via the API with an empty body `{}` to backfill metrics on existing cases
      (processes the first 80 cases per run).

    ## Required custom fields

    Create these four custom fields in your tenant before using:
      - `timestamp-time-to-respond` (Date)
      - `time-to-respond-in-minutes` (Number)
      - `timestamp-time-to-contain` (Date)
      - `time-to-contain-in-minutes` (Number)

    ## Requirements

    - Task groups in your case templates must match the names used in this function
      ("Communication", "Containment", "Eradication"). Adjust the constants in the code
      if your naming differs.
    - Tasks must have been *started* (have a startDate) to be counted.
    - Cases with no matching started tasks are skipped.

    The baseline date used as t0 for all metrics is controlled by the `BASELINE_DATE`
    constant at the top of the script. Default is `startDate` (time the event occurred).
    Other options: `_createdAt` (case created in TheHive), `newDate` (first New-stage
    status), `inProgressDate` (first InProgress-stage status).

    Metric definitions follow SOC-101 and the SANS Incident Handler's Handbook.
    Adapt task groups, field names, and computation logic to fit your workflows.
  type: Notifier
  vendor: Generic
  kind: function
  version: 2.0.0
---*/

// ---------------------------------------------------------------------------
// Baseline date field used as t0 for all metrics.
// Options: "startDate"      (time the event occurred; shown as Start date in UI)
//          "_createdAt"     (time the case was created in TheHive)
//          "newDate"        (first time the case entered a New-stage status)
//          "inProgressDate" (first time the case entered an InProgress-stage status)
// ---------------------------------------------------------------------------
const BASELINE_DATE = "startDate";

// ---------------------------------------------------------------------------
// Metric definitions — add or edit entries here to extend to 3, 4+ metrics
// ---------------------------------------------------------------------------
const METRICS = [
  {
    taskGroups: ["Communication", "Containment", "Eradication"],
    timestampCustomField: "timestamp-time-to-respond",
    metricCustomField: "time-to-respond-in-minutes",
    timestampType: "earliest"
  },
  {
    taskGroups: ["Containment"],
    timestampCustomField: "timestamp-time-to-contain",
    metricCustomField: "time-to-contain-in-minutes",
    timestampType: "latest"
  }
];

// ---------------------------------------------------------------------------
// Resolve the best timestamp for a single task:
//   1. includeInTimeline from logs (preferred — reflects actual action time)
//   2. task.startDate (fallback)
//   3. null (task is excluded)
// ---------------------------------------------------------------------------
function getEffectiveTaskTimestamp(task, context, timestampType) {
  const logs = context.query.execute([
    { _name: "getTask", idOrName: task._id },
    { _name: "logs" }
  ]);

  const timelineTimestamps = logs
    .map(log => log.includeInTimeline)
    .filter(ts => ts !== undefined && ts !== null);

  if (timelineTimestamps.length > 0) {
    const picked = timestampType === "earliest"
      ? Math.min(...timelineTimestamps)
      : Math.max(...timelineTimestamps);
    console.log(`Task ${task._id} (${task.title}): using includeInTimeline from ${timelineTimestamps.length} log(s) → ${picked}`);
    return picked;
  }

  if (task.startDate !== undefined) {
    const fallback = new Date(task.startDate).getTime();
    console.log(`Task ${task._id} (${task.title}): no includeInTimeline found, falling back to startDate → ${fallback}`);
    return fallback;
  }

  console.log(`Task ${task._id} (${task.title}): no usable timestamp, skipping.`);
  return null;
}

// ---------------------------------------------------------------------------
// Compute one metric for a case and push the results into allUpdates.
// Does NOT write to TheHive — caller is responsible for the single update.
// ---------------------------------------------------------------------------
function collectMetric(caze, metric, context, allUpdates) {
  const { taskGroups, timestampCustomField, metricCustomField, timestampType } = metric;
  const caseStartDate = caze[BASELINE_DATE];

  const tasksOfCase = context.query.execute([
    { _name: "getCase", idOrName: caze._id },
    { _name: "tasks" }
  ]);

  const filteredTasks = tasksOfCase.filter(task => taskGroups.includes(task.group));
  console.log(`[${metricCustomField}] Filtered tasks: ${filteredTasks.length}`);

  const effectiveTimestamps = filteredTasks
    .map(task => getEffectiveTaskTimestamp(task, context, timestampType))
    .filter(ts => ts !== null);
  console.log(`[${metricCustomField}] Effective timestamps resolved: ${effectiveTimestamps.length}`);

  if (effectiveTimestamps.length === 0) {
    console.log(`[${metricCustomField}] No usable timestamps in groups [${taskGroups.join(", ")}] — skipping.`);
    return;
  }

  const targetTs = timestampType === "earliest"
    ? Math.min(...effectiveTimestamps)
    : Math.max(...effectiveTimestamps);

  let metricTimeMinutes = null;
  let timestampValue = targetTs;

  if (Number.isFinite(targetTs) && Number.isFinite(caseStartDate)) {
    metricTimeMinutes = parseFloat(((targetTs - caseStartDate) / (60 * 1000)).toFixed(1));
  } else {
    console.log(`[${metricCustomField}] Cannot compute — caseStartDate: ${caseStartDate}, targetTs: ${targetTs}`);
    timestampValue = null;
  }

  console.log(`Value for ${timestampCustomField}: ${timestampValue}`);
  console.log(`Value for ${metricCustomField}: ${metricTimeMinutes}`);

  allUpdates.push({ name: timestampCustomField, value: timestampValue });
  allUpdates.push({ name: metricCustomField, value: metricTimeMinutes });
}

// ---------------------------------------------------------------------------
// Compute ALL metrics for a case and write them in a single update call.
// ---------------------------------------------------------------------------
function computeAndUpdateCase(caze, context) {
  console.log("---------------------");
  console.log(`Processing case ID: ${caze._id} — Case Number: ${caze.number}`);

  const allUpdates = [];
  METRICS.forEach(metric => collectMetric(caze, metric, context, allUpdates));

  if (allUpdates.length === 0) {
    console.log("No metric updates to write — skipping case update.");
    return;
  }

  const customFieldsUpdated = updateOrAddCustomFields(caze.customFields, allUpdates);
  context.caze.update(caze._id, { customFields: customFieldsUpdated });
  console.log("Case update completed — all metrics written in one call.");
  console.log("--");
}

// ---------------------------------------------------------------------------
// Batch: iterate over a page of cases
// ---------------------------------------------------------------------------
function processCases(filtersQuery, context) {
  console.log("---------------------");
  console.log("Batch mode: listing cases...");
  const list = context.query.execute(filtersQuery);
  console.log(`Cases found: ${list.length}`);
  list.forEach(caze => computeAndUpdateCase(caze, context));
}

// ---------------------------------------------------------------------------
// Merge custom field updates into the existing array (update or append)
// ---------------------------------------------------------------------------
function updateOrAddCustomFields(customFields, customFieldUpdates) {
  customFieldUpdates.forEach(customFieldUpdate => {
    if (customFieldUpdate.value === null || customFieldUpdate.value === '') {
      return;
    }

    let fieldFound = false;

    customFields = customFields.map(field => {
      if (field.name === customFieldUpdate.name) {
        fieldFound = true;
        return { ...field, value: customFieldUpdate.value };
      }
      return field;
    });

    if (!fieldFound) {
      customFields.push({ name: customFieldUpdate.name, value: customFieldUpdate.value });
    }
  });

  return customFields;
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------
function handle(input, context) {
  if (Object.entries(input).length === 0 && input.constructor === Object) {
    console.log("HANDLE - No input — Batch mode");
    processCases([{ _name: "listCase" }, { _name: "page", from: 0, to: 80 }], context);
  } else {
    console.log("HANDLE - Input found — Event-driven");
    computeAndUpdateCase(input, context);
  }
}