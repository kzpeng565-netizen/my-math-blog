import { evaluateLecture, filterBookableLectures } from './filters.mjs';
import { LoginRequiredError } from './site-client.mjs';

function sameStringSet(left, right) {
  if (left.size !== right.size) {
    return false;
  }
  return [...left].every((value) => right.has(value));
}

function publicLecture(lecture, lastResult = null) {
  return {
    lectureId: lecture.lectureId,
    title: lecture.title,
    location: lecture.location,
    timeText: lecture.timeText,
    audience: lecture.audience,
    detailUrl: lecture.detailUrl,
    startAt: lecture.startAt,
    endAt: lecture.endAt,
    exclusionReasonCode: lecture.exclusionReasonCode || null,
    exclusionReason: lecture.exclusionReason || null,
    lastResult,
    canBook: !lastResult || lastResult.retryable === true,
  };
}

export class WatcherService {
  constructor({ config, browserManager, siteClient, runtimeStore, notifier, logger }) {
    this.config = config;
    this.browserManager = browserManager;
    this.siteClient = siteClient;
    this.runtimeStore = runtimeStore;
    this.notifier = notifier;
    this.logger = logger;
    this.dashboardUrl = null;
    this.runtimeState = null;
    this.timer = null;
    this.stopping = false;
    this.scanInProgress = false;
    this.bookingInProgress = false;
    this.failureCount = 0;
    this.lastLectures = [];
    this.candidates = [];
    this.excluded = [];
    this.publicState = {
      phase: 'starting',
      message: '正在启动',
      lastScanAt: null,
      nextScanAt: null,
      lastSuccessAt: null,
      lastError: null,
      pagesScanned: 0,
    };

    this.browserManager.on('authenticated', () => {
      void this.#onAuthenticated();
    });
    this.browserManager.on('login_closed', () => {
      void this.#onLoginClosed();
    });
  }

  setDashboardUrl(url) {
    this.dashboardUrl = url;
  }

  async start() {
    this.runtimeState = await this.runtimeStore.init();
    this.stopping = false;
    await this.logger.info('service_started', {
      pollSeconds: this.config.pollSeconds,
      campusKeywords: this.config.campusKeywords,
    });
    this.#scheduleScan(0);
  }

  async stop() {
    this.stopping = true;
    this.#clearTimer();
    this.publicState.phase = 'stopped';
    this.publicState.message = '已停止';
    await this.browserManager.stop();
    await this.runtimeStore.flush();
    await this.logger.info('service_stopped');
  }

  getPublicStatus() {
    const lastResults = this.runtimeState?.lastResults || {};
    return {
      app: 'UCAS Humanity Watcher',
      ...this.publicState,
      loginWindowOpen: this.browserManager.loginWindowOpen,
      pollSeconds: this.config.pollSeconds,
      candidates: this.candidates.map((lecture) => publicLecture(lecture, lastResults[lecture.lectureId] || null)),
      excluded: this.excluded.map((lecture) => publicLecture(lecture, lastResults[lecture.lectureId] || null)),
      successfulCount: Object.keys(this.runtimeState?.successfulLectures || {}).length,
    };
  }

  async openLoginWindow() {
    if (this.browserManager.loginWindowOpen) {
      return { ok: true, message: '登录窗口已经打开' };
    }
    this.#clearTimer();
    this.publicState.phase = 'login_window';
    this.publicState.message = '请在独立 Edge 窗口中手动完成登录和验证码';
    try {
      await this.browserManager.openLoginWindow();
      return { ok: true, message: this.publicState.message };
    } catch (error) {
      this.publicState.phase = 'login_required';
      this.publicState.message = '无法打开登录窗口，请查看日志';
      this.publicState.lastError = error.message;
      await this.logger.error('manual_login_window_failed', { error });
      throw error;
    }
  }

  async ignoreLecture(lectureId) {
    const id = String(lectureId);
    await this.runtimeStore.update((state) => {
      state.ignoredIds = [...new Set([...state.ignoredIds, id])];
      return state;
    });
    this.runtimeState = this.runtimeStore.snapshot();
    this.#applyFilters();
    await this.logger.info('lecture_ignored', { lectureId: id });
    return { ok: true };
  }

  async unignoreLecture(lectureId) {
    const id = String(lectureId);
    await this.runtimeStore.update((state) => {
      state.ignoredIds = state.ignoredIds.filter((value) => value !== id);
      return state;
    });
    this.runtimeState = this.runtimeStore.snapshot();
    this.#applyFilters();
    await this.logger.info('lecture_unignored', { lectureId: id });
    return { ok: true };
  }

  async bookLecture(lectureId) {
    const id = String(lectureId);
    if (this.scanInProgress || this.bookingInProgress) {
      const error = new Error('监控器正在执行其他页面操作，请稍后重试。');
      error.statusCode = 409;
      throw error;
    }
    const candidate = this.candidates.find((lecture) => lecture.lectureId === id);
    if (!candidate) {
      const error = new Error('该讲座已不在当前可预约候选中。');
      error.statusCode = 404;
      throw error;
    }
    const previousResult = this.runtimeState.lastResults[id];
    if (previousResult && !previousResult.retryable && !previousResult.success) {
      const error = new Error('该讲座上次结果不可自动重试，请先人工核对或忽略本场。');
      error.statusCode = 409;
      throw error;
    }

    this.#clearTimer();
    this.bookingInProgress = true;
    this.publicState.phase = 'booking';
    this.publicState.message = `正在确认预约《${candidate.title}》`;
    try {
      const outcome = await this.siteClient.book(id, async (freshLecture) => evaluateLecture(freshLecture, this.#filterOptions()));
      const resultRecord = {
        code: outcome.result.code,
        message: outcome.result.message,
        success: Boolean(outcome.result.success),
        retryable: Boolean(outcome.result.retryable),
        verified: Boolean(outcome.verified),
        timestamp: new Date().toISOString(),
      };
      await this.runtimeStore.update((state) => {
        state.lastResults[id] = resultRecord;
        if (outcome.result.success && outcome.lecture) {
          state.successfulLectures[id] = outcome.lecture;
        }
        return state;
      });
      this.runtimeState = this.runtimeStore.snapshot();
      this.#applyFilters();
      this.publicState.phase = 'running';
      this.publicState.message = outcome.result.message;
      this.publicState.lastError = null;
      await this.logger.info('booking_result', {
        lectureId: id,
        resultCode: outcome.result.code,
        success: outcome.result.success,
        verified: outcome.verified,
        submitted: outcome.submitted,
      });
      if (outcome.result.success) {
        await this.#notify({
          title: outcome.verified ? '人文讲座预约成功' : '预约返回成功，请核对记录',
          message: `${outcome.lecture?.title || candidate.title}\n${outcome.result.message}`,
        });
      }
      this.#scheduleScan(1_000);
      return {
        ok: outcome.result.success,
        submitted: Boolean(outcome.submitted),
        verified: Boolean(outcome.verified),
        result: resultRecord,
      };
    } catch (error) {
      if (error instanceof LoginRequiredError) {
        await this.#enterLoginRequired();
      } else {
        this.publicState.phase = 'error';
        this.publicState.message = '预约操作失败，没有自动重试';
        this.publicState.lastError = error.message;
        await this.logger.error('booking_failed', { lectureId: id, error });
        this.#scheduleScan(this.config.pollSeconds * 1_000);
      }
      throw error;
    } finally {
      this.bookingInProgress = false;
    }
  }

  async scanNow() {
    if (this.stopping || this.scanInProgress || this.bookingInProgress || this.browserManager.loginWindowOpen) {
      return;
    }
    this.scanInProgress = true;
    this.#clearTimer();
    this.publicState.phase = 'scanning';
    this.publicState.message = '正在扫描讲座预告';
    this.publicState.nextScanAt = null;
    try {
      const result = await this.siteClient.scan();
      if (result.loginRequired) {
        await this.#enterLoginRequired();
        return;
      }

      this.failureCount = 0;
      this.lastLectures = result.lectures;
      this.publicState.lastScanAt = new Date().toISOString();
      this.publicState.lastSuccessAt = this.publicState.lastScanAt;
      this.publicState.lastError = null;
      this.publicState.pagesScanned = result.pagesScanned;
      this.publicState.phase = 'running';
      this.publicState.message = `扫描完成：${result.lectures.length} 场，${result.pagesScanned} 页`;
      this.#applyFilters();
      await this.#notifyNewCandidates();
      if (result.warnings.length > 0) {
        await this.logger.warn('scan_parse_warnings', { warnings: result.warnings });
      }
      await this.logger.info('scan_completed', {
        lectureCount: result.lectures.length,
        candidateCount: this.candidates.length,
        excludedCount: this.excluded.length,
        pagesScanned: result.pagesScanned,
      });
      this.#scheduleScan(this.config.pollSeconds * 1_000);
    } catch (error) {
      this.failureCount += 1;
      this.publicState.phase = 'error';
      this.publicState.message = `扫描失败，准备按退避策略重试（第 ${this.failureCount} 次）`;
      this.publicState.lastError = error.message;
      await this.logger.error('scan_failed', { failureCount: this.failureCount, error });
      if (this.failureCount === 3) {
        await this.#notify({ title: '人文讲座监控连续失败', message: '已连续失败 3 次，请打开本地面板查看状态。' });
      }
      const index = Math.min(this.failureCount - 1, this.config.failureBackoffSeconds.length - 1);
      this.#scheduleScan(this.config.failureBackoffSeconds[index] * 1_000);
    } finally {
      this.scanInProgress = false;
    }
  }

  #filterOptions() {
    return {
      campusKeywords: this.config.campusKeywords,
      weeklyBlocks: this.config.weeklyBlocks,
      ignoredIds: new Set(this.runtimeState?.ignoredIds || []),
      successfulLectures: Object.values(this.runtimeState?.successfulLectures || {}),
    };
  }

  #applyFilters() {
    const filtered = filterBookableLectures(this.lastLectures, this.#filterOptions());
    this.candidates = filtered.candidates;
    this.excluded = filtered.excluded;
  }

  async #notifyNewCandidates() {
    const currentIds = new Set(this.candidates.map((lecture) => lecture.lectureId));
    const notifiedIds = new Set(this.runtimeState.notifiedIds || []);
    for (const lecture of this.candidates) {
      if (!notifiedIds.has(lecture.lectureId)) {
        await this.#notify({
          title: '发现可预约的人文讲座',
          message: `${lecture.title}\n${lecture.timeText}\n${lecture.location}`,
        });
      }
    }
    if (!sameStringSet(currentIds, notifiedIds)) {
      await this.runtimeStore.update((state) => {
        state.notifiedIds = [...currentIds];
        return state;
      });
      this.runtimeState = this.runtimeStore.snapshot();
    }
  }

  async #enterLoginRequired() {
    const alreadyRequired = this.publicState.phase === 'login_required';
    this.#clearTimer();
    await this.browserManager.closeMonitor();
    this.publicState.phase = 'login_required';
    this.publicState.message = '登录已失效：监控已暂停，请手动登录';
    this.publicState.nextScanAt = null;
    if (!alreadyRequired) {
      await this.logger.warn('login_required');
      await this.#notify({
        title: '人文讲座监控需要登录',
        message: '扫描已暂停。请打开本地面板，点击“打开登录窗口”后手动完成登录和验证码。',
      });
    }
  }

  async #onAuthenticated() {
    if (this.stopping) {
      return;
    }
    this.publicState.phase = 'running';
    this.publicState.message = '登录已恢复，准备重新扫描';
    this.publicState.lastError = null;
    await this.#notify({ title: '人文讲座监控已恢复', message: '手动登录已验证，正在恢复每分钟扫描。', sound: false });
    this.#scheduleScan(0);
  }

  async #onLoginClosed() {
    if (this.stopping) {
      return;
    }
    this.publicState.phase = 'login_required';
    this.publicState.message = '登录窗口已关闭，但尚未验证成功；监控仍暂停';
    this.publicState.nextScanAt = null;
  }

  async #notify({ title, message, sound = true }) {
    await this.notifier.send({ title, message, openUrl: this.dashboardUrl, sound });
  }

  #scheduleScan(delayMs) {
    if (this.stopping || this.publicState.phase === 'login_required' || this.publicState.phase === 'login_window') {
      return;
    }
    this.#clearTimer();
    this.publicState.nextScanAt = new Date(Date.now() + delayMs).toISOString();
    this.timer = setTimeout(() => {
      void this.scanNow();
    }, delayMs);
  }

  #clearTimer() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    this.publicState.nextScanAt = null;
  }
}
