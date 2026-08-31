<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified -->

# 半小时行为解释系统——DECISIONS

### D45. 半小时报告只归档，不再微信推送 【有效】

**[已由用户确认][已由服务器核实]**

==半小时 AI 报告必须继续写入 `data/ai_reports/`，供专注花园只读状态面板读取最新报告；`activitywatch-advisor.service` 通过 systemd drop-in 移除 `PUSHPLUS_TOKEN`，使该服务的 PushPlus 发送确定性跳过。该开关仅作用于半小时报告，周报 PushPlus 与独立 ntfy 通知不变。==

> 本文档记录项目中的关键设计决策及其原因。每个决策标注状态：**有效** / **已废弃** / **待评估**。

## 架构决策

### D1. 树莓派作为处理中心，而非 Windows 【有效】

**决策**：行为数据清洗和 AI 调用全部在树莓派上进行。Windows 只运行无 AI、无网络上传逻辑的 Obsidian 只读导出器，传输仍由 Syncthing 完成。

**原因**：
- 树莓派 24 小时运行，不受用户开关机影响
- 避免 Windows 上弹出 PowerShell 窗口
- 统一管理手机和电脑数据
- 行为数据与 AI 依赖只在树莓派维护；Windows 仅保留读取本机 Vault 所必需的轻量导出器，并通过 `pythonw.exe` 静默运行

### D2. Syncthing 而非自建上传 【有效】

**决策**：电脑 ActivityWatch 数据通过 Syncthing 同步到树莓派，而非写 Python 脚本上传。

**原因**：
- ActivityWatch 使用 SQLite 数据库，直接读 SQLite 比调 REST API 更可靠
- 避免 Windows 上运行额外上传脚本带来的 PowerShell 弹窗问题
- Syncthing 已成熟部署，提供文件级增量同步

### D3. 手机走 Tailscale Funnel 而非 Syncthing 【有效】

**决策**：手机数据通过 HTTPS PUT 上传，经 Tailscale Funnel 到达树莓派。

**原因**：
- Android 同时只能运行一个 VPN（Clash 已占用），不能用 Tailscale
- Automate 内置 HTTP 请求模块，不需要安装额外应用
- Funnel 提供公网可达域名，手机在任何网络下都能上传
- 接收端强制验证 token，安全性足够

### D4. 两层 AI（语义时间线 + 解释），程序在中间计算 【有效】

**决策**：第一次 AI 调用生成互斥语义时间段，程序计算混杂指标，第二次 AI 调用仅解释。

**原因**：
- 用户明确要求"工作时间应该由程序计算，不是让 AI 猜"
- 分层后可以独立校验：时间线不对找第一次 AI，指标不对找程序
- 语义时间线是全场可复用的资产，全天分析时可以直接读

### D5. 设备独立事实层（computer_facts + phone_facts + tablet_facts） 【有效】

**决策**：电脑、手机和平板各自独立清洗为事实摘要，只在 cross_device 层计算客观时间重叠；平板保持辅助数据源地位。

**原因**：
- 电脑 AFK 不等于休息（可能在看手机）
- 三套采集器的缺失率和延迟不同
- 独立保存后全天分析可以复用，不需要重新读取原始事件

### D5.1 清洗事实之后增加可配置标签层 【有效】

**[已由用户确认][已由服务器核实]**

**决策**：电脑、手机、平板仍分别清洗；融合后由 `fact_tagger.py` 根据 `config/tag_rules.json` 生成统一40分钟 `tagged_facts`。规则可以新增、删除、禁用和调整优先级，不把不断增长的识别逻辑硬编码在 prompt 中。

**原因**：
- 程序适合识别微信、Telegram、知乎首页、确认休息等稳定事实，并锁定不可被 AI 覆盖的边界；
- AI仍负责标题语义、任务关系和未知活动，避免把程序有限的识别能力当作最终分类器；
- 每个标签保留规则 ID、强度和规则版本，误判可以追踪并单独修改。

### D5.2 AI只接收候选单元，精确时间由程序恢复 【有效】

**[已由用户确认][已由服务器核实]**

**决策**：1—3秒采样缝隙由程序吸附到相邻候选单元；程序锁定段只作为无可输出 ID 的边界标记。AI返回候选单元 ID 和语义，不生成时间戳。若 AI 跨越锁定边界分组，程序按原子事实块拆开；漏答只局部标为 `uncertain`。

**原因**：减少 JSON 重复和输出 token，同时保证30分钟恰好覆盖、锁定通信/休息不会被吞并。

### D5.3 第二次 AI 只解释精简摘要 【有效】

**[已由用户确认][已由服务器核实]**

**决策**：最终解释模型只接收完整活动总量、至少30秒的重要片段、设备 Top 活动、混杂指标和受限 Obsidian 上下文；完整时间线和确定性数字由程序写回报告。

**验证**：19:00 与20:00历史回放均完整覆盖1800秒；两窗平均估算约0.0095元，按48窗/日粗算约0.46元，较原约1.3元/日预计下降约65%。

### D5.4 每日生活复盘由脚本计数，AI 只写建议 【有效】

**[已由用户确认][已由服务器核实]**

**决策**：`daily_life_statistics.py` 负责确定性统计总工作时间、各工作类别、娱乐、通信、AI使用和手机睡眠边界；DeepSeek 只接收脚本给出的候选项、Obsidian Profile/任务/番茄钟上下文，输出简短建议和明日优先任务，不重算分钟数。

**模型**：建议层单独使用 `settings.json` 的 `report_model.name = deepseek-v4-pro`；半小时解释主流程仍保持原模型配置。

**原因**：用户希望建议能判断“某个时间块是否耗时过多、效率是否过低、系统是否需要调整、明天哪些任务优先”，但这些判断必须以程序统计和任务上下文为边界，避免 AI 编造任务或把正常娱乐/休息道德化。

## 语义判断决策

### D6. 确认休息必须满足：电脑 AFK ≥ 3 分钟且手机熄屏 【有效】

**决策**：确定性规则，AI 不能自行判断休息。

**来源**：用户明确确认："电脑连续 AFK 至少 3 分钟、手机熄屏，平板亮屏不否决休息，仅降低置信度（D18）。" 这与 D28 的“停止 AI/推送”规则不同；D28 还要求平板无亮屏。

### D7. 工作-娱乐混杂而非碎片化统计 【有效】

**决策**：衡量工作-娱乐混杂（工作中出现 >30s 娱乐偏离的次数和时长），而非应用切换次数。

**来源**：用户反馈"在工作的时候花十秒钟回消息是正常的。真正需要避免的是，在做一项任务的时候，切出去娱乐两三分钟。"

### D8. 娱乐偏离阈值：> 30 秒 【有效】

**决策**：工作中被 AI 判为娱乐且持续严格超过 30 秒，才计入娱乐偏离。

**来源**：用户确认"娱乐偏离超过 30 秒钟就可以判定。"

### D9. 短暂通信不计入娱乐偏离 【有效】

**决策**：微信、QQ 等通信被 AI 标记为 `brief_communication` 时，不计入娱乐偏离，也不拆散前后相同工作任务。

**来源**：用户确认工作期间的回复消息属于正常行为。

### D10. 同任务工具切换不算偏离 【有效】

**决策**：ChatGPT、浏览器、Obsidian、B站数学视频等服务于同一任务时，不算娱乐偏离。

**来源**：用户反馈"ChatGPT、Obsidian、浏览器页面标签都是服务于同一个任务"。

## 实现决策

### D11. 浏览器数据优先使用 Web Watcher 【有效】

**决策**：`computer_facts.py` 优先使用 ActivityWatch Web Watcher（Edge 插件）记录的域名和标签页标题；缺失时退回窗口标题。

**原因**：窗口标题可能是"Microsoft Edge"，而 Web Watcher 记录了具体标签页标题和域名，AI 需要后者来理解用户实际在浏览什么。

### D12. 定时器偏移到 08/38 分 【有效】

**决策**：`activitywatch-advisor.timer` 在每小时 08 分和 38 分触发，而非整点/半点。

**原因**：手机约 15 分钟上传一次（00/15/30/45 分），偏移 8 分钟确保最近的手机数据已到达再开始分析。

### D13. 语义切段使用非思考模式 【有效】

**决策**：第一次 AI 调用（生成语义时间线）禁用 DeepSeek 思考模式。

**原因**：思考模式可能把输出 token 全部消耗在内部推理，导致无 JSON 返回。通用调用层在检测到这种情况时也会自动关闭思考并重试。

### D14. 用 MD 报告做微信推送 【有效】

**决策**：PushPlus 使用 `markdown` 模板推送，内容是精简过的 Markdown。

**原因**：用户要求通过微信公众号核验，Markdown 在微信中可读性较高，同时保留了结构化信息。

### D15. 密钥分离存储 【有效】

**决策**：DeepSeek API 密钥 (`~/.config/activitywatch-advisor/env`)、PushPlus token (`~/.config/activitywatch-advisor/pushplus.env`)、上传 token (`/home/conrad/phone_usage/token.txt`) 三个密钥独立存储，均为 600 权限。

**原因**：权限最小化，单一密钥泄露不导致全部系统失效。

## 应用分类决策

### D16. 电脑应用显示名映射 【有效】

`settings.json` 中的 `computer_app_names` 映射了关键应用（msedge.exe → "Microsoft Edge", ChatGPT.exe → "ChatGPT" 等）。浏览器进程名不直接映射为"工作"或"娱乐"，由 AI 根据标签页标题和域名判断。

### D17. 浏览器 URL 只保留域名 【有效】

完整 URL 不发送给 AI，只保留域名（如 `chatgpt.com`、`zhihu.com`），同时发送标签页标题。标题中的未读数量、浏览器后缀会被清洗。

### D18. 平板为辅助数据源  【有效】
**决策**：平板在数据融合中作为辅助数据源，而不是与电脑、手机平等的第三数据源。
**原因**：
- 平板无可靠的 AFK 或触摸检测，亮屏不等于确认使用
- 平板可能长时间保持亮屏（如 PDF 阅读器），此时不应视为活跃
- any_device_interaction 只包含电脑活跃和手机亮屏的并集，不含平板
- 休息判定：只要求电脑 AFK + 手机熄屏，平板亮屏不否决休息仅降低置信度
- 平板亮屏时间不加入 minimum_evidence_seconds（只在电脑和手机均无证据时作为 fallback）

### D19. phone_facts.py 增加 device 过滤  【有效】
**决策**：`phone_facts.py` 和 `tablet_facts.py` 各自按 device 字段过滤事件，避免手机和平板数据相互污染。
**原因**：
- 手机和平板的 JSONL 存在同一 archive 目录
- 不按 device 过滤会导致前台应用事件在设备间错误重叠
- 去重 identity 中加入 device 字段，防止同名事件跨设备去重

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## Obsidian 上下文与行为建议决策（2026-07-28）

==以下决策已经进入当前运行代码和部署配置。==

### D20. Obsidian 是唯一任务权威源 【有效】

**[已由用户确认][已由服务器核实]**

==任务的新增、删除、完成、延期和重排只在 Obsidian/Claudian 侧发生。树莓派只读取同步快照，不回写 Tasks，不自动勾选完成，不修改 scheduled date，也不维护第二份任务状态。==

### D21. 不要求任务 ID 或精确时间表 【有效】

**[已由用户确认]**

==自然语言标题、分类、日期、优先级、番茄钟进度和文件顺序足以支持软建议。系统不检查用户是否严格服从上午/下午或精确开始时间。==

### D22. Windows 只负责确定性导出，Syncthing 负责传输 【有效】

**[已由服务器核实]**

- 导出器：`D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.py`
- 输出：`C:\Users\15345\BehaviorContextSync`
- Windows Syncthing：Send Only
- 树莓派目录：`/home/conrad/workspace/behavior-context-sync`
- 树莓派 Syncthing：Receive Only

==Windows 脚本不使用 HTTP、SSH 或 PUT 向树莓派传输，也不包含密钥。==

### D23. 番茄钟是弱证据，声明时长优先 【有效】

**[已由用户确认][已由服务器核实]**

==番茄钟只表示近期可能主动开始过工作；没有记录不能解释为没有学习，也不能用于判断具体任务进度。工作量使用 `duration` 声明值。`end - begin` 可能包含暂停后继续计时，因此较长墙钟跨度不是坏数据、低效或负面行为证据。==

### D24. 设备行为仍是主要事实源 【有效】

**[已由用户确认]**

==Obsidian Profile、任务计划和番茄钟只参与解释与建议，不能覆盖 `computer_facts`、`phone_facts`、`tablet_facts`、`combined_facts`、`semantic_timelines` 和 `mixing_metrics` 已确定的客观时长。==

### D25. 上下文使用 last-known-good，但陈旧上下文不产生强建议 【有效】

**[已由服务器核实]**

==实时 JSON 缺失、损坏、写到一半或 schema 不支持时，读取模块回退到 `data/context_cache/current.json`。完全不可用时主流程继续；使用旧缓存时不推荐具体任务。==

### D26. 先影子模式，再考虑有限提醒 【有效】

**[已由用户确认][已由服务器核实]**

==`shadow_mode` 保持为 `true`。影子判断会随半小时 PushPlus 核验消息展示，但只写候选、绝不执行干预。至少观察 3—7 天并人工检查误报后，才能另行决定是否启用有限提醒。==

### D27. 影子判断与半小时核验合并发送 【有效】

**[已由用户确认][已由服务器核实]**

==影子判断附加到原有 PushPlus 消息，避免每半小时额外增加一条通知。日报每天 09:00 发送，周报周一 09:05 发送，避免午夜统计通知。所有统计发送保存回执，同周期成功后默认不重复。==

### D28. 全设备无活动时静默并停止 AI 【有效】

**[已由用户确认][已由服务器核实]**

==当电脑没有非 AFK 活动（含没有电脑消息/数据），且手机、平板都没有亮屏证据时：不调用 DeepSeek以节省 token，不发送 PushPlus；但事实层、上下文、本地无活动/休息报告、影子候选和统计仍照常归档。完整版必须继续保留该短路。==

### D29. DeepSeek 失败时降级而不是中断 【有效】

**[已由服务器核实]**

==DeepSeek 返回非法 JSON、请求失败或语义时间线未通过校验时，系统保存设备事实和失败信息，生成低置信度本地报告并继续归档/通知，避免 oneshot systemd 服务整体失败。==

### D30. AI 状态解释及其依据必须可追溯 【有效】

**[已由服务器核实]**

==每个时段保存 AI 报告 JSON/Markdown、语义时间线、混杂指标、实际使用的上下文快照、影子候选和 PushPlus 回执，以便回答“当时 AI 看到了什么、为什么给出该判断”。==

### D31. 过期移动设备状态不得当作当前活动；静默判断必须前置且唯一 【有效】

**[已由用户确认][已由服务器核实]**

==移动设备最后一条屏幕事件只在 `processing.heartbeat_stale_seconds`（当前 2700 秒）内延续；超过该时限且没有新事件时，状态转为 `unknown`，不得把旧“亮屏”无限外推。设备事实生成后立即计算一次全设备静默结果：该结果同时控制是否进入 DeepSeek 分支和是否发送 PushPlus，避免 AI 与通知使用两套不同判断。`unknown` 表示没有当前亮屏证据，不阻止静默，但必须作为数据质量问题归档。==

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 手机异常反馈决策（2026-07-28）

==以下决策已经部署到 `phone-usage-receiver.service`，并已通过 localhost 集成测试和两条真实手机提交验收。==

### D32. 手机反馈只上传分类和说明 【有效】

**[已由用户确认][已由服务器核实]**

==手机 Automate 桌面快捷方式只提交 `category` 与可选 `message`，不提交时间戳、报告编号、设备状态、任务信息或上下文文件路径。接收时间、`annotation_id`、半小时窗口和相关报告/事实层全部由树莓派生成。==

### D33. `/annotation` 复用现有手机上传 token，但使用 Bearer 鉴权 【有效】

**[已由服务器核实]**

==`/annotation` 使用 `/home/conrad/phone_usage/token.txt` 中的现有 token，要求请求头 `Authorization: Bearer <token>`，并用 `hmac.compare_digest` 做安全比较。旧 `/upload/` 数据上传仍使用 `X-Upload-Token`，不得为了反馈功能破坏原协议。==

### D34. 人工反馈是调试标注，不触发自动修复 【有效】

**[已由用户确认][已由服务器核实]**

==反馈记录的 `status` 初始为 `unreviewed`。接收期间不调用 DeepSeek 或其他外部 AI，不读取聊天、通知正文、短信或截图，不自动修改 Profile、ToDo、Prompt、任务计划或系统配置。==

### D35. Raw JSON 是事实记录，Markdown 是派生视图 【有效】

**[已由服务器核实]**

==每条反馈保存为 `data/user_annotations/raw/YYYY-MM-DD/<annotation_id>.json`，使用 UTF-8、临时文件和 `os.replace` 原子写入，文件权限为 600，目录权限为 700。`daily/YYYY-MM-DD.md` 和 `UNREVIEWED.md` 每次从 raw JSON 原子重建，不直接无保护 append。==

### D36. 反馈关联最近已生成的报告，而不是强绑接收时间窗口 【有效】

**[已由用户确认][已由服务器核实]**

==用户通常在读到刚推送的报告后提交反馈，所以 `primary_related_report` 从最近 `ai_reports` 中选择：文件存在、生成/修改时间不晚于接收时间、与接收时间相差不超过 90 分钟、时间上最近的一份。记录仍保留接收时间所在的当前半小时窗口，以及“上一窗口 + 当前窗口”两个候选窗口，方便人工复核。==

<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/ntfy提醒系统配置.md" -->

## 深夜 ntfy 提醒决策（2026-07-29）

### D37. 深夜停止设备使用采用独立确定性策略 【有效】

==`bedtime_stop` 不依赖 DeepSeek，不修改 Obsidian，不属于半小时 AI 影子干预。它只在 `00:30—04:30` 判断手机或电脑是否仍有新鲜活跃证据，并通过 ntfy 发送两层提醒。通用 AI 正式干预仍保持未启用。==

### D38. ntfy 为主通知渠道，PushPlus 不同时发送 【有效】

==深夜提醒主通道为 ntfy，PushPlus 仅保留为明确配置后才可能启用的备用通道。默认不同时发送，避免重复提醒。真实 `NTFY_TOPIC` 只存放在 `/home/conrad/.config/activitywatch-advisor/ntfy.env`，不得写入 Git、README 示例或交接文档。==

### D39. 每次升级前重新检查设备活动 【有效】

==第一层发送后等待5分钟，只有重新检查仍触发时才进入第二层。第二层最多3次、间隔1分钟；每一次发送前也必须重新检查。条件停止或数据过期时立即停止后续升级并回到等待状态。==

### D40. 过期数据默认不升级 【有效】

==`maximum_data_age_seconds` 当前为120秒。电脑 ActivityWatch 或手机心跳/屏幕事实超过新鲜度窗口时，不把旧状态当作“仍在使用”。如果主要数据都不新鲜，状态机记录 `activity_data_stale`，不补发、不连发。==

### D41. 树莓派持久化状态并用文件锁防重复 【有效】

==状态写入 `data/state/bedtime-reminder-state.json`，结构化日志写入 `data/bedtime_reminder/events.jsonl`。状态文件包含 event_id、current_state、level_1_sent_at、level_2_count、last_notification_at、cooldown_until、round_count 和 policy_hash。执行时使用 lock 文件，避免同一分钟多个调度器重复发送。==

### D42. 04:30 后强制恢复白天禁用 【有效】

==窗口外任何状态都会回到 `DISABLED`，不补发旧通知，不恢复旧升级任务。当策略配置变动导致 `policy_hash` 改变时，下一次进入有效窗口会重新初始化事件状态。==

<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/ntfy提醒系统配置.md,非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

## 15:00 任务进度提醒决策（2026-07-29）

### D43. Windows Obsidian 上下文导出必须有独立时间触发 【有效】

==只挂在 LogonTrigger 上的计划任务可能在安装后不进入重复链。当前采用 `Behavior Context Exporter Timer` 作为可靠周期任务，每 20 分钟运行只读导出器，输出到 `C:\Users\15345\BehaviorContextSync`，再由 Syncthing 单向同步到树莓派。原导出器脚本仍保留文件锁和原子写入。==

### D44. 15:00 任务进度提醒只读 Obsidian，不修改任务 【有效】

==`afternoon_task_check.py` 只读取 `context_snapshot.json`、`raw/ToDo-已经规划好的任务.md` 和 `raw/番茄钟log.md`。它不勾选任务、不调整番茄字段、不延期、不重排任务，也不写回 Windows 或 Obsidian。唯一持久化输出是 ntfy receipt。==

### D45. “是否完成一半”同时看任务数量和番茄钟 【有效】

==当天任务由 `⏳ YYYY-MM-DD` 或 `📅 YYYY-MM-DD` 等于当天的 `#task` 定义。`- [x]` 计为已完成，`- [ ]` 计为未完成；番茄钟优先使用任务字段 `[🍅:: 已完成/总数]`，若当天 `番茄钟log.md` 的 40 分钟等价量更多，则用日志兜底。任务完成比例和番茄比例各占一半，综合低于 0.5 时确定性规则认为需要提醒。==

### D46. V4 Flash 只辅助裁决，失败时退回确定性规则 【有效】

==下午提醒会把进度摘要交给 DeepSeek V4 Flash 输出 JSON：`should_send`、`reason`、`confidence`、`suggested_next_action`。模型不可用、超时或 JSON 非法时，不中断流程，直接使用确定性规则；通知文案保持克制，只说明进度和下一步，不责备用户。==

## 已废弃的决策

- **Windows 端用 Python 脚本上传**：因 PowerShell 弹窗问题，改为 Syncthing 同步。
- **整点触发定时器**：因手机上传延迟，改为 08/38 分。
- **第一版单一 AI 调用**：因无法区分语义判断和数值计算，改为两层 AI + 程序中间层。
- **碎片化指（切换次数）**：用户反馈不适用，改为工作-娱乐混杂。
- **AFK 即休息**：用户纠正，改为 AFK ≥ 3 分钟 + 所有设备无活动。
- **用微信公众号回复作为反馈回写**：当前改为手机桌面快捷 `/annotation` 保存人工标注；公众号回复仍不写回系统。

## 待评估的决策

- DeepSeek API 密钥是否需要轮换
- 根据人工反馈扩充或禁用 `config/tag_rules.json` 中的应用/标题规则
- 影子模式观察 3—7 天后，误报率是否足以进入有限提醒
- 是否把 60 分钟历史扩展为 120 分钟，并实现正式提醒冷却期
- ==15:00 任务进度提醒是否应把“预留整个下午的外出/康复/上课任务”单独折算为非番茄任务，避免番茄比例和任务数量比例冲突。==
## 2026-07-29 系统维护超时提醒与半小时提醒检测系统决策

### D47. 系统维护超时提醒属于确定性分类层，不依赖半小时 AI prompt【有效】

系统维护超时提醒由 `sysadmin-time-guard.timer` 每 5 分钟运行一次，直接读取 ActivityWatch 最近 60 分钟电脑前台时间线。它的目标是即时提醒，因此不接入半小时 AI 第一轮语义时间段划分；半小时 AI 仍用于事后解释和核验报告。此次问题定位在 `src/sysadmin_time_guard.py` 的系统维护分类层，而不是 DeepSeek prompt 层。

### D48. ChatGPT/Codex 只在邻近明确维护证据时继承为系统维护【有效】

`ChatGPT.exe` 和 `Codex.exe` 如果与明确系统维护片段间隔不超过 300 秒，则继承为系统维护。明确维护片段包括 Pi/File Browser/Monaco Lite/systemd/journalctl/Tailscale/DNS/ntfy/activitywatch-advisor/树莓派/服务器/运维等应用、域名或标题证据。数学、作业、定理、证明、`math`、`homework` 等排除词优先级更高；含这些词的 ChatGPT/Codex 片段不会因邻近维护而继承。

### D49. 浏览器不得作为通用上下文桥接应用【有效】

浏览器页面必须自身命中系统维护证据才算维护。知乎、普通网页、数学资料不应仅因为靠近维护片段而被继承为维护。此前测试中发现把浏览器加入桥接应用会把一个知乎页面误计为维护，现已收窄为只桥接 `ChatGPT.exe` 和 `Codex.exe`。

### D50. 半小时提醒检测系统是正式名称【有效】

对外通知、回执路径和交接标题统一使用“半小时提醒检测系统”。内部仍保留 `intervention_candidates` / `would_intervene` 作为影子候选计算机制，但 ntfy 只在 `would_intervene=true` 时发送，且不会执行干预或修改任务。
## 2026-07-29：Next Action Web 与下一步行动助手

**状态：有效。**

- 新增“下一步行动助手”作为独立系统部件。它不是半小时行为解读系统的一部分，也不是自动干预系统。
- 决策状态生成器只在用户主动点击网页按钮时运行，不后台自动生成建议，不自动推送。
- 下一步建议使用 DeepSeek V4 Pro，即 `settings.json` 中的 `decision_model`；半小时主流程继续使用原模型配置。
- AI 输出允许较丰富的说服性解释，不再限制为极短命令。建议应包含：行动、时长、第一步、简短理由、数据依据、说服说明、可能阻力、缩小版行动。
- 工作/学习类行动必须匹配当天 Obsidian 任务；树莓派不得创造新任务，不得回写 Obsidian Tasks。
- 番茄钟全局改为中等可靠性正向证据：有记录说明投入过时间；缺失记录不能反推没有学习。
- 第一版执行观察只采用用户手动结果，不根据设备活动自动判定完成或失败。
- 半小时报告继续推送到 PushPlus，同时允许在网页中查看和提交反馈；网页反馈与 Automate 反馈统一进入 `data/user_annotations/`。
- Web 入口通过 Tailscale Serve tailnet-only 暴露在 `https://pi.taild4d3f7.ts.net:8450`，不复用公开 Funnel。
- 睡眠日报改为 09:00/10:00/11:00 重试；11:00 仍无早晨边界时标记 possible_fault。
## 2026-07-29：Next Action v1.1

**状态：有效。**

- 下一步行动助手版本命名为 `next-action-v1.1`。
- v1.1 优先解决建议语言和规则边界，不解决任务标题粒度过大的结构问题。
- 建议语气应温和、具体、有适度亲近感，像熟悉用户节奏的助手，而不是训诫者、心理咨询师或鸡汤文案。
- 说服逻辑应降低启动阻力：承认真实阻力、给出低成本第一步、说明短期具体收益。
- 每天 12:00-13:00 固定为吃饭和午休时间，默认不推荐数学/项目工作。
- 番茄钟数量是预估任务预算或进度标记，不是完成保证；实际需要数量可能大于预估。
- 2026-07-29 修正：本系统中 `1 🍅 = 40 分钟`，不是常见 25 分钟。Next Action prompt、状态 JSON 和输出验证器都必须防止把 15/25/30 分钟启动片段称为“一个番茄钟”。
## 2026-07-30 新增决策

### D34. Next Action Web 增加独立“问题反馈”入口【有效】

**决策**：在 Next Action Web 中新增“问题反馈”页面，用于收集系统问题，而不是继续把所有问题混入下一步建议的“拒绝/换一个”反馈。

**原因**：

- 下一步建议反馈主要回答“这个建议我是否接受、为什么不适合”。
- 问题反馈主要回答“系统哪里有 bug、数据哪里错、规则哪里不合理、网页哪里难用”。
- 两类反馈分开后，后续 Codex 可以直接从 `data/issue_feedback/UNREVIEWED.md` 进入批处理，而不会污染执行效果统计。

**边界**：

- 问题反馈只记录文本、分类、严重程度、当前页面、相关建议 ID 或报告路径。
- 不上传截图，不保存密钥，不暴露原始日志目录。
- 后端只提供登录后的提交和最近列表 API。

### D35. 问题反馈以 raw JSON 为事实源，Markdown 只作视图【有效】

**决策**：每条问题反馈先写入 raw JSON，再由程序重建 daily Markdown 和 `UNREVIEWED.md`。

**原因**：

- raw JSON 便于程序稳定读取、去重和后续批处理。
- Markdown 适合人和 Codex 快速审阅。
- 由 raw 重建 Markdown 可以避免手工编辑视图导致事实源漂移。

### D36. 为 Codex 增加 `pi-ops-system-context` skill【有效】

**决策**：新增本地 Codex skill，专门路由树莓派行为顾问系统相关请求。

**原因**：

- 系统已经跨越手机、平板、电脑、树莓派、Obsidian、Tailscale、DeepSeek、ntfy/PushPlus 和网页，单靠对话记忆容易漏读关键约束。
- skill 会要求 Codex 先读取 canonical docs、reading routes、service map 和 update protocol，再修改系统。
- skill 明确记录 `1 🍅 = 40 分钟`、番茄钟是中等可靠正向证据、Obsidian Tasks 不由树莓派回写、问题反馈 backlog 从 `UNREVIEWED.md` 进入等硬约束。

### D51. 新建议生成必须先完成上一条建议的人工闭环【有效】

==当 `data/next_action/active.json` 指向的建议没有执行结果，且用户也没有明确选择“换一个”或“现在不做”时，后端不得直接生成并覆盖新建议。接口应返回 `409 pending_outcome_required`，网页强制展示上一条建议；用户提交“完成了/正在做/没开始”后，网页自动恢复本次生成请求。==

“换一个”和“现在不做”本身已经明确关闭当前建议，因此不再额外要求执行结果；“开始”只表示接受，仍需后续填写结果。

### D52. 主动点击“生成建议”是用户已醒的直接交互证据【有效】

==Next Action 是用户主动触发的网页请求。能够点击按钮即足以证明用户已经醒来并能交互；睡眠日报中的早晨边界即使仍为 pending，也不得促使建议系统询问“是否起床/是否醒来”。==

该规则同时进入决策状态、模型 prompt 和确定性输出验证器；若模型仍返回此类 `clarify`，后端拒绝模型输出并使用安全 fallback。

<!-- ai_provenance: source=codex; date=2026-07-30; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->
## 2026-07-31 电脑端 Cold Turkey 介入决策

==半小时系统可以从影子候选生成电脑端介入请求，但 Pi 端只负责判断、归档和提供 API，不远程执行任意 Windows 命令。Windows agent 以拉取方式获取 pending request，执行前必须用本地 allowlist 校验 block 名；当前仅允许 `常刷网站` 与 `bilibili`。==

==用户连续两次点击“不介入”后，第三次仍触发时强制执行 30 分钟 Cold Turkey 介入；点击介入、强制介入成功、agent 判断目标已处于封锁状态、观察到有意义活动恢复或确认休息，都会重置拒绝计数。弹窗超时未响应记为 `ignored`，不计入连续拒绝。==

==B 站 block 在周六全天、周日全天、周一 00:00-12:00 Asia/Shanghai 作为备课例外，不执行封锁且不计入拒绝。电脑 ActivityWatch 无活动不阻止介入请求生成；手机/平板沉迷也可以触发电脑端 Cold Turkey 封锁。==

<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D64. 暂停是一次定时的锁机租约，而非手动恢复按钮【有效】

==暂停前必须输入并确认 1—120 分钟。Pi 保存唯一暂停记录和截止时刻，先经既有 Windows agent 停止 Cold Turkey，再由后台 reconciler 在截止时自动重新下发电脑锁定；网页或 Obsidian 不在线也不影响恢复。手机 Quick Pomodoro 尚无远程暂停接口。暂停一次即永久标记该 session 按半额成长与番茄结算，不能通过提早点“继续”规避。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

### D62. 番茄锁定是 agent 托管的可撤销 lease【有效】

==New Pomodoro Timer 不拥有第二个锁机 agent；它只通过 Pi 发送结构化 start/release 请求给既有 Windows `computer-intervention-agent`。该 agent 对 allowlist block 执行 Cold Turkey `-start <block>` 与 `-stop <block>`，禁止为番茄钟使用 `-lock` 硬锁。==

### D63. 一次暂停换取半额成长【有效】

==每个 Focus Garden session 最多暂停一次，暂停分钟数为显式输入。暂停阻止结算并请求释放电脑 lease；恢复会重启同 profile 的 allowlist。只要使用过暂停，整轮最终有效专注分钟、植物积分和关联任务番茄积分统一按原计划时长的 1/2 结算。==

### D65. Cold Turkey lease 必须由 agent 按绝对时间回收【有效】

==普通半小时介入与 Focus Garden 专注均保留可暂停的 `-start/-stop` lease，不使用 Cold Turkey `-lock` 计时。Windows agent 持久化 `lease_id` 与 `lock_until_estimated`，在启动、轮询和唤醒后的第一次循环执行过期回收；因此休眠不会让解锁依赖某一个瞬时轮询。==

==Pi 的 release 命令是 durable pending，必须等 Windows agent 对匹配 lease 返回成功或安全的 `lease_superseded` 后才标记完成。release 请求不受普通 180 秒 TTL 限制，并按稳定 ID 去重；旧 lease 的 release 不得关闭新的 lease。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D68. 健康面板只聚合状态和新鲜度，不读取用户内容【有效】

==“系统状态”页只可汇总固定服务的 active/inactive、任务 queue 数量、快照/备份的更新时间、以及 Windows/Android bridge 的心跳年龄。它不得返回 Tasks 标题、Obsidian 正文、原始行为事件、token、cookie 或任意可执行指令；Pi 不因该面板而获得修改 Markdown 或 Windows 的权限。==

### D69. Windows agent 采用计划任务启动并提交独立心跳【有效，取代 D56】

==`ComputerInterventionAgent` 在用户登录后的交互会话中通过 `pythonw.exe` 启动，保留 Tk 弹窗能力。它每 5 分钟向固定的 `/api/computer-interventions/heartbeat` 写入在线状态、版本、最近轮询状态和活跃锁定数量；heartbeat 仅用于可观测性，失败不阻断正常 pending request 轮询。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

### D62. 任务网页采用 Pi 意图队列、Obsidian 单写者【有效；取代 D20/D21 的相关部分】

==网页新建、编辑、推迟和完成操作先写入 Pi 的持久化 mutation queue，并立即覆盖 Next Action 的有效任务视图；只有 Obsidian Pi Context Sync 插件能修改三个任务 Markdown。插件写入后运行导出器，且仅当 Pi 收到具有匹配哈希的新快照时确认并删除 queue 项。这样关闭 Obsidian 时网页仍能立即影响建议，同时不存在 Pi 与本地 Markdown 双写冲突。==

### D63. 任务 ID 统一采用 Obsidian block ID【有效】

==新任务使用行末 `^xxxxxxxx` 的 8 位小写字母数字 block ID；New Pomodoro Timer 叉在创建任务时生成同一格式。保留既有短 block ID，避免破坏历史块链接。==

### D64. 任务桥接保持本地与 tailnet 边界【有效】

==advisor 的任务 API 仅监听 `127.0.0.1:8767`，只接受 Obsidian 插件或 Focus Garden 固定 bridge header；花园仍经现有 tailnet-only Serve 访问。不得为任务同步新增 Funnel、端口或让 Pi 直接访问 Vault。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

### D68. 正式专注只允许固定时长，连续休息不解除锁机【有效】

==手动和预约专注只接受 5、10、20、30、40、45、60 分钟；连续专注只接受 30、40、45、60 分钟，且显式选择休息时间和轮数。电脑与手机的既有锁机均不提供提前解除：连续模式在每轮专注开始时发起新的锁定，休息时只记录阶段，不绕过或撤销已有锁定。==

### D69. 手机桥接以无障碍服务心跳作为可用性证据【有效】

==Android 无障碍服务每 5 分钟向 Focus Garden 的固定私有 API 写入 `android-main` 心跳；20 分钟未见心跳即视为暂停，并在下一次加载花园网页时显示一次简短提示。心跳仅反映桥接可用性，不证明手机锁机已成功执行；实际执行仍以事件回执和本地日志为准。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D69. Next Action 免密码必须与 Tailnet-only 边界配套【有效】

==Next Action 不再要求独立网页登录密码，但仅可经既有 Tailscale Serve `:8450` 或专注花园 `:8460` 访问。撤销密码时必须同步撤除公网 Funnel；不得把 8767/8838 绑定到非 loopback 地址，也不得以“方便访问”为由重开 `:10000`。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D68. 花园合并 Next Action 时只可调用同 Pi 的固定 loopback 接口【有效】

==花园服务仅可向 `127.0.0.1:8767` 转发明确列出的 Next Action 路由，并只透传用户浏览器已有的登录 cookie；不得保存密码、读取 Next Action 私有配置/归档、接受任意上游 URL，或改变 Tailscale Serve/Funnel 边界。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/树莓派 Next Action Web架构.md" -->

## 2026-08-03 我的专注花园 Pi 迁移决策

### D65. Pi 是唯一正式写入端【有效】

==权威数据库只由 Pi 的 `focus-garden.service` 写入。电脑通过网页使用同一实例，不让两个活跃进程直接同步或同时写 SQLite；Windows 原项目只保留为开发与恢复副本。==

### D66. 存档以一致性快照单向同步【有效】

==定时任务使用 SQLite backup API 把 WAL 状态合并为原子快照，再经 Syncthing 从 Pi send-only 同步到 Windows receive-only，并在接收端保留 staggered 历史版本。不得把活跃 SQLite 改为双向文件同步。==

### D67. 私有访问只使用 Tailscale Serve【有效】

==应用保持 loopback 监听，8460 仅为 tailnet-only Serve；不得为专注花园启用 Funnel、公开反向代理或 `0.0.0.0:8838`。受版权保护的素材只在 Tailnet 内提供，且不进入存档同步目录。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/02-游戏架构.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

## 2026-08-03 我的专注花园交接决策

### D61. 运行真相与交接文档分离【有效】

==交接文档与运行数据保持分离；`工作流程与系统运维/我的专注花园/` 只保存可审计交接，不复制数据库、密钥、token 或贴图。迁移后运行与存档事实源在 Pi，`D:\MyFocusGarden` 是开发和恢复副本。交接入口为 [[我的专注花园/00-交接总览]]。==

### D62. 植物注册使用稳定 ID，视觉素材可替换【有效】

==可种植对象由 `config/plants.json` 注册并按 `flower`、`tree`、`mushroom` 分类。历史种植记录只保存 `species_id`，因此替换贴图时保留 ID，不改历史数据库；蘑菇在种植弹窗中保持独立标签页。==

### D63. 花园随机位置必须可复现且只能消费一次奖励【有效】

==位置选择以 `reward_id + species_id` 的哈希作为固定随机种子；SQLite 事务、`reward_id` 唯一约束和坐标唯一约束共同保证一份奖励只能种一次。花园仅在所有格子填满后按奇数边长扩展。==

### D64. 当前第三方贴图继续限个人私有环境使用【有效，待原创替换】

==当前目录含 Minecraft Education Edition、本机 Steam 游戏 Mushroom Nook 和用户提供的草方块贴图。它们只可存在于个人 Windows 与私人 Pi，不得上传公网、分享或随代码分发；Git 排除规则必须覆盖 mushrooms、blocks 和其他非原创素材。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/01-数据来源与处理.md,非笔记内容/工作流程与系统运维/我的专注花园/02-游戏架构.md" -->

## 2026-08-02 我的专注花园决策

### D57. 游戏保持 Windows 本地优先，不新增树莓派公开服务【已被 D65—D67 取代】

==这是迁移前决策。现已改为 Pi loopback + tailnet-only Serve，仍不启用 Funnel 或公网 API；正式读取改为 Pi 本地只读聚合。==

### D58. 奖励必须由确定性事实和稳定 ID 产生【有效】

==主动介入只奖励 `accepted + execution success`，排除 `forced/ignored/already_locked/skipped`；AI 完成必须在同一 `suggestion_id` 上同时存在 `accepted` response 与 `completed` outcome；早睡只作为手机停止使用估计，不宣称为真实入睡。所有奖励进入本地 SQLite 并以源事件 ID 去重。==

### D59. 自愿专注复用 Cold Turkey allowlist【有效】

==游戏不得执行任意 block 或任意 shell 命令，只允许调用现有 computer-intervention-agent 配置中的 allowlist。开发和自动测试必须设置 `FOCUS_GARDEN_DRY_RUN=1`，不得为了验收真实锁定网站。==

### D60. 第一版原版贴图只限本地且禁止进入版本控制【有效，待替换】

==第一版从本机已安装的 Minecraft Education Edition 复制 20 个植物 PNG；这些文件加入项目 `.gitignore`，不得上传、分享或分发。第二版保持植物 ID 和注册接口不变，逐步换成原创素材。==

### D62. 关联任务的番茄进度必须来自完成的同一条专注会话【有效】

==Focus Garden 的全局专注奖励与任务 🍅 是两个独立账本。只有带有有效 Obsidian block ID 的完成会话才进入该任务的 40 分钟累计；无关联专注、其他任务的专注、取消/失败会话均不得贡献该任务的番茄。达到 40 分钟后，Pi 只排队一个带稳定 session ID 的绝对 `target_completed`，Obsidian 插件以 `max(当前值, target)` 写入，保证重试幂等且不覆盖人工更高进度。==

### D63. New Pomodoro Timer 是 Focus Garden 的桌面入口，不是第二个记账者【有效】

==工作段开始时，New Pomodoro Timer 只通过 Pi 的 tailnet-only `:8460` 创建同一条 Focus Garden 会话，默认时长 40 分钟，默认锁定电脑＋手机。用户可选择仅电脑、仅手机或仅计时；不锁机时不发送设备介入。插件不得自行增加 `[🍅::]`，所有任务写回仍由 Pi Context Sync 在打开 Obsidian 后完成。==

<!-- ai_provenance: source=codex; date=2026-08-02; verification=user-confirmed; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D53. Cold Turkey 自动开启由 Windows 本地 agent 执行【有效】

==Pi 端只生成结构化介入请求、保存回执、提供登录后 API；不下发任意 shell 命令，也不直接远程控制 Windows。Windows agent 拉取请求后，只能执行本地 `allowed_blocks` 中预先配置的 Cold Turkey block。当前 allowlist 仅包含 `常刷网站` 与 `bilibili`。==

### D54. 忽略等同于“暂不介入”的完成请求，但不累计拒绝【有效】

==弹窗超时或 UI 无法显示时返回 `ignored`。它会把当前 request 标记为完成，避免同一请求反复弹出；但 `decline_streak_after` 保持不变，不触发“两次不介入后第三次强制”的累计。==

### D55. 弹窗必须适配高 DPI 并保持底部操作可见【有效】

==Windows Tk 弹窗必须显式设置 DPI awareness；主体内容允许滚动，底部倒计时与“暂不介入 / 介入 30 分钟”按钮固定可见。若字体、系统缩放或触发原因文本导致内容变高，也不得遮挡操作按钮。目标名需使用 `display_name` 兜底，避免中文 block 名在测试或编码异常时显示成 `????`。==

### D56. 当前 agent 运行方式是普通后台进程，不是持久化服务【有效，待改进】

==当前运行命令为 `D:\anaconda\python.exe D:\tools\computer-intervention-agent\agent.py`，由用户会话中的后台进程承担。重启 Windows、注销用户或进程退出后不会自动恢复。后续若要长期依赖该模块，应安装 Windows 计划任务或服务，并加入定期心跳/健康检查。==

### D61. 锁机启动失败采用有限、显式的重试【有效】


<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

## 2026-08-06 近期动态决策

### D70. 用户原文是近期动态的唯一权威来源【有效】
==content/impact_text 由用户输入并原样保存；AI 解析只写 parse 辅助字段，不得改写原文；created_at 服务端生成不可修改；编辑时更新 updated_at/confirmed_at 并重新解析。==

### D71. 相对时间一律以 recorded_at 为基准【有效】
==解析 prompt 强制以记录时间为基准解释「今天/明天/本周/下午」，不得以模型调用时间重新计算；daypart 只给日期粒度，不伪造精确小时作为过期边界。==

### D72. 条件型记录不自动过期，但需要确认【有效】
==event/open/vague/解析失败按 conditional 处理；超过 review_after_days（默认 14 天）后 needs_review=true，仍在页面显示但不进入 AI 上下文（置顶不能绕过）；「仍然相关」更新 confirmed_at。==

### D73. 近期动态 API 只接受 loopback + X-Focus-Garden-Bridge【有效】
==/api/recent-context* 全部要求来源为 127.0.0.0/8 或 ::1 且带固定 bridge header，不允许全局免密兜底；花园是固定白名单代理，不持有、不直接读写 state.json。写接口必须携带 expected_revision，冲突返回 409。==

### D74. 数据处理 AI 失败不影响 Next Action【有效】
==解析失败只保存 error；筛选 AI 超时/非法输出按本地规则降级（fallback_used=true）；state.json 损坏返回 503 并保留 .corrupt 副本，不回退空状态、不覆盖损坏文件。==

### D75. recent_context_used 只保存并校验候选 ID【有效】
==最终模型只能引用本次传入的 selected/forced ID；虚构 ID 被剔除；页面按 ID 反查用户原文展示。prompt 版本：next-action-v1.3 / recent-context-parse-v1 / recent-context-selector-v1。==

### D76. 手机控制关键链路不得依赖 Tailscale【有效】

==Focus Bridge 的 pending、heartbeat、decision、event 默认经 `https://pi.taild4d3f7.ts.net/focus-bridge/*` 公网 HTTPS 固定白名单路径访问 Pi；每台设备使用仅保存在应用私有目录与 Pi `0600` 文件中的独立 Bearer token。Tailnet `:8460` 只允许作为公网 IOException 后的备用。这样 Clash 与 Tailscale 的 Android 单 VPN 互斥不会中断手机控制。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=android-device-and-pi-verified; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D77. 未安排网页任务以 collection 分区为权威入口【有效】

==网页新增且没有 `⏳` 的任务必须保留 block ID，写入 `ToDo-任务集合.md` 顶部的 `# ⚠️ 树莓派新增 · 待正式安排`；不假装已经安排，也不丢弃到普通文本。填写真实安排日后，桌面唯一 Markdown 写入器将同一行（同一 ID）移至 `ToDo-已经规划好的任务.md`。删除同样只通过 queue 请求桌面写入器完成。==

### D78. 影响时段优先保留用户表达的精度【有效】

==仅有日期的区间保持日期精度；原文明示时分的区间才保存分钟级 ISO 时间与 `+08:00`。代码只能做确定的状态和窗口比较；自然语言无法可靠判定时，交给 `deepseek-v4-flash` 的非思考 JSON 解析，失败则保守标为 vague/conditional，绝不补造小时。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-and-pi-tests-plus-live-endpoints; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D79. Next Action 澄清最多两轮，接受永远指向最后行动版本【有效】

==澄清不是开放聊天：每个 active suggestion 最多接收两条用户澄清，每条产生一个新的 action revision。第二轮必须收到完整的第一轮 `user_message + assistant_message + resulting_action`，使上下文连续而仍受两轮和字段长度限制。浏览器必须提交其看到的 `expected_action_revision`；服务端只在该 revision 等于 active 当前 revision 时记录 accepted，并持久化实际接受的 `action_id/revision`。因此第一轮、初始建议或过期标签页都不能被误当作最后一轮接受。澄清固定复用初始建议的 V4 Pro 思考模型，最终建议仍受既有任务标题、时段和番茄钟规则校验。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=targeted-unit-test-plus-pi-loopback; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/树莓派 Next Action Web架构.md" -->

### D80. 手机介入采用“锁屏等待 2 分钟 + 解锁后 10 秒原生选择页”【有效】

==offer 生命周期由前台桥接服务统一管理：锁屏期间不强行弹 Activity，只检查设备可交互状态；解锁后通过已连接的无障碍服务启动应用内介入页。页面只提供接受、拒绝和 10 秒超时，重新锁屏会撤下页面并恢复等待。超时记为 `ignored`，决定先持久化再提交，提交成功前后续 pending 快照不得覆盖。无障碍服务不可用时保留通知操作作为降级入口，不引入 Automate 或第三方唤醒链路。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=user-confirmed-plus-device-and-pi-event; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/专注花园桥接手机APP.md" -->

### D81. release 必须有可验证 lease，清理以归档和终态为准【有效】

==任何缺失 `lease_id` 的 release 都不得调用 Cold Turkey `-stop`：它无法证明属于当前锁，必须作为 legacy 记录隔离。Pi 对创建超过 10 分钟的无 lease release 自动移入私有 archive，保留原始 JSON；新 API 不再生成这类请求。==

==带 `lease_id` 的 release 是解锁补偿命令，不以任意 TTL 删除。只有 Windows Agent 回传 final（实际 released 或安全的 ownership 不匹配）后，Pi 才将该 request 从派发目录移入 completed archive。因而自动清理的依据是“无法匹配任何 lease”或“已经获得终态回执”，不是猜测电脑是否在线。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=windows-and-pi-tests-plus-live-queue-check; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D82. 闲鱼固定为购物，不能构成娱乐偏离【有效】

==闲鱼（网页标题/idlefish 域名、应用名或 `com.taobao.idlefish`）必须被 deterministic tag rule 锁定为 `shopping`，并以独立边界进入语义时间线。购物不是娱乐、也不是休息或工作；它保持时长可见，但不进入 entertainment minutes、娱乐偏离或工作—娱乐转换，因而不得单独或与前后工作段共同触发 `work_entertainment_alternation`。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=pi-targeted-tests-and-replay; retrieved_notes="非笔记内容/工作流程与系统运维/DECISIONS.md" -->

### D83. 迁移以可编辑源码、声明式重建和分离私有状态为准【有效】

==不把系统打成不可编辑镜像或容器作为主迁移方式。代码、依赖清单、systemd 单元、端口与 Tailscale 路由由本地 Git、清单和 Ansible 重建；运行数据、令牌和受版权约束素材走独立加密备份。新设备先恢复到隔离目录并验收，原 Pi 继续作为唯一生产写入端，直到明确切换。==

### D84. Minecraft 来源素材永不进入公开发布链路【有效】

==`static/assets/{plants,mushrooms,blocks}` 不得被 Git 跟踪、不得进入可公开的源码快照、网站部署或公开远程。私有编辑副本可以保留素材以维持预览能力，但必须依赖 `.gitignore`、pre-push 拦截和发布前检查；迁移时只能通过私有加密 Restic 仓库恢复。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=implemented-and-guard-tested; retrieved_notes="Pi live repositories and copyright asset audit" -->

### D85. 客户端迁移采用“可编辑 Git bundle + 可安装构建 + 分离秘密”【有效】

==每个客户端 release 必须包含可恢复完整历史的 Git bundle、构建/任务参考、脱敏配置模板和 SHA-256 清单；APK 只是快速安装副本，不能代替源码。`CURRENT.json` 只在验收后指向新版，旧 release 保持不可变。设备 token、上传 token、密码、SSH/Syncthing 身份和用户数据只进加密私有备份或在新设备重建。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=implemented-and-release-verified; retrieved_notes="Pi client migration release 2026.08.07-r1" -->

## 2026-08-08 Next Action 召回与任务时间决策

### D86. 近期动态先宽召回，再由 Flash 进行可审计的有限筛选【有效】

==代码粗筛最多保留 30 条；`deepseek-v4-flash` 以 thinking enabled、请求 `reasoning_effort=low` 筛选最多六条。它必须看到逾期一天、今天、明天与后天的任务投影，并返回有序 ID、relevance、direct/preparation/conditional、importance、关联任务和摘要。最终 V4 Pro 只接收该保留顺序；强制动态在模型前占位，超额 forced ID 必须留存审计。==

### D87. 任务时间窗只影响建议锁定，不修改 Obsidian 原任务【有效】

==标题中明确的时间范围仅被只读解析为 upcoming/active/between_windows/elapsed；当天最后窗口结束后不再把该任务放进 `today_task_titles`，但原任务、循环投影和 Obsidian 写入边界均不变。仅取消 Next Action 最终输出的番茄钟文本拒绝器；Prompt 的 `1 🍅 = 40 分钟` 及其他报告、统计和结算规则不得删除。==

<!-- ai_provenance: source=codex; date=2026-08-08; verification=56-targeted-tests-plus-production-source-hash; retrieved_notes="PI_SERVER_HANDOFF.md,我的专注花园/树莓派 Next Action Web架构.md" -->

### D88. Agent 崩溃恢复由独立 Watchdog 和预写 lease 共同保证【有效】

==`ComputerInterventionAgent` 不能成为可暂停 Cold Turkey lease 的唯一计时器。每个允许自动停止的 block 必须在 `-start` 前持久化同一 `lease_id`、block 和绝对到期时间；重启后的 Agent 只可对仍由该 lease 所有的 block 执行 `-stop`。UI 必须运行于可丢弃子进程，不能把 Tk/Tcl 生命周期放在后台核心中。==

==Windows 采用三层恢复：主计划任务在失败时重试；常驻 Watchdog 检查本地心跳；独立两分钟 kick 在常驻 Watchdog 缺席时继续检查。UI 等待期间显式发布 `busy_until`，避免正常 90 秒选择页被误杀。连续重启采用 0/30/60/180/300 秒退避；恢复后先 reconcile persisted lease，才处理新的 pending request。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=windows-unit-tests-and-live-crash-recovery; retrieved_notes="DECISIONS.md" -->

### D89. 循环任务按日期实例完成，每日满番茄奖励独立结算【有效】

==网页完成循环任务时，Pi 必须先以 `task_id@YYYY-MM-DD` 幂等记录本次实例，再复用现有 `update` mutation 推进 Obsidian 模板；不得让 Pi 直接写 Markdown，也不得新增第二套插件写回协议。当前只允许精确的 `every week on <weekday>`，其他循环表达式安全拒绝。完成实例保留在“今天”，但从开放任务和 Agent 输入排除。==

==每日挑战采用当天计划番茄数的单调快照，并仅在次日 04:10 后结算。`planned >= 7 && completed >= planned` 时按日期只发一次独立高级种植权益；该权益不是 3 个普通奖励，也不能种普通植物。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=pi-unit-tests-and-live-service-check; retrieved_notes="PROJECT_STATE.md,PI_SERVER_HANDOFF.md" -->

### D90. 手动手机锁机以绝对截止时间和可配置梯次为准【有效】

==手动专注必须下发绝对 `focus_deadline_at` 与本次允许档位快照；Android 在首次实际尝试前选择与剩余时间距离最小的非负档位，精确中点取较长档。phone 与 windows 的 release 使用不同 request ID，手机 release 同时 supersede 原 execute ID。==

<!-- ai_provenance: source=codex; date=2026-08-10; verification=unit-and-integration-tested; retrieved_notes="PROJECT_STATE.md,我的专注花园/专注花园桥接手机APP.md" -->

### D91. 累计推迟 2 天即视为拖延，并优先进入 Next Action【有效】

==只有 Focus Garden 的显式“推迟一天”操作累计拖延天数；普通编辑安排日期不计入。累计向后移动达到 2 天后，任务标记 `procrastinated=true`，在清单与日历显示“拖延 · N天”。计数保存在 Pi task-sync 状态中，不写入 Obsidian；完成或删除任务时清除。旧版本没有可靠历史，禁止凭当前日期反推过去推迟次数。==

==存在仍可行动的拖延任务时，Next Action 的 task 类型建议必须先从拖延任务中选择并说明累计推迟天数；模型输出违反该规则时由校验器拒绝并 fallback。午休、深夜睡眠等非 task 硬规则继续优先，表达不得羞辱或道德评判。==

<!-- ai_provenance: source=codex; date=2026-08-12; verification=pi-tests-services-and-tailnet; retrieved_notes="PROJECT_STATE.md,PI_SERVER_HANDOFF.md,我的专注花园/树莓派 Next Action Web架构.md" -->


### D92. Steam 使用是确定性娱乐事实，超过 5 分钟直接触发本轮电脑介入【有效】

==Steam 客户端、Steam 商店和已识别 Steam 游戏必须由 tag rule 锁定为 `entertainment`，不能交给语义模型改写。Steam 时长只累计当前半小时 report scope，阈值采用严格 `> 5` 分钟；每次 08/38 分定时检查中，只要本窗口越过该阈值，就以独立原因 `steam_activity` 令 `would_intervene=true` 并生成 `steam游戏` 目标，不再要求高刺激或工作—娱乐切换等第二个理由。连续触发沿用 Pi 共享介入状态机，第二次拒绝即转 forced；相邻窗口保留拒绝计数，距上次拒绝达到 90 分钟、恢复至少 20 分钟有意义活动或 10 分钟确认休息时重置。forced Steam 执行前必须提供 60 秒不可取消的本地存档倒计时。==

### D93. Steam 夜间收尾使用 Cold Turkey 硬锁，专注与半小时锁仍使用可回收 lease【有效】

==Windows Agent 每日 23:30 弹出 60 秒收尾框：用户可立即关闭配置中精确路径对应的游戏并获得一次普通植物奖励，或按 15 分钟档延时，最晚只能选到次日 01:00；倒计时无操作或延时到点后先保留 60 秒存档时间，再关闭该游戏并以 Cold Turkey `-start "steam游戏" -lock <minutes>` 硬锁到 12:00。夜间硬锁不能由 Agent 中途 `-stop`，避免被本地流程提前解开。半小时强制锁和 Focus Garden 专注锁仍按 lease 所有权建立与回收；旧 release 不能解除更新的 lease。==

### D94. 中午后的 Steam 解锁以“达到 5 个实际完成番茄且当天主要任务已完成”为双门槛【有效】

==任务清单只允许今天和明天各设一个主要任务；标记只保存在 Pi task-sync 状态，不写入 Obsidian Markdown。按钮位于原四个操作按钮上一行的右侧，同一按钮再次点击取消，同日改选则替换。当天完成任务所授予的番茄达到 5 个，并且当天主要任务已经完成，`steam_unlock_gate.eligible` 才为 true；一项任务整项完成时一次性按其 `tomatoes_total` 授予，未完成任务的 `tomatoes_completed` 中途进度（如 `2/4`）不计入，指标封顶显示为 `5/5`。否则 Windows Agent 每分钟续上 5 分钟 Cold Turkey 硬锁，Pi 暂时不可达也按未满足处理。Next Action 只把主要任务作为拖延、时段与健康等既有规则之后的软性排序依据，不得压过硬规则。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=implemented-ui-verified-and-targeted-tested; retrieved_notes="PROJECT_STATE.md,PI_SERVER_HANDOFF.md,我的专注花园/02-游戏架构.md" -->

### D95. 执行效果使用周级状态机，不使用综合自律分【有效】

==系统只把数学产出与延期债务视为结果，把工作、娱乐、Next Action、系统使用、恢复和 AI 视为诊断。主指标固定为 M、D、W、L、A、F、U、R；不计算 R_c。D 只读取用户显式推迟产生的 `postponed_days`，不从截止日期或安排日期猜测拖延。每天只采集，周级只选择一个主状态和一个调整并冻结七天；Steam、Focus 等硬规则不由识别器自动修改。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=implemented-pi-ui-and-timers; retrieved_notes="PROJECT_STATE.md,PI_SERVER_HANDOFF.md,我的专注花园/系统层控制&识别系统执行效果.md" -->

### D96. 手动同步只更新事实，不改写冻结中的周决策【有效】

==“同步状态”可以更新当天 D 和当前八项聚合，但不得重算或替换冻结期内的状态、证据、唯一调整与截止时间。实时数据与周决策分别保存；新的正常周评审产生时废弃旧实时快照。该按钮不是缩短七日冻结或触发参数调整的入口。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=implemented-and-tailnet-verified; retrieved_notes="PROJECT_STATE.md,PI_SERVER_HANDOFF.md,我的专注花园/系统层控制&识别系统执行效果.md" -->

## 2026-08-31 目标模式决策

### D97. Goal Agent 与 Next Action 是两个独立功能【有效】

==Goal Agent 负责长期目标距离、证据置信度、月/周计划和策略调整；Next Action 只负责当下行动推荐。两者使用独立提示词、模型配置、聊天记录、SQLite 和审计历史，不允许把目标聊天伪装成 Next Action。联动只发生在共享任务、稳定 `task_id` 和完成证据层。==

### D98. 目标进度按轨道和证据维度呈现，不计算单一综合百分比【有效】

==专业课、数学所笔试、遍历论和抽象代数分别显示内容覆盖、真实题源掌握、周执行、最近吞吐量、证据置信度与未知/正常/有风险/偏离。少于三周可比数据、课程考核比例未知或题源不足时必须保持“未知/待核验”。40/20/30/10 是资源权重，不是伪精确总分。==

### D99. 推荐日由用户确认后才写入任务系统【有效】

==周任务先进入本周池；Goal Agent 可以推荐日期，但只有用户点击确认后才提交 task-sync mutation。Pi 不直接修改 Vault，桌面 Obsidian 插件仍是唯一 Markdown 写入者，新快照确认后才标记同步完成。==

### D100. 自动调整按影响范围分级【有效】

==同月周任务、推荐日、任务拆分和低价值事项顺序可自动修改并立即生成计划版本；总目标、截止日期、资源权重、每日容量范围和重大跨月移动必须创建 ApprovalRequest。所有修改都保存原因、证据、前后差异和可回退快照。==

### D101. Goal 写请求必须幂等且使用乐观并发【有效】

==所有写请求带 `request_id` 和 `base_plan_version`。重复请求返回原结果；版本不一致返回 409，整个操作不部分应用。回退本身生成新版本，不删除原版本。==

### D102. 学习资料采用逐项授权、最小提取和单向同步【有效】

==Windows 导出器只处理资料清单中已勾选、位于 Vault 内的 PDF/Markdown/文本；保存页码、来源路径、修改时间和 SHA-256，并剥离 MathInk 笔迹载荷与内嵌 base64。Pi 通过 SQLite FTS 检索当前判断所需片段，不接收整个 Vault。==

### D103. 外部来源分级且 Tavily 查询不得包含私人信息【有效】

==A 级官方来源可在确认后改变硬要求；至少两个独立来源互证的 B 级材料只能调练习策略；C 级单一帖子只待核验。Tavily 只搜索公开招生和导师信息，查询不得含个人成绩、简历或笔记正文。往届规则在 2028 级正式通知发布前始终标为参考。==

### D104. 开学杂项不进入目标模式【有效】

==作息统计、批量教材转 Markdown、人文课抢课、额外开学自学安排和夜间固定 Agent 工作制明确排除，不占四轨道预算，也不进入 Goal Agent 提示词或资料检索。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=user-scope-and-production-behavior-checked; retrieved_notes="计划模式/00-目标模式总览与方案设计.md,计划模式/01-整体架构与数据流.md" -->

### D105. 本学期课程进度只由用户确认，不从笔记时间或课时表推断【有效】

==概率论、泛函分析和微分几何每周由用户选择实际讲到的小节，并逐项填写 0–3 掌握度。Goal Agent 可以读取授权笔记生成复述、证明重建和当前章节习题，但文件修改时间、笔记数量和大纲学时不得自动解释为“已学完”。未填写授课进度的课程任务保持 awaiting_course_progress，不能写入 task-sync。==

### D106. MathInk 只向 Goal Agent 暴露 AI 可读投影【有效】

==普通 Markdown、LaTeX、`inkedmark-text` 忠实识别段、分页识别文字和标准相对图片引用可以进入资料索引；压缩笔迹、base64、图片二进制和 `mathink:image` 布局坐标必须移除。手写占位符或图片路径本身不是掌握证据。目录递归继续排除 `.ink.md`、冲突文件、隐藏目录和临时文件。==

### D107. 仅 Goal Agent 使用 GPT-5.6 Sol，且不回退到 DeepSeek【有效】

==Goal Agent 固定使用中转站 `gpt-5.6-sol`、Responses API、`medium` 推理和独立 `GOAL_AGENT_API_KEY`。JSON Schema 不兼容时，只允许同一模型/同一 Responses 协议的提示词 JSON 契约回退。模型失败时保留确定性功能，不切换 DeepSeek。Next Action、行为报告、语义分析等既有路由不随之改变。==

### D108. 课程/资料迁移不得覆盖已确认任务或历史计划【有效】

==v1→v2 只改动未确认日期且没有 plan_item_task 映射的任务。已写入任务系统的任务必须保持原样；数据库迁移生成新 plan version 并保留 v1。普通回退通过版本系统完成，不能用旧 SQLite 覆盖新的反馈、聊天和版本。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=production-schema-tests-and-tailnet-api; retrieved_notes="计划模式/01-整体架构与数据流.md,计划模式/05-v2课程进度与GPT-5.6迁移验收.md" -->

### D109. 电脑 Tailnet peer 不得作为网络故障触发条件【有效】

==电脑可能被带走、关机或休眠。Pi 只根据本机默认路由、IPv4 204 与 IPv6 HTTPS 判断网络是否失效；Windows peer 只作诊断，不参与自动切换。只要 UCAS 外网正常，电脑不在场时不得切换热点。==

### D110. 自动热点回退使用双栈连续失败与冷却【有效】

==Pi 每 30 秒检查一次，只有 IPv4 和 IPv6 连续 4 次均失败或没有默认路由时，才尝试 `netplan-wlan0-XYH 0563`。热点激活失败立即恢复 UCAS并冷却 10 分钟；热点健康时保持，连续两次失去外网才恢复 UCAS。手动其他 Wi-Fi 不被覆盖。==

### D111. 固定 UCAS BSSID 前必须先有真实可用回退【有效】

==当前不固定 BSSID。电脑热点由用户按需开启，相关脚本、Pi profile、自动切换失败恢复、自动回切和触屏手动按钮均需保留。只有热点开启时的真实往返验收通过，并依据长期监测选择出稳定 AP 后，才允许固定 BSSID。固定后 AP 离线会失去漫游能力，因此仍必须保留 hotspot profile 和本地按钮。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=real-hotspot-switch-and-computer-away-test; retrieved_notes="树莓派UCAS无线漫游与电脑热点自动回退.md" -->

### D112. 快速反馈只压缩重复输入，不降低证据条件【有效】

==日常反馈按任务类型动态生成，并以 25 秒为真实用户可用性目标；只自动带入已确认的任务、课程、权重和题源，不猜测独立程度、正确性、新题、限时或掌握度。最终正确与独立正确、听课自评与实测能力、正式成绩与估分、熟题与新题必须分开保存。硬指标只有在来源、辅助、核对和测试条件完整时成立；信息不足继续显示未知。Agent 可检索已授权材料，但材料片段和模型总结不能递归充当新的学习事实。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=implemented-tested-and-tailnet-verified; retrieved_notes="计划模式/06-任务类型快速证据反馈v2部署验收.md" -->


## 2026-08-31：课表导入与系统适配

==课程按用户要求默认出勤，不核验、不推断授课章节或掌握程度。课表仅作为安排背景，独立于设备事实、番茄和奖励。课前20分钟至下课不安排其他行动；工作日180分钟、周末480分钟、周22–31小时仍全部用于课外深度学习。导入不改已确认计划，也不新增通知。==

详见 [[树莓派课程表导入与系统适配]]。

<!-- ai_provenance: source=codex; date=2026-08-31; verification=checked; retrieved_notes="DECISIONS.md" -->
