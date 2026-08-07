from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from common import load_json
from computer_intervention import (
    build_manual_focus_request,
    build_manual_focus_release_request,
    latest_pending_phone_request,
    latest_pending_request,
    receive_computer_intervention_event,
    receive_computer_intervention_heartbeat,
    resolve_intervention_decision,
    save_computer_intervention_request,
)
from issue_feedback import receive_issue_feedback, recent_issues
from recent_context import (
    RecentContextConflictError,
    RecentContextCorruptError,
    RecentContextNotFoundError,
    confirm_note,
    create_note,
    list_notes,
    relevant_notes,
    set_archived,
    set_pinned,
    update_note,
)
from next_action import (
    DEFAULT_ENV,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SETTINGS,
    generate_next_action,
    pending_active_suggestion,
    save_outcome,
    save_response,
)
from task_sync import acknowledge_mutations, effective_state, enqueue_mutation
from user_annotations import receive_annotation


HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>下一步</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
    body { margin: 0; background: #f6f7f2; color: #202124; }
    main { max-width: 760px; margin: 0 auto; padding: 18px; }
    nav { display: flex; gap: 8px; margin-bottom: 16px; }
    button, select, textarea, input { font: inherit; }
    button { border: 0; border-radius: 8px; padding: 11px 14px; background: #1f6feb; color: white; }
    button.secondary { background: #e8e8e2; color: #202124; }
    button.danger { background: #8f3a30; }
    section { display: none; }
    section.active { display: block; }
    pre, .panel, .card { white-space: pre-wrap; background: white; border: 1px solid #ddded6; border-radius: 12px; padding: 14px; }
    .card { box-shadow: 0 6px 18px rgba(42, 48, 34, .06); }
    .hero { border-left: 6px solid #1f6feb; }
    .report-card { line-height: 1.55; }
    .title-line { font-size: 20px; font-weight: 750; margin-bottom: 10px; color: #124f9c; }
    .pill { display: inline-block; border-radius: 999px; padding: 4px 9px; margin: 3px 5px 6px 0; background: #e8f1ff; color: #124f9c; font-size: 13px; font-weight: 650; }
    .label { color: #7a4a00; font-weight: 750; }
    .block { margin: 10px 0; padding: 10px 11px; border-radius: 10px; background: #f7f8f2; border-left: 4px solid #d8a31a; }
    .evidence { border-left-color: #438a55; }
    .soft { border-left-color: #8a6fd1; }
    .report-heading { margin: 12px 0 6px; color: #124f9c; font-weight: 750; }
    .report-line { margin: 4px 0; }
    textarea, select, input { width: 100%; box-sizing: border-box; margin: 8px 0 12px; border-radius: 8px; border: 1px solid #c9cabf; padding: 10px; background: white; color: #202124; }
    .row { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
    .muted { color: #60635c; font-size: 14px; }
    @media (prefers-color-scheme: dark) {
      body { background: #161714; color: #f0f0ea; }
      pre, .panel, .card, textarea, select, input { background: #22231f; color: #f0f0ea; border-color: #3a3b35; }
      button.secondary { background: #34362f; color: #f0f0ea; }
      .muted { color: #b8b9b0; }
      .title-line, .report-heading { color: #8fbfff; }
      .pill { background: #23344b; color: #b7d4ff; }
      .block { background: #2a2b25; }
      .label { color: #f2c46d; }
    }
  </style>
</head>
<body>
<main>
  <nav>
    <button class="secondary" onclick="show('next')">下一步</button>
    <button class="secondary" onclick="show('reports'); loadReports()">半小时报告</button>
    <button class="secondary" onclick="show('issues'); loadIssues()">问题反馈</button>
  </nav>
  <section id="next" class="active">
    <div class="row"><button onclick="nextAction()">生成建议</button><button class="secondary" onclick="loadActive()">查看当前建议</button></div>
    <div id="suggestion" class="card hero">点击“生成建议”后，树莓派会临时整理当前状态并调用 V4 Pro。</div>
    <div id="feedback" style="display:none">
      <div class="row">
        <button onclick="respond('accepted')">开始</button>
        <button class="secondary" onclick="showReason('alternative_requested')">换一个</button>
        <button class="danger" onclick="showReason('declined')">现在不做</button>
      </div>
      <div id="reasonBox" style="display:none" class="panel">
        <select id="reason">
          <option value="too_tired">太累</option>
          <option value="wrong_priority">优先级不对</option>
          <option value="too_difficult_or_large">太难或太大</option>
          <option value="first_step_unclear">第一步不清楚</option>
          <option value="environment_inconvenient">环境不适合</option>
          <option value="task_already_done">任务已完成</option>
          <option value="already_doing_something_else">已经在做别的事</option>
          <option value="stale_data">数据过时</option>
          <option value="other">其他</option>
        </select>
        <textarea id="detail" rows="3" placeholder="具体哪里不好？可选，但建议写一句，之后能存档复盘。"></textarea>
        <button onclick="submitReason()">提交</button>
      </div>
      <div class="row">
        <button class="secondary" onclick="outcome('completed')">完成了</button>
        <button class="secondary" onclick="outcome('still_doing')">正在做</button>
        <button class="secondary" onclick="outcome('not_started')">没开始</button>
      </div>
      <p class="muted" id="status"></p>
    </div>
  </section>
  <section id="reports">
    <div class="row"><button onclick="loadReports()">刷新最新 3 条报告</button></div>
    <div id="reportList" class="panel">加载中</div>
    <div id="reportDetail" class="card report-card"></div>
    <div id="reportFeedback" class="panel" style="display:none">
      <select id="reportCategory">
        <option value="0">AI行为判断错误</option>
        <option value="1">数据缺失或设备状态错误</option>
        <option value="2">AI输出格式或内容不合要求</option>
        <option value="3">建议不合适</option>
        <option value="4">其他问题</option>
      </select>
      <textarea id="reportMessage" rows="3" placeholder="这份半小时解读哪里不对？"></textarea>
      <button onclick="submitReportFeedback()">提交报告反馈</button>
      <p class="muted" id="reportStatus"></p>
    </div>
  </section>
  <section id="issues">
    <div class="card hero">
      <div class="title-line">🧰 系统问题反馈</div>
      <p class="muted">这里用来收集网页、AI建议、数据、通知和规则问题。之后你可以让 Codex 统一处理这些 backlog。</p>
      <select id="issueCategory">
        <option value="ai_suggestion_quality">AI建议质量</option>
        <option value="data_wrong_or_missing">数据明显不对</option>
        <option value="web_ui">网页显示/交互问题</option>
        <option value="notification">通知推送问题</option>
        <option value="rule_mismatch">规则不符合我的习惯</option>
        <option value="security_or_access">安全或访问问题</option>
        <option value="docs_or_handoff">文档或交接问题</option>
        <option value="other">其他</option>
      </select>
      <select id="issueSeverity">
        <option value="low">低：之后再看</option>
        <option value="medium" selected>中：影响体验</option>
        <option value="high">高：影响判断</option>
        <option value="blocking">阻塞：功能不能用</option>
      </select>
      <textarea id="issueMessage" rows="5" maxlength="2000" placeholder="描述你发现的问题。比如：刚才建议把一个番茄钟当成25分钟；或者某个报告数据明显不对。"></textarea>
      <div class="row">
        <button onclick="submitIssue()">提交问题</button>
        <button class="secondary" onclick="loadIssues()">查看最近问题</button>
      </div>
      <p class="muted" id="issueStatus"></p>
    </div>
    <div id="issueList" class="panel" style="margin-top:12px">最近问题会显示在这里。</div>
  </section>
</main>
<script>
let activeSuggestion = null;
let pendingResult = null;
let pendingGeneration = false;
let currentReportPath = null;
function show(id) {
  document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}
function escapeHtml(value) {
  return String(value || '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
async function api(path, body) {
  const options = body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {};
  const res = await fetch(path, options);
  const data = await res.json();
  if (!res.ok) {
    const error = new Error(data.error || res.statusText);
    error.payload = data;
    throw error;
  }
  return data;
}
function renderSuggestion(data) {
  activeSuggestion = data;
  const evidence = Array.isArray(data.evidence_points) ? data.evidence_points.slice(0, 4) : [];
  document.getElementById('suggestion').innerHTML = `
    <div class="title-line">🎯 ${escapeHtml(data.title || '当前建议')}</div>
    <div>
      <span class="pill">⏱ ${escapeHtml(data.duration_minutes || '')} 分钟</span>
      <span class="pill">${escapeHtml(data.decision_type || '')}</span>
    </div>
    <div class="block"><span class="label">第一步：</span>${escapeHtml(data.first_step || '')}</div>
    <div class="block"><span class="label">为什么现在做：</span>${escapeHtml(data.reason_short || '')}</div>
    <div class="block soft">${escapeHtml(data.persuasive_explanation || '')}</div>
    <div class="block evidence"><span class="label">依据：</span><br>${evidence.map(item => '• ' + escapeHtml(item)).join('<br>')}</div>
    <div class="block"><span class="label">如果不想做：</span>${escapeHtml(data.reduced_version || '')}</div>
  `;
  document.getElementById('feedback').style.display = data.suggestion_id ? 'block' : 'none';
}
async function nextAction(exclude) {
  document.getElementById('suggestion').textContent = '正在生成建议...';
  try {
    renderSuggestion(await api('/api/next-action', exclude ? {exclude_suggestion_id: exclude} : {}));
    pendingGeneration = false;
  } catch (error) {
    if (error.payload && error.payload.code === 'pending_outcome_required') {
      pendingGeneration = true;
      renderSuggestion(error.payload.suggestion);
      document.getElementById('status').textContent =
        '先记录上一条建议是否完成；提交后会自动继续生成这次建议。';
      return;
    }
    document.getElementById('suggestion').textContent = '生成失败：' + error.message;
  }
}
async function loadActive() { renderSuggestion(await api('/api/next-action/active')); }
async function respond(result) {
  if (!activeSuggestion) return;
  await api('/api/next-action/' + activeSuggestion.suggestion_id + '/response', {result});
  document.getElementById('status').textContent = '已记录：' + result;
}
function showReason(result) {
  pendingResult = result;
  document.getElementById('reasonBox').style.display = 'block';
}
async function submitReason() {
  if (!activeSuggestion || !pendingResult) return;
  const reason_code = document.getElementById('reason').value;
  const detail = document.getElementById('detail').value;
  await api('/api/next-action/' + activeSuggestion.suggestion_id + '/response', {result: pendingResult, reason_code, detail});
  document.getElementById('status').textContent = '已记录反馈';
  document.getElementById('reasonBox').style.display = 'none';
  if (pendingResult === 'alternative_requested') await nextAction(activeSuggestion.suggestion_id);
}
async function outcome(result) {
  if (!activeSuggestion) return;
  await api('/api/next-action/' + activeSuggestion.suggestion_id + '/outcome', {result});
  document.getElementById('status').textContent = '已记录结果：' + result;
  if (pendingGeneration) {
    pendingGeneration = false;
    await nextAction();
  }
}
async function loadReports() {
  const data = await api('/api/half-hour/reports');
  const box = document.getElementById('reportList');
  box.innerHTML = '';
  data.reports.forEach(item => {
    const b = document.createElement('button');
    b.className = 'secondary';
    b.textContent = item.label;
    b.onclick = async () => {
      currentReportPath = item.path;
      const data = await api('/api/half-hour/report?path=' + encodeURIComponent(item.path));
      renderReport(data.text || '');
      document.getElementById('reportFeedback').style.display = 'block';
    };
    box.appendChild(b);
  });
}
function renderReport(text) {
  const lines = String(text || '').split('\\n');
  const html = lines.map(line => {
    const safe = escapeHtml(line);
    if (!line.trim()) return '<div style="height:8px"></div>';
    if (/^[^：:]{2,18}[：:]$/.test(line.trim())) return `<div class="report-heading">${safe}</div>`;
    if (/^(时间核算|主要时间线|电脑与手机|不确定性|核验问题|工作娱乐混杂|结论)[：:]?/.test(line.trim())) return `<div class="report-heading">${safe}</div>`;
    return `<div class="report-line">${safe}</div>`;
  }).join('');
  document.getElementById('reportDetail').innerHTML = html;
}
async function submitReportFeedback() {
  const category = document.getElementById('reportCategory').value;
  const message = document.getElementById('reportMessage').value;
  const data = await api('/api/half-hour/feedback', {category, message});
  document.getElementById('reportStatus').textContent = '已存档：' + data.annotation_id;
  document.getElementById('reportMessage').value = '';
}
async function submitIssue() {
  const message = document.getElementById('issueMessage').value.trim();
  if (!message) {
    document.getElementById('issueStatus').textContent = '请先写一句问题描述。';
    return;
  }
  const data = await api('/api/issue-feedback', {
    category: document.getElementById('issueCategory').value,
    severity: document.getElementById('issueSeverity').value,
    message,
    page: document.querySelector('section.active')?.id || 'unknown',
    suggestion_id: activeSuggestion ? activeSuggestion.suggestion_id : '',
    report_path: currentReportPath || ''
  });
  document.getElementById('issueStatus').textContent = '已收进问题 backlog：' + data.issue_id;
  document.getElementById('issueMessage').value = '';
  await loadIssues();
}
async function loadIssues() {
  const data = await api('/api/issue-feedback/recent');
  const issues = Array.isArray(data.issues) ? data.issues : [];
  if (!issues.length) {
    document.getElementById('issueList').textContent = '还没有问题反馈。';
    return;
  }
  document.getElementById('issueList').innerHTML = issues.map(item => `
    <div class="block">
      <span class="pill">${escapeHtml(item.severity_label || item.severity)}</span>
      <span class="pill">${escapeHtml(item.category_label || item.category)}</span>
      <div class="muted">${escapeHtml(item.created_at || '')} · ${escapeHtml(item.issue_id || '')}</div>
      <div>${escapeHtml(item.message || '')}</div>
    </div>
  `).join('');
}
</script>
</body>
</html>"""


LOGIN_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Next Action Login</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f6f7f2; color: #202124; }
    form { width: min(360px, calc(100vw - 36px)); background: white; border: 1px solid #ddded6; border-radius: 12px; padding: 18px; box-shadow: 0 8px 28px rgba(0,0,0,.08); }
    input, button { width: 100%; box-sizing: border-box; font: inherit; border-radius: 8px; padding: 11px; }
    input { border: 1px solid #c9cabf; margin: 8px 0 12px; }
    button { border: 0; background: #1f6feb; color: white; }
    .muted { color: #60635c; font-size: 14px; }
    @media (prefers-color-scheme: dark) {
      body { background: #161714; color: #f0f0ea; }
      form, input { background: #22231f; color: #f0f0ea; border-color: #3a3b35; }
      .muted { color: #b8b9b0; }
    }
  </style>
</head>
<body>
  <form onsubmit="login(event)">
    <h2>下一步行动助手</h2>
    <p class="muted">公网入口需要先登录。</p>
    <input id="password" type="password" inputmode="numeric" autocomplete="current-password" placeholder="输入密码" autofocus>
    <button type="submit">登录</button>
    <p id="status" class="muted"></p>
  </form>
  <script>
    async function login(event) {
      event.preventDefault();
      const password = document.getElementById('password').value;
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({password})
      });
      if (res.ok) {
        location.href = '/next';
      } else {
        document.getElementById('status').textContent = '密码不对。';
      }
    }
  </script>
</body>
</html>"""


AUTH_COOKIE = "next_action_session"
SESSION_SECONDS = 30 * 24 * 60 * 60


class AppState:
    def __init__(self, settings_path: Path, env_file: Path):
        self.settings_path = settings_path
        self.settings = load_json(settings_path)
        self.output_root = Path(self.settings.get("output_root", DEFAULT_OUTPUT_ROOT))
        self.env_file = env_file
        self.web_password = os.environ.get("NEXT_ACTION_WEB_PASSWORD", "")
        self.web_secret = os.environ.get("NEXT_ACTION_WEB_SECRET") or self.web_password


class Handler(BaseHTTPRequestHandler):
    server_version = "ActivityAdvisorWeb/1.0"

    def _state(self) -> AppState:
        return self.server.app_state  # type: ignore[attr-defined]

    def _json(self, status: int, data: Any) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def _body(self) -> dict[str, Any]:
        length = min(int(self.headers.get("Content-Length", "0") or 0), 8192)
        if not length:
            return {}
        try:
            value = json.loads(self.rfile.read(length).decode("utf-8"))
            return value if isinstance(value, dict) else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}

    def _auth_enabled(self) -> bool:
        state = self._state()
        return bool(state.web_password and state.web_secret)

    def _cookie_value(self) -> str | None:
        cookie_header = self.headers.get("Cookie", "")
        for item in cookie_header.split(";"):
            if "=" not in item:
                continue
            key, value = item.strip().split("=", 1)
            if key == AUTH_COOKIE:
                return value
        return None

    def _sign(self, payload: str) -> str:
        secret = self._state().web_secret.encode("utf-8")
        return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def _authenticated(self) -> bool:
        if not self._auth_enabled():
            return True
        value = self._cookie_value()
        if not value:
            return False
        parts = value.split(":")
        if len(parts) != 3:
            return False
        expires, nonce, signature = parts
        try:
            if int(expires) < int(time.time()):
                return False
        except ValueError:
            return False
        payload = f"{expires}:{nonce}"
        return hmac.compare_digest(self._sign(payload), signature)

    def _set_session_cookie(self) -> None:
        expires = str(int(time.time()) + SESSION_SECONDS)
        nonce = secrets.token_urlsafe(18)
        payload = f"{expires}:{nonce}"
        value = f"{payload}:{self._sign(payload)}"
        self.send_header(
            "Set-Cookie",
            f"{AUTH_COOKIE}={value}; Path=/; Max-Age={SESSION_SECONDS}; HttpOnly; Secure; SameSite=Lax",
        )

    def _require_auth(self, parsed_path: str) -> bool:
        # Focus Garden is a fixed same-Pi proxy.  It may reach only this small
        # intervention surface over loopback; browser/Tailnet callers still
        # never receive an unauthenticated Advisor API.
        internal_bridge = (
            parsed_path.startswith("/api/interventions/")
            and self.client_address[0] in {"127.0.0.1", "::1"}
            and self.headers.get("X-Focus-Garden-Bridge") == "1"
        )
        task_sync_bridge = (
            parsed_path.startswith("/api/task-sync/")
            and self.client_address[0] in {"127.0.0.1", "::1"}
            and self.headers.get("X-Obsidian-Task-Sync") == "1"
        )
        focus_garden_task_bridge = (
            parsed_path.startswith("/api/task-sync/")
            and self.client_address[0] in {"127.0.0.1", "::1"}
            and self.headers.get("X-Focus-Garden-Bridge") == "1"
        )
        recent_context_bridge = (
            (
                parsed_path == "/api/recent-context"
                or parsed_path.startswith("/api/recent-context/")
            )
            and self.client_address[0] in {"127.0.0.1", "::1"}
            and self.headers.get("X-Focus-Garden-Bridge") == "1"
        )
        if internal_bridge or task_sync_bridge or focus_garden_task_bridge or recent_context_bridge:
            return True
        if parsed_path == "/api/recent-context" or parsed_path.startswith("/api/recent-context/"):
            # Recent-context is only reachable through the fixed Focus Garden
            # proxy (loopback AND bridge header); global auth must not bypass it.
            self._error(HTTPStatus.UNAUTHORIZED, "login required")
            return False
        if self._authenticated():
            return True
        if parsed_path.startswith("/api/"):
            self._error(HTTPStatus.UNAUTHORIZED, "login required")
        else:
            self._html(HTTPStatus.UNAUTHORIZED, LOGIN_HTML)
        return False

    def _login(self) -> None:
        body = self._body()
        password = str(body.get("password", ""))
        expected = self._state().web_password
        if not expected or not hmac.compare_digest(password, expected):
            self._error(HTTPStatus.UNAUTHORIZED, "invalid password")
            return
        response = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_session_cookie()
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/login":
            self._html(HTTPStatus.OK, LOGIN_HTML)
            return
        if not self._require_auth(parsed.path):
            return
        if parsed.path in {"/", "/next"}:
            body = HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/next-action/active":
            active = _read_json(self._state().output_root / "next_action" / "active.json")
            if not active:
                self._error(HTTPStatus.NOT_FOUND, "no active suggestion")
            else:
                if _suggestion_is_stale(active, self._state()):
                    active["stale"] = True
                    active["stale_reason"] = "task_revision_changed"
                self._json(HTTPStatus.OK, active)
            return
        if parsed.path == "/api/task-sync/state":
            self._json(HTTPStatus.OK, _task_sync_state(self._state()))
            return
        if parsed.path == "/api/recent-context":
            query = parse_qs(parsed.query)
            include_archived = query.get("include_archived", ["0"])[0] in {"1", "true"}
            try:
                self._json(
                    HTTPStatus.OK,
                    list_notes(
                        self._state().output_root,
                        include_archived=include_archived,
                        settings=self._state().settings,
                        timezone_name=self._state().settings.get("timezone", "Asia/Shanghai"),
                    ),
                )
            except RecentContextCorruptError:
                self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "recent_context_state_corrupt"})
            return
        if parsed.path == "/api/recent-context/relevant":
            try:
                self._json(
                    HTTPStatus.OK,
                    relevant_notes(
                        self._state().output_root,
                        settings=self._state().settings,
                        timezone_name=self._state().settings.get("timezone", "Asia/Shanghai"),
                    ),
                )
            except RecentContextCorruptError:
                self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "recent_context_state_corrupt"})
            return
        if parsed.path == "/api/half-hour/reports":
            self._json(HTTPStatus.OK, {"reports": _report_index(self._state().output_root)})
            return
        if parsed.path == "/api/issue-feedback/recent":
            self._json(
                HTTPStatus.OK,
                {"issues": recent_issues(self._state().output_root, limit=20)},
            )
            return
        if parsed.path == "/api/computer-interventions/pending":
            query = parse_qs(parsed.query)
            computer_id = query.get("computer_id", ["windows-main"])[0]
            pending = latest_pending_request(
                self._state().output_root,
                computer_id,
                datetime.now().astimezone(),
            )
            self._json(HTTPStatus.OK, {"request": pending})
            return
        if parsed.path == "/api/interventions/pending":
            query = parse_qs(parsed.query)
            device_id = query.get("device_id", [""])[0]
            if device_id != "android-main":
                self._error(HTTPStatus.BAD_REQUEST, "unknown bridge device")
                return
            pending = latest_pending_phone_request(
                self._state().output_root,
                device_id,
                datetime.now().astimezone(),
            )
            self._json(HTTPStatus.OK, {"request": pending})
            return
        if parsed.path == "/api/half-hour/report":
            query = parse_qs(parsed.query)
            try:
                text = _read_report_text(
                    self._state().output_root, query.get("path", [""])[0]
                )
            except Exception as error:
                self._error(HTTPStatus.BAD_REQUEST, f"{type(error).__name__}: {error}")
                return
            self._json(HTTPStatus.OK, {"text": text})
            return
        self._error(HTTPStatus.NOT_FOUND, "not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/login":
            self._login()
            return
        if not self._require_auth(parsed.path):
            return
        state = self._state()
        try:
            if parsed.path == "/api/next-action":
                body = self._body()
                pending = pending_active_suggestion(state.output_root)
                if pending and _suggestion_is_stale(pending, state):
                    pending = None
                if pending:
                    self._json(
                        HTTPStatus.CONFLICT,
                        {
                            "error": "previous suggestion outcome required",
                            "code": "pending_outcome_required",
                            "suggestion": pending,
                        },
                    )
                    return
                result = generate_next_action(
                    state.settings,
                    state.output_root,
                    env_file=state.env_file,
                    exclude_suggestion_id=body.get("exclude_suggestion_id"),
                )
                self._json(HTTPStatus.OK, result)
                return
            if parsed.path == "/api/task-sync/mutations":
                self._json(
                    HTTPStatus.CREATED,
                    enqueue_mutation(
                        _context_path(state),
                        state.output_root,
                        self._body(),
                        timezone_name=state.settings.get("timezone", "Asia/Shanghai"),
                    ),
                )
                return
            if parsed.path == "/api/task-sync/ack":
                self._json(
                    HTTPStatus.OK,
                    acknowledge_mutations(
                        _context_path(state),
                        state.output_root,
                        self._body(),
                        timezone_name=state.settings.get("timezone", "Asia/Shanghai"),
                    ),
                )
                return
            if parsed.path == "/api/recent-context":
                body = self._body()
                self._json(
                    HTTPStatus.CREATED,
                    create_note(
                        state.output_root,
                        str(body.get("content", "")),
                        str(body.get("impact_text", "")),
                        body.get("expected_revision"),
                        settings=state.settings,
                        timezone_name=state.settings.get("timezone", "Asia/Shanghai"),
                    ),
                )
                return
            recent_match = re.fullmatch(
                r"/api/recent-context/([A-Za-z0-9_-]+)/(update|archive|unarchive|pin|unpin|confirm)",
                parsed.path,
            )
            if recent_match:
                note_id, action = recent_match.group(1), recent_match.group(2)
                body = self._body()
                tz = state.settings.get("timezone", "Asia/Shanghai")
                if action == "update":
                    result = update_note(
                        state.output_root,
                        note_id,
                        body.get("expected_revision"),
                        settings=state.settings,
                        content=body.get("content"),
                        impact_text=body.get("impact_text"),
                        pinned=body.get("pinned"),
                        timezone_name=tz,
                    )
                elif action == "archive":
                    result = set_archived(
                        state.output_root, note_id, body.get("expected_revision"), True, timezone_name=tz
                    )
                elif action == "unarchive":
                    result = set_archived(
                        state.output_root, note_id, body.get("expected_revision"), False, timezone_name=tz
                    )
                elif action == "pin":
                    result = set_pinned(
                        state.output_root, note_id, body.get("expected_revision"), True, timezone_name=tz
                    )
                elif action == "unpin":
                    result = set_pinned(
                        state.output_root, note_id, body.get("expected_revision"), False, timezone_name=tz
                    )
                else:
                    result = confirm_note(
                        state.output_root, note_id, body.get("expected_revision"), timezone_name=tz
                    )
                self._json(HTTPStatus.OK, result)
                return
            if parsed.path == "/api/half-hour/feedback":
                body = self._body()
                self._json(
                    HTTPStatus.OK,
                    receive_annotation(
                        body.get("category", 4),
                        body.get("message", ""),
                        project_root=Path(__file__).resolve().parents[1],
                    ),
                )
                return
            if parsed.path == "/api/issue-feedback":
                self._json(
                    HTTPStatus.OK,
                    receive_issue_feedback(
                        self._body(),
                        output_root=state.output_root,
                        user_agent=self.headers.get("User-Agent", ""),
                    ),
                )
                return
            if parsed.path in {
                "/api/computer-interventions/ack",
                "/api/computer-interventions/response",
            }:
                self._json(
                    HTTPStatus.OK,
                    receive_computer_intervention_event(
                        state.output_root,
                        self._body(),
                        user_agent=self.headers.get("User-Agent", ""),
                    ),
                )
                return
            if parsed.path == "/api/computer-interventions/heartbeat":
                self._json(
                    HTTPStatus.OK,
                    receive_computer_intervention_heartbeat(
                        state.output_root,
                        self._body(),
                        user_agent=self.headers.get("User-Agent", ""),
                    ),
                )
                return
            if parsed.path == "/api/interventions/manual-focus":
                body = self._body()
                duration = int(body["duration"])
                targets = body.get("targets", ["windows", "phone"])
                if not isinstance(targets, list):
                    raise ValueError("targets must be a list")
                request = build_manual_focus_request(
                    state.settings, duration, [str(item) for item in targets],
                    requested_blocks=[str(item) for item in body.get("blocks", [])] or None,
                )
                path = save_computer_intervention_request(state.output_root, request)
                self._json(
                    HTTPStatus.CREATED,
                    {"request": request, "path": str(path.relative_to(state.output_root))},
                )
                return
            if parsed.path == "/api/interventions/manual-focus/release":
                body = self._body()
                blocks = body.get("blocks", [])
                if not isinstance(blocks, list):
                    raise ValueError("blocks must be a list")
                request = build_manual_focus_release_request(
                    state.settings,
                    [str(item) for item in blocks],
                    lease_id=(str(body.get("lease_id", "")).strip() or None),
                    session_id=(str(body.get("session_id", "")).strip() or None),
                )
                path = save_computer_intervention_request(state.output_root, request)
                self._json(HTTPStatus.CREATED, {"request": request, "path": str(path.relative_to(state.output_root))})
                return
            if parsed.path == "/api/interventions/decision":
                body = self._body()
                self._json(
                    HTTPStatus.OK,
                    resolve_intervention_decision(
                        state.output_root,
                        str(body["request_id"]),
                        str(body["decision"]),
                        str(body.get("device_id", "unknown")),
                    ),
                )
                return
            if parsed.path == "/api/interventions/event":
                body = self._body()
                if str(body.get("computer_id", "")) != "android-main":
                    raise ValueError("unknown bridge device")
                self._json(
                    HTTPStatus.OK,
                    receive_computer_intervention_event(
                        state.output_root,
                        body,
                        user_agent=self.headers.get("User-Agent", ""),
                    ),
                )
                return
            match = _match_next_action(parsed.path, "response")
            if match:
                body = self._body()
                self._json(
                    HTTPStatus.OK,
                    save_response(
                        state.output_root,
                        match,
                        str(body.get("result", "")),
                        reason_code=str(body.get("reason_code", "other")),
                        detail=str(body.get("detail", "")),
                    ),
                )
                return
            match = _match_next_action(parsed.path, "outcome")
            if match:
                body = self._body()
                self._json(
                    HTTPStatus.OK,
                    save_outcome(
                        state.output_root,
                        match,
                        str(body.get("result", "")),
                        detail=str(body.get("detail", "")),
                    ),
                )
                return
        except RecentContextConflictError as error:
            self._json(
                HTTPStatus.CONFLICT,
                {
                    "error": "revision conflict",
                    "code": "revision_conflict",
                    "current_revision": error.current_revision,
                },
            )
            return
        except RecentContextCorruptError:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "recent_context_state_corrupt"})
            return
        except RecentContextNotFoundError:
            self._json(HTTPStatus.NOT_FOUND, {"error": "note not found"})
            return
        except Exception as error:
            self._error(HTTPStatus.BAD_REQUEST, f"{type(error).__name__}: {error}")
            return
        self._error(HTTPStatus.NOT_FOUND, "not found")

    def log_message(self, format: str, *args: Any) -> None:
        return


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _context_path(state: AppState) -> Path:
    return Path(
        state.settings.get(
            "obsidian_context_path",
            "/home/conrad/workspace/behavior-context-sync/context_snapshot.json",
        )
    )


def _task_sync_state(state: AppState) -> dict[str, Any]:
    return effective_state(
        _context_path(state),
        state.output_root,
        timezone_name=state.settings.get("timezone", "Asia/Shanghai"),
    )


def _suggestion_is_stale(suggestion: dict[str, Any], state: AppState) -> bool:
    recorded_revision = suggestion.get("task_revision")
    if not isinstance(recorded_revision, int):
        return False
    return recorded_revision != _task_sync_state(state).get("revision")


def _match_next_action(path: str, suffix: str) -> str | None:
    prefix = "/api/next-action/"
    marker = "/" + suffix
    if path.startswith(prefix) and path.endswith(marker):
        return path[len(prefix) : -len(marker)]
    return None


def _report_index(output_root: Path, limit: int = 3) -> list[dict[str, str]]:
    reports = sorted((output_root / "ai_reports").glob("*/*.md"))[-limit:]
    if not reports:
        reports = sorted((output_root / "ai_reports").glob("*/*.json"))[-limit:]
    result = []
    for path in reversed(reports):
        result.append(
            {
                "label": f"{path.parent.name} {path.stem}",
                "path": str(path.relative_to(output_root)),
            }
        )
    return result


def _read_report_text(output_root: Path, relative_path: str) -> str:
    allowed_paths = {item["path"] for item in _report_index(output_root)}
    if relative_path not in allowed_paths:
        raise ValueError("report path is not in the latest allowed reports")
    target = (output_root / relative_path).resolve()
    allowed = (output_root / "ai_reports").resolve()
    if allowed not in target.parents or not target.exists():
        raise ValueError("report path is not allowed")
    return _plain_report_text(target.read_text(encoding="utf-8"))[:20000]


def _plain_report_text(markdown: str) -> str:
    """Convert archived Markdown reports into a mobile-friendly plain display text."""
    lines: list[str] = []
    in_code_block = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            lines.append(line)
            continue
        if not line:
            if lines and lines[-1]:
                lines.append("")
            continue
        if re.fullmatch(r"-{3,}", line):
            continue
        heading = re.match(r"^(#{1,6})\s*(.+)$", line)
        if heading:
            text = _strip_inline_markdown(heading.group(2)).strip()
            lines.append(("🧾 " if len(heading.group(1)) == 1 else "") + text + "：")
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [
                _strip_inline_markdown(cell.strip())
                for cell in line.strip("|").split("|")
            ]
            if all(not cell or re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
                continue
            if cells:
                lines.append(" / ".join(cell for cell in cells if cell))
            continue
        line = re.sub(r"^[-*]\s+", "• ", line)
        line = re.sub(r"^\d+[.)]\s+", lambda match: match.group(0).replace(".", "、").replace(")", "、"), line)
        lines.append(_strip_inline_markdown(line))
    return "\n".join(lines).strip()


def _strip_inline_markdown(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("*", "")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the private next-action web UI.")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    args = parser.parse_args()
    app_state = AppState(args.settings, args.env_file)
    next_action = app_state.settings.get("next_action", {})
    host = str(next_action.get("web_host", "127.0.0.1"))
    port = int(next_action.get("web_port", 8767))
    server = ThreadingHTTPServer((host, port), Handler)
    server.app_state = app_state  # type: ignore[attr-defined]
    print(f"Serving next-action web UI on http://{host}:{port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
