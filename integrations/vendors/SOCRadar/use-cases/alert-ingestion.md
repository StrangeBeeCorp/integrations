---
title: Ingest SOCRadar Alarms into TheHive Using an Alert Feeder
description: Ingest SOCRadar XTI alarms from the Incident API v4 as TheHive alerts with full paging, a moving start date, and an hourly lookback that catches alarms approved late.
tags: [socradar, xti, incidents, alarms, alert-ingestion]
thehive_version_required: "5.5"
license_required: "platinum"
linked_to: ["integrations/vendors/SOCRadar/thehive/functions/function_Feeder_alertFromSOCRadar.js"]
---
# Tutorial: Ingest SOCRadar Alarms into TheHive Using an Alert Feeder

> **Note:** This integration was tested on TheHive 5.8.0 with the production SOCRadar Incident API v4, and with a mock of the API for edge cases. Verify it with your SOCRadar tenant in a test organization before using it in production.

In this tutorial, we're going to configure an alert feeder that polls the SOCRadar Incident API v4 and creates one TheHive alert per SOCRadar alarm. The feeder:

* Pages through every new alarm since the last one it saw, so a burst of hundreds of alarms is ingested in one go.
* Rescans the last 5 days every hour, to catch alarms that became visible in SOCRadar after a delay, for example after analyst approval.
* Never creates the same alarm twice.

## Requirements

* TheHive 5.5 or later with a **Platinum** license. Alert feeders, functions and the *HttpRequest* notifier aren't available on other licenses.
* A TheHive user with the `manageConfig` and `manageFunction/create` permissions in the target organization.
* A TheHive service account in the same organization with the `manageConfig` permission, and its API key. The paging notification uses it to update the feeder.
* A SOCRadar XTI subscription with API access, and the **company ID** of the monitored company.

## How it works

An alert feeder sends one HTTP request per run to a fixed URL, and a feeder function can't send requests itself. To page through results and move the start date forward, the integration combines three TheHive components:

1. The **alert feeder** requests one page of 100 alarms and passes it to the **feeder function**.
2. The function creates the missing alerts, then writes the URL of the next request to a **cursor alert** titled *[SOCRadar] Feeder cursor*.
3. A **notification** on the cursor alert sends that URL to the TheHive API, which updates the feeder. TheHive runs a feeder as soon as it's updated, so the next page is requested right away.

The function alternates between two kinds of passes:

| Pass | Requests | When |
|---|---|---|
| Recent | Alarms created since the newest alarm already seen, page after page | Every 5 minutes, at the feeder interval |
| Lookback | Every page of alarms created in the last 5 days | Every 60 minutes, between two recent passes |

When a recent pass finds nothing new, the URL doesn't change, the notification doesn't fire, and the feeder waits for its next interval.

The function also repairs itself:

* If the feeder ran an outdated URL, for example because another feeder update overwrote it, the function detects it from the alarm dates and requests the page again.
* If a requested page never arrives, the function retries at each run and, after 3 retries, creates one health alert per day titled *[SOCRadar] Paging isn't applied to the SOCRadar feeder*.

### TheHive behaviors behind this design

These were verified on TheHive 5.8:

* TheHive rejects template placeholders in a feeder URL, and functions can't send HTTP requests.
* Two runs that process the same alarm at the same time can both create it, so the integration uses a single feeder: its runs never overlap.
* Updating two feeders at the same time can make TheHive drop one of the updates. A single feeder avoids it, and the self-repair covers updates made to other feeders.
* A function run must finish within 1 minute, or TheHive rolls back everything it created. A run handles at most one page of 100 alarms.
* An uncaught error in a function also rolls back the whole run, so the function logs errors instead of raising them.

## Step 1: Get your SOCRadar API key and company ID

1. Log in to the [SOCRadar platform](https://platform.socradar.com).
2. Copy the **company API key** from the platform's API settings. If you don't have one, ask your SOCRadar account team to enable API access.
3. Note your **company ID**. It appears in the platform URL after `/app/company/`.

## Step 2: Create the TheHive service account

1. As an administrator, create a **service** user in the organization that receives the alerts, for example *socradar-feeder@<your-domain>*.
2. Assign it the *org-admin* profile, or any profile with the `manageConfig` permission.
3. Create an API key for it and save the key. You'll need it in the next step.

## Step 3: Create the paging notification

Create the notification before the feeder, so the feeder's first run can already page. If you create it after the feeder, nothing is lost: the function retries the first page request at the next feeder interval.

1. Log in with a user of the organization that receives the alerts, not with the platform administrator of the `admin` organization. Go to the **Organization** view, then select the **Notifications** tab.

2. Select **+** and enter the following information:

    | Field | Value |
    |---|---|
    | Name | *SOCRadar-paging* |
    | Send notification to every user in the organisation | Off |
    | Trigger | *FilteredEvent* |
    | Enable notification | On |

3. Enter this filter. Replace `<company_id>` with your SOCRadar company ID:

    ```json
    {
      "_and": [
        { "_is": { "_field": "objectType", "_value": "Alert" } },
        { "_is": { "_field": "object.sourceRef", "_value": "socradar-cursor:<company_id>" } },
        { "_startsWith": { "_field": "details.description", "_value": "http" } }
      ]
    }
    ```

4. Select the **HttpRequest** notifier and enter the following information:

    | Field | Value |
    |---|---|
    | Endpoint | Leave empty |
    | Method | *PUT* |
    | URL | `<thehive_url>/api/v1/connector/alert-feeder/SOCRadar` |
    | Headers | `Content-Type`: `application/json` |
    | Auth type | *Bearer*, with the service account API key from Step 2 |

    `<thehive_url>` is the URL at which TheHive can reach its own API, for example `http://localhost:9000` on a single node, or your public TheHive URL behind a reverse proxy. `SOCRadar` at the end is the name of the feeder you create in Step 4.

5. Enter this template. Replace `<socradar_api_key>` with your SOCRadar company API key:

    ```json
    {
      "description": "SOCRadar alarms, paged by the SOCRadar-paging notification",
      "method": "GET",
      "url": "{{{audit.details.description}}}",
      "interval": { "value": 5, "unit": "Minutes" },
      "headers": [{ "key": "API-Key", "value": "<socradar_api_key>" }],
      "auth": { "type": "none" },
      "requestTimeout": { "value": 60, "unit": "Seconds" },
      "responseMaxSize": 20971520,
      "enabled": true
    }
    ```

    > **Warning:** Each update replaces the whole feeder configuration with this template. Keep the interval, timeout, size and API key here identical to the feeder settings in Step 4. Use triple braces around `audit.details.description`: double braces escape the `&` characters of the URL.

6. Select **Confirm**.

## Step 4: Create the alert feeder

1. Select the **Connectors** tab. On narrow screens, it's in the **⋯** menu at the end of the tab bar.

2. In the **General settings** section, enter the following information:

    | Field | Value |
    |---|---|
    | Name | *SOCRadar*. It must match the end of the notification URL. |
    | Interval | *5 minutes* |
    | Request timeout time | *60* seconds |
    | Request response max size | *20* MB |
    | Description | *SOCRadar alarms, paged by the SOCRadar-paging notification* |

3. In the **HTTP request** section, enter the following information:

    | Field | Value |
    |---|---|
    | Method | *GET* |
    | URL | `https://platform.socradar.com/api/company/<company_id>/incidents/v4?limit=100&page=1&include_company_id=true` |
    | Headers | `API-Key`: your SOCRadar company API key |
    | Authentication | *None*. The **Key** type can't set the `API-Key` header name. |

    This first URL is only used for the first run. The function replaces it with the paging URL.

4. Select **Test connection**. An invalid key returns `Unauthorized Access to use API! Check your api key!`.

5. In the **Create function** section, enter the following information. This section always creates a new function: you can't select an existing one, and the name must be unique in the organization.

    | Field | Value |
    |---|---|
    | Function name | *SOCRadar-fn* |
    | Description | *Creates TheHive alerts from SOCRadar alarms and pages through the Incident API* |
    | Definition | Paste the content of [function_Feeder_alertFromSOCRadar.js](../thehive/functions/function_Feeder_alertFromSOCRadar.js) and set `COMPANY_ID` at the top to your SOCRadar company ID. |

6. Select **Confirm**. TheHive runs the feeder immediately.

> **Warning:** Don't select **Run** on this feeder. The feeder runs by itself, and a manual run that overlaps a scheduled or paging run can create duplicate alerts. To change the function code later, edit it in the **Functions** tab.

## Step 5: Verify the setup

1. Open the **Alerts** list and filter on the type *socradar-feeder*. The *[SOCRadar] Feeder cursor* alert appears after the first run, with the status *Ignored*. Its description is the next request URL, and its summary holds the paging state.
2. Within a few minutes, the first lookback pass imports the alarms of the last 5 days, then the feeder switches to recent passes.
3. Each run writes a summary line to the TheHive application log, for example:

    ```text
    SOCRadar feeder (recent pass, page 1): received 3 of 1 pages, older than 5 days 0, already in TheHive 1, created 2, deferred to next run 0, duplicates 0, failed 0, next request https://platform.socradar.com/api/...
    ```

> **Note:** Don't delete or merge the cursor alert. If it's deleted, the next run starts over with a lookback pass, which doesn't create duplicates.

## Function settings

Edit these constants at the top of the function definition:

| Constant | Default | Purpose |
|---|---|---|
| `COMPANY_ID` | `"<company_id>"` | Your SOCRadar company ID. Required. |
| `API_BASE` | `"https://platform.socradar.com/api"` | SOCRadar API base URL. |
| `EXTRA_QUERY` | `""` | Filters appended to every request. See [Optional filters](#optional-filters). |
| `PAGE_SIZE` | `100` | Alarms per request. The API accepts at most 100. |
| `LOOKBACK_DAYS` | `5` | Age of the oldest alarms the lookback pass ingests. Older alarms are ignored. |
| `LOOKBACK_INTERVAL_MINUTES` | `60` | Minutes between two lookback passes. |
| `MAX_NEW_ALERTS_PER_RUN` | `200` | Safety cap per run, to stay under TheHive's 1-minute limit. |

## Optional filters

Set `EXTRA_QUERY` to narrow the ingested alarms, for example `"&severities=HIGH&severities=CRITICAL"`. For list parameters, repeat the key for each value. Comma-separated values aren't supported.

| Parameter | Example | Effect |
|---|---|---|
| `severities` | `&severities=HIGH&severities=CRITICAL` | Only these risk levels. |
| `status` | `&status=OPEN` | Only alarms with this status: `OPEN`, `CLOSED` or `ON_HOLD`. |
| `alarm_main_types` | `&alarm_main_types=Brand%20Protection` | Only these main types. |
| `excluded_alarm_main_types` | `&excluded_alarm_main_types=Fraud%20Protection` | Exclude these main types. |
| `alarm_sub_types` | `&alarm_sub_types=Impersonating%20Domain` | Only these sub types. |
| `tags` | `&tags=vip` | Only alarms with these SOCRadar tags. Use lowercase values. |

## Import older alarms

To import alarms older than 5 days, set `LOOKBACK_DAYS` to the number of days to import, for example `30`, and wait for the next lookback pass to finish. Then set it back to `5`. Each page is one run of a few seconds, so a long period can take several minutes.

## Rotate the API keys

* SOCRadar API key: update it in the feeder header and in the notification template.
* TheHive service account API key: update it in the notification **Auth type** settings.

## Field mapping

| TheHive alert field | SOCRadar source | Notes |
|---|---|---|
| `type` | constant `socradar-alarm` | SOCRadar main and sub types exceed TheHive's 32-character `type` limit, so they're stored as tags. |
| `source` | constant `SOCRadar` | |
| `sourceRef` | `company_id:alarm_id` | Deduplication key. |
| `title` | `[SOCRadar] ` + `alarm_type_details.alarm_generic_title` | Falls back to `title`, then to the first line of `alarm_text`. |
| `description` | Markdown summary table, `alarm_text`, mitigation, `alarm_detection_and_analysis`, related assets and entities, compliance list, the full `content` dict, and all other alarm fields (history, notes, extra, approver) | Mitigation uses `alarm_response`, or `alarm_default_mitigation_plan` when empty. In `content` and the other fields, credential values are redacted, and strings over 2,000 characters and lists over 100 items are shortened and marked `[truncated, ...]`. |
| `severity` | `alarm_risk_level` | `LOW`=1, `MEDIUM`=2, `HIGH`=3, `CRITICAL`=4. Defaults to 2. |
| `date` | `date` | Alarm creation date, UTC. |
| `externalLink` | `company_id`, `alarm_id` | `https://socradar.com/app/company/<company_id>/alarm-management?tab=approved&field=alarmId&operator=equals&value=<alarm_id>` |
| `tags` | `SOCRadar`, `main-type:<…>`, `sub-type:<…>`, `severity:<…>`, `status:<…>`, SOCRadar alarm tags | |
| `observables` | `alarm_related_assets`, `alarm_related_entities`, `alarm_asset` | Related items are `{key, value}` pairs. `domain` → `domain`, `hostname` → `hostname`, `url` and `effective_url` → `url`, `ip` → `ip`, `cert_serial_number` → `other`. Brand keywords, DNS record changes, ports and internal IDs stay in the description only. `alarm_asset` becomes an observable only when it's an IP, domain, URL, email or hash, not a company name. All observables are created with `ioc: false`: they describe affected assets, not malicious indicators. |

Disapproved alarms (`is_approved: false`) are skipped. The cursor alert and the health alerts use the type `socradar-feeder`, so they never mix with alarm alerts.

### Field length limits

The SOCRadar API doesn't truncate any field, and TheHive rejects an alert whose fields exceed its limits. The function clips values before creating the alert and appends `... [truncated]`:

| Field | TheHive limit | Function behavior |
|---|---|---|
| `title` | 512 characters | Clipped. |
| `description` | 1,048,576 characters | Each text section is clipped to 200,000 characters and `content` to 300,000, then the whole description is clipped. |
| `sourceRef` | 128 characters | Clipped. |
| `externalLink` | 4,096 characters | Clipped. |
| Each tag | 128 characters | Clipped; empty tags are dropped. |
| Observable value | 4,096 characters | Not created as an observable; listed in the description instead. |

## Troubleshooting

The function output of each run is visible in the TheHive application log.

| Symptom | Cause and fix |
|---|---|
| Test connection fails with `Check your api key` | The `API-Key` header is missing, or the key isn't a company API key. |
| Run fails with `SOCRadar API error: ...` | The API returned an error. No alerts are created in that run. |
| Run fails with `Execution of function ... timed out after 1 minute` | The function took too long. Lower `MAX_NEW_ALERTS_PER_RUN`. Nothing from the timed-out run was kept; the next run retries. |
| Request timeout error | The SOCRadar response took longer than **Request timeout time**. Raise it in the feeder and in the notification template. |
| Alert *[SOCRadar] Paging isn't applied to the SOCRadar feeder* | The notification didn't update the feeder. Check that it's enabled, that the filter contains your company ID, that its URL ends with the feeder name, that `<thehive_url>` is reachable from TheHive, and that the service account API key is valid. Enable **Log errors** on the notifier to see failed requests in the log. |
| Feeder settings revert to 10-second timeout or 10 MB size | The notification template doesn't contain them. Every update replaces the whole feeder configuration. |
| Duplicate alerts for the same alarm | Two runs overlapped, usually because the feeder was run manually. Don't select **Run** on this feeder. |
| Alerts have the tag `socradar:missing-company-id` and no link | `include_company_id=true` is missing from the request. Check that `COMPANY_ID` is set and the function code is unchanged. |
| An older alarm never appears | It was created more than `LOOKBACK_DAYS` ago. See [Import older alarms](#import-older-alarms). |
| A filter on tags returns nothing | SOCRadar matches tags in lowercase. Use lowercase values. |

For more details, see [Create an Alert Feeder](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-feeders/create-a-feeder/) and [Configure the HttpRequest Notifier](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-notifications/notifiers/http-request/).
