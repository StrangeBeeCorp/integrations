## Analyzer (1)

### Enrich observables with intelligence

#### [Elasticsearch Analysis v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/Elasticsearch)
Search for IoCs in Elasticsearch

- **Author:** Nick Prokop
- **License:** MIT
- **Data Types:** `url`, `domain`, `ip`, `hash`, `filename`, `fqdn`, `mail`, `mail-subject`, `user-agent`, `hostname`, `username`

---

## Responder (1)

### Trigger automated responses

#### [ElasticSecurity AlertStatusSync v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/Elasticsearch)
Sync TheHive case/alert status back to the corresponding Elastic Security detection alert(s), including a closing reason

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case`, `thehive:alert`

---

## TheHive Flow node (1)

### Orchestrate this vendor from TheHive Flow workflows

Query Elasticsearch data and read Elastic Security detection alerts.

**Example use cases:**

- Pull Elastic detection alerts and create TheHive alerts
- Run an ES|QL query to scope an incident across users, hosts and time range
- Write enrichment results or case summaries into a dedicated index

TheHive Flow is a first-party module that requires a TheHive ONE license.

---

## External Integration (1)

### External integrations that connect Elasticsearch with TheHive

#### [TheHive Connector for Kibana](https://www.elastic.co/docs/reference/kibana/connectors-kibana/thehive-action-type)
Native Kibana connector that allows Elasticsearch to create alerts and create cases in TheHive

- **Type:** connector
