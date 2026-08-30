import { deduplicateLectures, parseTableSnapshot } from './parser.mjs';
import { mapBookingResult } from './result-map.mjs';

export class LoginRequiredError extends Error {
  constructor(message = '需要手动登录') {
    super(message);
    this.name = 'LoginRequiredError';
  }
}

async function extractSnapshot(page) {
  return page.evaluate(() => {
    const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    const required = ['讲座名称', '讲座地点', '讲座时间', '面向对象', '操作区'];
    const tables = [...document.querySelectorAll('table')];
    const table = tables.find((candidate) => {
      const headers = [...candidate.querySelectorAll('th')].map((node) => clean(node.textContent));
      return required.every((header) => headers.includes(header));
    });
    const pageMatch = /当前页\s*(\d+)\s*\/\s*(\d+)/.exec(document.body?.innerText || '');
    if (!table) {
      return {
        headers: [],
        rows: [],
        currentPage: pageMatch ? Number(pageMatch[1]) : 1,
        totalPages: pageMatch ? Number(pageMatch[2]) : 1,
      };
    }

    const headerRow = [...table.querySelectorAll('tr')].find((row) => row.querySelector('th'));
    const headers = headerRow ? [...headerRow.children].map((node) => clean(node.textContent)) : [];
    const bodyRows = [...table.querySelectorAll('tbody tr')].filter((row) => row.querySelector('td'));
    const rows = bodyRows.map((row) => ({
      cells: [...row.children]
        .filter((node) => node.tagName === 'TD')
        .map((cell) => ({
          text: clean(cell.textContent),
          links: [...cell.querySelectorAll('a,button')].map((action) => ({
            text: clean(action.textContent),
            href: action.href || '',
            onclick: action.getAttribute('onclick') || '',
          })),
        })),
    }));
    return {
      headers,
      rows,
      currentPage: pageMatch ? Number(pageMatch[1]) : 1,
      totalPages: pageMatch ? Number(pageMatch[2]) : 1,
    };
  });
}

function oldestLectureEpoch(lectures) {
  const values = lectures.map((lecture) => lecture.startEpochMs).filter(Number.isFinite);
  return values.length > 0 ? Math.min(...values) : null;
}

export class HumanitySiteClient {
  constructor({ config, browserManager, logger }) {
    this.config = config;
    this.browserManager = browserManager;
    this.logger = logger;
  }

  async scan({ now = Date.now() } = {}) {
    const page = await this.browserManager.getMonitorPage();
    await this.#navigate(page, this.config.targetUrl);
    if (await this.browserManager.pageRequiresLogin(page)) {
      return { loginRequired: true, lectures: [], warnings: [] };
    }

    const lectures = [];
    const warnings = [];
    let pagesScanned = 0;
    while (pagesScanned < this.config.maxScanPages) {
      if (await this.browserManager.pageRequiresLogin(page)) {
        return { loginRequired: true, lectures: [], warnings: [] };
      }
      const parsed = parseTableSnapshot(await extractSnapshot(page));
      lectures.push(...parsed.lectures);
      warnings.push(...parsed.warnings);
      pagesScanned += 1;

      const oldest = oldestLectureEpoch(parsed.lectures);
      const shouldContinue = parsed.currentPage < parsed.totalPages
        && oldest !== null
        && oldest > now
        && pagesScanned < this.config.maxScanPages;
      if (!shouldContinue) {
        break;
      }
      await this.#goToPage(page, parsed.currentPage + 1);
    }

    return {
      loginRequired: false,
      lectures: deduplicateLectures(lectures),
      warnings,
      pagesScanned,
    };
  }

  async book(lectureId, validateBeforeSubmit) {
    const page = await this.browserManager.getMonitorPage();
    const located = await this.#findBookableLecture(page, String(lectureId));
    if (located.loginRequired) {
      throw new LoginRequiredError();
    }
    if (!located.lecture) {
      return {
        submitted: false,
        result: {
          code: 'no_longer_available',
          success: false,
          retryable: false,
          message: '该讲座已不再显示“预约”，没有提交任何请求',
        },
      };
    }

    const validation = await validateBeforeSubmit(located.lecture);
    if (!validation.eligible) {
      return {
        submitted: false,
        lecture: located.lecture,
        result: {
          code: validation.reasonCode,
          success: false,
          retryable: false,
          message: validation.reason,
        },
      };
    }

    const row = page.locator('tr').filter({
      has: page.locator(`a[href*="/subject/${String(lectureId)}/humanityView"]`),
    }).first();
    const action = row.getByText('预约', { exact: true }).first();
    if (await action.count() === 0 || !(await action.isVisible())) {
      return {
        submitted: false,
        lecture: located.lecture,
        result: {
          code: 'no_longer_available',
          success: false,
          retryable: false,
          message: '预约控件已经消失，没有提交任何请求',
        },
      };
    }

    let dialogMessage = '';
    const dialogHandler = async (dialog) => {
      dialogMessage = dialog.message();
      await dialog.accept().catch(() => {});
    };
    page.on('dialog', dialogHandler);
    let rawCode = '';
    try {
      const [response] = await Promise.all([
        page.waitForResponse((candidate) => {
          try {
            return new URL(candidate.url()).pathname === '/subject/toSign' && candidate.request().method() === 'POST';
          } catch {
            return false;
          }
        }, { timeout: this.config.navigationTimeoutMs }),
        action.click({ timeout: this.config.navigationTimeoutMs }),
      ]);
      rawCode = (await response.text()).trim();
      await page.waitForTimeout(250);
    } catch (error) {
      await this.logger.error('booking_submission_uncertain', { lectureId, error });
      const fallback = mapBookingResult('', dialogMessage);
      return {
        submitted: true,
        lecture: located.lecture,
        result: fallback.code === 'unknown'
          ? { ...fallback, message: '提交过程未得到明确响应，请先在报名记录中人工核对，切勿立即重复点击' }
          : fallback,
      };
    } finally {
      page.off('dialog', dialogHandler);
    }

    const result = mapBookingResult(rawCode, dialogMessage);
    let verified = false;
    if (result.success) {
      verified = await this.verifyRecord(String(lectureId));
    }
    return {
      submitted: true,
      lecture: located.lecture,
      verified,
      result: result.success && !verified
        ? { ...result, message: `${result.message}；报名记录暂未核验到，请稍后人工确认` }
        : result,
    };
  }

  async verifyRecord(lectureId) {
    const page = await this.browserManager.getMonitorPage();
    for (let attempt = 0; attempt < 3; attempt += 1) {
      await this.#navigate(page, this.config.recordsUrl);
      if (await this.browserManager.pageRequiresLogin(page)) {
        return false;
      }
      const count = await page.locator(`a[href*="/subject/${lectureId}/humanityView"]`).count();
      if (count > 0) {
        return true;
      }
      await page.waitForTimeout(1_000);
    }
    return false;
  }

  async #findBookableLecture(page, lectureId) {
    await this.#navigate(page, this.config.targetUrl);
    if (await this.browserManager.pageRequiresLogin(page)) {
      return { loginRequired: true, lecture: null };
    }

    let pagesScanned = 0;
    while (pagesScanned < this.config.maxScanPages) {
      const parsed = parseTableSnapshot(await extractSnapshot(page));
      const lecture = parsed.lectures.find((item) => item.lectureId === lectureId && item.available);
      if (lecture) {
        return { loginRequired: false, lecture };
      }
      pagesScanned += 1;
      if (parsed.currentPage >= parsed.totalPages || pagesScanned >= this.config.maxScanPages) {
        break;
      }
      await this.#goToPage(page, parsed.currentPage + 1);
    }
    return { loginRequired: false, lecture: null };
  }

  async #navigate(page, url) {
    await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: this.config.navigationTimeoutMs,
    });
  }

  async #goToPage(page, pageNumber) {
    const navigation = page.waitForNavigation({
      waitUntil: 'domcontentloaded',
      timeout: this.config.navigationTimeoutMs,
    });
    const submitted = await page.evaluate((targetPage) => {
      const input = document.querySelector('input[name="pageNum"]');
      const form = input?.form || document.querySelector('form[name="pagefrm"]');
      if (!input || !form) {
        return false;
      }
      input.value = String(targetPage);
      form.submit();
      return true;
    }, pageNumber);
    if (!submitted) {
      throw new Error(`页面存在后续页，但无法提交第 ${pageNumber} 页表单。`);
    }
    await navigation;
  }
}
