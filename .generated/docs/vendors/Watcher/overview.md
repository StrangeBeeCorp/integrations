## Analyzers (1)

### Enrich observables with intelligence

#### [Watcher Check v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Watcher)
Check if a domain is monitored in Watcher (Legitimate Domain and/or Website Monitoring modules) and retrieve all details.

- **Author:** THA-CERT // YNE
- **License:** AGPL-V3
- **Data Types:** `domain`

---

## Responders (4)

### Trigger automated responses

#### [Watcher Add v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Watcher)
Add domain to Watcher. Required tags: watcher:module=LegitDomain|WebsiteMonitoring. For LegitDomain: watcher:repurchased=Yes/No (required), watcher:contact=email (optional). For WebsiteMonitoring: watcher:legitimacy=2-6 (required), watcher:takedown_request=Yes/No, watcher:legal_team=Yes/No, watcher:blocking_request=Yes/No

- **Author:** THA-CERT // YNE
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [Watcher Transfer v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Watcher)
Transfer domain between Watcher modules. Required tag: watcher:module=LegitDomain|WebsiteMonitoring (DESTINATION module). Transfer TO LegitDomain: watcher:repurchased=Yes/No (required), watcher:contact=email (optional). Transfer TO WebsiteMonitoring: watcher:legitimacy=2-6 (required), watcher:takedown_request=Yes/No, watcher:legal_team=Yes/No, watcher:blocking_request=Yes/No

- **Author:** THA-CERT // YNE
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [Watcher Update v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Watcher)
Update domain in Watcher. Required tags: watcher:module=LegitDomain|WebsiteMonitoring. For LegitDomain: watcher:repurchased=Yes/No, watcher:contact=email (optional). For WebsiteMonitoring: watcher:legitimacy=2-6, watcher:takedown_request=Yes/No, watcher:legal_team=Yes/No, watcher:blocking_request=Yes/No

- **Author:** THA-CERT // YNE
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [Watcher Remove v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Watcher)
Remove domain from Watcher. Required tag: watcher:module=LegitDomain|WebsiteMonitoring

- **Author:** THA-CERT // YNE
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
