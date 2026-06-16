---
epoch: 1781573628357
modelKey: "deepseek-v4-pro|deepseek"
topic: "Barrier method for maximum principle"



tags:
  - copilot-conversation
---

**user**: 可以把老师的证明记成一句话：

**局部切一块区域，给 (u) 加一个很小的障碍函数，然后对新函数用弱最大值原理。**

定理形式：

设 (u\in C^2(B_1)\cap C^1(\overline{B_1}))，满足 (\Delta u\ge 0)。若 (x_0\in \partial B_1)，且

[
u(x_0)=\max_{\overline{B_1}}u,
]

并且 (u) 非常数，则

[
\frac{\partial u}{\partial n}(x_0)>0.
]

这里 (n) 是外法向。对单位球，(n=x_0)。

证明思路：

在 (x_0) 附近取一个小球 (B_\rho(x_0))，令

[
\Omega=B_1\cap B_\rho(x_0).
]

它的边界分成两部分：

[
\partial\Omega=\Gamma_1\cup \Gamma_2.
]

其中 (\Gamma_1) 是原来 (B_1) 的边界部分，(\Gamma_2) 是新切出来的小球边界部分。

构造辅助函数

[
w(x)=e^{-a|x|^2}-e^{-a}.
]

它的作用是：

[
w=0 \quad \text{on } \partial B_1,
]

并且在靠近 (x_0) 的球内有

[
w>0,\qquad \Delta w\ge 0.
]

令

[
\widetilde u=u+\varepsilon w.
]

因为

[
\Delta \widetilde u=\Delta u+\varepsilon\Delta w\ge 0,
]

所以 (\widetilde u) 仍然满足可以使用弱最大值原理的条件。

现在看边界：

在 (\Gamma_1) 上，(w=0)，所以

[
\widetilde u=u\le u(x_0).
]

在 (\Gamma_2) 上，由于 (\Gamma_2) 离开了最大值点 (x_0)，并且 (u) 在内部严格小于 (u(x_0))，所以取 (\varepsilon) 足够小，可使

[
\widetilde u=u+\varepsilon w\le u(x_0).
]

因此在整个 (\partial\Omega) 上都有

[
\widetilde u\le u(x_0).
]

由弱最大值原理，

[
\widetilde u\le u(x_0)\quad \text{in }\Omega.
]

也就是

[
u(x)+\varepsilon w(x)\le u(x_0).
]

取 (x=x_0-tn)，即从边界沿内法向进入球内，得到

[
u(x_0)-u(x_0-tn)\ge \varepsilon w(x_0-tn).
]

两边除以 (t)，令 (t\to0^+)，右边因为 (w) 沿内法向严格增加，所以极限是正数。因此

[
\frac{\partial u}{\partial n}(x_0)>0.
]

核心逻辑就是：

[
u \le u(x_0)
]

本来只是普通最大值，但我们人为加上一个正的 (w)，得到

[
u+\varepsilon w\le u(x_0).
]

于是

[
u(x_0)-u(x)\ge \varepsilon w(x),
]

这就强迫 (u) 从内部走向边界时至少有一阶的严格增长，所以外法向导数严格为正。


帮我修改这个, 用$ , $$包裹公式, 然后压缩内容变成笔记式的简洁
[Context: Notes: 分析/微分方程/Untitled.md]
[Timestamp: 2026/06/16 09:33:48]

**ai**: 
<think>我们被要求修改一个用户提供的文本。文本是一段对Hopf Lemma的证明进行口头解释的笔记。要求：用$和$$包裹公式，压缩内容变成笔记式的简洁。

我们需要保留核心思想，但用更简洁的方式表达，使用LaTeX公式用$或$$包裹。要把原来的长篇大论变成简洁的笔记风格。

需要输出修改后的内容。保持原意，但精简。

原用户文本：

```
可以把老师的证明记成一句话：

**局部切一块区域，给 (u) 加一个很小的障碍函数，然后对新函数用弱最大值原理。**

定理形式：

设 (u∈C^2(B_1)∩C^1(‾B_1))，满足 (Δu≥0)。若 (x_0∈∂B_1)，且

[
u(x_0)=max_{‾B_1}u,
]

并且 (u) 非常数，则

[
∂u/∂n(x_0)>0.
]

这里 (n) 是外法向。对单位球，(n=x_0)。

证明思路：

在 (x_0) 附近取一个小球 (B_ρ(x_0))，令

[
Ω=B_1∩B_ρ(x_0).
]

它的边界分成两部分：

[
∂Ω=Γ_1∪Γ_2.
]

其中 (Γ_1) 是原来 (B_1) 的边界部分，(Γ_2) 是新切出来的小球边界部分。

构造辅助函数

[
w(x)=e^{-a|x|^2}-e^{-a}.
]

它的作用是：

[
w=0   on ∂B_1,
]

并且在靠近 (x_0) 的球内有

[
w>0, Δw≥0.
]

令

[
‾u=u+ε w.
]

因为

[
Δ‾u=Δu+εΔw≥0,
]

所以 (‾u) 仍然满足可以使用弱最大值原理的条件。

现在看边界：

在 (Γ_1) 上，(w=0)，所以

[
‾u=u≤u(x_0).
]

在 (Γ_2) 上，由于 (Γ_2) 离开了最大值点 (x_0)，并且 (u) 在内部严格小于 (u(x_0))，所以取 (ε) 足够小，可使

[
‾u=u+ε w≤u(x_0).
]

因此在整个 (∂Ω) 上都有

[
‾u≤u(x_0).
]

由弱最大值原理，

[
‾u≤u(x_0) in Ω.
]

也就是

[
u(x)+ε w(x)≤u(x_0).
]

取 (x=x_0-t n)，即从边界沿内法向进入球内，得到

[
u(x_0)-u(x_0-t n)≥ε w(x_0-t n).
]

两边除以 (t)，令 (t→0+)，右边因为 (w) 沿内法向严格增加，所以极限是正数。因此

[
∂u/∂n(x_0)>0.
]

核心逻辑就是：

[
u ≤ u(x_0)
]

本来只是普通最大值，但我们人为加上一个正的 (w)，得到

[
u+ε w ≤ u(x_0).
]

于是

[
u(x_0)-u(x) ≥ ε w(x),
]

这就强迫 (u) 从内部走向边界时至少有一阶的严格增长，所以外法向导数严格为正。
```

要压缩内容，变成简洁笔记，用$和$$包裹公式。笔记式的简洁。

修改目标：像是上课记的要点笔记，保留原有逻辑，但每个部分用简洁符号和公式表达，可能省略一些文字。输出中要包含定理和证明思路，但压缩。

考虑到用户说“帮我修改这个, 用$ , $$包裹公式, 然后压缩内容变成笔记式的简洁”，我们应该直接给出修改后的笔记，用markdown格式，注意公式包裹：行内用$，独立用$$。

注意原文本有些( )括起来的公式，需要改成$...$，如(u) → $u$。原来用[ ... ]的环境改成$$...$$。

同时压缩内容：把叙述变成要点式，例如“核心逻辑”可以精简为：

核心：由$u\le u(x_0)$，外加正值辅助函数$w$，得$u+\varepsilon w\le u(x_0)$，从而$u(x_0)-u(x)\ge \varepsilon w(x)$，强迫内法向差商正极限，推出外法向导数$>0$。

保留“一句话”和定理形式、证明思路。合并边界讨论。最后核心逻辑可以保留。

注意原来用的符号：$\widetilde u$ 似乎写成‾u，最好改成 $\widetilde{u}$。

输出不要包含“帮你修改”之类的客套话，直接输出修改后的笔记内容。根据要求，只输出修改后的内容即可。

让我规划一下结构：

# Hopf Lemma 极简版（笔记）

**一句概括**：局部切一块区域，给 $u$ 加一个很小的障碍函数，然后对新函数用弱最大值原理。

**定理**：设 $u\in C^2(B_1)\cap C^1(\overline{B_1})$，$\Delta u\ge 0$。若 $x_0\in\partial B_1$ 使 $u(x_0)=\max_{\overline{B_1}}u$ 且 $u$ 非常数，则 $\frac{\partial u}{\partial n}(x_0)>0$。（对单位球 $n=x_0$）

**证明思路**：（分步）

1. **切区域**：取小球 $B_\rho(x_0)$，令 $\Omega=B_1\cap B_\rho(x_0)$，边界 $\partial\Omega=\Gamma_1\cup\Gamma_2$（$\Gamma_1$ 在 $\partial B_1$，$\Gamma_2$ 在球内）。

2. **障碍函数**：$w(x)=e^{-a|x|^2}-e^{-a}$，满足 $w=0$ on $\partial B_1$，且在球内 $w>0,\Delta w\ge0$。

3. **辅助函数**：$\widetilde{u}=u+\varepsilon w$，则 $\Delta\widetilde{u}\ge0$，可用弱最大值原理。

4. **边界估计**：在 $\Gamma_1$ 上 $\widetilde{u}=u\le u(x_0)$；在 $\Gamma_2$ 上，因 $u$ 在内严格小于最大值，取 $\varepsilon$ 足够小可得 $\widetilde{u}\le u(x_0)$。所以整体 $\widetilde{u}\le u(x_0)$ 在 $\Omega$ 上成立。

5. **导出严格梯度**：取 $x=x_0-tn$，得 $u(x_0)-u(x_0-tn)\ge\varepsilon w(x_0-tn)$。除以 $t\to0^+$，右端极限为正（因 $w$ 沿内法向递增），得 $\frac{\partial u}{\partial n}(x_0)>0$。

**核心逻辑**：$u\le u(x_0)$ 加正项 $w$ 得 $u+\varepsilon w\le u(x_0)$，即 $u(x_0)-u\ge\varepsilon w(x)$，导致在边界处必有严格内法向增长，从而法向导数为正。

这样就很简洁了。再压缩一点也可，但我认为这样已经够笔记式。

注意原始请求是“帮我把这个修改，用$,$$包裹公式，然后压缩内容变成笔记式的简洁”，所以我会输出上述文本，不附加其他说明。</think># Hopf Lemma 极简版（笔记）

**一句话**：局部切一块区域，给 $u$ 加一个很小的障碍函数，然后对新函数用弱最大值原理。

**定理**：  
设 $u\in C^{2}(B_{1})\cap C^{1}(\overline{B_{1}})$，$\Delta u\ge 0$。若 $x_{0}\in\partial B_{1}$ 满足  
$$u(x_{0})=\max_{\overline{B_{1}}}u,$$  
且 $u$ 非常数，则  
$$\frac{\partial u}{\partial n}(x_{0})>0.$$  
对单位球 $n=x_{0}$。

**证明思路**  
1. **切区域**：取小球 $B_{\rho}(x_{0})$，令 $\Omega=B_{1}\cap B_{\rho}(x_{0})$，边界  
   $$\partial\Omega=\Gamma_{1}\cup\Gamma_{2},$$  
   $\Gamma_{1}$ 在 $\partial B_{1}$ 上，$\Gamma_{2}$ 在球内。

2. **障碍函数**：  
   $$w(x)=e^{-a|x|^{2}}-e^{-a}.$$  
   性质：$w=0$ on $\partial B_{1}$，在球内 $w>0$，$\Delta w\ge0$。

3. **辅助函数**：  
   $$\widetilde{u}=u+\varepsilon w\quad\Rightarrow\quad\Delta\widetilde{u}\ge0,$$  
   可对其用弱最大值原理。

4. **边界控制**：  
   - 在 $\Gamma_{1}$ 上：$w=0\;\Rightarrow\;\widetilde{u}=u\le u(x_{0})$。  
   - 在 $\Gamma_{2}$ 上：内部严格小于最大值，取 $\varepsilon$ 充分小有 $\widetilde{u}=u+\varepsilon w\le u(x_{0})$。  
   故在整个 $\partial\Omega$ 上 $\widetilde{u}\le u(x_{0})$，由弱最大值原理  
   $$\widetilde{u}\le u(x_{0})\quad\text{in }\Omega.$$

5. **导出严格导数**：  
   取 $x=x_{0}-tn$（内法向），则  
   $$u(x_{0})-u(x_{0}-tn)\ge\varepsilon w(x_{0}-tn).$$  
   除以 $t>0$ 并令 $t\to0^{+}$，右端极限为正（$w$ 沿内法向严格增长），于是  
   $$\frac{\partial u}{\partial n}(x_{0})>0.$$

**核心逻辑**  
由 $u\le u(x_{0})$ 外加正函数 $w$ 得 $u+\varepsilon w\le u(x_{0})$，即  
$$u(x_{0})-u\ge\varepsilon w(x),$$  
从而迫使 $u$ 从内部靠近边界时有一阶严格增长，故外法向导数必 $>0$。
[Timestamp: 2026/06/16 09:34:17]