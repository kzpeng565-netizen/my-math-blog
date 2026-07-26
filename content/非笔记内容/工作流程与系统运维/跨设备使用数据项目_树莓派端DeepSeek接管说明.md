# 跨设备使用数据采集项目：树莓派端接管与配置说明

> 面向执行者：DeepSeek  
> 更新时间：2026-07-27  
> 项目状态：手机端与 Windows 电脑端已经能够上传数据；下一步是完成树莓派端的可靠接收、规范存储、去重、汇总、监控与备份。  
> 公网入口：`https://pi.taild4d3f7.ts.net/upload`

---

## 0. 给 DeepSeek 的执行要求

这是一个已经投入测试的个人系统，不是从零开始的示例项目。执行时必须遵守以下规则：

1. **先检查，再修改。**不得在未查看现有目录、脚本、systemd 服务、Funnel 配置和最近日志前重写系统。
2. **不得破坏现有手机端和电脑端上传。**优先兼容现有请求路径、文件名和数据格式，不要求客户端重新配置。
3. **不得执行破坏性命令。**不得删除现有数据、重装系统、执行 `tailscale funnel reset`、覆盖未知配置或清空数据库。
4. **修改前必须备份。**备份现有脚本、配置、systemd 单元、数据库和关键数据文件。
5. **树莓派是 Raspberry Pi 3B。**方案应轻量、依赖少、内存占用低，不引入 Docker、Kubernetes、复杂消息队列或大型前端。
6. **第一阶段只做客观数据处理。**不加入 AI 评价、自动锁机、计划管理或行为干预。
7. 每完成一个阶段，先运行验收测试并报告结果，再进入下一阶段。
8. 对无法从现有系统确认的内容，必须标记为“待确认”，不得自行猜测。

---

## 1. 项目目标

建立一个低维护、跨设备的个人数字使用记录系统：

```text
vivo 手机（Automate）
        │
        │ HTTPS 上传
        ▼
Tailscale Funnel
https://pi.taild4d3f7.ts.net/upload
        │
        ▼
树莓派本地接收服务
        │
        ├─ 保存最新原始文件
        ├─ 校验 JSON/JSONL
        ├─ 去重并写入 SQLite
        ├─ 按自然半小时汇总
        └─ 输出可供后续 AI 或 Obsidian 读取的结果

Windows 电脑（ActivityWatch + 已完成的上传脚本）
        │
        └──────────────────────→ 同一树莓派后端
```

系统需要回答：

- 每个自然半小时内，手机和电脑分别使用了哪些应用；
- 亮屏但无操作、息屏、电脑 AFK 等状态分别持续多久；
- 各应用可以被归入数学学习、沟通、信息浏览、短视频、娱乐、系统等类别；
- 上传链路是否中断；
- 数据是否完整、重复或异常。

---

## 2. 已完成的部分

### 2.1 手机端

手机为 vivo Android 设备，使用 **Automate** 图形化流程采集，不开发自制 Android App。

已经完成的采集内容：

#### 前台应用事件

```json
{"timestamp":"2026-07-24T14:00:58+08:00","device":"phone","event":"foreground","package":"com.tencent.mm"}
```

本地文件通常为：

```text
Documents/PhoneUsage/foreground.jsonl
```

#### 亮屏、息屏事件

```json
{"timestamp":"2026-07-24T14:01:15+08:00","device":"phone","event":"screen","state":"off"}
{"timestamp":"2026-07-24T14:01:20+08:00","device":"phone","event":"screen","state":"on"}
```

本地文件通常为：

```text
Documents/PhoneUsage/screen.jsonl
```

#### 心跳事件

```json
{"timestamp":"2026-07-24T14:16:47+08:00","device":"phone","event":"heartbeat"}
```

本地文件通常为：

```text
Documents/PhoneUsage/heartbeat.jsonl
```

手机流程的主要结构：

```text
Flow beginning
→ 创建目录
→ Fork

支路1：
App foreground
→ 写 foreground.jsonl
→ 返回等待

支路2：
Device interactive
├─ screen on  → 写 screen.jsonl
└─ screen off → 写 screen.jsonl

支路3：
写 heartbeat.jsonl
→ 上传三个文件
→ Delay
→ 循环
```

已验证：

- JSONL 格式正确；
- 前台应用切换可以记录；
- 息屏和亮屏可以记录；
- 息屏期间心跳仍能运行；
- 三个文件能够分开保存；
- 上传已经完成配置；
- Automate 已配置开机恢复和后台运行。

手机端会定期上传**完整文件快照**，而不是只上传新增行。因此树莓派端必须能够去重，不能把每次完整文件都重复插入数据库。

### 2.2 Windows 电脑端

Windows 已安装并使用 ActivityWatch，电脑使用数据已经完成上传。

预期涉及的数据源包括：

- `aw-watcher-window`：当前窗口应用和标题；
- `aw-watcher-afk`：`afk` / `not-afk`；
- `aw-watcher-web`：浏览器网址或域名，若当前上传脚本已启用。

**重要：当前上下文没有给出电脑上传脚本的确切文件名、URL 子路径和最终 JSON 格式。DeepSeek 必须从树莓派现有文件、Windows 上传脚本或服务日志中识别，不能自行假设。**

ActivityWatch 原始事件一般包含：

```json
{
  "timestamp": "2026-07-24T06:00:00Z",
  "duration": 12.5,
  "data": {
    "app": "msedge.exe",
    "title": "..."
  }
}
```

电脑端已经能够上传，因此本任务不应重新设计或替换 Windows 客户端。

### 2.3 网络入口

当前使用 Tailscale Funnel，入口为：

```text
https://pi.taild4d3f7.ts.net/upload
```

这一地址不依赖家庭局域网 IP。树莓派搬到学校、更换 Wi-Fi 或获得新的局域网 IP 后，只要树莓派能够联网并重新连接 Tailscale，客户端地址通常不需要修改。

Funnel 是公网入口，因此后端必须有独立鉴权，不能仅依赖“别人不知道地址”。

---

## 3. 本阶段不做的内容

第一版树莓派端不得加入：

- 自制 Android App；
- 手机锁定、自动点击或强制退出应用；
- AI 自动评价；
- 新闻推荐或信息流；
- Web 管理后台；
- 复杂用户系统；
- Docker；
- 对外公开 ActivityWatch 的 `5600` 端口；
- 自动删除长期数据。

---

## 4. 目标架构

建议采用轻量结构：

```text
Tailscale Funnel
        │
        │ HTTPS
        ▼
127.0.0.1:8765
usage-receiver.service
        │
        ├─ incoming/latest/
        ├─ logs/
        └─ state/upload_state.json
                │
                ▼
usage-processor.service / timer
                │
                ├─ SQLite 去重
                ├─ 标准化事件
                └─ 数据完整性检查
                        │
                        ▼
usage-aggregate.service / timer
                        │
                        ├─ 半小时汇总
                        ├─ 每日汇总
                        └─ JSON/CSV 输出
```

后端只监听：

```text
127.0.0.1:8765
```

不要监听 `0.0.0.0`，避免同一局域网中的其他设备绕过 Funnel 直接访问接收端。

---

## 5. 建议目录结构

DeepSeek 应先检查现有目录。若已有 `/home/conrad/phone_usage` 或其他项目目录，优先在原项目上兼容升级。

若不存在现有项目，可使用：

```text
/home/conrad/usage-hub/
├── app/
│   ├── receiver.py
│   ├── processor.py
│   ├── aggregate.py
│   ├── db.py
│   └── config.json
├── data/
│   ├── incoming/
│   │   └── latest/
│   ├── database/
│   │   └── usage.sqlite3
│   ├── output/
│   │   ├── half_hour/
│   │   └── daily/
│   └── backup/
├── state/
│   └── upload_state.json
├── logs/
├── tests/
├── scripts/
├── README.md
└── .gitignore
```

权限要求：

- 项目目录归运行服务的普通用户所有；
- token 文件权限为 `600`；
- 数据库和原始数据不得由公网直接下载；
- 日志中不得输出上传 token。

---

## 6. 阶段 0：只读审计

DeepSeek 第一次接管时，先执行以下检查，不修改任何文件。

```bash
whoami
pwd
hostname
uname -a
cat /etc/os-release
free -h
df -h
python3 --version
tailscale version
tailscale status
sudo tailscale funnel status
```

检查监听端口：

```bash
sudo ss -ltnp
```

检查可能已有的项目和服务：

```bash
find /home/conrad -maxdepth 3 \
  \( -iname '*usage*' -o -iname '*activity*' -o -iname '*receiver*' \) \
  -print 2>/dev/null

systemctl list-unit-files | grep -Ei 'usage|activity|receiver|upload'
systemctl list-units --type=service --all | grep -Ei 'usage|activity|receiver|upload'
```

检查最近的 Funnel 和接收端日志：

```bash
sudo journalctl -u tailscaled -n 100 --no-pager
sudo journalctl --since '24 hours ago' --no-pager \
  | grep -Ei 'PUT|POST|upload|foreground|heartbeat|activitywatch'
```

若发现现有接收服务，继续查看：

```bash
systemctl cat <现有服务名>
sudo journalctl -u <现有服务名> -n 200 --no-pager
```

检查现有上传文件：

```bash
find /home/conrad -type f \
  \( -name '*.json' -o -name '*.jsonl' -o -name '*.db' -o -name '*.sqlite3' \) \
  -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' \
  2>/dev/null | sort
```

### 审计阶段的输出要求

DeepSeek 必须先报告：

1. 当前 Funnel 实际转发到哪个本地端口和路径；
2. 当前接收服务名称、运行用户和脚本路径；
3. 手机端实际请求路径和文件名；
4. 电脑端实际请求路径、文件名和数据格式；
5. 当前是否已有 SQLite；
6. 当前系统是否存在冲突端口；
7. 建议保留、修改或废弃哪些现有组件。

在得到这些结果前，不进入修改阶段。

---

## 7. 阶段 1：备份现状

确定现有路径后，创建带时间戳的备份。

示例：

```bash
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "/home/conrad/backups/usage-hub/$STAMP"
```

备份内容至少包括：

- 当前接收脚本；
- systemd 单元；
- Funnel 状态输出；
- token 配置；
- SQLite 数据库；
- 最近的原始上传文件；
- Windows 上传脚本的副本，若树莓派上有；
- 当前项目的 `git status` 和 `git diff`。

示例：

```bash
sudo tailscale funnel status \
  > "/home/conrad/backups/usage-hub/$STAMP/funnel-status.txt"

sudo systemctl cat <服务名> \
  > "/home/conrad/backups/usage-hub/$STAMP/service.txt"
```

数据库备份应优先使用 SQLite 自带备份命令，而不是运行中直接复制：

```bash
sqlite3 /path/to/usage.sqlite3 \
  ".backup '/home/conrad/backups/usage-hub/$STAMP/usage.sqlite3'"
```

---

## 8. 阶段 2：接收 API

### 8.1 必须提供的接口

```text
GET  /health
GET  /upload/health
PUT  /upload/<filename>
POST /upload/<filename>
```

由于 Funnel 的 `--set-path=/upload` 可能影响后端看到的路径，接收端应兼容以下两种形式：

```text
/upload/foreground.jsonl
/foreground.jsonl
```

但必须只允许明确白名单中的文件名。

### 8.2 已知手机文件名

至少兼容：

```text
foreground.jsonl
screen.jsonl
heartbeat.jsonl
```

若平板随后加入，可兼容：

```text
tablet_foreground.jsonl
tablet_screen.jsonl
tablet_heartbeat.jsonl
```

### 8.3 电脑文件名

电脑文件名必须从现有系统识别后加入白名单，不得先写死猜测名称。

### 8.4 鉴权

沿用现有客户端已经配置的请求头，例如：

```text
X-Upload-Token: <secret>
```

服务端要求：

- 使用恒定时间比较；
- token 放在独立文件或环境文件中；
- 文件权限 `600`；
- token 不进入 Git；
- 日志不得记录完整 token；
- 错误 token 返回 `401`。

### 8.5 请求限制

接收端必须：

- 限制上传大小，例如单文件不超过 20 MB；
- 仅接受 UTF-8；
- JSONL 文件逐行解析；
- 任意一行无效时拒绝整个上传；
- 只接受白名单文件名；
- 防止 `../` 路径穿越；
- 请求成功返回 JSON；
- 使用临时文件和 `os.replace()` 原子替换；
- 旧文件只有在新文件完整校验成功后才被替换；
- 记录接收时间、文件名、字节数、行数和 SHA-256；
- 不将原始请求正文写入普通日志。

成功响应示例：

```json
{
  "ok": true,
  "file": "foreground.jsonl",
  "bytes": 10240,
  "lines": 90,
  "sha256": "..."
}
```

### 8.6 重复快照处理

手机每次上传完整 JSONL 文件，因此接收端应先计算 SHA-256：

- 若与上次完全相同，返回 `200`，但不重复处理；
- 若不同，原子替换 `incoming/latest/<filename>`；
- 更新 `upload_state.json`；
- 通知处理程序读取新快照。

不要把每 15 分钟的完整快照全部永久归档，否则会重复占用大量空间。

---

## 9. 阶段 3：SQLite 标准化与去重

建议数据库：

```text
data/database/usage.sqlite3
```

### 9.1 建议表结构

#### uploads

记录每次有效上传：

```sql
CREATE TABLE uploads (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    device TEXT,
    source TEXT,
    received_at TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    bytes INTEGER NOT NULL,
    lines INTEGER NOT NULL,
    UNIQUE(filename, sha256)
);
```

#### events

存储标准化事件：

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_key TEXT NOT NULL UNIQUE,
    device TEXT NOT NULL,
    source TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    duration REAL,
    event_type TEXT NOT NULL,
    app TEXT,
    title TEXT,
    url TEXT,
    state TEXT,
    raw_json TEXT NOT NULL,
    inserted_at TEXT NOT NULL
);
```

#### half_hour_summary

```sql
CREATE TABLE half_hour_summary (
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    device TEXT NOT NULL,
    category TEXT NOT NULL,
    seconds REAL NOT NULL,
    generated_at TEXT NOT NULL,
    PRIMARY KEY (period_start, device, category)
);
```

#### source_health

```sql
CREATE TABLE source_health (
    source TEXT PRIMARY KEY,
    last_upload_at TEXT,
    last_event_at TEXT,
    last_heartbeat_at TEXT,
    status TEXT,
    detail TEXT
);
```

### 9.2 去重键

手机前台事件可使用：

```text
sha256(device + event_type + timestamp + package + state)
```

ActivityWatch 事件可使用：

```text
sha256(device + bucket_id + timestamp + duration + canonical_json(data))
```

所有重复插入采用：

```sql
INSERT OR IGNORE
```

### 9.3 时间处理

规则：

- 数据库统一保存带时区的 ISO 8601 时间；
- 手机上传的 `+08:00` 必须保留；
- ActivityWatch 若为 UTC，转换时不能丢失原始时间；
- 汇总使用用户所在时区 `Asia/Shanghai`；
- 自然半小时区间为：
  - `00:00–00:30`
  - `00:30–01:00`
  - …
- 跨半小时的事件必须拆分到两个区间。

---

## 10. 阶段 4：手机数据计算规则

手机数据由前台应用事件和屏幕事件共同解释。

### 10.1 基本算法

按时间合并排序：

```text
foreground 事件
screen on/off 事件
```

维护状态：

```text
current_app
screen_state
last_timestamp
```

区间 `[last_timestamp, current_timestamp)` 的归属规则：

- `screen_state == off`：计入 `screen_off`；
- `screen_state == on` 且已有 `current_app`：计入当前应用；
- 状态不足：计入 `unknown`，不得强行推断。

### 10.2 连续重复事件

例如：

```text
14:00:58 com.tencent.mm
14:01:03 com.tencent.mm
```

应当合并为同一个应用区间，不重复计算。

### 10.3 心跳用途

`heartbeat` 只用于判断采集流程是否存活，不计入使用时长。

健康判定建议：

- 最近 30 分钟有心跳：`healthy`；
- 30–45 分钟无心跳：`delayed`；
- 超过 45 分钟无心跳：`offline_or_killed`。

阈值必须放入配置文件，后续可调整。

### 10.4 “30 秒无触屏”规则

第一版不实现“30 秒不触屏即离开”。看视频、阅读、思考或通话都可能长时间没有触摸，这一规则会误判。

亮屏但长时间无应用变化可以保留为当前应用，也可以额外标记为 `possibly_idle`，但不能直接删除。

---

## 11. 阶段 5：电脑数据计算规则

### 11.1 ActivityWatch 数据源

优先使用：

- Window bucket：应用名和窗口标题；
- AFK bucket：是否离开电脑；
- Web bucket：浏览器域名，若现有上传包含。

### 11.2 有效使用区间

规则：

- `afkstatus == afk`：计入 `computer_afk`；
- `afkstatus == not-afk`：窗口事件可以计入应用使用；
- 浏览器窗口若有 Web Watcher 数据，用域名进一步分类；
- 没有 AFK 信息的区间标记为 `unknown`，不得默认全部活跃。

### 11.3 安全约束

不要通过 Funnel 暴露 ActivityWatch 本地服务器端口。ActivityWatch 的本地 REST API 应继续只在 Windows 本机访问，由现有 Windows 上传脚本抽取所需数据后推送到树莓派。

---

## 12. 阶段 6：分类配置

分类规则必须是外部配置，不要写死在处理代码中。

示例：

```json
{
  "android_packages": {
    "com.tencent.mm": "communication",
    "tv.danmaku.bili": "video",
    "com.zhihu.android": "information"
  },
  "windows_apps": {
    "obsidian.exe": "mathematics",
    "code.exe": "programming",
    "msedge.exe": "browser"
  },
  "domains": {
    "mathoverflow.net": "mathematics",
    "bilibili.com": "video"
  },
  "defaults": {
    "unknown_android": "unknown",
    "unknown_windows": "unknown"
  }
}
```

第一版建议分类：

```text
mathematics
programming
communication
information
video
short_video
entertainment
system
screen_off
computer_afk
unknown
```

分类修改后，应允许重新生成历史汇总，不必重新上传原始数据。

---

## 13. 阶段 7：输出文件

每个自然半小时生成一个统一 JSON，例如：

```json
{
  "period_start": "2026-07-27T14:00:00+08:00",
  "period_end": "2026-07-27T14:30:00+08:00",
  "devices": {
    "phone": {
      "communication": 180,
      "information": 420,
      "short_video": 300,
      "screen_off": 900
    },
    "windows": {
      "mathematics": 720,
      "browser": 240,
      "computer_afk": 840
    }
  },
  "health": {
    "phone": "healthy",
    "windows": "healthy"
  }
}
```

时间单位统一为秒。需要展示时再换算成分钟。

建议输出：

```text
data/output/half_hour/YYYY-MM-DD.jsonl
data/output/daily/YYYY-MM-DD.json
```

---

## 14. 阶段 8：systemd 服务

至少需要：

```text
usage-receiver.service
usage-processor.service
usage-processor.timer
usage-aggregate.service
usage-aggregate.timer
```

### 14.1 receiver

要求：

- 普通用户运行；
- 监听 `127.0.0.1:8765`；
- `Restart=on-failure`；
- 设置合理的重启间隔；
- 工作目录固定；
- token 通过只读环境文件加载；
- 日志进入 journald。

### 14.2 processor timer

建议每 5 分钟运行一次：

```text
OnCalendar=*:0/5
Persistent=true
```

### 14.3 aggregate timer

建议每小时的第 2 分和第 32 分运行：

```text
OnCalendar=*-*-* *:02,32:00
Persistent=true
```

延迟两分钟是为了等待客户端上传刚结束的自然半小时数据。

### 14.4 启用后检查

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now usage-receiver.service
sudo systemctl enable --now usage-processor.timer
sudo systemctl enable --now usage-aggregate.timer

systemctl is-enabled usage-receiver.service
systemctl is-active usage-receiver.service
systemctl list-timers --all | grep usage
```

---

## 15. 阶段 9：Funnel 配置

当前公网入口已经可用，DeepSeek 不得直接重置。

先检查：

```bash
sudo tailscale funnel status
sudo tailscale funnel status --json
```

目标状态应为：

```text
https://pi.taild4d3f7.ts.net/upload
→ http://127.0.0.1:8765
```

只有在现有配置错误或不持久时，才调整为后台模式。命令应根据当前安装版本的 `tailscale funnel --help` 确认。

当前版本常见形式为：

```bash
sudo tailscale funnel \
  --bg \
  --https=443 \
  --set-path=/upload \
  localhost:8765
```

执行前必须：

```bash
tailscale funnel --help
sudo tailscale funnel status
```

不要运行：

```bash
sudo tailscale funnel reset
```

除非已经备份当前状态并得到用户明确授权。

---

## 16. 阶段 10：验收测试

### 16.1 本地健康检查

```bash
curl -i http://127.0.0.1:8765/health
curl -i http://127.0.0.1:8765/upload/health
```

预期：

```text
HTTP/1.1 200
```

### 16.2 Funnel 健康检查

```bash
curl -i https://pi.taild4d3f7.ts.net/upload/health
```

预期：

```text
HTTP/2 200
```

### 16.3 未授权上传

```bash
printf '%s\n' \
'{"timestamp":"2026-07-27T10:00:00+08:00","device":"test","event":"heartbeat"}' \
> /tmp/test.jsonl

curl -i \
  -X PUT \
  --data-binary @/tmp/test.jsonl \
  https://pi.taild4d3f7.ts.net/upload/heartbeat.jsonl
```

预期：

```text
401 Unauthorized
```

### 16.4 正确 token 上传

不要在终端历史中直接暴露 token。建议临时读取：

```bash
TOKEN="$(cat /path/to/upload-token)"
```

然后：

```bash
curl -i \
  -X PUT \
  -H "X-Upload-Token: $TOKEN" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @/tmp/test.jsonl \
  https://pi.taild4d3f7.ts.net/upload/heartbeat.jsonl
```

预期：

```text
200 OK
```

### 16.5 无效 JSONL

上传包含损坏行的文件，预期：

```text
400 Bad Request
```

并且服务器上的旧有效文件保持不变。

### 16.6 重复上传

同一文件连续上传两次：

- 两次都返回 `200`；
- 第二次不重复插入事件；
- `events` 表行数不增加；
- 可记录一次“内容未变化”。

### 16.7 手机实机测试

确认：

1. 手机切换应用；
2. 息屏和亮屏；
3. 等待一个上传周期；
4. 树莓派收到新文件；
5. SQLite 出现新事件；
6. 半小时输出正常；
7. 心跳状态为 `healthy`。

### 16.8 Windows 实机测试

确认：

1. Windows 正常使用 5–10 分钟；
2. 暂时离开电脑触发 AFK；
3. 上传脚本运行；
4. 树莓派收到数据；
5. SQLite 没有重复；
6. 活跃和 AFK 时长能够区分。

### 16.9 重启测试

```bash
sudo reboot
```

重启后检查：

```bash
systemctl is-active usage-receiver.service
systemctl list-timers --all | grep usage
sudo tailscale funnel status
curl -i https://pi.taild4d3f7.ts.net/upload/health
```

全部恢复后才算完成。

---

## 17. 日志和状态检查

常用命令：

```bash
sudo journalctl -u usage-receiver.service -n 100 --no-pager
sudo journalctl -u usage-processor.service -n 100 --no-pager
sudo journalctl -u usage-aggregate.service -n 100 --no-pager
```

查看最近上传：

```bash
sqlite3 /path/to/usage.sqlite3 \
  "SELECT filename, received_at, lines, bytes
   FROM uploads
   ORDER BY received_at DESC
   LIMIT 20;"
```

查看数据源健康状态：

```bash
sqlite3 /path/to/usage.sqlite3 \
  "SELECT * FROM source_health;"
```

---

## 18. 备份策略

第一版建议：

- 每日备份 SQLite；
- 保留配置文件、脚本和 systemd 单元；
- 每次修改前创建手动备份；
- 不备份大量重复的完整上传快照；
- 不自动删除原始手机或电脑数据，直到系统稳定并得到用户确认。

数据库备份示例：

```bash
sqlite3 /path/to/usage.sqlite3 \
  ".backup '/home/conrad/backups/usage-$(date +%F).sqlite3'"
```

项目代码应使用 Git，但以下内容不得提交：

```text
token
*.sqlite3
incoming/
output/
logs/
backup/
```

---

## 19. 回滚方案

若新接收端出现问题：

1. 停止新服务；
2. 恢复旧 systemd 单元；
3. 恢复旧接收脚本；
4. 恢复原 Funnel 转发目标；
5. 启动旧服务；
6. 用手机和 Windows 各上传一次验证。

任何数据库迁移都必须保留原数据库副本，不得原地不可逆修改。

---

## 20. DeepSeek 最终必须交付的内容

完成后向用户提供：

1. 当前系统架构图；
2. 实际项目目录；
3. 所有服务名称；
4. Funnel 实际配置；
5. 手机和电脑实际上传路径；
6. 数据库结构；
7. 半小时汇总规则；
8. 分类配置文件位置；
9. 查看运行状态的命令；
10. 查看最新数据的命令；
11. 备份和恢复方法；
12. 完整验收结果；
13. 未解决问题和风险；
14. Git 提交记录。

---

## 21. 推荐执行顺序

```text
[ ] 只读审计
[ ] 报告现状
[ ] 备份现有系统
[ ] 确认手机和 Windows 实际协议
[ ] 完善接收端
[ ] 配置鉴权与白名单
[ ] 实现原子写入和 SHA-256
[ ] 建立 SQLite
[ ] 导入手机事件并去重
[ ] 导入 Windows ActivityWatch 事件并去重
[ ] 实现自然半小时汇总
[ ] 建立分类配置
[ ] 建立 systemd 服务和 timer
[ ] 检查并持久化 Funnel
[ ] 完成局部测试
[ ] 完成手机实机测试
[ ] 完成 Windows 实机测试
[ ] 完成断网、重复、错误数据测试
[ ] 完成树莓派重启测试
[ ] 写 README 和运维文档
[ ] Git 提交
```

---

## 22. 可直接交给 DeepSeek 的任务指令

```text
请接管这个跨设备数字使用数据项目的树莓派端。

不要立即修改。首先完整阅读本文，然后执行“阶段 0：只读审计”，检查当前目录、接收脚本、systemd 服务、Tailscale Funnel 配置、监听端口、最近上传日志、现有 JSONL 文件和 SQLite 数据库。

手机端和 Windows 电脑端已经能够上传，不要重新设计客户端，也不要改变现有上传地址。公网入口是：
https://pi.taild4d3f7.ts.net/upload

先确认手机和电脑当前真实使用的请求路径、文件名和数据格式。对未知内容不得猜测。报告现状和变更计划，完成备份后再修改。

目标是在 Raspberry Pi 3B 上建立轻量、可靠的接收、校验、去重、SQLite 存储、自然半小时汇总、健康监控、systemd 自启动和备份体系。后端只能监听 localhost，通过 Tailscale Funnel 暴露；必须保留 token 鉴权、文件名白名单、大小限制、JSONL 校验、原子替换和重复数据去重。

每完成一个阶段先运行验收并报告结果。不得删除现有数据，不得重置 Funnel，不得暴露 ActivityWatch 的本地端口，不得加入 AI 评价、锁机或额外功能。最终提交 README、运维命令、测试结果、回滚方法和 Git 提交。
```
