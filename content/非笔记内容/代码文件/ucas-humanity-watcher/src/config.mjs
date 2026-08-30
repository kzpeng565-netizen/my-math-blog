import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import { constants as fsConstants } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { DEFAULT_CONFIG } from './constants.mjs';

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function runtimeRootFromEnvironment(env = process.env) {
  const localAppData = env.LOCALAPPDATA || join(homedir(), 'AppData', 'Local');
  return join(localAppData, 'UCASHumanityWatcher');
}

export function findEdgeExecutable(env = process.env) {
  const candidates = [
    join(env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    join(env.PROGRAMFILES || 'C:\\Program Files', 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    env.LOCALAPPDATA
      ? join(env.LOCALAPPDATA, 'Microsoft', 'Edge', 'Application', 'msedge.exe')
      : null,
  ].filter(Boolean);
  return candidates;
}

function isClock(value) {
  return typeof value === 'string' && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(value);
}

function isIsoDate(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function validateConfig(config) {
  if (!Number.isInteger(config.pollSeconds) || config.pollSeconds < 15) {
    throw new Error('pollSeconds 必须是至少 15 的整数。');
  }
  if (config.dashboardHost !== '127.0.0.1') {
    throw new Error('dashboardHost 必须保持为 127.0.0.1。');
  }
  if (!Number.isInteger(config.dashboardPort) || config.dashboardPort < 1 || config.dashboardPort > 65_535) {
    throw new Error('dashboardPort 必须是有效端口。');
  }
  if (!Array.isArray(config.campusKeywords) || config.campusKeywords.length === 0) {
    throw new Error('campusKeywords 至少需要一个关键词。');
  }
  if (!Array.isArray(config.weeklyBlocks)) {
    throw new Error('weeklyBlocks 必须是数组。');
  }
  for (const block of config.weeklyBlocks) {
    if (!Array.isArray(block.weekdays) || block.weekdays.some((day) => !Number.isInteger(day) || day < 0 || day > 6)) {
      throw new Error(`无效的星期设置：${block.name || '未命名规则'}`);
    }
    if (!isClock(block.start) || !isClock(block.end)) {
      throw new Error(`无效的时间设置：${block.name || '未命名规则'}`);
    }
    if (!isIsoDate(block.validFrom) || !isIsoDate(block.validThrough) || block.validFrom > block.validThrough) {
      throw new Error(`无效的日期范围：${block.name || '未命名规则'}`);
    }
  }
  return config;
}

async function firstExistingPath(candidates) {
  for (const candidate of candidates) {
    try {
      await access(candidate, fsConstants.X_OK);
      return candidate;
    } catch {
      // 继续检查下一个系统 Edge 路径。
    }
  }
  throw new Error('未找到 Microsoft Edge。请先安装 Edge，再启动监控器。');
}

export async function loadConfig({ runtimeRoot = runtimeRootFromEnvironment(), overrides = {} } = {}) {
  await mkdir(runtimeRoot, { recursive: true });
  const configPath = join(runtimeRoot, 'config.json');
  let userConfig = {};
  try {
    userConfig = JSON.parse(await readFile(configPath, 'utf8'));
  } catch (error) {
    if (error.code !== 'ENOENT') {
      throw new Error(`无法读取本地配置：${error.message}`);
    }
    const initialConfig = {
      pollSeconds: DEFAULT_CONFIG.pollSeconds,
      dashboardHost: DEFAULT_CONFIG.dashboardHost,
      dashboardPort: DEFAULT_CONFIG.dashboardPort,
      campusKeywords: clone(DEFAULT_CONFIG.campusKeywords),
      weeklyBlocks: clone(DEFAULT_CONFIG.weeklyBlocks),
    };
    await mkdir(dirname(configPath), { recursive: true });
    await writeFile(configPath, `${JSON.stringify(initialConfig, null, 2)}\n`, { encoding: 'utf8', mode: 0o600 });
  }

  const allowedUserConfig = Object.fromEntries([
    'pollSeconds',
    'dashboardHost',
    'dashboardPort',
    'campusKeywords',
    'weeklyBlocks',
  ].filter((key) => Object.hasOwn(userConfig, key)).map((key) => [key, userConfig[key]]));

  const merged = validateConfig({
    ...clone(DEFAULT_CONFIG),
    ...allowedUserConfig,
    ...overrides,
    weeklyBlocks: clone(overrides.weeklyBlocks || userConfig.weeklyBlocks || DEFAULT_CONFIG.weeklyBlocks),
    campusKeywords: clone(overrides.campusKeywords || userConfig.campusKeywords || DEFAULT_CONFIG.campusKeywords),
  });

  const edgeExecutable = overrides.edgeExecutable
    || await firstExistingPath(findEdgeExecutable());

  return {
    ...merged,
    edgeExecutable,
    runtimeRoot,
    profileDir: join(runtimeRoot, 'edge-profile'),
    logsDir: join(runtimeRoot, 'logs'),
    statePath: join(runtimeRoot, 'state.json'),
    configPath,
  };
}
