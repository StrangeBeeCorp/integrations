# externalAccessAutomation

## Metadata

- **Version:** `1.0.0`
- **Type:** Generic Function
- **Function Type:** `Notifier`
- **Kind:** `function`
- **Mode:** `Enabled`
- **Source File:** `integrations/generic/functions/function_notifier_externalAccessAutomation.js`

## Description

Automatically grants external case access to client users when a case is closed. It reads the client custom field from the case, extracts the company domain label, and retrieves the external users linked to the case. Users whose email domain matches the client domain are identified and granted external access to the case.

## Code

```javascript
// Configuration
const CLIENT_CUSTOM_FIELD = "client";

/**
 * Extract the domain label from the client custom field value.
 * Handles plain label ("company"), domain+TLD ("company.com"), or email ("x@company.com").
 * Always returns the first label only, lowercased: "company"
 */
function extractDomainLabel(clientValue) {
    let value = clientValue.trim().toLowerCase();

    // If it's an email, take the domain part first
    if (value.includes("@")) {
        value = value.split("@")[1];
    }

    // Strip TLD if present: "company.com" -> "company"
    return value.split(".")[0];
}

/**
 * Extract the client custom field value from the case object.
 * TheHive may expose customFields as:
 *   - an object: { "client": { "string": "company" } }
 *   - an array:  [ { "name": "client", "value": "company" } ]  (seen in notification payload)
 * Returns the raw string value or null.
 */
function extractClientFieldValue(caseObj) {
    const cf = caseObj.customFields;

    // Object format: { "client": { "string": "...", ... } }
    if (cf && !Array.isArray(cf) && typeof cf === "object") {
        const field = cf[CLIENT_CUSTOM_FIELD];
        if (field) {
            return field.string || field.text || field.value || null;
        }
        return null;
    }

    // Array format: [ { "name": "client", "value": "..." }, ... ]
    if (Array.isArray(cf)) {
        const field = cf.find(f => f.name === CLIENT_CUSTOM_FIELD);
        return field ? (field.value || field.string || null) : null;
    }

    // Fallback: customFieldValues object (also present in some payloads)
    const cfv = caseObj.customFieldValues;
    if (cfv && typeof cfv === "object" && cfv[CLIENT_CUSTOM_FIELD]) {
        return String(cfv[CLIENT_CUSTOM_FIELD]);
    }

    return null;
}

/**
 * Retrieve all external users linked to the case via the query API.
 */
function getExternalUsers(context, caseId) {
    return context.query.execute([
        { "_name": "getCase", "idOrName": caseId },
        { "_name": "organisations" },
        { "_name": "users" },
        {
            "_name": "filter",
            "_eq": { "_field": "type", "_value": "External" }
        }
    ]);
}

/**
 * Filter users whose login domain label matches the client domain label.
 * "user@company.co.jp" matches label "company".
 */
function filterUsersByDomainLabel(users, domainLabel) {
    return users
        .map(u => u.login || u._id || "")
        .filter(login => {
            if (!login.includes("@")) return false;
            const loginDomainLabel = login.split("@")[1].split(".")[0].toLowerCase();
            return loginDomainLabel === domainLabel;
        });
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

function handle(input, context) {
    // Guard: must be a Case update action
    // Payload uses: objectType = "Case", action = "update"
    if (input.objectType !== "Case" || input.action !== "update") {
        return { skipped: true, reason: "Not a case update event" };
    }

    const caseObj = input.object;

    // Guard: only proceed when the case stage reaches "Closed"
    // (status can be "Resolved", "Indeterminate", etc. — stage is the reliable field)
    if (caseObj.stage !== "Closed") {
        return { skipped: true, reason: "Case stage is not Closed" };
    }

    const caseId = caseObj._id;

    try {
        // 1. Extract client value from custom fields
        const clientValue = extractClientFieldValue(caseObj);

        if (!clientValue) {
            console.log(`Case ${caseId}: custom field '${CLIENT_CUSTOM_FIELD}' is missing or empty — skipping`);
            return { skipped: true, reason: `Custom field '${CLIENT_CUSTOM_FIELD}' empty` };
        }

        const domainLabel = extractDomainLabel(clientValue);
        console.log(`Case ${caseId}: resolved client domain label = '${domainLabel}'`);

        // 2. Retrieve external users linked to this case
        const externalUsers = getExternalUsers(context, caseId);
        console.log(`Case ${caseId}: found ${externalUsers.length} external user(s)`);

        if (!externalUsers.length) {
            console.log(`Case ${caseId}: no external users linked — skipping`);
            return { skipped: true, reason: "No external users on case" };
        }

        // 3. Filter users matching the client domain label
        const eligibleUsers = filterUsersByDomainLabel(externalUsers, domainLabel);
        console.log(`Case ${caseId}: ${eligibleUsers.length} user(s) match domain '${domainLabel}'`);

        if (!eligibleUsers.length) {
            console.log(`Case ${caseId}: no users match domain '${domainLabel}' — skipping`);
            return { skipped: true, reason: `No users match domain '${domainLabel}'` };
        }

        // 4. Grant external access to the case
        context.caze.manageCaseAccess(caseId, {
            access: {
                _kind: "ExternalAccessKind",
                users: eligibleUsers
            }
        });

        console.log(`Case ${caseId}: external access granted to ${eligibleUsers.length} user(s)`);

        return {
            success: true,
            caseId: caseId,
            clientDomain: domainLabel,
            usersGranted: eligibleUsers
        };

    } catch (error) {
        console.error(`Case ${caseId}: unexpected error — ${error.message}`);
        return { success: false, error: error.message };
    }
}
```

---

*This documentation is auto-generated. Do not edit manually.*
