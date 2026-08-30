import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const notificationScript = fileURLToPath(new URL('../scripts/show-notification.ps1', import.meta.url));

export class WindowsNotifier {
  constructor({ logger }) {
    this.logger = logger;
  }

  async send({ title, message, openUrl, sound = true }) {
    if (process.platform !== 'win32') {
      await this.logger.info('notification_skipped_non_windows', { title });
      return false;
    }
    const powerShell = `${process.env.SystemRoot || 'C:\\Windows'}\\System32\\WindowsPowerShell\\v1.0\\powershell.exe`;
    return new Promise((resolve) => {
      const child = spawn(powerShell, [
        '-NoLogo',
        '-NoProfile',
        '-NonInteractive',
        '-WindowStyle',
        'Hidden',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        notificationScript,
        '-Title',
        String(title).slice(0, 80),
        '-Message',
        String(message).slice(0, 240),
        '-OpenUrl',
        openUrl || '',
        '-Sound',
        sound ? 'true' : 'false',
      ], {
        detached: true,
        stdio: 'ignore',
        windowsHide: true,
      });
      child.once('spawn', () => {
        child.unref();
        resolve(true);
      });
      child.once('error', async (error) => {
        await this.logger.warn('notification_failed', { error });
        resolve(false);
      });
    });
  }
}
