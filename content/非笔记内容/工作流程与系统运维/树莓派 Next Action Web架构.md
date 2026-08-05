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
