# flagCase

## Metadata

- **Version:** `1.0.0`
- **Type:** Generic Function
- **Function Type:** `Notifier`
- **Kind:** `function`
- **Mode:** `Enabled`
- **Source File:** `integrations/generic/functions/function_notifier_flagCase.js`

## Description

Flags the case it is invoked for. Works as a Notifier on a Case event such as a FilteredEvent on Case update, and as an Action run manually from a case (create it with type Action:Case). Alerts cannot be flagged in TheHive 5, so this function only targets cases. Already flagged cases are left untouched to avoid update loops on a Case update trigger.

## Code

```javascript
// Set to false to unflag instead of flag.
const FLAG_VALUE = true;

/**
 * Resolve the case to flag from the function input.
 *
 * The input shape depends on how the function is invoked:
 *
 * - Notifier on a Case event: input.objectType === "Case" and the case is at
 *   input.object (id input.object._id, current flag input.object.flag).
 * - Action:Case run manually from a case: input IS the case, so the id is at
 *   input._id and its fields (including flag) are on input directly, matching
 *   function_Action_assignToMe.js which uses input._id.
 *
 * Returns { id, flagged } or null.
 */
function resolveCase(input) {
    // Notifier on a Case event
    if (input.objectType === "Case" && input.object && input.object._id) {
        return { id: input.object._id, flagged: input.object.flag === true };
    }

    // Action:Case: input is the case itself (no objectType wrapper)
    if (!input.objectType && input._id) {
        return { id: input._id, flagged: input.flag === true };
    }

    return null;
}

function handle(input, context) {
    const target = resolveCase(input);

    if (!target) {
        console.log(`Skipping: no case found in input (objectType=${input.objectType}, action=${input.action})`);
        return { skipped: true, reason: "No case in function input" };
    }

    if (target.flagged === FLAG_VALUE) {
        console.log(`Case ${target.id} already has flag=${FLAG_VALUE}, nothing to do`);
        return { skipped: true, reason: "Flag already set", id: target.id };
    }

    try {
        context.caze.update(target.id, { flag: FLAG_VALUE });
        console.log(`Case ${target.id} flag set to ${FLAG_VALUE}`);
        return { success: true, id: target.id, flag: FLAG_VALUE };
    } catch (error) {
        console.error(`Failed to update case ${target.id}: ${error.message}`);
        return { success: false, id: target.id, error: error.message };
    }
}
```

---

*This documentation is auto-generated. Do not edit manually.*
