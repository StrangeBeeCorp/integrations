## Use Cases (2)

### Ingest Proofpoint MessagesDelivered Events into TheHive Using an Alert Feeder
Ingest Proofpoint TAP messagesDelivered events as TheHive alerts to track and respond to threats that have reached user mailboxes and may require investigation.

- **License required:** Platinum
- **TheHive version required:** 5.5+
- **Documentation:** [View tutorial](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/use-cases/alert-ingestion-messageDelivered.md)
- **Related function:** [alertFeeder_ProofPoint_messageDelivered](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_messageDelivered.js)

---

### Ingest Proofpoint ClicksPermitted Events into TheHive Using an Alert Feeder
Ingest Proofpoint TAP clicksPermitted events as TheHive alerts to track and respond to users who clicked on malicious links that were not blocked by Proofpoint and may require investigation.

- **License required:** Platinum
- **TheHive version required:** 5.5+
- **Documentation:** [View tutorial](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/use-cases/alert-ingestion-clicksPermitted.md)
- **Related function:** [alertFeeder_ProofPoint_clicksPermitted](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_clicksPermitted.js)

---

## Analyzers (1)

### [Proofpoint Lookup v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Proofpoint/ProofPoint_Lookup.json)
Check URL, file, SHA256 against Proofpoint forensics

- **Author:** Emmanuel Torquato
- **License:** AGPL-V3
- **Data Types:** `url`, `file`, `hash`

---

## Functions (2)

### alertFeeder_ProofPoint_messageDelivered `v1.0.0`
Ingests ProofPoint messageDelivered alerts in TheHive

- **Source:** [View code](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_messageDelivered.js)

### alertFeeder_ProofPoint_clicksPermitted `v1.0.0`
Ingests ProofPoint clicksPermitted alerts in TheHive

- **Source:** [View code](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_clicksPermitted.js)
