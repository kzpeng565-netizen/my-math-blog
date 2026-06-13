---
epoch: 1781331918026
modelKey: "deepseek-v4-pro|deepseek"
topic: "Homotopy class implication"



tags:
  - copilot-conversation
---

**user**: $$
\begin{aligned}
& {\left[i_A\circ \alpha\right]=\left[i_A\circ \beta\right] } \\
& {\left[r_0\circ \alpha\right]=\left[r_0\circ i_A\circ \beta\right] } \\
& \Rightarrow {\left[i_A\circ \alpha\right]=\left[i_A\circ \beta\right] } \\
& \Rightarrow \quad[\alpha]=[\beta]
\end{aligned}
$$
所以$i_{A*}$是单同态
[Context: Notes: 拓扑/9. 基本群&复叠空间.md]
[Timestamp: 2026/06/13 14:25:18]

**ai**: 
<think>我们被问到的问题是关于一段数学证明，具体是习题1-1的证明，其中证明含入映射诱导基本群单同态。用户给出的证明步骤可能有些混乱或笔误，需要理清并给出正确的证明。

用户提供的文本：

$$
\begin{aligned}
& {\left[i_A\circ \alpha\right]=\left[i_A\circ \beta\right] } \\
& {\left[r_0\circ \alpha\right]=\left[r_0\circ i_A\circ \beta\right] } \\
& \Rightarrow {\left[i_A\circ \alpha\right]=\left[i_A\circ \beta\right] } \\
& \Rightarrow \quad[\alpha]=[\beta]
\end{aligned}
$$
所以$i_{A*}$是单同态

但这里似乎有笔误：第一步和第三步相同，应该是应用了收缩映射r。实际上完整的正确证明应为：假设 $i_{A*}([\alpha]) = i_{A*}([\beta])$，即 $[i_A\circ\alpha] = [i_A\circ\beta]$。由于 $r: X \to A$ 是收缩映射，$r\circ i_A = id_A$。于是 $r_*$ 作用得到 $[r\circ i_A\circ\alpha] = [r\circ i_A\circ\beta]$，即 $[\alpha]=[\beta]$。所以单射。

在用户给出的推导中，第二步写的是 $[r_0\circ \alpha]=[r_0\circ i_A\circ\beta]$，但应该两边都是 $r\circ i_A$ 才对，可能笔误。并且第三步直接又写了假设，不太对。我们需要指出正确证明，并说明用户推导中的错误。或者用户只是贴了笔记中已有的证明，想让我们评价？用户的问题仅仅是给出了这个片段，没有明确提问。根据对话，用户可能是想让我们解释或修正这个证明。因为这是从 active note 中截取的部分，可能他希望我们澄清这个证明的逻辑。

回应：解释证明的正确思路，指出推导中的小问题，并给出清晰版本。结合上下文，用户的问题是隐式的。我要以助手身份回答。注意使用中文。</think>你的推导思路是正确的，但在书写上有些地方不够严谨，我来帮你整理出一个清晰的证明。

**目标**：证明含入映射 $i_A: A \hookrightarrow X$ 诱导的同态
$$
i_{A*}: \pi_1(A,a) \longrightarrow \pi_1(X,a),\quad [\alpha]\mapsto [i_A\circ\alpha]
$$
是单同态。

**已知条件**：$A$ 是 $X$ 的收缩核，即存在收缩映射 $r: X \to A$ 满足 $r\circ i_A = \mathrm{id}_A$。

**正确证明**：

假设 $i_{A*}([\alpha]) = i_{A*}([\beta])$，即
$$
[i_A\circ\alpha] = [i_A\circ\beta] \quad \text{在 }\pi_1(X,a)\text{ 中}.
$$

将收缩映射 $r$ 诱导的同态 $r_*: \pi_1(X,a) \to \pi_1(A,a)$ 作用到等式两边：
$$
r_*\big([i_A\circ\alpha]\big) = r_*\big([i_A\circ\beta]\big)
\;\Longrightarrow\;
[r\circ i_A\circ\alpha] = [r\circ i_A\circ\beta].
$$

因为 $r\circ i_A = \mathrm{id}_A$，所以上式化为
$$
[\alpha] = [\beta] \quad \text{在 }\pi_1(A,a)\text{ 中}.
$$

这就证明了 $i_{A*}$ 是单同态。

---

**关于你写的推导中的问题**：

你写了：

- 第一步：$[i_A\circ\alpha] = [i_A\circ\beta]$   ← 这是我们要证明单射时的假设，没问题。
- 第二步：$[r_0\circ\alpha] = [r_0\circ i_A\circ\beta]$  
  这里出现了 $r_0$，且左边 $r_0\circ\alpha$ 缺少了 $i_A$。应该是 $[r\circ i_A\circ\alpha] = [r\circ i_A\circ\beta]$ 才由第一步经 $r_*$ 得到。如果直接写 $[r\circ\alpha]$，$\alpha$ 是 $A$ 中道路，$r$ 定义域是 $X$，必须把 $\alpha$ 先嵌入 $X$（即 $i_A\circ\alpha$）才能复合。
- 第三步又重复了第一步，显得多余。

修正后就得到上面的标准证明。把记号统一、步骤连贯，这就是一个完整的证明。
[Timestamp: 2026/06/13 14:25:30]

**user**: 能不能直接写r复合上i是id, 所以i一定是单同态
[Context: Notes: 拓扑/9. 基本群&复叠空间.md]
[Timestamp: 2026/06/13 14:26:18]

**ai**: 
<think>我们被问到：“能不能直接写r复合上i是id, 所以i一定是单同态？” 用户是想知道是否可以直接由 r ∘ i = id 推出 i 是单同态，而不需要上面那种详细的证明。在代数中，如果两个映射 f: X→Y 和 g: Y→X 满足 g∘f = id_X，那么 f 一定是单射，g 是满射。对于群同态，这直接蕴含 f 是单同态。因此，可以简洁地说明：由 r ∘ i_A = id_A，两边应用基本群函子，得到 r_* ∘ i_{A*} = (id_A)_* = id_{π1(A,a)}，所以 i_{A*} 有左逆，从而 i_{A*} 是单同态。这就是一个直接而简短的证明。所以回答：是的，可以直接这样写，然后解释一下为什么有左逆就是单射。同时要说明，因为 r 和 i 都是连续映射，且基点在 a，所以诱导同态满足函子性。</think>完全可以，而且这样写更简洁。

由收缩映射的定义知 $r \circ i_A = \mathrm{id}_A$，两边同时应用基本群函子 $\pi_1(-,a)$，并利用函子性 $(\mathrm{id}_A)_* = \mathrm{id}_{\pi_1(A,a)}$ 以及 $(r\circ i_A)_* = r_* \circ i_{A*}$，立即得到
$$
r_* \circ i_{A*} = \mathrm{id}_{\pi_1(A,a)} .
$$
因此 $i_{A*}$ 有左逆（即 $r_*$），所以 $i_{A*}$ 必为单同态。这个论证一步到位，完全不需要像之前那样从两个道路类相等开始推导。
[Timestamp: 2026/06/13 14:26:25]