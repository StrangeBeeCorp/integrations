## Responders (2)

### [JAMFProtect addHashtoPreventList v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/JAMFProtect/JAMFProtect_addHashtoPreventList.json)
Add IOC to JAMF Protect - creates a custom prevent list for a hash

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [JAMFProtect removeHashfromPreventList v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/JAMFProtect/JAMFProtect_removeHashfromPreventList.json)
Remove IOC on JAMF Protect - removes associated custom prevent list(s) containing the hash

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

---

## Functions (1)

### createAlertFromJAMFProtect `v1.0.0`
Ingests alerts from JAMF Protect. Extracts analytic details, host and user information, MITRE ATT&CK tags, and file/path data. The function constructs a TheHive alert, including a title, markdown-formatted description (with original alert JSON), relevant observables (IP, hostname, file, hash, URL, FQDN, URI path, user agent), MITRE ATT&CK enrichment, and a link to the JAMF alert. Handles default values and supports tagging and mapping of MITRE tactics for easier triage and investigation. For the setup in JAMF Protect, go to Configuration > Actions > *your action* > Add an HTTP data endpoint + your Authorization Header and Bearer as value

- **Source:** [View code](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/JAMFProtect/thehive/functions/function_API_createAlertFromJAMFProtect.js)
