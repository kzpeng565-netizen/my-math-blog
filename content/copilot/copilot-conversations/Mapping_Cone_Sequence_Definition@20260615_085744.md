---
epoch: 1781485064012
modelKey: deepseek-v4-pro|deepseek
tags:
  - copilot-conversation
topic: Mapping Cone Sequence Definition
---

**user**: $$ \dots \to A_{i} \xrightarrow{u_i} B_{i} \oplus A_{i}' \xrightarrow{v_i} B_{i}' \xrightarrow{w_i} A_{i-1} \to \dots $$

其中为了书写简便，我们定义这三个映射为：

- $u_i(a) = (f_i(a), \alpha_i(a))$
    
- $v_i(b, a') = \beta_i(b) - f_i'(a')$
    
- $w_i(b') = h_i(\gamma_i^{-1}(g_i'(b')))$
    

下面我们通过**图追法 (Diagram Chasing)** 分三步来证明该序列在 $B_i \oplus A_i'$，$B_i'$ 和 $A_{i-1}$ 处均是正合的。根据题目条件，上下两行都是正合序列，并且所有的 $\gamma$ 均为同构。

### 第一步：证明在 $B_i \oplus A_i'$ 处正合 ($\text{Im}(u_i) = \text{Ker}(v_i)$)

**1. 证明 $\text{Im}(u_i) \subseteq \text{Ker}(v_i)$：**

任取 $a \in A_i$，我们需要证明 $v_i(u_i(a)) = 0$。

$$ v_i(u_i(a)) = v_i(f_i(a), \alpha_i(a)) = \beta_i(f_i(a)) - f_i'(\alpha_i(a)) $$

由于图的第一块正方形是交换的，即 $\beta_i \circ f_i = f_i' \circ \alpha_i$，因此：

$$ \beta_i(f_i(a)) - f_i'(\alpha_i(a)) = 0 $$

所以 $\text{Im}(u_i) \subseteq \text{Ker}(v_i)$。

**2. 证明 $\text{Ker}(v_i) \subseteq \text{Im}(u_i)$：**

任取 $(b, a') \in \text{Ker}(v_i)$，即 $\beta_i(b) - f_i'(a') = 0$，也就是 $\beta_i(b) = f_i'(a')$。

将映射 $g_i'$ 作用在两边，得到：

$$ g_i'(\beta_i(b)) = g_i'(f_i'(a')) $$

因为底行在 $B_i'$ 处正合，所以 $g_i' \circ f_i' = 0$，故 $g_i'(\beta_i(b)) = 0$。

利用第二块正方形的交换性 ($\gamma_i \circ g_i = g_i' \circ \beta_i$)，我们有：

$$ \gamma_i(g_i(b)) = 0 $$

因为 $\gamma_i$ 是同构，故单射，所以必有 $g_i(b) = 0$。

这说明 $b \in \text{Ker}(g_i)$。由顶行在 $B_i$ 处正合 ($\text{Ker}(g_i) = \text{Im}(f_i)$)，存在 $a \in A_i$ 使得 $f_i(a) = b$。

现在我们考虑 $u_i(a) = (f_i(a), \alpha_i(a)) = (b, \alpha_i(a))$。我们还不能确定 $a'$ 就是 $\alpha_i(a)$，所以计算它们的差：

$$ f_i'(a' - \alpha_i(a)) = f_i'(a') - f_i'(\alpha_i(a)) = \beta_i(b) - \beta_i(f_i(a)) = \beta_i(b) - \beta_i(b) = 0 $$

（这里用到了前面得出的 $\beta_i(b) = f_i'(a')$ 以及交换性 $f_i' \circ \alpha_i = \beta_i \circ f_i$）。

这说明 $a' - \alpha_i(a) \in \text{Ker}(f_i')$。由底行的正合性，存在 $c' \in C_{i+1}'$ 使得 $h_{i+1}'(c') = a' - \alpha_i(a)$。

由于 $\gamma_{i+1}$ 也是同构（即满射），存在 $c \in C_{i+1}$ 使得 $\gamma_{i+1}(c) = c'$。

利用最左侧的图交换性 ($\alpha_i \circ h_{i+1} = h_{i+1}' \circ \gamma_{i+1}$)，我们得到：

$$ a' - \alpha_i(a) = h_{i+1}'(\gamma_{i+1}(c)) = \alpha_i(h_{i+1}(c)) $$

移项得到 $a' = \alpha_i(a + h_{i+1}(c))$。

现在我们令 $\tilde{a} = a + h_{i+1}(c) \in A_i$。

- 一方面，$\alpha_i(\tilde{a}) = a'$。
    
- 另一方面，$f_i(\tilde{a}) = f_i(a) + f_i(h_{i+1}(c)) = b + 0 = b$（因为顶行正合，$f_i \circ h_{i+1} = 0$）。
    

因此，$u_i(\tilde{a}) = (f_i(\tilde{a}), \alpha_i(\tilde{a})) = (b, a')$。这就证明了 $\text{Ker}(v_i) \subseteq \text{Im}(u_i)$。

### 第二步：证明在 $B_i'$ 处正合 ($\text{Im}(v_i) = \text{Ker}(w_i)$)

**1. 证明 $\text{Im}(v_i) \subseteq \text{Ker}(w_i)$：**

任取 $(b, a') \in B_i \oplus A_i'$，需要证明 $w_i(v_i(b, a')) = 0$。

$$ w_i(\beta_i(b) - f_i'(a')) = w_i(\beta_i(b)) - w_i(f_i'(a')) $$

分别计算这两项：

- 第一项：$w_i(\beta_i(b)) = h_i(\gamma_i^{-1}(g_i'(\beta_i(b))))$。利用交换性 $g_i' \circ \beta_i = \gamma_i \circ g_i$，得到 $h_i(\gamma_i^{-1}(\gamma_i(g_i(b)))) = h_i(g_i(b))$。因为顶行正合，所以 $h_i \circ g_i = 0$。
    
- 第二项：$w_i(f_i'(a')) = h_i(\gamma_i^{-1}(g_i'(f_i'(a'))))$。因为底行正合，所以 $g_i' \circ f_i' = 0$，该项为 $0$。
    

两者相减为 $0$，故 $\text{Im}(v_i) \subseteq \text{Ker}(w_i)$。

**2. 证明 $\text{Ker}(w_i) \subseteq \text{Im}(v_i)$：**

任取 $b' \in \text{Ker}(w_i)$，这意味着：

$$ h_i(\gamma_i^{-1}(g_i'(b'))) = 0 $$

所以 $\gamma_i^{-1}(g_i'(b')) \in \text{Ker}(h_i)$。由顶行正合性 ($\text{Ker}(h_i) = \text{Im}(g_i)$)，存在 $b \in B_i$ 使得：

$$ g_i(b) = \gamma_i^{-1}(g_i'(b')) $$

两边同时作用 $\gamma_i$，得到 $\gamma_i(g_i(b)) = g_i'(b')$。

利用交换图，我们知道 $\gamma_i \circ g_i = g_i' \circ \beta_i$，所以：

$$ g_i'(\beta_i(b)) = g_i'(b') \implies g_i'(b' - \beta_i(b)) = 0 $$

这说明 $b' - \beta_i(b) \in \text{Ker}(g_i')$。由底行正合性，存在 $a' \in A_i'$ 使得 $f_i'(a') = b' - \beta_i(b)$。

整理等式得到：

$$ b' = \beta_i(b) + f_i'(a') = \beta_i(b) - f_i'(-a') $$

这正是 $v_i(b, -a')$。因此 $b' \in \text{Im}(v_i)$。

### 第三步：证明在 $A_{i-1}$ 处正合 ($\text{Im}(w_i) = \text{Ker}(u_{i-1})$)

这里我们要连接到下一个映射 $u_{i-1} = (f_{i-1}, \alpha_{i-1})$。

**1. 证明 $\text{Im}(w_i) \subseteq \text{Ker}(u_{i-1})$：**

任取 $b' \in B_i'$，需要计算 $u_{i-1}(w_i(b')) = (f_{i-1}(w_i(b')), \alpha_{i-1}(w_i(b')))$。

- 第一分量：$f_{i-1}(h_i(\gamma_i^{-1}(g_i'(b'))))$。由于顶行正合，$f_{i-1} \circ h_i = 0$，故该分量为 $0$。
    
- 第二分量：$\alpha_{i-1}(h_i(\gamma_i^{-1}(g_i'(b'))))$。
    
    利用图中第三块正方形的交换性 $\alpha_{i-1} \circ h_i = h_i' \circ \gamma_i$，将该式改写为：
    
    $$ h_i'(\gamma_i(\gamma_i^{-1}(g_i'(b')))) = h_i'(g_i'(b')) $$
    
    由于底行正合，$h_i' \circ g_i' = 0$，故该分量也为 $0$。
    

结果为 $(0,0)$，所以 $\text{Im}(w_i) \subseteq \text{Ker}(u_{i-1})$。

**2. 证明 $\text{Ker}(u_{i-1}) \subseteq \text{Im}(w_i)$：**

任取 $a \in \text{Ker}(u_{i-1})$，意味着 $f_{i-1}(a) = 0$ 且 $\alpha_{i-1}(a) = 0$。

因为 $f_{i-1}(a) = 0$ ($a \in \text{Ker}(f_{i-1})$)，由顶行正合性，存在 $c \in C_i$ 使得 $h_i(c) = a$。

因为 $\alpha_{i-1}(a) = 0$，我们有 $\alpha_{i-1}(h_i(c)) = 0$。利用图交换性 ($\alpha_{i-1} \circ h_i = h_i' \circ \gamma_i$)，得到：

$$ h_i'(\gamma_i(c)) = 0 $$

这说明 $\gamma_i(c) \in \text{Ker}(h_i')$。由底行正合性，存在 $b' \in B_i'$ 使得 $g_i'(b') = \gamma_i(c)$。

由于 $\gamma_i$ 是同构，我们可以反解出 $c$：

$$ c = \gamma_i^{-1}(g_i'(b')) $$

把这个 $c$ 代回原式 $a = h_i(c)$，得到：

$$ a = h_i(\gamma_i^{-1}(g_i'(b'))) = w_i(b') $$

这就证明了 $a \in \text{Im}(w_i)$。

**结论：**

通过严密的图追法，我们证明了该序列在任意 $i$ 指标处的三个节点均满足“核等于像”的正合条件。因此，所构建的序列：

$$ \dots \to A_{i} \xrightarrow{(f_i, \alpha_i)} B_{i} \oplus A_{i}' \xrightarrow{\beta_i - f_i'} B_{i}' \xrightarrow{h_i \circ \gamma_i^{-1} \circ g_i'} A_{i-1} \to \dots $$

构成一个长正合序列。证明完毕。

帮我把它精简成为不超过20行的证明, 格式简洁
[Context: Notes: 拓扑/14. 正合三元组, 同调与映射度.md]
[Timestamp: 2026/06/15 08:57:44]