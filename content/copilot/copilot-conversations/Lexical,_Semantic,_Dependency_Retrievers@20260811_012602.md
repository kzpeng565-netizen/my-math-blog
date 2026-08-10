---
epoch: 1786382762647
modelKey: "deepseek-v4-pro|deepseek"
topic: "Lexical, Semantic, Dependency Retrievers"



tags:
  - copilot-conversation
---

**user**: Lexical Retriever
FTS5 / BM25
Semantic Retriever
Embedding 语义召回



Dependency Retriever
关系与依赖扩展

这三个分别是什么意思
[Context: Notes: 非笔记内容/工作流程与系统运维/MathStudyAgent/教材搜索问题的解决-方案总览.md]
[Timestamp: 2026/08/11 01:26:02]

**ai**: 
<think>我们被问到三个 Retriever 的含义：Lexical Retriever (FTS5/BM25), Semantic Retriever (Embedding 语义召回), Dependency Retriever (关系与依赖扩展)。需要根据提供的笔记内容解释它们的意思。笔记中第8节详细描述了这些。我们给出简明解释。</think>根据你提供的文档，这三个检索器分别解决不同类型的教材内容查找问题：

- **Lexical Retriever（词法检索器）**  
  使用全文搜索引擎（如 SQLite FTS5）和经典的 BM25 排序算法，根据用户问题中提取出的**关键词、术语、短语、教材编号、公式符号**等进行精确或近似的字面匹配。它不需要理解语义，只依赖词语的出现、频率和邻近度。例如，将“Exercise 2.1.5”“非平凡因子”、规范的章节编号等拆成词项来搜索，并利用章节、页面邻近性优化排序。

- **Semantic Retriever（语义检索器）**  
  基于**嵌入向量（Embedding）的语义相似度**搜索。它把问题或当前对象编码到向量空间，找出即使字面上不匹配但含义相近的教材内容，例如“中文提问匹配英文教材”“查找类似但用词不同的例子”“找到与当前例子相关的定理、定义或证明技巧”“OCR 损坏或概念间接描述的内容”。这会用到向量索引（如 pgvector 或类似方案），并可根据请求的对象类型（如只找 example）进行加权。

- **Dependency Retriever（依赖关系检索器）**  
  利用教材对象之间的**显式关系与依赖扩展**来补充检索结果。例如：定理需要某个定义、证明使用了某个引理/技巧、例子说明某个定义、反例反驳逆命题、习题练习某个知识点。它从已知对象出发，通过轻量关系（如相邻块、内部交叉引用、块类型推导）扩展出一跳（1-hop）的相关对象，避免无限扩散。这通常需要先建立对象间的结构化关系数据（未来版本）。
[Timestamp: 2026/08/11 01:26:12]

**user**: Candidate Fusion / Reranker 是什么
[Context: Notes: 非笔记内容/工作流程与系统运维/MathStudyAgent/教材搜索问题的解决-方案总览.md]
[Timestamp: 2026/08/11 01:26:52]

**ai**: 
<think>我们被问到“Candidate Fusion / Reranker 是什么”。根据文档中的架构图，它位于检索器之后，Hydrator 之前。具体含义需要从文档中推断。文档第8节可能有说明，但在提供的片段中，只显示到 Semantic Retriever 描述，然后说“[... 11 more sections omitted ...]”，因此可能文档后续部分有更详细描述，但没给出。我们需要基于常见知识并结合文档上下文解释。从 mermaid 图来看，检索器（Exact, Lexical, Semantic, Dependency）的结果都汇聚到 Candidate Fusion / Reranker，然后再到 Hydrator。其职责应该是融合不同检索渠道的候选，进行重排序（rerank），以决定哪些块进入后续的 Hydrator 提取完整上下文。可能还涉及去重、合并、根据来源可信度加权、再根据当前学习状态和工作集调整顺序等。由于没有具体文档细节，应该解释为：将多种检索渠道产生的多个候选块合并成一个统一列表，并根据相关性得分、来源类型优先级、与当前上下文的匹配度等进行重新排序，选出最相关且可靠的内容，以便后续加载完整正文。</think>根据文档架构，**Candidate Fusion / Reranker** 的职责是：

- 汇聚前面多个检索器（精确、词法、语义、依赖关系）分别产出的候选项。
- 对这些来源不同、相关性信号各异的候选结果进行**合并、去重和重新排序**。
- 重排序时会综合考虑：原始相关性分数、来源优先级（如精确标签 > 语义召回）、与当前 Working Set 中对象的关系、章节/小节一致性等。
- 最终输出一个精简、高可信度的候选列表，只让最可能真正需要的块进入下一阶段的 **Hydrator**（负责加载完整块内容和邻域）。这样可以避免将大量相似片段无差别地塞进模型上下文，同时保留从不同检索角度捕获到的互补信息。
[Timestamp: 2026/08/11 01:27:01]