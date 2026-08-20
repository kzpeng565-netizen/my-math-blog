---
epoch: 1787193830799
modelKey: "deepseek-v4-pro|deepseek"
topic: "RetrievalShadowCanary门禁解释"



tags:
  - copilot-conversation
---

**user**: Retrieval/Shadow/Canary门禁是什么
[Context: Notes: 非笔记内容/工作流程与系统运维/MathStudyAgent/MathStudyAgent v3.0｜架构说明.md]
[Timestamp: 2026/08/20 10:43:50]

**ai**: 
<think>我们需要回答用户问题。用户询问“Retrieval/Shadow/Canary门禁是什么”。语言中文。需要基于提供的笔记内容回答。笔记是MathStudyAgent v3.0架构说明。其中提到评测与发布架构、门禁、feature flags等。需要解读 Retrieval/Shadow/Canary 门禁是什么。应该结合笔记内容，引用相关段落。用户可能想知道这些门禁具体含义。需要简洁、准确，用中文回答。不能提及没有访问。根据笔记：

- 第8节评测与发布架构：严格门禁的证据不能互相替代：Development、sealed、hard-negative、下游Tutor、Shadow、Canary。
- Retrieval门禁应该指检索质量门禁：Development检索质量、sealed/hard-negative retrieval，以及暖索引延迟等。可能是“Retrieval / Shadow / Canary 门禁”在架构图中 GATES["Retrieval / Shadow / Canary 门禁"]。
- Shadow 门禁：Shadow 只观察真实流量差异，达到100条后仍需人工检查新增硬失败；不修改回答/Working Set。样本量门槛。
- Canary 门禁：Canary + 回退演练，需要 feature flag 和可验证回退路径。

需要解释三层门禁是什么，以及它们之间证据不可互相替代。还要提到当前状态：检索门禁中 development通过、新sealed/hard-negative待人工；Shadow待真实流量100；Canary未开始。可以引用第8节和第12节、第9.3节、第10节 feature flags。

需要生成中文回答，格式可能用标题或列表。使用 '-' 项目符号。注意要求：markdown bullets use '- ' no leading spaces. 表格使用 github markdown，表头加 ' |'? 用户只是问问题，不一定需要表格。可能使用列表。要回答清楚。

需要明确“Retrieval门禁”包含 Development / sealed / hard-negative retrieval 证据；Shadow门禁是真实流量旁路对比；Canary门禁是灰度发布与回退演练。笔记中有：

- “GATES --> RELEASE["Feature flag 决策与回退"]”
- “DEV_GATE --> SHADOW100; SEALED_RUN --> SHADOW100; BLIND --> SHADOW100; SHADOW100 --> CANARY; CANARY --> PROD”
- “严格门禁的证据不能互相替代：Development 用于诊断和调参；Historical holdout 只保留历史记录，不能重新充当 sealed；新 sealed 与 hard-negative 必须先人工批准和冻结，再运行检索；下游 Tutor 必须使用人工金标、真实注入证据和盲评裁决；模型 judge 只能辅助，不能代替人工数学裁决；Shadow 只观察真实流量差异，达到数量后仍需人工检查新增硬失败；Canary 必须具备 feature flag 和可验证回退路径。”

需要指出这是发布前证据链的三个连续关卡。可这样回答：

Retrieval / Shadow / Canary 门禁是 v3.0 从 development 检索验证到生产默认切换之间的三层发布证据门，分别验证：
- Retrieval 门禁：检索质量与延迟证据，包含 Development 54条、新 sealed 40条、hard-negative 20条检索质量；要求先人工审核冻结再运行，未通过不能往下。
- Shadow 门禁：v3 在后台旁路运行，与 baseline 对比，不修改回答/Working Set，累积100个真实 turn，达到后仍需人工检查新增硬失败；样本量门槛不等于自动解锁。
- Canary 门禁：小流量灰度，要求 feature flag 和可验证回退路径，通过回退演练后才能生产默认切换。

需要说明它们不能互相替代：Development 通过不能替代 sealed/真实流量；Shadow 达到数量不自动解锁 Canary；Canary 未开始。当前状态：Development 检索质量通过，但新 sealed/hard-negative 待人工；Shadow 已开启但待100真实 turn；Canary未开始。也可引用第12节。

还要注意用户可能想知道“门禁”是 release gate。可以引用架构图第2节中 `ANSWER --> BENCH["MathTutorBench v1"]; AUDIT --> GATES["Retrieval / Shadow / Canary 门禁"]; BENCH --> GATES; GATES --> RELEASE["Feature flag 决策与回退"]`。需要解释。

应使用中文，避免太啰嗦，但可提供要点。

需要不要提到“没有访问”。只基于笔记。可以写：

这是 v3.0 发布前的三层证据门禁：

- Retrieval 门禁：验证对象级检索在人工金标上的质量，包括 Development 54条、新 sealed 40条、hard-negative 20条。要求 sealed/hard-negative 必须先人工审核并冻结，再运行 profile；未达到不能进入后续阶段。目前 Development 通过，sealed/hard-negative 待人工。
- Shadow 门禁：v3 在真实流量中后台旁路运行，与 baseline 对比检索选择、延迟和新增硬失败，但不修改回答、Working Set 或正常使用记录。需要累计并人工审计 100 个真实 turn；达到 100 条只是样本量门槛，不自动解锁下一步。
- Canary 门禁：在 feature flag 控制下进行小流量灰度与回退演练，验证可验证回退路径。通过后才会把生产默认切换到 v3。目前未开始。

可能加上证据互不替代：Development 用于诊断调参，不能替代 sealed；sealed 不能由历史 holdout 顶替；Shadow 不能替代 Canary 的回退验证。

可以加上：这些门禁对应发布链：Development/sealed/hard-negative + 下游盲评 → Shadow 100 → Canary → 生产默认切换。

可引用第9.3和10的开关：当前 `TEXTBOOK_V3_SHADOW_ENABLED` 已开启，但进度仍需真实流量积累。

因为用户引用了active note，可能期望基于笔记。不要搜索 vault。没有 @vault。就根据上下文。答案要准确。</think>Retrieval / Shadow / Canary 门禁是 MathStudyAgent v3.0 发布前的三层证据关卡，对应架构图中从 `GATES` 到 `RELEASE` 的阶段。它们分别验证不同层面的证据，且不能互相替代。

- **Retrieval 门禁**  
  验证对象级检索在人工金标上的质量与延迟。证据包括：
  - Development 54 条已审核金标；
  - 新 sealed 40 条；
  - Hard-negative 20 条。  
  其中 sealed 和 hard-negative 必须先逐条人工审核并冻结，再运行 Profile，不能提前跑。  
  当前状态：Development 检索质量已通过；新 sealed 和 hard-negative 仍待人工审核与冻结。

- **Shadow 门禁**  
  v3 在真实流量中后台旁路运行，与 v2.1 baseline 对比检索选择、resolution、总延迟和阶段延迟。  
  Shadow 不修改回答、Working Set 或正常 Tutor 使用记录。需要累计并人工审计 100 个真实 turn；达到 100 条只是样本量门槛，不自动解锁 Canary。  
  当前状态：`TEXTBOOK_V3_SHADOW_ENABLED` 已开启，但仍需真实流量积累。

- **Canary 门禁**  
  在 feature flag 控制下进行小流量灰度发布，并完成回退演练。要求具备 feature flag 和可验证回退路径，验证通过后才允许把生产默认切换到 v3。  
  当前状态：未开始。

一句话概括：  
**Retrieval 门禁证明“检索在人工金标上可靠”，Shadow 门禁证明“真实流量旁路无新增硬失败”，Canary 门禁证明“灰度发布可控制、可回退”，三者共同构成从 development 到生产默认切换的证据链。**
[Timestamp: 2026/08/20 10:44:20]

**user**: Chunk-to-Object聚合的工作流程是什么
[Context: Notes: 非笔记内容/工作流程与系统运维/MathStudyAgent/MathStudyAgent v3.0｜架构说明.md]
[Timestamp: 2026/08/20 10:46:12]

**ai**: 
<think>We need answer based on note. User asks "Chunk-to-Object聚合的工作流程是什么" Chinese. Need explain workflow from note. We have prior context note. Need extract relevant parts: object model, candidate generation and aggregation. Section 5.1 evidence object model: underlying parsed textbook blocks as immutable chunks; object registry organizes consecutive/related blocks into stable objects. Section 5.2 candidate generation and aggregation: multiple queries, multiple channels, multiple chunks of same object first merged into object candidate, then compute scores. Need explain workflow step by step. Maybe include object types, stable ID, source block mapping, boundary confidence, relationships, versioned manifest and events. Need be precise.

Let's retrieve note sections:

5.1:
底层解析产物仍以不可变教材 block 保存。对象注册表把连续或相关 block 组织成稳定对象：
- Definition；
- Theorem / Lemma / Proposition / Corollary；
- Proof；
- Example / Exercise；
- Remark 等辅助对象。

每个对象保存稳定 ID、类型、标签、章节、源 block 映射和边界置信度；对象之间可以记录 prerequisite_of、uses、proves、illustrates 等关系。删除、更新和重建通过版本化 manifest 与事件记录保持可追溯。

5.2:
Semantic 是...主召回；Exact、FTS、术语、结构和关系通道提供互补证据。多个 query、多个通道和同一对象的多个 chunk 先合并成对象候选，再计算：
- best / mean semantic score；
- query-role coverage；
- exact、FTS、term、relation 支持；
- 对象类型与目标类型的一致性；
- required / negative constraints 覆盖；
- anchor、章节与 Working Set 距离；
- 边界质量、冲突风险和重复程度。

Need maybe explain "Chunk-to-Object聚合" specifically happens before detailed scoring? It says multiple queries, multiple channels and same object's chunks first merge into object candidate, then compute. Need describe workflow:

1. 解析层产生不可变 block chunk（证据单元），不能直接作为检索身份。
2. 对象注册表识别连续或相关的 blocks, 按类型构建对象, 记录 ID、类型、标签、章节、源block映射、边界置信度, 记录对象间关系；manifest + events 保证可追溯。
3. 检索时，Planner v3 生成多个语义查询；各通道（Semantic/Exact/FTS/术语/结构/关系) 返回候选 chunks。
4. 聚合：把属于同一对象的多个 chunk（可能来自不同 query、不同通道）合并为一个对象候选，避免重复身份。
5. 对对象候选计算特征/分数：best/mean semantic score, query-role coverage, 各类支持, 类型一致性, constraints覆盖, anchor/章节/WS距离, 边界质量/冲突/重复。
6. 后续才是明确硬预筛、去重、精排、动态选择。

Need maybe include that "chunk 仍是不可变证据单元，对象才是聚合、精排、选择和预算控制的主体" from section 1 core change 1. Include.

Need maybe mention "对象去重" in deterministic prefilter. But workflow asked likely wants process. We can answer in Chinese with bullet list. Use no table? Could use list. Need maybe include diagram? Not necessary. But maybe include short mermaid? User didn't ask. Keep text.

Need ensure not too long. Let's draft:

Chunk-to-Object 聚合把不可变教材 block 提升为可评分、可选择的数学对象，流程如下：

1. 底层解析：PDF 解析输出不可变教材 block，作为 chunk 证据单元；同一事实可能分散在多个 block。
2. 对象注册：对象注册表按连续或相关 block 构建 Definition/Theorem/Lemma/.../Remark；每个对象记录稳定 ID、类型、标签、章节、源 block 映射和边界置信度；对象关系如 prerequisite_of/uses/proves/illustrates；用版本化 manifest + 事件保证删除/更新/重建可追溯。
3. 多通道召回：Planner 生成多个 query；Semantic/Exact/FTS/术语/结构/关系各通道返回候选 chunk。
4. 聚合到对象：把来自不同 query、不同通道、但属于同一对象的多个 chunk 合并为一个对象候选，消除 chunk 级重复，主身份从 chunk 变为对象。
5. 对象级特征计算：对候选对象计算 best/mean semantic score、query-role coverage、exact/FTS/term/relation 支持、类型一致性、required/negative constraint 覆盖、anchor/章节/Working Set 距离、边界质量/冲突/重复度。
6. 后续决策：再进行确定性预筛（去重、硬约束、唯一 exact保护）与对象级精排/动态选择。

关键点: chunk remains immutable evidence, object is aggregation/ranking/selection/budget control subject. So retrieval selects objects, not chunks.

Need maybe mention retrieval ranking only objects. Good.

Let's answer in Chinese.</think>Chunk-to-Object 聚合是 v3.0 中把不可变教材 block 提升为可评分、可选择、可控制预算的“数学对象”的过程。整体流程如下：

1. **底层解析保留 chunk**  
   PDF 解析仍产生不可变教材 block，作为唯一可引用的证据单元。此时 chunk 本身还不是检索的排序身份，同一数学事实可能分散在多个 block 中。

2. **对象注册表构建对象**  
   对象注册表把连续或相关 block 组织成稳定对象，类型包括：
   - Definition
   - Theorem / Lemma / Proposition / Corollary
   - Proof
   - Example / Exercise
   - Remark 等辅助对象

   每个对象保存稳定 ID、类型、标签、章节、源 block 映射和边界置信度；对象之间可记录 `prerequisite_of`、`uses`、`proves`、`illustrates` 等关系。删除、更新和重建通过版本化 manifest 与事件记录保持可追溯。

3. **多查询多通道召回候选 chunk**  
   Planner v3 生成多个 Semantic query，并由 Semantic、Exact、FTS、术语、结构、关系等通道分别召回候选 chunk。

4. **合并为对象候选**  
   把来自不同 query、不同通道，但属于同一对象的多个 chunk 先合并成一个对象候选，完成 chunk 到 object 的聚合。这样就从“相同内容的不同片段”变为“一个稳定对象”，消除 chunk 级重复。

5. **对象级特征计算**  
   对合并后的对象候选计算：
   - best / mean semantic score
   - query-role coverage
   - exact、FTS、term、relation 支持
   - 对象类型与目标类型一致性
   - required / negative constraints 覆盖
   - anchor、章节与 Working Set 距离
   - 边界质量、冲突风险和重复程度

6. **进入后续决策链**  
   聚合后的对象继续进入确定性预筛、去重硬约束、精排和动态选择，最终的选择对象再进入类型化 Hydration 和预算控制。

关键结论：**chunk 仍是不变证据单元，但聚合、精排、选择和上下文预算控制的主体都是对象；检索选择的是数学对象，而不是最小 chunk 片段。**
[Timestamp: 2026/08/20 10:46:37]

**user**: 确定性预筛的工作原理和流程是什么
[Context: Notes: 非笔记内容/工作流程与系统运维/MathStudyAgent/MathStudyAgent v3.0｜架构说明.md]
[Timestamp: 2026/08/20 10:47:41]

**ai**: 
<think>我们需要回答用户关于“确定性预筛的工作原理和流程是什么”。用户说中文。需要基于提供的笔记内容。笔记中相关内容在 5.2 提到“确定性预筛只执行安全规则：保护唯一 exact、删除无对象身份的无效块、对象去重，以及应用类型和范围硬约束。” 以及 5.3 精排与动态选择之前。需要解释确定性预筛的工作原理和流程。注意用户可能在上下文中有 active note。我们需要根据笔记准确回答。

需要找出更多细节：第5章对象级检索链: 5.1 证据对象模型; 5.2 候选生成与聚合 中包含特征计算，然后“确定性预筛只执行安全规则：保护唯一 exact、删除无对象身份的无效块、对象去重，以及应用类型和范围硬约束。” 5.3 精排与动态选择：不要强行注入。可能还有 Planner v3 合同中的 constraints 等。架构说明第4节 Planner v3 合同 includes required / negative constraints, target type, textbook scope. 确定性预筛应用类型和范围硬约束可能与 Planner 计划的 constraints 有关。也要注意“唯一精确命中可以直接结束；精确解析失败或存在多个对象时，才进入受限 Semantic 消歧。” 这可能是预筛前? 在第4节 Planner v3 合同有提到 Exact reference、页码、标签和 Working Set 指代优先。唯一精确命中可以直接结束。可能确定性预筛包含这种 exact 保护? 笔记说“保护唯一 exact”就是保护唯一精确命中不被精排干扰。需要展开。

我们需要回答“工作原理和流程是什么”。可以这样组织：

- 定义：确定性预筛是对象级检索链中介于候选生成/聚合与精排之间的安全规则层，只执行确定、可解释、无模型不确定性的安全过滤；不引入排序或概率判断。
- 目标：保护唯一 exact，去除无效对象，保证对象身份唯一，应用硬约束；避免后续精排错误地淘汰/注入。
- 流程/规则：
  1. 保护唯一 exact：如果 Planner 明确给出 exact_reference/页码/标签/Working Set 指代，且只有一个精确命中，直接保留并通过，甚至可以直接结束（不进入 Semantic 消歧）；若多个精确对象，才进入后续消歧。
  2. 删除无对象身份的无效块：召回结果中尚未被对象注册表映射、无法归入任何 TextbookObject 的 chunk/block 被删除，不能作为候选对象参与排序。
  3. 对象去重：同一对象因多个 query/多个通道/多个 chunk 被重复召回时，合并为一个对象身份；防止同一个对象占据多个候选名额。
  4. 应用类型和范围硬约束：过滤掉不符合 Planner 目标对象类型（Definition/Theorem/Proof/Example 等）、教材范围（指定 textbook/章节）以及 required/negative constraints 不满足的对象。这些是硬约束，不允许 Soft score 覆盖。
- 输出：只有满足所有安全规则的对象进入精排与动态选择。确定性预筛不负责相关性排序，也不负责决定最终选择；它只确保候选集干净、唯一、且不违反计划约束。
- 关键特点：不调用大模型/不依赖语义 score 阈值，无随机性、可复现；只做确定性规则，避免“保护唯一 exact”等被 LLM/特征误伤。

还要提到“多个 query、多个通道和同一对象的多个 chunk 先合并成对象候选，再计算……”。预筛在计算特征后? 从段落顺序看，先合并成对象候选，再计算特征；然后“确定性预筛只执行安全规则”。所以特征可能已经计算，用于后续；预筛只是硬筛。但有些对象级特征如 required/negative constraints 覆盖可能也用于预筛？笔记把 constraints 覆盖列在特征计算，而预筛“应用类型和范围硬约束”，类型硬约束可能从 Planner plan 的目标类型。需要区分：特征计算是收集信息，预筛真正强制约束。

需要准确。可以引用原文“确定性预筛只执行安全规则：保护唯一 exact、删除无对象身份的无效块、对象去重，以及应用类型和范围硬约束。” 并展开。也可以提及“Selector 不简单截取 Top-K...输出状态...低置信时最多允许一次指定缺失类型和概念的补检索；仍不足则返回澄清或 unresolved，不把‘最不差’的对象强行注入。” 这可能属于后续动态选择，不属于预筛，但可以说明预筛之后。

还要考虑用户也许需要流程图表？可以用列表。

注意回答语言中文。不要用英文标签可能不好？可以使用中文但保留代码标识。我们要保持简洁。

需要检查是否在 note 中有更多预筛细节？比如第5.2 “确定性预筛只执行安全规则：保护唯一 exact、删除无对象身份的无效块、对象去重，以及应用类型和范围硬约束。” 没有更多。所以我们需要从上下文合理引申，不要虚构太多。可以基于这些四类展开。但注意“保护唯一 exact”也可能涉及第4节：“Exact reference、页码、标签和 Working Set 指代优先。唯一精确命中可以直接结束；精确解析失败或存在多个对象时，才进入受限 Semantic 消歧。” 这可以引用。但这是 Planner 合同，不是预筛? 可能确定性预筛保护唯一 exact 与之一致。可以说明。

“删除无对象身份的无效块”：回收通道可能返回 block 但不在对象注册表，或者对象注册未完成，应删除。对象去重：“同一对象因多个 query/通道/chunk 被合并”。

“应用类型和范围硬约束”：类型 = 目标对象类型，范围 = 教材范围（如指定 textbook，章节）。还有 required/negative constraints？笔记中 Planner 合同有 required / negative constraints，特征计算有 required / negative constraints 覆盖，预筛可能也应用这些硬约束？文本只写类型和范围硬约束，可能 constraints 的硬部分也包含？要谨慎，不能扩展太远。但我们可以说“这些硬约束至少包括类型和范围，也可能包括 Planner 给出的 required/negative constraints 中可确定性判断的部分”但这有点推测。最好stick to 原文：类型和范围硬约束。硬约束可能由 Planner 输出目标类型和教材范围。可以提 required/negative？ 为避免不准确，只提类型和范围。但也可说“Planner 合同中的目标对象类型、教材范围等需要满足的硬约束”。

需要给出“流程”步骤清晰。可以写：

确定性预筛位于候选生成/聚合之后、精排/动态选择之前，职责是排除不应进入排序的对象，而不是排序。

流程：

1. 从多通道召回结果和对象聚合结果中确认唯一 exact 命中的优先级。若 Planner 指定了 exact_reference / 页码 / 标签 / Working Set 指代，且唯一命中，则直接保留甚至可以直接结束，不需要 Semantic 消歧；若同一 exact 解析对应多个对象，则不能此阶段断定，保留待后续消歧。
2. 删除无对象身份的无效块：没有 Object ID / 无法映射到对象注册表的 chunk 被移除。
3. 对象去重：把属于同一 TextbookObject 的多个 chunk/多通道命中合并为单个对象候选；删除重复对象。
4. 应用硬约束：过滤掉不满足 Planner 的目标对象类型、教材范围等确定性约束的对象。
5. 输出干净的对象候选集，交给精排和动态选择。

可以加“为什么是确定性的”：不使用语义 score 阈值、不调用 LLM、不排序，因此可复现、可审计；防止唯一 exact 或精确引用被语义分数干扰，也防止无效/重复对象占用 Primary/Support 名额。

注意格式 bullet 使用 '- '。

回答时不要提“我无法访问”等。基于上下文。可引用 [[MathStudyAgent v3.0｜架构说明]]? 不需要。

用户可能想看到“工作原理和流程”详细一些，我们可以适当解释。最终答案 medium length。

Let's formulate final in Chinese with headings maybe.

Need be careful with "对象去重" 与 "合并成对象候选" 发生在预筛之前？文本说“多个 query、多个通道和同一对象的多个 chunk 先合并成对象候选，再计算...确定性预筛只执行安全规则...”。这意味着合并成对象候选发生在特征计算之前，而预筛在之后。所以对象去重可能已经在聚合阶段发生？但文本又说预筛包含对象去重。可能理解：候选生成阶段聚合会合并，但预筛仍需“对象去重”作为安全规则确保没有重复对象（如不同通道/query在计算前未完全合并？或者对象注册表可能产生边界重叠）。可以简单说：即使聚合阶段已合并，确定性预筛仍执行对象去重，确保同一对象在候选集中只出现一次。这样没问题。

需要说明“保护唯一 exact”可能发生在预筛前？文本“Exact reference、页码、标签和 Working Set 指代优先。唯一精确命中可以直接结束；精确解析失败或存在多个对象时，才进入受限 Semantic 消歧。” 这属于 Planner 合同。可能预筛会执行此规则。可以表述。

Let's generate final.</think>确定性预筛是对象级检索链中**候选生成/聚合之后、精排与动态选择之前**的一层安全过滤。它不做排序，也不引入模型判断，只执行确定、可复现、可审计的安全规则。

## 工作原理

预筛的目标是保证进入精排的对象候选集是**干净的、唯一的、不违反硬约束的**，防止：

- 唯一精确命中被语义分数误淘汰；
- 无对象身份的无效块混入候选；
- 同一对象重复占用多个候选名额；
- 不符合 Planner 目标类型或教材范围的候选进入后续选择。

它的核心是**只做安全过滤，不做相关性排序**。

## 流程

1. **保护唯一 exact**  
   如果 Planner 明确给出了 exact reference、页码、标签或 Working Set 指代，并且解析结果只有一个精确命中，则该对象被直接保留，甚至可以直接结束检索，不再进入 Semantic 消歧。  
   如果精确解析失败，或同一 exact 对应多个对象，则不会在此阶段强行断定，而是保留该歧义进入后续受控消歧。

2. **删除无对象身份的无效块**  
   对召回结果中无法映射到对象注册表、没有稳定 Object ID 的 chunk / block，直接删除。它们不能作为对象候选参与精排或选择。

3. **对象去重**  
   对来自不同 query、不同通道、不同 chunk，但属于同一个 TextbookObject 的重复命中，合并为单个对象候选。确保同一个数学对象不会在候选集中重复出现、占用多个位置。

4. **应用类型和范围硬约束**  
   过滤掉不满足 Planner 输出约束的对象，至少包括：
   - 目标对象类型（Definition / Theorem / Proof / Example 等）不一致的对象；
   - 不在指定教材范围、章节范围内的对象。  
   这些是硬约束，不能用语义分数或排序权重覆盖。

5. **输出干净候选集**  
   经过上述过滤后，剩余对象才进入对象级精排和动态选择，再决定 Primary / Support 及最终 Hydration。

关键点：确定性预筛不依赖语义 score 阈值、不调用大模型，只执行稳定规则，因此结果可复现、可审计。
[Timestamp: 2026/08/20 10:48:28]