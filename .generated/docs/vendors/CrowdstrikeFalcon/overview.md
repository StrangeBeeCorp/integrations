## Use Cases (2)

### Ingest CrowdStrike Falcon Detections and Incidents into TheHive Using an External Script
Install and configure the falcon2thehive connector to automatically ingest CrowdStrike Falcon detections and incidents into TheHive as alerts in real time.

- **Documentation:** [View tutorial](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/CrowdstrikeFalcon/use-cases/ingest-crowdstrike-falcon-alerts-external-script.md)

---

### Synchronise status between TheHive alerts/cases and CrowdStrike detections/incidents
Keep case/alert status in sync between TheHive and CrowdStrike Falcon using notifications and the CrowdStrikeFalcon_Sync responder.

- **Documentation:** [View tutorial](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/CrowdstrikeFalcon/use-cases/synchronize-status-thehive-crowdstrike-falcon.md)

---

## Analyzers (11)

### [CrowdstrikeFalcon_Sandbox_Win7_64 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_Win7_64.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon_GetDeviceVulnerabilities v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_GetDeviceVulnerabilities.json)
Get device vulnerabilities from hostname

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hostname`

### [CrowdstrikeFalcon_Sandbox_Android v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_Android.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon_Sandbox_Linux v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_Linux.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon_getDeviceDetails v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_getDeviceDetails.json)
Get device information from Crowdstrike Falcon

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hostname`

### [CrowdstrikeFalcon_ThreatIntel v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_ThreatIntel.json)
Query threat intelligence indicators from Crowdstrike Falcon Intelligence

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hash`, `domain`, `ip`, `url`

### [CrowdstrikeFalcon_Sandbox_Win11 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_Win11.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon_Sandbox_MacOS v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_MacOS.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon_Sandbox_Win10 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_Win10.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon_getDeviceAlerts v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_getDeviceAlerts.json)
Get Device alerts from Crowdstrike Falcon

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hostname`

### [CrowdstrikeFalcon_Sandbox_Win7 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon/CrowdstrikeFalcon_Sandbox_Win7.json)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

---

## Responders (9)

### [CrowdStrikeFalcon_AddIOC v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdStrikeFalcon_AddIOC.json)
Add IOC to IoC Management on Crowdstrike - supports domain, url, IPs & different kind of hashes

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_unhideHost v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdstrikeFalcon_unhideHost.json)
This action will restore a host. Detection reporting will resume after the host is restored

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_RemoveIOC v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdStrikeFalcon_removeIOC.json)
remove IOC from IoC Management on Crowdstrike

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_unsuppressDetections v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdstrikeFalcon_unsuppressDetection.json)
Allow detections for the host.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_HostContainment v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdstrikeFalcon_containHost.json)
This action contains the host, which stops any network communications to locations other than the CrowdStrike cloud and IPs specified in your containment policy

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_hideHost v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdstrikeFalcon_hideHost.json)
This action will delete a host. After the host is deleted, no new detections for that host will be reported via UI or APIs

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_Sync v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdStrikeFalcon_Sync.json)
Sync TheHive status back to CS Alerts or Incidents

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`, `thehive:alert`

### [CrowdStrikeFalcon_suppressDetections v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdstrikeFalcon_suppressDetections.json)
Supress detections for the host.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon_LiftContainmentHost v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon/CrowdstrikeFalcon_liftContainmentHost.json)
This action lifts containment on the host, which returns its network communications to normal

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

---

## Functions (1)

### CRWDAlertIngestion `v1.0.0`
Ingests CrowdstrikeFalcon Alerts, also processes observables & TTPs.

- **Source:** [View code](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/CrowdstrikeFalcon/thehive/functions/crwd-alert-ingestion.js)

---

## External Integrations (1)

External integrations that connect CrowdStrike Falcon with TheHive:

### falcon2thehive
Real-time connector that streams CrowdStrike Falcon detection events into TheHive, turning Falcon alerts into actionable TheHive Alerts. Supports DetectionSummaryEvent, IdentityProtectionEvent, and MobileDetectionSummaryEvent with automatic observable extraction and TTP mapping.

- **Type:** connector
- **Documentation:** [https://github.com/StrangeBeeCorp/falcon2thehive](https://github.com/StrangeBeeCorp/falcon2thehive)
