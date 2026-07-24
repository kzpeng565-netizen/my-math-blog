# ActivityWatch 树莓派同步运维手册

<!-- ai_provenance: source=codex; date=2026-07-24; verification=source-backed; retrieved_notes="" -->

## 1. 当前用途

这套系统把电脑端 ActivityWatch 的数据镜像到树莓派，作为以后“计划—实际行为对照系统”的数据基础。

```text
电脑 ActivityWatch（只监听 localhost:5600）
→ Windows 计划任务每 5 分钟调用隐藏启动器
→ 隐藏启动器运行 PowerShell 同步脚本和 aw-sync
→ C:\Users\15345\ActivityWatchSync
→ Syncthing 加密传输
→ 树莓派 /home/conrad/workspace/activitywatch-sync
```

==计划任务调用 `run-activitywatch-sync-hidden.vbs`，由它在不可见窗口中启动 `push-activitywatch.ps1`。隐藏启动器只负责运行方式；实际同步、状态记录和错误日志仍由 PowerShell 脚本负责。==

ActivityWatch 的 `5600` 端口没有暴露到局域网。官方不建议直接运行远程 ActivityWatch Server，因为 API 没有身份认证；当前方案使用官方支持的 `aw-sync` 同步目录，再由 Syncthing 传输。

> [!success] 2026-07-24 验证结果
> - ActivityWatch：`v0.13.2`
> - 电脑数据桶：窗口活动、离开状态
> - 树莓派：`Pi`，`192.168.0.229`
> - 树莓派 Syncthing：`v1.29.5`
> - 连接：TLS 1.3
> - 树莓派接收完成度：`100%`
> - 待传文件、待传字节：`0`
> - 树莓派无降频：`throttled=0x0`
> - 根分区：15 GB，总计使用约 3.4 GB

## 2. 重要位置

| 内容                  | 位置                                                                                       |
| ------------------- | ---------------------------------------------------------------------------------------- |
| 本手册与脚本              | `D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\ActivityWatch树莓派同步`                          |
| 后台隐藏启动器             | `run-activitywatch-sync-hidden.vbs`                                                      |
| 同步逻辑脚本              | `push-activitywatch.ps1`                                                                 |
| ActivityWatch 原始数据库 | `C:\Users\15345\AppData\Local\activitywatch\activitywatch\aw-server\peewee-sqlite.v2.db` |
| 电脑端同步目录             | `C:\Users\15345\ActivityWatchSync`                                                       |
| 电脑端同步状态             | `C:\Users\15345\AppData\Local\ActivityWatchPiSync\status.json`                           |
| 电脑端同步日志             | `C:\Users\15345\AppData\Local\ActivityWatchPiSync\logs`                                  |
| 树莓派接收目录             | `/home/conrad/workspace/activitywatch-sync`                                              |
| 树莓派 Syncthing 服务    | `syncthing@conrad.service`                                                               |

树莓派目录是“同步副本”，不是不可变备份：如果电脑端同步目录中的文件被删除，删除也可能同步到树莓派。需要长期备份时，应另外建立带历史版本的定期备份。

## 3. 正常使用

正常情况下无需手动操作：

1. ActivityWatch 随 Windows 登录启动。
2. `ActivityWatch Sync to Pi` 每 5 分钟通过隐藏启动器更新同步数据库，不显示 PowerShell 窗口。
3. `Syncthing for ActivityWatch` 登录后持续把变化发送到树莓派。
4. 树莓派以 `receiveonly` 模式接收，不主动改写电脑数据。

常用页面：

- ActivityWatch：<http://127.0.0.1:5600>
- 电脑 Syncthing：<http://127.0.0.1:8384>
- 树莓派 Cockpit：<https://pi.local:9090>
- 树莓派 File Browser：<https://pi.local:8080>

Syncthing 管理页和 ActivityWatch API 都只应在本机或受保护的管理通道中使用，不要映射到公网。

## 4. 快速检查

### 检查最近一次 ActivityWatch 数据生成

在 PowerShell 中执行：

```powershell
Get-Content -Raw "$env:LOCALAPPDATA\ActivityWatchPiSync\status.json"
```

正常结果应包含：

```json
{
  "ok": true,
  "activitywatch_version": "v0.13.2",
  "last_error": null
}
```

### 检查两个计划任务

```powershell
Get-ScheduledTask -TaskName "ActivityWatch Sync to Pi","Syncthing for ActivityWatch"
Get-ScheduledTaskInfo -TaskName "ActivityWatch Sync to Pi"
```

正常情况：

- `ActivityWatch Sync to Pi` 为 `Ready`，最近结果为 `0`；
- `Syncthing for ActivityWatch` 为 `Running`。

### 检查树莓派是否已同步

最简单的方法是打开 <http://127.0.0.1:8384>，查看：

- 远程设备 `RaspberryPi` 显示已连接；
- 文件夹 `ActivityWatch Sync (PC to Pi)` 显示 `Up to Date`。

也可以登录树莓派后执行：

```bash
systemctl status syncthing@conrad.service --no-pager
find /home/conrad/workspace/activitywatch-sync -maxdepth 3 -type f -name 'test.db' -ls
```

## 5. 手动同步与启停

### 立即生成一次同步数据

```powershell
& "D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\ActivityWatch树莓派同步\push-activitywatch.ps1"
```

执行后检查：

```powershell
Get-Content -Raw "$env:LOCALAPPDATA\ActivityWatchPiSync\status.json"
```

### 重新启动电脑端任务

```powershell
Start-ScheduledTask -TaskName "ActivityWatch Sync to Pi"
Start-ScheduledTask -TaskName "Syncthing for ActivityWatch"
```

仅临时停止：

```powershell
Stop-ScheduledTask -TaskName "ActivityWatch Sync to Pi"
Stop-ScheduledTask -TaskName "Syncthing for ActivityWatch"
```

`Stop-ScheduledTask` 不会删除数据或任务配置。不要随意删除 `C:\Users\15345\ActivityWatchSync`。

### 重启树莓派端 Syncthing

```bash
sudo systemctl restart syncthing@conrad.service
systemctl status syncthing@conrad.service --no-pager
journalctl -u syncthing@conrad.service --no-pager -n 100
```

## 6. 故障排查顺序

| 现象 | 先检查 | 处理 |
|---|---|---|
| `status.json` 显示 `ok: false` | ActivityWatch 是否打开 | 打开 <http://127.0.0.1:5600>，再手动运行推送脚本 |
| 计划任务最近结果不是 `0` | `status.json` 和当天日志 | 优先处理 `last_error` 中的第一条错误 |
| Syncthing 显示树莓派离线 | `ping pi.local` | 确认树莓派开机且电脑与树莓派在同一局域网 |
| 树莓派端口不通 | `Test-NetConnection pi.local -Port 22000` | 在树莓派检查 `syncthing@conrad.service` |
| 文件夹显示未同步 | 两端剩余磁盘空间 | 电脑检查 C 盘；树莓派执行 `df -h /` |
| IP 改变 | `ping pi.local` | 优先使用 `pi.local`，不要把 DHCP 地址当作永久地址 |
| ActivityWatch 有数据但树莓派没有更新 | 手动运行推送脚本 | 再检查本机 Syncthing 页面中的文件夹状态 |

当前 `v0.13.2` 附带的 `aw-sync` 在使用 `--buckets` 参数时会崩溃，因此脚本使用 `sync-advanced --mode push` 同步全部现有数据桶。当前只有窗口活动与离开状态两个桶，范围符合预期。

## 7. 数据保护与恢复

更新或维修前，至少保留以下两项：

```text
C:\Users\15345\AppData\Local\activitywatch\activitywatch\aw-server\peewee-sqlite.v2.db
C:\Users\15345\ActivityWatchSync
```

安全原则：

- 不直接复制正在写入的数据库来覆盖另一端；
- 不开放 `5600`、`8384` 到公网；
- 不把 ActivityWatch 数据提交到公开 Git 仓库；
- 不在脚本、文档或聊天中保存树莓派密码；
- 删除或重建同步目录前，先制作独立备份；
- 恢复时先停止相关任务，再检查文件版本，避免旧数据反向覆盖。

## 8. 当前边界与下一步

当前已完成的是“电脑数据可靠上传到树莓派”，尚未包含：

- 手机使用数据；
- 每半小时的应用分类汇总；
- 与当天计划的自动对照；
- AI 判断偏离、疲劳或休息；
- 自动控制 Cold Turkey 或手机控。

下一步最合适的是只读汇总：每半小时从树莓派上的同步数据库生成一条分类记录，先验证统计是否准确，不立即加入 AI 或自动管控。

## 9. 官方资料

- [ActivityWatch 同步说明](https://docs.activitywatch.net/en/latest/syncing.html)
- [ActivityWatch 远程服务安全说明](https://docs.activitywatch.net/en/latest/remote-server.html)
- [ActivityWatch 数据导出](https://docs.activitywatch.net/en/latest/features/exporting-data.html)
- [Syncthing 文档](https://docs.syncthing.net/)
