---
aliases:
  - |-
    树莓派
     Next Action Web架构
---
# 树莓派下一步行动助手架构

这份文档记录 2026-07-29 新增的 Next Action Web。它是现有半小时行为解读系统之上的一个主动请求入口：当我不知道接下来该做什么时，手机打开网页，树莓派临时整理当前状态，调用 DeepSeek V4 Pro，返回一个具体且有说服力的下一步行动。

## 定位

这个系统不是通用聊天，也不是自动干预。它只在我主动点击时运行，目标是把已经收集到的数据转化成一个能马上开始的行动。

AI 输出不只是“做什么”，还要解释为什么现在做这件事值得。建议应包含行动、时长、第一步、简短理由、数据依据、说服说明、可能阻力和缩小版行动。

## 入口

网页入口：

```text
https://pi.taild4d3f7.ts.net:8450
```

Tailscale Serve：

```text
https://pi.taild4d3f7.ts.net:8450 -> http://127.0.0.1:8767
```

systemd 服务：

```text
activitywatch-advisor-web.service
```

项目文件：

```text
/home/conrad/workspace/activitywatch-advisor/src/web_app.py
/home/conrad/workspace/activitywatch-advisor/src/next_action.py
```

该入口是 tailnet only，不使用公开 Funnel。公开 Funnel 仍只用于手机上传和 Automate annotation。

## 决策流程

```text
用户点击“生成建议”
  -> POST /api/next-action
  -> 生成 decision_state
  -> 保存 state snapshot
  -> 调用 DeepSeek V4 Pro
  -> 校验 JSON
  -> 保存 suggestion
  -> 网页展示
```

状态生成器读取：

```text
data/ai_reports/
data/statistics/daily_life/
data/context_cache/current.json
behavior-context-sync/context_snapshot.json
data/next_action/responses/
```

它只读这些数据，不写 Obsidian，不修改任务，不修改番茄钟。

## AI 约束

`decision_type` 只能是：

```text
task
break
exercise
sleep
clarify
no_action
```

工作/学习类建议必须来自当前 Obsidian 任务。AI 不能凭空创造新项目，也不能回写 Obsidian。

允许时长：

```text
5, 10, 15, 25, 40
```

如果模型输出不合法，后端使用本地 fallback suggestion，并把错误写入建议归档。

## 归档

下一步建议相关数据在：

```text
data/next_action/state_snapshots/
data/next_action/suggestions/
data/next_action/responses/
data/next_action/outcomes/
data/next_action/active.json
```

建议中会保存 `_generation`，包括模型名、token 用量和估算成本。

## 反馈

网页按钮：

```text
开始
换一个
现在不做
完成了
正在做
没开始
```

“换一个”和“现在不做”可以填写原因和具体说明。反馈只用于存档和后续分析，不会自动改 prompt、配置或任务。

第一版执行观察只采用手动反馈。设备行为未来可以作为弱证据加入复盘，但不能覆盖用户反馈。

## 半小时报告反馈

网页也能查看半小时报告，但只列出最新 3 条，避免把全部半小时检测日志暴露到网页界面：

```text
data/ai_reports/YYYY-MM-DD/HH-MM.md
```

网页反馈复用已有 annotation 系统：

```text
data/user_annotations/raw/
data/user_annotations/daily/
data/user_annotations/UNREVIEWED.md
```

这意味着 Automate 反馈和网页反馈进入同一套归档。

## 睡眠日报重试

日报 timer 改为：

```text
09:00
10:00
11:00
```

09:00/10:00 如果还没检测到早晨手机边界，只写 pending，不推送日报。11:00 仍没有则标记 possible_fault，并生成低置信日报。

## 当前状态

已验证：

```bash
python3 -m unittest discover -s tests
systemctl is-active activitywatch-advisor-web.service
curl -fsS http://127.0.0.1:8767/api/half-hour/reports
curl -fsS https://pi.taild4d3f7.ts.net:8450/api/half-hour/reports
```

82 项测试通过。实际 `POST /api/next-action` 已成功生成一条 DeepSeek V4 Pro 建议。

## 后续

近期只需要试用，不要急着扩展。最重要的指标是：建议是否足够说服我在几分钟内开始行动。如果经常拒绝，优先分析拒绝原因，而不是加入更多自动化。
# Version 1.1：语言和规则边界

`next-action-v1.1` 在 2026-07-29 加入四类规则。

第一，建议语言更重视心理启动。它应该温和、具体、有适度亲近感，像熟悉我节奏的助手。说服重点是降低启动阻力，而不是训诫、鼓励或催促完成大任务。

第二，12:00-13:00 是固定吃饭和午休窗口。这个时间段默认推荐吃饭、离屏、午睡或轻恢复，不推荐数学和项目工作。

第三，番茄钟是中等可靠性正向证据。番茄数量表示预估预算或进度标记，不保证实际工作能按预估完成。AI 不能说“只剩一个番茄即可完成”，只能说“记录显示接近收尾”或“预估还剩约一个番茄”。

本系统里的番茄钟单位必须明确：`1 🍅 = 40 分钟`，不是常见的 25 分钟。若建议时长是 5、10、15 或 25 分钟，只能称为“启动片段”“缩小版”或“小块”，不能说“刚好一个番茄”或暗示“一个番茄可以用 25 分钟完成”。

第四，任务粒度过大暂不在本版解决。AI 仍从当天任务标题中选择，但 `first_step` 与 `reduced_version` 必须切到 5-10 分钟可启动的小动作。
## 2026-07-30 更新：问题反馈入口

Next Action Web 新增“问题反馈”入口。它和“开始 / 换一个 / 现在不做”这类建议反馈不同，专门用于记录系统本身的问题，例如：

- AI 建议质量粗糙；
- 数据缺失或同步错误；
- 网页显示或交互不顺手；
- 通知没有按预期发送；
- 规则与真实生活习惯不匹配；
- 文档或交接信息过时。

网页会让用户选择分类、严重程度，并填写具体描述。描述应尽量回答：

```text
哪里不对？
当时你预期系统怎么做？
如果与建议或半小时报告有关，具体是哪一条？
```

后端写入：

```text
data/issue_feedback/raw/YYYY-MM-DD/<issue_id>.json
data/issue_feedback/daily/YYYY-MM-DD.md
data/issue_feedback/UNREVIEWED.md
```

后续统一处理时，Codex 从 `UNREVIEWED.md` 开始聚合问题，然后再决定是否修改 prompt、规则、网页、接口或文档。

新增接口：

```text
POST /api/issue-feedback
GET  /api/issue-feedback/recent
```

两个接口都要求登录。这个入口不暴露原始日志，不读取全部半小时报告，只记录用户主动提交的问题描述和当前页面上下文。

# Version 1.2：未完成建议闭环与显式交互证据

## 新建议前先处理上一条

==`POST /api/next-action` 不再无条件生成并覆盖 `active.json`。后端先检查当前建议：已有 outcome，或最近 response 为“换一个/现在不做”，才允许生成下一条；其余情况返回 HTTP 409 和 `pending_outcome_required`。==

网页收到该响应后：

1. 展示后端返回的上一条建议；
2. 提示先填写“完成了/正在做/没开始”；
3. 暂存本次生成意图；
4. outcome 保存成功后，自动重新执行本次生成请求。

这一流程只依赖人工反馈，不使用设备活动猜测完成状态，也不修改 Obsidian Tasks。

## 点击生成即证明用户已经醒来

==用户能够主动打开网页并点击“生成建议”，已经构成“已醒且能交互”的直接证据。睡眠统计中的早晨边界可以继续保持 pending 或 possible_fault，但不能覆盖这条当前交互证据。==

防线分三层：

```text
decision state: request_context.user_is_awake_for_decision_purposes=true
model prompt: 禁止询问是否起床、醒来或仍在睡
validator: clarify 命中起床/醒来语义时拒绝模型输出
```

## 验证

```text
python3 -m unittest discover -s tests -p test_next_action.py -v  -> 9 OK
python3 -m unittest discover -s tests                            -> 90 OK
activitywatch-advisor-web.service                               -> active
POST /api/next-action with unresolved active suggestion         -> 409 pending_outcome_required
```

<!-- ai_provenance: source=codex; date=2026-07-30; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/树莓派下一步行动助手架构.md" -->

## 2026-08-04：免密码访问边界

==`NEXT_ACTION_WEB_PASSWORD` 已从 Pi 的私有环境文件移除；当密码为空时服务的现有认证逻辑直接放行，因此花园的固定 loopback 代理不再需要转发登录 cookie。==

==这不代表公开访问：同时已移除公网 `:10000` Funnel。Next Action 只通过 Tailscale Serve `https://pi.taild4d3f7.ts.net:8450/` 和专注花园 `https://pi.taild4d3f7.ts.net:8460/` 使用；8767 继续只监听 `127.0.0.1`。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/树莓派 Next Action Web架构.md" -->

## 2026-08-05：即时任务有效视图

==生成建议前，Next Action 会读取最新 Obsidian 快照并叠加 Pi 尚未写回的任务 mutation。因此网页刚新建、编辑、推迟或完成任务后，AI 不必等待 Obsidian 打开便能收到最新任务；已有建议若对应旧 task revision 会标记为 stale。==

==请求状态中固定包含上海时区的时间戳、日期、时分、星期、时区和 UTC 偏移。AI 仍只可从有效任务标题中选择工作/学习建议，不能把建议反馈或网页状态直接写入 Obsidian。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/任务计划/ToDo-已经规划好的任务.md" -->

## 2026-08-05：Windows agent heartbeat

==Next Action 新增 `POST /api/computer-interventions/heartbeat`，由 Windows 本地 agent 在既有私有访问链路上每 5 分钟调用。它只更新 server-side agent state 的在线事实，不能领取 request、不能生成建议、不能修改 task mutation，也不能执行任意命令。==

==Focus Garden 仅在 Pi loopback 中读取该状态并展示为健康摘要；Windows heartbeat 超过 12 分钟标记 stale。页面经 :8460 的 tailnet-only Serve 访问，未增加任何公网 API。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## Recent context injection (2026-08-08, v3.2)

Flow: build_decision_state enriches each effective task with an explicit title time-window status, then code coarse-filters archived/ended/needs-review/far-future notes to at most 30 candidates. The V4 Flash selector receives the overdue-one-day + today + next-two-days task plan, including effective date, priority, recurrence projection, time-window status and tomato progress. It runs with thinking enabled, requests `reasoning_effort=low`, and uses an 800-token budget; DeepSeek currently maps low to high, so this requested/effective limitation is recorded in the audit.

Active, within-24-hour, and conservative critical health/exam/deadline notes reserve deterministic slots. If more than six forced notes exist, importance, active status, time proximity, pinning and recency determine the kept six and omitted IDs are recorded. Flash ranks only the remaining slots and returns id/relevance/reason/importance/related task IDs/summary. The server preserves this order instead of re-sorting by recency, caps the final list at six, and stores candidate, forced, Flash-ranked and final-ranked arrays in `recent_context_selection`. Final V4 Pro receives the ordered items plus this audit metadata; it may cite only IDs passed in `recent_context`.

## 2026-08-08：任务时间窗和番茄钟校验范围

Next Action now orders task candidates by actionable time state, effective date, priority and source order. Explicit title ranges such as `11:00–12:30、16:00–17:30` are read without modifying Obsidian: active/upcoming/between-window tasks keep the current-day constraint, while a task whose final window has elapsed no longer locks every task suggestion. Tomorrow's recurring task therefore sorts before a later near-term task.

The final Next Action prompt continues to state `1 🍅 = 40 minutes` and tomato records remain medium-reliability evidence. Only the local text rejection inside Next Action was removed: wording involving 15/25/30-minute starter slices no longer discards an otherwise valid suggestion. Half-hour reports, daily reports, task syncing, Garden settlement and all other Pomodoro rules are unchanged.
## 2026-08-12：拖延任务成为第一任务候选

任务通过 Focus Garden 的“推迟一天”累计向后移动至少 2 天后，compact context 会带出 `procrastinated=true` 与 `postponed_days`。`build_decision_state` 生成 `procrastinated_tasks` / `procrastinated_task_titles`；这组任务在普通今天、逾期和未来任务之前排序。

若 `procrastinated_task_titles` 非空，task 类型模型输出必须逐字选择其中标题，并在原因或证据中说明累计推迟天数；校验器会拒绝选择普通今天任务的结果，fallback 也使用同一优先级。午休禁工作、深夜睡眠等非 task 决策规则不受影响。Prompt 版本为 `next-action-v1.4-procrastination-priority`。

<!-- ai_provenance: source=codex; date=2026-08-12; verification=advisor-35-tests-and-live-service -->

## 2026-08-31：与 Goal Agent 的边界

Goal Agent 不是 Next Action 的新版本。Next Action 继续只回答“当前做什么”，沿用自己的提示词、suggestion/response/outcome 归档和澄清状态；Goal Agent 独立保存长期目标、里程碑、周承诺、证据、聊天、审批和计划版本。

二者只共享 task-sync 的任务事实、稳定 `task_id` 和完成事件。Goal Agent 可以在用户确认推荐日后提交 task mutation，但不能向 Next Action 注入长期聊天或绕过其既有健康、时段、拖延和休息规则。

<!-- ai_provenance: source=codex; date=2026-08-31; verification=production-domain-separation-checked -->
