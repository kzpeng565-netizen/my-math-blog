<!-- ai_provenance: updated=2026-07-27 -->
<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified -->

# 半小时行为解释系统——NEXT_STEPS

> 本文档描述下一步工作计划，按优先级排列。状态：☐ 待开始 / ◐ 进行中 / ☑ 已完成。

## 立即要做

### ☐ 1. 确认今天手机数据流正常

检查 `/home/conrad/phone_usage/archive/2026-07-26/` 是否已有数据文件。如果今天上午仍无数据，排查 Automate 流是否被系统杀死。

```bash
ssh pi.local "ls -lh /home/conrad/phone_usage/archive/2026-07-26/"
```

### ☐ 2. 验证 00:08 生成的报告质量

读取 `/home/conrad/workspace/activitywatch-advisor/data/ai_reports/2026-07-25/23-30.md`，确认 23:30—00:00 的核验报告合理。

### ✅ 14. 平板数据接入
平板已通过相同 Funnel 入口上传数据。接收端白名单增加 tablet_foreground/screen/heartbeat。phone_facts.py 增加 device 过滤，新建 tablet_facts.py。cross_device.py 支持三设备融合（平板为辅助数据源）。AI prompt 适配平板上下文。

### ✅ 15. 设备语义修正
平板亮屏不加入 any_device_interaction 和 minimum_evidence_seconds。休息判定只要求电脑 AFK + 手机熄屏，平板亮屏降低置信度但不否决。平板作为辅助数据源，仅在电脑和手机均无证据时作为低置信度 fallback。

## 短期（本周）

### ☐ 3. 观察数据质量 3-7 天

不修改任何系统配置，纯粹观察：
- 手机数据是否有连续缺失（心跳断 > 30 分钟）
- AI 语义时间线是否稳定（不会对相同行为给出不同解释）
- 休息判断是否准确
- 娱乐偏离检测是否合理

### ☐ 4. 夜间静默推送

在 `run_half_hour.py` 或 `pushplus_client.py` 中增加时段判断：00:00—07:00 的无活动时段跳过 PushPlus 推送（仍生成报告文件但不推送）。配置项可放在 `settings.json` 中。

**当前问题**：凌晨 48 个时段全部推送，大量"电脑无活动、手机熄屏"消息无意义。

### ☐ 5. 数据增长确认

运行一周后计算 `data/` 目录真实日增长量，与预估的 1.4 MB/天对比。如大幅超出，排查是否某层数据异常膨胀。

### ☐ 6. DeepSeek API 密钥轮换

架构文档建议在部署验证后轮换密钥。在 DeepSeek 控制台生成新密钥，更新 `/home/conrad/.config/activitywatch-advisor/env`，重启 advisor：

```bash
sudo systemctl restart activitywatch-advisor.service
```

## 中期（2-4 周）

### ☐ 7. 全天分析脚本

基于已有 `computer_facts`、`phone_facts` 和 `semantic_timelines` 数据层，编写只读分析脚本：
- 每日工作/娱乐/休息总时长
- 娱乐偏离高发时段
- 最长连续工作时间
- 手机与电脑使用的时段分布

**不需要重新读取原始事件**，复用已保存的事实摘要即可。

### ☐ 8. 接入任务计划对照

让 OP/Claude 制定计划时额外输出标准 JSON（任务名、计划时长、允许的应用类别）。比对计划与实际行为：

```text
计划：学习 Haar 测度 25 分钟
实际：Obsidian 12 分钟 + 浏览器 5 分钟 + 知乎 9 分钟
偏离：知乎浏览 9 分钟不在计划内
```

这步需要先在 OP/Claude 端约定 JSON 格式，然后在树莓派端增加对照模块。

### ☐ 9. 报告查看页面

在 File Browser 可访问的 workspace 中生成静态 HTML 页面，显示最近几天的报告摘要和趋势图。或者用 Cockpit 的自定义页面。

### ☐ 10. 手机应用名映射扩充

当前 `phone_app_names` 只映射了微信、QQ、哔哩哔哩等少量应用。在 `settings.json` 中增加更多常用应用（小红书、知乎、淘宝等）的包名到中文名的映射。

## 长期（1-3 月）

### ☐ 11. 信息过滤与替代内容平台

在树莓派上搭建一个低刺激信息供给系统，在被判断为"需要恢复但想获取刺激"时推送替代内容。这需要：
- 确定内容源（RSS、预选文章等）
- 设计输出格式（有限队列，非无限滚动）
- 与行为中枢的交互协议

### ☐ 12. 有限自动干预

在数据积累充分、AI 判断准确率足够高后，从"纯观察"升级为"有限干预"：
- 只启用少数干预动作（提醒当前任务、建议 5 分钟启动、建议开启屏蔽模式）
- 不直接控制 Cold Turkey 或不做手机控
- 每次干预记录结果，用于后续调整

### ☐ 13. AI 维护配置

让 AI 每周检查一次配置文件和提示词，提出修改建议。约束：
- 稳定原则（core_principles）不可自动修改
- 个人偏好（profile）可提议但需确认
- 每次修改需出 diff
- Git 管理所有配置变更

## 不做的事（明确排除）

- 让 AI 自由生成 Cold Turkey 阻止规则
- 读取聊天内容、通知正文、短信
- 记录屏幕截图或键盘输入
- 将数据上传到非树莓派的第三方服务
- 自动修改用户的任务计划
- 弹窗或强锁屏幕

## 维护检查清单

每周花 5 分钟检查：

1. `ssh pi.local` → `systemctl is-active phone-usage-receiver.service activitywatch-advisor.timer syncthing@conrad.service tailscaled.service`
2. `df -h /` → 磁盘是否低于 20%
3. `journalctl -u activitywatch-advisor.service --since "1 day ago" --no-pager | grep -c "completed"` → 应有 ~48 条
4. `journalctl -u phone-usage-receiver.service --since "1 hour ago" --no-pager | grep "PUT"` → 应有最近上传记录
5. `ls /home/conrad/phone_usage/archive/$(date +%F)/` → 当天三个 JSONL 文件存在且非空
6. 查看最近一条 PushPlus 微信消息 → 内容合理
