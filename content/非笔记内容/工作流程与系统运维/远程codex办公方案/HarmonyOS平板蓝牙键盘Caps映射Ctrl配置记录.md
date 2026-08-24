# HarmonyOS 平板蓝牙键盘 Caps 映射 Ctrl 配置记录

> 目标：让 HarmonyOS/Android 平板上的外接蓝牙键盘把 `Caps Lock` 当作左 `Ctrl` 使用，从而通过 `Caps + Space` 触发系统的 `Ctrl + Space` 中英文切换，同时保留 `Caps + C/V/A` 等 Ctrl 快捷键。

<!-- ai_provenance: source=codex; date=2026-08-25; verification=checked -->

## 1. 已验证环境与结论

本方案已在以下环境实际安装并验证：

- 平板：华为 `BAH3-W09`
- 系统：HarmonyOS 3.0.0，底层 Android 10 / API 29
- 蓝牙键盘：`B.O.W-3.0`
- 键盘标识：Vendor `25a7`，Product `faa3`
- 输入法：华为系统输入法，未被替换

最终采用 **ExKeyMo 物理键盘布局 APK**。它利用 Android 原生 KCM（Key Character Map）覆盖层完成改键：

```text
type OVERLAY

# Modifications made by ExKeyMo project:
map key 58 CTRL_LEFT
```

其中 Linux 扫描码 `58` 是 Caps Lock，映射目标是 Android 的 `CTRL_LEFT`。该方案不需要 Root、不修改 `/system`，也不需要常驻无障碍服务。

## 2. 为什么选择这个方案

HarmonyOS 3 的设置中没有新版 Android 的“修饰键”自定义入口。直接修改 `/system/usr/keylayout/Generic.kl` 需要 Root，而 Key Mapper 等按键映射应用在 Android 10 上可能要求启用它自己的输入法，从而干扰中文输入。

ExKeyMo 安装后只是向系统注册额外的“实体键盘布局”，不是新的输入法，因此可以继续使用小艺输入法或其他中文输入法。

相关资料：

- [ExKeyMo 在线 APK 生成器](https://ris58h.github.io/exkeymo/)
- [ExKeyMo 源代码](https://github.com/ris58h/exkeymo)
- [ExKeyMo 旧版仓库与预生成 APK](https://github.com/ris58h/exkeymo-server)
- [Android KCM 官方文档](https://source.android.com/docs/core/interaction/input/key-character-map-files)
- [华为关于实体键盘 Ctrl+Space 切换语言的说明](https://consumer.huawei.com/cn/support/content/zh-cn15911099/)

## 3. 更换平板后的完整操作

### 3.1 先确认系统原始快捷键

在任意输入框中连接蓝牙键盘，先测试物理 `Ctrl + Space`：

- 如果能够切换中英文，后面的 Caps→Ctrl 映射即可把它变成 `Caps + Space`。
- 如果 `Ctrl + Space` 本身不能切换，先检查输入法语言、实体键盘布局和华为输入法设置；此时问题不在 Caps 映射。
- 部分普通输入框可能使用 `Ctrl + Shift`，映射完成后对应组合是 `Caps + Shift`。

### 3.2 用 ADB 识别新平板和键盘

打开开发者选项和 USB 调试，连接电脑后执行：

```powershell
adb devices -l

$serial = '<adb devices 显示的平板序列号>'
adb -s $serial get-state
adb -s $serial shell getprop ro.product.model
adb -s $serial shell getprop ro.build.version.release
adb -s $serial shell getprop ro.build.version.sdk
adb -s $serial shell dumpsys input
```

在 `dumpsys input` 输出中找到蓝牙键盘，记录：

- 设备名，例如 `B.O.W-3.0`
- `vendor` 与 `product`
- `Path`，例如 `/dev/input/event6`；编号每次连接都可能改变，不能写死
- `KeyLayoutFile`、`KeyCharacterMapFile`
- `HaveKeyboardLayoutOverlay`

配置前通常会看到：

```text
KeyLayoutFile: /system/usr/keylayout/Generic.kl
KeyCharacterMapFile: /system/usr/keychars/Generic.kcm
HaveKeyboardLayoutOverlay: false
```

### 3.3 获取 Caps→Ctrl 布局 APK

优先使用 ExKeyMo 官方在线生成器，在简单模式中选择：

```text
Caps Lock → Left Ctrl
```

也可以在高级模式中使用：

```text
type OVERLAY
map key 58 CTRL_LEFT
```

旧版官方仓库提供了预生成的 `ExKeyMo-caps2ctrl.zip`。本次使用并验证的 APK 信息如下：

```text
应用名：ExKeyMo Keyboard Layout
包名：ris58h.exkeymo_keyboard_layout
版本：1.0
minSdkVersion：16
targetSdkVersion：29
APK SHA-256：F920CB510ED53507F57445451D639B0CBA5AAAB7A66351856442A87A023610D1
```

该 APK 的 Manifest 没有申请权限，只注册了：

```text
android.hardware.input.action.QUERY_KEYBOARD_LAYOUTS
```

如果以后重新下载的文件哈希不同，不一定代表有问题，但应重新检查来源、签名、权限和 KCM 内容，不要直接从不明 APK 网站安装。

### 3.4 安装 APK

```powershell
$serial = '<平板序列号>'
$apkPath = '<ExKeyMo Keyboard Layout.apk 的绝对路径>'

adb -s $serial install -r $apkPath
adb -s $serial shell pm path ris58h.exkeymo_keyboard_layout
```

正常情况会返回 `Success`。华为系统偶尔不会及时输出安装结果，只要 `pm path` 返回 `/data/app/.../base.apk`，就说明已经安装成功，不要连续重复安装。

### 3.5 为蓝牙键盘启用 ExKeyMo Layout

保持蓝牙键盘连接，打开：

```text
设置 → 系统和更新 → 语言和输入法 → 实体键盘
```

也可以直接通过 ADB 打开：

```powershell
adb -s $serial shell am start -a android.settings.HARD_KEYBOARD_SETTINGS
```

然后依次操作：

1. 点击 `B.O.W-3.0` 或当前键盘名称。
2. 点击“添加键盘布局”。
3. 勾选 `ExKeyMo Layout`，点击右上角确认。
4. 返回“选择键盘布局”弹窗。
5. **再次点击 `ExKeyMo Layout`，将当前布局从“自动”切换为 ExKeyMo。**

第 5 步是最容易遗漏的地方：在“添加键盘布局”页面勾选，仅表示把它加入候选列表；还需要回到上一层把它真正选为当前布局。

## 4. 验证是否生效

### 4.1 设置页面验证

“实体键盘”页面中，键盘名称下方应显示：

```text
ExKeyMo Layout
```

而不是“自动”。

### 4.2 ADB 验证

```powershell
adb -s $serial shell dumpsys input
```

找到当前蓝牙键盘，其状态应变为：

```text
HaveKeyboardLayoutOverlay: true
```

这表示系统已经实际加载 KCM 覆盖层。只看到 APK 已安装、但这里仍是 `false`，说明布局尚未应用到该键盘。

### 4.3 实际按键验收

在文本输入框中逐项测试：

- `Caps + Space`：等价于 `Ctrl + Space`，切换中英文。
- `Caps + C`：复制。
- `Caps + V`：粘贴。
- `Caps + A`：全选。
- 单按 Caps 不再锁定大写；大写字母改用 Shift。

## 5. 常见故障

### 5.1 设置中找不到 ExKeyMo Layout

依次检查：

```powershell
adb -s $serial shell pm path ris58h.exkeymo_keyboard_layout
adb -s $serial shell cmd package resolve-activity --brief -a android.settings.HARD_KEYBOARD_SETTINGS
adb -s $serial shell dumpsys input
```

还要确认蓝牙键盘此刻保持连接。系统通常只为当前已连接的实体键盘显示布局入口。

### 5.2 已勾选，但 Caps 仍然是大写锁定

回到“选择键盘布局”弹窗检查当前项。最常见原因是只完成了“添加布局”，但当前选项仍然是“自动”。正确状态应同时满足：

```text
设置页摘要：ExKeyMo Layout
HaveKeyboardLayoutOverlay: true
```

### 5.3 Caps 已变成 Ctrl，但不能切换中英文

先用键盘原来的 Ctrl 测试：

- 原始 `Ctrl + Space` 也失败：检查输入法及语言配置。
- 原始 `Ctrl + Space` 成功、`Caps + Space` 失败：重新检查布局是否为 ExKeyMo，以及覆盖层是否为 `true`。
- 某些应用成功、某些应用失败：可能是应用自行拦截快捷键，应在系统设置或普通文本框中对照测试。

### 5.4 重连或重启后失效

通常布局选择会保留，但系统是按输入设备描述符保存选择的。更换键盘、蓝牙配对记录变化或换新平板后，需要重新进入“实体键盘”页面选择 ExKeyMo。

如果 APK 仍在但覆盖层为 `false`，重新选择一次布局即可，不必重复安装。

### 5.5 恢复默认行为

在“实体键盘”设置中把当前布局改回“自动”，Caps 即恢复为大写锁定。确认不再需要该布局后，才卸载：

```powershell
adb -s $serial uninstall ris58h.exkeymo_keyboard_layout
```

卸载会移除该自定义布局；这是恢复操作，不应在排障时随意执行。

## 6. 迁移到新平板时的最短清单

1. 连接 B.O.W. 蓝牙键盘，确认原始 `Ctrl + Space` 可切换语言。
2. 安装已检查的 ExKeyMo Caps→Ctrl APK。
3. 打开“实体键盘”，先添加 `ExKeyMo Layout`，再把它选为当前布局。
4. 用 `dumpsys input` 确认 `HaveKeyboardLayoutOverlay: true`。
5. 测试 `Caps + Space`、`Caps + C/V/A`。
6. 若失败，先判断是“映射没有加载”还是“输入法本身不响应 Ctrl+Space”。
