定理 4.24 （Lebesgue－Radon－Nikodym 定理：带号测度情形）。设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的 $\sigma$－有限带号测度，$\mu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限正测度，则存在 $(X, \mathcal{M})$ 上的唯一 $\sigma$－有限带号测度 $\lambda$ 和 $\rho$ ，使得

$$
\lambda \perp \mu, \rho \ll \mu, \text { 且 } \nu=\lambda+\rho .
$$

此外，存在一个广义 $\mu$－可积函数 $f: X \rightarrow \mathbb{R}$ ，使得 $d \rho=f d \mu$ ，且任何两个这样的函数是 $\mu$－a．e．相等的．

**1. Lebesgue 分解：测度的“物以类聚”**

定理第一步给出分解 $\nu = \lambda + \rho$，对 $\nu$ 分类：
- **$\rho \ll \mu$（绝对连续测度）**：$\mu(E)=0 \implies \rho(E)=0$，$\rho$ 只在 $\mu$ 有正测度的地方非零。
- **$\lambda \perp \mu$（互相奇异测度）**：存在划分 $X=A\cup B$，$\mu(B)=0$，$\lambda(A)=0$，两者各自集中在不相交的集合上，互不“往来”。

**2. Radon-Nikodym 导数：绝对连续的本质**

第二步断言 $d\rho = f d\mu$，即绝对连续测度本质上是带密度函数的积分。
- $f$ 是 **Radon-Nikodym 导数**，记作 $f = \frac{d\rho}{d\mu}$。
- 它把导数推广到测度：在微积分中 $F(x)=\int_a^x f(t)dt$ 的导数是 $f$；这里 $\rho$ 相对 $\mu$ 的局部变化率就是 $f$。




命题 4．25．设 $\nu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限带号测度，$\mu, \lambda$ 是 $\sigma$－有限测度且 $\nu \ll \mu$ 且 $\mu \ll \lambda$ 。
（i）若 $g \in L^1(X, \nu)$ ，则 $g(d \nu / d \mu) \in L^1(X, \mu)$ 且
$$
\int_X g d \nu=\int_X g \frac{d \nu}{d \mu} d \mu
$$
（ii）$\nu \ll \lambda$ ，且 Radon－Nikodym 导数满足：
$$
\frac{d \nu}{d \lambda}=\frac{d \nu}{d \mu} \cdot \frac{d \mu}{d \lambda} \quad \lambda \text {-a.e. }
$$

