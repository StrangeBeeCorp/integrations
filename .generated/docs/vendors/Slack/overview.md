## Use Cases (2)

### Real-world integrations with TheHive

#### [Notify Slack When a Case Assignee Changes in TheHive](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Slack/use-cases/slack-case-assignee-change.md)
For each assignee change for a case in TheHive, create a Slack block message and link to the case. @here will inform only active users.


#### [Notify Slack When an Alert Is Created in TheHive](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Slack/use-cases/slack-notifier-alert-creation.md)
For each new alert in TheHive, create a Slack block message with a title, severity & link to the alert.


---

## Responders (2)

### Trigger automated responses

#### [Slack SyncChannel v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Slack)
Syncs Slack channel conversations to TheHive task logs. Imports messages chronologically with file attachments for traceability.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`

#### [Slack CreateChannel v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Slack)
Creates a Slack channel for a TheHive case, invites participants, and optionally posts a case summary and description.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`

---

## Notifier

### Notify external systems when events occur

This integration is available as a built-in [TheHive notifier](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-notifications/about-notifications/).

---

## TheHive Flow node (1)

### Orchestrate this vendor from TheHive Flow workflows

Notify, coordinate and interact with people in Slack during an incident.

**Example use cases:**

- Post a notification in the SOC channel when a critical case is created
- Create a dedicated war-room channel per major incident and invite responders
- DM a user to confirm whether they performed a suspicious action

TheHive Flow is TheHive's native automation and orchestration engine, available exclusively with the TheHive ONE plan.

---

## Workflow (1)

### Ready-to-use TheHive Flow workflows

- [Slack Alert Manager](https://strangebee.com/workflow/slack-alert-manager-workflow/) - The Slack Alert Manager workflow automates alert monitoring and response tracking through Slack. It processes reactions, comments, and thread replies to update alert statuses, ensuring timely follow-ups and efficient incident management.
