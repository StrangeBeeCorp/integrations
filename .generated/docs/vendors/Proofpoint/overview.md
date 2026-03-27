## Use Cases (2)

*Real-world integrations with TheHive*

### [Ingest Proofpoint MessagesDelivered Events into TheHive Using an Alert Feeder](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/use-cases/alert-ingestion-messageDelivered.md)
Ingest Proofpoint TAP messagesDelivered events as TheHive alerts to track and respond to threats that have reached user mailboxes and may require investigation.

- **License required:** Platinum
- **TheHive version required:** 5.5+
- **Related function:** [alertFeeder_ProofPoint_messageDelivered](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_messageDelivered.js)

### [Ingest Proofpoint ClicksPermitted Events into TheHive Using an Alert Feeder](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/use-cases/alert-ingestion-clicksPermitted.md)
Ingest Proofpoint TAP clicksPermitted events as TheHive alerts to track and respond to users who clicked on malicious links that were not blocked by Proofpoint and may require investigation.

- **License required:** Platinum
- **TheHive version required:** 5.5+
- **Related function:** [alertFeeder_ProofPoint_clicksPermitted](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_clicksPermitted.js)

---

## Analyzers (1)

*Enrich observables with intelligence*

### [Proofpoint Lookup v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Proofpoint)
Check URL, file, SHA256 against Proofpoint forensics

- **Author:** Emmanuel Torquato
- **License:** AGPL-V3
- **Data Types:** `url`, `file`, `hash`

---

## Functions (2)

*Automate TheHive actions or ingest alerts*

### [alertFeeder_ProofPoint_clicksPermitted](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_clicksPermitted.js) `v1.0.0`
Ingests ProofPoint clicksPermitted alerts in TheHive

- **Author:** Fabien Bloume, StrangeBee

### [alertFeeder_ProofPoint_messageDelivered](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Proofpoint/thehive/functions/function_Feeder_alertFromProofpoint_messageDelivered.js) `v1.0.0`
Ingests ProofPoint messageDelivered alerts in TheHive

- **Author:** Fabien Bloume, StrangeBee
