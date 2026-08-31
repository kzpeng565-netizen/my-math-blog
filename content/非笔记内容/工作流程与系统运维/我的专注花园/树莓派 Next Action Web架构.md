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

==代码粗筛保留至多 30 条未归档、未结束且仍可能相关的动态。V4 Flash 看到“逾期一天＋今天＋未来两天”的任务安排，其中包含有效日期、priority、循环投影、标题时间窗状态与番茄进度；它以 thinking enabled、请求 `reasoning_effort=low`、800 token 预算筛选。DeepSeek 实际会将 low 映射为 high，该限制会写入审计。==

==健康、生病、考试、硬截止以及当前生效／24 小时内事件会进入强制候选。总量仍为六条；超额时按重要性、是否生效、发生时间、置顶和确认时间裁剪，淘汰 ID 会被记录。Flash 仅给剩余名额排序，返回顺序、相关性、理由、重要性和关联任务会原样保留在 `recent_context_selection`，并随有序 `recent_context` 传给最终 V4 Pro。==

## 2026-08-08：任务时间窗与番茄钟校验范围

==Next Action 按可行动时间窗、有效日期、priority、source order 排序。标题内 `11:00–12:30、16:00–17:30` 会被只读解析；当天最后一个时间窗结束后，该任务不再锁死建议。==

==继续在 Prompt 中保留 `1 🍅 = 40 分钟`，也保留半小时报告、每日报告与专注花园的番茄规则；仅删除 Next Action 最终 AI 输出的本地番茄钟文本拒绝器。==

<!-- ai_provenance: source=codex; date=2026-08-08; verification=unit-tests-plus-live-v4-flash-selector-and-v4-pro-replay; retrieved_notes="PI_SERVER_HANDOFF.md" -->

## 2026-08-08：部署闭环与新增复杂回归

==生产端已核对四个核心源文件哈希及 `selector_candidate_limit=30`。复杂回归覆盖：critical forced 动态在六条上限内优先且记录淘汰项；逾期一天到后天的循环/普通任务投影与 Flash 排序可审计；双时间窗家教结束后不再锁死、明日高优先准备任务可通过校验。相关测试总计 56/56。==

==运行入口未变化：Advisor 仍只监听 `127.0.0.1:8767`，花园仍只调用固定 bridge；从 Windows Tailnet 实测 `:8450` 与 `:8460` 均为 HTTP 200。未新增公网暴露、未重启服务、未写入 Obsidian 任务。==

<!-- ai_provenance: source=codex; date=2026-08-08; verification=pi-source-hash-56-tests-and-windows-tailnet-endpoints; retrieved_notes="PI_SERVER_HANDOFF.md" -->

## 2026-08-09：前端长时生成恢复协议

==`POST /api/next-action/generate` 仍是一次可能持续较久的同步请求；生成结果写入 active storage 只发生在 Advisor 完成后。因此 Focus Garden 不能在导航回 Next Action 时以 active 的 404 清空等待提示。==

==前端在 POST 前于 `sessionStorage[focus-garden-next-action-generation-v1]` 写入 `startedAt` 和 `baselineSuggestionId`，计时器每秒更新等待文案。回到页面先恢复该标记，再每 2 秒 GET `/api/next-action/active`：404 代表仍在运行；若读取到的 ID 仍等于 baseline，代表旧建议，继续等待；读取到新 ID 才清除标记并渲染结果。5 分钟后标记自然失效，避免异常浏览器会话永久禁用生成按钮。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=javascript-syntax-pi-loopback-and-windows-tailnet; retrieved_notes="PI_SERVER_HANDOFF.md" -->

## 2026-08-12：拖延任务成为第一任务候选

==任务通过 Focus Garden 的“推迟一天”累计向后移动至少 2 天后，compact context 会带出 `procrastinated=true` 与 `postponed_days`。`build_decision_state` 生成 `procrastinated_tasks` / `procrastinated_task_titles`；这组任务在普通今天、逾期和未来任务之前排序。==

==若 `procrastinated_task_titles` 非空，task 类型模型输出必须逐字选择其中标题，并在原因或证据中说明累计推迟天数；校验器会拒绝选择普通今天任务的结果，fallback 也使用同一优先级。午休禁工作、深夜睡眠等非 task 决策规则不受影响。Prompt 版本为 `next-action-v1.4-procrastination-priority`。==

<!-- ai_provenance: source=codex; date=2026-08-12; verification=advisor-35-tests-and-live-service; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->


## 2026-08-31：课表导入与系统适配

==Next Action保护课程前20分钟至下课。课程提示复用no_action，source=course_schedule、read_only=true、duration_minutes=0；不进入接受/完成或待反馈闭环。生成、模型返回后、追问、fallback及接受旧建议均核对课程约束，已开始任务仍可正常记录结果。页面新增课程卡片和周切换。==

详见 [[树莓派课程表导入与系统适配]]。

<!-- ai_provenance: source=codex; date=2026-08-31; verification=checked; retrieved_notes="我的专注花园/树莓派 Next Action Web架构.md" -->
