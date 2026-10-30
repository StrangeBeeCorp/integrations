## TheHive Flow node (1)

### Orchestrate this vendor from TheHive Flow workflows

Manage Microsoft Sentinel incidents and maintain Sentinel watchlists.

**Example use cases:**

- Import Sentinel incidents with their entities as TheHive alerts and observables
- Write the TheHive analysis back as a comment on the Sentinel incident
- Close the Sentinel incident with the right classification when the case is closed

TheHive Flow is TheHive's native automation and orchestration engine, available exclusively with the TheHive ONE plan.

---

## Function (1)

### Automate TheHive actions or ingest alerts

#### [alertfeeder_ingestSentinelIncidents](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/MSSentinel/thehive/functions/function_alertfeeder_ingestSentinelIncidents.js) `v1.0.0`
Polls Microsoft Sentinel/Defender alerts from the Microsoft Graph Security API (/security/alerts_v2), groups them by incidentId, and creates one TheHive alert per incident

- **Author:** Fabien Bloume, StrangeBee
