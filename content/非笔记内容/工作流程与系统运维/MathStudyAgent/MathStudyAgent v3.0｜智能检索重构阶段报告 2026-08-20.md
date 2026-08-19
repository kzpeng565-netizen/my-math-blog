# MathStudyAgent v3.0｜智能检索重构阶段报告 2026-08-20

> 状态：development 实现完成；发布门禁未全部通过，生产开关保持关闭
>
> 关联：[[MathStudyAgent v3.0｜智能检索重构与量化实验计划]]

<!-- ai_provenance: source=codex; date=2026-08-20; verification=checked; retrieved_notes="MathStudyAgent v3.0｜智能检索重构与量化实验计划.md" -->

## 执行结论

智能检索重构目前具备可运行、可回放的 development 实现：Planner v3、对象级候选聚合、Query–Object 重排、动态 Primary Selector、类型化 compact hydration、独立 v3 评测 profile、统计方法和严格门禁报告均已落地。

但计划尚不能宣称全部完成。54 条 development 的 Candidate Recall 已达到 100%，安全约束也保持 forbidden-object rate 与 duplicate-primary rate 为 0；跨语言教材的对象精排、上下文精度和远程延迟仍未达到冻结门禁。新的 sealed 集、下游 Tutor 盲评和 100 个真实 shadow turn 也需要人工金标或真实流量，当前没有条件用自动化结果替代。

## 已完成的工程交付

### Planner 与检索合同

- `RetrievalPlanV3` 明确记录检索模式、锚点、目标对象类型、数学概念、关系意图、1–3 个语义查询、词法补召回、正负约束、检索范围、Primary/Support 数量范围、置信度、歧义原因和停止条件。
- 在线 v3 Planner 使用确定性规则、已验证术语和教材结构生成合同；逐题 LLM Planner 因单题耗时接近数分钟被移出在线主链。
- 历史 `ai_fts` 与 `semantic_only` 快照不改写；新实验使用独立 `v3` profile 追加记录。

### 对象召回、重排和选择

- 多 query、多 chunk、多通道命中先聚合到稳定数学对象；没有 object ID 的块级候选在 v3 预筛中删除。
- Semantic 是主召回，FTS、术语和结构只提供辅助信号；只有唯一 exact label 可以被保护，术语字典不再以固定高分压过 Semantic。
- Query–Object 重排记录 embedding 相似度、对象类型、约束覆盖、query-role coverage、通道支持、边界置信度和冲突风险。
- 最终选择不再填满 Top‑K，而是计算新增对象的相关性、角色覆盖、冗余、冲突和上下文成本；低置信候选不注入。
- LLM listwise 只允许对白名单 object ID 评分，并使用对象 statement/compact view；schema 失败时回退确定性排序。

### Selective Hydration 与评测

- 证明 compact view 改为“目标—关键步骤—结论”骨架，不再只做首尾截断。
- 例题/习题使用“条件—核心构造—结论”，定理和定义支持 statement-only compact view，并保留原始 block 映射。
- 新增 Candidate Recall、Top‑1、Top‑2、NDCG@5、Context Precision、预算、forbidden 和 duplicate-primary 指标。
- paired bootstrap 使用 10,000 次抽样；新增 exact McNemar 检验和机器可读门禁报告。

## 量化结果

### 实分析 development（37 条）

| 指标 | 结果 |
| --- | ---: |
| Candidate Recall | 100% |
| Top‑1 | 91.9% |
| Top‑2 | 91.9% |
| NDCG@5 | 0.943 |
| Context Precision | 82.9% |
| 预算合规 | 91.9% |
| Forbidden / Duplicate | 0 / 0 |

这一切片已经通过 Candidate、Top‑1、NDCG、Context Precision、预算与安全门禁；Top‑2 距 93% 目标仍差 1 条。

### GTM 259 development（17 条）

| 指标 | 结果 |
| --- | ---: |
| Candidate Recall | 100% |
| Top‑1 | 70.6% |
| Top‑2 | 82.4% |
| NDCG@5 | 0.810 |
| Context Precision | 58.8% |
| 预算合规 | 82.4% |
| Forbidden / Duplicate | 0 / 0 |

把 `candidate_k / rerank_k` 提高到消融矩阵上界后，GTM Candidate Recall 从 88.2% 提升到 100%，说明候选生成问题已经修复；正确对象在候选池中却仍常被相邻定理、命题或定义压过，瓶颈已经明确转到跨语言对象精排。

### 综合判定

机器可读门禁报告对 54 条 development 加权后给出：Candidate Recall 100%、Top‑1 85.2%、Top‑2 88.9%、NDCG@5 0.901、Context Precision 75.3%、预算合规 88.9%。因此严格结论是：**质量门禁未全部通过**。

LLM listwise 在实分析切片有明显收益，但其成功触发路径 p95 达到 27.5 秒，远超 3 秒门禁；远程 embedding 路径也未达到 800 ms。按照原计划的证据边界，LLM 只能保留为离线 judge/bake-off，不能作为在线默认重排器。

## 尚未完成且不能伪造的门禁

1. 至少 40 条未见 sealed retrieval set 仍需人工审核并冻结；
2. 至少 20 条 hard-negative 集仍需人工确认相邻对象边界；
3. 至少 40 条 downstream Tutor 题仍需盲评数学正确性、来源忠实度、关键证明步和提示策略；
4. 100 个真实 shadow turn、canary 与回退审计仍需真实流量；
5. Source Fidelity、数学硬错误率和端到端相对提升不能从检索 development 指标推断。

## 发布决定与下一步

生产 feature flags 继续保持关闭。下一步优先为英文教材引入满足延迟要求的专用 cross-encoder，并以对象 statement/compact view 完成静态、cross-encoder、LLM 三路 bake-off；随后由人工冻结新的 sealed、hard-negative 和 downstream Tutor 集。只有质量、延迟和盲评同时通过，才进入 shadow/canary 和生产默认切换。
