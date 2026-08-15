## Analyzers (2)

### Enrich observables with intelligence

#### [MSDefenderForEndpoint HashReputation v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSDefenderForEndpoint)
Check a file hash (SHA1 or SHA256) against Microsoft Defender for Endpoint: organization prevalence and related alerts.

- **Author:** Elina Galvao, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `hash`

#### [MSDefenderForEndpoint DeviceLookup v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSDefenderForEndpoint)
Look up a device (by IP or hostname/FQDN) in Microsoft Defender for Endpoint: risk score, exposure level, health status and related alerts.

- **Author:** Elina Galvao, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `ip`, `fqdn`

---

## Responders (12)

### Trigger automated responses

#### [MSDefenderForEndpoint-PushIOC-Warn v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Push IOC to Defender client. Warn mode (Microsoft Defender for Cloud only)

- **Author:** Vito Piserchia
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-PushIOC-Block v2.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Push IOC to Defender client. Block mode

- **Author:** Keijo Korte, Louis-Maximilien Dupouy, Vito Piserchia
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-RestrictAppExecution v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Restrict execution of all applications on the device except a predefined set

- **Author:** Keijo Korte, Louis-Maximilien Dupouy
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-PushIOC-Allowed v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Push IOC to Defender client. Allowed mode

- **Author:** Vito Piserchia
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-PushIOC-BlockAndRemediate v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Push IOC to Defender client. Block and Remediate mode

- **Author:** Vito Piserchia
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-AutoInvestigation v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Start an automated investigation on a device

- **Author:** Keijo Korte, Louis-Maximilien Dupouy
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-UnisolateMachine v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Unisolate machine with Microsoft Defender for Endpoints

- **Author:** Keijo Korte
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-IsolateMachine v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Isolate machine with Microsoft Defender for Endpoints

- **Author:** Keijo Korte
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-UnRestrictAppExecution v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Enable execution of any application on the device

- **Author:** Keijo Korte, Louis-Maximilien Dupouy
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-FullVirusScan v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Run full virus scan to machine with Microsoft Defender for Endpoints

- **Author:** Keijo Korte
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-PushIOC-Audit v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Push IOC to Defender client. Audit mode

- **Author:** Vito Piserchia
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSDefenderForEndpoint-StopAndQuarantineFile v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSDefenderForEndpoint)
Stop execution of a file and delete it on every machine where it was seen (SHA1 hashes only)

- **Author:** Elina Galvao, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
