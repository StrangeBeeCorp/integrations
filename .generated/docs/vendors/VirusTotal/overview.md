## Analyzers (4)

### Enrich observables with intelligence

#### [VirusTotal GetReport v3.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/VirusTotal)
Get the latest VirusTotal report for a file, hash, domain or an IP address.

- **Author:** CERT-BDF, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`, `hash`, `domain`, `fqdn`, `ip`, `url`

#### [VirusTotal DownloadSample v3.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/VirusTotal)
Use VirusTotal to download the original file for an hash.

- **Author:** LDO-CERT
- **License:** AGPL-V3
- **Data Types:** `hash`

#### [VirusTotal Scan v3.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/VirusTotal)
Use VirusTotal to scan a file or URL.

- **Author:** CERT-BDF, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `file`, `url`

#### [VirusTotal Rescan v3.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/VirusTotal)
Use VirusTotal to run new analysis on hash.

- **Author:** CERT-LDO
- **License:** AGPL-V3
- **Data Types:** `hash`

---

## TheHive Flow node (1)

### Orchestrate this vendor from TheHive Flow workflows

Get VirusTotal reputation reports and submit files and URLs for scanning.

**Example use cases:**

- Check the reputation of a hash, URL, domain or IP found in an alert
- Submit an unknown attachment for scanning and wait for the analysis result
- Auto-tag observables as malicious above a detection threshold

TheHive Flow is TheHive's native automation and orchestration engine, available exclusively with the TheHive ONE plan.
