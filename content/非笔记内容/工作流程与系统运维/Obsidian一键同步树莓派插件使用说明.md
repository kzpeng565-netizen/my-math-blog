# Obsidian 一键同步树莓派插件使用说明

<!-- ai_provenance: source=codex; date=2026-07-29; verification=checked; retrieved_notes="none" -->

这个插件叫 `Pi Context Sync`，插件 ID 是 `pi-context-sync`。它给 Obsidian 增加一个左侧栏上传按钮和一个命令面板命令，用来手动触发现有的 behavior context exporter，把任务计划和番茄钟数据立即导出到 Syncthing 的 Windows Send Only 目录，再由 Syncthing 发送到树莓派。

## 文件位置

- 源码目录：`D:\mathblog\tools\obsidian-pi-context-sync`
- Obsidian 插件目录：`D:\mathblog\quartz\content\.obsidian\plugins\pi-context-sync`
- 现有 exporter：`D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.py`
- exporter 配置：`D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.json`
- Windows 同步目录：`C:\Users\15345\BehaviorContextSync`
- 树莓派接收目录：`/home/conrad/workspace/behavior-context-sync`

## 一键同步会做什么

点击按钮后，插件按这个顺序执行：

1. 如果当前打开的目标文件有尚未写入磁盘的内容，先保存这些打开的目标文件。
2. 调用 `D:\anaconda\python.exe` 运行现有 exporter。
3. exporter 读取这些文件：
   - `非笔记内容/任务计划/Profile.md`
   - `非笔记内容/任务计划/ToDo-已经规划好的任务.md`
   - `非笔记内容/任务计划/番茄钟log.md`
4. exporter 更新 `C:\Users\15345\BehaviorContextSync\context_snapshot.json` 和相关 raw 文件。
5. Syncthing 把 Windows Send Only 目录同步到树莓派 Receive Only 目录。
6. 如果设置中开启了树莓派校验，插件会用 SSH 只读比较本地和 Pi 端 `context_snapshot.json` 的 SHA-256。

## 使用方法

重启 Obsidian 或重新加载插件后，左侧栏会出现一个上传云图标。点击它即可执行一键同步。

也可以打开命令面板，运行：

```text
Pi Context Sync: 一键同步到树莓派
```

插件设置页在：

```text
设置 -> 第三方插件 -> Pi Context Sync
```

设置页里可以修改 Python 路径、exporter 路径、配置文件路径、导出目录、SSH 路径、Pi 主机名、远端快照路径，并可以直接点“测试运行”。

## 提示语说明

插件会在 Obsidian 内部给出 Notice 提示：

- `正在同步到树莓派。`：已经开始执行。
- `树莓派同步完成。`：本地导出成功，并且 Pi 端快照哈希已经匹配。
- `本地导出完成，已交给 Syncthing。`：未开启远端校验时的成功提示。
- `本地导出完成；暂未确认树莓派接收，Syncthing 将继续重试。`：本地导出成功，但 Pi 离线、SSH 不通，或 Syncthing 尚未在校验窗口内完成。
- `同步失败：...`：exporter、文件读取、Python 路径、SSH 路径等环节出现错误。

设置里可以开启“系统通知”。开启后，完成或异常提示会额外尝试发 Windows 系统通知；即使系统通知不可用，Obsidian 内部 Notice 仍然会显示。

## 和 20 分钟定时任务的关系

原来的 `Behavior Context Exporter Timer` 不需要关闭。它继续作为兜底机制，每 20 分钟运行一次。

一键同步和定时任务都调用同一个 exporter。exporter 自带 lock 文件，正常情况下不会把两次运行互相写坏。如果刚好同时运行，后启动的一次会尽快退出或等待现有结果。

## 常见问题

如果点击后提示 Python 或 exporter 找不到，检查插件设置里的路径是否仍然是：

```text
D:\anaconda\python.exe
D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.py
D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.json
```

如果提示“本地导出完成；暂未确认树莓派接收”，先看树莓派是否在线，再看 Syncthing 是否运行。这个提示不是本地导出失败，而是插件没有在设置的校验时间内确认 Pi 端已经收到。

如果左侧栏没有按钮，先重启 Obsidian，或在第三方插件页面确认 `Pi Context Sync` 已启用。

如果改完 ToDo 后马上点击，插件会主动保存当前打开的目标 note；但如果文件在外部编辑器里打开并且外部编辑器没有保存，插件只能读取磁盘上的旧内容。

## 更新插件

修改源码后，在 PowerShell 里运行：

```powershell
cd D:\mathblog\tools\obsidian-pi-context-sync
npm run build
```

然后在 Obsidian 里重新加载插件或重启 Obsidian。
