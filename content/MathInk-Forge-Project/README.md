# MathInk Forge 项目包

<!-- ai_provenance: source=codex; date=2026-08-23; verification=checked -->

这是 MathInk Forge 的独立交接目录。它同时保存当前调查源码、平板实际运行的回退版制品、v1.0 计划和下一轮实施顺序。

> [!warning] 两套版本不要混用
> - `artifacts/deployed-rollback/`：平板当前实际运行的旧版，作为性能基线。
> - `code-source/` 与 `artifacts/unconfirmed-current/`：包含尚未通过平板性能验证的改动，不得直接当作已验收版本发布。

## 建议阅读顺序

1. `HANDOFF.md`：接手入口和关键约束。
2. `PROJECT_STATE.md`：设备、版本、证据和已知问题。
3. `DECISIONS.md`：已经确定、不应反复推翻的决定。
4. `NEXT_STEPS.md`：最近一次测试与分支判断。
5. `IMPLEMENTATION_NEXT.md`：定位后如何逐项实现。
6. `V1_PLAN.md`：完整 v1.0 目标与验收标准。

## 目录

- `code-source/`：源码、测试、fixture、构建配置和项目文档快照；未包含 `.git`、`node_modules`、`coverage`、`.deploy-target` 和生成的 `main.js`。
- `artifacts/deployed-rollback/`：当前平板部署的 `main.js`、`manifest.json`、`styles.css`。
- `artifacts/unconfirmed-current/`：当前调查源码对应的未确认构建产物。
- `evidence/`：只保存脱敏后的测试事实与哈希，不保存用户笔记正文。

## 当前最短路径

先在回退版、Input Lab 关闭的条件下快速画 30 个彼此分开的短竖线。现有测试笔记是 207 笔，保存后应精确变成 237 笔。完成这个基线前，不再改性能相关代码。

## 恢复开发环境

在项目目录外安装依赖，避免把 `node_modules` 放进 Obsidian Vault：

```powershell
Copy-Item -Recurse -LiteralPath '.\code-source' -Destination 'D:\MathInk-Forge-Work'
Set-Location 'D:\MathInk-Forge-Work'
npm ci
npm test
npm run build
```

当前环境无法直接写入 `D:\` 根目录，所以本交接目录建立在 `D:\mathblog\quartz\content\MathInk-Forge-Project`。如需根目录项目，可在普通 PowerShell 中将整个目录复制出去。
