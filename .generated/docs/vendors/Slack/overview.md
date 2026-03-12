## Use Cases (2)

### Notify Slack When an Alert Is Created in TheHive
For each new alert in TheHive, create a Slack block message with a title, severity & link to the alert.

- **Documentation:** [View tutorial](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Slack/use-cases/slack-notifier-alert-creation.md)

---

### Notify Slack When a Case Assignee Changes in TheHive
For each assignee change for a case in TheHive, create a Slack block message and link to the case. @here will inform only active users.

- **Documentation:** [View tutorial](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Slack/use-cases/slack-case-assignee-change.md)

---

## Responders (2)

### [Slack CreateChannel v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Slack)
Creates a Slack channel for a TheHive case, invites participants, and optionally posts a case summary and description.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`

### [Slack SyncChannel v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Slack)
Syncs Slack channel conversations to TheHive task logs. Imports messages chronologically with file attachments for traceability.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`
