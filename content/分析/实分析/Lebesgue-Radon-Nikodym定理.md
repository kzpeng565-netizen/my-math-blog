定理 4.24 （Lebesgue－Radon－Nikodym 定理：带号测度情形）。设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的 $\sigma$－有限带号测度，$\mu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限正测度，则存在 $(X, \mathcal{M})$ 上的唯一 $\sigma$－有限带号测度 $\lambda$ 和 $\rho$ ，使得

$$
\lambda \perp \mu, \rho \ll \mu, \text { 且 } \nu=\lambda+\rho .
$$

此外，存在一个广义 $\mu$－可积函数 $f: X \rightarrow \mathbb{R}$ ，使得 $d \rho=f d \mu$ ，且任何两个这样的函数是 $\mu$－a．e．相等的．

## 命题的结论

**1. Lebesgue 分解：测度的“物以类聚”**

定理第一步给出分解 $\nu = \lambda + \rho$，对 $\nu$ 分类：
- **$\rho \ll \mu$（绝对连续测度）**：$\mu(E)=0 \implies \rho(E)=0$，$\rho$ 只在 $\mu$ 有正测度的地方非零。
- **$\lambda \perp \mu$（互相奇异测度）**：存在划分 $X=A\cup B$，$\mu(B)=0$，$\lambda(A)=0$，两者各自集中在不相交的集合上，互不“往来”。

**2. Radon-Nikodym 导数：绝对连续的本质**

第二步断言 $d\rho = f d\mu$，即绝对连续测度本质上是带密度函数的积分。
- $f$ 是 **Radon-Nikodym 导数**，记作 $f = \frac{d\rho}{d\mu}$。
- 它把导数推广到测度：在微积分中 $F(x)=\int_a^x f(t)dt$ 的导数是 $f$；这里 $\rho$ 相对 $\mu$ 的局部变化率就是 $f$。

## 证明的思路

核心想法是：从 $\nu$ 中尽可能“榨取”出对 $\mu$ 绝对连续的部分 $\int f d\mu$，榨干后的残余必然是完全奇异的 $\lambda$。

**定义候选密度函数族**
$$
\mathcal{F} = \{f: X \to [0, \infty] \mid f \text{ 可测}, \int_E f d\mu \le \nu(E), \forall E \in \mathcal{M}\}
$$
$\mathcal{F}$ 收集了所有积分不超过 $\nu$ 的密度。关键性质：$\mathcal{F}$ 对取最大值封闭，即若 $f,g \in \mathcal{F}$，则 $\max(f,g) \in \mathcal{F}$。这允许我们将两个密度在不同区域的优势“拼接”成一个更大的合法密度。

**取上确界并构造单调逼近序列**
**在标准证明当中, 我们先假设测度有限** 
令 $a = \sup_{f \in \mathcal{F}} \int_X f d\mu$，由 $\nu$ 有限知 $a \le \nu(X) < \infty$。取序列 $\{f_n\} \subset \mathcal{F}$ 使 $\int_X f_n d\mu \to a$。利用封闭性，令 $g_n = \max(f_1,\dots,f_n)$，则 $g_n \in \mathcal{F}$ 且单调递增，设 $g_n \nearrow f$。

**用单调收敛定理提取最大绝对连续部分**
对任意 $E \in \mathcal{M}$，由 MCT，
$$
\int_E f d\mu = \lim_{n \to \infty} \int_E g_n d\mu \le \nu(E),
$$
故 $f \in \mathcal{F}$。于是 $f d\mu$ 就是能榨取出的最大绝对连续部分，即 $\rho$。

**反证法证明残余部分奇异**
定义 $d\lambda = d\nu - f d\mu$，由 $f \in \mathcal{F}$ 知 $\lambda$ 是正测度。假设 $\lambda$ 不垂直于 $\mu$，由引理 4.23，存在 $E$ 及 $\varepsilon>0$ 使在 $E$ 上 $\lambda \ge \varepsilon \mu$。对任意可测子集 $F \subset E$，
$$
\nu(F) - \int_F f d\mu \ge \varepsilon \mu(F)
\quad\Longrightarrow\quad
\int_F (f + \varepsilon \chi_E) d\mu \le \nu(F).
$$
这推出 $f + \varepsilon \chi_E \in \mathcal{F}$，但它在全空间的积分为 $a + \varepsilon \mu(E) > a$，与 $a$ 是上确界矛盾。故 $\lambda \perp \mu$ 成立。

整个过程从构造候选集、逼近上确界，到用极限定理和反证法完成分解，充分体现了变分法中“极值对象的构造与验证”的核心范式。


命题 4．25．设 $\nu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限带号测度，$\mu, \lambda$ 是 $\sigma$－有限测度且 $\nu \ll \mu$ 且 $\mu \ll \lambda$ 。
（i）若 $g \in L^1(X, \nu)$ ，则 $g(d \nu / d \mu) \in L^1(X, \mu)$ 且
$$
\int_X g d \nu=\int_X g \frac{d \nu}{d \mu} d \mu
$$
（ii）$\nu \ll \lambda$ ，且 Radon－Nikodym 导数满足：
$$
\frac{d \nu}{d \lambda}=\frac{d \nu}{d \mu} \cdot \frac{d \mu}{d \lambda} \quad \lambda \text {-a.e. }
$$

