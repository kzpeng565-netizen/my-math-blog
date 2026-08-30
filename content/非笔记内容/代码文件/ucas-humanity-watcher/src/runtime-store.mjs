import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

const DEFAULT_STATE = {
  version: 1,
  ignoredIds: [],
  notifiedIds: [],
  successfulLectures: {},
  lastResults: {},
};

function normalizeState(value = {}) {
  return {
    version: 1,
    ignoredIds: Array.isArray(value.ignoredIds) ? [...new Set(value.ignoredIds.map(String))] : [],
    notifiedIds: Array.isArray(value.notifiedIds) ? [...new Set(value.notifiedIds.map(String))] : [],
    successfulLectures: value.successfulLectures && typeof value.successfulLectures === 'object'
      ? value.successfulLectures
      : {},
    lastResults: value.lastResults && typeof value.lastResults === 'object' ? value.lastResults : {},
  };
}

export class RuntimeStore {
  constructor(path) {
    this.path = path;
    this.state = structuredClone(DEFAULT_STATE);
    this.queue = Promise.resolve();
  }

  async init() {
    await mkdir(dirname(this.path), { recursive: true });
    try {
      this.state = normalizeState(JSON.parse(await readFile(this.path, 'utf8')));
    } catch (error) {
      if (error.code !== 'ENOENT') {
        throw new Error(`无法读取运行状态：${error.message}`);
      }
      await this.save();
    }
    return this.snapshot();
  }

  snapshot() {
    return structuredClone(this.state);
  }

  update(mutator) {
    const draft = this.snapshot();
    const result = mutator(draft) || draft;
    this.state = normalizeState(result);
    return this.save().then(() => this.snapshot());
  }

  save() {
    const payload = `${JSON.stringify(this.state, null, 2)}\n`;
    const temporary = `${this.path}.${process.pid}.tmp`;
    this.queue = this.queue.then(async () => {
      await writeFile(temporary, payload, { encoding: 'utf8', mode: 0o600 });
      await rename(temporary, this.path);
    });
    return this.queue;
  }

  async flush() {
    await this.queue;
  }
}
