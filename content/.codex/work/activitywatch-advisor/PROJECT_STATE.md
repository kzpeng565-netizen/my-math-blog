# Project State

2026-07-28：已接入只读 Obsidian 上下文、last-known-good 缓存、实际上下文归档和
影子干预候选。影子判断随原有半小时 PushPlus 核验消息发送；每日和每周统计分别由
独立 systemd timer 在白天发送。正式干预未启用，`shadow_mode` 保持为 `true`。

设备事实、语义时间线和确定性混杂指标仍是行为判断的主要事实源。上下文损坏或缺失
不会中断半小时主流程。

AI 状态解释同时归档为 `data/ai_reports/...json` 和 `.md`；DeepSeek 无效 JSON 会
降级成本地低置信度报告，不再导致服务整体失败。

全设备无活动时不调用 DeepSeek、不发 PushPlus，但继续归档本地报告及全部事实层。
这也是完整版必须保留的 token 节省规则。

2026-07-28：手机端系统异常反馈已接入现有 `phone-usage-receiver.service`。
手机只上传 `category` 和可选 `message`；接收时间、编号、半小时窗口与相关报告/事实层
关联全部由树莓派生成。原始反馈保存为不可由 AI 自动改写的 JSON，Markdown 日汇总和
`UNREVIEWED.md` 只是可从 raw JSON 重建的派生视图。
