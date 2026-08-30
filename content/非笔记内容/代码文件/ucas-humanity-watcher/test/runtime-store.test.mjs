import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { RuntimeStore } from '../src/runtime-store.mjs';

test('运行状态原子写入并能重新读取', async (t) => {
  const root = await mkdtemp(join(tmpdir(), 'ucas-watcher-store-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const path = join(root, 'state.json');
  const store = new RuntimeStore(path);
  await store.init();
  await store.update((state) => {
    state.ignoredIds.push('9001', '9001');
    return state;
  });
  const written = JSON.parse(await readFile(path, 'utf8'));
  assert.deepEqual(written.ignoredIds, ['9001']);

  const reloaded = new RuntimeStore(path);
  const state = await reloaded.init();
  assert.deepEqual(state.ignoredIds, ['9001']);
});
