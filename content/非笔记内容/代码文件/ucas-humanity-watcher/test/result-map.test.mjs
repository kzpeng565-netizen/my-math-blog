import test from 'node:test';
import assert from 'node:assert/strict';
import { mapBookingResult } from '../src/result-map.mjs';

test('映射网站全部已知预约结果', () => {
  assert.deepEqual(
    ['success', 'exits', 'conflict', 'fail', 'countFail', 'reserveTimeFail', 'centerFail', 'existLecture', 'maxcount']
      .map((value) => mapBookingResult(value).code),
    ['success', 'already_booked', 'course_conflict', 'no_show_block', 'full', 'outside_window', 'ineligible', 'lecture_conflict', 'limit_reached'],
  );
});

test('人数已满可手动重试，但未知结果禁止自动重试', () => {
  assert.equal(mapBookingResult('countFail').retryable, true);
  assert.equal(mapBookingResult('unexpected').retryable, false);
  assert.equal(mapBookingResult('', '报名成功！').success, true);
});
