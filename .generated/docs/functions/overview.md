# Functions Catalog

Example functions for TheHive. Use them as-is or as inspiration for your own.

**Create your own:** [Functions](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-functions/create-a-function/) - [Feeders](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-feeders/create-a-feeder/)

## Summary

- **Total Functions:** 17
- **Generic Functions:** 11
- **Vendor-Specific Functions:** 6
- **Vendors with Functions:** 5

## Generic Functions

These functions are vendor-agnostic and can be used across all TheHive installations:

### [alertfeeder_ingestSentinelIncidents](alertfeeder_ingestsentinelincidents.md) `v1.0.0`

**Type:** Feeder
**Mode:** Enabled

Ingests Microsoft Sentinel incidents from the Microsoft 365 Defender API and creates TheHive alerts, one per incident

[View full documentation](alertfeeder_ingestsentinelincidents.md)

---

### [assignAlert](assignalert.md) `v1.0.0`

**Type:** Notifier
**Mode:** Enabled

This function is designed to trigger on alert creation event. It automatically assignes severity High & Critical alerts to a given user

[View full documentation](assignalert.md)

---

### [assignToMe](assigntome.md) `v1.0.0`

**Type:** Action:Case
**Mode:** Enabled

This function changes the assignee of the Case and all the associated tasks to the user who launches the function

[View full documentation](assigntome.md)

---

### [automatedIgnoreSimilarityForNoisyObservables](automatedignoresimilarityfornoisyobservables.md) `v1.0.0`

**Type:** Notifier
**Mode:** Enabled

This function is intended to be triggered on ObservableCreated events. It automatically sets ignoreSimilarity to true for observables matching a known list of common, noisy, or non-actionable values (such as localhost, private IPs, and generic hostnames..). This reduces alert noise and avoids false correlation in TheHive. Note that it is a workaround, and such issues are better managed in your alert ingestion pipeline(s)

[View full documentation](automatedignoresimilarityfornoisyobservables.md)

---

### [changeImportedAlertStatus](changeimportedalertstatus.md) `v1.0.0`

**Type:** Notifier
**Mode:** Enabled

This function is designed to trigger on case closed event. It automatically changes imported alerts to a given custom status

[View full documentation](changeimportedalertstatus.md)

---

### [Check IP RFC 1918/4193](check-ip-rfc-1918-4193.md) `v1.0.0`

**Type:** Notifier
**Mode:** Enabled

Checks the IP Observable type and tags it as "ip:public", "ip:private", or "ip:invalid" based on RFC 1918/4193. For both IPv4 and IPv6.

[View full documentation](check-ip-rfc-1918-4193.md)

---

### [coldCaseAutomation](coldcaseautomation.md) `v1.0.0`

**Type:** API
**Mode:** Enabled

This function will find the "New" or "InProgress" cases that were not updated since one month. For each case, add a tag "cold-case"

[View full documentation](coldcaseautomation.md)

---

### [computeCustomMetrics](computecustommetrics.md) `v2.0.0`

**Type:** Notifier
**Mode:** Enabled

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


[View full documentation](computecustommetrics.md)

---

### [computeTotalTimeSpent](computetotaltimespent.md) `v1.0.0`

**Type:** Notifier
**Mode:** Enabled

On task closure, compute the duration of the task rounded up to the nearest minute. It's then added to the TASK_TIME_CUSTOMFIELD integer customfield at the case level. Use a trigger "task closed"

[View full documentation](computetotaltimespent.md)

---

### [deleteIPObsFromAlert](deleteipobsfromalert.md) `v1.0.0`

**Type:** Action:Alert
**Mode:** Enabled

This function will delete all the IP Observable from an alert

[View full documentation](deleteipobsfromalert.md)

---

### [externalAccessAutomation](externalaccessautomation.md) `v1.0.0`

**Type:** Notifier
**Mode:** Enabled

Automatically grants external case access to client users when a case is closed. It reads the client custom field from the case, extracts the company domain label, and retrieves the external users linked to the case. Users whose email domain matches the client domain are identified and granted external access to the case.

[View full documentation](externalaccessautomation.md)

---

## Vendor-Specific Functions

### Airtable

**Vendor:** [Airtable](../vendors/Airtable/overview)

#### [alertFromAirtable](airtable-alertfromairtable.md) `v1.0.0`
**Kind:** `function`

This function creates alerts from data coming from a Airtable database. It checks the alert does not already exist, then creates the alert, and completes type, source, source-ref, title, description and tags

[View full documentation](airtable-alertfromairtable.md)

---

### JAMFProtect

**Vendor:** [JAMFProtect](../vendors/JAMFProtect/overview)

#### [createAlertFromJAMFProtect](jamfprotect-createalertfromjamfprotect.md) `v1.0.0`
**Kind:** `function`

Ingests alerts from JAMF Protect. Extracts analytic details, host and user information, MITRE ATT&CK tags, and file/path data. The function constructs a TheHive alert, including a title, markdown-formatted description (with original alert JSON), relevant observables (IP, hostname, file, hash, URL, FQDN, URI path, user agent), MITRE ATT&CK enrichment, and a link to the JAMF alert. Handles default values and supports tagging and mapping of MITRE tactics for easier triage and investigation. For the setup in JAMF Protect, go to Configuration > Actions > *your action* > Add an HTTP data endpoint + your Authorization Header and Bearer as value

[View full documentation](jamfprotect-createalertfromjamfprotect.md)

---

### JIRA

**Vendor:** [JIRA](../vendors/JIRA/overview)

#### [alertFromJIRA](jira-alertfromjira.md) `v1.0.0`
**Kind:** `function`

This function creates alerts from JIRA issues. It checks if the alert already exists, then creates it with type, source, source-ref, title, and description

[View full documentation](jira-alertfromjira.md)

---

### Proofpoint

**Vendor:** [Proofpoint](../vendors/Proofpoint/overview)

#### [alertFeeder_ProofPoint_clicksPermitted](proofpoint-alertfeeder_proofpoint_clickspermitted.md) `v1.0.0`
**Kind:** `function`

Ingests ProofPoint clicksPermitted alerts in TheHive

[View full documentation](proofpoint-alertfeeder_proofpoint_clickspermitted.md)

#### [alertFeeder_ProofPoint_messageDelivered](proofpoint-alertfeeder_proofpoint_messagedelivered.md) `v1.0.0`
**Kind:** `function`

Ingests ProofPoint messageDelivered alerts in TheHive

[View full documentation](proofpoint-alertfeeder_proofpoint_messagedelivered.md)

---

### Splunk

**Vendor:** [Splunk](../vendors/Splunk/overview)

#### [createAlertFromSplunk](splunk-createalertfromsplunk.md) `v1.0.0`
**Kind:** `function`

This function creates a TheHive Alert based on an input coming from Splunk, and matches the Splunk fields to TheHive fields. In Splunk, you'll need to configure the webhook URL to point to the TheHive function URL

[View full documentation](splunk-createalertfromsplunk.md)

---

---

*This catalog is auto-generated. Do not edit manually.*
