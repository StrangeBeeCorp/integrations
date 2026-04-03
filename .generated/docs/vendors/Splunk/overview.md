## Analyzers (11)

### Enrich observables with intelligence

#### [Splunk Search File Filename v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a file/filename as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `file`, `filename`

#### [Splunk Search URL URI Path v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with an URL or a URI path as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `url`, `uri_path`

#### [Splunk Search Hash v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a hash as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `hash`

#### [Splunk Search Mail Email v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a mail/email as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `mail`, `email`

#### [Splunk Search Mail Subject v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a mail subject as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `mail_subject`, `mail-subject`

#### [Splunk Search Domain FQDN v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a domain or a FQDN as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`

#### [Splunk Search User Agent v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a user agent as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `user-agent`

#### [Splunk Search IP v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with an IP as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `ip`

#### [Splunk Search Registry v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a registry data as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `registry`

#### [Splunk Search User v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with a user ID as argument

- **Author:** LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `other`

#### [Splunk Search Other v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk)
Execute a savedsearch on a Splunk instance with an unidentified data as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `other`

---

## Functions (1)

### Automate TheHive actions or ingest alerts

#### [createAlertFromSplunk](https://github.com/StrangeBeeCorp/integrations/blob/develop/integrations/vendors/Splunk/thehive/functions/function_API_createAlertFromSplunk.js) `v1.0.0`
This function creates a TheHive Alert based on an input coming from Splunk, and matches the Splunk fields to TheHive fields. In Splunk, you'll need to configure the webhook URL to point to the TheHive function URL


---

## External Integrations (2)

### External integrations that connect Splunk with TheHive

#### [TheHive/Cortex Technical Add-on](https://splunkbase.splunk.com/app/5329)
Bidirectional integration add-on that pulls case and alert events from TheHive, retrieves Cortex job information, and enables creating alerts/cases and executing functions in TheHive directly from Splunk searches and dashboards

- **Type:** technical-addon

---

#### [TheHive SOAR Connector](https://splunkbase.splunk.com/app/5939)
Official Splunk SOAR connector with 16 actions for case management, task operations, observable handling, and TTP tracking to automate incident response workflows between Splunk and TheHive

- **Type:** soar-connector
