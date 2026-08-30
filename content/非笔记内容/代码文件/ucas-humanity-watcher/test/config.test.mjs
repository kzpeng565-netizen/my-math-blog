import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { loadConfig } from '../src/config.mjs';
import { TARGET_URL } from '../src/constants.mjs';

test('本地配置不能改写目标网站或 Edge 程序路径', async (t) => {
  const root = await mkdtemp(join(tmpdir(), 'ucas-watcher-config-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  await writeFile(join(root, 'config.json'), JSON.stringify({
    pollSeconds: 60,
    dashboardHost: '127.0.0.1',
    dashboardPort: 17863,
    campusKeywords: ['雁栖湖'],
    weeklyBlocks: [],
    targetUrl: 'https://example.invalid/steal',
    edgeExecutable: 'C:\\malicious.exe',
  }));

  const config = await loadConfig({
    runtimeRoot: root,
    overrides: { edgeExecutable: 'C:\\safe-test-edge.exe' },
  });
  assert.equal(config.targetUrl, TARGET_URL);
  assert.equal(config.edgeExecutable, 'C:\\safe-test-edge.exe');
});

test('面板地址不能配置为公开监听', async (t) => {
  const root = await mkdtemp(join(tmpdir(), 'ucas-watcher-config-host-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  await writeFile(join(root, 'config.json'), JSON.stringify({
    pollSeconds: 60,
    dashboardHost: '0.0.0.0',
    dashboardPort: 17863,
    campusKeywords: ['雁栖湖'],
    weeklyBlocks: [],
  }));
  await assert.rejects(
    () => loadConfig({ runtimeRoot: root, overrides: { edgeExecutable: 'C:\\safe-test-edge.exe' } }),
    /必须保持为 127\.0\.0\.1/,
  );
});
