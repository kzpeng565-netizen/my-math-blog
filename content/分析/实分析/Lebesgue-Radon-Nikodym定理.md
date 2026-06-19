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

### 1.2.1 定义候选密度函数族

令
$$
\mathcal{F}
= \left\{f: X \to [0, \infty] \mid f \text{ 可测},\ \int_E f\,d\mu \le \nu(E),\ \forall E \in \mathcal{M}\right\}.
$$

$\mathcal{F}$ 收集了所有积分不超过 $\nu$ 的密度。关键性质：$\mathcal{F}$ 对取最大值封闭，即若 $f,g \in \mathcal{F}$，则 $\max(f,g) \in \mathcal{F}$。这允许我们将两个密度在不同区域的优势“拼接”成一个更大的合法密度。

### 1.2.2 取上确界并构造单调逼近序列

**在标准证明当中，我们先假设测度有限。**

令
$$
a = \sup_{f \in \mathcal{F}} \int_X f\,d\mu.
$$

由 $\nu$ 有限知 $a \le \nu(X) < \infty$。取序列 $\{f_n\} \subset \mathcal{F}$ 使
$$
\int_X f_n\,d\mu \to a.
$$

利用封闭性，令 $g_n = \max(f_1,\dots,f_n)$，则 $g_n \in \mathcal{F}$ 且单调递增，设 $g_n \nearrow f$。

### 1.2.3 用单调收敛定理提取最大绝对连续部分

对任意 $E \in \mathcal{M}$，由 MCT，
$$
\int_E f\,d\mu
= \lim_{n \to \infty} \int_E g_n\,d\mu
\le \nu(E),
$$
故 $f \in \mathcal{F}$。于是 $f\,d\mu$ 就是能榨取出的最大绝对连续部分，即 $\rho$。

### 1.2.4 反证法证明残余部分奇异

定义 $d\lambda = d\nu - f\,d\mu$，由 $f \in \mathcal{F}$ 知 $\lambda$ 是正测度。

假设 $\lambda$ 不垂直于 $\mu$，由引理 4.23，存在 $E$ 及 $\varepsilon>0$ 使在 $E$ 上 $\lambda \ge \varepsilon \mu$。对任意可测子集 $F \subset E$，
$$
\nu(F) - \int_F f\,d\mu \ge \varepsilon \mu(F)
\quad\Longrightarrow\quad
\int_F (f + \varepsilon \chi_E)\,d\mu \le \nu(F).
$$

这推出 $f + \varepsilon \chi_E \in \mathcal{F}$，但它在全空间的积分为 $a + \varepsilon \mu(E) > a$，与 $a$ 是上确界矛盾。故 $\lambda \perp \mu$ 成立。

整个过程从构造候选集、逼近上确界，到用极限定理和反证法完成分解，充分体现了变分法中“极值对象的构造与验证”的核心范式。

## 1.3 Radon-Nikodym 导数的线性性质

**性质**：Radon-Nikodym 导数满足线性性质。

**回顾定义**：设 $\nu_1,\nu_2 \ll \mu$ 为 $\sigma$-有限带号测度，则存在 $f_i = d\nu_i/d\mu$，使得 $\nu_i(E)=\int_E f_i\,d\mu$ 对一切可测集 $E$ 成立。

**构造积分等式**：对 $\nu=\nu_1+\nu_2$，有
$$
\nu(E)
=\nu_1(E)+\nu_2(E)
=\int_E f_1\,d\mu+\int_E f_2\,d\mu
=\int_E (f_1+f_2)\,d\mu.
$$
其中最后一步使用了 Lebesgue 积分的线性性。

**利用唯一性**：上式表明 $\nu$ 关于 $\mu$ 的 R-N 导数为 $f_1+f_2$，由 $\mu$-a.e. 唯一性即得
$$
\frac{d(\nu_1+\nu_2)}{d\mu}
=\frac{d\nu_1}{d\mu}+\frac{d\nu_2}{d\mu}
\quad \mu\text{-a.e.}
$$

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

### 2.1.1 前置准备：化归为正测度

通过 Jordan 分解，任何带号测度 $\nu$ 可分解为 $\nu = \nu^+ - \nu^-$。由于积分和导数都是线性的，可直接假设 $\nu$ 是正测度，从而 $\frac{d\nu}{d\mu} \ge 0$，避免符号带来的麻烦。

接下来是“四步提拔法”：

1. **指示函数**：设 $g = \chi_E$（$E \in \mathcal{M}$）。左边 $\int_X \chi_E\,d\nu = \nu(E)$；右边由 R-N 导数定义
   $$
   \nu(E)
   = \int_E \frac{d\nu}{d\mu}\,d\mu
   = \int_X \chi_E \frac{d\nu}{d\mu}\,d\mu.
   $$
   等式成立。

2. **简单函数**：设 $g = \sum c_i \chi_{E_i}$。由积分的线性，等式对每个 $\chi_{E_i}$ 成立则对线性组合成立。

3. **非负可测函数**：设 $g \ge 0$ 可测，存在简单函数列 $g_n \nearrow g$。对等式两边用 **单调收敛定理 (MCT)**：左边 $\int_X g\,d\nu = \lim\int_X g_n\,d\nu$，右边
   $$
   \int_X g_n \frac{d\nu}{d\mu}\,d\mu
   \to
   \int_X g \frac{d\nu}{d\mu}\,d\mu
   $$
   （因 $\frac{d\nu}{d\mu}\ge 0$）。由第 2 步对每个 $n$ 成立，取极限后等式仍成立。

4. **一般 $L^1$ 函数**：$g = g^+ - g^-$，$g^+, g^-$ 非负可测，分别应用第 3 步，再相减即得。

## 2.2 链式法则

**目标**：证明
$$
\frac{d\nu}{d\lambda}
= \frac{d\nu}{d\mu} \cdot \frac{d\mu}{d\lambda}
\quad \lambda\text{-a.e.}
$$

已知 $\nu \ll \mu$ 且 $\mu \ll \lambda$。利用 (i) 的结论构造积分等式，再脱去积分号。

1. **构造两套积分表达**：对任意可测集 $E$，考虑 $\nu(E)$。

   - 第一套：由 $\nu \ll \lambda$ 得
     $$
     \nu(E) = \int_E \frac{d\nu}{d\lambda}\,d\lambda.
     $$

   - 第二套：由 $\nu \ll \mu$ 得
     $$
     \nu(E) = \int_E \frac{d\nu}{d\mu}\,d\mu.
     $$
     将 $\chi_E \frac{d\nu}{d\mu}$ 视为函数 $g$，应用命题 (i) 将 $\mu$ 积分转为 $\lambda$ 积分：
     $$
     \int_X \left(\chi_E \frac{d\nu}{d\mu}\right)\,d\mu
     =
     \int_X \left(\chi_E \frac{d\nu}{d\mu}\right)\frac{d\mu}{d\lambda}\,d\lambda
     =
     \int_E \left(\frac{d\nu}{d\mu}\frac{d\mu}{d\lambda}\right)\,d\lambda.
     $$

2. **两式相减**：两个积分都等于 $\nu(E)$，故
   $$
   \int_E \left(
   \frac{d\nu}{d\lambda}
   -
   \frac{d\nu}{d\mu}\frac{d\mu}{d\lambda}
   \right)\,d\lambda = 0
   $$
   对任意 $E\in\mathcal{M}$ 成立。

3. **脱去积分号**：若对所有 $E$ 有 $\int_E f\,d\lambda = 0$，则 $f = 0$ $\lambda$-a.e.。因此
   $$
   \frac{d\nu}{d\lambda}
   =
   \frac{d\nu}{d\mu}\frac{d\mu}{d\lambda}
   \quad \lambda\text{-a.e.}
   $$

这部分逻辑严密流畅。“四步提拔法”是极强大的工具，在 Fubini 定理、拉东测度等章节会反复出现。
