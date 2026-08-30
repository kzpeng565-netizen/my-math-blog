let csrfToken = null;
let refreshTimer = null;

const phaseLabels = {
  starting: '启动中',
  scanning: '扫描中',
  running: '运行中',
  login_required: '需要登录',
  login_window: '等待登录',
  booking: '预约处理中',
  error: '异常退避',
  stopped: '已停止',
};

function $(id) {
  return document.getElementById(id);
}

function formatTime(value) {
  if (!value) return '—';
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(new Date(value));
}

function createElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

async function post(path) {
  const response = await fetch(path, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken,
    },
    body: '{}',
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || '操作失败');
  }
  return payload;
}

function actionButton(label, className, handler, disabled = false) {
  const button = createElement('button', `button ${className}`, label);
  button.disabled = disabled;
  button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      await handler();
    } catch (error) {
      window.alert(error.message);
    } finally {
      await refresh();
    }
  });
  return button;
}

function lectureCard(lecture, excluded = false) {
  const card = createElement('article', `lecture-card${excluded ? ' excluded' : ''}`);
  const heading = createElement('div', 'lecture-heading');
  heading.append(createElement('h3', '', lecture.title));
  heading.append(createElement('span', 'lecture-id', `#${lecture.lectureId}`));
  card.append(heading);

  const details = createElement('dl', 'lecture-details');
  for (const [label, value] of [
    ['时间', lecture.timeText],
    ['地点', lecture.location],
    ['对象', lecture.audience],
  ]) {
    details.append(createElement('dt', '', label), createElement('dd', '', value || '—'));
  }
  card.append(details);

  if (lecture.exclusionReason) {
    card.append(createElement('p', 'reason', lecture.exclusionReason));
  }
  if (lecture.lastResult) {
    card.append(createElement('p', `result ${lecture.lastResult.success ? 'success' : 'warning'}`, lecture.lastResult.message));
  }

  const actions = createElement('div', 'actions');
  if (!excluded) {
    actions.append(actionButton(
      lecture.canBook ? '确认预约' : '当前不可重试',
      'primary',
      async () => {
        const payload = await post(`/api/candidates/${lecture.lectureId}/book`);
        window.alert(payload.result.message);
      },
      !lecture.canBook,
    ));
    actions.append(actionButton('忽略本场', 'secondary', () => post(`/api/candidates/${lecture.lectureId}/ignore`)));
  } else if (lecture.exclusionReasonCode === 'ignored') {
    actions.append(actionButton('恢复监控', 'secondary', () => post(`/api/candidates/${lecture.lectureId}/unignore`)));
  }
  const detail = createElement('a', 'button link-button', '打开官网详情');
  detail.href = lecture.detailUrl;
  detail.target = '_blank';
  detail.rel = 'noopener noreferrer';
  actions.append(detail);
  card.append(actions);
  return card;
}

function renderList(container, lectures, excluded = false) {
  container.replaceChildren();
  if (lectures.length === 0) {
    container.append(createElement('p', 'empty', excluded ? '当前没有被规则排除的可预约讲座。' : '当前没有符合条件的可预约讲座。'));
    return;
  }
  for (const lecture of lectures) {
    container.append(lectureCard(lecture, excluded));
  }
}

async function refresh() {
  clearTimeout(refreshTimer);
  try {
    const response = await fetch('/api/status', { cache: 'no-store', credentials: 'same-origin' });
    if (!response.ok) throw new Error('无法读取监控器状态');
    const status = await response.json();
    csrfToken = status.csrfToken;
    $('phase').textContent = phaseLabels[status.phase] || status.phase;
    $('phase').dataset.phase = status.phase;
    $('message').textContent = status.message;
    $('error').textContent = status.lastError || '';
    $('last-scan').textContent = formatTime(status.lastScanAt);
    $('next-scan').textContent = formatTime(status.nextScanAt);
    $('pages-scanned').textContent = String(status.pagesScanned || 0);
    $('candidate-count').textContent = String(status.candidates.length);
    $('excluded-count').textContent = String(status.excluded.length);
    const showLogin = status.phase === 'login_required' || status.phase === 'login_window';
    $('login-panel').classList.toggle('hidden', !showLogin);
    $('open-login').disabled = status.loginWindowOpen;
    $('open-login').textContent = status.loginWindowOpen ? '登录窗口已打开' : '打开登录窗口';
    renderList($('candidates'), status.candidates, false);
    renderList($('excluded'), status.excluded, true);
  } catch (error) {
    $('phase').textContent = '连接失败';
    $('message').textContent = error.message;
  } finally {
    refreshTimer = setTimeout(refresh, 5_000);
  }
}

$('open-login').addEventListener('click', async () => {
  $('open-login').disabled = true;
  try {
    await post('/api/login/open');
  } catch (error) {
    window.alert(error.message);
  } finally {
    await refresh();
  }
});

void refresh();
