import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { BrowserManager } from '../src/browser-manager.mjs';
import { HumanitySiteClient } from '../src/site-client.mjs';

const edgeExecutable = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const logger = { info: async () => {}, warn: async () => {}, error: async () => {} };

function lecturePage() {
  return `<!doctype html><html><body>
    <table>
      <thead><tr><th>讲座专题</th><th>讲座名称</th><th>学时</th><th>讲座地点</th><th>讲座时间</th><th>面向对象</th><th>操作区</th></tr></thead>
      <tbody><tr>
        <td>测试</td><td>M9999 雁栖湖主会场：模拟讲座</td><td>2</td><td>主会场：雁栖湖 - 教一楼101</td>
        <td>2099-09-01 20:05-21:00</td><td>本科生</td>
        <td><a href="/subject/9001/humanityView">查看详情</a> <a href="#" onclick="toSign('9001'); return false;">预约</a></td>
      </tr></tbody>
    </table>
    <div>共1项, 当前页1/1</div>
    <script>
      async function toSign(id) {
        const response = await fetch('/subject/toSign', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'lectureId=' + encodeURIComponent(id)});
        const result = await response.text();
        alert(result === 'success' ? '报名成功！' : result);
      }
    </script>
  </body></html>`;
}

test('模拟站点覆盖登录暂停、扫描、真实控件点击和记录核验', async (t) => {
  let loginRequired = true;
  let bookingRequests = 0;
  const server = createServer((request, response) => {
    if (request.url === '/subject/humanityLecture') {
      response.setHeader('Content-Type', 'text/html; charset=utf-8');
      response.end(loginRequired ? '<form id="sepform"><input id="userName1"><input id="pwd1"><input id="certCode1"></form>' : lecturePage());
      return;
    }
    if (request.url === '/subject/toSign' && request.method === 'POST') {
      bookingRequests += 1;
      response.setHeader('Content-Type', 'text/plain; charset=utf-8');
      response.end('success');
      return;
    }
    if (request.url === '/subject/humanityStudent') {
      response.setHeader('Content-Type', 'text/html; charset=utf-8');
      response.end('<a href="/subject/9001/humanityView">查看详情</a>');
      return;
    }
    response.statusCode = 404;
    response.end('not found');
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));

  const root = await mkdtemp(join(tmpdir(), 'ucas-watcher-browser-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const baseUrl = `http://127.0.0.1:${server.address().port}`;
  const config = {
    targetUrl: `${baseUrl}/subject/humanityLecture`,
    recordsUrl: `${baseUrl}/subject/humanityStudent`,
    targetOrigin: baseUrl,
    navigationTimeoutMs: 15_000,
    maxScanPages: 3,
    profileDir: join(root, 'profile'),
    edgeExecutable,
  };
  const browserManager = new BrowserManager({ config, logger });
  t.after(() => browserManager.stop());
  const client = new HumanitySiteClient({ config, browserManager, logger });

  const blocked = await client.scan();
  assert.equal(blocked.loginRequired, true);
  assert.equal(bookingRequests, 0);

  loginRequired = false;
  const scan = await client.scan();
  assert.equal(scan.loginRequired, false);
  assert.equal(scan.lectures.length, 1);
  assert.equal(scan.lectures[0].available, true);

  const outcome = await client.book('9001', async () => ({ eligible: true }));
  assert.equal(outcome.submitted, true);
  assert.equal(outcome.result.success, true);
  assert.equal(outcome.verified, true);
  assert.equal(bookingRequests, 1);
});
