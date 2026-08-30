import { EventEmitter } from 'node:events';
import { mkdir } from 'node:fs/promises';
import { chromium } from 'playwright-core';

export class BrowserManager extends EventEmitter {
  constructor({ config, logger }) {
    super();
    this.config = config;
    this.logger = logger;
    this.monitorContext = null;
    this.monitorPage = null;
    this.loginContext = null;
    this.loginPollTimer = null;
    this.loginPollBusy = false;
    this.closingLoginForSuccess = false;
    this.stopping = false;
  }

  get loginWindowOpen() {
    return Boolean(this.loginContext);
  }

  async getMonitorPage() {
    if (this.loginContext) {
      throw new Error('手动登录窗口打开时不能启动后台扫描。');
    }
    if (this.monitorPage && !this.monitorPage.isClosed()) {
      return this.monitorPage;
    }
    await this.#launchMonitorContext();
    return this.monitorPage;
  }

  async isAuthenticatedPage(page) {
    if (!page || page.isClosed()) {
      return false;
    }
    let url;
    try {
      url = new URL(page.url());
    } catch {
      return false;
    }
    const expectedOrigin = new URL(this.config.targetUrl).origin;
    if (url.origin !== expectedOrigin || url.pathname === '/redirect') {
      return false;
    }
    if (!url.pathname.startsWith('/subject/')) {
      return false;
    }
    const loginFormCount = await page.locator('#sepform, #userName1, #pwd1').count().catch(() => 1);
    return loginFormCount === 0;
  }

  async pageRequiresLogin(page) {
    if (!page || page.isClosed()) {
      return true;
    }
    const url = page.url();
    const target = new URL(this.config.targetUrl);
    let parsed;
    try {
      parsed = new URL(url);
    } catch {
      return true;
    }
    if (parsed.hostname === 'sep.ucas.ac.cn' || parsed.pathname === '/redirect') {
      return true;
    }
    if (parsed.origin !== target.origin) {
      return true;
    }
    return (await page.locator('#sepform, #userName1, #pwd1').count().catch(() => 1)) > 0;
  }

  async closeMonitor() {
    const context = this.monitorContext;
    this.monitorContext = null;
    this.monitorPage = null;
    if (context) {
      await context.close().catch(() => {});
    }
  }

  async openLoginWindow() {
    if (this.loginContext) {
      return { opened: false, reason: 'already_open' };
    }
    await this.closeMonitor();
    await mkdir(this.config.profileDir, { recursive: true });

    this.closingLoginForSuccess = false;
    const context = await chromium.launchPersistentContext(this.config.profileDir, {
      executablePath: this.config.edgeExecutable,
      headless: false,
      locale: 'zh-CN',
      timezoneId: 'Asia/Shanghai',
      viewport: null,
      acceptDownloads: false,
      args: ['--start-maximized'],
    });
    this.loginContext = context;
    context.once('close', () => this.#handleLoginContextClosed());
    const page = context.pages()[0] || await context.newPage();
    await page.goto(this.config.targetUrl, {
      waitUntil: 'domcontentloaded',
      timeout: this.config.navigationTimeoutMs,
    }).catch(async (error) => {
      await this.logger.warn('login_page_navigation_failed', { error });
    });
    await this.logger.info('manual_login_window_opened');
    this.loginPollTimer = setInterval(() => {
      void this.#pollLoginProgress();
    }, 2_000);
    return { opened: true };
  }

  async stop() {
    this.stopping = true;
    this.#clearLoginPoll();
    await this.closeMonitor();
    const loginContext = this.loginContext;
    this.loginContext = null;
    if (loginContext) {
      await loginContext.close().catch(() => {});
    }
  }

  async #launchMonitorContext() {
    await mkdir(this.config.profileDir, { recursive: true });
    try {
      const context = await chromium.launchPersistentContext(this.config.profileDir, {
        executablePath: this.config.edgeExecutable,
        headless: true,
        locale: 'zh-CN',
        timezoneId: 'Asia/Shanghai',
        viewport: { width: 1280, height: 900 },
        acceptDownloads: false,
      });
      this.monitorContext = context;
      this.monitorPage = context.pages()[0] || await context.newPage();
      context.once('close', () => {
        if (this.monitorContext === context) {
          this.monitorContext = null;
          this.monitorPage = null;
        }
      });
      await this.logger.info('monitor_browser_started', { headless: true });
    } catch (error) {
      throw new Error(`无法启动独立 Edge 会话：${error.message}`);
    }
  }

  async #pollLoginProgress() {
    if (this.loginPollBusy || !this.loginContext) {
      return;
    }
    this.loginPollBusy = true;
    try {
      const context = this.loginContext;
      const pages = context.pages().filter((page) => !page.isClosed());
      for (const page of pages) {
        if (await this.isAuthenticatedPage(page)) {
          await this.#completeLogin(context);
          return;
        }
      }

      for (const page of pages) {
        let url;
        try {
          url = new URL(page.url());
        } catch {
          continue;
        }
        if (url.hostname !== 'sep.ucas.ac.cn') {
          continue;
        }
        const loginFormVisible = await page.locator('#sepform, #userName1, #pwd1').count().catch(() => 1);
        if (loginFormVisible === 0) {
          await page.goto(this.config.targetUrl, {
            waitUntil: 'domcontentloaded',
            timeout: this.config.navigationTimeoutMs,
          }).catch(() => {});
          if (await this.isAuthenticatedPage(page)) {
            await this.#completeLogin(context);
            return;
          }
        }
      }
    } finally {
      this.loginPollBusy = false;
    }
  }

  async #completeLogin(context) {
    if (this.loginContext !== context) {
      return;
    }
    this.closingLoginForSuccess = true;
    this.#clearLoginPoll();
    await this.logger.info('manual_login_verified');
    await context.close().catch(() => {});
    this.loginContext = null;
    this.closingLoginForSuccess = false;
    this.emit('authenticated');
  }

  #handleLoginContextClosed() {
    const completed = this.closingLoginForSuccess;
    this.#clearLoginPoll();
    this.loginContext = null;
    if (!completed && !this.stopping) {
      void this.logger.warn('manual_login_window_closed_before_verification');
      this.emit('login_closed');
    }
  }

  #clearLoginPoll() {
    if (this.loginPollTimer) {
      clearInterval(this.loginPollTimer);
      this.loginPollTimer = null;
    }
  }
}
