// Web counterpart of New Pomodoro Timer's one-pause rule. The Pi database
// is authoritative; this file only renders controls and calls fixed routes.
(function () {
  const start = document.querySelector("#startBtn");
  if (!start) return;

  const panel = document.createElement("div");
  panel.id = "focusSessionActions";
  panel.className = "focus-session-actions hidden";
  panel.innerHTML = '<button id="focusPauseBtn" class="outline-button" type="button">暂停一次</button><p id="focusPauseHint" class="focus-pause-hint"></p>';
  start.insertAdjacentElement("afterend", panel);

  const style = document.createElement("style");
  style.textContent = ".focus-session-actions{display:grid;grid-template-columns:1fr;gap:9px;margin:12px 0 2px}.focus-session-actions .outline-button{width:100%;background:#fff3bd}.focus-pause-hint{margin:0;color:var(--muted);font-size:12px;line-height:1.5}.focus-session-actions .outline-button{box-shadow:4px 4px 0 rgba(26,82,60,.22)}";
  document.head.appendChild(style);

  function secondsUntil(value) {
    const timestamp = Date.parse(value || "");
    return Number.isFinite(timestamp) ? Math.max(0, Math.ceil((timestamp - Date.now()) / 1000)) : 0;
  }

  function durationText(seconds) {
    return String(Math.floor(seconds / 60)).padStart(2, "0") + ":" + String(seconds % 60).padStart(2, "0");
  }

  // The dashboard can re-render while an async refresh is in flight.  Keep
  // this enhancement optional rather than letting a missing legacy element
  // break the whole page.
  function setText(selector, value) {
    const element = document.querySelector(selector);
    if (element) element.textContent = value;
  }

  const renderBeforePauseUi = renderFocus;
  renderFocus = function () {
    renderBeforePauseUi();
    const focus = state.data?.focus;
    const pause = document.querySelector("#focusPauseBtn");
    const hint = document.querySelector("#focusPauseHint");
    const note = document.querySelector(".lock-note");
    panel.classList.toggle("hidden", !focus);
    if (!focus || !pause || !hint) return;

    const paused = Boolean(focus.paused);
    const used = Boolean(focus.was_paused);
    pause.classList.toggle("hidden", paused || used);
    if (paused) {
      const seconds = secondsUntil(focus.resume_at);
      clearInterval(state.timer);
      setText("#timerDisplay", "暂停 " + durationText(seconds));
      setText("#focusKicker", "专注暂停中；到点会自动恢复计时，并重新交给 agent 托管锁定。");
      if (note) note.textContent = "暂停期间已请求解除电脑锁定；暂停结束时会自动恢复锁定。";
      hint.textContent = "暂停还剩 " + durationText(seconds) + "；本轮已使用一次暂停，完成时只按原计划时长的一半成长。";
      const countdown = () => {
        const remaining = secondsUntil(focus.resume_at);
        setText("#timerDisplay", remaining ? "暂停 " + durationText(remaining) : "正在恢复…");
        if (!remaining) {
          clearInterval(panel._pauseTimer);
          setTimeout(load, 2500);
        }
      };
      clearInterval(panel._pauseTimer);
      panel._pauseTimer = setInterval(countdown, 1000);
    } else if (used) {
      clearInterval(panel._pauseTimer);
      if (note) note.textContent = "本轮曾暂停一次；完成时只会按原计划时长的一半成长。";
      hint.textContent = "本轮已用过一次暂停；完成时会按半额成长。";
    } else {
      clearInterval(panel._pauseTimer);
      if (note) note.textContent = "开始后由现有电脑 agent 管理可暂停的锁定。";
      hint.textContent = "需要暂离时可暂停一次：确认预计分钟数后，电脑锁定会解除；到点自动恢复，本轮完成按半额成长。";
    }
  };

  async function pauseFocus() {
    const value = window.prompt("预计暂停多少分钟？（1–120；本轮只可暂停一次）", "10");
    if (value === null) return;
    const minutes = Number(value);
    if (!Number.isInteger(minutes) || minutes < 1 || minutes > 120) {
      return toast("请输入 1–120 的整数分钟数。", true);
    }
    if (!window.confirm("确认暂停 " + minutes + " 分钟？暂停期间会解除电脑锁定；到时自动恢复锁定与计时。本轮成长按一半计算。")) {
      return;
    }
    try {
      const pauseButton = document.querySelector("#focusPauseBtn");
      if (pauseButton) pauseButton.disabled = true;
      await api("/api/focus/pause", { method: "POST", body: JSON.stringify({ pause_minutes: minutes }) });
      await load();
      toast("已暂停；电脑锁定解除请求已交给 agent，到点将自动恢复。");
    } catch (error) {
      toast(error.message, true);
    } finally {
      const pauseButton = document.querySelector("#focusPauseBtn");
      if (pauseButton) pauseButton.disabled = false;
    }
  }

  document.querySelector("#focusPauseBtn").onclick = pauseFocus;
}());
