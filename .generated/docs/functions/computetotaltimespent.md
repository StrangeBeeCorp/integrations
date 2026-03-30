# computeTotalTimeSpent

## Metadata

- **Version:** `1.0.0`
- **Type:** Generic Function
- **Function Type:** `Notifier`
- **Kind:** `function`
- **Mode:** `Enabled`
- **Source File:** `integrations/generic/functions/function_notifier_computeTotalTimeSpent.js`

## Description

On task closure, compute the duration of the task rounded up to the nearest minute. It's then added to the TASK_TIME_CUSTOMFIELD integer customfield at the case level. Use a trigger "task closed"

## Code

```javascript
// Notification trigger needed : task closed.
// ============================================================
// CONFIGURATION - Edit these values to match your environment
// ============================================================
var TASK_TIME_CUSTOMFIELD = "TASK_TIME_CUSTOMFIELD";
// ============================================================


/**
 * Resolve the case object from the task notification input.
 */
function getCaseFromInput(input) {
    if (
        input.objectType === "Task" &&
        input.object &&
        input.object.case
    ) {
        return input.object.case;
    }
    return null;
}


/**
 * Compute elapsed minutes between two epoch-ms timestamps.
 * Result is rounded UP to the nearest full minute (minimum 0).
 */
function elapsedMinutesCeil(startMs, endMs) {
    var diffMs = endMs - startMs;
    if (diffMs <= 0) return 0;
    return Math.ceil(diffMs / 60000);
}


/**
 * Read the current accumulated value from the case custom field.
 * Returns 0 if not set, not a number, or negative.
 */
function readCurrentMinutes(caseObj) {
    if (
        caseObj.customFieldValues &&
        caseObj.customFieldValues[TASK_TIME_CUSTOMFIELD] !== undefined
    ) {
        var val = caseObj.customFieldValues[TASK_TIME_CUSTOMFIELD];
        if (typeof val === "number" && val > 0) return val;
    }
    return 0;
}


function handle(input, context) {

    // ── 1. Guard: must be a Task event ──────────────────────────────────────
    if (input.objectType !== "Task") {
        return { skipped: true, reason: "Not a task event" };
    }

    var task = input.object;

    // ── 2. Guard: must be a closing operation ────────────────────────────────
    // Notification fires on any task update; we only care about final states.
    if (task.status !== "Completed" && task.status !== "Cancel") {
        return { skipped: true, reason: "Task not in a closed status", status: task.status };
    }

    // ── 3. Resolve parent case ───────────────────────────────────────────────
    var caseObj = getCaseFromInput(input);
    if (!caseObj || !caseObj._id) {
        return { skipped: true, reason: "Cannot resolve parent case from task" };
    }
    var caseId = caseObj._id;

    // ── 4. Resolve task timestamps ───────────────────────────────────────────
    var endMs = task.endDate || task._updatedAt || null;
    if (!endMs) {
        return { skipped: true, reason: "Task has no end timestamp", taskId: task._id };
    }

    // Prefer explicit startDate; fall back to _createdAt.
    var startMs = task.startDate || task._createdAt || null;
    if (!startMs) {
        return { skipped: true, reason: "Task has no start timestamp", taskId: task._id };
    }

    // ── 5. Compute this task's duration ─────────────────────────────────────
    var taskMinutes = elapsedMinutesCeil(startMs, endMs);
    console.log(
        "Task " + task._id + " duration: " + taskMinutes + " min" +
        " (start=" + new Date(startMs).toISOString() +
        ", end=" + new Date(endMs).toISOString() + ")"
    );

    // ── 6. Read current accumulated value from the case ──────────────────────
    var previousMinutes = readCurrentMinutes(caseObj);
    var totalMinutes    = previousMinutes + taskMinutes;
    console.log(
        "Case " + caseId + ": previous=" + previousMinutes +
        " min, adding=" + taskMinutes +
        " min, new total=" + totalMinutes + " min"
    );

    // ── 7. Persist updated total back to the case ────────────────────────────
    try {
        var customFields = {};
        customFields[TASK_TIME_CUSTOMFIELD] = totalMinutes;
        context.caze.update(caseId, { customFields: customFields });
    } catch (e) {
        console.error("Failed to update case custom field: " + String(e));
        return {
            success: false,
            reason:  "Case update failed",
            error:   String(e),
            caseId:  caseId,
            taskId:  task._id
        };
    }

    return {
        success:         true,
        caseId:          caseId,
        taskId:          task._id,
        taskMinutes:     taskMinutes,
        previousMinutes: previousMinutes,
        totalMinutes:    totalMinutes
    };
}
```

---

*This documentation is auto-generated. Do not edit manually.*
