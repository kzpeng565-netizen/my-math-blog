import { intervalsOverlap, lectureConflictsWithBlock } from './time.mjs';

export const EXCLUSION_MESSAGES = {
  time_unparsed: '无法可靠解析讲座时间，已按安全原则排除',
  campus_mismatch: '名称和地点均不包含雁栖湖',
  tutorial_conflict: '与未录入课表的习题课冲突',
  ignored: '已手动忽略本场讲座',
  already_booked: '已成功预约',
  booked_lecture_conflict: '与本工具已确认预约的讲座冲突',
};

export function evaluateLecture(lecture, {
  campusKeywords,
  weeklyBlocks,
  ignoredIds = new Set(),
  successfulLectures = [],
} = {}) {
  if (!lecture.available) {
    return { eligible: false, hidden: true, reasonCode: 'not_available', reason: '当前不可预约' };
  }
  if (!Number.isFinite(lecture.startEpochMs) || !Number.isFinite(lecture.endEpochMs)) {
    return { eligible: false, reasonCode: 'time_unparsed', reason: EXCLUSION_MESSAGES.time_unparsed };
  }
  if (!(campusKeywords || []).some((keyword) => lecture.title.includes(keyword) || lecture.location.includes(keyword))) {
    return { eligible: false, reasonCode: 'campus_mismatch', reason: EXCLUSION_MESSAGES.campus_mismatch };
  }
  const conflictingBlock = (weeklyBlocks || []).find((block) => lectureConflictsWithBlock(lecture, block));
  if (conflictingBlock) {
    return {
      eligible: false,
      reasonCode: 'tutorial_conflict',
      reason: `${EXCLUSION_MESSAGES.tutorial_conflict}：${conflictingBlock.name}`,
    };
  }
  if (ignoredIds.has(lecture.lectureId)) {
    return { eligible: false, reasonCode: 'ignored', reason: EXCLUSION_MESSAGES.ignored };
  }
  if (successfulLectures.some((item) => item.lectureId === lecture.lectureId)) {
    return { eligible: false, reasonCode: 'already_booked', reason: EXCLUSION_MESSAGES.already_booked };
  }
  const conflict = successfulLectures.find((item) => Number.isFinite(item.startEpochMs)
    && intervalsOverlap(lecture.startEpochMs, lecture.endEpochMs, item.startEpochMs, item.endEpochMs));
  if (conflict) {
    return {
      eligible: false,
      reasonCode: 'booked_lecture_conflict',
      reason: `${EXCLUSION_MESSAGES.booked_lecture_conflict}：《${conflict.title}》`,
    };
  }
  return { eligible: true, reasonCode: null, reason: null };
}

export function filterBookableLectures(lectures, options) {
  const candidates = [];
  const excluded = [];
  for (const lecture of lectures) {
    const evaluation = evaluateLecture(lecture, options);
    if (evaluation.eligible) {
      candidates.push(lecture);
    } else if (!evaluation.hidden && lecture.available) {
      excluded.push({ ...lecture, exclusionReasonCode: evaluation.reasonCode, exclusionReason: evaluation.reason });
    }
  }
  return { candidates, excluded };
}
