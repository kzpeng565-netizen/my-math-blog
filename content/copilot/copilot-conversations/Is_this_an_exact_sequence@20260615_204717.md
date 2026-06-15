---
epoch: 1781527637148
modelKey: "deepseek-v4-pro|deepseek"
topic: "Is this an exact sequence"



tags:
  - copilot-conversation
---

**user**: \cdots \rightarrow C_{k+1} \xrightarrow{d_{k+1}} C_k \xrightarrow{d_k} C_{k-1} \rightarrow \cdots 这是正合列吗
[Context: Notes: 拓扑/胞腔同调的计算-1.md]
[Timestamp: 2026/06/15 20:47:17]

**ai**: 
<think>我们需要判断给定的序列 `... -> C_{k+1} -> C_k -> C_{k-1} -> ...` 是否是正合列 (exact sequence)。这是一个给定的胞腔链复形，它本身是一个链复形 (chain complex)，满足 $d_k \circ d_{k+1} = 0$。但正合列要求 $\operatorname{Im} d_{k+1} = \operatorname{Ker} d_k$，这通常并不成立，因为同调群 $H_k = \operatorname{Ker} d_k / \operatorname{Im} d_{k+1}$ 大多情况下非平凡。所以它一般不是正合列，除非所有的同调群都是零（即零调/acyclic）。根据上下文，这是用来计算同调群的链复形，而不是正合列。需要给出明确答案。

因此，回答：不是正合列，它是链复形，满足 $d_k \circ d_{k+1} = 0$，但通常 $\operatorname{Im} d_{k+1} \subsetneq \operatorname{Ker} d_k$，正是这个差商定义了同调群。</think>不是正合列，而是**链复形**（chain complex）。

链复形只需要满足合成映射为零，即 $d_k \circ d_{k+1} = 0$（等价于 $\operatorname{Im} d_{k+1} \subseteq \ker d_k$）。而**正合列**要求更强：$\operatorname{Im} d_{k+1} = \ker d_k$。胞腔同调的非平凡部分正好来自两者不相等的地方，即
$$
H_k(X) \cong \ker d_k / \operatorname{Im} d_{k+1}.
$$
所以这段序列一般不是正合列，除非空间的所有同调群都为零（零调情形）。
[Timestamp: 2026/06/15 20:47:25]