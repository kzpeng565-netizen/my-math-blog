import os, sys

base = r"D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维"

# ===== PROJECT_STATE.md =====
path = os.path.join(base, "PROJECT_STATE.md")
with open(path, encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "和手机（Android Automate）的使用数据",
    "、手机和平板（Android Automate）的使用数据"
)
content = content.replace(
    "接收手机三文件上传",
    "接收手机和平板共六文件上传（foreground/screen/heartbeat x 2）"
)
content = content.replace(
    "computer_facts.py / phone_facts.py 独立清洗",
    "computer_facts.py / phone_facts.py / tablet_facts.py 独立清洗"
)
content = content.replace(
    "cross_device.py 双设备时间重叠计算",
    "cross_device.py 三设备时间重叠计算（平板为辅助数据源）"
)
content = content.replace(
    "工作-娱乐混杂指标（>30s 偏离判定）-- 已验证",
    "工作-娱乐混杂指标（>30s 偏离判定）-- 已验证\n14. 平板数据上传（tablet_foreground/screen/heartbeat）-- 已验证\n15. 平板事实提取与三设备融合（tablet as auxiliary）-- 已验证\n16. 休息判定：平板亮屏不否决休息，仅降低置信度 -- 已验证"
)
content = content.replace(
    "最新一条报告为 `2026-07-26 00:08` 生成的 `23:30—00:00`。",
    "最新一条报告为 `2026-07-27 01:38`。平板已接入全链路，timer 正常运行。"
)

# Add tablet component section
old = """### Android 手机

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate `Phone Usage Logger` 流 | 运行中 | 采集 foreground/screen/heartbeat，每 15 分钟上传 |
| Clash | 运行中 | 代理（与 HTTPS 上传无冲突，已验证） |

## 当前数据量"""

new = """### Android 手机

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate `Phone Usage Logger` 流 | 运行中 | 采集 foreground/screen/heartbeat，每 15 分钟上传 |
| Clash | 运行中 | 代理（与 HTTPS 上传无冲突，已验证） |

### Android 平板

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate 平板采集流 | 运行中 | 采集 tablet_foreground/screen/heartbeat，每约 2 分钟上传 |
| 设备型号 | Huawei | 使用相同 token 和 Funnel 入口，文件名为 tablet_* 前缀 |

## 当前数据量"""

content = content.replace(old, new)

# Add tablet to data flow diagram
old_diagram = """    computer_facts.py    phone_facts.py
          |                      |
    computer_facts/       phone_facts/
          |                      |
          +----------+-----------+
                     |
           cross_device.py (时间重叠)"""
new_diagram = """    computer_facts.py    phone_facts.py    tablet_facts.py
          |                      |                |
    computer_facts/       phone_facts/      tablet_facts/
          |                      |                |
          +----------+-----------+----------------+
                     |
           cross_device.py (三设备融合，平板为辅助)"""
content = content.replace(old_diagram, new_diagram)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("PROJECT_STATE.md done")

# ===== PI_SERVER_HANDOFF.md =====
path2 = os.path.join(base, "PI_SERVER_HANDOFF.md")
with open(path2, encoding="utf-8") as f:
    content = f.read()

# Add tablet section after phone section
old_phone2 = """### 2.2 手机端 -> 树莓派
**[已由旧对话确认][已由服务器核验]**

- Android 上使用 Automate 运行 `Phone Usage Logger` 流
- 每 15 分钟通过 HTTPS PUT 上传三个文件到 `https://pi.taild4d3f7.ts.net/upload/`（Tailscale Funnel）
- 三文件：`foreground.jsonl`（前台应用）、`screen.jsonl`（亮/灭屏）、`heartbeat.jsonl`（心跳）
- Funnel 代理到 `127.0.0.1:8765`（`phone-usage-receiver.service`）
- 接收端验证 token，按日期归档到 `/home/conrad/phone_usage/archive/YYYY-MM-DD/`
- 同一天多次上传会自动合并去重
- 超过 30 天压缩为 `.jsonl.gz`，超过 365 天删除"""

new_phone2 = """### 2.2 手机端 -> 树莓派
**[已由旧对话确认][已由服务器核验]**

- Android 手机上使用 Automate 运行采集流
- 每约 15 分钟通过 HTTPS PUT 上传三个文件到 `https://pi.taild4d3f7.ts.net/upload/`（Tailscale Funnel）
- 三文件：`foreground.jsonl`（前台应用）、`screen.jsonl`（亮/灭屏）、`heartbeat.jsonl`（心跳）
- Funnel 代理到 `127.0.0.1:8765`（`phone-usage-receiver.service`）
- 接收端验证 token，按日期归档到 `/home/conrad/phone_usage/archive/YYYY-MM-DD/`
- 同一天多次上传会自动合并去重
- 超过 30 天压缩为 `.jsonl.gz`，超过 365 天删除

### 2.3 平板端 -> 树莓派
**[已由旧对话确认][已由服务器核验]**

- Android 平板上使用 Automate 运行相同结构的采集流
- 每约 2 分钟通过 HTTPS PUT 上传到同一 Funnel 入口
- 三文件：`tablet_foreground.jsonl`、`tablet_screen.jsonl`、`tablet_heartbeat.jsonl`
- 使用与手机相同的 token，相同 URL，接收端白名单已包含 tablet_* 文件名
- 归档到同一 `/home/conrad/phone_usage/archive/YYYY-MM-DD/` 目录
- device 字段为 `"tablet"`，`phone_facts.py` 和 `tablet_facts.py` 各自按 device 过滤"""

content = content.replace(old_phone2, new_phone2)

# Add tablet_facts to data files table
old_data2 = """| 手机事实 | `data/phone_facts/YYYY-MM-DD/HH-MM.json` | phone_facts.py | 去重、亮灭屏重建后的手机活动事实 |
| 合并事实""" 
new_data2 = """| 手机事实 | `data/phone_facts/YYYY-MM-DD/HH-MM.json` | phone_facts.py | 去重、亮灭屏重建后的手机活动事实 |
| 平板事实 | `data/tablet_facts/YYYY-MM-DD/HH-MM.json` | tablet_facts.py | 去重、亮灭屏重建后的平板活动事实（辅助数据源） |
| 合并事实"""
content = content.replace(old_data2, new_data2)

# Add tablet_facts.py to src listing
content = content.replace(
    "phone_facts.py, cross_device.py,",
    "phone_facts.py, tablet_facts.py, cross_device.py,"
)

# Update data flow diagram in handoff
old_diagram2 = """    computer_facts.py    phone_facts.py
          |                      |
    computer_facts/       phone_facts/
          |                      |
          +----------+-----------+
                     |
           cross_device.py (时间重叠)"""
content = content.replace(old_diagram2, new_diagram)

# Update config section
old_config = "当前已连接设备：`computer`, `phone`；未来预留 `tablet`"
new_config = "当前已连接设备：`computer`, `phone`, `tablet`（平板为辅助数据源）"
content = content.replace(old_config, new_config)

# Add tablet to verified features
content = content.replace(
    "6. `phone_facts.py` 从 JSONL 提取并清洗手机事实 -- 已验证",
    "6. `phone_facts.py` 从 JSONL 提取并清洗手机事实 -- 已验证\n7. `tablet_facts.py` 从 JSONL 提取并清洗平板事实 -- 已验证"
)

# Update interruption position
old_int2 = "最新一次 systemd timer 触发：`2026-07-26 00:08:00`（正在执行中）。"
new_int2 = "最新一次 systemd timer 触发：`2026-07-27 01:38`（已完成）。平板已全链路接入。"
content = content.replace(old_int2, new_int2)

# Update next steps
old_next2 = "3. **生成 PROJECT_STATE.md / DECISIONS.md / NEXT_STEPS.md**：按用户原要求，方便其它 AI 接手"
new_next2 = "3. **生成 PROJECT_STATE.md / DECISIONS.md / NEXT_STEPS.md**：已完成（2026-07-27 更新）\n4. **平板数据接入**：已完成（2026-07-27），包括接收端白名单、事实提取、三设备融合、AI prompt 适配"
content = content.replace(old_next2, new_next2)

with open(path2, "w", encoding="utf-8") as f:
    f.write(content)
print("PI_SERVER_HANDOFF.md done")

# ===== DECISIONS.md =====
path3 = os.path.join(base, "DECISIONS.md")
with open(path3, encoding="utf-8") as f:
    content = f.read()

# Add D18: Tablet as auxiliary
old_d18_pos = "## 已废弃的决策"
new_d18 = """### D18. 平板为辅助数据源  【有效】
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

## 已废弃的决策"""
content = content.replace(old_d18_pos, new_d18)

# Update D6 to reflect tablet doesn't block rest
content = content.replace(
    "并且以后接入的平板也没有操作时，可以确定为休息",
    "平板亮屏不否决休息，仅降低置信度（D18）"
)

with open(path3, "w", encoding="utf-8") as f:
    f.write(content)
print("DECISIONS.md done")

# ===== NEXT_STEPS.md =====
path4 = os.path.join(base, "NEXT_STEPS.md")
with open(path4, encoding="utf-8") as f:
    content = f.read()

# Mark tablet integration as complete and add completed items
content = content.replace(
    "<!-- ai_provenance:",
    "<!-- ai_provenance: updated=2026-07-27 -->\n<!-- ai_provenance:"
)

# Add completed items after immediate section
old_immediate_end = "## 短期（本周）"
new_completed = """### ✅ 14. 平板数据接入
平板已通过相同 Funnel 入口上传数据。接收端白名单增加 tablet_foreground/screen/heartbeat。phone_facts.py 增加 device 过滤，新建 tablet_facts.py。cross_device.py 支持三设备融合（平板为辅助数据源）。AI prompt 适配平板上下文。

### ✅ 15. 设备语义修正
平板亮屏不加入 any_device_interaction 和 minimum_evidence_seconds。休息判定只要求电脑 AFK + 手机熄屏，平板亮屏降低置信度但不否决。平板作为辅助数据源，仅在电脑和手机均无证据时作为低置信度 fallback。

## 短期（本周）"""
content = content.replace(old_immediate_end, new_completed)

# Update item 3 status
content = content.replace(
    "### ☆ 3. 观察数据质量 3-7 天",
    "### ☆ 3. 观察平板数据质量 3-7 天\n确认平板数据连续、heartbeat 正常、foreground 事件不缺失。关注平板 Automate 流是否被系统杀死。"
)

with open(path4, "w", encoding="utf-8") as f:
    f.write(content)
print("NEXT_STEPS.md done")

print("\nAll four documents updated successfully")
