import { createServer } from 'node:http';
import { randomBytes } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

function parseCookies(header = '') {
  return Object.fromEntries(header.split(';').map((part) => {
    const index = part.indexOf('=');
    if (index < 0) {
      return [part.trim(), ''];
    }
    return [part.slice(0, index).trim(), decodeURIComponent(part.slice(index + 1).trim())];
  }).filter(([key]) => key));
}

function json(response, statusCode, payload, extraHeaders = {}) {
  response.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    ...extraHeaders,
  });
  response.end(JSON.stringify(payload));
}

async function readJsonBody(request) {
  let size = 0;
  const chunks = [];
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 16_384) {
      const error = new Error('请求正文过大。');
      error.statusCode = 413;
      throw error;
    }
    chunks.push(chunk);
  }
  if (chunks.length === 0) {
    return {};
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}

export class DashboardServer {
  constructor({ host, port, projectRoot, service, logger }) {
    this.host = host;
    this.port = port;
    this.projectRoot = projectRoot;
    this.service = service;
    this.logger = logger;
    this.server = null;
    this.actualPort = null;
    this.csrfToken = randomBytes(32).toString('base64url');
    this.assets = new Map();
  }

  get url() {
    return this.actualPort ? `http://${this.host}:${this.actualPort}` : null;
  }

  async start() {
    await this.#loadAssets();
    this.server = createServer((request, response) => {
      void this.#handle(request, response);
    });
    await new Promise((resolve, reject) => {
      this.server.once('error', reject);
      this.server.listen(this.port, this.host, () => {
        this.server.off('error', reject);
        resolve();
      });
    });
    this.actualPort = this.server.address().port;
    await this.logger.info('dashboard_started', { host: this.host, port: this.actualPort });
    return this.url;
  }

  async stop() {
    if (!this.server) {
      return;
    }
    const server = this.server;
    this.server = null;
    await new Promise((resolve) => server.close(() => resolve()));
  }

  async #loadAssets() {
    const webDir = join(this.projectRoot, 'web');
    this.assets.set('/', { type: 'text/html; charset=utf-8', body: await readFile(join(webDir, 'index.html')) });
    this.assets.set('/app.js', { type: 'text/javascript; charset=utf-8', body: await readFile(join(webDir, 'app.js')) });
    this.assets.set('/styles.css', { type: 'text/css; charset=utf-8', body: await readFile(join(webDir, 'styles.css')) });
  }

  async #handle(request, response) {
    const commonHeaders = {
      'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'no-referrer',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    };
    for (const [key, value] of Object.entries(commonHeaders)) {
      response.setHeader(key, value);
    }

    try {
      const expectedHost = `${this.host}:${this.actualPort}`;
      if (request.headers.host !== expectedHost) {
        json(response, 403, { error: '非法 Host。' });
        return;
      }
      const url = new URL(request.url, this.url);
      if (request.method === 'GET' && this.assets.has(url.pathname)) {
        const asset = this.assets.get(url.pathname);
        response.writeHead(200, {
          'Content-Type': asset.type,
          'Cache-Control': url.pathname === '/' ? 'no-store' : 'public, max-age=300',
        });
        response.end(asset.body);
        return;
      }
      if (request.method === 'GET' && url.pathname === '/healthz') {
        json(response, 200, { ok: true, phase: this.service.getPublicStatus().phase });
        return;
      }
      if (request.method === 'GET' && url.pathname === '/api/status') {
        json(response, 200, {
          ...this.service.getPublicStatus(),
          csrfToken: this.csrfToken,
        }, {
          'Set-Cookie': `ucas_watcher_csrf=${encodeURIComponent(this.csrfToken)}; Path=/; HttpOnly; SameSite=Strict`,
        });
        return;
      }
      if (request.method === 'POST' && url.pathname.startsWith('/api/')) {
        this.#assertProtectedRequest(request);
        await readJsonBody(request);
        const route = this.#matchAction(url.pathname);
        if (!route) {
          json(response, 404, { error: '接口不存在。' });
          return;
        }
        const payload = await route.action(route.lectureId);
        json(response, 200, payload);
        return;
      }
      json(response, 404, { error: '页面不存在。' });
    } catch (error) {
      const statusCode = Number.isInteger(error.statusCode) ? error.statusCode : 500;
      if (statusCode >= 500) {
        await this.logger.error('dashboard_request_failed', { method: request.method, path: request.url, error });
      }
      json(response, statusCode, { error: error.message || '请求失败。' });
    }
  }

  #assertProtectedRequest(request) {
    const expectedOrigin = this.url;
    if (request.headers.origin !== expectedOrigin) {
      const error = new Error('非法请求来源。');
      error.statusCode = 403;
      throw error;
    }
    const cookies = parseCookies(request.headers.cookie);
    if (request.headers['x-csrf-token'] !== this.csrfToken || cookies.ucas_watcher_csrf !== this.csrfToken) {
      const error = new Error('CSRF 校验失败。');
      error.statusCode = 403;
      throw error;
    }
    const contentType = request.headers['content-type'] || '';
    if (!contentType.startsWith('application/json')) {
      const error = new Error('请求格式必须是 JSON。');
      error.statusCode = 415;
      throw error;
    }
  }

  #matchAction(pathname) {
    if (pathname === '/api/login/open') {
      return { action: () => this.service.openLoginWindow(), lectureId: null };
    }
    const match = /^\/api\/candidates\/(\d+)\/(book|ignore|unignore)$/.exec(pathname);
    if (!match) {
      return null;
    }
    const [, lectureId, action] = match;
    if (action === 'book') {
      return { action: (id) => this.service.bookLecture(id), lectureId };
    }
    if (action === 'ignore') {
      return { action: (id) => this.service.ignoreLecture(id), lectureId };
    }
    return { action: (id) => this.service.unignoreLecture(id), lectureId };
  }
}
