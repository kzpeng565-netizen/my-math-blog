export const APP_NAME = 'UCAS Humanity Watcher';
export const TARGET_URL = 'https://xkcts.ucas.ac.cn:8443/subject/humanityLecture';
export const RECORDS_URL = 'https://xkcts.ucas.ac.cn:8443/subject/humanityStudent';
export const TARGET_ORIGIN = 'https://xkcts.ucas.ac.cn:8443';

export const DEFAULT_WEEKLY_BLOCKS = [
  {
    name: '周二习题课',
    weekdays: [2],
    start: '18:30',
    end: '20:05',
    validFrom: '2026-08-31',
    validThrough: '2027-01-17',
  },
  {
    name: '周三习题课',
    weekdays: [3],
    start: '18:30',
    end: '20:05',
    validFrom: '2026-08-31',
    validThrough: '2027-01-17',
  },
  {
    name: '周四习题课',
    weekdays: [4],
    start: '18:30',
    end: '20:05',
    validFrom: '2026-08-31',
    validThrough: '2027-01-17',
  },
];

export const DEFAULT_CONFIG = {
  pollSeconds: 60,
  dashboardHost: '127.0.0.1',
  dashboardPort: 17863,
  campusKeywords: ['雁栖湖'],
  weeklyBlocks: DEFAULT_WEEKLY_BLOCKS,
  maxScanPages: 10,
  navigationTimeoutMs: 30_000,
  failureBackoffSeconds: [60, 120, 300, 600],
  targetUrl: TARGET_URL,
  recordsUrl: RECORDS_URL,
  targetOrigin: TARGET_ORIGIN,
};

export const REQUIRED_TABLE_HEADERS = [
  '讲座名称',
  '讲座地点',
  '讲座时间',
  '面向对象',
  '操作区',
];
