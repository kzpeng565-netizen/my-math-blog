import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { BrowserManager } from './browser-manager.mjs';
import { loadConfig } from './config.mjs';
import { DashboardServer } from './dashboard.mjs';
import { JsonLogger } from './logger.mjs';
import { WindowsNotifier } from './notifier.mjs';
import { RuntimeStore } from './runtime-store.mjs';
import { WatcherService } from './service.mjs';
import { HumanitySiteClient } from './site-client.mjs';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const config = await loadConfig();
const logger = new JsonLogger({ logsDir: config.logsDir });
await logger.init();

const runtimeStore = new RuntimeStore(config.statePath);
const browserManager = new BrowserManager({ config, logger });
const siteClient = new HumanitySiteClient({ config, browserManager, logger });
const notifier = new WindowsNotifier({ logger });
const service = new WatcherService({
  config,
  browserManager,
  siteClient,
  runtimeStore,
  notifier,
  logger,
});
const dashboard = new DashboardServer({
  host: config.dashboardHost,
  port: config.dashboardPort,
  projectRoot,
  service,
  logger,
});

let shuttingDown = false;
async function shutdown(reason, exitCode = 0) {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;
  await logger.info('shutdown_requested', { reason });
  await service.stop().catch((error) => logger.error('service_stop_failed', { error }));
  await dashboard.stop().catch((error) => logger.error('dashboard_stop_failed', { error }));
  await logger.flush();
  process.exitCode = exitCode;
}

process.once('SIGINT', () => void shutdown('SIGINT'));
process.once('SIGTERM', () => void shutdown('SIGTERM'));
process.on('uncaughtException', (error) => {
  void logger.error('uncaught_exception', { error }).then(() => shutdown('uncaught_exception', 1));
});
process.on('unhandledRejection', (error) => {
  void logger.error('unhandled_rejection', { error });
});

try {
  const dashboardUrl = await dashboard.start();
  service.setDashboardUrl(dashboardUrl);
  await service.start();
  await logger.info('watcher_ready', { dashboardUrl });
  console.log(`本地面板：${dashboardUrl}`);

  if (process.argv.includes('--open-dashboard')) {
    const child = spawn(config.edgeExecutable, [dashboardUrl], {
      detached: true,
      stdio: 'ignore',
    });
    child.unref();
  }
} catch (error) {
  await logger.error('startup_failed', { error });
  console.error(`启动失败：${error.message}`);
  await shutdown('startup_failed', 1);
}
