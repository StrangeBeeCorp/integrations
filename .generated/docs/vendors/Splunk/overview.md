## Analyzers (11)

### [Splunk_Search_URL_URI_Path v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_url_uri_path.json)
Execute a savedsearch on a Splunk instance with an URL or a URI path as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `url`, `uri_path`

### [Splunk_Search_User v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_user.json)
Execute a savedsearch on a Splunk instance with a user ID as argument

- **Author:** LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `other`

### [Splunk_Search_Mail_Subject v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_mail_subject.json)
Execute a savedsearch on a Splunk instance with a mail subject as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `mail_subject`, `mail-subject`

### [Splunk_Search_Registry v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_registry.json)
Execute a savedsearch on a Splunk instance with a registry data as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `registry`

### [Splunk_Search_Mail_Email v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_mail_email.json)
Execute a savedsearch on a Splunk instance with a mail/email as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `mail`, `email`

### [Splunk_Search_User_Agent v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_user_agent.json)
Execute a savedsearch on a Splunk instance with a user agent as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `user-agent`

### [Splunk_Search_IP v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_ip.json)
Execute a savedsearch on a Splunk instance with an IP as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `ip`

### [Splunk_Search_Hash v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_hash.json)
Execute a savedsearch on a Splunk instance with a hash as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `hash`

### [Splunk_Search_Domain_FQDN v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_domain_fqdn.json)
Execute a savedsearch on a Splunk instance with a domain or a FQDN as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `domain`, `fqdn`

### [Splunk_Search_File_Filename v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_file_filename.json)
Execute a savedsearch on a Splunk instance with a file/filename as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `file`, `filename`

### [Splunk_Search_Other v3.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Splunk/Splunk_Search_other.json)
Execute a savedsearch on a Splunk instance with an unidentified data as argument

- **Author:** Unit777, LetMeR00t
- **License:** AGPL-V3
- **Data Types:** `other`

---

## Functions (1)

### createAlertFromSplunk `v1.0.0`
This function creates a TheHive Alert based on an input coming from Splunk, and matches the Splunk fields to TheHive fields. In Splunk, you'll need to configure the webhook URL to point to the TheHive function URL

- **Source:** [View code](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Splunk/thehive/functions/function_API_createAlertFromSplunk.js)

---

## External Integrations (2)

External integrations that connect Splunk with TheHive:

### TheHive/Cortex Technical Add-on
Bidirectional integration add-on that pulls case and alert events from TheHive, retrieves Cortex job information, and enables creating alerts/cases and executing functions in TheHive directly from Splunk searches and dashboards

- **Type:** technical-addon
- **Documentation:** [https://splunkbase.splunk.com/app/5329](https://splunkbase.splunk.com/app/5329)

---

### TheHive SOAR Connector
Official Splunk SOAR connector with 16 actions for case management, task operations, observable handling, and TTP tracking to automate incident response workflows between Splunk and TheHive

- **Type:** soar-connector
- **Documentation:** [https://splunkbase.splunk.com/app/5939](https://splunkbase.splunk.com/app/5939)
