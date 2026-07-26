import re

path = r"D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\PROJECT_STATE.md"
with open(path, encoding="utf-8") as f:
    content = f.read()

# Update system description
content = content.replace(
    "和手机（Android Automate）的使用数据",
    "、手机和平板（Android Automate）的使用数据"
)

# Update receiver description
content = content.replace(
    "接收手机三文件上传",
    "接收手机和平板共六文件上传（foreground/screen/heartbeat x 2）"
)

# Update data flow
content = content.replace(
    """            activitywatch-advisor.timer (每半小时 08/38 分触发)
                     |
          +----------+-----------+
          |                      |
    computer_facts.py    phone_facts.py
          |                      |
    computer_facts/       phone_facts/
          |                      |
          +----------+-----------+
                     |
           cross_device.py (时间重叠)""",
    """            activitywatch-advisor.timer (每半小时 08/38 分触发)
                     |
          +----------+-----------+-----------+
          |                      |           |
    computer_facts.py    phone_facts.py  tablet_facts.py
          |                      |           |
    computer_facts/       phone_facts/  tablet_facts/
          |                      |           |
          +----------+-----------+-----------+
                     |
           cross_device.py (三设备时间重叠，平板为辅助)"""
)

# Add tablet to verified features
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

# Add tablet to components after phone section
old_phone_section = """### Android 手机

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate `Phone Usage Logger` 流 | 运行中 | 采集 foreground/screen/heartbeat，每 15 分钟上传 |
| Clash | 运行中 | 代理（与 HTTPS 上传无冲突，已验证） |

## 当前数据量"""

new_phone_section = """### Android 手机

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

content = content.replace(old_phone_section, new_phone_section)

# Update interruption position
content = content.replace(
    "最新一条报告为 `2026-07-26 00:08` 生成的 `23:30\u201400:00`。",
    "最新一条报告为 `2026-07-27 01:38` 生成的 `01:00\u201401:30`。平板已接入全链路，timer 正常运行。"
)

# Update server-layout note about receiver
content = content.replace(
    "phone-usage-receiver.service",
    "phone-usage-receiver.service（同时接收手机和平板，共六种文件名）"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("PROJECT_STATE.md updated")
