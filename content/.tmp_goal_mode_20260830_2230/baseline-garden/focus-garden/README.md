# 我的专注花园

仅供个人 Tailnet 使用的像素风专注游戏。正式实例运行在树莓派上。它会：

- 启动专注计时并调用 Cold Turkey 屏蔽配置好的网站；
- 每累计完成 40 分钟发放一份种植奖励；
- 通过 SSH 只读同步树莓派上的主动介入、Next Action 完成闭环和早睡记录；
- 让用户选择植物种类，自动随机安排种植位置；
- 从 `5×5` 开始，在花园填满时自动扩展为 `7×7`、`9×9`……
- 以花园原生菜单整合 Next Action：生成建议、记录开始/拒绝/结果、查看最近三条报告和提交问题反馈。

## 正式访问

电脑或手机连接 Tailscale 后访问 `https://pi.taild4d3f7.ts.net:8460/`。Pi 应用只监听 `127.0.0.1:8838`，8460 使用 tailnet-only Tailscale Serve，严禁启用 Funnel。

Pi 正式服务使用安全模拟专注模式：计时和奖励正常工作，但不会替 Windows 调用 Cold Turkey。

## Next Action 集成

花园只代理 Pi loopback `http://127.0.0.1:8767` 上一组固定的 Next Action API；不会读取其密码、环境文件或数据目录，也不接受浏览器传入任意上游地址。首次使用时仍在花园页面输入原有 Next Action 密码，登录 cookie 仅转发回同一台 Pi 的 Next Action 服务，不写入花园数据库或配置。

本地开发副本已实现该菜单；部署到 Pi 后，必须先运行 Python 测试、`node --check static\app.js`，重启 `focus-garden.service`，再从 `:8460` 用真实登录与反馈闭环验收。不要仅为连通性点击“为我找下一步”，它会触发一次真实模型请求。

## Windows 开发副本

双击 `run.ps1`。本地副本只监听 `127.0.0.1:8838`，不要与 Pi 权威实例同时写存档。

首次开发验收请双击 `run-safe-test.ps1`；该入口不会真正执行 Cold Turkey。

## 素材边界

`static/assets/plants/` 第一版使用本机已安装 Minecraft Education Edition 的原版纹理，只限本地个人使用，不得上传、分享或分发。第二版可在保持文件名/植物 ID 不变的情况下逐步替换为原创素材。

## 扩展

- 新植物：复制 PNG 到 `static/assets/plants/`，并编辑 `config/plants.json`。
- 新专注模式：编辑 `config/focus_profiles.json`；block 必须已经存在于 computer-intervention-agent 的 allowlist。
- 早睡阈值：编辑 `config/settings.json` 的 `early_sleep_cutoff`。
- 新奖励规则：在 `focus_garden/pi_sync.py` 中生成带有稳定唯一 `id` 的标准事件；SQLite 会自动去重。

## 数据

Pi 权威存档位于 `/home/conrad/services/focus-garden/data/focus-garden.sqlite3`。`focus-garden-backup.timer` 每分钟生成一致性快照，经 Syncthing 单向同步到 Windows 的 `D:\MyFocusGardenArchive\focus-garden.sqlite3`。
