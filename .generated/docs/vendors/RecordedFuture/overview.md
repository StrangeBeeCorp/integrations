## Analyzer (1)

### Enrich observables with intelligence

#### [RecordedFuture v2.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/RecordedFuture)
Enrich IP, Domain, FQDN, URL, or Hash with Recorded Future context:  Risk Score, Risk Details, AI Insights, Links, Threat Actor, Attack Vector, Malware Category / Family, and Related Entities (IPs, Domains, and Hashes)

- **Author:** Recorded Future
- **License:** AGPL-V3
- **Data Types:** `ip`, `domain`, `fqdn`, `hash`, `url`

---

## TheHive Flow node (1)

### Orchestrate this vendor from TheHive Flow workflows

Enrich observables with Recorded Future risk scores, context and threat actor intelligence.

**Example use cases:**

- Enrich every new observable with a risk score and tag it in TheHive
- Bulk-triage all observables of an alert to decide whether to escalate
- Attach threat actor context to a case when an IOC matches a known campaign

TheHive Flow is a first-party module that requires a TheHive ONE license.
