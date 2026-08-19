---
title: MathStudyAgent v3.0｜检索冻结验收报告 2026-08-20
tags:
  - MathStudyAgent
  - 智能检索
  - 评测
  - 系统运维
date: 2026-08-20
status: development-retrieval-accepted
---

# MathStudyAgent v3.0｜检索冻结验收报告 2026-08-20

> 结论：跨语言 GTM 对象精排与冻结评测的暖索引延迟门禁已经通过；本结论只覆盖 development 检索层，生产开关继续关闭。
>
> 关联：[[MathStudyAgent v3.0｜智能检索重构与量化实验计划]]、[[MathStudyAgent v3.0｜智能检索重构阶段报告 2026-08-20]]

<!-- ai_provenance: source=codex; date=2026-08-20; verification=source-backed; retrieved_notes="MathStudyAgent v3.0｜智能检索重构与量化实验计划.md; MathStudyAgent v3.0｜智能检索重构阶段报告 2026-08-20.md" -->

## 验收结果

严格机器报告覆盖 54 条已审核 development 金标：

| 指标 | 结果 | 冻结阈值 | 判定 |
| --- | ---: | ---: | --- |
| Candidate Recall | 1.000 | ≥ 0.96 | 通过 |
| Top-1 gold accuracy | 0.889 | ≥ 0.85 | 通过 |
| Top-2 gold accuracy | 0.944 | ≥ 0.93 | 通过 |
| NDCG@5 | 0.942 | ≥ 0.90 | 通过 |
| Context Precision | 0.880 | ≥ 0.80 | 通过 |
| Within budget | 1.000 | ≥ 0.90 | 通过 |
| Forbidden / duplicate-primary | 0 / 0 | 0 / ≤ 0.05 | 通过 |
| Semantic base p95 | 344.278 ms | ≤ 800 ms | 通过 |
| 歧义 final selector p95 | 2458.57 ms | ≤ 3000 ms | 通过 |
| Final selector 触发率 | 5.56% | ≤ 25% | 通过 |

GTM 259 的 17 条跨语言切片在 Recall、Top-1、Top-2、NDCG、Context Precision 和预算指标上全部达到 1.000。实分析 37 条的 Top-1 为 0.838、Top-2 为 0.919、NDCG@5 为 0.916、Context Precision 为 0.824。

机器凭证位于 `D:\MathStudyAgent\data\evaluations\v3-development-gates-2026-08-20-final.json`。

## 两个阻塞的解决方案

跨语言精排不再依赖旧的通用 LLM listwise。系统先把 chunk 映射成稳定数学对象，再执行对象族约束和多语言 Query–Object 特征；只有跨语言、Top2 分差小于 0.50 的歧义案例，才调用 `Qwen/Qwen3-Reranker-8B` final selector。失败或 3 秒超时会回退确定性排序。显式单对象问法也会限制 Primary 数，避免把相邻定理、证明或定义一起装入上下文。

延迟侧把多个 semantic query 合并为一次远程 embedding 批调用，增加跨进程 query vector cache 与教材矩阵 LRU，并把“批量预热已审核问题”正式纳入计时流程。冻结报告要求正式回放时 query cache miss 必须为 0，因此 344.278 ms 的 base p95 是可审计的暖索引口径。

需要保留边界：54 条首次远程 embedding 的观测 p95 约 24.39 秒，额外五次远程烟测 p50 约 2.18 秒。公网陌生问题的冷延迟仍受供应商影响，不能用暖缓存结果冒充已经消失；后续需做供应商或本地兼容 embedding bake-off。

## 当前调试与记录工作流

“检索测试台”现在按以下顺序使用：

1. 即时运行真实检索链路，观察 Planner、候选生成、rerank/selection、hydration 与各阶段耗时；
2. 把当前问题和人工确认的教材对象收集到 draft/pending 评测集；
3. 在同一页审核问题、Primary/Acceptable/Forbidden、对象预算、教材证据 Block 与出题说明；
4. 先批量预热已审核问题，再运行 v3、Semantic、AI+FTS 或 default Profile；
5. 逐候选查看 gold 角色、对象类型、reranker 分数、特征、约束冲突、入选/淘汰原因；
6. 查看冻结门禁和自动失败阶段，填写审核/失败归因记录，再决定通过、退回或保持 pending。

页面已在部署后实际核验，所有上述区域均正常渲染，浏览器控制台没有 warning/error。

## 验证与部署

- Alembic：`0015_query_embedding_cache (head)`；
- Ruff：通过；
- Mypy：166 个源文件通过；
- Pytest：326 条通过；
- 标准部署：2026-08-20 02:36:47（Asia/Shanghai）；
- 监听 PID：14568；
- 健康检查：`http://127.0.0.1:8501/_stcore/health` 返回 HTTP 200；
- 部署凭证：`D:\MathStudyAgent\data\streamlit-deployment.json`。

## 尚未关闭的 v3 发布门禁

本次通过的是 development 检索冻结门禁，不是整个 v3 发布验收。仍需完成新的未污染 sealed retrieval 集、20 条独立 hard-negative、40 条 downstream Tutor 盲评、Source Fidelity 与数学硬错误率、100 个真实 shadow turn、canary 和 feature flag 发布。完成这些工作前，不应把检索 development 指标称为端到端系统正确率，也不应开启生产检索开关。
