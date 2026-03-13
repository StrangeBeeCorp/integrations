## Use Cases (2)

### [Ingest CrowdStrike Falcon Detections and Incidents into TheHive Using an External Script](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/CrowdstrikeFalcon/use-cases/ingest-crowdstrike-falcon-alerts-external-script.md)
Install and configure the falcon2thehive connector to automatically ingest CrowdStrike Falcon detections and incidents into TheHive as alerts in real time.


### [Synchronise status between TheHive alerts/cases and CrowdStrike detections/incidents](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/CrowdstrikeFalcon/use-cases/synchronize-status-thehive-crowdstrike-falcon.md)
Keep case/alert status in sync between TheHive and CrowdStrike Falcon using notifications and the CrowdStrikeFalcon_Sync responder.

- **License required:** Platinum
- **TheHive version required:** 5.0+

---

## Analyzers (11)

### [CrowdstrikeFalcon Sandbox Win7 64 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon GetDeviceVulnerabilities v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Get device vulnerabilities from hostname

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hostname`

### [CrowdstrikeFalcon Sandbox Android v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon Sandbox Linux v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon getDeviceDetails v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Get device information from Crowdstrike Falcon

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hostname`

### [CrowdstrikeFalcon ThreatIntel v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Query threat intelligence indicators from Crowdstrike Falcon Intelligence

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hash`, `domain`, `ip`, `url`

### [CrowdstrikeFalcon Sandbox Win11 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon Sandbox MacOS v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon Sandbox Win10 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

### [CrowdstrikeFalcon getDeviceAlerts v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Get Device alerts from Crowdstrike Falcon

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hostname`

### [CrowdstrikeFalcon Sandbox Win7 v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CrowdstrikeFalcon)
Send a file to CrowdstrikeFalcon Sandbox

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`

---

## Responders (9)

### [CrowdStrikeFalcon AddIOC v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
Add IOC to IoC Management on Crowdstrike - supports domain, url, IPs & different kind of hashes

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon unhideHost v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
This action will restore a host. Detection reporting will resume after the host is restored

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon RemoveIOC v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
remove IOC from IoC Management on Crowdstrike

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon unsuppressDetections v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
Allow detections for the host.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon HostContainment v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
This action contains the host, which stops any network communications to locations other than the CrowdStrike cloud and IPs specified in your containment policy

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon hideHost v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
This action will delete a host. After the host is deleted, no new detections for that host will be reported via UI or APIs

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon Sync v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
Sync TheHive status back to CS Alerts or Incidents

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`, `thehive:alert`

### [CrowdStrikeFalcon suppressDetections v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
Supress detections for the host.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [CrowdStrikeFalcon LiftContainmentHost v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/CrowdstrikeFalcon)
This action lifts containment on the host, which returns its network communications to normal

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

---

## External Integrations (1)

External integrations that connect CrowdStrike Falcon with TheHive:

### [falcon2thehive](https://github.com/StrangeBeeCorp/falcon2thehive)
Real-time connector that streams CrowdStrike Falcon detection events into TheHive, turning Falcon alerts into actionable TheHive Alerts. Supports DetectionSummaryEvent, IdentityProtectionEvent, and MobileDetectionSummaryEvent with automatic observable extraction and TTP mapping.

- **Type:** connector
