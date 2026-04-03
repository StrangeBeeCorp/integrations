## Analyzers (1)

### Enrich observables with intelligence

#### [AbuseIPDB v2.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/AbuseIPDB)
Check IP addresses or CIDR blocks against AbuseIPDB. Returns abuse confidence score, report categories, reporter countries, and detailed report history.

- **Author:** Matteo Lodi; Fabien Bloume, StrangeBee
- **License:** AGPL-v3
- **Data Types:** `ip`

---

## Responders (1)

### Trigger automated responses

#### [AbuseIPDB Report v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/AbuseIPDB)
Report an IP address to AbuseIPDB for abuse tracking and community sharing. Please, make sure to use the correct category in your Cortex responder configuration.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
