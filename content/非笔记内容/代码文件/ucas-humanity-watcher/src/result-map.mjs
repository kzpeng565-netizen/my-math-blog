const RESULT_MAP = {
  success: { code: 'success', success: true, retryable: false, message: '预约成功' },
  exits: { code: 'already_booked', success: true, retryable: false, message: '该讲座已经预约' },
  conflict: { code: 'course_conflict', success: false, retryable: false, message: '与已选课程时间冲突' },
  fail: { code: 'no_show_block', success: false, retryable: false, message: '存在爽约记录，两周内无法预约' },
  countFail: { code: 'full', success: false, retryable: true, message: '讲座人数已满，可稍后手动重试' },
  reserveTimeFail: { code: 'outside_window', success: false, retryable: true, message: '当前不在预约时间段内' },
  centerFail: { code: 'ineligible', success: false, retryable: false, message: '当前账号不符合集中教学资格' },
  existLecture: { code: 'lecture_conflict', success: false, retryable: false, message: '同一时间段已预约其他讲座' },
  maxcount: { code: 'limit_reached', success: false, retryable: true, message: '已达到预约人数或数量限制' },
};

const DIALOG_RULES = [
  ['报名成功', 'success'],
  ['已经报名', 'exits'],
  ['已选课程时间有冲突', 'conflict'],
  ['爽约记录', 'fail'],
  ['容纳人数已满', 'countFail'],
  ['未到讲座预约时间', 'reserveTimeFail'],
  ['只有集中教学', 'centerFail'],
  ['已经报名其他讲座', 'existLecture'],
  ['超过人数限制', 'maxcount'],
];

export function mapBookingResult(rawCode, dialogMessage = '') {
  const normalized = String(rawCode || '').trim();
  const direct = RESULT_MAP[normalized];
  if (direct) {
    return { ...direct, rawCode: normalized, dialogMessage: String(dialogMessage || '').trim() };
  }
  const dialogRule = DIALOG_RULES.find(([needle]) => String(dialogMessage || '').includes(needle));
  if (dialogRule) {
    const mapped = RESULT_MAP[dialogRule[1]];
    return { ...mapped, rawCode: normalized || null, dialogMessage: String(dialogMessage || '').trim() };
  }
  return {
    code: 'unknown',
    success: false,
    retryable: false,
    message: '预约结果未知，请在报名记录中人工核对后再操作',
    rawCode: normalized || null,
    dialogMessage: String(dialogMessage || '').trim(),
  };
}
