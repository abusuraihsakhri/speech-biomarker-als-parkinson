"use strict";
function evaluateTask(raw) {
  const taskId = String(raw.task_id || "").trim();
  const targetId = String(raw.target_identifier || "").trim();
  const descriptor = String(raw.status_descriptor || "").trim();
  if (!taskId || taskId.length > 128 || !targetId || targetId.length > 128)
    throw new Error("Task and sample IDs are required (maximum 128 characters).");
  if (!descriptor || descriptor.length > 64)
    throw new Error("A status descriptor is required (maximum 64 characters).");
  const primary = Number(raw.primary_metric);
  const secondary = Number(raw.secondary_metric);
  if (raw.primary_metric === "" || raw.secondary_metric === "" ||
      !Number.isFinite(primary) || !Number.isFinite(secondary))
    throw new Error("Enter finite numeric values for both measurements.");
  const critical = raw.is_critical_flag === true;
  const alerts = [];
  if (primary > 25)
    alerts.push({worker: "InvariantQCWorker", urgency: "ELEVATED_RISK",
      summary: "Primary measurement exceeds demonstration threshold (25)."});
  if (critical || secondary > 12)
    alerts.push({worker: "SafetyEscalationWorker",
      urgency: critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Priority flag set or secondary measurement exceeds demonstration threshold (12)."});
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
    .some(word => descriptor.toUpperCase().includes(word)))
    alerts.push({worker: "ProtocolConformanceWorker", urgency: "ELEVATED_RISK",
      summary: "Status descriptor matches a predefined anomaly keyword."});
  const urgency = alerts.some(a => a.urgency === "CRITICAL_STAT_PANIC")
    ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    task_id: taskId, target_identifier: targetId, primary_metric: primary,
    secondary_metric: secondary, status_descriptor: descriptor,
    is_critical_flag: critical, overall_urgency: urgency,
    total_alerts: alerts.length, alerts,
    note: "Rule-based numeric prototype only. No speech/audio processing, disease prediction, or clinical validation."
  };
}
if (typeof module !== "undefined" && module.exports) module.exports = {evaluateTask};
if (typeof document !== "undefined") {
  const form = document.getElementById("audit-form");
  const output = document.getElementById("output");
  const status = document.getElementById("status");
  const count = document.getElementById("count");
  const save = document.getElementById("save");
  let latest = null, completed = 0;
  form.addEventListener("submit", event => {
    event.preventDefault();
    try {
      const result = evaluateTask({
        task_id: document.getElementById("task-id").value,
        target_identifier: document.getElementById("target-id").value,
        primary_metric: document.getElementById("primary").value,
        secondary_metric: document.getElementById("secondary").value,
        status_descriptor: document.getElementById("descriptor").value,
        is_critical_flag: document.getElementById("priority").checked
      });
      latest = result;
      output.textContent = JSON.stringify(result, null, 2);
      status.textContent = result.overall_urgency.replaceAll("_", " ");
      status.dataset.urgency = result.overall_urgency;
      count.textContent = String(++completed);
      save.disabled = false;
    } catch (error) {
      latest = null;
      save.disabled = true;
      status.textContent = "INVALID INPUT";
      status.dataset.urgency = "INVALID";
      output.textContent = error.message;
    }
  });
  save.addEventListener("click", () => {
    if (!latest) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(latest, null, 2) + "\n"], {type: "application/json"}));
    const link = document.createElement("a");
    link.href = url;
    link.download = "numeric-audit.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  });
}
