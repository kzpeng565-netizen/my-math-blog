---
title: QtScrcpy 与华为平板 USB 反复断连排查复盘
date: 2026-07-22
tags:
  - Windows
  - Android
  - ADB
  - QtScrcpy
  - 故障排查
---

<!-- ai_provenance: source=codex; date=2026-07-22; verification=checked; retrieved_notes="" -->

# QtScrcpy 与华为平板 USB 反复断连排查复盘

## 1. 场景与结论

设备与环境：

- 华为 MatePad `BAH3-W09`，EMUI 13、Android 10；
- Windows 11 64 位；
- QtScrcpy 3.3.3 x86；
- 使用 USB 调试进行有线投屏，主要用于长时间线上理科授课。

本次问题不能简单归因于 QtScrcpy。实际同时存在多个层级的问题：

1. HiSuite 安装了被 Windows 安全性阻止的旧华为 USB 复合设备过滤驱动；
2. MTP 子接口一度没有正确匹配 Windows 自带驱动；
3. QtScrcpy 自带的 ADB 版本较旧；
4. Windows 电源计划中的“USB 选择性暂停”实际上仍处于启用状态；
5. 平板会在不同 USB 组合身份之间重新枚举，使故障看起来像“QtScrcpy 自己断开”。

==最终修复并不是“把所有复合接口都修到正常”，而是把投屏链路收敛回原来的“仅充电 + 仅充电模式下允许 ADB 调试”，并把线缆从异常的电脑 USB 端口 `HS01` 换到另一个 USB-A 端口 `HS02`。换口后父设备正常启动，ADB 从 `unauthorized` 经重新授权变为 `device`，QtScrcpy 成功投屏；连续 3 分钟监测中 ADB 状态变化为 0 次。==

==HiSuite 及其旧过滤驱动是排查过程中引入的额外问题，但最终的底层枚举故障固定出现在 `HS01`：该端口先后出现设备描述符失败、配置描述符失败、Code 43 和复合设备 Code 10。重启电脑与重置根集线器后仍可复现，而同一平板、同一软件环境换到 `HS02` 后立即恢复，因此端口／控制器路径是本次最终定位到的关键变量。==

## 2. 典型症状

- 插线后的前几秒，Windows 反复播放 USB 接入和断开提示；
- 偶尔弹出“无法识别 USB 设备”；
- QtScrcpy 设备列表暂时消失，拔插后有时仍不出现；
- 文件资源管理器自动打开 MatePad 的“传输文件”窗口，约一秒后又关闭；
- 连接恢复后看似一切正常，但 ADB 的 `transport_id` 已经改变；
- 晃动 USB-A 或 Type-C 接头不能稳定复现。

“晃动不复现”不能完全排除线材问题。USB 充电线芯可能稳定，而高速数据线芯仍可能存在信号质量问题。是否为物理链路故障，应通过换线、换端口、换电脑交叉验证，而不是仅凭晃动测试判断。

## 3. 按层级诊断，而不是反复重装软件

### 3.1 第一层：Windows 是否识别出 USB 设备

先查看当前设备：

```powershell
Get-PnpDevice -PresentOnly |
  Where-Object {
    $_.InstanceId -match 'VID_12D1&PID_107E|VID_0000&PID_000[23]'
  } |
  Format-Table Status, Class, FriendlyName, InstanceId, Problem -AutoSize
```

本次出现过：

- `Unknown USB Device (Device Descriptor Request Failed)`；
- `Unknown USB Device (Configuration Descriptor Request Failed)`；
- `VID_0000&PID_0002` 或 `VID_0000&PID_0003`；
- Code 43。

这种情况下，Windows 连厂商和产品描述符都未正确取得，故障发生在 ADB 之前。此时反复执行 `adb kill-server`、修改 QtScrcpy 参数或重新授权 USB 调试没有意义。

### 3.2 第二层：USB 复合设备驱动

重启后曾出现：

```text
无法在此设备上加载驱动程序
ew_usbccgpfilter.sys
```

进一步确认：

- 驱动服务：`ew_usbccgpfilter`；
- 显示名称：`HwHandSet_CompositeFilter`；
- 驱动包：`oem128.inf`；
- 版本：1.0.9.0，2016 年；
- INF 会为华为 `PID_107E` 的复合 USB 设备添加 `UpperFilters=ew_usbccgpfilter`。

Windows 安全性阻止该过滤驱动加载后，`USB Composite Device` 出现 Code 39，所有子接口都会连带异常。

正确处理顺序：

1. 先导出驱动包、INF、SYS 和相关注册表作为备份；
2. 删除当前与残留的华为设备实例；
3. 从 Driver Store 删除问题驱动包；
4. 删除对应驱动服务；
5. 重新扫描设备；
6. 验证父设备改用微软 `usb.inf` 和 `usbccgp`；
7. 保持“内存完整性”等 Windows 安全设置开启。

不要为了加载旧驱动而关闭 Windows 安全功能。应移除不兼容的过滤驱动，让设备回到微软通用 USB 驱动链路。

### 3.3 第三层：逐个检查 MTP、ADB 和存储接口

正常情况下应看到：

```text
MatePad                  WPD        OK
USB Composite Device     USB        OK
ADB Interface            USBDevice  OK
USB Mass Storage Device  USB        OK
```

本次 MTP 接口先后出现过：

- Code 28：驱动未安装；
- Code 10：设备无法启动；
- 设备硬件 ID：`USB\VID_12D1&PID_107E&MI_00`；
- 兼容 ID：`USB\MS_COMP_MTP`。

HiSuite 携带的旧 `mtp.inf` 没有直接列出该 PID。重新枚举后，Windows 最终匹配内置 `wpdmtp.inf`，设备名称变为 `MatePad`，状态恢复正常。

若文件资源管理器窗口自动打开后又立刻关闭，应同时检查 ADB：如果 `transport_id` 改变，且 QtScrcpy 投屏窗口也关闭，就说明确实发生过 USB 重新枚举，而不只是自动播放窗口误弹。

### 3.4 第四层：ADB 与 QtScrcpy

QtScrcpy 3.3.3 自带的 ADB 为 33.0.2。排查时曾用 Google 官方 Platform-Tools 中的 ADB 37.0.0进行对照：

```ini
AdbPath=C:/path/to/platform-tools/adb.exe
```

==ADB 37 适合脱离 QtScrcpy 做诊断，但它没有修复本次掉线。最终为减少多个 ADB 进程与版本混用，QtScrcpy 已恢复使用其自带 ADB 33.0.2，`AdbPath=` 留空；稳定投屏验证也是在这一配置下完成的。==

检查设备：

```powershell
adb devices -l
```

状态含义：

- `device`：链路和授权正常；
- `offline`：USB 接口仍存在，但 ADB 会话异常；
- `unauthorized`：需要在平板确认 RSA 授权；
- 完全为空：先检查 PnP 和 USB 枚举，不要先责怪 QtScrcpy。

## 4. 华为 USB 功能组合的特殊性

平板报告的配置为：

```text
hisuite,mtp,mass_storage,adb
```

尝试执行：

```powershell
adb shell svc usb setFunctions
adb shell svc usb setFunctions ptp
```

并不能可靠地把设备收敛为“仅 ADB”。EMUI 会恢复自己的组合配置，甚至触发另一轮 USB 重新枚举，使父设备从带序列号的身份切换为通用端口身份，并造成 ADB `offline` 或 MTP Code 10。

==因此，正式上课前不要使用 `svc usb setFunctions` 临时切换功能。本机最终稳定配置不是强制保留完整的 HiSuite/MTP/虚拟光驱组合，而是恢复用户原先的“仅充电”用途，同时开启“USB 调试”和“仅充电模式下允许 ADB 调试”。“传输文件”会建立 MTP、HiSuite 虚拟光驱和 ADB 等多个子接口；本次曾出现资源管理器自动弹出 `E:`、虚拟光驱 I/O 错误并拖累整个复合设备的现象。==

## 5. 容易漏掉的电源管理设置

通过 `powercfg /Q SCHEME_CURRENT` 发现，虽然之前曾在设备管理器中调整 USB 电源管理，但当前电源计划的“USB 选择性暂停”仍然是启用状态：

```text
USB 设置：2a737441-1930-4402-8d77-b2bebba308a3
USB 选择性暂停：48e6b7a6-50f5-4782-a5d4-53bb8f07e226
当前交流设置：1（启用）
当前直流设置：1（启用）
```

禁用交流和电池模式：

```powershell
$sub = '2a737441-1930-4402-8d77-b2bebba308a3'
$setting = '48e6b7a6-50f5-4782-a5d4-53bb8f07e226'

powercfg /SETACVALUEINDEX SCHEME_CURRENT $sub $setting 0
powercfg /SETDCVALUEINDEX SCHEME_CURRENT $sub $setting 0
powercfg /SETACTIVE SCHEME_CURRENT
```

修改后必须重新查询，确认交流与直流设置索引都为 `0`。该设置会轻微增加电池耗电，但长时间线上授课通常应接通电源，稳定性更重要。

## 6. 无效或风险较高的尝试

### 6.1 在 Code 43 时反复重启 ADB

当 Windows 显示 `VID_0000` 时，设备还未进入 ADB 层，重启 ADB 服务不会修复描述符请求失败。

### 6.2 把问题全部归因于 QtScrcpy

QtScrcpy 依赖 ADB。只要 `adb devices -l` 中没有设备，QtScrcpy 就不可能连接。QtScrcpy 的旧 ADB 值得更新，但不能解释 Windows 的 Code 39、Code 43 和描述符失败。

### 6.3 为兼容旧驱动而关闭安全设置

不应通过关闭内存完整性来加载 `ew_usbccgpfilter.sys`。正确方案是移除旧过滤驱动并使用微软通用驱动。

### 6.4 混淆“系统命令强制切换”与“平板界面选择仅充电”

==通过 `adb shell svc usb setFunctions ...` 强制切换 USB 功能会主动断开 ADB，并可能触发固件重新枚举，不适合正式上课时使用。但这不等于平板界面中的“仅充电”不可用。本次最终稳定方案恰恰是：在平板 USB 通知中选择“仅充电”，并开启“仅充电模式下允许 ADB 调试”。二者必须区分。==

### 6.5 只进行几分钟稳定性测试

一次 45 秒和一次 3 分钟的投屏测试都完全正常，但随后仍发生了一次完整重连。偶发性故障必须持续监控，短测只能证明“当前状态正常”。

## 7. 推荐的标准排查流程

1. 关闭 HiSuite、QtScrcpy、Android Studio 和其他可能调用 ADB 的程序；
2. 使用 Google 官方 ADB 执行 `adb devices -l`；
3. 同时检查 PnP 父设备及各子接口；
4. ==出现 `VID_0000`、设备／配置描述符失败或 Code 43 时，记录 `Location Paths` 与 `Port_#`，优先更换物理 USB 端口，而不只是更换线材；==
5. 出现 Code 39 时，检查 `UpperFilters` 和被拦截的过滤驱动；
6. 父设备正常、ADB 为空时，再检查 ADB 驱动和 RSA 授权；
7. MTP Code 28/10 时，检查 `wpdmtp.inf` 的匹配和启动结果；
8. 检查电源计划中的 USB 选择性暂停，而不只看设备管理器复选框；
9. ==确保电脑上只运行一个 ADB 服务器；诊断时可用官方 ADB，正式使用时也可以回到 QtScrcpy 自带 ADB，关键是不要混用；==
10. 进行至少 30 分钟的带视频负载测试，并记录每次状态变化。

## 8. 实时监控方法

仅在状态变化时记录 ADB，避免产生大量无效日志：

```powershell
$last = $null
while ($true) {
    $line = adb devices -l |
        Where-Object { $_ -match '^8UXNU' } |
        Select-Object -First 1

    if (-not $line) { $line = 'ABSENT' }

    if ($line -ne $last) {
        "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff')] $line"
        $last = $line
    }

    Start-Sleep -Milliseconds 500
}
```

重点记录：

- 从 `device` 变为 `ABSENT` 的精确时间；
- 恢复后的 `transport_id` 是否改变；
- 同一时刻是否出现 `VID_0000`、Code 43 或 MTP Code 10；
- QtScrcpy 的投屏窗口是否同时关闭；
- 资源管理器是否自动打开或关闭 MatePad。

## 9. 用于正式授课的可靠性建议

- 主通道：当前 USB 有线投屏；
- ==固定使用已验证稳定的 `HS02` USB-A 端口，不再把平板接回出现描述符失败的 `HS01`；==
- ==平板固定选择“仅充电”，同时保持两个 USB 调试选项开启；==
- 备用通道：提前配置无线 ADB，或让平板直接加入会议共享屏幕；
- 同一份 PDF 同时保存在电脑和平板；
- 不在上课前临时安装 HiSuite、切换 USB 功能或更新驱动；
- 正式使用前做一次与实际课程等长的压力测试；
- 若再次出现断连，先保留时间戳和监控日志，不要立刻连续拔插，以免覆盖现场。

## 10. 当前验证状态

截至 2026-07-22：

- 旧华为过滤驱动已移除；
- Windows 安全设置保持开启；
- ==HiSuite 已卸载，未恢复被 Windows 安全性阻止的 `ew_usbccgpfilter.sys`；==
- ==QtScrcpy 最终恢复使用自带 ADB 33.0.2，避免与诊断用 ADB 37 混用；==
- ==原 USB 端口定位为 `Port_#0001 / HS01`，在该路径上反复出现 `USB\DEVICE_DESCRIPTOR_FAILURE`、`USB\CONFIG_DESCRIPTOR_FAILURE`、Code 43 和 Code 10；==
- ==换到另一个 USB-A 端口后，位置变为 `Port_#0002 / HS02`，父复合设备状态为 `Started`；==
- ==ADB 首次显示 `unauthorized`，在平板重新确认 RSA 后变为 `device`；==
- ==QtScrcpy 已成功显示平板画面，连续 3 分钟监测中 ADB 状态变化 0 次，QtScrcpy 进程保持响应；==
- ==平板使用“仅充电 + USB 调试 + 仅充电模式下允许 ADB 调试”；未使用的 MTP 子接口仍可能显示 Code 28，但不影响 ADB 投屏，不应为此重新安装 HiSuite；==
- USB 选择性暂停已在交流和电池模式下禁用；
- ==QtScrcpy 当前使用较保守的 4 Mbps 码率，待完成与实际课程等长的压力测试后再考虑提高。==

<!-- ai_provenance: source=codex; date=2026-07-22; verification=user-confirmed; retrieved_notes="非笔记内容/工作流程组织经验/QtScrcpy与华为平板USB反复断连排查复盘.md" -->

==本次已经恢复可用，但 3 分钟测试仍不能替代 2～4 小时的真实授课压力测试。若 `HS02` 后续再次出现 `VID_0000` 或 Code 43，再用另一台电脑交叉测试，以区分平板 Type-C 控制器、电脑 USB 控制器和线材信号质量问题；在没有新证据前，不再重装 HiSuite 或批量更换驱动。==

## 参考资料

- [Android SDK Platform-Tools 官方发布页](https://developer.android.com/tools/releases/platform-tools)
- [scrcpy 官方仓库](https://github.com/Genymobile/scrcpy)
- [QtScrcpy 官方仓库](https://github.com/barry-ran/QtScrcpy)
- [华为 HiSuite 官方下载与版本说明](https://consumer.huawei.com/cn/support/hisuite/)
