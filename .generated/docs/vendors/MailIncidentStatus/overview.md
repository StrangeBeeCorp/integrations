## Responders (1)

### Trigger automated responses

#### [MailIncidentStatus v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MailIncidentStatus)
Mail a detailed status information of an incident case. The mail is sent to recipients specified by tags prefixed with 'mail='. The responder respects tlp definitions. For tlp:amber mail addresse and for tlp:green mail domains must be pre-defined in the configuration. For tlp:red sending mails is denied. The responser also uses thehive4py to collect information about the status of the tasks of the incidents.

- **Author:** Manuel Krucker
- **License:** AGPL-V3
- **Data Types:** `thehive:case`
