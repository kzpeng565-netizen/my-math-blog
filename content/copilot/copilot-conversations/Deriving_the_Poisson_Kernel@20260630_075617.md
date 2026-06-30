---
epoch: 1782777377354
modelKey: "deepseek-v4-pro|deepseek"
topic: "Deriving the Poisson Kernel"



tags:
  - copilot-conversation
---

**user**: K(x,y)=\frac{1-|x|^2}{\omega_n|x-y|^n}
怎么推出
P_R(x, y)=\frac{R^2-|x|^2}{\omega_n R|x-y|^n} .
[Context: Notes: 分析/微分方程/调和方程格林函数的推导.md]
[Timestamp: 2026/06/30 07:56:17]

**ai**: 
<think>我们被问到如何从单位球的泊松核 K(x,y) = (1-|x|^2) / (ω_n |x-y|^n) 推出半径为R的球的泊松核 P_R(x,y) = (R^2-|x|^2) / (ω_n R |x-y|^n)。我们需要解释缩放变换。用户提供了包含单位球泊松核推导的笔记。这个推导基于单位球 B_1。对于半径为 R 的球，我们可以通过缩放变换得到相应的泊松核。

推导方法：
- 单位球 B_1 的泊松公式：对于 u 在 B_1 内调和，边界为 g，有 u(x) = ∫_{∂B_1} K(x,y) g(y) dS_y, 其中 K(x,y) = (1-|x|^2) / (ω_n |x-y|^n).
- 对于半径为 R 的球 B_R，定义变量变换：令 x' = x/R, y' = y/R 将 B_R 映射到 B_1。设 v(x') = u(Rx') = u(x)。则 v 在 B_1 内调和，边界 v(x') = u(Rx') = g(Rx') 在 ∂B_1 上。
- 应用单位球的泊松公式于 v: v(x') = ∫_{∂B_1} (1-|x'|^2) / (ω_n |x'-y'|^n) v(y') dS(y')。
- 代回原变量：x' = x/R, y' = y/R, v(x') = u(x), v(y') = u(y) = g(y) (因为 y 在边界上，g 是边界值)。积分面元变换：dS(y') = dS(y) / R^{n-1} (因为 ∂B_1 是 ∂B_R 缩放 1/R)。
- 计算：|x'| = |x|/R, |x'-y'| = |x/R - y/R| = |x-y|/R。所以：
 (1-|x'|^2) = 1 - |x|^2/R^2 = (R^2 - |x|^2)/R^2.
 |x'-y'|^n = |x-y|^n / R^n.
- 核变为： K(x',y') = ((R^2-|x|^2)/R^2) / (ω_n (|x-y|^n / R^n)) = (R^2-|x|^2) / (ω_n |x-y|^n) * R^{n-2}.
- 积分变换：∫_{∂B_1} K(x',y') g(y) dS(y') = ∫_{∂B_R} [ (R^2-|x|^2) / (ω_n |x-y|^n) * R^{n-2} ] g(y) (dS(y)/R^{n-1}) = ∫_{∂B_R} (R^2-|x|^2) / (ω_n R |x-y|^n) g(y) dS(y).
- 这就给出了 P_R(x,y) = (R^2-|x|^2) / (ω_n R |x-y|^n)。注意：标准的泊松核有时在分母写为 ω_n R 有时 ω_n R |x-y|^n 中，R 是在分母。用户给出的 P_R 正是这个形式。所以回答应该解释通过缩放自变量实现从单位球到半径为 R 的球的变换，并展示积分核如何变化。

另外注意原公式中 K(x,y) 分母可能是 |x-y|^n，这与笔记中一致。

我将用中文回答，清晰展示缩放推导过程。</think>从单位球 $B_1$ 到一般半径 $R$ 的球 $B_R$，核心方法是**变量缩放**。下面逐步推导：

---

设 $u$ 在 $B_R$ 内调和，边界值为 $g$（已知）。为了利用单位球的泊松公式，我们把 $B_R$ 缩放成 $B_1$。

**1. 缩放变换**

令 
$$
x' = \frac{x}{R}, \quad y' = \frac{y}{R}
$$
则 $x \in B_R$ 对应 $x' \in B_1$，$y \in \partial B_R$ 对应 $y' \in \partial B_1$。

定义缩放后的函数：
$$
v(x') = u(Rx') = u(x)
$$
由于拉普拉斯方程在缩放下的不变性，$v$ 在 $B_1$ 内调和，边值为 $v(y') = g(Ry') = g(y)$。

**2. 对 $v$ 应用单位球的泊松公式**

单位球 $B_1$ 的泊松公式为：
$$
v(x') = \int_{\partial B_1} \frac{1 - |x'|^2}{\omega_n |x' - y'|^n} \, v(y') \, dS(y')
$$
将变量换回 $x, y$：

- $|x'| = \dfrac{|x|}{R}$，因此 $1 - |x'|^2 = 1 - \dfrac{|x|^2}{R^2} = \dfrac{R^2 - |x|^2}{R^2}$
- $|x' - y'| = \dfrac{|x - y|}{R}$，因此 $|x' - y'|^n = \dfrac{|x - y|^n}{R^n}$
- 球面积元缩放：$dS(y') = \dfrac{dS(y)}{R^{\,n-1}}$（因为 $\partial B_R$ 的面积元是 $\partial B_1$ 的 $R^{\,n-1}$ 倍）

**3. 代入并化简**

$$
\begin{aligned}
u(x) = v(x') 
&= \int_{\partial B_R} \frac{ \dfrac{R^2 - |x|^2}{R^2} }{ \omega_n \, \dfrac{|x - y|^n}{R^n} } \, g(y) \, \frac{dS(y)}{R^{\,n-1}} \\
&= \int_{\partial B_R} \frac{R^2 - |x|^2}{\omega_n |x-y|^n} \cdot \frac{R^{n-2}}{R^{\,n-1}} \, g(y) \, dS(y) \\
&= \int_{\partial B_R} \frac{R^2 - |x|^2}{\omega_n R \, |x-y|^n} \, g(y) \, dS(y)
\end{aligned}
$$

---

**结论：** 半径为 $R$ 的球的泊松核正是

$$
P_R(x, y) = \frac{R^2 - |x|^2}{\omega_n R \, |x - y|^n}
$$

它由单位球的核 $K(x,y) = \dfrac{1 - |x|^2}{\omega_n |x - y|^n}$ 经缩放变换自然得出。分母中多出的 $R$ 本质上来自面积元与距离幂次的缩放差异（一个 $R^{\,n-1}$，一个 $R^n$，以及分子的 $R^2$ 消去后净剩一个 $R$ 在分母）。
[Timestamp: 2026/06/30 07:56:50]