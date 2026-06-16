定理 4.24 （Lebesgue－Radon－Nikodym 定理：带号测度情形）。设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的 $\sigma$－有限带号测度，$\mu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限正测度，则存在 $(X, \mathcal{M})$ 上的唯一 $\sigma$－有限带号测度 $\lambda$ 和 $\rho$ ，使得

$$
\lambda \perp \mu, \rho \ll \mu, \text { 且 } \nu=\lambda+\rho .
$$

此外，存在一个广义 $\mu$－可积函数 $f: X \rightarrow \mathbb{R}$ ，使得 $d \rho=f d \mu$ ，且任何两个这样的函数是 $\mu$－a．e．相等的．

### 1. Lebesgue 分解：测度的“物以类聚”

定理的第一步断言了 $\nu = \lambda + \rho$。这是在对测度 $\nu$ 进行分类：

- **$\rho \ll \mu$（绝对连续测度）**：这是相对于 $\mu$ 的“乖孩子”。绝对连续的意思是，只要 $\mu(E) = 0$，就必然有 $\rho(E) = 0$。也就是说，$\rho$ 只能在 $\mu$ 认为有意义（测度大于 0）的地方“存活”。
    
- **$\lambda \perp \mu$（互相奇异测度）**：这是相对于 $\mu$ 的“外星人”。互相奇异意味着存在一个划分 $X = A \cup B$，使得 $\mu$ 完全集中在 $A$ 上（$\mu(B)=0$），而 $\lambda$ 完全集中在 $B$ 上（$\lambda(A)=0$）。它们生活在同一个空间里，但彼此“老死不相往来”。
    

### 2. Radon-Nikodym 导数：绝对连续的本质

定理的第二步断言 $d\rho = f d\mu$。

既然 $\rho$ 是依附于 $\mu$ 的“乖孩子”，那么 $\rho$ 到底是怎么依附于 $\mu$ 的？定理说：**绝对连续测度本质上就是一个带有密度函数的积分。**

- 这里的 $f$ 就是大名鼎鼎的 **Radon-Nikodym 导数**，通常记作 $f = \frac{d\rho}{d\mu}$。
    
- 它把微积分里的导数概念推广到了测度上。在普通微积分里，如果 $F(x) = \int_a^x f(t)dt$，那么 $F$ 的变化率（导数）是 $f$。这里说的是，测度 $\rho$ 相对于测度 $\mu$ 的局部变化率就是 $f$。


命题 4．25．设 $\nu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限带号测度，$\mu, \lambda$ 是 $\sigma$－有限测度且 $\nu \ll \mu$ 且 $\mu \ll \lambda$ 。
（i）若 $g \in L^1(X, \nu)$ ，则 $g(d \nu / d \mu) \in L^1(X, \mu)$ 且
$$
\int_X g d \nu=\int_X g \frac{d \nu}{d \mu} d \mu
$$
（ii）$\nu \ll \lambda$ ，且 Radon－Nikodym 导数满足：
$$
\frac{d \nu}{d \lambda}=\frac{d \nu}{d \mu} \cdot \frac{d \mu}{d \lambda} \quad \lambda \text {-a.e. }
$$

