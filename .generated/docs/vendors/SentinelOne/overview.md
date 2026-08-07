## Analyzers (3)

### Enrich observables with intelligence

#### [SentinelOne DNSQuery v2.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/SentinelOne)
Query SentinelOne for hosts that have requested DNS lookups for a domain/URL/FQDN. Supports both new SDL (Security Data Lake) API and legacy Deep Visibility API v2.1.

- **Author:** Joe Vasquez; Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `url`, `domain`, `fqdn`

#### [SentinelOne DeepVisibility DNSQuery v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/SentinelOne)
Query Sentinel One Deep Visibility API v2.1 for hosts that have requested DNS lookups for a domain/URL/FQDN.

- **Author:** Joe Vasquez
- **License:** AGPL-V3
- **Data Types:** `url`, `domain`, `fqdn`

#### [SentinelOne DNSReverseLookup v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/SentinelOne)
Query SentinelOne for DNS names that resolved to a given IP address. Returns the domains and the hosts that made the DNS queries. Supports both SDL (Security Data Lake) API and legacy Deep Visibility API.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `ip`

---

## Responders (1)

### Trigger automated responses

#### [SentinelOne Hash Blacklister v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/SentinelOne)
Add SHA1 hash to SentinelOne Blacklist via API v2.1.

- **Author:** Joe Vasquez
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
