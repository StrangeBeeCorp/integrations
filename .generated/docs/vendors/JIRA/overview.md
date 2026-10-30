## TheHive Flow node (1)

### Orchestrate this vendor from TheHive Flow workflows

Create and follow Jira issues from SOC workflows, with full Jira Cloud REST v3 coverage.

**Example use cases:**

- Open a Jira ticket for the owning team when a case needs a fix such as a patch or config change
- Link the Jira issue back to the TheHive case and comment progress
- Close the case automatically when the Jira issue is resolved

TheHive Flow is a first-party module that requires a TheHive ONE license.

---

## Function (1)

### Automate TheHive actions or ingest alerts

#### [alertFromJIRA](https://github.com/StrangeBeeCorp/integrations/blob/main/integrations/vendors/JIRA/thehive/functions/function_Feeder_alertFromJIRA.js) `v1.0.0`
This function creates alerts from JIRA issues. It checks if the alert already exists, then creates it with type, source, source-ref, title, and description

