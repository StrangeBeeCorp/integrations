# TheHive Flow Workflows

Ready-to-use workflows for TheHive Flow. Import the file into your instance, then set up the secrets and global variables it refers to.

## Summary

- **Total Workflows:** 6
- **Generic Workflows:** 1
- **Vendor-Specific Workflows:** 5

## Generic Workflows

### Command line analysis

Automatically analyzes command-line activity in TheHive alerts to extract indicators of compromise (IOCs), including IP addresses, URLs, domains and file hashes. It decodes Base64-encoded PowerShell commands and adds extracted indicators as observables for further investigation.

- **Steps:** 15
- **Flow integrations used:** thehive
- **To set up after import:** 1 secret(s), 1 global variable(s)
- **Timeout:** 10m0s
- **Links:** [Workflow page](https://strangebee.com/workflow/command-line-analysis/) | [Code on GitHub](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/generic/thehive/workflows/command-line-analysis.yml) | [Raw file](https://raw.githubusercontent.com/StrangeBeeCorp/integrations/refs/heads/main/integrations/generic/thehive/workflows/command-line-analysis.yml)

## Vendor-Specific Workflows

### CIRCL Vulnerability-Lookup

#### CVE monitoring with CIRCL

Automatically retrieves vulnerability information from the CIRCL CVE database for specified vendors and products. It creates detailed TheHive alerts containing affected software versions, technical descriptions, vulnerability details, references and recommended remediation actions.

- **Steps:** 8
- **Flow integrations used:** thehive
- **To set up after import:** 1 secret(s), 1 global variable(s)
- **Timeout:** 10m0s
- **Links:** [Workflow page](https://strangebee.com/workflow/cve-monitoring-with-circl/) | [Code on GitHub](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/CIRCLVulnerabilityLookup/thehive/workflows/cve-monitoring-with-circl.yml) | [Raw file](https://raw.githubusercontent.com/StrangeBeeCorp/integrations/refs/heads/main/integrations/vendors/CIRCLVulnerabilityLookup/thehive/workflows/cve-monitoring-with-circl.yml)

### EmlParser

#### Suspicious email campaign detection

Automatically processes suspicious email alerts, extracts key email details and identifies related incidents. It groups matching alerts into existing cases or creates new ones in TheHive, helping security teams track and investigate potential email campaigns.

- **Steps:** 19
- **Flow integrations used:** thehive
- **To set up after import:** 1 secret(s), 1 global variable(s)
- **Links:** [Workflow page](https://strangebee.com/workflow/suspicious-email-campaign-detection/) | [Code on GitHub](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/EmlParser/thehive/workflows/suspicious-email-campaign-detection.yml) | [Raw file](https://raw.githubusercontent.com/StrangeBeeCorp/integrations/refs/heads/main/integrations/vendors/EmlParser/thehive/workflows/suspicious-email-campaign-detection.yml)

### Jira Cloud

#### TheHive to Jira ITSM sync

Automatically creates Jira issues from new TheHive alerts and synchronizes comments between both platforms. It prevents duplicate updates, keeps incident discussions aligned and closes Jira issues when the corresponding alerts are resolved.

- **Steps:** 15
- **Flow integrations used:** jira, thehive
- **To set up after import:** 2 secret(s), 2 global variable(s)
- **Timeout:** 24h0m0s
- **Links:** [Workflow page](https://strangebee.com/workflow/thehive-to-jira-itsm-sync/) | [Code on GitHub](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/JIRA/thehive/workflows/thehive-to-jira-itsm-sync.yml) | [Raw file](https://raw.githubusercontent.com/StrangeBeeCorp/integrations/refs/heads/main/integrations/vendors/JIRA/thehive/workflows/thehive-to-jira-itsm-sync.yml)

### Recorded Future

#### Alert triage with Recorded Future

Automatically processes Elasticsearch security alerts in TheHive and enriches IP addresses and file hashes with threat intelligence from Recorded Future. It identifies high-risk indicators, escalates critical alerts into cases and documents malicious findings to streamline incident investigation.

- **Steps:** 14
- **Flow integrations used:** recorded_future, thehive
- **To set up after import:** 2 secret(s), 1 global variable(s)
- **Timeout:** 10m0s
- **Links:** [Workflow page](https://strangebee.com/workflow/alert-triage-with-recorded-future/) | [Code on GitHub](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/RecordedFuture/thehive/workflows/alert-triage-with-recorded-future.yml) | [Raw file](https://raw.githubusercontent.com/StrangeBeeCorp/integrations/refs/heads/main/integrations/vendors/RecordedFuture/thehive/workflows/alert-triage-with-recorded-future.yml)

### Slack

#### Slack Alert Manager workflow

TheHive Flow's Slack Alert Manager workflow automates alert monitoring and response tracking through Slack. It processes reactions, comments and thread replies to update alert statuses, ensuring timely follow-ups and efficient incident management.

- **Steps:** 19
- **Flow integrations used:** slack, thehive
- **To set up after import:** 3 secret(s), 1 global variable(s)
- **Timeout:** 1h0m0s
- **Links:** [Workflow page](https://strangebee.com/workflow/slack-alert-manager-workflow/) | [Code on GitHub](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/Slack/thehive/workflows/slack-alert-manager-workflow.yml) | [Raw file](https://raw.githubusercontent.com/StrangeBeeCorp/integrations/refs/heads/main/integrations/vendors/Slack/thehive/workflows/slack-alert-manager-workflow.yml)

*This documentation is auto-generated. Do not edit manually.*
