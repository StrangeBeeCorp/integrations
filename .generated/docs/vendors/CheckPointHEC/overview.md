## Analyzers (5)

### Enrich observables with intelligence

#### [CheckPointHEC SearchEmail v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CheckPointHEC)
Search for an email in Check Point Harmony Email & Collaboration and retrieve its security verdict, phishing confidence, classification and scan results. Accepts an .eml file or a Message-ID as an 'other' observable.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`, `other`

#### [CheckPointHEC SearchByDomain v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CheckPointHEC)
Search for all emails from a sender domain in Check Point Harmony Email & Collaboration. Accepts a domain observable or an .eml file (sender domain is extracted automatically, with forwarded email support).

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `domain`, `file`

#### [CheckPointHEC SearchByURL v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CheckPointHEC)
Search for all emails containing a specific URL in Check Point Harmony Email & Collaboration and retrieve their security verdicts.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `url`

#### [CheckPointHEC SearchBySenderIP v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CheckPointHEC)
Search for all emails from a sender IP in Check Point Harmony Email & Collaboration. Accepts an IP observable or an .eml file (sender IP is extracted from Received headers, with forwarded email support).

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `ip`, `file`

#### [CheckPointHEC SearchBySender v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/CheckPointHEC)
Search for all emails from a sender address in Check Point Harmony Email & Collaboration. Accepts a mail observable or an .eml file (sender is extracted automatically, with forwarded email support).

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`, `file`
