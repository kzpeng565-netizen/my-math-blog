from pathlib import Path


ROOT = Path('/home/conrad/workspace/activitywatch-advisor')
MARKER = '## 2026-08-07：Cold Turkey release backlog 隔离与保守归档'
BODY = '''

## 2026-08-07：Cold Turkey release backlog 隔离与保守归档

==历史 Focus Garden 无 lease release 共 2,761 条，已从派发目录移至 `data/computer_interventions/archive/release/legacy-unleased/`，原始 JSON 保留。Windows Agent 拒绝无 lease 的 `-stop`；新的 release 必须带启动请求的 lease_id。==

==保守自动清理：无 lease 且超过 10 分钟宽限期的旧协议记录归档；带 lease 的 release 不按 TTL 删除，只在 Windows Agent final 后移至 `archive/release/completed/`。Focus Garden 结束或取消时从 execute dispatcher receipt 取得 lease 后再请求 release。==
'''

for filename in ('PROJECT_STATE.md', 'DECISIONS.md', 'NEXT_STEPS.md', 'PI_SERVER_HANDOFF.md'):
    path = ROOT / filename
    text = path.read_text(encoding='utf-8')
    if MARKER not in text:
        path.write_text(text.rstrip() + BODY + '\n', encoding='utf-8')
        print(f'updated {filename}')
    else:
        print(f'already current {filename}')
