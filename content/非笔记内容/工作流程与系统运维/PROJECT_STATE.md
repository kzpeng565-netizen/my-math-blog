<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified -->

# 半小时行为解释系统——PROJECT_STATE

> 本文档描述系统当前实际状态。技术细节见 PI_SERVER_HANDOFF.md，设计决策见 DECISIONS.md。

## 系统是什么

一个运行在树莓派上的**半小时行为解释系统**。每半小时自动收集电脑（ActivityWatch + Syncthing）和手机（Android Automate）的使用数据，清洗后交 DeepSeek V4 Flash 生成语义时间线和核验报告，通过 PushPlus 微信公众号推送给用户。当前阶段**只核验 AI 的理解能力，不做任何自动干预**。

## 当前版本：第三版

三轮迭代已完成：

- **第一版**：叙事型报告。用户反馈"没有直接回答工作多久、休息多久"——被否定。
- **第二版**：指标先行，程序计算确定性数字（工作时间、休息时间等），AI 只负责语义解释。加入用户确认的休息规则（电脑 AFK ≥ 3 分钟 + 手机熄屏）。
- **第三版（当前）**：引入两层 AI 调用——第一次生成语义时间线（work/entertainment/communication/rest/other/uncertain），程序据此计算工作-娱乐混杂指标，第二次 AI 只负责解释结果并生成报告。核心创新是**工作-娱乐混杂检测**：工作中被 AI 判断为娱乐且持续 > 30 秒才算一次偏离，30 秒及以下不计。

## 当前运行的组件

### 树莓派 (Raspberry Pi 3 Model B, Debian 13, 1GB RAM)

| 组件 | 状态 | 说明 |
|---|---|---|
| `phone-usage-receiver.service` | active | Flask 服务器监听 `127.0.0.1:8765`，接收手机三文件上传 |
| `phone-usage-maintenance.timer` | active | 每日 03:30 归档压缩（>30 天）和清理（>365 天） |
| `activitywatch-advisor.timer` | active, enabled | 每半小时 08/38 分触发分析 |
| `activitywatch-advisor.service` | triggered by timer | 单次执行，完成后退出 |
| `syncthing@conrad.service` | active | 同步 Windows ActivityWatch 数据到树莓派 |
| `tailscaled.service` | active | Tailscale VPN + Funnel（公网入口 for 手机） |
| `cockpit.socket` | active | Web 管理界面 `https://pi.local:9090` |
| `filebrowser.service` | active | 文件管理 `https://pi.local:8080` |

### Windows 电脑

| 组件 | 状态 | 说明 |
|---|---|---|
| ActivityWatch | 运行中 | 记录窗口标题、网页标签页、AFK 状态 |
| ActivityWatch Web Watcher (Edge 插件) | 运行中 | 记录浏览器标签页 URL 和标题 |
| Syncthing | 运行中 | 同步 `C:\Users\15345\ActivityWatchSync` 到树莓派 |

### Android 手机

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate `Phone Usage Logger` 流 | 运行中 | 采集 foreground/screen/heartbeat，每 15 分钟上传 |
| Clash | 运行中 | 代理（与 HTTPS 上传无冲突，已验证） |

## 当前数据量

- 2026-07-25 全天：48 个时段全部有输出（~29 KB/时段，含所有数据层）
- 预估增长：~1.4 MB/天，~0.5 GB/年（不需要立即压缩）
- 手机 archive 尚未自动压缩（今天是第三天，未触发 30 天阈值）

## 已验证的功能（全部通过）

1. 手机 → Tailscale Funnel → 树莓派 数据上传与归档
2. 电脑 → Syncthing → 树莓派 数据同步
3. computer_facts.py / phone_facts.py 独立清洗
4. cross_device.py 双设备时间重叠计算
5. DeepSeek 生成语义时间线（非思考模式，避免 token 耗尽）
6. 语义时间线校验（分钟总和、时间连续性、休息规则一致性）
7. 工作-娱乐混杂指标计算（>30s 偏离检测）
8. DeepSeek 生成最终核验报告
9. PushPlus 微信公众号推送
10. systemd timer 自动调度

## 当前限制

- 没有读取任务计划，不与 OP/Claude 对照
- 夜间（00:00-07:00）无活动时段仍然推送报告
- 手机跨午夜最后一段数据可能遗漏（Automate 每次只上传当天文件）
- 微信公众号回复不会写回系统

## 中断位置

上一轮 ChatGPT 会话在额度耗尽后分叉。中断前正在生成 PROJECT_STATE / DECISIONS / NEXT_STEPS。系统本身未受影响，定时器持续运行。最新一条报告为 `2026-07-26 00:08` 生成的 `23:30—00:00`。
