---
epoch: 1781081562131
modelKey: "deepseek-v4-pro|deepseek"
topic: "Orthogonal Matrix Definition"



tags:
  - copilot-conversation
---

**user**: orthogonal metrix 这是啥
[Context: Notes: 拓扑/14..md]
[Timestamp: 2026/06/10 16:52:42]

**ai**: 
<think>我们被问到 "orthogonal metrix 这是啥"，结合 active note 上下文，第7条写着 "令$A\in O(n+1)$, 也就是orthogonal metrix"。用户可能是在问 orthogonal metrix 是什么意思，或者是笔记中的拼写错误（应该是 orthogonal matrix）。我们需要解释 orthogonal matrix（正交矩阵）的定义。同时考虑上下文，可能是拓扑课上的问题，也许需要联系 $S^n$ 等。用户只是简单问 "orthogonal metrix 这是啥"，所以回答什么是正交矩阵即可。可以顺便指出拼写错误。</think>看起来你的笔记里有个小笔误：**orthogonal metrix** 应该是 **orthogonal matrix**，中文叫 **正交矩阵**。

---

### 正交矩阵的定义

一个 $n \times n$ 实矩阵 $A$ 叫做 **正交矩阵** (orthogonal matrix)，如果它满足：

$$
A^{T} A = A A^{T} = I
$$

其中 $A^{T}$ 是 $A$ 的转置，$I$ 是单位矩阵。

等价地说：

- $A$ 的行向量构成 $\mathbb{R}^{n}$ 的一组**标准正交基**
- $A$ 的列向量构成 $\mathbb{R}^{n}$ 的一组**标准正交基**
- $A^{-1} = A^{T}$
- $\det(A) = \pm 1$

---

### 记号 $O(n)$

笔记里写的 $O(n+1)$ 指的是 **$(n+1) \times (n+1)$ 正交矩阵构成的群**，叫作 **正交群** (orthogonal group)：

$$
O(n+1) = \{ A \in GL(n+1, \mathbb{R}) \mid A^{T}A = I \}
$$

---

### 为什么在拓扑里出现？

正交矩阵经常和球面 $S^{n}$ 联系在一起，比如：

- $S^{n}$ 可以看作 $\mathbb{R}^{n+1}$ 中的单位球，而 $O(n+1)$ 恰好是保持 $\mathbb{R}^{n+1}$ 中内积（从而保持球面）的线性变换群
- 笔记第 6 题在说 $S^{n}$ 到自身的映射的度数，第 7 题引入正交矩阵很可能是在构造某个具体的球面自映射，比如对径映射 $x \mapsto -x$（它是正交矩阵 $A=-I$ 作用在 $S^{n}$ 上）
[Timestamp: 2026/06/10 16:52:54]