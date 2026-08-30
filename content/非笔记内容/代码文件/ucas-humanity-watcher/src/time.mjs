const SHANGHAI_OFFSET_MINUTES = 8 * 60;

function pad(value) {
  return String(value).padStart(2, '0');
}

function parseClock(value) {
  const match = /^(\d{2}):(\d{2})$/.exec(value || '');
  if (!match) {
    throw new Error(`无法解析时间：${value}`);
  }
  return Number(match[1]) * 60 + Number(match[2]);
}

function localEpochMs(year, month, day, minutes) {
  const hour = Math.floor(minutes / 60);
  const minute = minutes % 60;
  return Date.UTC(year, month - 1, day, hour, minute) - SHANGHAI_OFFSET_MINUTES * 60_000;
}

function nextLocalDay(year, month, day) {
  const date = new Date(Date.UTC(year, month - 1, day) + 86_400_000);
  return {
    year: date.getUTCFullYear(),
    month: date.getUTCMonth() + 1,
    day: date.getUTCDate(),
  };
}

export function parseLectureTime(text) {
  const normalized = String(text || '').replace(/\s+/g, ' ').trim();
  const match = /(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{2})\s*[-–—至]\s*(\d{1,2}):(\d{2})/.exec(normalized);
  if (!match) {
    throw new Error(`无法解析讲座时间：${normalized || '空值'}`);
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const startMinutes = Number(match[4]) * 60 + Number(match[5]);
  const endMinutes = Number(match[6]) * 60 + Number(match[7]);
  const date = `${year}-${pad(month)}-${pad(day)}`;
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay();
  const endDateParts = endMinutes <= startMinutes ? nextLocalDay(year, month, day) : { year, month, day };
  const startEpochMs = localEpochMs(year, month, day, startMinutes);
  const endEpochMs = localEpochMs(endDateParts.year, endDateParts.month, endDateParts.day, endMinutes);

  return {
    raw: normalized,
    date,
    weekday,
    startMinutes,
    endMinutes,
    startEpochMs,
    endEpochMs,
    startAt: `${date}T${pad(Math.floor(startMinutes / 60))}:${pad(startMinutes % 60)}:00+08:00`,
    endAt: `${endDateParts.year}-${pad(endDateParts.month)}-${pad(endDateParts.day)}T${pad(Math.floor(endMinutes / 60))}:${pad(endMinutes % 60)}:00+08:00`,
  };
}

export function intervalsOverlap(startA, endA, startB, endB) {
  return startA < endB && endA > startB;
}

export function lectureConflictsWithBlock(lecture, block) {
  if (!lecture || !Number.isFinite(lecture.startEpochMs) || !Number.isFinite(lecture.endEpochMs)) {
    return false;
  }
  if (lecture.date < block.validFrom || lecture.date > block.validThrough) {
    return false;
  }
  if (!block.weekdays.includes(lecture.weekday)) {
    return false;
  }

  const [year, month, day] = lecture.date.split('-').map(Number);
  const startMinutes = parseClock(block.start);
  const endMinutes = parseClock(block.end);
  const endDateParts = endMinutes <= startMinutes ? nextLocalDay(year, month, day) : { year, month, day };
  const blockStart = localEpochMs(year, month, day, startMinutes);
  const blockEnd = localEpochMs(endDateParts.year, endDateParts.month, endDateParts.day, endMinutes);
  return intervalsOverlap(lecture.startEpochMs, lecture.endEpochMs, blockStart, blockEnd);
}

export function shanghaiDateKey(date = new Date()) {
  const shifted = new Date(date.getTime() + SHANGHAI_OFFSET_MINUTES * 60_000);
  return `${shifted.getUTCFullYear()}-${pad(shifted.getUTCMonth() + 1)}-${pad(shifted.getUTCDate())}`;
}
