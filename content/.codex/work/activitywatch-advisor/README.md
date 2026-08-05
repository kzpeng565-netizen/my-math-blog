# activitywatch-advisor

树莓派上的半小时行为解释系统。设备事实仍是唯一的客观时长来源；Obsidian 上下文
仅用于解释和影子候选建议。

## Obsidian 上下文

- 输入：`/home/conrad/workspace/behavior-context-sync/context_snapshot.json`
- last-known-good：`data/context_cache/current.json`
- 每次实际使用归档：`data/context_snapshots/YYYY-MM-DD/HH-MM.json`
- 影子候选：`data/intervention_candidates/YYYY-MM-DD/HH-MM.json`
- 每日/每周统计：`data/statistics/daily/`、`data/statistics/weekly/`
- AI 状态解释：`data/ai_reports/YYYY-MM-DD/HH-MM.json` 和同名 `.md`
- AI 语义切段：`data/semantic_timelines/YYYY-MM-DD/HH-MM.json`
- PushPlus 回执：`data/pushplus_receipts/` 与 `data/statistics/pushplus_receipts/`
- 手机异常反馈：`data/user_annotations/raw/`、`data/user_annotations/daily/` 与
  `data/user_annotations/UNREVIEWED.md`

读取失败会回退到 last-known-good；完全不可用时主流程仍继续。树莓派不会写入
Obsidian、同步源目录或任务状态。番茄钟只作低置信度参考。

`behavior_advisor.shadow_mode` 必须至少观察 3—7 天并人工复核后才可改为 `false`。
影子判断现在会附加在原有半小时 PushPlus 核验消息中供人工检查，但不会执行干预。
每日统计在次日 09:00 发送；每周统计在周一 09:05 发送上一自然周。正式干预仍未启用。

若电脑没有非 AFK 活动（包括没有电脑消息/数据），同时手机和平板都没有亮屏证据，
该半小时不会调用 DeepSeek，以节省 token，也不会发送 PushPlus。设备事实、上下文、
本地无活动/休息报告和影子候选仍照常归档。完整版上线后必须继续保留这条规则。

如果 DeepSeek 返回损坏 JSON 或请求失败，系统会归档设备事实、失败语义结果和本地
低置信度报告，并继续发送可核验消息，而不是让整个 systemd 服务失败。

## 手机异常反馈

手机 Automate 通过现有 Funnel 调用 `POST /annotation`，只发送 `category` 和可选
`message`。服务端使用 `ZoneInfo("Asia/Shanghai")` 生成接收时间、半小时窗口和
`annotation_id`，再在 90 分钟内选择接收时间之前最近的 `ai_reports` 作为主要关联报告。
原始 JSON 是事实记录；Markdown 汇总均从 raw JSON 原子重建。

Windows 导出器的版本化副本位于 `windows/behavior-context-exporter/`；实际运行副本
位于 `D:\mathblog\tools\behavior-context-exporter`。

脱敏结构示例见 `docs/context_snapshot.example.json` 和
`docs/shadow_candidate.example.json`。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

统计通知定时器：

```bash
systemctl status activitywatch-advisor-daily-summary.timer --no-pager
systemctl status activitywatch-advisor-weekly-summary.timer --no-pager
```

## 卸载上下文层

1. 保持 Syncthing 文件夹为暂停状态或先从两端移除；
2. 恢复 `run_half_hour.py`、`deepseek_client.py`、prompt 与 settings 的上下文提交；
3. 可选删除 `data/context_cache`、`data/context_snapshots` 和
   `data/intervention_candidates`；这些都是派生数据；
4. 不要删除或修改 Windows 上的 Obsidian 源笔记。
