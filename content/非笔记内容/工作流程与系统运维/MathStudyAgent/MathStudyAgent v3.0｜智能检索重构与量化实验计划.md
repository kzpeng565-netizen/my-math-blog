# MathStudyAgent v3.0｜智能检索重构与量化实验计划

> 状态：设计讨论稿，冻结指标后进入实现
>
> 日期：2026-08-19
>
> 关联：[[教材搜索问题的解决-方案总览]]、[[MathStudyAgent 愿景书]]、[[MathStudyAgent v2.1｜架构图说明]]

<!-- ai_provenance: source=codex; date=2026-08-19; verification=source-backed; retrieved_notes="教材搜索问题的解决-方案总览.md, MathStudyAgent 愿景书.md, MathStudyAgent v2.1｜架构图说明.md" -->

## 1. 决策摘要

v3.0 的第一目标不是继续增加检索通道，而是把现有“能召回相关内容”的系统改造成“能稳定选出一到两个正确教材对象”的系统。

主链确定为：

```text
Reference Resolution
  → Planner v3：生成检索意图，而不是只生成关键词
  → Semantic-first Candidate Retrieval
  → Chunk-to-Object Aggregation
  → Deterministic Prefilter
  → Query–Object Semantic Reranker
  → Constrained Primary Selector
  → Selective Hydration
  → Minimum Sufficient Context
```

三条原则不变：

1. 能精确解析指代时，先精确解析，不用 Semantic 猜测；
2. 对非精确、跨语言、相关知识和相似对象查询，Semantic 是主召回，FTS 是补充信号；
3. 搜索可以宽，进入 Tutor 的 Active Context 必须窄。

旧讨论和参考图片提出：

\[
\text{candidate\_k} \gg \text{rerank\_k} > \text{active\_k}.
\]

这个方向有外部研究和当前金标结果支持；但“例子 3 个、定理 1–2 个、证明 1–2 个”只能作为初始策略，不能当作普适常数。最终数值必须由 MathStudyAgent 自己的 (k) 消融实验决定。

## 2. 当前事实基线

### 2.1 已完成的人工评测

80 条 authored case 中，71 条金标通过、9 条被退回。以 71 条有效金标计算：

| 方案 | 命中 | 命中率 | Top 1 | 平均 NDCG@5 | 对象预算内 |
| --- | ---: | ---: | ---: | ---: | ---: |
| AI 关键词 + FTS | 29/71 | 40.8% | 23/71 | 0.374 | 70.4% |
| 纯 Semantic | 64/71 | 90.1% | 56/71 | 0.858 | 31.0% |

两路并集覆盖 66/71（93.0%）。这说明：

- Semantic 已经明显优于关键词 + FTS，应该成为模糊检索的主召回；
- 当前主要瓶颈已经从“完全找不到”转成“候选过多、相邻对象混淆、Primary 选择不准”；
- FTS 仍有少量独有命中，适合保留为标签、公式、专有名词和字面证据通道；
- 90.1% 是“金标出现在 Primary 列表中”的检索命中率，不是系统回答正确率。

完整逐题数据见工作区 `docs/retrieval-paired-result-review-2026-08-19.md`。

### 2.2 当前代码已经有什么

当前实现并非完全没有重排，而是只有一个**静态加权排序骨架**：

- `policy.py` 已区分 `candidate_k / rerank_k / active_k`；
- `ranker.py` 按来源类型、对象类型、少量意图词和证据等级做固定加分；
- `service.py` 会去重、截取 `rerank_k`，再按 `active_k.maximum` 选择 Primary；
- `hydrator.py` 在选择后加载对象正文，并区分 compact/full 表示。

但它还不能称为真正的语义重排：

1. 排序器没有联合理解“用户问题—候选对象”的数学含义；
2. 静态来源加分可能压过真正的候选相关度；
3. 没有成组判断互补性、重复性和错误定理风险；
4. `active_k` 实际按最大值截取，而不是根据边际收益动态停止；
5. 低分差只在选择后标记 ambiguous，并不会阻止可疑对象进入上下文；
6. compact proof 主要依赖首尾截断，不等于可靠的 proof skeleton；
7. 当前 Semantic 首先召回 chunk，再补对象归属，对象边界错误会直接传递到排序阶段。

### 2.3 当前 Planner 的主要限制

当前 `semantic_query` 默认就是用户原句；Full Planner 主要补充教材语言关键词、对象类型、关系意图和章节锚点。它还不能输出：

- 多个承担不同作用的 Semantic query；
- 目标对象应满足的数学条件和结论；
- 不应选择哪些相邻概念或对象类型；
- 当前查询需要“相似”“对比”“反例”还是“依赖”；
- Primary 与 Support 各需要几个、分别承担什么角色；
- 候选不足时怎样改写查询，以及何时应停止检索。

因此 Planner 仍然偏向“关键词生成器”，而不是可审计的检索意图规划器。

## 3. 旧方案中需要修正的认识

### 3.1 固定的 (k) 不是科学结论

旧对话把“相似例子 3 个、定理 1–2 个、复杂证明 1–2 个”收敛为默认值。这个数值适合作为工程起点，但证据存在明显适用范围：

- thinking trace 研究中，(k=3) 在 AIME 上比 (k=1,5) 更稳定，但检索对象是推理轨迹，不是教材定理；
- 通用 Contextual Retrieval 的最佳设置可能向模型提供 20 个 chunk，与数学 Tutor 的最小上下文目标并不相同；
- 不同模型对多文档干扰的敏感度不同，不能把其他模型结果直接等同于当前 Sol；
- 对“比较三个定理”和“解释一个定理”，最优 active_k 本来就不同。

所以策略应写成“初值 + 可调范围 + 退出条件”，不能只写死一个数字。

### 3.2 高 Recall 不等于可用上下文

当前 Semantic 的 90.1% 命中与 31.0% 预算合规同时出现，已经直接证明：

> Candidate Recall 和 Active Context Precision 必须独立优化和独立报告。

扩大 `candidate_k` 可以帮助召回，但不能直接扩大 `active_k`。反过来，重排也不能找回候选池里不存在的金标。因此必须分别诊断：

- Planner failure；
- candidate-generation failure；
- chunk-to-object failure；
- rerank failure；
- selection/budget failure；
- hydration/context failure。

### 3.3 “有 Reranker 类”不等于完成了重排设计

真正的重排至少要回答三个问题：

1. 单个候选是否真正回答当前查询；
2. 候选之间是否重复、冲突或承担互补角色；
3. 多选一个对象带来的信息增益，是否大于注意力和误导成本。

当前静态分数只部分回答第一个问题，尚未回答后二者。

## 4. v3.0 可量化目标

### 4.1 北极星目标

面对需要教材证据的问题，系统能够：

1. 在候选池中高概率包含正确对象；
2. 将正确对象稳定排到前一到两位；
3. 不把半相关定理、相邻证明或重复例子注入 Tutor；
4. 候选不足时显式返回 unresolved、澄清或一次受控补检索；
5. 最终提高数学回答正确率和来源忠实度，而不是只提高离线 Recall。

### 4.2 首轮建议门禁

这些数值必须在运行新 sealed 集之前冻结：

| 层级 | 指标 | 当前可见基线 | v3.0 首轮目标 |
| --- | --- | ---: | ---: |
| Candidate | Gold Recall@candidate_k | Semantic 90.1% 的近似参考 | ≥96%，且每个主要切片 ≥90% |
| Rank | Top 1 gold accuracy | 56/71 = 78.9% | ≥85% |
| Rank | Top 2 gold accuracy | 尚未单独冻结 | ≥93% |
| Rank | NDCG@5 | 0.858 | ≥0.90 |
| Context | within-budget rate | 31.0% | ≥90% |
| Context | forbidden-object rate | 0 | 保持 0 |
| Context | duplicate-primary rate | 尚无 | ≤5% |
| Context | Context Precision | 尚无 | ≥0.80 |
| Context | Context Utilization | 尚无 | ≥0.70 |
| Answer | Source Fidelity pass rate | 尚无 | ≥95% |
| Answer | 数学硬错误率 | 尚无 | ≤5%，且不劣于 v2.1 |
| Answer | 端到端通过率 | 尚无 | 相对 v2.1 提升至少 8 个百分点 |

其中 Context Utilization 指最终回答中实际使用或引用的注入对象数除以注入对象总数。它需要来源归因记录，不能只让模型自报。

### 4.3 延迟门禁

建议分路径约束，不用一个 p95 掩盖不同成本：

| 路径 | 建议 p95 |
| --- | ---: |
| Exact / Working Set | ≤300 ms |
| Semantic + 对象聚合 + 本地/专用 reranker | ≤800 ms |
| 仅歧义场景触发的 LLM final selector | ≤3 s，触发率 ≤25% |

如果模型重排不能在质量上稳定超过专用 reranker，或者延迟超过门禁，应保留为离线 judge，不进入在线主链。

## 5. Planner v3：从关键词生成器到检索意图规划器

### 5.1 职责边界

Planner 只决定“找什么、在哪里找、哪些条件必须满足”，不负责：

- 回答数学问题；
- 直接指定最终教材对象；
- 根据评测题 ID 产生特殊规则；
- 决定一个候选一定正确；
- 把 `active_k` 自动填满。

### 5.2 建议合同

```python
class RetrievalPlanV3:
    should_retrieve: bool
    mode: Literal[
        "exact_reference",
        "semantic_discovery",
        "similar_objects",
        "dependency_lookup",
        "comparison",
    ]

    anchor_references: list[str]
    target_object_types: list[str]
    target_concepts: list[str]
    relation_intents: list[str]

    semantic_queries: list[SemanticQuery]
    lexical_fallback_terms: list[str]

    required_constraints: list[str]
    negative_constraints: list[str]
    scope: RetrievalScope

    desired_roles: list[str]
    primary_range: tuple[int, int]
    support_range: tuple[int, int]

    confidence: float
    ambiguity_reasons: list[str]
    stop_condition: str
```

`SemanticQuery` 至少包含：

```python
class SemanticQuery:
    text: str
    role: Literal[
        "direct_match",
        "mechanism",
        "conditions_conclusion",
        "contrast",
        "counterexample",
        "proof_technique",
    ]
    object_types: list[str]
    weight: float
```

### 5.3 模式行为

**Exact reference**

- 标签、页码、用户粘贴原文和 Working Set 指代优先；
- 精确命中且唯一时不运行全局 Semantic；
- exact 失败或出现多个对象时，再进入受限 Semantic 消歧。

**Semantic discovery / similar objects**

- Semantic 是主召回；
- Planner 生成 1–3 个保持完整数学语义的查询，而不是只生成名词列表；
- FTS 用于公式、专有词、作者用语和精确短语补召回；
- 多 query 结果先在对象层合并，再进入重排。

**Dependency lookup**

- 先以当前目标对象为锚点；
- 关系边是候选来源，不是自动注入许可；
- 只返回完成当前推理所需的定义、引理或定理。

## 6. Semantic-first 候选召回

### 6.1 从 chunk-first 转向 object-first

保留 chunk 作为证据单元，但索引和排序的主身份应是数学对象：

```text
Definition / Theorem / Lemma / Proposition / Corollary
Example / Exercise / Proof / Remark
```

每个对象至少建立三种表示：

1. `source_text`：可引用的教材原文；
2. `retrieval_summary`：用于检索的短自然语言描述；
3. `structured_view`：对象类型、标签、假设、结论、章节和父子关系。

定理搜索研究显示，为数学对象生成简短自然语言 slogan 再做 embedding，明显优于直接 embedding 原始 LaTeX；但生成的 summary 只能用于检索，不能作为教材事实引用。

### 6.2 多视图 Embedding

建议按对象类型建立不同检索视图：

- theorem/lemma：名称 + 假设 + 结论 + contextual summary；
- proof：目标 + 关键技巧 + 依赖对象 + proof skeleton；
- example/exercise：问题条件 + 核心构造 + 展示的概念；
- definition：被定义对象 + 精确定义 + 别名。

同一对象可以有多个 embedding，但最终只占一个候选名额。对象分数可由多视图的最大值、加权均值和 query-role coverage 组合得到。

### 6.3 通道角色

| 通道 | 主职责 | 不应承担的职责 |
| --- | --- | --- |
| Exact | 编号、标签、页码、当前指代 | 模糊相关知识发现 |
| Semantic | 概念、机制、相似对象、跨语言 | 证明教材原文精确出现某个字符串 |
| FTS | 公式、专有词、原文短语、低成本补召回 | 单独承担自然语言理解 |
| Relation | 从已知对象找前置/证明/推论 | 无锚点无限扩展 |

### 6.4 初始候选策略

| 查询类型 | candidate_k 初值 | 备注 |
| --- | ---: | --- |
| exact | 1–10 | 唯一精确命中直接结束 |
| similar examples | 24 | 多 query 合并后对象去重 |
| related theorems | 16 | 对象类型强约束 |
| similar proofs | 16 | 需要 proof-view embedding |
| dependency | 10 | 只允许 0-hop/1-hop |
| broad semantic discovery | 24 | 低置信度时最多改写一次 |

这些是实验起点，不是发布常数。

## 7. 真正的对象级重排与选择

### 7.1 Stage A：对象聚合与确定性预筛

先把同一对象的多个 chunk、多个 semantic query 和多个通道命中合并。每个候选保留：

- best/mean semantic score；
- 命中的 query role 数量；
- exact/FTS/term/relation 支持；
- 对象类型与 Planner 目标类型一致性；
- 章节、Working Set 和 anchor 距离；
- 对象质量和边界置信度；
- 与其他候选的重复程度；
- required/negative constraints 覆盖情况。

确定性规则只做安全处理：保护唯一 exact、删除无效对象、合并重复、应用类型和范围硬约束。然后保留约 8 个对象进入真正 reranker。

### 7.2 Stage B：Query–Object Semantic Reranker

对 Top 8 候选进行 query–object 联合评分。首轮应比较三种实现，而不是预先认定某一种最好：

1. 当前静态特征排序；
2. 专用 cross-encoder reranker；
3. 结构化 LLM listwise reranker。

输入使用 compact object view，不加载完整正文。输出至少包含：

```json
{
  "object_id": "...",
  "direct_relevance": 0.0,
  "constraint_coverage": 0.0,
  "role_fit": "primary|support|contrast|reject",
  "conflict_risk": 0.0,
  "reason_code": "..."
}
```

LLM reranker 只能看到候选元数据和 compact view，不能生成新 object ID，也不能修改教材事实。

### 7.3 Stage C：Constrained Primary Selector

最终不是简单取 Top-K，而是在数量约束下最大化集合效用：

\[
U(S)=\sum_{x\in S}R(x)
+\lambda\operatorname{Coverage}(S)
+\mu\operatorname{RoleFit}(S)
-\delta\operatorname{Redundancy}(S)
-\rho\operatorname{ConflictRisk}(S)
-\tau\operatorname{ContextCost}(S).
\]

初始策略：

| 模式 | Primary 初值 | 角色约束 |
| --- | ---: | --- |
| exact | 1 | 目标对象 |
| similar examples | 最多 3 | 最相似 + 互补 + 差异/反例；没有价值时少于 3 |
| related theorems | 1–2 | 主定理 + 必要互补定理 |
| similar proofs | 1–2 | 主证明技巧 + 可选互补证明 |
| dependency | 1–2 compact | 只选完成当前步骤的必要依赖 |

是否加入第二、第三个对象由**边际信息增益**决定，而不是为了达到最大数量。

### 7.4 置信度、拒选与补检索

需要在 development 集上校准：

- Top 1 分数；
- Top 1/Top 2 margin；
- 多 query 是否一致指向同一对象；
- required constraints 覆盖率；
- exact、semantic、FTS、relation 是否交叉支持；
- 对象边界质量。

建议状态：

```text
resolved
ambiguous
unresolved
missing_dependency
```

低置信度时不注入“最不差”的候选。只允许一次指定类型和概念的补检索；仍不足则澄清或 unresolved。

## 8. Selective Hydration 与最小充分上下文

Hydration 必须发生在 Primary Selector 之后。

| 对象类型 | 默认加载 |
| --- | --- |
| Definition | 精确定义与必要符号 |
| Theorem/Lemma | 名称、假设、结论；默认不加载证明 |
| Example/Exercise | 条件、核心构造、关键结论 |
| Proof | 目标、关键技巧、proof skeleton；用户追问时再加载全文 |
| Support | compact representation，默认不加载其证明 |

需要把当前按字符首尾截断的 compact 表示升级为结构化生成物，并保存其原始 block 映射。最终上下文同时受三类预算约束：

- Primary 对象数量；
- Supporting 对象数量；
- 总字符/token 数。

正常问答的完整外部数学对象原则上不超过 3 个；比较、综述和多跳任务可以例外，但必须由 Planner 显式声明并进入独立评测切片。

## 9. 科学实验设计

### 9.1 数据集划分

1. **Development**：现有实分析 37 条有效金标 + GTM 259 的 17 条有效金标，共 54 条；允许诊断和调参。
2. **Historical holdout**：Durrett 的 17 条有效金标只用于记录历史结果。由于结果已经人工查看，不再作为调参后的 sealed 证明。
3. **New sealed retrieval set**：至少 40 条未见案例，exact、概念描述、相关定理/依赖、相似例子/证明各至少 10 条。
4. **Downstream Tutor set**：至少 40 条真实数学问题，具有答案正确性、来源忠实度、关键证明步和提示要求金标。
5. **Hard-negative set**：至少 20 条，专门覆盖相邻定理、定理/证明、命题/推论、习题/例子和同主题不同条件。

每条 retrieval case 除目标 object ID 外，还要标注：

- acceptable IDs；
- forbidden IDs；
- relevance grade 0/1/2；
- 期望 object type；
- Primary/Support 角色；
- max_primary；
- gold rationale；
- 是否允许 unresolved。

### 9.2 消融矩阵

按同一批查询成对比较：

| 实验 | Planner | 召回 | 对象聚合 | Reranker | Selector |
| --- | --- | --- | --- | --- | --- |
| B0 | 当前 | FTS | 当前 | 当前静态 | 当前 |
| B1 | 原句 | Semantic | 当前 | 当前静态 | 当前 |
| A1 | 原句 | Semantic | v3 | 当前静态 | v3 |
| A2 | Planner v3 | Semantic | v3 | 当前静态 | v3 |
| A3 | Planner v3 | Semantic + FTS | v3 | cross-encoder | v3 |
| A4 | Planner v3 | Semantic + FTS | v3 | LLM listwise | v3 |
| A5 | 最优离线组合 | Semantic + FTS + relation | v3 | 最优 | v3 + hydration |

这样可以回答：提升究竟来自 Planner、Semantic、多通道互补、对象聚合、reranker，还是最终预算选择。

### 9.3 (k) 消融

不要只比较一组默认值：

```text
candidate_k ∈ {8, 12, 16, 24, 32}
rerank_k    ∈ {4, 6, 8, 12}
active_k    ∈ {1, 2, 3, 4, 5}
```

按查询模式分别报告，不把例子、定理和证明混成一个平均值。除了检索指标，还要固定同一个 Tutor 和 Prompt，测：

- 数学回答正确率；
- 来源忠实度；
- 错误定理引用率；
- Context Precision / Utilization；
- token、延迟和模型调用成本。

最终策略选择采用 Pareto frontier：在正确率无显著下降的前提下，优先选择对象更少、延迟更低的配置。

### 9.4 统计方法

- 对同一 case 使用 paired comparison；
- Hit/未 Hit 使用 McNemar 检验；
- NDCG、MRR、Context Precision 和端到端分数使用 10,000 次 paired bootstrap，报告 95% 置信区间；
- 按教材、查询模式、对象类型和跨语言切片报告；
- 小样本切片只报告区间和原始计数，不用单个百分比下强结论；
- 生成模型存在随机性时，每个端到端配置至少重复 3 次，并保持模型、温度、Prompt 和证据包版本固定。

### 9.5 标注与盲法

- sealed query 在参数冻结前不可查看结果；
- 评审者不知道答案来自哪个系统版本；
- 数学争议案例保留原书页码和对象证据；
- 有条件时由两名评审独立判断；只有一名人工时，采用延迟复审并把争议案例单独列出；
- 模型 judge 只能作辅助，不能替代数学金标和最终人工裁决。

## 10. 分阶段实施计划

### Phase 0：冻结合同与基线

交付：

- `RetrievalPlanV3`、candidate、rerank、selection trace schema；
- development / historical / sealed 边界；
- B0/B1 的不可变报告；
- 新指标实现与报告模板。

退出条件：任何失败都能归因到 Planner、召回、对象、重排、选择或上下文阶段。

### Phase 1：对象级 Semantic 召回

交付：

- object retrieval summary 与多视图 embedding；
- chunk-to-object 聚合；
- Semantic 主召回、FTS 辅助和通道审计；
- Candidate Recall 实验。

退出条件：development Recall@candidate_k 达到门禁，且无 query-specific boost。

### Phase 2：重排与动态选择

交付：

- deterministic prefilter；
- cross-encoder/LLM reranker bake-off；
- constrained selector、边际停止和置信度校准；
- (k) 消融报告。

退出条件：Top 1/Top 2、NDCG、预算和 forbidden-object 门禁全部通过。

### Phase 3：Hydration 与端到端验证

交付：

- 类型化 compact/full representation；
- Minimum Sufficient Context；
- 一次受控补检索；
- Tutor 端到端盲评。

退出条件：Source Fidelity、数学硬错误率、端到端提升和延迟同时通过。

### Phase 4：Shadow 与发布

交付：

- 生产请求的 shadow 运行，不影响用户回答；
- 至少 100 个真实 turn 的候选、选择和延迟审计；
- feature flag canary、回退和版本化报告。

退出条件：真实流量没有新增硬失败，离线收益在 shadow 中能够复现，再切换生产默认。

## 11. 优先级与暂缓项

### P0

1. Planner v3 合同；
2. 对象边界、proof parent 和 chunk-to-object 聚合；
3. Semantic-first 候选召回；
4. 真正的 query–object reranker；
5. 动态 Primary Selector、置信度和 unresolved；
6. 新 sealed 集和分阶段评测。

### P1

1. 类型化 Hydration 和 Minimum Sufficient Context；
2. 来源忠实度和数学正确性 evaluator；
3. 一次受控补检索；
4. shadow/canary、延迟和成本监控。

### 暂缓

- 自动学习者模型；
- 多 Agent 自主搜索；
- 多跳 GraphRAG；
- 在线反馈自动改 Prompt 或权重；
- 在检索和答案正确率未稳定前扩展自动选题与长期课程规划。

## 12. 主要风险与防护

| 风险 | 防护 |
| --- | --- |
| Planner 生成看似合理但错误的约束 | 规则下限、schema 校验、保留原始 query、失败回退 |
| Semantic 召回相邻但错误的定理 | 对象类型、条件/结论 view、hard-negative 集、cross-encoder |
| Reranker 过拟合 54 条 development | 不训练 query-specific 权重；新 sealed 一次性验收 |
| LLM reranker 幻造对象或改写教材事实 | 只允许从给定 object IDs 中选择；输出 schema；原文为唯一引用来源 |
| active_k 过小导致依赖缺失 | Primary/Support 分离；一次指定缺失类型的补检索 |
| active_k 过大干扰推理 | 边际停止、Context Precision、Utilization 和 downstream (k) 实验 |
| 新方案离线好、线上慢 | 分路径 p95、LLM selector 触发率上限、shadow/canary |

## 13. 证据边界

以下证据支持设计方向，但不替代本项目实验：

1. [Anthropic Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)：在其跨领域实验中，Contextual Embedding + Contextual BM25 再加入 reranking，将 top-20 检索失败率从 5.7% 降到 1.9%。这支持混合召回和二阶段重排，但其向生成模型提供 20 chunks 的设置不能直接移植到数学 Tutor。
2. [Lost in the Middle](https://arxiv.org/abs/2307.03172)：相关信息位于长上下文中部时，多个模型表现显著下降；在开放域 QA 中，从 20 增到 50 个检索文档只带来约 1–1.5% 的边际提升。它支持“上下文窗口大不等于应注入更多对象”。
3. [More Documents, Same Length](https://arxiv.org/abs/2503.04388)：固定 token 总量和相关信息位置，只增加文档数量，多数模型仍下降，MuSiQue/2WikiMultiHopQA 最多下降约 10%/20%。这支持控制对象数量和半相关候选。
4. [How Is LLM Reasoning Distracted by Irrelevant Context?](https://arxiv.org/abs/2505.18761)：GSM-DC 的受控实验表明，无关上下文会影响推理路径选择和算术正确性。这支持建立数学 hard-negative 和 downstream (k) 实验。
5. [Semantic Search over 9 Million Mathematical Theorems](https://arxiv.org/abs/2602.05216)：以定理为一等检索对象、使用自然语言 slogan 和 Qwen3 Embedding；在其验证集上，cross-encoder 将 theorem Hit@1 从 17.1% 提高到 18.9%，MRR@20 从 24.3% 提高到 27.0%。这支持 object-first、检索表示和 reranker，但其研究级定理库与本项目教材对象不同。
6. [RAG over Thinking Traces Can Improve Reasoning Tasks](https://arxiv.org/abs/2605.03344)：在 AIME 及三种 reader/representation 设置中比较 (k=1,3,5)，(k=3) 最稳定，(k=5) 有时因噪声或冗余下降。这支持把 3 作为相似例子/思路的初始实验值，但不能证明定理和证明也应固定为 3。

结论是：旧对话和图片的方向成立，但参数必须通过本项目的对象级检索、上下文利用率和端到端数学正确率共同校准。

## 14. 实施前需要冻结的决策

1. 新 sealed 集使用新教材，还是使用三本教材中从未查看的章节；
2. 在线 reranker 优先比较专用 cross-encoder 与 LLM listwise，还是先只实现 cross-encoder；
3. 普通语义检索允许的 p95 延迟和单轮模型调用成本；
4. 新评测由一名人工延迟复审，还是安排第二名独立评审；
5. 端到端 Tutor 评测首批采用 40 条还是扩大到 80 条，以获得更窄的置信区间。

这些决策冻结后，再拆解 migration、索引、服务、UI、测试和部署任务。
