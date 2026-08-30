import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { DashboardServer } from '../src/dashboard.mjs';

const projectRoot = resolve(fileURLToPath(new URL('..', import.meta.url)));
const logger = { info: async () => {}, warn: async () => {}, error: async () => {} };

test('本地面板拒绝缺少 Origin 或 CSRF 的预约请求', async (t) => {
  let bookings = 0;
  const service = {
    getPublicStatus: () => ({ phase: 'running', candidates: [], excluded: [] }),
    openLoginWindow: async () => ({ ok: true }),
    bookLecture: async () => { bookings += 1; return { ok: true }; },
    ignoreLecture: async () => ({ ok: true }),
    unignoreLecture: async () => ({ ok: true }),
  };
  const dashboard = new DashboardServer({ host: '127.0.0.1', port: 0, projectRoot, service, logger });
  await dashboard.start();
  t.after(() => dashboard.stop());

  const statusResponse = await fetch(`${dashboard.url}/api/status`);
  const status = await statusResponse.json();
  const cookie = statusResponse.headers.get('set-cookie').split(';')[0];

  const rejected = await fetch(`${dashboard.url}/api/candidates/9001/book`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: '{}',
  });
  assert.equal(rejected.status, 403);
  assert.equal(bookings, 0);

  const accepted = await fetch(`${dashboard.url}/api/candidates/9001/book`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Origin: dashboard.url,
      Cookie: cookie,
      'X-CSRF-Token': status.csrfToken,
    },
    body: '{}',
  });
  assert.equal(accepted.status, 200);
  assert.equal(bookings, 1);
});

test('面板提供严格的浏览器安全响应头', async (t) => {
  const service = { getPublicStatus: () => ({ phase: 'running' }) };
  const dashboard = new DashboardServer({ host: '127.0.0.1', port: 0, projectRoot, service, logger });
  await dashboard.start();
  t.after(() => dashboard.stop());
  const response = await fetch(dashboard.url);
  assert.match(response.headers.get('content-security-policy'), /frame-ancestors 'none'/);
  assert.equal(response.headers.get('x-frame-options'), 'DENY');
});
