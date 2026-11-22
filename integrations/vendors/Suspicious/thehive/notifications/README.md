# Run Suspicious_Verdict Responder — TheHive Notification

## Overview

This notification automatically triggers the **Suspicious_Verdict** Responder
([StrangeBee/Cortex-Analyzers](https://github.com/TheHive-Project/Cortex-Analyzers))
whenever an analyst adds a `suspicious:verdict=` tag to a **Case** or an
**Alert** in TheHive.

It closes the loop between TheHive triage and
[**Suspicious**](https://github.com/thalesgroup-cert/suspicious), Thales
CERT's case management platform: tag the verdict → the responder runs → the
Suspicious investigation is updated — without any manual step.

| | |
|---|---|
| **Contributor** | THA-CERT // EB  |
| **Type** | `filteredEvent` |
| **Status** | working |
| **Related responder** | [Suspicious_Verdict](https://github.com/TheHive-Project/Cortex-Analyzers/) (Cortex-Analyzers repository) |
| **Related project** | [thalesgroup-cert/suspicious](https://github.com/thalesgroup-cert/suspicious) |

## Why two repositories?

This contribution is split across two StrangeBee repositories, matching their
respective scope:

| Repository | Content |
|---|---|
| [`TheHive-Project/Cortex-Analyzers`](https://github.com/TheHive-Project/Cortex-Analyzers) | The **Suspicious_Verdict Responder** itself (Cortex neuron: Python code, service interaction file, taxonomy) |
| [`StrangeBeeCorp/integrations`](https://github.com/StrangeBeeCorp/integrations) | This **notification** (TheHive-side automation that runs the responder above) |

The responder can be used entirely on its own (triggered manually). This
notification is an optional add-on that automates its execution. Both READMEs
link to each other so the full workflow is easy to follow from either side.

## How it works

The notification filters TheHive's event stream for:

- an object of type `Case` **or** `Alert`, **and**
- a tag-change event where a tag was **added** and its value **starts with**
  `suspicious:verdict=`.

When both conditions match, TheHive runs the `Suspicious_Verdict` responder
against the Case/Alert that was just tagged.

```json
{
  "name": "Run Suspicious_Verdict Responder",
  "description": "Notification that triggers Suspicious_Verdict Responder when a 'suspicious:verdict=' taxonomy tag is added to a Case or an Alert.",
  "contributor": "EB // THA-CERT",
  "type": "filteredEvent",
  "status": "working",
  "comment": "Triggers RunResponder 'Suspicious_Verdict' on Alert, and RunResponder 'Suspicious_Verdict' on Case.",
  "filter": {
    "_and": [
      {
        "_or": [
          { "_eq": { "_field": "objectType", "_value": "Case" } },
          { "_eq": { "_field": "objectType", "_value": "Alert" } }
        ]
      },
      {
        "_arrayMatch": {
          "_field": "details.tagChanges",
          "_filter": {
            "_and": [
              { "_eq": { "_field": "operation", "_value": "added" } },
              { "_startsWith": { "_field": "values", "_value": "suspicious:verdict=" } }
            ]
          }
        }
      }
    ]
  }
}
```

## Prerequisites

1. The **Suspicious_Verdict** responder must be installed, configured
   (`suspicious_url`, `suspicious_token`) and enabled for your organization —
   see its README in `Cortex-Analyzers`.
2. The **`suspicious`** taxonomy (shipped with the responder) must be
   imported into TheHive, so that the three verdict tags
   (`suspicious:verdict="SAFE"|"SUSPICIOUS"|"DANGEROUS"`) are available.

## Import into TheHive

1. Go to **Organization → Notifications** in TheHive.
2. Click **Add notification**, choose type **Run Responder / filtered event**, and paste the JSON definition above.
3. In the **action** section, select **both** **Suspicious_Verdict** responders:

   * **Suspicious_Verdict** for **Cases**
   * **Suspicious_Verdict** for **Alerts**

   Both actions must be selected. TheHive automatically determines which responder to run based on whether the matching event comes from a Case or an Alert.
4. Save and enable the notification for your organization.

## Usage

Once imported, no manual action is required beyond tagging:

1. An analyst tags a Case or Alert with, e.g., `suspicious:verdict="SAFE"`.
2. TheHive detects the tag addition and matches the notification filter.
3. TheHive runs **Suspicious_Verdict** automatically on that Case/Alert.
4. The matching Suspicious investigation is updated, and the Case/Alert is
   tagged `suspicious:status="challenge_reviewed."` on success.

## Files in this submission

```
notification/Suspicious_Verdict/
├── notification.json
└── README.md
```

