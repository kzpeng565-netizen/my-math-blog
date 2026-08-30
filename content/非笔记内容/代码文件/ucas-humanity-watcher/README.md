# 国科大人文讲座监控器

Windows 本地监控程序。它每 60 秒读取一次国科大人文讲座预告，只保留雁栖湖候选，并在本地排除周二、周三、周四 18:30–20:05 的习题课。程序不会无人值守预约；真实提交只能由用户在 `127.0.0.1` 本地面板点击“确认预约”触发。

## 安全边界

- 不识别、破解、截图或提交验证码。
- 不读取 `C:\Users\15345\Desktop\密码.txt`，也不保存或自动填写账号密码。
- 使用 `%LOCALAPPDATA%\UCASHumanityWatcher\edge-profile` 中的独立 Edge 配置，不读取日常 Edge 的 Cookie、密码、历史记录或其他配置。
- 本地面板只监听 `127.0.0.1:17863`，预约接口要求 SameSite Cookie、CSRF 令牌及正确的 Origin/Host。
- 日志只记录讲座 ID、扫描数量和状态码，不记录账号、密码、Cookie、会话令牌、验证码或完整网页。

## 首次运行

在 PowerShell 中进入本目录：

```powershell
npm install
npm test
npm run start:ui
```

面板地址为 <http://127.0.0.1:17863>。首次扫描通常会显示“需要手动登录”：

1. 点击“打开登录窗口”。
2. 在弹出的独立 Edge 中自行输入账号、密码和验证码并提交。
3. 登录成功后程序会验证讲座页、关闭这个独立窗口并恢复扫描。

如果用户主动关闭登录窗口但尚未验证成功，扫描保持暂停，不会反复请求登录页。

## 过滤规则

- 讲座名称或地点必须包含“雁栖湖”。
- 2026-08-31 至 2027-01-17（含首尾），周二、周三、周四 18:30–20:05 均按习题课排除。
- 时间采用半开区间：讲座恰好在 18:30 前结束或恰好从 20:05 开始，不视为冲突。
- 普通课表冲突继续由选课系统返回；程序会展示“与已选课程时间冲突”，不会重试。
- 同时出现多个合格候选时全部展示，由用户选择。一个讲座成功后，与其时间重叠的其他候选会被禁用。

运行配置位于 `%LOCALAPPDATA%\UCASHumanityWatcher\config.json`。修改后需要重启程序。`dashboardHost` 被强制限制为 `127.0.0.1`，`pollSeconds` 不允许低于 15 秒。

## 预约结果

点击“确认预约”时，程序会重新扫描对应讲座并再次应用全部本地规则，然后点击网站原始“预约”控件。支持的结果包括：

- 成功或已经报名：进入报名记录页按讲座 ID 二次核验。
- 已满、未到预约时间、达到数量限制：保留候选，允许用户稍后手动重试。
- 课程冲突、同时段讲座冲突、资格不符、爽约限制：停止重试并展示原因。
- 响应不明确：禁止立即重复点击，要求先人工核对报名记录。

## 登录启动

只有手动运行和只读实站验证稳定后，才注册登录启动任务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-task.ps1
```

已有同名任务时脚本会拒绝覆盖；确需更新时显式添加 `-Force`。删除任务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\uninstall-task.ps1
```

任务仅在当前用户已经登录且电脑清醒时运行。锁屏不影响扫描；睡眠、关机或未登录期间不会扫描。

## 数据与排障

- 状态：`%LOCALAPPDATA%\UCASHumanityWatcher\state.json`
- 日志：`%LOCALAPPDATA%\UCASHumanityWatcher\logs\watcher-YYYY-MM-DD.jsonl`
- 独立浏览器配置：`%LOCALAPPDATA%\UCASHumanityWatcher\edge-profile`
- 健康检查：<http://127.0.0.1:17863/healthz>

常见状态：

- `需要登录`：点击面板按钮并手动登录。
- `异常退避`：网络或页面结构错误，程序按 60/120/300/600 秒退避，不会并发重试。
- `当前不可重试`：上次结果具有不确定性或确定为终止状态，先人工核对或忽略本场。

停止前台程序使用 `Ctrl+C`。不要直接删除正在使用的独立 Edge 配置目录。
