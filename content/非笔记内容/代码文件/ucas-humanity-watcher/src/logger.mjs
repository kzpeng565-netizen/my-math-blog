import { appendFile, mkdir, readdir, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { shanghaiDateKey } from './time.mjs';

const SENSITIVE_KEY = /(password|passwd|pwd|cookie|token|csrf|captcha|certcode|session|username|account)/i;

function stripQuery(value) {
  if (typeof value !== 'string') {
    return value;
  }
  try {
    const parsed = new URL(value);
    parsed.search = '';
    parsed.hash = '';
    return parsed.toString();
  } catch {
    return value.length > 2_000 ? `${value.slice(0, 2_000)}…` : value;
  }
}

export function sanitizeForLog(value, seen = new WeakSet()) {
  if (value instanceof Error) {
    return {
      name: value.name,
      message: stripQuery(value.message),
      stack: value.stack ? stripQuery(value.stack).slice(0, 4_000) : undefined,
    };
  }
  if (typeof value === 'string') {
    return stripQuery(value);
  }
  if (value === null || typeof value !== 'object') {
    return value;
  }
  if (seen.has(value)) {
    return '[Circular]';
  }
  seen.add(value);
  if (Array.isArray(value)) {
    return value.slice(0, 100).map((item) => sanitizeForLog(item, seen));
  }
  const output = {};
  for (const [key, child] of Object.entries(value)) {
    output[key] = SENSITIVE_KEY.test(key) ? '[REDACTED]' : sanitizeForLog(child, seen);
  }
  return output;
}

export class JsonLogger {
  constructor({ logsDir, retentionDays = 14, consoleOutput = true }) {
    this.logsDir = logsDir;
    this.retentionDays = retentionDays;
    this.consoleOutput = consoleOutput;
    this.queue = Promise.resolve();
  }

  async init() {
    await mkdir(this.logsDir, { recursive: true });
    await this.#removeExpiredLogs();
  }

  info(event, data = {}) {
    return this.#write('info', event, data);
  }

  warn(event, data = {}) {
    return this.#write('warn', event, data);
  }

  error(event, data = {}) {
    return this.#write('error', event, data);
  }

  async flush() {
    await this.queue;
  }

  #write(level, event, data) {
    const record = sanitizeForLog({
      timestamp: new Date().toISOString(),
      level,
      event,
      ...data,
    });
    const line = `${JSON.stringify(record)}\n`;
    const path = join(this.logsDir, `watcher-${shanghaiDateKey()}.jsonl`);
    if (this.consoleOutput) {
      const consoleMethod = level === 'error' ? console.error : level === 'warn' ? console.warn : console.log;
      consoleMethod(`[${record.timestamp}] ${level.toUpperCase()} ${event}`);
    }
    this.queue = this.queue
      .then(() => appendFile(path, line, { encoding: 'utf8', mode: 0o600 }))
      .catch((error) => console.error(`写入日志失败：${error.message}`));
    return this.queue;
  }

  async #removeExpiredLogs() {
    const cutoff = Date.now() - this.retentionDays * 86_400_000;
    const entries = await readdir(this.logsDir, { withFileTypes: true });
    for (const entry of entries) {
      const match = /^watcher-(\d{4})-(\d{2})-(\d{2})\.jsonl$/.exec(entry.name);
      if (!entry.isFile() || !match) {
        continue;
      }
      const timestamp = Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
      if (timestamp < cutoff) {
        await rm(join(this.logsDir, entry.name), { force: true });
      }
    }
  }
}
