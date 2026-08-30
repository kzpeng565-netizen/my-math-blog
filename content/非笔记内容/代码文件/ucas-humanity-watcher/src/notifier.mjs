import notifier from 'node-notifier';

export class WindowsNotifier {
  constructor({ logger }) {
    this.logger = logger;
  }

  async send({ title, message, openUrl, sound = true }) {
    if (process.platform !== 'win32') {
      await this.logger.info('notification_skipped_non_windows', { title });
      return false;
    }
    return new Promise((resolve) => {
      notifier.notify({
        title: String(title).slice(0, 80),
        message: String(message).slice(0, 240),
        appID: 'UCAS Humanity Watcher',
        sound,
        wait: false,
        open: openUrl,
      }, async (error) => {
        if (error) {
          await this.logger.warn('notification_failed', { error });
          resolve(false);
          return;
        }
        resolve(true);
      });
    });
  }
}
