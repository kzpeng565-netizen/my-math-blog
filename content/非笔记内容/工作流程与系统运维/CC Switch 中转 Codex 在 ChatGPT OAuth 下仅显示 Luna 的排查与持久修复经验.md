# CC Switch 中转 Codex 在 ChatGPT OAuth 下仅显示 Luna 的排查与持久修复经验

<!-- ai_provenance: source=codex; date=2026-08-31; verification=checked; retrieved_notes="" -->

## 1. 问题结论

本次故障不是“CC Switch 没有接管请求”，而是**路由、模型目录、OAuth 凭据和正在运行的桌面进程处在不同状态**：

- 请求确实到达了 `https://sub2api.52ai.pro/`，所以中转本身已生效。
- 旧任务仍发送 `gpt-reserve`，中转侧最终落到 `gpt-5.6-luna`。
- ChatGPT OAuth 登录下，模型选择页只显示 Luna；API Key 登录下则可以正常使用 Sol。
- 只修改 `C:\Users\15345\.codex\config.toml` 不能持久生效，因为 CC Switch 会根据数据库中的 provider 模板重新生成该文件。
- Windows 上 OAuth 凭据可能分散在系统凭据库、`auth.json` 和 CC Switch 数据库中。旧 OAuth 副本虽然能让部分本地检查显示“已登录”，但 ChatGPT 插件、额度等接口会返回 `401 Unauthorized`。

最终修复由四部分组成：

1. 把 `gpt-5.6-sol` 和绝对模型目录路径写入 CC Switch provider 的持久化模板。
2. 固定 `cli_auth_credentials_store = "file"`，让 Codex 与 CC Switch 共同使用 `auth.json`。
3. 重新完成一次真实的 ChatGPT OAuth 登录，并把新凭据同步回 CC Switch 的官方认证副本。
4. 完全退出并重开 Codex，使用新任务验证，不继续沿用绑定旧模型的任务。

## 2. 三条容易混淆的数据流

### 2.1 推理请求

当前采用的是 CC Switch 改写配置后直连中转站，而不是本地代理转发：

```text
Codex 桌面端
  -> C:\Users\15345\.codex\config.toml
  -> model_provider = "custom"
  -> https://sub2api.52ai.pro
  -> 中转站上游模型
```

CC Switch 数据库中的 Codex 本地代理状态为关闭，因此 `http://127.0.0.1:15721/health` 不可用并不代表本方案失效。此模式应检查 `base_url`、真实请求返回和中转站日志。

### 2.2 模型选择页

模型选择页不是简单读取 `model = "..."`。桌面端通过 Codex app-server 的 `model/list` 获取可显示模型：

```text
模型目录
  -> Codex app-server
  -> model/list
  -> 桌面端模型选择器
```

因此：

- `model = "gpt-5.6-sol"` 只设置默认请求模型，不保证模型选择页一定出现 Sol。
- `codex debug models` 查看的是原始模型目录；它包含 Sol，也不等于当前桌面进程的选择页已经刷新。
- `model_catalog_json` 在 Codex 启动时加载，修改后必须彻底重启桌面端。

### 2.3 OAuth 凭据

修复后的凭据流为：

```text
ChatGPT 浏览器 OAuth
  -> C:\Users\15345\.codex\auth.json
  -> Codex 登录状态
  -> CC Switch 的 OpenAI Official 认证副本
```

不要把 OAuth token、API Key 或 `experimental_bearer_token` 的值写入笔记、工单、聊天记录或 Git。

## 3. 根因

### 3.1 只改活动配置，未改 provider 模板

CC Switch 当前中转 provider：

- 名称：`中转站`
- ID：`efe2219b-60c4-4104-91fa-9c7e6a9bb575`
- 上游：`https://sub2api.52ai.pro`

CC Switch 使用数据库 `C:\Users\15345\.cc-switch\cc-switch.db` 中的：

```text
providers.settings_config.config
```

重新生成 `C:\Users\15345\.codex\config.toml`。原模板只有 `model = "gpt-5.6-sol"`，没有 `model_catalog_json`，所以手动加入的目录路径会在切换 provider、切换登录方式或重启 CC Switch 后消失。

### 3.2 OAuth 存储层分裂

未显式设置 `cli_auth_credentials_store` 时，Codex 可使用 Windows 凭据库。CC Switch 主要操作 `auth.json`，两者可能出现状态分裂：

- 本地文件是旧 OAuth；
- 系统凭据库是另一种登录；
- CC Switch 数据库又保存一份官方 OAuth 副本。

旧副本一度能让中转请求成功，但 ChatGPT 的插件、额度和遥测接口连续返回 `401`。这说明“能发模型请求”不能代替“OAuth 有效”的验收。

### 3.3 旧进程和旧任务缓存

模型目录在进程启动时加载，旧任务还可能保留创建时的模型绑定。修复配置后继续在旧任务里测试，会看到 `gpt-reserve` 或只显示 Luna，从而误判修复无效。

### 3.4 两套 Codex CLI 造成误判

本机同时出现过：

- PATH 中的 `codex`；
- ChatGPT/Codex 桌面端自带的 `codex.exe`。

两者版本、`CODEX_HOME` 和加载到的配置可能不同。若测试输出显示 `provider: openai`，而预期是 `provider: custom`，应先检查执行文件和 `CODEX_HOME`，不要立刻判断中转失效。

## 4. 修复后的关键配置

活动配置文件：

```text
C:\Users\15345\.codex\config.toml
```

关键内容：

```toml
model_provider = "custom"
model = "gpt-5.6-sol"
model_catalog_json = "cc-switch-model-catalog-persistent.json"
cli_auth_credentials_store = "file"

[model_providers.custom]
name = "custom"
wire_api = "responses"
requires_openai_auth = true
base_url = "https://sub2api.52ai.pro"
```

活动配置中还会有 CC Switch 管理的 `experimental_bearer_token`。只检查该字段是否存在，不要读取、复制或记录其值。

模型目录文件：

```text
C:\Users\15345\.codex\cc-switch-model-catalog-persistent.json
```

当前选择页目录包含：

- `deepseek-v4-flash`
- `gpt-5.6-sol`
- `deepseek-v4-pro`

以上两个新增顶层配置也已写入 provider 的 `settings_config.config`，避免 CC Switch 再次覆盖。

### 4.1 图片输入能力声明

模型目录不仅决定模型是否显示，还会决定输入框是否允许附加图片。Sol 条目必须保持：

```json
"slug": "gpt-5.6-sol",
"input_modalities": [
  "text",
  "image"
],
"supports_image_detail_original": true
```

本次后续故障的直接原因是补丁匹配了目录中的第一个模型块，把 `deepseek-v4-flash` 改成了图片模型，而 Sol 仍保留为：

```json
"input_modalities": [
  "text"
],
"supports_image_detail_original": false
```

修复时必须按 `"slug": "gpt-5.6-sol"` 定位完整对象，不能只按 `input_modalities` 或 `supports_image_detail_original` 的第一次出现位置替换。修复后 app-server 的 `model/list` 应返回：

```text
gpt-5.6-sol
inputModalities = ["text", "image"]
hidden = false
```

这次只验证了模型能力目录和选择器判定，没有上传真实图片到中转站；真实图片请求仍需由用户在重启后的新任务中自行确认。

### 4.2 思考强度被缩减为少数档位

==CC Switch 3.18.0 的 provider 编辑器会把 `settings_config.modelCatalog` 转换为 `cc-switch-model-catalog.json`。该数据结构只能表达粗粒度的“是否支持推理”，不能完整保存 Sol 的具体档位。==

本次活动目录被重新生成后，Sol 一度只剩：

```text
default_reasoning_level = high
supported_reasoning_levels = [none, high]
```

`models.json` 中则仍是旧的 `low, high, max`，两份目录互相不一致。桌面端实际读取 `config.toml` 中 `model_catalog_json` 指向的文件，因此修改未被引用的 `models.json` 不足以修复模型选择器。

官方内置 Sol 目录包含六档：

```text
low, medium, high, xhigh, max, ultra
```

持久化修复采用以下结构：

1. 从 Codex 内置目录复制 Sol 的 `default_reasoning_level` 和完整 `supported_reasoning_levels`。
2. 写入独立文件 `cc-switch-model-catalog-persistent.json`。
3. 将活动配置和中转 provider 模板的 `model_catalog_json` 都指向该文件。
4. 从中转 provider 的 `settings_config` 中移除 `modelCatalog`，阻止 CC Switch 再生成并覆盖目录。
5. 保留 provider 的 `auth`、中转地址、代理管理令牌和其他配置，不做整行重建。

Sol 的关键字段应为：

```json
"default_reasoning_level": "low",
"supported_reasoning_levels": [
  { "effort": "low" },
  { "effort": "medium" },
  { "effort": "high" },
  { "effort": "xhigh" },
  { "effort": "max" },
  { "effort": "ultra" }
]
```

`config.toml` 中的 `model_reasoning_effort = "high"` 只表示当前默认选择，不应被误认为模型只支持 High。真正决定下拉列表的是 `supported_reasoning_levels`。

## 5. 正确修复流程

### 5.1 先备份

至少备份：

```text
C:\Users\15345\.cc-switch\cc-switch.db
C:\Users\15345\.codex\config.toml
C:\Users\15345\.codex\auth.json
C:\Users\15345\.codex\cc-switch-model-catalog-persistent.json
```

`auth.json` 和数据库都可能含凭据，备份不得上传或提交 Git。

### 5.2 修改持久化模板

不要只改活动 `config.toml`。应同时保证“中转站”provider 的模板包含：

```toml
model = "gpt-5.6-sol"
model_catalog_json = "cc-switch-model-catalog-persistent.json"
cli_auth_credentials_store = "file"
```

数据库只读检查命令：

```powershell
$db = 'C:\Users\15345\.cc-switch\cc-switch.db'
$sqlite = 'D:\anaconda\Library\bin\sqlite3.exe'
& $sqlite -header -column $db @"
SELECT id, name, is_current,
       json_extract(settings_config, '$.config') AS config
FROM providers
WHERE app_type = 'codex'
  AND id = 'efe2219b-60c4-4104-91fa-9c7e6a9bb575';
"@
```

手工更新数据库前必须退出 CC Switch 并备份数据库。不要用会把 `settings_config.auth` 覆盖为空的整行替换。若要保留完整六档，应确认 `settings_config` 中不再存在会触发目录再生成的 `modelCatalog`。

### 5.3 刷新 OAuth

在最终配置已经写好后，使用桌面端同一个 `CODEX_HOME`：

```powershell
$env:CODEX_HOME = 'C:\Users\15345\.codex'
codex.exe logout
codex.exe login
codex.exe login status
```

浏览器完成 ChatGPT 登录和工作空间确认后，预期输出：

```text
Logged in using ChatGPT
```

随后把新 `auth.json` 同步到 CC Switch 的 `OpenAI Official` provider 认证副本。同步时只替换该 provider 的 `settings_config.auth`，不要改中转 provider 中保存的上游凭据。

### 5.4 重启和新建任务

1. 退出所有 Codex/ChatGPT 桌面窗口。
2. 确认托盘或任务管理器中旧 Codex 进程已退出。
3. 重新启动 Codex。
4. 新建一个任务，不要继续使用原来绑定 `gpt-reserve` 的任务。
5. 打开模型选择器检查 Sol。

## 6. 可观察验收

### 6.1 配置层

确认以下项目同时成立：

- `model_provider = "custom"`
- `model = "gpt-5.6-sol"`
- `model_catalog_json` 指向不受 CC Switch 生成器管理的 `cc-switch-model-catalog-persistent.json`
- `cli_auth_credentials_store = "file"`
- `requires_openai_auth = true`
- `base_url = "https://sub2api.52ai.pro"`
- provider 模板中也有相同的目录和凭据存储配置

### 6.2 认证层

```powershell
$env:CODEX_HOME = 'C:\Users\15345\.codex'
codex.exe login status
```

验收标准：

- 显示 `Logged in using ChatGPT`；
- 新请求期间不再出现 `401 Unauthorized`；
- 不以“本地文件里存在 token”作为有效登录证据。

### 6.3 模型目录层

官方原始目录诊断：

```powershell
codex debug models
codex debug models --bundled
```

桌面模型选择器的权威接口是 app-server：

```json
{"method":"initialize","id":0,"params":{"clientInfo":{"name":"model_check","title":"Model Check","version":"1.0"}}}
{"method":"initialized","params":{}}
{"method":"model/list","id":6,"params":{"limit":50,"includeHidden":false}}
```

本次最终结果：

```text
SolVisible=True
gpt-5.6-sol -> hidden=false
```

### 6.4 真实请求层

```powershell
$env:CODEX_HOME = 'C:\Users\15345\.codex'
codex.exe exec --skip-git-repo-check `
  --model gpt-5.6-sol `
  --config 'model_reasoning_effort="low"' `
  '只回复 OK'
```

本次最终验收：

```text
ExitCode=0
provider=custom
model=gpt-5.6-sol
OK
401 Unauthorized 数量=0
```

最后在中转站日志确认请求模型是 `gpt-5.6-sol`。若仍显示 `GPT-reserve XHigh`，优先检查是否还在旧任务或旧桌面进程中。

## 7. 故障定位表

| 现象 | 优先检查 | 常见原因 |
| --- | --- | --- |
| OAuth 下只显示 Luna | 完全退出并重开 Codex，再查 `model/list` | 旧进程仍使用启动时目录 |
| `config.toml` 修好后又恢复 | provider 的 `settings_config.config` | 只改了活动文件，未改 CC Switch 模板 |
| `debug models` 有 Sol，但界面没有 | app-server `model/list` | 原始目录与选择页不是同一层 |
| `login status` 看似正常，但插件/额度 401 | 重新 OAuth，检查 `cli_auth_credentials_store` | 旧凭据或 Windows 凭据库与文件分裂 |
| 请求头显示 `provider: openai` | `CODEX_HOME` 和所用可执行文件 | 跑到了另一套 Codex CLI |
| 中转日志显示 `gpt-reserve` | 新建任务并确认 `model` | 旧任务保存了旧模型绑定 |
| `127.0.0.1:15721/health` 不通 | 查看 CC Switch `proxy_config` | 当前是直连中转站模式，本地代理未启用 |
| Sol 请求成功但界面仍显示官方额度 | 区分额度面板与实际路由日志 | ChatGPT 账户额度 UI 不等于中转站计费与路由 |
| Sol 只剩 None/High 或少数思考档位 | 检查活动目录和 provider 的 `settings_config.modelCatalog` | CC Switch 3.18.0 用粗粒度模型配置重生成目录 |
| `models.json` 已有完整档位但界面没有 | 检查 `config.toml` 的 `model_catalog_json` | 桌面端读取的是另一份活动目录 |
| 重启或切换 provider 后档位再次消失 | 检查 provider 是否重新出现 `modelCatalog` | CC Switch 再次接管并覆盖持久目录 |

## 8. 本次备份与回滚

本次新增备份位于：

```text
C:\Users\15345\.cc-switch\backups\codex_auth_20260831_004447_before_oauth_catalog_fix.json
C:\Users\15345\.cc-switch\backups\codex_config_20260831_004447_before_oauth_catalog_fix.toml
C:\Users\15345\.cc-switch\backups\db_backup_20260831_004447_before_oauth_catalog_fix.db
C:\Users\15345\.cc-switch\backups\codex_config_20260831_005306_before_file_auth_store.toml
C:\Users\15345\.cc-switch\backups\db_backup_20260831_005306_before_file_auth_store.db
C:\Users\15345\.cc-switch\backups\db_backup_20260831_005837_before_fresh_oauth_sync.db
C:\Users\15345\.cc-switch\backups\db_backup_*_before_reasoning_levels_fix.db
C:\Users\15345\.cc-switch\backups\codex_config_*_before_reasoning_levels_fix.toml
C:\Users\15345\.cc-switch\backups\codex_generated_catalog_*_before_reasoning_levels_fix.json
C:\Users\15345\.cc-switch\backups\codex_models_*_before_reasoning_levels_fix.json
```

完全回滚到本轮修复前：

1. 退出 Codex 和 CC Switch。
2. 先再次备份当前数据库、配置和认证文件。
3. 用 `db_backup_20260831_004447_before_oauth_catalog_fix.db` 恢复 `cc-switch.db`。
4. 用同时间戳的 `codex_config` 和 `codex_auth` 恢复 Codex 配置与认证。
5. 重启 CC Switch 和 Codex。

该回滚会恢复到当时的 API Key 登录状态，并撤销本轮 OAuth 目录持久化修复。

若只回滚思考强度修复，应恢复同一时间戳的 `before_reasoning_levels_fix` 数据库、配置和两份目录备份。恢复数据库会重新启用原来的 `settings_config.modelCatalog`，Sol 的档位也会再次缩减。

## 9. 官方文档依据

- [Authentication：Alternative model providers](https://learn.chatgpt.com/docs/auth#alternative-model-providers)：`requires_openai_auth = true` 可使用 ChatGPT 或 API Key 登录自定义 provider。
- [Authentication：Credential storage](https://learn.chatgpt.com/docs/auth#credential-storage)：`cli_auth_credentials_store` 可固定使用文件、系统凭据库或自动选择。
- [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)：`model_catalog_json` 是启动时加载的 JSON 模型目录路径。
- [Codex App Server：model/list](https://learn.chatgpt.com/docs/app-server#list-models-model-list)：桌面客户端应根据 `model/list` 渲染模型选择器。
- [Developer commands：codex debug models](https://learn.chatgpt.com/docs/developer-commands#codex-debug-models)：检查 Codex 看到的原始模型目录。
- [Models：Reasoning levels](https://learn.chatgpt.com/docs/models#reasoning-levels)：Sol 支持 Low、Medium、High、XHigh 和 Max；本机内置目录还提供 Ultra。
