# 1. Lebesgue-Radon-Nikodym 定理

> [!Note] 定理 4.24（Lebesgue-Radon-Nikodym 定理：带号测度情形）
> 设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的 $\sigma$-有限带号测度，$\mu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$-有限正测度，则存在 $(X, \mathcal{M})$ 上的唯一 $\sigma$-有限带号测度 $\lambda$ 和 $\rho$，使得
> $$
> \lambda \perp \mu,\quad \rho \ll \mu,\quad \text{且 } \nu=\lambda+\rho .
> $$
> 此外，存在一个广义 $\mu$-可积函数 $f: X \rightarrow \mathbb{R}$，使得 $d\rho=f\,d\mu$，且任何两个这样的函数是 $\mu$-a.e. 相等的。

## 1.1 命题的结论

**1. Lebesgue 分解：测度的“物以类聚”**

定理第一步给出分解 $\nu = \lambda + \rho$，对 $\nu$ 分类：

- **$\rho \ll \mu$（绝对连续测度）**：$\mu(E)=0 \implies \rho(E)=0$，$\rho$ 只在 $\mu$ 有正测度的地方非零。
- **$\lambda \perp \mu$（互相奇异测度）**：存在划分 $X=A\cup B$，$\mu(B)=0$，$\lambda(A)=0$，两者各自集中在不相交的集合上，互不“往来”。

**2. Radon-Nikodym 导数：绝对连续的本质**

第二步断言 $d\rho = f\,d\mu$，即绝对连续测度本质上是带密度函数的积分。

- $f$ 是 **Radon-Nikodym 导数**，记作 $f = \frac{d\rho}{d\mu}$。
- 它把导数推广到测度：在微积分中 $F(x)=\int_a^x f(t)\,dt$ 的导数是 $f$；这里 $\rho$ 相对 $\mu$ 的局部变化率就是 $f$。

## 1.2 证明的思路

**核心想法**：从 $\nu$ 中尽可能“榨取”出对 $\mu$ 绝对连续的部分 $\int f\,d\mu$，榨干后的残余必然是完全奇异的 $\lambda$。

## 1.3 证明过程

**核心想法**：先在有限测度情形下，从 $\nu$ 中找出一个最大的绝对连续部分 $f\,d\mu$，再证明剩下的部分只能与 $\mu$ 奇异。

1. **构造候选密度族**：定义
   $$
   \mathcal{F}
   = \left\{f: X \to [0, \infty] \mid f \text{ 可测},\ \int_E f\,d\mu \le \nu(E),\ \forall E \in \mathcal{M}\right\}.
   $$
   $\mathcal{F}$ 收集了所有积分不超过 $\nu$ 的密度。关键性质是 $\mathcal{F}$ 对取最大值封闭：若 $f,g\in\mathcal{F}$，则 $\max(f,g)\in\mathcal{F}$。这允许我们把不同区域上的较优密度拼接起来。

2. **取上确界并逼近最大密度**：在标准证明中，先假设测度有限。令
   $$
   a = \sup_{f \in \mathcal{F}} \int_X f\,d\mu.
   $$
   由 $\nu$ 有限知 $a\le \nu(X)<\infty$。取 $\{f_n\}\subset\mathcal{F}$ 使 $\int_X f_n\,d\mu\to a$，再令 $g_n=\max(f_1,\dots,f_n)$，则 $g_n\in\mathcal{F}$ 且单调递增。设 $g_n\nearrow f$。

3. **用 MCT 得到最大绝对连续部分**：对任意 $E\in\mathcal{M}$，由单调收敛定理，
$$
   \int_E f\,d\mu
   = \lim_{n\to\infty}\int_E g_n\,d\mu
   \le \nu(E),
$$
   因此 $f\in\mathcal{F}$。于是 $f\,d\mu$ 就是能从 $\nu$ 中榨取出的最大绝对连续部分，记为 $\rho$。

4. **证明残余部分奇异**：定义 $d\lambda=d\nu-f\,d\mu$，由 $f\in\mathcal{F}$ 知 $\lambda$ 是正测度。若 $\lambda$ 不垂直于 $\mu$，则由引理 4.23，存在 $E$ 及 $\varepsilon>0$ 使在 $E$ 上 $\lambda\ge \varepsilon\mu$。对任意可测子集 $F\subset E$，
   $$
   \nu(F)-\int_F f\,d\mu \ge \varepsilon\mu(F)
   \quad\Longrightarrow\quad
   \int_F(f+\varepsilon\chi_E)\,d\mu \le \nu(F).
   $$
   这推出 $f+\varepsilon\chi_E\in\mathcal{F}$，但它在全空间的积分为 $a+\varepsilon\mu(E)>a$，与 $a$ 是上确界矛盾。因此 $\lambda\perp\mu$。

整个过程从构造候选集、逼近上确界，到用极限定理和反证法完成分解，体现了变分法中“极值对象的构造与验证”的核心范式。

## 1.4 Radon-Nikodym 导数的线性性质

**性质**：若 $\nu_1,\nu_2\ll\mu$ 为 $\sigma$-有限带号测度，则
$$
\frac{d(\nu_1+\nu_2)}{d\mu}
=\frac{d\nu_1}{d\mu}+\frac{d\nu_2}{d\mu}
\quad \mu\text{-a.e.}
$$

**证明**：设 $f_i=d\nu_i/d\mu$，则对一切可测集 $E$，有
$$
(\nu_1+\nu_2)(E)
=\nu_1(E)+\nu_2(E)
=\int_E f_1\,d\mu+
\int_E f_2\,d\mu
=\int_E(f_1+f_2)\,d\mu.
$$
由 Radon-Nikodym 导数的 $\mu$-a.e. 唯一性，即得结论。

## 1.5 唯一性
**1. Lebesgue 分解的唯一性**
假设存在两组分解：
$$\nu = \lambda_1 + \rho_1 = \lambda_2 + \rho_2$$
其中 $\lambda_1, \lambda_2 \perp \mu$，$\rho_1, \rho_2 \ll \mu$。由于 $\sigma$-有限，可移项相减，令 $\omega = \lambda_1 - \lambda_2 = \rho_2 - \rho_1$。证明 $\omega = 0$：
- **奇异性的传递**：存在零测集 $A_1, A_2$（$\mu(A_1)=\mu(A_2)=0$），使得 $\lambda_1$ 集中在 $A_1$，$\lambda_2$ 集中在 $A_2$。令 $A = A_1 \cup A_2$，则 $\mu(A)=0$，且 $\lambda_1,\lambda_2$ 在 $A^c$ 上为 $0$，故 $\omega$ 在 $A^c$ 上也为 $0$，即 $\omega \perp \mu$。
- **绝对连续性的传递**：$\rho_1,\rho_2 \ll \mu$，由线性性得 $\omega \ll \mu$。
- **得出矛盾**：$\omega$ 集中在 $A$ 上（$\omega(A^c)=0$），而 $\mu(A)=0$ 及 $\omega \ll \mu$ 推出 $\omega(A)=0$，因此 $\omega=0$。
故 $\lambda_1=\lambda_2$，$\rho_1=\rho_2$，分解唯一。

**2. Radon-Nikodym 导数 $f$ 的唯一性（几乎处处唯一）**
假设 $f_1,f_2$ 满足 $d\rho = f_1 d\mu = f_2 d\mu$。对任意可测集 $E$，
$$\int_E f_1 d\mu = \int_E f_2 d\mu \implies \int_E (f_1-f_2) d\mu = 0$$

## 1.6 例子-F绝对连续的L-S测度

当 $F$ 绝对连续且单调递增时，可诱导有限正测度。由 Radon-Nikodym 定理，存在积分核 $f$，使 $F$ 写成 $f$ 的积分。

**1. 存在性**  
$F$ 诱导 Lebesgue-Stieltjes 测度 $\mu_F$，满足 $\mu_F((c, d]) = F(d) - F(c)$。由绝对连续得 $\mu_F \ll m$。Radon-Nikodym 定理给出 $f \in L^1$，使得对任意 Borel 集 $A$：
$$\mu_F(A) = \int_A f dm$$
取 $A=[a,x]$ 得：
$$F(x) - F(a) = \int_a^x f(t) dt$$

**2. 唯一性**   
差商：
$$\frac{F(x+h)-F(x)}{h} = \frac1h \int_x^{x+h} f(t) dt$$
由 Lebesgue 微分定理，右边极限几乎处处等于 $f(x)$，故左边极限几乎处处存在且等于 $f(x)$，即：
$$F'(x) = f(x) \quad m\text{-a.e.}$$
# 2. Radon-Nikodym 导数的换元与链式法则

> [!Note] 命题 4.25
> 设 $\nu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$-有限带号测度，$\mu, \lambda$ 是 $\sigma$-有限测度且 $\nu \ll \mu$ 且 $\mu \ll \lambda$。
>
> （i）若 $g \in L^1(X, \nu)$，则 $g(d \nu / d \mu) \in L^1(X, \mu)$ 且
> $$
> \int_X g\,d\nu
> =\int_X g \frac{d \nu}{d \mu}\,d\mu.
> $$
>
> （ii）$\nu \ll \lambda$，且 Radon-Nikodym 导数满足：
> $$
> \frac{d \nu}{d \lambda}
> =\frac{d \nu}{d \mu} \cdot \frac{d \mu}{d \lambda}
> \quad \lambda\text{-a.e.}
> $$

## 2.1 积分换元公式

**目标**：证明
$$
\int_X g\,d\nu
= \int_X g \frac{d\nu}{d\mu}\,d\mu.
$$

核心目标是将关于 $\nu$ 的积分通过 Radon-Nikodym 导数 $\frac{d\nu}{d\mu}$ 转化为关于 $\mu$ 的积分。

**证明过程**：

1. **化归为正测度**：通过 Jordan 分解，任何带号测度 $\nu$ 可分解为 $\nu = \nu^+ - \nu^-$。由于积分和导数都是线性的，可直接假设 $\nu$ 是正测度，从而 $\frac{d\nu}{d\mu} \ge 0$，避免符号带来的麻烦。

2. **指示函数**：设 $g = \chi_E$（$E \in \mathcal{M}$）。左边 $\int_X \chi_E\,d\nu = \nu(E)$；右边由 R-N 导数定义：
$$
\nu(E)
= \int_E \frac{d\nu}{d\mu}\,d\mu
= \int_X \chi_E \frac{d\nu}{d\mu}\,d\mu.
$$

因此等式成立。

3. **简单函数**：设 $g = \sum c_i \chi_{E_i}$。由积分的线性，等式对每个 $\chi_{E_i}$ 成立则对线性组合成立。

4. **非负可测函数**：设 $g \ge 0$ 可测，存在简单函数列 $g_n \nearrow g$。对等式两边用 **单调收敛定理 (MCT)**：左边 $\int_X g\,d\nu = \lim\int_X g_n\,d\nu$，右边由于 $\frac{d\nu}{d\mu}\ge 0$，有

$$
\int_X g_n \frac{d\nu}{d\mu}\,d\mu
\to
\int_X g \frac{d\nu}{d\mu}\,d\mu.
$$

由第 3 步对每个 $n$ 成立，取极限后等式仍成立。

5. **一般 $L^1$ 函数**：$g = g^+ - g^-$，$g^+, g^-$ 非负可测，分别应用第 4 步，再相减即得。

## 2.2 链式法则

**目标**：证明
$$
\frac{d\nu}{d\lambda}
= \frac{d\nu}{d\mu} \cdot \frac{d\mu}{d\lambda}
\quad \lambda\text{-a.e.}
$$

已知 $\nu \ll \mu$ 且 $\mu \ll \lambda$。利用 (i) 的结论构造积分等式，再脱去积分号。

**证明过程**：

1. **先得到绝对连续关系**：由 $\nu \ll \mu$ 且 $\mu \ll \lambda$，立刻有 $\nu \ll \lambda$，所以 $\frac{d\nu}{d\lambda}$ 存在。

2. **构造两套积分表达**：对任意可测集 $E$，考虑 $\nu(E)$。一方面，由 $\nu \ll \lambda$ 得
$$
\nu(E) = \int_E \frac{d\nu}{d\lambda}\,d\lambda.
$$

另一方面，由 $\nu \ll \mu$ 得 $\nu(E) = \int_E \frac{d\nu}{d\mu}\,d\mu$。将 $\chi_E \frac{d\nu}{d\mu}$ 视为函数 $g$，应用命题 (i) 将 $\mu$ 积分转为 $\lambda$ 积分：
$$
\nu(E)
=\int_X \left(\chi_E \frac{d\nu}{d\mu}\right)\,d\mu
=\int_X \left(\chi_E \frac{d\nu}{d\mu}\right)\frac{d\mu}{d\lambda}\,d\lambda
=\int_E \left(\frac{d\nu}{d\mu}\frac{d\mu}{d\lambda}\right)\,d\lambda.
$$

3. **两式相减**：两个积分都等于 $\nu(E)$，故对任意 $E\in\mathcal{M}$，
$$
\int_E \left(
\frac{d\nu}{d\lambda}
-
\frac{d\nu}{d\mu}\frac{d\mu}{d\lambda}
\right)\,d\lambda = 0.
$$

4. **脱去积分号**：若对所有 $E$ 有 $\int_E f\,d\lambda = 0$，则 $f = 0$ $\lambda$-a.e.。因此
$$
\frac{d\nu}{d\lambda}
=
\frac{d\nu}{d\mu}\frac{d\mu}{d\lambda}
\quad \lambda\text{-a.e.}
$$

这部分逻辑严密流畅。“四步提拔法”是极强大的工具，在 Fubini 定理、拉东测度等章节会反复出现。
