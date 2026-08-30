import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateLecture, filterBookableLectures } from '../src/filters.mjs';
import { deduplicateLectures, parseTableSnapshot } from '../src/parser.mjs';

function snapshot({ title = 'M1200 雁栖湖主会场：测试讲座', location = '主会场：雁栖湖 - 教一楼101', time = '2026-09-01 18:30-20:30' } = {}) {
  return {
    currentPage: 1,
    totalPages: 2,
    headers: ['讲座专题', '讲座名称', '学时', '讲座地点', '讲座时间', '面向对象', '操作区'],
    rows: [{
      cells: [
        { text: '测试', links: [] },
        { text: title, links: [] },
        { text: '2', links: [] },
        { text: location, links: [] },
        { text: time, links: [] },
        { text: '本科生', links: [] },
        {
          text: '查看详情 预约',
          links: [
            { text: '查看详情', href: 'https://xkcts.ucas.ac.cn:8443/subject/9001/humanityView' },
            { text: '预约', href: '#', onclick: "toSign('9001','A')" },
          ],
        },
      ],
    }],
  };
}

const weeklyBlocks = [{
  name: '周二习题课',
  weekdays: [2],
  start: '18:30',
  end: '20:05',
  validFrom: '2026-08-31',
  validThrough: '2027-01-17',
}];

test('按表头解析讲座和预约控件', () => {
  const parsed = parseTableSnapshot(snapshot({ time: '2026-09-01 20:05-21:00' }));
  assert.equal(parsed.currentPage, 1);
  assert.equal(parsed.totalPages, 2);
  assert.equal(parsed.lectures[0].lectureId, '9001');
  assert.equal(parsed.lectures[0].available, true);
  assert.equal(parsed.lectures[0].location.includes('雁栖湖'), true);
});

test('缺少必需表头时失败关闭', () => {
  const invalid = snapshot();
  invalid.headers = invalid.headers.filter((header) => header !== '操作区');
  assert.throws(() => parseTableSnapshot(invalid), /缺少列：操作区/);
});

test('筛选雁栖湖、习题课和忽略项', () => {
  const allowed = parseTableSnapshot(snapshot({ time: '2026-09-01 20:05-21:00' })).lectures[0];
  const tutorialConflict = parseTableSnapshot(snapshot()).lectures[0];
  const wrongCampus = parseTableSnapshot(snapshot({
    title: 'M1200 中关村分会场：测试讲座',
    location: '主会场：中关村 - N101',
    time: '2026-09-01 20:05-21:00',
  })).lectures[0];

  assert.equal(evaluateLecture(allowed, { campusKeywords: ['雁栖湖'], weeklyBlocks }).eligible, true);
  assert.equal(evaluateLecture(tutorialConflict, { campusKeywords: ['雁栖湖'], weeklyBlocks }).reasonCode, 'tutorial_conflict');
  assert.equal(evaluateLecture(wrongCampus, { campusKeywords: ['雁栖湖'], weeklyBlocks }).reasonCode, 'campus_mismatch');
  assert.equal(evaluateLecture(allowed, {
    campusKeywords: ['雁栖湖'],
    weeklyBlocks,
    ignoredIds: new Set(['9001']),
  }).reasonCode, 'ignored');
});

test('成功预约后排除同时间候选并去重', () => {
  const lecture = parseTableSnapshot(snapshot({ time: '2026-09-01 20:05-21:00' })).lectures[0];
  const other = { ...lecture, lectureId: '9002', title: '另一场雁栖湖讲座' };
  const filtered = filterBookableLectures([other], {
    campusKeywords: ['雁栖湖'],
    weeklyBlocks,
    successfulLectures: [lecture],
  });
  assert.equal(filtered.candidates.length, 0);
  assert.equal(filtered.excluded[0].exclusionReasonCode, 'booked_lecture_conflict');
  assert.equal(deduplicateLectures([lecture, lecture]).length, 1);
});
