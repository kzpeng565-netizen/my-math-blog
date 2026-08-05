# Pi Server Handoff

项目位于 `/home/conrad/workspace/activitywatch-advisor`，Syncthing 接收目录为
`/home/conrad/workspace/behavior-context-sync`。上下文缓存和归档均在项目 `data/`
下，后者已被 Git 忽略。

运行服务前可检查：

```bash
python3 -m unittest discover -s tests -v
systemctl status syncthing@conrad.service --no-pager
systemctl status activitywatch-advisor.timer --no-pager
```

上下文同步文件夹必须为 Receive Only。不要在树莓派编辑同步内容；不要把它放入
`activitywatch-sync`。半小时核验 PushPlus 消息包含 AI 状态解释和影子判断，但
影子判断不会执行干预。每日和每周统计由独立 timer 发送。

AI 状态解释归档在 `data/ai_reports/YYYY-MM-DD/HH-MM.json` 和 `.md`；语义切段、
混杂指标及 PushPlus 回执均有独立目录。DeepSeek 无效 JSON 会使用本地降级报告。

电脑没有非 AFK 活动且手机、平板没有亮屏时，系统不调用 DeepSeek、不发 PushPlus，
但仍写入事实、上下文、本地报告和影子候选。日报 09:00、周报周一 09:05 发送。

手机异常反馈入口复用 `phone-usage-receiver.service` 和 Tailscale Funnel：

```text
POST https://pi.taild4d3f7.ts.net/annotation
Authorization: Bearer <现有手机上传 token>
Content-Type: application/x-www-form-urlencoded

category=0..4
message=可选说明
```

`/upload/` 仍使用原有 `X-Upload-Token`，不要改变手机数据上传协议。`/annotation`
同时支持 JSON 请求体，但手机 Automate 的正式协议是表单提交。反馈保存在
`data/user_annotations/raw/YYYY-MM-DD/<annotation_id>.json`；当日汇总和未处理总表分别是
`data/user_annotations/daily/YYYY-MM-DD.md` 与 `data/user_annotations/UNREVIEWED.md`。
接收器只记录人工调试标注，不调用 DeepSeek，不自动修改任务或配置。
