# Obsidian Copilot GPT-5.6 Sol 中转站测试失败与修复经验

更新时间：2026-09-01

<!-- ai_provenance: source=codex; date=2026-09-01; verification=desktop-chat-real-request; secrets=excluded -->

## 1. 结论先行

本次电脑端 Obsidian Copilot 已完成实际聊天验证，gpt-5.6-sol 能够正常返回结果。

实际测试内容：

~~~text
请只回复：COPILOT_OK
~~~

实际返回：

~~~text
COPILOT_OK
~~~

当前只完成电脑端，**没有部署到平板**。

## 2. 环境与目标配置

- Obsidian：1.13.7
- Copilot：3.3.3
- 模型：gpt-5.6-sol
- Copilot 内部 provider：3rd party (openai-format)
- 设置界面显示：OpenAI Format
- Base URL：https://sub2api.52ai.pro/v1
- 请求协议：OpenAI Responses API
- 流式输出：开启
- 推理深度：medium
- 当前能力勾选：Reasoning
- Vision、Websearch：本次未启用
- 中转站：与树莓派目标模式使用同一个中转站

注意：Base URL 应填写到 /v1，**不要**填写成：

~~~text
https://sub2api.52ai.pro/v1/responses
~~~

Copilot 会自行调用：

~~~text
/v1/responses
~~~

API key 不记录在本文件中。

## 3. 故障表现与时间线

### 3.1 第一次表现：Failed to fetch

Copilot Chat 显示：

~~~text
Error occurred
Connection error.
more message: Failed to fetch
~~~

同一时间 Copilot 日志记录了连接测试的两次请求：

~~~text
First ping attempt failed, retrying with CORS enabled.
without CORS Error: Request was aborted.
with CORS Error: Request was aborted.
~~~

### 3.2 第二次表现：明确的 HTTP 400

开启 Copilot 的 CORS 原生请求通道并完整重启 Obsidian 后，错误从浏览器层的：

~~~text
Failed to fetch
~~~

变成了中转站返回的：

~~~text
Request failed, status 400.
{"error":{"message":"Upstream request failed","type":"upstream_error"}}
~~~

这证明请求已经到达中转站，问题不再是 API key、域名解析或浏览器 CORS。

### 3.3 最终表现：测试成功

对 Copilot 3.3.3 做 GPT-5 temperature 兼容性补丁，完全退出并重新打开 Obsidian 后，真实聊天返回：

~~~text
COPILOT_OK
~~~

## 4. 根因分析

### 4.1 根因一：中转站没有返回浏览器 CORS 头

对以下地址做预检：

~~~text
https://sub2api.52ai.pro/v1/responses
~~~

预检返回 HTTP 204，但没有提供可供普通浏览器 fetch 使用的：

- Access-Control-Allow-Origin
- Access-Control-Allow-Methods
- Access-Control-Allow-Headers

因此 Copilot 使用普通浏览器 Fetch 时，最终只显示笼统的 Failed to fetch。

Copilot 的 CORS 复选框含义容易误解：它不是要求中转站增加 CORS，而是让 Copilot 改用 Obsidian 原生的 requestUrl 请求通道，从而绕过浏览器 CORS 限制。

因此这个模型条目需要：

~~~json
"enableCors": true
~~~

### 4.2 根因二：只修改 data.json 时，运行中的 Copilot 不会立即采用新设置

曾经直接修改：

~~~text
.obsidian/plugins/copilot/data.json
~~~

但 Obsidian 进程仍在运行。之后按 Ctrl+R 并没有产生新的 Copilot 初始化日志，旧的内存配置仍在使用。

可靠做法是：

1. 保存配置文件；
2. 完全退出 Obsidian；
3. 确认 Obsidian 窗口已经消失；
4. 重新启动 Obsidian；
5. 再检查 Copilot 日志中的模型初始化记录；
6. 最后再发送测试消息。

仅刷新界面或重新打开设置页不应被视为插件已经重新加载。

### 4.3 根因三：Copilot 3.3.3 对 GPT-5 自动发送 temperature

Copilot 3.3.3 对 GPT-5/Responses API 自动生成的请求中包含类似字段：

~~~json
{
  "model": "gpt-5.6-sol",
  "temperature": 1,
  "reasoning": {
    "effort": "medium"
  },
  "text": {
    "verbosity": "medium"
  },
  "max_output_tokens": 6000,
  "stream": true
}
~~~

同一个中转站的参数隔离结果：

| 请求变体 | 结果 |
| --- | --- |
| reasoning.effort=medium、max_output_tokens=4096，不带 temperature | 成功，返回完整 SSE |
| 带 temperature=1 | HTTP 400，上游请求失败 |
| 带 temperature=0.1 | HTTP 400，上游请求失败 |
| reasoning.effort=medium、text.verbosity=medium、max_output_tokens=4096，不带 temperature | 成功 |

所以本次可确认的兼容性问题是：**该中转站的 GPT-5 Responses 上游不接受 Copilot 3.3.3 附带的 temperature 字段。**

### 4.4 连接测试还有一个独立的 8 秒超时边界

Copilot 3.3.3 的模型 ping 使用：

~~~text
invoke([{role: "user", content: "hello"}], {timeout: 8e3})
~~~

GPT-5.6 Sol 经由中转站返回可能超过 8 秒，因此模型设置页的连接测试可能出现：

~~~text
Request was aborted
~~~

这与后来出现的 HTTP 400 是两个不同层次的问题：

- Request was aborted：连接测试的 8 秒超时边界；
- HTTP 400：请求已经到达上游，但字段不兼容。

实际聊天测试比单纯 ping 更有代表性，但也应允许中转站有足够响应时间。

## 5. 本次实际修复

### 5.1 Copilot 模型配置

gpt-5.6-sol 条目最终需要包含以下非敏感配置：

~~~json
{
  "name": "gpt-5.6-sol",
  "provider": "3rd party (openai-format)",
  "enabled": true,
  "baseUrl": "https://sub2api.52ai.pro/v1",
  "capabilities": ["reasoning"],
  "enableCors": true,
  "reasoningEffort": "medium",
  "stream": true
}
~~~

API key 仍然保存在 Copilot 的本地配置中，但不写入经验文档。

全局配置同时设为：

~~~json
"reasoningEffort": "medium"
~~~

### 5.2 Copilot 3.3.3 兼容性补丁

补丁位置：

~~~text
.obsidian/plugins/copilot/main.js
~~~

原始逻辑会让 GPT-5 使用固定的 reasoning-model temperature：

~~~text
getTemperatureForModel(...){
  ...
  return e.isOSeries || e.isGPT5 ? cs.REASONING_MODEL_TEMPERATURE : ...
}
~~~

本次补丁改为：

~~~text
getTemperatureForModel(e,n,r){
  if(!e.isThinkingEnabled)
    return e.isGPT5
      ? void 0
      : e.isOSeries
        ? cs.REASONING_MODEL_TEMPERATURE
        : n.temperature ?? r.temperature
}
~~~

含义是：

- GPT-5：不发送 temperature；
- O 系列模型：保留原来的 reasoning temperature 行为；
- 普通非 reasoning 模型：保留原来的 temperature 行为。

这是针对当前兼容性问题的最小修改，不改变 Responses API、推理深度或流式输出。

### 5.3 回滚备份

当前 main.js 原文件备份位于：

~~~text
C:\Users\15345\AppData\Local\Temp\copilot-main-3.3.3-before-gpt5-temperature-fix.js
~~~

如需回滚：

1. 退出 Obsidian；
2. 将上面的备份复制回：

~~~text
D:\mathblog\quartz\content\.obsidian\plugins\copilot\main.js
~~~

3. 重新启动 Obsidian；
4. 再恢复或禁用 gpt-5.6-sol 模型条目。

不要在 Obsidian 正在运行时覆盖 main.js，否则运行中的插件实例仍可能使用旧代码。

## 6. 验收结果

| 验收项 | 结果 |
| --- | --- |
| 模型名称为 gpt-5.6-sol | 通过 |
| Provider 为 OpenAI Format | 通过 |
| Base URL 为 /v1 根地址 | 通过 |
| 模型启用 | 通过 |
| CORS 原生请求通道启用 | 通过 |
| 推理深度为 medium | 通过 |
| Responses SSE 直连结构验证 | 通过 |
| Copilot 真实 Chat 请求 | 通过 |
| 实际返回 COPILOT_OK | 通过 |
| 测试聊天临时笔记已清理 | 通过 |
| API key 临时文件已清理 | 通过 |
| Vault 内 API.md 已删除 | 通过 |
| 平板部署 | 尚未执行 |

## 7. 安全与 Git 注意事项

### 7.1 不要再次把 API key 放入普通 Markdown

本次曾将 API key 临时放在：

~~~text
非笔记内容/代码文件/API.md
~~~

该文件曾经是 Git 跟踪文件。它后来已从工作区删除，并增加了针对该路径的忽略规则，但删除工作区文件不能清除 Git 历史中的旧内容。

因此应按以下原则处理：

- 不要恢复 API.md；
- 不要把 key 写进经验文档；
- 不要把 key 发到聊天中；
- 平板部署前先轮换中转站 API key；
- 轮换后同步更新树莓派目标模式的私有环境变量；
- 轮换后再重新完成电脑端和树莓派端验证。

### 7.2 Copilot 日志可能包含笔记上下文

调试期间生成了：

~~~text
copilot/copilot-log.md
~~~

Copilot 日志本身会脱敏 API key，但可能包含完整的当前笔记上下文和请求内容。排障结束后，如果不再需要，应在确认没有审计需求后清理或限制其同步范围。

### 7.3 data.json 不应上传

当前：

~~~text
.obsidian/plugins/copilot/data.json
~~~

由 .gitignore 中的 .obsidian 规则忽略。不要取消该忽略规则，也不要把其中的 API key 复制到 Vault Markdown、脚本、Git 或同步目录。

## 8. 下次排障顺序

遇到同类问题时，按以下顺序执行：

1. 检查模型名是否精确为 gpt-5.6-sol；
2. 检查 Provider 是否为 OpenAI Format，不要选普通 OpenAI；
3. 检查 Base URL 是否为 https://sub2api.52ai.pro/v1；
4. 检查 API key 是否存在，但只检查存在性，不输出明文；
5. 勾选模型级 CORS；
6. 勾选 Reasoning，并确认 reasoningEffort=medium；
7. 不先启用 Vision/Websearch；
8. 完全退出并重新启动 Obsidian；
9. 先发送最小文本测试，不要先附加整篇笔记；
10. 若是 Failed to fetch，查 CORS/原生请求通道；
11. 若是 HTTP 400，查请求字段，优先移除 temperature；
12. 若是 Request was aborted，考虑中转站响应时间超过连接测试的 8 秒；
13. 电脑端真实 Chat 通过后，才考虑平板部署。

## 9. 平板部署前置条件

平板部署尚未开始。开始前必须满足：

- 电脑端真实 Chat 连续测试通过；
- 使用轮换后的新 API key；
- 树莓派目标模式已同步使用新 key；
- 确认 vivo Pad5e 为当前活动平板；
- 选择明确的 ADB serial；
- 先做平板端配置备份；
- 平板端使用与电脑端相同的 /v1 Base URL；
- 平板端同样验证 CORS/native request path；
- 平板端单独做最小文本测试；
- 未通过前不声明部署完成。

## 10. 相关本地证据

- Copilot 配置：.obsidian/plugins/copilot/data.json
- Copilot 运行代码：.obsidian/plugins/copilot/main.js
- Copilot 版本：.obsidian/plugins/copilot/manifest.json
- 排障日志：copilot/copilot-log.md
- 树莓派目标模式验收文档：非笔记内容/工作流程与系统运维/计划模式/05-v2课程进度与GPT-5.6迁移验收.md

本文件不保存 API key、完整请求头、完整响应体或任何可恢复凭据。
