# ActivityWatch 维护说明

<!-- ai_provenance: source=codex; date=2026-07-24; verification=user-confirmed; retrieved_notes="" -->

## 1. 当前目标

第一版只区分：

- 工作；
- 数学学习；
- 系统维护；
- 家教；
- 浏览器；
- 娱乐；
- 未分类。

==Edge 和 Chrome 默认归为“浏览器”；网页版 ChatGPT 也保持为“浏览器”，只有 ChatGPT 桌面应用归入“工作”。知乎、Reddit、YouTube、Twitter、X 的标题规则层级更深，会覆盖“浏览器”而归入直接娱乐；B 站和小红书归入可能娱乐。==

## 2. 运行架构

```text
aw-watcher-window ─┐
                   ├─> aw-server ─> SQLite 数据库
aw-watcher-afk ────┘       │
                            └─> Web UI（localhost:5600）
                                  │
                                  └─> 分类规则 classes
```

- `aw-watcher-window`：每秒左右记录当前应用名和窗口标题。
- `aw-watcher-afk`：根据键盘、鼠标活动判断是否离开电脑。
- `aw-server`：保存原始事件并向网页界面提供接口。
- Web UI：查询原始事件，应用分类规则，再显示时间统计。

分类不会改写历史事件。历史记录仍然是原始的应用名和窗口标题；修改规则后，重新查看同一段历史时间，分类结果也会跟着改变。

## 3. 本机实际文件

程序位置：

```text
D:\ActivityWatch\
```

用户数据与配置根目录：

```text
C:\Users\15345\AppData\Local\activitywatch\activitywatch\
```

主要文件：

```text
aw-server\peewee-sqlite.v2.db
    原始活动数据和服务器设置。分类保存后，classes 设置也由服务器持久化。

aw-server\aw-server.toml
    服务器地址、端口和存储方式。分类不写在这里。

aw-watcher-window\aw-watcher-window.toml
    窗口采集频率、是否排除窗口标题。分类不写在这里。

aw-watcher-afk\aw-watcher-afk.toml
    AFK 超时和检测频率。当前默认超时约 180 秒。

aw-qt\aw-qt.toml
    ActivityWatch 启动哪些模块。分类不写在这里。
```

自己维护的分类源文件：

```text
D:\mathblog\quartz\content\非笔记内容\代码文件\ActivityWatch\categories-v4.json
```

==`categories-v1.json`、`categories-v2.json` 和 `categories-v3.json` 保留旧方案，`categories-v4.json` 是当前使用版本。== JSON 文件用于阅读、比较、Git 版本管理和恢复；ActivityWatch 实际运行时使用的是服务器中保存的 `classes` 设置。

## 4. 一条分类规则怎样工作

示例：

```json
{
  "name": ["家教"],
  "rule": {
    "type": "regex",
    "regex": "wemeetapp[.]exe|腾讯会议",
    "ignore_case": true
  }
}
```

- `name` 是分类名称。这里表示“家教”。
- `type: regex` 表示使用正则表达式匹配。
- `regex` 同时匹配事件中的应用名 `app` 和窗口标题 `title`。
- `|` 表示“或者”。
- `[.]` 表示普通的小数点，避免 `.` 被当成正则通配符。
- `ignore_case: true` 表示不区分英文大小写。

同一事件匹配多个规则时，ActivityWatch 采用层级最深的分类。因此：

```text
msedge.exe + “首页 - 知乎”
```

==浏览器进程先匹配“浏览器”。如果窗口标题同时匹配具体娱乐网站，则采用层级更深的“娱乐 > 直接娱乐”或“娱乐 > 可能娱乐”；网页版 ChatGPT 不再单独识别为工作。==

## 5. 怎样修改

少量临时修改：

1. 打开 `http://localhost:5600/#/settings`。
2. 找到 `Categorization`。
3. 点击分类右侧的编辑按钮。
4. 修改正则表达式并保存。
5. 回到 Activity 页面检查当天和过去记录。

需要保留修改时：

1. 在设置页点击 `Export`。
2. 将导出的 `aw-category-export.json` 与当前版本比较。
3. 确认有效后保存为下一个版本，例如 `categories-v5.json`，不要直接覆盖旧版本。

从源文件恢复：

1. 在设置页点击 `Import`。
2. 选择需要恢复的版本；当前版本是 `categories-v4.json`。
3. 检查分类树。
4. 点击 `Save`。

## 6. 已知限制

- ==当前没有浏览器 URL watcher，Edge 和 Chrome 默认计入“浏览器”；能从窗口标题识别的网站会被更具体的娱乐规则覆盖。==
- 知乎即使偶尔用于查资料，当前规则仍会直接计入娱乐。
- B 站和小红书保留为“可能娱乐”，以后再根据实际误判细分。
- `x.com` 很少直接出现在窗口标题中，不能用单独的字母 `X` 匹配，否则会产生大量误判。
- ==腾讯会议 `wemeetapp.exe` 归入“家教”。==
- ==Obsidian 既用于数学学习，也可能用于家教准备，因此应用级统计统一归入“工作”。==

后续修改应依据真实误判记录，每次只改一两条规则。
