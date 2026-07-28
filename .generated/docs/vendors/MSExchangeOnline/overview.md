## Analyzers (1)

### Enrich observables with intelligence

#### [MSExchangeOnline GetInboxRules v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSExchangeOnline)
List a mailbox's inbox rules via Microsoft Graph and flag rules commonly abused after a mailbox compromise/BEC: external auto-forwarding, silent delete/move rules, keyword filters on security or financial terms, hiding folders (RSS Feeds...), obfuscated rule names.

- **Author:** Fabien Bloume ,StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`

---

## Responders (1)

### Trigger automated responses

#### [MSExchangeOnline RemoveInboxRule v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSExchangeOnline)
Removes a malicious Exchange Online inbox rule via Microsoft Graph. Reads the target mailbox UPN and Graph rule ID from a case custom field (name configurable, defaults to "inbox-rule-input"), formatted as "<mailboxUPN>|<ruleId>".

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`
