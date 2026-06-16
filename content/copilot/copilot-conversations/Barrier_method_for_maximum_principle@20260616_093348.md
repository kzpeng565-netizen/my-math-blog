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

**user**: 你老师提醒的是对的：我前面的证明**思路对，但少说了一个关键严谨点**：要保证我们取到的“低值区域里的内切球”没有先碰到 (\partial\Omega)。否则这个球不一定完全在 (\Omega) 里，就不能直接对它用 Hopf 引理。

严谨做法如下。

设

[
M=\max_{\Omega}u,\qquad F={x\in\Omega:u(x)=M}.
]

要证明强极值原理，就是证明 (F=\Omega)。

(F) 显然是闭集。关键是证明 (F) 也是开集。

取 (p\in F)。因为 (p\in\Omega)，所以可以取 (\rho>0)，使得

[
B_{2\rho}(p)\subset \Omega.
]

现在反设 (p) 附近有低值点，即存在

[
a\in B_\rho(p),\qquad u(a)<M.
]

令

[
r=\operatorname{dist}(a,F).
]

因为 (p\in F)，所以

[
r\le |a-p|<\rho.
]

于是

[
B_r(a)\subset B_{2\rho}(p)\subset \Omega.
]

这一步就是老师说的“避免球还没碰到最高值集 (F)，就先碰到区域边界”。我们把 (a) 选得足够靠近 (p)，所以球一定在 (\Omega) 内部扩张。

由 (r=\operatorname{dist}(a,F))，存在 (y\in F)，使得

[
y\in \partial B_r(a).
]

并且在 (B_r(a)) 内部没有点属于 (F)，所以

[
u<M \quad \text{in } B_r(a),
]

而

[
u(y)=M.
]

于是 (u) 在球 (B_r(a)) 的边界点 (y) 处取最大值。由 Hopf 引理，

[
\frac{\partial u}{\partial n}(y)>0.
]

但 (y\in F\subset\Omega)，它是原区域内部点，并且 (u) 在 (y) 处达到最大值，所以

[
\nabla u(y)=0.
]

因此所有方向导数都是 (0)，特别是

[
\frac{\partial u}{\partial n}(y)=0.
]

矛盾。

所以 (p) 附近不可能有低值点，即 (F) 是开集。又 (F) 是闭集，(\Omega) 连通，因此

[
F=\Omega.
]

也就是

[
u\equiv M.
]

所以更准确地说：前面的证明不是本质错误，而是省略了“球要完全留在 (\Omega) 内”的论证。老师强调的就是这个严谨点。


继续处理这个文本, 尽量使用行内公式 删除标题和空行
[Context: Notes: 分析/微分方程/Untitled.md]
[Timestamp: 2026/06/16 09:51:13]

**ai**: 
<think>我们被要求继续处理一个文本，用行内公式，删除标题和空行。用户提供了又一个关于证明的严谨点的论述。需要压缩、精简，变成笔记式的简洁，使用$行内公式，去掉标题和空行，可能还要合并内容。注意之前用户已经发过一个笔记，现在补充一个严谨点。但现在仅就这个新文本进行处理。要求是“继续处理这个文本, 尽量使用行内公式 删除标题和空行”。所以我们要对这个文本做修改，输出压缩后的笔记，用行内公式，删除标题和空行。我们可以将解释性的内容精简为要点，保留核心推理。采用$...$而不是$$。注意，用户提供了具体内容，我们要给出修改后的简洁笔记。不要添加额外说明。直接回答修改后的笔记。

原文：

```
你老师提醒的是对的：我前面的证明**思路对，但少说了一个关键严谨点**：要保证我们取到的“低值区域里的内切球”没有先碰到 (\partial\Omega)。否则这个球不一定完全在 (\Omega) 里，就不能直接对它用 Hopf 引理。

严谨做法如下。

设

[
M=\max_{\Omega}u,\qquad F={x\in\Omega:u(x)=M}.
]

要证明强极值原理，就是证明 (F=\Omega)。

(F) 显然是闭集。关键是证明 (F) 也是开集。

取 (p\in F)。因为 (p\in\Omega)，所以可以取 (\rho>0)，使得

[
B_{2\rho}(p)\subset \Omega.
]

现在反设 (p) 附近有低值点，即存在

[
a\in B_\rho(p),\qquad u(a)<M.
]

令

[
r=\operatorname{dist}(a,F).
]

因为 (p\in F)，所以

[
r\le |a-p|<\rho.
]

于是

[
B_r(a)\subset B_{2\rho}(p)\subset \Omega.
]

这一步就是老师说的“避免球还没碰到最高值集 (F)，就先碰到区域边界”。我们把 (a) 选得足够靠近 (p)，所以球一定在 (\Omega) 内部扩张。

由 (r=\operatorname{dist}(a,F))，存在 (y\in F)，使得

[
y\in \partial B_r(a).
]

并且在 (B_r(a)) 内部没有点属于 (F)，所以

[
u<M \quad \text{in } B_r(a),
]

而

[
u(y)=M.
]

于是 (u) 在球 (B_r(a)) 的边界点 (y) 处取最大值。由 Hopf 引理，

[
\frac{\partial u}{\partial n}(y)>0.
]

但 (y\in F\subset\Omega)，它是原区域内部点，并且 (u) 在 (y) 处达到最大值，所以

[
\nabla u(y)=0.
]

因此所有方向导数都是 (0)，特别是

[
\frac{\partial u}{\partial n}(y)=0.
]

矛盾。

所以 (p) 附近不可能有低值点，即 (F) 是开集。又 (F) 是闭集，(\Omega) 连通，因此

[
F=\Omega.
]

也就是

[
u\equiv M.
]

所以更准确地说：前面的证明不是本质错误，而是省略了“球要完全留在 (\Omega) 内”的论证。老师强调的就是这个严谨点。
```

目标：精简，用行内公式，删除标题和空行。可能保留关键步骤。可以用短句。将原来的叙述压缩。

我们可这样处理：

- 第一句话“你老师提醒的是对的：...”可以改成“补充严谨点：要保证内切球完全在$\Omega$内，才能用Hopf引理。”
- 然后定义$M=\max_\Omega u$，$F=\{x\in\Omega: u(x)=M\}$。要证$F=\Omega$。
- $F$闭。证$F$开：任取$p\in F$，选$\rho>0$使$B_{2\rho}(p)\subset\Omega$。反设存在$a\in B_\rho(p)$使$u(a)<M$。
- 令$r=\operatorname{dist}(a,F)$，则$r\le |a-p|<\rho$，故$B_r(a)\subset B_{2\rho}(p)\subset\Omega$。
- 由距离定义，存在$y\in\partial B_r(a)\cap F$，且内部无$F$点，即$u<M$ inside $B_r(a)$，$u(y)=M$。
- 由Hopf引理，$\frac{\partial u}{\partial n}(y)>0$（外法向即径向向外）。
- 但$y\in\Omega$是内点且取最大值，故$\nabla u(y)=0$，矛盾。所以$p$附近无低值点，$F$开。
- 由连通性，$F=\Omega$，即$u\equiv M$。

- 最后“所以更准确地说...”可以省略或简化成“关键：保证球全在区域内。”

使用行内公式，用$...$，如$M=\max_\Omega u$。删除标题和空行：输出连续文本，但保留逻辑分段，可换行但不要空行，可以段落。但用户说“删除标题和空行”，可能想要一个紧凑段落。我会输出类似：

补充严谨点：要保证内切球完全在 $\Omega$ 内，才能用 Hopf 引理。设 $M=\max_\Omega u$，$F=\{x\in\Omega:u(x)=M\}$，证 $F=\Omega$。$F$ 闭，证 $F$ 开：取 $p\in F$，选 $\rho>0$ 使 $B_{2\rho}(p)\subset\Omega$。若存在 $a\in B_\rho(p)$ 满足 $u(a)<M$，令 $r=\operatorname{dist}(a,F)$，则 $r\le|a-p|<\rho$，故 $B_r(a)\subset\Omega$。由距离定义，存在 $y\in\partial B_r(a)\cap F$，且 $B_r(a)$ 内 $u<M$，$u(y)=M$。Hopf 引理给出 $\frac{\partial u}{\partial n}(y)>0$，但 $y$ 是内点极大，应有 $\nabla u(y)=0$，矛盾。故 $F$ 开，连通区域上 $F=\Omega$，$u\equiv M$。核心：控制球不触边界。

这就是压缩了。保持逻辑，无空行。用行内公式。输出即可。</think>补充严谨点：要保证内切球完全在 $\Omega$ 内才能用 Hopf 引理。设 $M=\max_\Omega u$，$F=\{x\in\Omega:u(x)=M\}$，需证 $F=\Omega$。$F$ 闭，证 $F$ 开：取 $p\in F$，选 $\rho>0$ 使 $B_{2\rho}(p)\subset\Omega$。若存在 $a\in B_\rho(p)$ 使 $u(a)<M$，令 $r=\operatorname{dist}(a,F)$，则 $r\le|a-p|<\rho$，故 $B_r(a)\subset\Omega$。由距离定义存在 $y\in\partial B_r(a)\cap F$，且 $B_r(a)$ 内 $u<M$，$u(y)=M$。由 Hopf 引理得 $\frac{\partial u}{\partial n}(y)>0$，但 $y\in\Omega$ 为极大值内点，$\nabla u(y)=0$，矛盾。故 $p$ 附近无低值点，$F$ 开。$\Omega$ 连通 $\Rightarrow F=\Omega$，$u\equiv M$。关键：球不触边界。
[Timestamp: 2026/06/16 09:51:35]

**user**: 不要这么简洁, 我的意思是整理成笔记
[Context: Notes: 分析/微分方程/Untitled.md]
[Timestamp: 2026/06/16 09:51:49]

**ai**: 
<think>我们再次收到用户的要求：“不要这么简洁, 我的意思是整理成笔记”。之前用户提供了一个文本，要求我们“继续处理这个文本, 尽量使用行内公式 删除标题和空行”，我们给出了一个极简的版本。现在用户说“不要这么简洁, 我的意思是整理成笔记”。所以我们需要重新处理那个文本（关于严谨点的证明），整理成笔记，但不要过于简洁，保留必要的解释，但仍然是笔记形式，使用行内公式，删除标题和空行？可能我们还是需要把文本变成简洁但完整的笔记，而不是极简版。用户说“不要这么简洁，我的意思是整理成笔记”，意味着我们之前的回答太简略了，缺少解释。也许笔记应该包含原来的结构，但用更清晰的公式和语言，删除多余的内容如“你老师提醒的是对的”等。我们要给出一个整理好的笔记。

回顾原始文本（从对话记录）：

用户提供了第二个文本，要求“继续处理这个文本, 尽量使用行内公式 删除标题和空行”，我们给出了一个极简的版本。现在用户说不要这么简洁，要整理成笔记。所以我们重新处理那个文本，给出一个笔记版本，不过于压缩，但删除空行和标题可能还是需要的。但是“整理成笔记”意味着可以有一些分段，用项目符号或清晰的结构，但不要空行？笔记通常会有分段和项目符号，可能需要一些换行。用户可以接受分段但不要空行？之前说“删除标题和空行”，现在又说“整理成笔记”，可能还是希望紧凑但内容充分。我可以写成一个结构清晰的笔记，使用行内公式，适当分段，但不留空行，或者只保留必要的换行。可以这样：

- 先指出严谨点。
- 然后描述证明步骤。
- 最后总结。

使用行内公式。输出一个整理好的笔记版本。

注意：原始文本中有一部分是解释“老师提醒...”等，这些可以去掉，只保留证明内容。将证明过程写成笔记。可以保留一些注释。

生成内容。</think>**补充严密性：球必须完全留在区域内才能用 Hopf 引理**  
设 $M=\max_{\Omega}u$，$F=\{x\in\Omega:u(x)=M\}$，目标是证 $F=\Omega$。  

- $F$ 是闭集（由连续性）。  
- 证 $F$ 也是开集：  
  取 $p\in F\subseteq\Omega$，可选 $\rho>0$ 使 $B_{2\rho}(p)\subset\Omega$。  
  反设 $p$ 附近有低值点，即存在 $a\in B_{\rho}(p)$ 满足 $u(a)<M$。  
  令 $r=\operatorname{dist}(a,F)$，则 $r\le|a-p|<\rho$，因此 $B_{r}(a)\subset B_{2\rho}(p)\subset\Omega$。  
  这一步保证了球完全在 $\Omega$ 内部，不碰到 $\partial\Omega$。  

- 由 $r$ 的定义，存在 $y\in\partial B_{r}(a)\cap F$，且在 $B_{r}(a)$ 内部没有 $F$ 的点，所以  
  $u<M$ 在 $B_{r}(a)$ 内，而 $u(y)=M$。  
  此时可对 $u$ 在球 $B_{r}(a)$ 上应用 Hopf 引理（$y$ 为边界最大值点），得  
  $\frac{\partial u}{\partial n}(y)>0$（$n$ 为 $B_{r}(a)$ 在 $y$ 处的外法向）。  

- 另一方面，$y\in F\subset\Omega$ 是区域内的内部点，且 $u$ 在 $y$ 取全局最大值，故梯度为零，$\nabla u(y)=0$，特别有 $\frac{\partial u}{\partial n}(y)=0$。  
  矛盾。  

因此 $p$ 附近不可能有低值点，$p$ 是 $F$ 的内点，$F$ 为开集。  
结合 $F$ 闭、$\Omega$ 连通，得 $F=\Omega$，即 $u\equiv M$。  

**核心**：通过选择足够靠近 $\Omega$ 内部的辅助球，确保球不先碰边界，才能用 Hopf 引理制造矛盾。
[Timestamp: 2026/06/16 09:52:05]