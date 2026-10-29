## Analyzers (2)

### Enrich observables with intelligence

#### [DomainToolsIris Investigate v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/DomainToolsIris)
Use DomainTools Iris API to investigate a domain.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `domain`

#### [DomainToolsIris Pivot v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/DomainToolsIris)
Use DomainTools Iris API to pivot on ssl_hash, ip, or email.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `hash`, `ip`, `mail`

---

## Responders (2)

### Trigger automated responses

#### [DomainToolsIris AddRiskyDNSTag v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/DomainToolsIris)
Add Tag saying that the case contains a risky DNS.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [DomainToolsIris CheckMaliciousTags v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/DomainToolsIris)
Add Tag saying that the observable and case have a malicious tag in their Iris Tags.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
