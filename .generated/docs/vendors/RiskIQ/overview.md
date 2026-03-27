## Analyzers (16)

*Enrich observables with intelligence*

### [RiskIQ Components v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: web components observed during crawls on a hostname.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Reputation v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ Illuminate Reputation Score for an indicator.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Artifacts v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: Illuminate / PassiveTotal project artifacts that match an indicator.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Malware v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: malware hashes from various sources associated with an IOC.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Resolutions v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: PDNS resolutions for an IOC.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Trackers v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: trackers observed during a crawl on a host.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Certificates v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: SSL/TLS certificates associated with an indicator.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Whois v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ Whois lookup for an indicator.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Cookies v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: cookies observed during crawls on a hostname.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Subdomains v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: subdomains observed historically in pDNS records.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `fqdn`, `domain`

### [RiskIQ HostpairChildren v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: hosts with a child web component relationship to an IOC.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Summary v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ Illuminate and PassiveTotal datasets with records for an indicator.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Services v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: services observed on an IP address.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `ip`

### [RiskIQ Articles v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: OSINT articles that reference an indicator.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ HostpairParents v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: hosts with a parent web component relationship to an IOC.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

### [RiskIQ Projects v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RiskIQ)
RiskIQ: Illuminate / PassiveTotal projects that contain an artifact which matches an IOC.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `ip`

---

## Responders (1)

*Trigger automated responses*

### [RiskIQ PushArtifactToProject v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/RiskIQ)
Push a case to a RiskIQ Illuminate project.

- **Author:** RiskIQ
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
