## Use Cases (2)

*Real-world integrations with TheHive*

### [Notify Slack When an Alert Is Created in TheHive](https://github.com/StrangeBeeCorp/integrations/blob/develop/integrations/vendors/Slack/use-cases/slack-notifier-alert-creation.md)
For each new alert in TheHive, create a Slack block message with a title, severity & link to the alert.


### [Notify Slack When a Case Assignee Changes in TheHive](https://github.com/StrangeBeeCorp/integrations/blob/develop/integrations/vendors/Slack/use-cases/slack-case-assignee-change.md)
For each assignee change for a case in TheHive, create a Slack block message and link to the case. @here will inform only active users.


---

## Responders (2)

*Trigger automated responses*

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

---

## Notifier

*Notify external systems when events occur*

This integration is available as a built-in [TheHive notifier](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-notifications/about-notifications/).
