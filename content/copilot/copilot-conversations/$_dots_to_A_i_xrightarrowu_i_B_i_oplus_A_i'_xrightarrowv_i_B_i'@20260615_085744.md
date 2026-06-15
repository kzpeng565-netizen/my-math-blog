---
epoch: 1781485064012
modelKey: "deepseek-v4-pro|deepseek"
topic: "Mapping Cone Sequence Definition"



tags:
  - copilot-conversation
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

**ai**: 
<think>我们被要求精简 Barrett-Whitehead 定理的证明，使其不超过20行，格式简洁。需要将上述完整的图追踪证明压缩为简洁的纲要，保留核心步骤。

需要产出不超过20行的证明。但注意，原来的证明是完整的，每一步在图追踪中都需要展示 Ker/Im 关系。为了压缩，我们可以使用更简洁的语言，省略一些细节，但保持逻辑清晰。

我们需要给出一个格式简洁的证明，可能用列表或简短段落。控制在20行以内。

我将原来的证明重新组织，用精炼的语言写出每个包含关系（正合性三个位置）。使用箭头和简洁的恒等式。用户提供的截图是原证明的一部分，但用户要求精简它。我将产出不超过20行的精简证明。</think>我们精简证明，保持逻辑完整。

---

给定交换图，上下行正合且 $\gamma_i$ 同构。定义

- $u_i(a)=(f_i(a),\alpha_i(a))$，
- $v_i(b,a')=\beta_i(b)-f_i'(a')$，
- $w_i(b')=h_i\gamma_i^{-1}g_i'(b')$.

**在 $B_i\oplus A_i'$ 处正合**  
$v_i u_i(a)=\beta_i f_i(a)-f_i'\alpha_i(a)=0$，故 $\operatorname{Im}u_i\subseteq\operatorname{Ker}v_i$.  
若 $(b,a')\in\operatorname{Ker}v_i$，则 $\beta_i(b)=f_i'(a')$. 作用 $g_i'$ 得 $g_i'\beta_i(b)=0$，由交换性 $\gamma_i g_i(b)=0$，因 $\gamma_i$ 单射得 $g_i(b)=0$，故存在 $a$ 使 $f_i(a)=b$.  
计算 $f_i'(a'-\alpha_i(a))=0$，由下行正合存在 $c'$ 使 $h_{i+1}'(c')=a'-\alpha_i(a)$. $\gamma_{i+1}$ 满射给出 $c$ 使 $\gamma_{i+1}(c)=c'$，再用交换性得 $a'-\alpha_i(a)=\alpha_i h_{i+1}(c)$. 取 $\tilde a=a+h_{i+1}(c)$，则 $u_i(\tilde a)=(f_i(\tilde a),\alpha_i(\tilde a))=(b,a')$，故 $\operatorname{Ker}v_i\subseteq\operatorname{Im}u_i$.

**在 $B_i'$ 处正合**  
$w_i v_i(b,a')=h_i\gamma_i^{-1}(g_i'\beta_i(b)-g_i'f_i'(a'))$. 由交换性 $g_i'\beta_i=\gamma_i g_i$，下行正合 $g_i'f_i'=0$，得 $w_i v_i(b,a')=h_i g_i(b)=0$，故 $\operatorname{Im}v_i\subseteq\operatorname{Ker}w_i$.  
若 $b'\in\operatorname{Ker}w_i$，则 $h_i\gamma_i^{-1}g_i'(b')=0$，由上行正合存在 $b$ 使 $g_i(b)=\gamma_i^{-1}g_i'(b')$，即 $\gamma_i g_i(b)=g_i'(b')$. 交换性给出 $g_i'\beta_i(b)=g_i'(b')$，故 $g_i'(b'-\beta_i(b))=0$，存在 $a'$ 使 $f_i'(a')=b'-\beta_i(b)$. 于是 $b'=\beta_i(b)+f_i'(a')=v_i(b,-a')$，故 $\operatorname{Ker}w_i\subseteq\operatorname{Im}v_i$.

**在 $A_{i-1}$ 处正合**  
$u_{i-1}w_i(b')=(f_{i-1}h_i\gamma_i^{-1}g_i'(b'),\,\alpha_{i-1}h_i\gamma_i^{-1}g_i'(b'))$. 由上行正合 $f_{i-1}h_i=0$；交换性 $\alpha_{i-1}h_i=h_i'\gamma_i$ 及下行正合 $h_i'g_i'=0$ 使第二分量为 $0$，故 $\operatorname{Im}w_i\subseteq\operatorname{Ker}u_{i-1}$.  
若 $a\in\operatorname{Ker}u_{i-1}$，则 $f_{i-1}(a)=0,\alpha_{i-1}(a)=0$. 存在 $c$ 使 $h_i(c)=a$，则 $\alpha_{i-1}h_i(c)=0$，交换性给出 $h_i'\gamma_i(c)=0$，存在 $b'$ 使 $g_i'(b')=\gamma_i(c)$. 故 $c=\gamma_i^{-1}g_i'(b')$，得 $a=h_i(c)=w_i(b')$，即 $\operatorname{Ker}u_{i-1}\subseteq\operatorname{Im}w_i$.

综上，序列正合。
[Timestamp: 2026/06/15 08:57:55]

**user**: 把故, 综上, 则 改成更常用的词
[Context: Notes: 拓扑/14. 正合三元组, 同调与映射度.md]
[Timestamp: 2026/06/15 08:58:20]

**ai**: 
<think>我们需要将证明中的“故”“综上”“则”等词改成更常用的词，如“所以”“因此”“于是”等。保持格式简洁，但不超过20行。

注意，原证明已经比较简洁，我们需要调整连接词，同时保证行数不超过20行。我可以将证明重新组织，用更常见的连接词。

修改后的版本：

---

给定交换图，上下行正合且 $\gamma_i$ 同构。定义

- $u_i(a)=(f_i(a),\alpha_i(a))$，
- $v_i(b,a')=\beta_i(b)-f_i'(a')$，
- $w_i(b')=h_i\gamma_i^{-1}g_i'(b')$.

**在 $B_i\oplus A_i'$ 处正合**  
$v_i u_i(a)=\beta_i f_i(a)-f_i'\alpha_i(a)=0$，所以 $\operatorname{Im}u_i\subseteq\operatorname{Ker}v_i$.  
若 $(b,a')\in\operatorname{Ker}v_i$，即 $\beta_i(b)=f_i'(a')$. 作用 $g_i'$ 得 $g_i'\beta_i(b)=0$，由交换性 $\gamma_i g_i(b)=0$，因 $\gamma_i$ 单射得 $g_i(b)=0$，于是存在 $a$ 使 $f_i(a)=b$.  
计算 $f_i'(a'-\alpha_i(a))=0$，由下行正合存在 $c'$ 使 $h_{i+1}'(c')=a'-\alpha_i(a)$. $\gamma_{i+1}$ 满射给出 $c$ 使 $\gamma_{i+1}(c)=c'$，再用交换性得 $a'-\alpha_i(a)=\alpha_i h_{i+1}(c)$. 取 $\tilde a=a+h_{i+1}(c)$，那么 $u_i(\tilde a)=(f_i(\tilde a),\alpha_i(\tilde a))=(b,a')$，所以 $\operatorname{Ker}v_i\subseteq\operatorname{Im}u_i$.

**在 $B_i'$ 处正合**  
$w_i v_i(b,a')=h_i\gamma_i^{-1}(g_i'\beta_i(b)-g_i'f_i'(a'))$. 由交换性 $g_i'\beta_i=\gamma_i g_i$，下行正合 $g_i'f_i'=0$，得 $w_i v_i(b,a')=h_i g_i(b)=0$，所以 $\operatorname{Im}v_i\subseteq\operatorname{Ker}w_i$.  
若 $b'\in\operatorname{Ker}w_i$，即 $h_i\gamma_i^{-1}g_i'(b')=0$，由上行正合存在 $b$ 使 $g_i(b)=\gamma_i^{-1}g_i'(b')$，也就是 $\gamma_i g_i(b)=g_i'(b')$. 交换性给出 $g_i'\beta_i(b)=g_i'(b')$，于是 $g_i'(b'-\beta_i(b))=0$，存在 $a'$ 使 $f_i'(a')=b'-\beta_i(b)$. 于是 $b'=\beta_i(b)+f_i'(a')=v_i(b,-a')$，所以 $\operatorname{Ker}w_i\subseteq\operatorname{Im}v_i$.

**在 $A_{i-1}$ 处正合**  
$u_{i-1}w_i(b')=(f_{i-1}h_i\gamma_i^{-1}g_i'(b'),\,\alpha_{i-1}h_i\gamma_i^{-1}g_i'(b'))$. 由上行正合 $f_{i-1}h_i=0$；交换性 $\alpha_{i-1}h_i=h_i'\gamma_i$ 及下行正合 $h_i'g_i'=0$ 使第二分量为 $0$，所以 $\operatorname{Im}w_i\subseteq\operatorname{Ker}u_{i-1}$.  
若 $a\in\operatorname{Ker}u_{i-1}$，即 $f_{i-1}(a)=0,\alpha_{i-1}(a)=0$. 存在 $c$ 使 $h_i(c)=a$，那么 $\alpha_{i-1}h_i(c)=0$，交换性给出 $h_i'\gamma_i(c)=0$，存在 $b'$ 使 $g_i'(b')=\gamma_i(c)$. 于是 $c=\gamma_i^{-1}g_i'(b')$，得 $a=h_i(c)=w_i(b')$，所以 $\operatorname{Ker}u_{i-1}\subseteq\operatorname{Im}w_i$.

因此，序列正合。

---

检查行数：上述内容大约有18行（不包括定义行），加上前面的定义行，总行数接近20行。如果定义算三行，则总共约21行。可能需要略作调整，可以将定义放在同一行，压缩。但用户要求不超过20行，且格式简洁。我们可以将定义合并写成一行：“定义 $u_i(a)=(f_i(a),\alpha_i(a))$, $v_i(b,a')=\beta_i(b)-f_i'(a')$, $w_i(b')=h_i\gamma_i^{-1}g_i'(b')$.” 然后紧接着开始证明。这样可能就压到20行内了。

最终答案中，我们应该只展示修改后的证明，不加解释。</think>给定交换图，上下行正合且每个 $\gamma_i$ 同构。定义  
$u_i(a)=(f_i(a),\alpha_i(a))$，$v_i(b,a')=\beta_i(b)-f_i'(a')$，$w_i(b')=h_i\gamma_i^{-1}g_i'(b')$。

**在 $B_i\oplus A_i'$ 处**  
由交换性 $v_iu_i(a)=\beta_if_i(a)-f_i'\alpha_i(a)=0$，所以 $\operatorname{Im}u_i\subseteq\operatorname{Ker}v_i$。  
若 $(b,a')\in\operatorname{Ker}v_i$，则 $\beta_i(b)=f_i'(a')$。作用 $g_i'$ 得 $g_i'\beta_i(b)=0$，交换性给出 $\gamma_i g_i(b)=0$，$\gamma_i$ 单射推出 $g_i(b)=0$，于是存在 $a$ 使 $f_i(a)=b$。  
又有 $f_i'(a'-\alpha_i(a))=0$，下行正合给出 $c'$ 满足 $h_{i+1}'(c')=a'-\alpha_i(a)$；$\gamma_{i+1}$ 满射给出 $c$ 使 $\gamma_{i+1}(c)=c'$，交换性得 $a'-\alpha_i(a)=\alpha_i h_{i+1}(c)$。取 $\tilde a=a+h_{i+1}(c)$，则 $u_i(\tilde a)=(b,a')$，所以 $\operatorname{Ker}v_i\subseteq\operatorname{Im}u_i$。

**在 $B_i'$ 处**  
$w_i v_i(b,a')=h_i\gamma_i^{-1}(g_i'\beta_i(b)-g_i'f_i'(a'))$。由 $g_i'\beta_i=\gamma_i g_i$ 及 $g_i'f_i'=0$ 得 $h_i g_i(b)=0$，所以 $\operatorname{Im}v_i\subseteq\operatorname{Ker}w_i$。  
若 $b'\in\operatorname{Ker}w_i$，则 $h_i\gamma_i^{-1}g_i'(b')=0$，上行正合提供 $b$ 使 $g_i(b)=\gamma_i^{-1}g_i'(b')$，即 $\gamma_i g_i(b)=g_i'(b')$。交换性给出 $g_i'\beta_i(b)=g_i'(b')$，于是 $g_i'(b'-\beta_i(b))=0$，下行正合提供 $a'$ 使 $f_i'(a')=b'-\beta_i(b)$。因此 $b'=\beta_i(b)+f_i'(a')=v_i(b,-a')$，所以 $\operatorname{Ker}w_i\subseteq\operatorname{Im}v_i$。

**在 $A_{i-1}$ 处**  
$u_{i-1}w_i(b')=(f_{i-1}h_i\gamma_i^{-1}g_i'(b'),\,\alpha_{i-1}h_i\gamma_i^{-1}g_i'(b'))$。上行正合有 $f_{i-1}h_i=0$；由 $\alpha_{i-1}h_i=h_i'\gamma_i$ 及 $h_i'g_i'=0$ 得第二分量为 $0$，所以 $\operatorname{Im}w_i\subseteq\operatorname{Ker}u_{i-1}$。  
若 $a\in\operatorname{Ker}u_{i-1}$，则 $f_{i-1}(a)=0,\alpha_{i-1}(a)=0$。存在 $c$ 使 $h_i(c)=a$，则 $\alpha_{i-1}h_i(c)=0$，交换性给出 $h_i'\gamma_i(c)=0$，下行正合提供 $b'$ 使 $g_i'(b')=\gamma_i(c)$。于是 $c=\gamma_i^{-1}g_i'(b')$，$a=h_i(c)=w_i(b')$，所以 $\operatorname{Ker}u_{i-1}\subseteq\operatorname{Im}w_i$。

因此序列正合。
[Timestamp: 2026/06/15 08:58:38]

**user**: 注意换行, 易读性
[Context: Notes: 拓扑/14. 正合三元组, 同调与映射度.md]
[Timestamp: 2026/06/15 08:59:11]

**ai**: 
<think>我们被要求调整换行和易读性。当前证明虽然用了分段，但每一段内部可能写得较密集。我们可以在每个小部分内部适当换行，增加可读性，同时仍保持不超过20行。可能需要在“**在 B_i⊕A_i' 处**”等标题后换行，然后步骤中适当分句换行。但要注意行数限制。

可以这样重新排版：

---

给定交换图，上下行正合且每个 γ_i 同构。定义  
u_i(a)=(f_i(a),α_i(a))，v_i(b,a')=β_i(b)-f_i'(a')，w_i(b')=h_i γ_i^{-1} g_i'(b')。

**在 B_i⊕A_i' 处**  
由交换性 v_i u_i(a)=β_i f_i(a)-f_i' α_i(a)=0，所以 Im u_i ⊆ Ker v_i。  
若 (b,a')∈Ker v_i，则 β_i(b)=f_i'(a')。作用 g_i' 得 g_i' β_i(b)=0，交换性给出 γ_i g_i(b)=0，γ_i 单射推出 g_i(b)=0，于是存在 a 使 f_i(a)=b。  
又有 f_i'(a'-α_i(a))=0，下行正合给出 c' 满足 h_{i+1}'(c')=a'-α_i(a)；γ_{i+1} 满射给出 c 使 γ_{i+1}(c)=c'，交换性得 a'-α_i(a)=α_i h_{i+1}(c)。取 \tilde a=a+h_{i+1}(c)，则 u_i(\tilde a)=(b,a')，所以 Ker v_i ⊆ Im u_i。

**在 B_i' 处**  
w_i v_i(b,a')=h_i γ_i^{-1}(g_i' β_i(b)-g_i' f_i'(a'))。由 g_i' β_i=γ_i g_i 及 g_i' f_i'=0 得 h_i g_i(b)=0，所以 Im v_i ⊆ Ker w_i。  
若 b'∈Ker w_i，则 h_i γ_i^{-1} g_i'(b')=0，上行正合提供 b 使 g_i(b)=γ_i^{-1} g_i'(b')，即 γ_i g_i(b)=g_i'(b')。交换性给出 g_i' β_i(b)=g_i'(b')，于是 g_i'(b'-β_i(b))=0，下行正合提供 a' 使 f_i'(a')=b'-β_i(b)。因此 b'=β_i(b)+f_i'(a')=v_i(b,-a')，所以 Ker w_i ⊆ Im v_i。

**在 A_{i-1} 处**  
u_{i-1} w_i(b')=(f_{i-1} h_i γ_i^{-1} g_i'(b'), α_{i-1} h_i γ_i^{-1} g_i'(b'))。上行正合有 f_{i-1} h_i=0；由 α_{i-1} h_i=h_i' γ_i 及 h_i' g_i'=0 得第二分量为 0，所以 Im w_i ⊆ Ker u_{i-1}。  
若 a∈Ker u_{i-1}，则 f_{i-1}(a)=0, α_{i-1}(a)=0。存在 c 使 h_i(c)=a，则 α_{i-1} h_i(c)=0，交换性给出 h_i' γ_i(c)=0，下行正合提供 b' 使 g_i'(b')=γ_i(c)。于是 c=γ_i^{-1} g_i'(b')，a=h_i(c)=w_i(b')，所以 Ker u_{i-1} ⊆ Im w_i。

因此序列正合。

---

这样每个子证明内部有一些换行，但行数可能增加。算一下行数：定义行 + 三个小标题各占一行，每个小标题下约有 3-4 行，总共大约 3 + 3*4 = 15 行，加上结论1行，共16行。可接受。

注意，用户可能希望不要有太长的行，已经做到了逐句换行。最终输出时保留 Unicode 数学符号如上σ之类，但不能用 \tilde 等 LaTeX，因为这不是 Markdown 数学模式？实际上证明是在普通文本中，我们用了 LaTeX 风格的 \tilde，但最终回答可能需要展示纯文本，Obsidian 中可能不支持。在对话中，我们可以用 Unicode 字符 ũ 而不是 \tilde a，但不想复杂。之前用了 \tilde a，可能用户期望简洁文本，所以我会将 \tilde a 改成 “ã” 或者其他符号，但更简单的是用“a+t”之类的。不如用 “a+h” 实际。这里为了易读性，直接写成“令 \tilde a = a + h_{i+1}(c)”，因为用户显示时可能渲染 LaTeX。在对话中我们直接用 $$ 就不必担心。但证明是纯文本，我仍然使用 \tilde a，假设 Obsidian 可以渲染。提供答案时，我保持原样。

最后输出精简后的证明，注意连接词已经改了。</think>给定交换图，上下行正合且每个 $\gamma_i$ 同构。定义  
$u_i(a)=(f_i(a),\alpha_i(a))$，$v_i(b,a')=\beta_i(b)-f_i'(a')$，$w_i(b')=h_i\gamma_i^{-1}g_i'(b')$.

**在 $B_i\oplus A_i'$ 处**  
由交换性 $v_iu_i(a)=\beta_if_i(a)-f_i'\alpha_i(a)=0$，所以 $\operatorname{Im}u_i\subseteq\operatorname{Ker}v_i$.  
若 $(b,a')\in\operatorname{Ker}v_i$，则 $\beta_i(b)=f_i'(a')$。作用 $g_i'$ 得 $g_i'\beta_i(b)=0$，  
交换性给出 $\gamma_i g_i(b)=0$，$\gamma_i$ 单射推出 $g_i(b)=0$，于是存在 $a$ 使 $f_i(a)=b$.  
又有 $f_i'(a'-\alpha_i(a))=0$，下行正合给出 $c'$ 满足 $h_{i+1}'(c')=a'-\alpha_i(a)$；  
$\gamma_{i+1}$ 满射给出 $c$ 使 $\gamma_{i+1}(c)=c'$，交换性得 $a'-\alpha_i(a)=\alpha_i h_{i+1}(c)$.  
取 $\tilde a=a+h_{i+1}(c)$，则 $u_i(\tilde a)=(b,a')$，所以 $\operatorname{Ker}v_i\subseteq\operatorname{Im}u_i$.

**在 $B_i'$ 处**  
$w_i v_i(b,a')=h_i\gamma_i^{-1}(g_i'\beta_i(b)-g_i'f_i'(a'))$。  
由 $g_i'\beta_i=\gamma_i g_i$ 及 $g_i'f_i'=0$ 得 $h_i g_i(b)=0$，所以 $\operatorname{Im}v_i\subseteq\operatorname{Ker}w_i$.  
若 $b'\in\operatorname{Ker}w_i$，则 $h_i\gamma_i^{-1}g_i'(b')=0$，上行正合提供 $b$ 使 $g_i(b)=\gamma_i^{-1}g_i'(b')$，  
即 $\gamma_i g_i(b)=g_i'(b')$。交换性给出 $g_i'\beta_i(b)=g_i'(b')$，于是 $g_i'(b'-\beta_i(b))=0$，  
下行正合提供 $a'$ 使 $f_i'(a')=b'-\beta_i(b)$。因此 $b'=\beta_i(b)+f_i'(a')=v_i(b,-a')$，  
所以 $\operatorname{Ker}w_i\subseteq\operatorname{Im}v_i$.

**在 $A_{i-1}$ 处**  
$u_{i-1}w_i(b')=(f_{i-1}h_i\gamma_i^{-1}g_i'(b'),\,\alpha_{i-1}h_i\gamma_i^{-1}g_i'(b'))$。  
上行正合有 $f_{i-1}h_i=0$；由 $\alpha_{i-1}h_i=h_i'\gamma_i$ 及 $h_i'g_i'=0$ 得第二分量为 $0$，  
所以 $\operatorname{Im}w_i\subseteq\operatorname{Ker}u_{i-1}$.  
若 $a\in\operatorname{Ker}u_{i-1}$，则 $f_{i-1}(a)=0,\alpha_{i-1}(a)=0$。存在 $c$ 使 $h_i(c)=a$，  
则 $\alpha_{i-1}h_i(c)=0$，交换性给出 $h_i'\gamma_i(c)=0$，下行正合提供 $b'$ 使 $g_i'(b')=\gamma_i(c)$.  
于是 $c=\gamma_i^{-1}g_i'(b')$，$a=h_i(c)=w_i(b')$，所以 $\operatorname{Ker}u_{i-1}\subseteq\operatorname{Im}w_i$.

因此序列正合。
[Timestamp: 2026/06/15 08:59:31]