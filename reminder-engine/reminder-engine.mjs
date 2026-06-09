#!/usr/bin/env node

/**
 * Quartz Reminder Engine - 系统级任务提醒引擎
 * 
 * 监视 Obsidian Tasks 格式的 Markdown 文件，检测到期任务，
 * 并通过 Windows 原生通知发送提醒。
 * 
 * 用法:
 *   node reminder-engine.mjs           # 后台运行
 *   node reminder-engine.mjs --verbose  # 详细日志
 *   node reminder-engine.mjs --once     # 仅检查一次，不持续监听
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

// ── 配置 ──────────────────────────────────────────────────────────
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONTENT_DIR = path.resolve(__dirname, '..', 'content');
const CHECK_INTERVAL_MS = 60000;         // 每分钟检查一次
const NOTIFICATION_TIMEOUT_MS = 10000;   // 通知显示时长

const FREQUENT_RECHECK_MS = 300000;      // 5分钟静默期，避免重复通知
const TASK_FILE_PATTERN = /\.md$/i;

// ── 解析命令行 ────────────────────────────────────────────────────
const args = process.argv.slice(2);
const VERBOSE = args.includes('--verbose') || args.includes('-v');
const RUN_ONCE = args.includes('--once') || args.includes('-1');

function log(...msg) {
  const ts = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  console.log(`[${ts}]`, ...msg);
}

function verbose(...msg) {
  if (VERBOSE) log(...msg);
}

// ── 通知去重 ──────────────────────────────────────────────────────
const notifiedTasks = new Map(); // taskId -> lastNotifiedTimestamp

function getTaskId(taskText, dueDate) {
  // 用任务的前 40 个字符 + 截止日期作为唯一标识
  return `${taskText.slice(0, 40)}::${dueDate}`;
}

function shouldNotify(taskId) {
  const last = notifiedTasks.get(taskId);
  const now = Date.now();
  if (!last || (now - last) > FREQUENT_RECHECK_MS) {
    notifiedTasks.set(taskId, now);
    return true;
  }
  return false;
}

// ── Windows 原生通知 ──────────────────────────────────────────────
function sendWindowsNotification(title, body, urgency = 'info') {
  return new Promise((resolve) => {
    // 使用 PowerShell 发送 Windows 原生 Toast 通知
    const psScript = `
      [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
      $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
      $textNodes = $template.GetElementsByTagName("text")
      $textNodes.Item(0).AppendChild($template.CreateTextNode('${title.replace(/'/g, "''")}')) > $null
      $textNodes.Item(1).AppendChild($template.CreateTextNode('${body.replace(/'/g, "''")}')) > $null
      $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
      [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier().Show($toast)
    `;

    const proc = spawn('powershell', [
      '-NoProfile', '-NonInteractive',
      '-Command', psScript
    ], { timeout: NOTIFICATION_TIMEOUT_MS });

    let stderr = '';
    proc.stderr.on('data', (d) => { stderr += d.toString(); });

    proc.on('close', (code) => {
      if (code !== 0 && stderr.includes('not registered')) {
        // PowerShell Toast API 不可用，回退到简单的 msg 命令
        fallbackNotification(title, body);
      }
      resolve();
    });
    proc.on('error', () => {
      fallbackNotification(title, body);
      resolve();
    });
  });
}

function fallbackNotification(title, body) {
  // 使用 Windows msg 命令作为后备方案
  // 使用 PowerShell balloon tip (Win7+ 兼容)
  const psBalloon = `
    Add-Type -AssemblyName System.Windows.Forms
    $notify = New-Object System.Windows.Forms.NotifyIcon
    $notify.Icon = [System.Drawing.SystemIcons]::Information
    $notify.BalloonTipIcon = 'Info'
    $notify.BalloonTipTitle = '${title.replace(/'/g, "''")}'
    $notify.BalloonTipText = '${body.replace(/'/g, "''")}'
    $notify.Visible = $true
    $notify.ShowBalloonTip(${NOTIFICATION_TIMEOUT_MS})
    Start-Sleep -Seconds 5
    $notify.Dispose()
  `;

  const proc = spawn('powershell', [
    '-NoProfile', '-NonInteractive',
    '-Command', psBalloon
  ], { timeout: 10000, stdio: 'ignore' });
  proc.on('error', () => {});
}

// ── 任务文件解析 ──────────────────────────────────────────────────

/**
 * 解析一个 Markdown 文件，提取其中的 Obsidian Tasks
 */
function parseTaskFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    const tasks = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      // 匹配 - [ ] #task 格式
      if (/^\s*[-*]\s+\[[\sxX]\]\s+#task\b/.test(line)) {
        const task = extractTaskInfo(line, filePath, i + 1);
        if (task) tasks.push(task);
      }
    }
    return tasks;
  } catch (err) {
    verbose(`  读取文件失败 ${filePath}: ${err.message}`);
    return [];
  }
}

/**
 * 从一行任务文本中提取结构化信息
 */
function extractTaskInfo(line, filePath, lineNumber) {
  const done = /^\s*[-*]\s+\[[xX]\]/.test(line);
  const taskText = line
    .replace(/^\s*[-*]\s+\[[\sxX]\]\s+#task\s*/, '')
    .trim();

  // 提取日期
  const dueMatch = taskText.match(/📅\W*(\d{4}-\d{2}-\d{2})/);
  const scheduledMatch = taskText.match(/⏳\W*(\d{4}-\d{2}-\d{2})/);
  const startMatch = taskText.match(/🛫\W*(\d{4}-\d{2}-\d{2})/);
  const completionMatch = taskText.match(/✅\W*(\d{4}-\d{2}-\d{2})/);

  // 提取优先级
  let priority = 'none';
  if (taskText.includes('⏫')) priority = 'high';
  else if (taskText.includes('🔺') || taskText.includes('🔼')) priority = 'medium';
  else if (taskText.includes('🔽')) priority = 'low';

  // 提取番茄钟
  const pomodoroMatch = taskText.match(/\[🍅::\s*(\d+)\/(\d+)\]/);

  // 提取标签（#xxx），但要排除 #task
  const tags = (taskText.match(/#[^\s#]+/g) || []).filter(t => t !== '#task');

  // 纯净任务名称（去掉所有标签、日期、优先级 emoji、番茄钟等）
  const cleanName = taskText
    .replace(/📅\W*\d{4}-\d{2}-\d{2}/g, '')
    .replace(/⏳\W*\d{4}-\d{2}-\d{2}/g, '')
    .replace(/🛫\W*\d{4}-\d{2}-\d{2}/g, '')
    .replace(/✅\W*\d{4}-\d{2}-\d{2}/g, '')
    .replace(/[⏫🔺🔼🔽]/g, '')
    .replace(/\[🍅::\s*\d*\/?\d*\]/g, '')
    .replace(/#[^\s#]+/g, '')
    .replace(/[🗓📅⏳🛫✅🔁]/g, '')
    .replace(/\[{2}|]{2}/g, '') // 去掉 [[ ]]
    .replace(/\s+/g, ' ')
    .trim();

  // 计算相对路径（用于显示）
  const relativePath = path.relative(CONTENT_DIR, filePath);

  return {
    text: cleanName || taskText.slice(0, 60),
    raw: taskText,
    done,
    due: dueMatch ? dueMatch[1] : null,
    scheduled: scheduledMatch ? scheduledMatch[1] : null,
    start: startMatch ? startMatch[1] : null,
    completed: completionMatch ? completionMatch[1] : null,
    priority,
    tags,
    pomodoro: pomodoroMatch ? { done: parseInt(pomodoroMatch[1]), total: parseInt(pomodoroMatch[2]) } : null,
    file: relativePath,
    line: lineNumber,
    path: filePath,
  };
}

/**
 * 递归扫描目录下所有 Markdown 文件
 */
function* walkContentDir(dir) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        // 跳过隐藏目录和 node_modules
        if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
          yield* walkContentDir(fullPath);
        }
      } else if (entry.isFile() && TASK_FILE_PATTERN.test(entry.name)) {
        yield fullPath;
      }
    }
  } catch (err) {
    verbose(`  跳过目录 ${dir}: ${err.message}`);
  }
}

// ── 核心提醒逻辑 ──────────────────────────────────────────────────

const today = () => {
  const d = new Date();
  // 使用北京时间
  const bj = new Date(d.toLocaleString('en-US', { timeZone: 'Asia/Shanghai' }));
  return bj.toISOString().split('T')[0];
};

function getDueAndOverdueTasks() {
  const todayStr = today();
  const dueToday = [];
  const overdue = [];
  const scheduledToday = [];
  let totalTaskCount = 0;

  for (const filePath of walkContentDir(CONTENT_DIR)) {
    const tasks = parseTaskFile(filePath);
    for (const task of tasks) {
      if (task.done) continue; // 跳过已完成任务
      totalTaskCount++;

      if (task.due === todayStr) {
        dueToday.push(task);
      } else if (task.due && task.due < todayStr) {
        overdue.push(task);
      }

      if (task.scheduled === todayStr) {
        scheduledToday.push(task);
      }
    }
  }

  return { dueToday, overdue, scheduledToday, totalTaskCount };
}

async function checkAndNotify() {
  verbose('检查任务文件...');
  const { dueToday, overdue, scheduledToday, totalTaskCount } = getDueAndOverdueTasks();

  verbose(`  共发现 ${totalTaskCount} 个未完成任务`);
  verbose(`  今日截止: ${dueToday.length} | 已逾期: ${overdue.length} | 计划今日: ${scheduledToday.length}`);

  // ── 发送今日截止通知 ──
  if (dueToday.length > 0) {
    const title = `📅 ${dueToday.length} 个任务今日截止`;
    const lines = dueToday.map(t => {
      const priorityEmoji = t.priority === 'high' ? '⏫' : t.priority === 'medium' ? '🔺' : '';
      return `  ${priorityEmoji} ${t.text} (${t.file})`;
    });
    const body = lines.join('\n');

    // 按优先级排序，高优先级先通知
    const highPriority = dueToday.filter(t => t.priority === 'high');
    const normalPriority = dueToday.filter(t => t.priority !== 'high');

    // 高优先级任务每个单独通知
    for (const task of highPriority) {
      const taskId = getTaskId(task.text, task.due);
      if (shouldNotify(taskId)) {
        const noteTitle = `⏫ 高优先级任务今日截止!`;
        const noteBody = `${task.text}\n文件: ${task.file}:${task.line}`;
        await sendWindowsNotification(noteTitle, noteBody);
        log(`🔔 提醒: ${noteTitle} - ${task.text}`);
      }
    }

    // 普通优先级合并通知
    if (normalPriority.length > 0) {
      const groupId = getTaskId(`group-due-${today()}`, today());
      if (shouldNotify(groupId)) {
        const groupText = normalPriority.map(t => `• ${t.text}`).join('\n');
        await sendWindowsNotification(title, groupText);
        log(`🔔 提醒: ${title}`);
      }
    }
  }

  // ── 发送逾期通知 ──
  if (overdue.length > 0) {
    const title = `⚠️ ${overdue.length} 个任务已逾期`;
    const lines = overdue.map(t => `• ${t.text} (截止: ${t.due})`);
    const body = lines.join('\n');

    const groupId = getTaskId(`group-overdue-${today()}`, today());
    if (shouldNotify(groupId)) {
      await sendWindowsNotification(title, body, 'warning');
      log(`🔔 提醒: ${title}`);
    }
  }

  // ── 发送计划提醒 ──
  if (scheduledToday.length > 0 && dueToday.length === 0) {
    // 只有当没有截止任务时才通知计划任务（减少干扰）
    const title = `⏳ 今日计划: ${scheduledToday.length} 个任务`;
    const lines = scheduledToday.slice(0, 3).map(t => `• ${t.text}`);
    const body = lines.join('\n') + (scheduledToday.length > 3 ? `\n...还有 ${scheduledToday.length - 3} 个` : '');

    const groupId = getTaskId(`group-scheduled-${today()}`, today());
    if (shouldNotify(groupId)) {
      await sendWindowsNotification(title, body);
      log(`🔔 提醒: ${title}`);
    }
  }

  return { dueToday: dueToday.length, overdue: overdue.length, scheduledToday: scheduledToday.length, totalTaskCount };
}

// ── 文件监听 ──────────────────────────────────────────────────────

async function watchForChanges() {
  let watchAvailable = false;

  try {
    const chokidar = await import('chokidar');
    watchAvailable = true;

    const watcher = chokidar.watch(CONTENT_DIR, {
      ignored: /(^|[\/\\])\../,  // 忽略隐藏文件
      persistent: true,
      ignoreInitial: true,
      awaitWriteFinish: { stabilityThreshold: 500 },
    });

    const onChange = async (filePath) => {
      // 去抖：短时间内多次触发只执行一次
      clearTimeout(onChange._timer);
      onChange._timer = setTimeout(async () => {
        if (TASK_FILE_PATTERN.test(filePath)) {
          verbose(`文件变更: ${filePath}`);
          await checkAndNotify();
        }
      }, 1000);
    };

    watcher.on('add', onChange);
    watcher.on('change', onChange);

    log('📁 文件监听已启动 (chokidar)');
    return watcher;
  } catch (err) {
    verbose('chokidar 不可用，使用轮询模式');
    return null;
  }
}

// ── 主函数 ────────────────────────────────────────────────────────

async function main() {
  console.log('');
  console.log('╔═══════════════════════════════════════════╗');
  console.log('║    Quartz Reminder Engine - 任务提醒引擎   ║');
  console.log('╚═══════════════════════════════════════════╝');
  console.log(`  工作目录: ${CONTENT_DIR}`);
  console.log(`  检查间隔: ${CHECK_INTERVAL_MS / 1000}s`);
  console.log(`  模式: ${RUN_ONCE ? '单次检查' : '持续监听'}`);
  console.log('');

  // 首次立即检查
  const result = await checkAndNotify();

  if (RUN_ONCE) {
    console.log(`\n检查完成: ${result.dueToday} 个到期, ${result.overdue} 个逾期, ${result.scheduledToday} 个计划`);
    process.exit(0);
  }

  // 启动文件监听
  const watcher = await watchForChanges();

  // 定时检查（防止监听漏掉文件）
  const intervalId = setInterval(async () => {
    verbose('定时检查...');
    await checkAndNotify();
  }, CHECK_INTERVAL_MS);

  console.log(`\n⏰ 提醒引擎运行中 (PID: ${process.pid})`);
  console.log('   按 Ctrl+C 停止\n');

  // 优雅退出
  const shutdown = () => {
    console.log('\n正在停止提醒引擎...');
    clearInterval(intervalId);
    if (watcher) watcher.close();
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((err) => {
  console.error('❌ 提醒引擎错误:', err);
  process.exit(1);
});