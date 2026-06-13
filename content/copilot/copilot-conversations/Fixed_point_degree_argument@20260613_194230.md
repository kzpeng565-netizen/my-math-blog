---
epoch: 1781350950418
modelKey: "deepseek-v4-pro|deepseek"
topic: "Fixed point degree argument"



tags:
  - copilot-conversation
---

**user**: 设$f(x)\neq x\quad \forall x\in S^{1}$
则$g(x)= \frac{f(x)}{x}$良定义(复数域上), $g:S^{1}\to S^{1}$
$$
deg(g)=deg(f(x)\cdot x^{-1})=deg(f(x))+deg(x^{-1})=-1
$$
我们注意到, $g(x)\neq1$, 所以$g:S^{1}\to S^{1}-\{1\}\cong[0,1]\simeq c$
因此$g$同伦与常值映射, 与$deg(g)=-1$矛盾.


我这里是不是直接写错了了
[Context: Notes: 拓扑/10. 映射度&函子性&Van Kampen.md]
[Timestamp: 2026/06/13 19:42:30]

**ai**: 
<think>我们被问到：在笔记中习题6的解答里，有一段推导：
设$f(x)\neq x\quad \forall x\in S^{1}$
则$g(x)= \frac{f(x)}{x}$良定义(复数域上), $g:S^{1}\to S^{1}$
$$
deg(g)=deg(f(x)\cdot x^{-1})=deg(f(x))+deg(x^{-1})=-1
$$
然后说注意到 $g(x)\neq 1$，所以 $g:S^{1}\to S^{1}-\{1\}\cong[0,1]\simeq c$，因此 $g$ 同伦于常值映射，与 $deg(g)=-1$ 矛盾。问：这里是不是直接写错了？我们需要检查映射度的计算及推理。

首先，题目是：设 $f: S^1 \rightarrow S^1$ 零伦，证明 $f$ 有一个不动点 $f(x)=x, x \in S^1$。

解答是反证法：假设没有不动点，即 $f(x) \neq x$ 对所有 $x$ 成立。定义 $g(x) = f(x)/x$ （把 $S^1$ 看作单位复数）。因为 $f(x), x$ 都在 $S^1$ 上，且 $f(x) \neq x$，所以 $g(x)$ 不等于 1，且 $g(x) \in S^1$。于是 $g: S^1 \to S^1$ 的像不包含 1，所以它可以分解为 $S^1 \to S^1\setminus\{1\} \hookrightarrow S^1$。而 $S^1\setminus\{1\}$ 同胚于开区间 $(0,2\pi)$，可缩，所以 $g$ 同伦于常值映射，因此 $deg(g)=0$。

另一方面，映射度关于乘法：$g(x) = f(x) \cdot x^{-1}$。映射度的加法性质：对于映射 $S^1 \to S^1$，有 $deg(f\cdot h) = deg(f) + deg(h)$（这里“乘法”是群乘法，即复数乘法，对应于基本群里的加法，因为 $\pi_1(S^1)=\mathbb{Z}$ 是加法群）。逆映射 $x \mapsto x^{-1}$ 的度是 $-1$。若 $f$ 是零伦的，则 $deg(f)=0$。那么 $deg(g) = deg(f) + deg(x^{-1}) = 0 + (-1) = -1$。解答中写的是 $deg(g) = -1$，这假设了 $f$ 零伦（题目条件）。这里写的是 $deg(g)=deg(f(x)\cdot x^{-1}) = deg(f(x)) + deg(x^{-1}) = -1$，但是实际上应该明确 $deg(f)=0$ 因为 $f$ 零伦。所以 $deg(g) = 0 + (-1) = -1$。这是对的。

然后，由 $g(x) \neq 1$ 得到 $g$ 的像包含在 $S^1 \setminus \{1\}$，可缩，所以 $deg(g)=0$。与 $deg(g)=-1$ 矛盾。这个逻辑没问题。

提问者问“我这里是不是直接写错了了”，可能怀疑 $deg(g) = deg(f(x)) + deg(x^{-1})$ 这个等式对零伦 $f$ 是否成立，或者是 $deg(x^{-1}) = -1$ 是否正确，或者该推导是否有误。通常，映射度是加性的：对于 $S^1 \to S^1$ 的映射 $f, g$，有 $deg(f \cdot g) = deg(f) + deg(g)$，因为乘法对应基本群同态将生成元加起来。这里 $g = f \cdot (x \mapsto x^{-1})$。零伦映射诱导的基本群同态是平凡的，所以 $deg(f)=0$。恒等映射度是1，逆映射将生成元 $1$ 映到 $-1$，所以度是 $-1$。因此 $deg(g) = 0 + (-1) = -1$。没问题。

可能提问者认为 $deg(g) = deg(f(x) \cdot x^{-1}) = deg(f(x)) + deg(x^{-1})$ 而 $deg(f(x))$ 不是 $0$？ 零伦映射的度是0。所以写 $-1$ 默认 $deg(f)=0$。所以解答中确实应该明确指出因为 $f$ 零伦，所以 $deg(f)=0$。原笔记里写的是：
$$
deg(g)=deg(f(x)\cdot x^{-1})=deg(f(x))+deg(x^{-1})=-1
$$
这里直接得出 $-1$，隐含 $deg(f)=0$，虽然没写，但结合上下文知道 $f$ 零伦，所以没问题。没有写错。

但是提问者可能困惑的是：$deg(f(x))+deg(x^{-1}) = 0 + (-1) = -1$，或者认为 $x^{-1}$ 的度不是 $-1$ 吗？ 是的。所以没有写错。

更仔细看一下笔记原文：
"设 $f: S^1 \rightarrow S^1$ 零伦，证明 $f$ 有一个不动点 $f(x)=x, x \in S^1$ ．□

设$f(x)\neq x\quad \forall x\in S^{1}$
则$g(x)= \frac{f(x)}{x}$良定义(复数域上), $g:S^{1}\to S^{1}$
$$
deg(g)=deg(f(x)\cdot x^{-1})=deg(f(x))+deg(x^{-1})=-1
$$
我们注意到, $g(x)\neq1$, 所以$g:S^{1}\to S^{1}-\{1\}\cong[0,1]\simeq c$
因此$g$同伦与常值映射, 与$deg(g)=-1$矛盾."

这里计算 $deg(g)$ 时，如果 $f$ 只是假设没有不动点，还没有用到零伦条件？ 要得出 $deg(g) = -1$ 需要 $deg(f)=0$，这来自 $f$ 零伦。这一步确实用了零伦的条件。所以没错。

可能提问者注意到 $g(x) = f(x)/x$，用度数的加性，但是否定了 $deg(f)$ 是0？零伦意味着 $f \simeq constant$，而常数映射的度是0。所以度是0。正确。

或者提问者怀疑 $g(x) \neq 1$ 能否推出 $g$ 可缩？ $S^1 \setminus \{1\}$ 同胚于 $\mathbb{R}$，是可缩的，所以任何映射到该空间的复合必定零伦。因此 $deg(g)=0$。正确。

所以答案应该是没有写错，推理正确。应该解释这个推理并确认无误。</think>你的推导是正确的，没有写错。这里梳理一下逻辑：

- 已知 $f\colon S^1 \to S^1$ 零伦，因此 $\deg(f)=0$。
- 反设 $f(x)\neq x$ 对所有 $x\in S^1$ 成立，则在复数乘法下 $g(x)=f(x)/x$ 是良定义的连续映射 $S^1\to S^1$，且 $g(x)\neq 1$。
- 映射度的加法性质：对 $S^1$ 上的映射，$\deg(f\cdot h)=\deg(f)+\deg(h)$，逆时针映射 $x\mapsto x^{-1}$ 的度为 $-1$。于是
  $$\deg(g)=\deg(f)+\deg(x^{-1})=0+(-1)=-1.$$
- 由 $g(x)\neq 1$ 知 $g$ 的像包含于 $S^1\setminus\{1\}$，而 $S^1\setminus\{1\}$ 可缩，故 $g$ 零伦，$\deg(g)=0$。
- 矛盾，故 $f$ 必有不动点。

你的笔记里直接写 $\deg(g)=\deg(f(x))+\deg(x^{-1})=-1$ 已经隐含了零伦条件 $\deg(f)=0$，结合上下文没有问题。
[Timestamp: 2026/06/13 19:42:50]

**user**: 这个加法性质证明证明
[Context: Notes: 拓扑/映射度的使用.md]
[Timestamp: 2026/06/13 19:48:56]

**ai**: 
<think>我们被要求证明映射度的加法性质：对于连续映射 $f,g: S^1 \to S^1$（将 $S^1$ 视作复平面上的单位圆），定义乘法 $fg(x) = f(x)\cdot g(x)$（复数乘法），则 $\deg(fg) = \deg(f) + \deg(g)$。

在笔记“映射度的使用”中，提到“加法性质: $deg(fg)=deg(f)+deg(g)$​, $f,g:S^{1}\to S^{1}$”。我们需要给出证明。用户希望证明这个性质。

我们需要提供严格的证明。可以使用基本群的语言，因为 $\pi_1(S^1,1) \cong \mathbb{Z}$，而映射度对应于诱导同态 $f_*: \mathbb{Z} \to \mathbb{Z}$ 的像（即乘以 $\deg(f)$）。对于乘法映射 $fg$，它在基本群上的作用可以用 $f$ 和 $g$ 的作用表示。已知基本群 $S^1$ 的群运算是加法（来自道路的连接），而映射 $f$ 诱导的同态乘以 $\deg(f)$。那么 $fg$ 的诱导同态如何与乘法结构相关？我们视 $S^1$ 是拓扑群（复数乘法群），则乘法映射 $S^1 \times S^1 \to S^1$ 诱导基本群同态 $\pi_1(S^1 \times S^1) \cong \pi_1(S^1) \oplus \pi_1(S^1) \to \pi_1(S^1)$，也就是 $(a,b) \mapsto a+b$。而 $fg$ 是复合 $S^1 \xrightarrow{\Delta} S^1 \times S^1 \xrightarrow{f \times g} S^1 \times S^1 \xrightarrow{m} S^1$，其中 $\Delta(x)=(x,x)$，$m$ 是乘法。那么在基本群层面，$\Delta_*: \mathbb{Z} \to \mathbb{Z}\oplus\mathbb{Z}$ 是对角映射 $1 \mapsto (1,1)$，$(f\times g)_*: (a,b) \mapsto (\deg(f) a, \deg(g) b)$，$m_*: (a,b) \mapsto a+b$。复合得到 $1 \mapsto (1,1) \mapsto (\deg(f),\deg(g)) \mapsto \deg(f)+\deg(g)$。所以 $(fg)_*(1) = \deg(f)+\deg(g)$，因此 $\deg(fg) = \deg(f)+\deg(g)$。

可以解释得更初等：利用覆盖空间提升的方法。设提升 $\tilde{f}, \tilde{g}: \mathbb{R} \to \mathbb{R}$ 使得 $f(e^{2\pi i t}) = e^{2\pi i \tilde{f}(t)}$，同样 $g$。那么 $fg(e^{2\pi i t}) = f(e^{2\pi i t}) g(e^{2\pi i t}) = e^{2\pi i (\tilde{f}(t) + \tilde{g}(t))}$。那么 $\tilde{f}+\tilde{g}$ 是 $fg$ 的一个提升。映射度 $\deg(fg) = (\tilde{f}+\tilde{g})(1) - (\tilde{f}+\tilde{g})(0) = (\tilde{f}(1)-\tilde{f}(0)) + (\tilde{g}(1)-\tilde{g}(0)) = \deg(f) + \deg(g)$。这需要说明提升的选取以及唯一性。由于 $fg$ 的提升与 $\tilde{f}+\tilde{g}$ 可能差一个常数整数，但度数差不变。更准确地说，选取提升 $\tilde{f}, \tilde{g}$ 满足 $\tilde{f}(0)=0, \tilde{g}(0)=0$ 那么 $\tilde{f}+\tilde{g}$ 也是提升且 $(fg)(e^{2\pi i 0})=f(1)g(1)=1$，所以提升满足 $\tilde{f}(0)+\tilde{g}(0)=0$？如果是这样，可以选择以 0 开始。总之提升方法证明很简单，适合初等水平。

另外，可以用同伦论：映射 $fg$ 在基本群中的像就是 $f$ 和 $g$ 在复数乘法群下的乘积，因为 $\pi_1$ 的群运算是回路拼接，而复乘法对应于回路拼接？实际上把 $S^1$ 视为拓扑群，基本群的加法和群的乘法结构相容：回路 $\alpha, \beta$ 的逐点乘积 $\alpha \cdot \beta$ 同伦于 $\alpha$ 然后 $\beta$ 的拼接，因为 $S^1$ 是拓扑群时有 $\alpha * \beta \simeq \alpha \cdot \beta$。利用这个事实，可以得到 $(fg)_* (1) = f_*(1) + g_*(1)$。这个更代数拓扑一些。

无论哪种方式，我们都可以给出证明。考虑到用户笔记是基于拓扑课程的，可能更喜欢基本群或提升的方法。我们给出一个清晰简明的证明，使用覆盖空间提升方法，并结合基本群解释。

注意用户前面提到的“映射度的使用”笔记中提了加法性质。我们给出证明时要回应“证明这个加法性质”。

结合上下文，用户之前问了习题中关于映射度计算是否正确，现在又问证明加法性质。我们以友好、教学的方式回答。

回答结构：
- 回顾问题：要求证明 $\deg(fg) = \deg(f) + \deg(g)$。
- 提供两种证明：
  1. 使用提升和覆盖空间（直观，利用实数覆盖）。
  2. 使用基本群（更代数拓扑）。
- 注意说明 $S^1$ 是拓扑群时的相容性。
- 总结。

最终输出用中文，带数学公式。</think>这是一个非常核心的性质，我们来透彻地证明它。  
先把设置说清楚：把圆周看作复平面上的单位圆 \(S^1 = \{z\in\mathbb{C}: |z|=1\}\)，赋予复数乘法使之成为拓扑群。对于连续映射 \(f,g: S^1 \to S^1\)，定义乘积映射  
\[
(fg)(z) = f(z)\cdot g(z).
\]  
目标：\(\deg(fg) = \deg(f) + \deg(g)\)。

下面给出两种证明——一种用覆盖空间提升，非常直观；另一种用基本群，体现代数结构。

---

## 证明一：用覆盖空间的提升法

**回忆映射度的提升定义**：  
复盖映射 \(p: \mathbb{R} \to S^1, \; t \mapsto e^{2\pi i t}\) 是泛复盖。对任意连续映射 \(h: S^1 \to S^1\)，存在一个提升 \(\tilde{h}: \mathbb{R} \to \mathbb{R}\) 使得  
\[
h(e^{2\pi i t}) = e^{2\pi i \tilde{h}(t)}, \qquad \forall t\in\mathbb{R}.
\]  
映射度定义为  
\[
\deg(h) = \tilde{h}(1) - \tilde{h}(0).
\]  
（提升在相差一个整常数的意义下唯一，但差值这个整数是唯一确定的。）

**对 \(f\) 和 \(g\) 分别取提升**  
选取 \(\tilde{f}, \tilde{g}: \mathbb{R}\to\mathbb{R}\)，满足  
\[
f(e^{2\pi i t}) = e^{2\pi i \tilde{f}(t)},\quad
g(e^{2\pi i t}) = e^{2\pi i \tilde{g}(t)}.
\]  
并可以规范地要求 \(\tilde{f}(0)=0,\ \tilde{g}(0)=0\)（这不影响度数，只是让书写更干净）。

**构造 \(fg\) 的提升**  
计算：
\[
(fg)(e^{2\pi i t}) = f(e^{2\pi i t})\, g(e^{2\pi i t})
= e^{2\pi i \tilde{f}(t)}\, e^{2\pi i \tilde{g}(t)}
= e^{2\pi i \big(\tilde{f}(t) + \tilde{g}(t)\big)}.
\]  
所以映射 \(\widetilde{fg}(t) := \tilde{f}(t) + \tilde{g}(t)\) 正好是 \(fg\) 的一个提升。

**度数的加法**  
按照定义：
\[
\begin{aligned}
\deg(fg) &= \widetilde{fg}(1) - \widetilde{fg}(0) \\
&= \big(\tilde{f}(1)+\tilde{g}(1)\big) - \big(\tilde{f}(0)+\tilde{g}(0)\big) \\
&= \big(\tilde{f}(1)-\tilde{f}(0)\big) + \big(\tilde{g}(1)-\tilde{g}(0)\big) \\
&= \deg(f) + \deg(g).
\end{aligned}
\]
证毕。

---

## 证明二：用基本群的同态观点

把映射度看作诱导同态在 \(\pi_1\) 上的作用：\(\pi_1(S^1,1)\cong \mathbb{Z}\)，生成元记作 \(1\)。则连续映射 \(h: S^1\to S^1\) 给出  
\[
h_*: \mathbb{Z} \to \mathbb{Z}, \quad h_*(1) = \deg(h).
\]

**关键事实：** 在拓扑群 \(S^1\) 中，回路拼接与逐点乘积同伦。确切地说，若 \(\alpha, \beta\) 是以 \(1\) 为基点的回路，则回路 \(\alpha * \beta\)（先走 \(\alpha\) 再走 \(\beta\)）与逐点乘积回路 \(t\mapsto \alpha(t)\beta(t)\) 同伦。因此乘积映射  
\[
m: S^1\times S^1 \to S^1,\quad m(z,w)=zw
\]  
诱导的同态 \(m_*: \pi_1(S^1\times S^1) \cong \mathbb{Z}\oplus\mathbb{Z} \to \pi_1(S^1)\cong\mathbb{Z}\) 就是加法：  
\[
m_*(a,b) = a + b.
\]

**组合映射**  
\(fg\) 可分解为：
\[
S^1 \xrightarrow{\;\Delta\;} S^1 \times S^1 \xrightarrow{\;f\times g\;} S^1 \times S^1 \xrightarrow{\;m\;} S^1,
\]  
其中 \(\Delta(x)=(x,x)\) 是对角映射。逐项查看诱导同态：
- \(\Delta_*: \mathbb{Z} \to \mathbb{Z}\oplus\mathbb{Z}\)，\(\Delta_*(1) = (1,1)\)。
- \((f\times g)_*: \mathbb{Z}\oplus\mathbb{Z} \to \mathbb{Z}\oplus\mathbb{Z}\)，\((a,b) \mapsto (\deg(f)\,a,\; \deg(g)\,b)\)。
- \(m_*: (a,b) \mapsto a+b\)。

复合：
\[
(fg)_*(1) = m_*\big( (f\times g)_*(\Delta_*(1)) \big)
= m_*\big( \deg(f), \deg(g) \big)
= \deg(f) + \deg(g).
\]  
因此 \(\deg(fg) = \deg(f) + \deg(g)\)。

---

## 小结

- 从提升的角度看，乘积映射相当于把实数提升加起来，度数就是终点减起点，自然可加。
- 从基本群的角度看，乘积映射在群结构下对应加法同态，度数的加性就是基本群同态保持加法。

两种视角都指向同一个优雅的事实：  
\[
\boxed{\deg(fg) = \deg(f) + \deg(g)}.
\]  

你在笔记中做的习题恰好用到了这个性质：假定 \(f\) 零伦（度数为 0），取 \(g(z)=z^{-1}\)（度数为 -1），于是 \(fg\) 的度数就是 -1，再与可缩矛盾推出不动点。现在你知道了度数加性的来龙去脉，整个推理就严丝合缝了。
[Timestamp: 2026/06/13 19:49:25]