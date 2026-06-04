## Analyzers (2)

### Enrich observables with intelligence

#### [ZscalerZIA URLLookup v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Zscaler)
Query Zscaler Internet Access for URL categorization and security classification. Supports OneAPI OAuth2 and legacy authentication.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`, `url`, `ip`

#### [Zscaler v1.3](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Zscaler)
Check Zscaler category for a domain, fqdn, IP address or FQDN. This analyzer requires a paid subscription to Zscaler ZIA

- **Author:** Simon Lavigne, Mikael Keri
- **License:** AGPL-V3
- **Data Types:** `ip`, `domain`, `url`, `fqdn`

---

## Responders (12)

### Trigger automated responses

#### [ZscalerZIA AddToURLCategoryWildcard v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Add a domain and all its subdomains to a custom ZIA URL category

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA RemoveFromATPDenylist v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Remove domains, FQDNs and URLs from the ZIA ATP Denylist (Policy > Security > Advanced Threat Protection > Blocked Malicious URLs)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA AddToATPDenylist v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Block domains, FQDNs and URLs in the ZIA ATP Denylist (Policy > Security > Advanced Threat Protection > Blocked Malicious URLs)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA AddToURLCategory v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Add observables (domain, fqdn, url, ip, cidr) to a custom ZIA URL category

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA RemoveFromURLCategory v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Remove observables (domain, fqdn, url, ip, cidr) from a custom ZIA URL category

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA AddToCloudFirewallRule v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Add an IP address or CIDR to the destination address list of a ZIA Cloud Firewall rule - network-layer block, all ports/protocols (Policy > Cloud Firewall)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA AddToATPSecurityExceptions v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Add domains, FQDNs and URLs to ZIA Security Exceptions - bypasses ATP content scanning (Policy > Security > Advanced Threat Protection > Security Exceptions)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA AddToATPDenylistWildcard v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Block a domain and all its subdomains in the ZIA ATP Denylist (Policy > Security > Advanced Threat Protection > Blocked Malicious URLs)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA RemoveFromATPSecurityExceptions v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Remove domains, FQDNs and URLs from ZIA Security Exceptions (Policy > Security > Advanced Threat Protection > Security Exceptions)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA RemoveFromURLCategoryWildcard v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Remove a domain and all its subdomains from a custom ZIA URL category

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA RemoveFromCloudFirewallRule v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Remove an IP address or CIDR from the destination address list of a ZIA Cloud Firewall rule - network-layer block, all ports/protocols (Policy > Cloud Firewall)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [ZscalerZIA RemoveFromATPDenylistWildcard v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Zscaler)
Remove a domain and all its subdomains from the ZIA ATP Denylist (Policy > Security > Advanced Threat Protection > Blocked Malicious URLs)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
