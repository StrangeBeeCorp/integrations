## Analyzers (2)

### [DomainToolsIris_Pivot v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/DomainToolsIris/DomainToolsIris_Pivot.json)
Use DomainTools Iris API to pivot on ssl_hash, ip, or email.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `hash`, `ip`, `mail`

### [DomainToolsIris_Investigate v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/DomainToolsIris/DomainToolsIris_Investigate.json)
Use DomainTools Iris API to investigate a domain.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `domain`

---

## Responders (2)

### [DomainToolsIris_CheckMaliciousTags v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/DomainToolsIris/DomainToolsIris_CheckMaliciousTags.json)
Add Tag saying that the observable and case have a malicious tag in their Iris Tags.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [DomainToolsIris_AddRiskyDNSTag v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/DomainToolsIris/DomainToolsIris_AddRiskyDNSTag.json)
Add Tag saying that the case contains a risky DNS.

- **Author:** DomainTools
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
