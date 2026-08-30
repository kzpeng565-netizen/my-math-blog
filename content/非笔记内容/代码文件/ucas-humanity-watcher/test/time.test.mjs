import test from 'node:test';
import assert from 'node:assert/strict';
import { intervalsOverlap, lectureConflictsWithBlock, parseLectureTime } from '../src/time.mjs';

const block = {
  name: '周二习题课',
  weekdays: [2],
  start: '18:30',
  end: '20:05',
  validFrom: '2026-08-31',
  validThrough: '2027-01-17',
};

test('解析讲座时间并将跨午夜结束时间放到下一天', () => {
  const lecture = parseLectureTime('2026-09-01 23:30-00:30');
  assert.equal(lecture.date, '2026-09-01');
  assert.equal(lecture.weekday, 2);
  assert.equal(lecture.endEpochMs - lecture.startEpochMs, 60 * 60 * 1_000);
  assert.match(lecture.endAt, /^2026-09-02T00:30/);
});

test('习题课冲突采用半开区间', () => {
  assert.equal(lectureConflictsWithBlock(parseLectureTime('2026-09-01 18:30-20:30'), block), true);
  assert.equal(lectureConflictsWithBlock(parseLectureTime('2026-09-01 17:00-18:30'), block), false);
  assert.equal(lectureConflictsWithBlock(parseLectureTime('2026-09-01 20:05-21:00'), block), false);
  assert.equal(lectureConflictsWithBlock(parseLectureTime('2026-09-01 19:00-19:30'), block), true);
});

test('日期范围之外以及其他星期不排除', () => {
  assert.equal(lectureConflictsWithBlock(parseLectureTime('2027-01-19 18:30-20:30'), block), false);
  assert.equal(lectureConflictsWithBlock(parseLectureTime('2026-09-07 18:30-20:30'), block), false);
});

test('通用重叠判断也遵循半开区间', () => {
  assert.equal(intervalsOverlap(0, 10, 10, 20), false);
  assert.equal(intervalsOverlap(0, 11, 10, 20), true);
});
