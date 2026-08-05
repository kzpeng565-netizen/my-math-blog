# Behavior Context Exporter

只读读取三份 Obsidian Markdown，确定性生成 `context_snapshot.json`，供 Syncthing
单向同步。脚本不会修改、完成、延期或重排任何 Obsidian 任务，也不会根据番茄钟
推断具体任务进度。

## 手动运行与测试

```powershell
python .\behavior_context_exporter.py
python -m unittest discover -s .\tests -v
```

输出目录默认为 `C:\Users\15345\BehaviorContextSync`。源内容无变化时只更新
`sync_heartbeat.json`；快照与 `raw\` 副本采用临时文件加 `os.replace()` 原子写入。
错误不会覆盖上一份正确快照。

番茄钟工作量始终使用 `(duration:: 40m)` 等声明时长。`end - begin` 较长通常可能
来自中途暂停后继续番茄钟，只记录为 `extended_wall_clock_interval_count` 供审计，
不视为坏数据、低效或任务失败。

## 定时任务

```powershell
.\scripts\install_exporter_task.ps1
```

任务使用 `pythonw.exe`，登录时启动并每 20 分钟重复，忽略并发新实例，失败可重试。
脚本自身也使用 `exporter.lock` 防止并发。
若系统返回 Task Scheduler `Access Denied`，请从“以管理员身份运行”的 PowerShell
执行一次安装脚本；日常任务仍以当前登录用户运行，不需要管理员权限。

卸载定时任务：

```powershell
.\scripts\remove_exporter_task.ps1
```

卸载不会删除导出目录。如需移除导出数据，请在确认 Syncthing 已移除该文件夹后手工
删除 `C:\Users\15345\BehaviorContextSync`。

## Syncthing

把 Windows 目录配置为 **Send Only**，文件夹 ID 建议为 `behavior-context`。共享给
树莓派，并在 Windows 端 `.stignore` 中加入：

```text
logs
exporter.lock
*.tmp
```

树莓派目录使用 `/home/conrad/workspace/behavior-context-sync` 并配置为
**Receive Only**。不要与 `activitywatch-sync` 混用。

仓库中的 `scripts/configure_syncthing_folder.py` 是一次性配置助手：它从本机
Syncthing XML 中读取本机 REST API key，不打印或保存密钥，并用官方配置端点新增
文件夹。日常导出不依赖该脚本。
