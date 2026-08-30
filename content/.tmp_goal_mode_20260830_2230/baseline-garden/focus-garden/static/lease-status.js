// The lease is reported by the existing Windows intervention agent heartbeat.
// This augments the health panel only; it never runs a second agent.
const renderSystemStatusWithLease = renderSystemStatus;
renderSystemStatus = function () {
  renderSystemStatusWithLease();
  const windows = state.systemStatus?.bridges?.windows;
  const board = document.querySelector("#systemStatusBoard");
  if (!board) return;
  if (windows) {
    const active = windows.lease_state === "active";
    const card = document.createElement("article");
    card.className = "pixel-panel health-card";
    card.innerHTML = `<p class="eyebrow">FOCUS LEASE</p><h3>电脑专注锁定</h3>
      <div class="health-list">${healthRow("Cold Turkey", active ? "active" : "idle",
        active ? (windows.lease_blocks || []).join(" / ") : "当前没有 agent 托管的锁定")}</div>`;
    board.appendChild(card);
  }

  const gate = state.systemStatus?.steam_unlock || {};
  const available = gate.available === true;
  const completed = Number(gate.completed_tomatoes || 0);
  const required = Number(gate.required_completed_tomatoes || 5);
  const tomatoDetail = available
    ? `${completed} / ${required} 个${gate.tomato_requirement_met ? " · 已达成" : ` · 还差 ${Math.max(0, required - completed)} 个`}`
    : "当前指标暂时无法读取";
  const primaryDetail = !available
    ? "当前指标暂时无法读取"
    : gate.primary_task_set !== true
      ? "今天尚未设置主要任务"
      : gate.primary_task_completed
        ? "已设置并完成"
        : "已设置，尚未完成";
  const reasons = Array.isArray(gate.blocking_reasons) && gate.blocking_reasons.length
    ? gate.blocking_reasons.join("；")
    : "两项条件均已达成，Agent 将停止续锁";
  const unlockCard = document.createElement("article");
  unlockCard.className = "pixel-panel health-card wide";
  unlockCard.innerHTML = `<p class="eyebrow">STEAM UNLOCK</p>
    <h3>Steam 解锁指标 · ${gate.eligible ? "已达成" : "未达成"}</h3>
    <p class="setting-help">解锁要求：当天完成至少 ${required} 个番茄，并完成今天的主要任务。两项必须同时满足。</p>
    <div class="health-list">
      ${healthRow("总体解锁", gate.eligible ? "ok" : available ? "blocked" : "unavailable", reasons)}
      ${healthRow("完成番茄", gate.tomato_requirement_met ? "ok" : available ? "pending" : "unavailable", tomatoDetail)}
      ${healthRow("今日主要任务", gate.primary_task_completed ? "ok" : available ? "pending" : "unavailable", primaryDetail)}
    </div>`;
  board.appendChild(unlockCard);
};
