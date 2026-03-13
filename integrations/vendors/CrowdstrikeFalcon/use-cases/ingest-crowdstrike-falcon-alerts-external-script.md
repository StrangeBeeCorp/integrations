---
title: Ingest CrowdStrike Falcon Detections and Incidents into TheHive Using an External Script
description: Install and configure the falcon2thehive connector to automatically ingest CrowdStrike Falcon detections and incidents into TheHive as alerts in real time.
tags:
  - alert-ingestion
  - crowdstrike
  - thehive
  - automation
---
# Tutorial: Ingest CrowdStrike Falcon Detections and Incidents into TheHive Using an External Script

> **Warning:** The falcon2thehive connector is currently in beta. Features and configuration may change.

In this tutorial, we're going to install and configure the [falcon2thehive connector](https://github.com/StrangeBeeCorp/falcon2thehive) to ingest CrowdStrike Falcon detections and incidents into TheHive as alerts.

By the end, you'll have a working setup that automatically brings CrowdStrike Falcon detections and incidents into TheHive in real time, helping your team respond as soon as they happen.

Before you begin, ensure that the CrowdStrike Falcon detections and incidents you want to ingest are part of the supported event types:

* DetectionSummaryEvent
* EppDetectionSummaryEvent
* IdentityProtectionEvent
* IdpDetectionSummaryEvent
* MobileDetectionSummaryEvent

> **Tip:** More integration options
> For the complete list of integration options between CrowdStrike Falcon and TheHive, see [CrowdStrike Falcon Integration with TheHive](crowdstrike-falcon-integrations.md).

## Step 1: Create an API client in CrowdStrike Falcon

Let's start by setting up an API client in your CrowdStrike Falcon console. This will allow the connector to securely access your detections and incidents.

1. Go to [https://www.crowdstrike.com/login/](https://www.crowdstrike.com/login/).

2. Log in to your CrowdStrike Falcon tenant with an administrator account.

3. In the console, go to **Support and resources**.

4. Under **Resources and tools**, select **API clients and keys**.

5. Select **Create API client**.

6. Enter the required details. Make sure to select **Read** and **Write** permissions for both the **Alerts** and **Incidents** scopes. The connector needs these permissions to work properly.

7. Select **Create**.

8. You'll now see your client ID, secret, and base URL. Copy and save them somewhere safe. You'll need them in the next step.

## Step 2: Install and configure falcon2thehive

You can install the falcon2thehive connector using either a [Docker deployment](#docker-deployment) or a [manual installation](#manual-python-installation), depending on your setup and preferences. Docker is the recommended method for ease of deployment and consistency.

### Docker deployment

> **Note:** Installing the falcon2thehive connector with Docker is the easiest and most reliable option. It helps keep your environment clean and makes deployment straightforward.

> **Warning:** Before you begin, make sure [Docker](https://docs.docker.com/get-started/get-docker/) is installed on your system.

> **Tip:** Quick testing
> If you just want to test the falcon2thehive connector, you can pass credentials directly as environment variables instead of using a `.env` file.
>
> ```bash
> docker run -d \
>     --restart unless-stopped \
>     -e CRWD_BASE_URL="<crowdstrike_base_url>" \
>     -e CRWD_CLIENT_ID="<crowdstrike_client_id>" \
>     -e CRWD_CLIENT_SECRET="<crowdstrike_client_secret>" \
>     -e THEHIVE_URL="<thehive_url>" \
>     -e THEHIVE_API_KEY="<thehive_api_key>" \
>     --name f2h falcon2thehive
> ```

1. Build the Docker image.

    ```bash
    docker build -t falcon2thehive .
    ```

2. Set up your `.env` file.

    a. Start by copying the example file.

    ```bash
    cp .env.example .env
    ```

    b. Open the `.env` file and enter your actual credentials. Use the client ID, secret, and base URL from [**Step 1**](#step-1-create-an-api-client-in-crowdstrike-falcon).

    ```
    CRWD_BASE_URL=<crowdstrike_base_url>
    CRWD_CLIENT_ID=<crowdstrike_client_id>
    CRWD_CLIENT_SECRET=<crowdstrike_client_secret>
    THEHIVE_URL=<thehive_url>
    THEHIVE_API_KEY=<thehive_api_key>
    # Optional settings
    THEHIVE_ORG=<thehive_organization_name>
    APP_ID=falcon2thehive
    ```

    **Environment variables explained:**

    | Variable | Required | Description |
    |---|---|---|
    | `CRWD_BASE_URL` | Yes | Your CrowdStrike Falcon base URL |
    | `CRWD_CLIENT_ID` | Yes | API client ID from Step 1 |
    | `CRWD_CLIENT_SECRET` | Yes | API client secret from Step 1 |
    | `THEHIVE_URL` | Yes | URL of your TheHive instance |
    | `THEHIVE_API_KEY` | Yes | API key for TheHive authentication |
    | `THEHIVE_ORG` | No | Target organization in TheHive |
    | `APP_ID` | No | Application ID for the CrowdStrike streaming API (default: `falcon2thehive`) |

    c. Run the container.

    ```bash
    docker run -d \
        --restart unless-stopped \
        --env-file .env \
        --name f2h falcon2thehive
    ```

At this point, the connector should be live and syncing CrowdStrike Falcon detections and incidents with TheHive.

> **Tip:** Connector operation commands
>
> * View logs:
>   ```bash
>   docker logs -f f2h
>   ```
>
> * Stop the connector:
>   ```bash
>   docker stop f2h
>   ```
>
> * Restart the connector with the same configuration:
>   ```bash
>   docker start f2h
>   ```
>
> * To change environment variables:
>
>     a. Stop and remove the container:
>     ```bash
>     docker stop f2h
>     docker rm f2h
>     ```
>
>     b. Start a new one with updated environment variables using `-e` flags or an updated `.env` file:
>     ```bash
>     docker run -d --restart unless-stopped --env-file .env --name f2h falcon2thehive
>     ```

### Manual Python installation

> **Warning:** Before you begin, make sure the following tools are installed on your system:
>
> * [Python 3.X](https://www.python.org/downloads/)
> * [TheHive4py 2.X](https://github.com/TheHive-Project/TheHive4py)
> * [FalconPy SDK](https://github.com/CrowdStrike/falconpy)

1. Clone the falcon2thehive repository.

    ```bash
    git clone https://github.com/StrangeBeeCorp/falcon2thehive.git
    cd falcon2thehive
    ```

2. Recommended: Create and activate a virtual environment.

    Using a virtual environment helps isolate dependencies so they don't interfere with other Python projects.

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies.

    ```bash
    pip install -r requirements.txt
    ```

4. Set your environment variables.

    You can export the variables directly in your shell.

    ```
    export CRWD_BASE_URL="<crowdstrike_base_url>"
    export CRWD_CLIENT_ID="<crowdstrike_client_id>"
    export CRWD_CLIENT_SECRET="<crowdstrike_client_secret>"
    export THEHIVE_URL="<thehive_url>"
    export THEHIVE_API_KEY="<thehive_api_key>"
    # Optional settings
    export THEHIVE_ORG="<organization_name>"
    export APP_ID="falcon2thehive"
    ```

    **Environment variables explained:**

    | Variable | Required | Description |
    |---|---|---|
    | `CRWD_BASE_URL` | Yes | Your CrowdStrike Falcon base URL |
    | `CRWD_CLIENT_ID` | Yes | API client ID from Step 1 |
    | `CRWD_CLIENT_SECRET` | Yes | API client secret from Step 1 |
    | `THEHIVE_URL` | Yes | URL of your TheHive instance |
    | `THEHIVE_API_KEY` | Yes | API key for TheHive authentication |
    | `THEHIVE_ORG` | No | Target organization in TheHive |
    | `APP_ID` | No | Application ID for the CrowdStrike streaming API (default: `falcon2thehive`) |

5. Run the connector.

    Now it's time to start the connector.

    * To run it in the background so it stays active while you continue working on other tasks:

    ```bash
    python falcon2thehive.py &
    ```

    * To run it in the foreground and see live logs directly in your terminal, which is useful for testing or troubleshooting:

    ```bash
    python falcon2thehive.py
    ```

You should now start seeing CrowdStrike Falcon detections and incidents in your TheHive alert list. If you're running it in the foreground, you should see log messages confirming a successful connection and alert ingestion.

## Next steps

* [Synchronize Alert and Case Statuses from TheHive to CrowdStrike Falcon](synchronize-status-thehive-crowdstrike-falcon.md)
