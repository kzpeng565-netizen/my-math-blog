import { REQUIRED_TABLE_HEADERS } from './constants.mjs';
import { parseLectureTime } from './time.mjs';

export function normalizeText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function headerIndexes(headers) {
  const normalized = headers.map(normalizeText);
  const indexes = Object.fromEntries(normalized.map((header, index) => [header, index]));
  const missing = REQUIRED_TABLE_HEADERS.filter((header) => !(header in indexes));
  if (missing.length > 0) {
    throw new Error(`讲座表格缺少列：${missing.join('、')}`);
  }
  return indexes;
}

function detailLinkFromRow(row) {
  return row.cells.flatMap((cell) => cell.links || []).find((link) => /\/subject\/\d+\/humanityView(?:$|[?#])/.test(link.href || ''));
}

function lectureIdFromHref(href) {
  return /\/subject\/(\d+)\/humanityView(?:$|[?#])/.exec(href || '')?.[1] || null;
}

export function parseTableSnapshot(snapshot) {
  const indexes = headerIndexes(snapshot.headers || []);
  const warnings = [];
  const lectures = [];

  for (const row of snapshot.rows || []) {
    const detailLink = detailLinkFromRow(row);
    const lectureId = lectureIdFromHref(detailLink?.href);
    if (!lectureId) {
      continue;
    }

    const title = normalizeText(row.cells[indexes['讲座名称']]?.text);
    const location = normalizeText(row.cells[indexes['讲座地点']]?.text);
    const timeText = normalizeText(row.cells[indexes['讲座时间']]?.text);
    const audience = normalizeText(row.cells[indexes['面向对象']]?.text);
    const operationCell = row.cells[indexes['操作区']] || { text: '', links: [] };
    const bookAction = (operationCell.links || []).find((link) => normalizeText(link.text) === '预约');

    let parsedTime = null;
    let timeParseError = null;
    try {
      parsedTime = parseLectureTime(timeText);
    } catch (error) {
      timeParseError = error.message;
      if (bookAction) {
        warnings.push({ lectureId, message: error.message });
      }
    }

    lectures.push({
      lectureId,
      title,
      location,
      timeText,
      audience,
      detailUrl: detailLink.href,
      available: Boolean(bookAction),
      actionText: normalizeText(operationCell.text),
      pageNumber: snapshot.currentPage || 1,
      timeParseError,
      ...(parsedTime || {}),
    });
  }

  return {
    lectures,
    warnings,
    currentPage: Number(snapshot.currentPage) || 1,
    totalPages: Math.max(Number(snapshot.totalPages) || 1, 1),
  };
}

export function deduplicateLectures(lectures) {
  const byId = new Map();
  for (const lecture of lectures) {
    byId.set(lecture.lectureId, lecture);
  }
  return [...byId.values()];
}
