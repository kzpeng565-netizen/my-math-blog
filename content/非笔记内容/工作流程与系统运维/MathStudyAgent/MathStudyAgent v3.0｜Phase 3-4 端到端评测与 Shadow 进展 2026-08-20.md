---
title: MathStudyAgent v3.0｜Phase 3-4 端到端评测与 Shadow 进展 2026-08-20
tags:
  - MathStudyAgent
  - 端到端评测
  - Shadow
  - 系统运维
date: 2026-08-20
status: in-progress-human-gates
---

# MathStudyAgent v3.0｜Phase 3-4 端到端评测与 Shadow 进展 2026-08-20

> 状态：可自动化基础设施已完成；人工金标、盲评与真实流量门禁仍在进行。
>
> 关联：[[MathStudyAgent v3.0｜智能检索重构与量化实验计划]]、[[MathStudyAgent v3.0｜检索冻结验收报告 2026-08-20]]

<!-- ai_provenance: source=codex; date=2026-08-20; verification=source-backed; retrieved_notes="MathStudyAgent v3.0｜智能检索重构与量化实验计划.md; MathStudyAgent v3.0｜检索冻结验收报告 2026-08-20.md" -->

## 已交付的基础设施

答案门禁从“长度/措辞初检”升级为五个相互独立的三态维度：数学正确性、证明实质性、核心目标、来源忠实度和教学策略。每一维只能返回 `passed / failed / unavailable`，证据不足不能猜测为通过。失败时只针对失败维度重写一次；独立复核仍不通过时，系统输出有限降级答案而不是继续给出未经验证的数学结论。

这一能力目前由 `TUTOR_QUALITY_GATE_ENABLED=false` 隔离。原因不是实现未完成，而是 40 条人工盲评尚未形成，不能先把额外模型调用和新降级策略放入默认用户链路。

Alembic `0016` 新增 MathTutorBench v1 的数据集、案例和运行快照表。质量检查页现在提供五步工作流：收集真实问题、审核人工金标、记录 v2.1/v3 重复运行、按 blind label 做五维裁决、查看严格发布门禁。冻结按钮只有在 sealed、至少 40 条 approved 金标、版本哈希和盲评协议完整，并关联未污染 sealed retrieval 通过时才启用。

## 当前案例与指标边界

系统从历史真实学习会话中去重收集了 7 条问题，数据集为 `mathtutorbench-v1-development-real-turns`。它们全部是 pending，approved=0、运行快照=0。自动收集只证明这些问题真实出现过；AI 没有补写或批准人工答案、教材对象、证明关键步和提示边界，因此当前不能报告端到端正确率。

正式门禁要求至少 40 条 approved case，v2.1 和 v3 每案各运行至少三次，并满足 Source Fidelity ≥95%、数学硬错误率 ≤5% 且不劣于 v2.1、端到端提升 ≥8 个百分点、Context Utilization ≥0.70、人工维度无 unavailable。

## Shadow 状态

v3 retrieval shadow 已开启。每个未来真实学习 turn 会在不改变用户答案和 Working Set 的前提下，后台保存 baseline/v3 run ID、选择对象、resolution、选择差异和阶段延迟。调试台当前显示 0/100，`ready_for_canary=false`。达到 100 只是数量条件，仍需人工审计是否出现新增硬失败。

## 验证与部署

- Ruff：通过；
- Mypy：172 个源文件通过；
- Pytest：337 条通过；
- Alembic：`0016 (head)`；
- 标准部署：2026-08-20 03:32:06（Asia/Shanghai）；
- PID：42624；
- 健康检查：HTTP 200 / `ok`；
- 页面实测：MathTutorBench、冻结防护和 shadow 面板正常，控制台无 warning/error。

## 下一步人工队列

1. 在质量检查页补齐并复核现有 7 条真实问题的金标；
2. 继续收集到至少 40 条，并执行第二评审者或延迟复审；
3. 由未参与调参的人工建立未污染 sealed retrieval 和 20 条 hard-negative；
4. 完成 v2.1/v3 三重复盲评并运行严格机器报告；
5. 自然积累并审计 100 个真实 shadow turn；
6. 全部门禁通过后再进入 quality gate canary 与 production flag 决策。

## 03:32 续作：从金标到盲评的自动证据链

为避免 40 条案例各手工复制六次答案，调试台已经加入可恢复的 `v2.1 / v3 × 3` 自动采集。它只接受人工金标已通过的案例，每次使用全新模型 thread，固定 Prompt、非敏感配置和源代码 SHA-256 指纹，并保存答案、实际教材证据包、注入对象和端到端延迟。已有 case/profile/repeat/code revision 槽位不会被覆盖。

盲评页面同步展示题目、人工金标、关键结论、证明步骤、来源事实、提示边界和此次运行的实际证据包，但不显示系统 profile。Context Utilization 不再依赖模型自报：评审者只能从此次运行真实注入的对象 ID 中勾选答案确实使用的对象，结果写入严格门禁读取字段。

源码或配置变化会令旧运行退出本版统计，并使 `frozen_artifact_identity` 失败。评测数据集已采用最新指纹；数据库只找到 7 个去重真实学习提问，仍为 0 approved、0 runs，不能用开发集或生成题冒充 downstream real turn。

浏览器实测 `frozen_artifact_identity=true`，整体冻结仍为 false，冻结按钮保持禁用，控制台无错误。
