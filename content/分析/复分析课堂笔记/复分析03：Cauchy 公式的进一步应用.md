---
tags:
  - 复分析
  - 分析
---
#复分析 #课堂笔记  

本节给出了柯西公式的主要结果
柯西公式使得我们能够通过**积分的方式求导**, 在讨论收敛性的时候, 积分的要求往往比求导弱很多.

魏尔斯特拉斯第一逼近定理(Theorem 5.2) 告诉了我们: 远远强于实函数, 全纯函数序列内闭一致收敛, 不仅保持了全纯性, 还保证了$f^{(m)}_{n}\rightrightarrows f^{(m)}$ 
应用: 我们可以对Taylor级数求任意阶导数
## Analytic Continuation

Let $\emptyset\neq\Omega \subset\Omega'\subset \mathbb{C}$ be connected open sets.  
Let $f:\Omega \to \mathbb{C}$, and $F,G:\Omega'\to \mathbb{C}$ be holomorphic functions.  
$F$ is called an **analytic continuation** of $f$ if $F|_{\Omega}=f$.

>[!Proposition]
>If $F$ and $G$ are analytic continuations of $f$ on $\Omega'$, then $F=G$.  
>This means that holomorphic functions are **rigid**.

### 证明思路
$F-G=0, \:when \: x\in\Omega'$
![[复分析02：Cauchy 积分公式的应用#^eb9556]]
从而根据孤立零点特性，$F-G=0$

**Example**: $C^{\infty}$ real functions are not rigid.

## Morera's Theorem

>[!Theorem 5.1: Morera's Theorem]
>Suppose $f$ is a continuous function in the open disc $D$ such that for any triangle $T$ contained in $D$:
>$$
>\int_{T} f(z)  dz = 0,
>$$
>then $f$ is holomorphic.

### 证明思路
$\int_{T} f(z)  dz = 0,$可以得到$F=\int_{\gamma}f(z)dz$，$\gamma$是如[[复分析01Cauchy theorem]] Theorem 2.1的简单曲线。从而$F$是可微的，进而$F$是全纯的, $f$也是全纯函数
**Proof**: By the proof of Theorem 2.1, the function $f$ has a primitive $F$ in $D$ that satisfies $F' = f$. By the regularity theorem, we know that $F$ is indefinitely (and hence twice) complex differentiable, and therefore $f$ is holomorphic.

## Sequence of Holomorphic Functions

>[!Theorem 5.2 内闭一致收敛推出极限函数是全纯函数]
>If $\{f_n\}_{n=1}^{\infty}$ is a sequence of holomorphic functions that converges uniformly to a function $f$ in every compact subset of $\Omega$, then $f$ is holomorphic in $\Omega$.

此处$\Omega$是连通开集
$f_{n}$ converges uniformly on $K$ means: for any $\varepsilon>0$, $\exists N$ such that
$$
\sup_{K}|f_{n}-f_{m}|<\varepsilon.
$$
In this case, the limit $f$ is a continuous function, and $\sup_{K}|f-f_{n}|\to 0$.

### 证明思路
对于任意一个三角形都可以构造一个紧集，这个紧集上$f_{n}\rightrightarrows f$​	
根据柯西积分公式$f_{n}$可以用一个积分公式表示，然后一致极限可以与积分交换，从而$\int_{T}f=0$
**Proof**:  
We will use Morera's theorem to prove $\int_{T}f=0$.  
We remark that $K=T\cup \{\text{interior of } T\}$.  
We know that $\{f_{n}\}$ converges uniformly to $f$ on $K$ by assumption.  
By Goursat's theorem, we have $\int_{T}f_{n}=0$ for all $n$.  
Thus, $\int_{T}f=0$.

**Example**: This property does not hold for $C^{\infty}$ real functions. Let $f_{n}(x)=\sqrt{x^{2}+ \frac{1}{n}}$ for all $n$, for all $x\in \mathbb{R}$.  
$f_{n}\to f=|x|$, but $|x|$ is not differentiable at $0$.

>[!Theorem 5.3 原函数内闭一致连续推出导函数内闭一致收敛]
>Under the hypotheses of the previous theorem, the sequence of derivatives $\{f_n'\}_{n=1}^{\infty}$ converges uniformly to $f'$ on every compact subset of $\Omega$.

Similarly, we can show that for any $k\in\mathbb{N}$, $\{f_{n}^{(k)}\}$ converges uniformly to $f^{(k)}$ on any compact subset.

### 证明思路
任意取一个紧集，可以用柯西积分公式中的开圆盘覆盖，因此只需要证明在有限个开圆盘中是一致收敛的。
利用$$
\left| (f'-f_{n}')(z) \right| \leq \frac{1}{2\pi} \int_{C} \frac{|f(\xi)-f_{n}(\xi)|}{|\xi-z|^{2}}d\xi.
$$
这个积分是有界的，而且上界与$\sup|f(\xi)-f_{n}(\xi)|$相关
**Proof**: For a given compact $K \subset\Omega$, we cover $K$ by finitely many open discs $D_{1},\dots,D_{m}$ such that $\bar{D_{1}},\dots,\bar{D_{m}}$ are contained in $\Omega$.  
We only need to prove the convergence on each $D_{i}$.  
Now let $D$ be a disc such that $\bar{D}\subset\Omega$.  
Then for any holomorphic function $g$ on $\Omega$, we have
$$
g'(z)= \frac{1}{2\pi i} \int_{C} \frac{g(\xi)}{(\xi-z)^{2}}d\xi
$$
where $C=\partial D$, $z\in D$.  
We put $g=f-f_{n}$, then we have
$$
\left| (f'-f_{n}')(z) \right| \leq \frac{1}{2\pi} \int_{C} \frac{|f(\xi)-f_{n}(\xi)|}{|\xi-z|^{2}}d\xi.
$$
If $z\in D'\subset D$, where $D'$ has the same center as $D$, and has radius equal to $(1-\Lambda)$ times the radius of $D$, then
$$
|f'(z)-f'_{n}(z)|\leq \frac{1}{2\pi} \cdot \frac{1}{(1-\Lambda)^{2}R^{2}}\sup_{C}|f-f_{n}|
$$
where $R$ is the radius of $D$.  
Since $f_{n}$ converges uniformly to $f$ on $C$, we see that
$$
\sup_{C}|f-f_{n}| \to 0.
$$
Thus
$$
\sup_{D}|f'-f'_{n}|\to 0.
$$

**Core idea**: Derivatives of a holomorphic function can be uniformly controlled by the infinity norm.

## Variant: Series of Holomorphic Functions

Let $\{f_{n}\}$ be a sequence of holomorphic functions on $\Omega$. Let $S_{m}=\sum_{n=0}^{m}f_{n}$.  
The series $\sum_{n=0}^{\infty}f_{n}$ is the formal sum of $\{f_{n}\}$.  
We say that this series converges uniformly on a subset $K\subset\Omega$ if the sequence $\{S_{m}\}$ converges uniformly on $K$.  
By the previous theorem, if $\sum f_{n}$ converges uniformly on any compact subset of $\Omega$, then
$$
F=\sum_{n=0}^{\infty}f_{n}
$$
is a holomorphic function on $\Omega$.

## Holomorphic Functions Defined in terms of integral

>[!Theorem]
>Let $F(z,s):\Omega \times [0,1]\to \mathbb{C}$, $(z,s)\to F(z,s)$, where $\Omega \subset \mathbb{C}$ is compact.  
>Assume that:
>1. For any $s\in[0,1]$, $F(z,s)$ is a holomorphic function in $z$.
>2. $F$ is continuous on $\Omega \times[0,1]$.
>
>Then
>$$
>f(z)=\int_{0}^{1} F(z,s)  ds 
>$$
>defines a holomorphic function on $\Omega$.

There are two proofs:

**Proof 1**: By Morera's theorem  
We only need to prove
$$
0=\int_{z\in T}f(z)=\int_{z\in T}\int_{0}^{1} F(z,s)  ds 
$$
for any appropriate triangle $T$.  
To this end, we notice that $T\times[0,1]$ is compact, and $F$ is continuous on $\Omega \times[0,1]$. Thus we can interchange $\int_{z\in T}$ and $\int_{0}^{1}$.  
It follows that
$$
\int_{z\in T}f= \int_{z\in T}\int_{0}^{1} F(z,s)  ds = \int_{0}^{1} \left( \int_{z\in T}F(z,s) \right)  ds =\int_{0}^{1}0  ds = 0.
$$

**Proof 2**:  
For any $n\in \mathbb{N}$, we define the Riemann sum
$$
f_{n}(z)= \frac{1}{n} \sum_{i=1}^{n} F\left(z, \frac{i}{n}\right).
$$
We will show that $\{f_{n}\}$ converges uniformly to $f$ on any compact subset of $\Omega$.  
Let $D$ be a disc with $\bar{D} \subset \Omega$.  
Since $F$ is continuous, it is uniformly continuous on $\bar{D} \times[0,1]$.  
Here, for a fixed $\varepsilon>0$, $\exists N$ such that $\left| F\left( z, \frac{i}{n}\right)-F(z,s) \right|\leq\varepsilon$ when $z\in \bar{D}$ and $s\in\left[ \frac{i-1}{n}, \frac{i}{n} \right]$.  
Then, for any $n\geq N$, we have
$$
\begin{align*}
|f(z)-f_{n}(z)|&\leq \sum _{i=1}^{n}  \int_{ \frac{i-1}{n}}^{\frac{i}{n}} |F(z,s)-F\left( z, \frac{i}{n} \right)|  ds  \\
&\leq \sum_{i=1}^{n} \int_{ \frac{i-1}{n}}^{\frac{i}{n}} \varepsilon  ds = \varepsilon 
\end{align*}
$$
for any $z\in \bar{D}$.  
This proves that $\{f_{n}\}$ converges uniformly on $\bar{D}$ to $f$, and completes the proof of the theorem.

![[Pasted image 20251020143920.png|600]]

## Symmetry Principle

>[!Theorem 5.5: Symmetry Principle]
>If $f^{+}$ and $f^{-}$ are holomorphic functions in $\Omega^{+}$ and $\Omega^{-}$ respectively, that extend continuously to $I$ and
>$$
>f^{+}(x) = f^{-}(x) \quad \text{for all } x \in I,
>$$
>then the function $f$ defined on $\Omega$ by
>$$
>f(z) = \begin{cases}
>f^{+}(z) & \text{if } z \in \Omega^{+},\\
>f^{+}(z) = f^{-}(z) & \text{if } z \in I,\\
>f^{-}(z) & \text{if } z \in \Omega^{-}
>\end{cases}
>$$
>is holomorphic on all of $\Omega$.

**Proof**: We observe immediately that $f$ is continuous.  
We will then check with Morera's theorem.

![[Pasted image 20251020144206.png]]

>[!Theorem]
>Assume that $\Omega$ is as in the previous theorem.  
>Let $f^{+}:\Omega^{+}\to \mathbb{C}$ be a holomorphic function such that $f^{+}$ extends continuously on $I$, and that $f|_{I}$ has real values. Then the function
>$$
>f(z) = \begin{cases}
>f^{+}(z) & \text{if } z \in \Omega^{+},\\
>f^{+}(z) & \text{if } z \in I,\\
>\overline{f^{+}(\bar{z})} & \text{if } z \in \Omega^{-}
>\end{cases}
>$$
>is holomorphic on $\Omega$.

**Remark**: To memorize $\overline{f^{+}(\bar{z})}$, we can imagine that
$$
f^{+}(z)=\sum a_{i}z^{i} \quad\text{is a series}.
$$
Then $f^{+}(\bar{z})=\sum a_{i}\bar{z}^{i}$ is anti-holomorphic,  
and $\overline{f^{+}(\bar{z})}=\sum \bar{a_{i}}z^{i}$ is again holomorphic.

## Evaluation of Certain Integrals

Recall that if $\gamma$ is a closed simple curve such that $\gamma$ and its interior are contained in $\Omega \subset \mathbb{C}$, and if $f:\Omega \to \mathbb{C}$ is holomorphic, then $\int_{\gamma}f=0$.

**Example 1**:  
For any $\xi\in \mathbb{R}$, we have
$$
\int_{\mathbb{R}}e^{-\pi x^{2}}e^{-2\pi ix\cdot \xi}dx= e^{-\pi \xi^{2}}.
$$

**Proof of Example 1**:  
Recall that $1=\int_{-\infty}^{+\infty}e^{-\pi x^{2}}dx$. Fix $\xi\in\mathbb{R}$.  
If $\xi = 0$, the formula is precisely the known integral:
$$
1 = \int_{-\infty}^{\infty} e^{-\pi x^2}  dx.
$$
Now suppose that $\xi > 0$, and consider the function $f(z) = e^{-\pi z^2}$, which is entire, and in particular holomorphic in the interior of the toy contour $\gamma_R$ depicted in Figure 8.

![[Pasted image 20251020150139.png|500]]

The contour $\gamma_R$ consists of a rectangle with vertices $R, R + i \xi, -R + i \xi, -R$ and the positive counterclockwise orientation. By Cauchy's theorem,
$$
\int_{\gamma_R} f(z)  dz = 0\qquad (6)
$$
The integral over the real segment is simply
$$
\int_{-R}^{R} e^{-\pi x^2}  dx,
$$
which converges to $1$ as $R \to \infty$. The integral on the vertical side on the right is
$$
I(R) = \int_{0}^{\xi} f(R + i y) i  dy = \int_{0}^{\xi} e^{-\pi (R^2 + 2i R y - y^2)} i  dy.
$$
This integral goes to $0$ as $R \to \infty$ since $\xi$ is fixed and we may estimate it by
$$
|I(R)| \leq e^{-\pi R^{2}}\cdot \int_{0}^{\xi}\left| e^{\pi y^{2}-2\pi iR y} \right| dy= e^{-\pi R^{2}}\int_{0}^{\xi} e^{\pi y^{2}}  dy \leq e^{-\pi R^{2}}\xi e^{\pi \xi^{2}}\leq C e^{-\pi R^2}.
$$
Similarly, the integral over the vertical segment on the left also goes to $0$ as $R \rightarrow \infty$ for the same reasons. Finally, the integral over the horizontal segment on top is
$$\begin{align*}
\int_{R}^{-R} e^{-\pi(x + i \xi)^2} \, dx = -e^{\pi \xi^2} \int_{-R}^{R} e^{-\pi x^2} e^{-2\pi i x \xi} \, dx.
\end{align*}$$
Therefore, we find in the limit as $R \rightarrow \infty$ that (6) gives
$$\begin{align*}
0 = 1 - e^{\pi \xi^2} \int_{-\infty}^{\infty} e^{-\pi x^2} e^{-2\pi i x \xi} \, dx,
\end{align*}$$

