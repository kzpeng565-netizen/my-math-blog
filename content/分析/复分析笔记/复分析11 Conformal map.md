---
tags:
  - 复分析
  - 分析
---
$(f^{-1})'(z)=\frac{1}{f'(f^{-1}(z))}=\frac{1}{f'(w)},w=f^{-1}(z)$   
# 1. Conformal Maps

## 1.1 Definition and Basic Properties

**Definition**: Let $U,V$ be open in $\mathbb{C}$. Let $f:U\to V$ be a bijective map. We say that $f$ is **biholomorphic** (or **conformal**) if $f$ is holomorphic. In this case, we say that $U,V$ are **conformally equivalent**, or $U$ and $V$ are **biholomorphic**.

> [!Note] Property
>If $f:U\to V$ is conformal, then $f'(z)\neq 0$ for all $z\in U$. In particular, $f^{-1}$ is holomorphic.

### 1.1.1 Proof Outline

反证法, 假设$f'(z_{0})=0$, 那么周围存在一个区域$f'(z)\neq0$, 也就是不可能有重根. 证明f不可能是双射. $f(z_{0})=w_{0}$, $f(z)-w_{0}+w_{0}-w_{1}$, 根据Rouche 定理, 如果选取$w_{1}$足够接近$w_{0}$,  $\left| w_{0}-w_{1} \right|<\left| f(z)-w_{0} \right| ,\:\forall x\in C_{r}(z_{0})$ 那么$f(z)-w_{1}$的零点个数等于$f(z)-w_{0}$的个数, 至少为二重. 但是不可能有重根, 所以至少有两个根, 矛盾.

- 直觉: 全纯函数$f(z)-w_{0}$与$f(z)-w_{1}$的零点个数差不多.
- 导数不等于0让$f(z)-w_{0}$在一个邻域内不可能有重根

详细充要定理见[[复分析习题08]] 
### 1.1.2 Proof of the Property

Let $g=f^{-1}$. From $z=f(g(z))$, we get $1=f'(g(z))g'(z)$, so $g'(z)=\frac{1}{f'(g(z))}$.

Assume by contradiction that $f'(z_0)=0$ at some $z_0\in U$. Let $w_0=f(z_0)$. Since $f$ is holomorphic, there exists a disc $D_r(z_0)$ with $\overline{D_r}(z_0)\subset U$ where $f$ has a power series expansion:
$$
f(z)=\sum_{n=0}^{+\infty} a_n(z-z_0)^n \quad \text{for } z\in D_r(z_0)
$$
Then $a_0=f(z_0)=w_0$ and $f'(z)=\sum_{n=1}^{+\infty}na_n(z-z_0)^{n-1}$, so $f'(z_0)=a_1$.

Assume $a_1=0$. Then $f(z)=w_0+(z-z_0)^k(a_k+h(z))$ where $h$ is holomorphic, $h(z_0)\neq 0$, $k\geq 2$, and $a_k\neq 0$. Thus $f(z)-w_0$ has a zero of order $k\geq 2$ at $z_0$.

Since $f$ is bijective, $z_0$ is the only point where $f(z)=w_0$. Now choose $w_1$ close to $w_0$ with $|w_1-w_0|<\inf_{z\in C_r(z_0)}|f(z)-w_0|$. By **Rouché's Theorem** ([[复分析08 Argument principle#^e4a105|Rouche's Theorem]]), $f(z)-w_1$ has the same number of zeros as $f(z)-w_0$ inside $D_r(z_0)$, i.e., $k$ zeros counting multiplicity.

Let $z_1$ be one such zero. Since $f$ is not constant and $f'$ is holomorphic, the zeros of $f'$ do not accumulate in $U$. By choosing $r$ sufficiently small, we may assume $f'(z)\neq 0$ for $z\in D_r(z_0)-\{z_0\}$. In particular, $f'(z_1)\neq 0$, so $f(z)-w_1$ has a zero of order 1 at $z_1$. Thus, there must be another zero $z_2\in D_r(z_0)$, contradicting the injectivity of $f$.

## 1.2 Unit Disc and Upper Half-Plane

**Definition**: Unit disc $\mathbb{D}=\{z\in \mathbb{C},|z|<1\}$, Upper half-plane $\mathbb{H}=\{z\in \mathbb{C}|\mathrm{Im}(z)>0\}$.

> [!Note]  Theorem
> Let $F(z)=\frac{i-z}{i+z}$, $G(w)=i\frac{1-w}{1+w}$. Then $F:\mathbb{H}\to \mathbb{D}$, $G:\mathbb{D}\to \mathbb{H}$ are conformal, and $F\circ G(w)=w$, $G\circ F(z)=z$.

### 1.2.1 Proof of the Theorem

For $z\in \mathbb{H}$, we verify $|F(z)|<1$. Similarly, for $w\in \mathbb{D}$, we verify $G(w)\in \mathbb{H}$.

To show $F$ and $G$ are bijective, we compute:
$$
F(G(w))=\frac{i-i\frac{1-w}{1+w}}{i+i\frac{1-w}{1+w}}=\frac{1+w-1+w}{1+w+1-w}=w
$$
Similarly, $G(F(z))=z$.

### 1.2.2 Boundary Properties

For $z\in \partial \mathbb{H}$ (real axis), we have:
$$
F(z)=\frac{-(z^2-1)}{z^2+1}+i\frac{2z}{z^2+1}, \quad |F(z)|=1
$$
Thus $F(z)\in \partial \mathbb{D}$.

As $z\to +\infty$, $F(z)\to -1$ from the upper half-circle; as $z\to -\infty$, $F(z)\to -1$ from the lower half-circle.

For any $w\in \partial \mathbb{D}$ with $w\neq -1$, there exists a unique $z\in \mathbb{R}$ such that $F(z)=w$.

![[Pasted image 20251110142737.png]]

## 1.3 Fractional Linear Maps

**Definition**: Let $a,b,c,d\in \mathbb{C}$. A **fractional linear map** is a meromorphic function of the form:
$$
f(z)=\frac{az+b}{cz+d}
$$

**Examples**:
1. $f(z)=cz$ where $c\in \mathbb{C}\setminus\{0\}$
   - When $c=\rho>0$, called **dilatation**
   - When $|c|=1$, called **rotation**
2. **Affine map** $f(z)=az+b$
   - When $a=1$, called **translation**
3. $f(z)=e^z$ is a conformal map from the strip $U=\{z| -\frac{\pi}{2}<\mathrm{Im}z<\frac{\pi}{2}\}$ to $V=\{w\in \mathbb{C}||w|<1, \mathrm{Re}w>0\}$

![[Pasted image 20251110144314.png]]

The inverse $g:V\to U$ is the logarithm: for $w=\rho e^{i\theta}\in V$ with $0<\rho<1$, $\theta\in(-\frac{\pi}{2},\frac{\pi}{2})$, we have $\log w=\log\rho+i\theta\in U$.

4. The logarithm on $\mathbb{H}$: For $z=\rho e^{i\theta}\in \mathbb{H}$ with $\theta\in(0,\pi)$, define $\log z=\log\rho+i\theta$.

![[Pasted image 20251110145229.png]]

**Boundary Properties**: As $\theta\to \pi$, $e^z$ tends to the negative real axis; as $\theta\to 0$, $e^z$ tends to the positive real axis. The logarithm is defined on $\overline{\mathbb{H}}\setminus\{0\}=\{z\in \mathbb{C},\mathrm{Im}(z)\geq 0,z\neq 0\}$.

## 1.4 Dirichlet Problem in a Strip

Consider $\Omega=\{z\in \mathbb{C}|0<\mathrm{Im}(z)<1\}$ and the **Dirichlet Problem**:
$$
\begin{cases}
\Delta u=0 \\
u|_{\partial\Omega}=f
\end{cases}
$$
where $f$ is a given continuous function on $\partial\Omega$, and we assume $\lim_{z\to+\infty,z\in \partial\Omega}|f(z)|=0$. 

> [!Note]  Lemma
> Let $F:U\to V$ be a conformal map. Let $u:U\to \mathbb{R}$ be a $C^2$ function. Then, $u$ is harmonic if and only if $u\circ F$ is harmonic on $U$.

### 1.4.1 Proof of the Lemma

Assume $u$ is harmonic. Let $z_0\in U$ and $w_0=F(z_0)$. There exist discs $D_r(z_0)$, $D_R(w_0)$ with $\overline{D_R(w_0)}\subset V$, $D_r(z_0)\subset U$, and $F(D_r(z_0))\subset D_R(w_0)$.

Since $D_R(w_0)$ is simply connected, there exists a holomorphic function $h:D_R(w_0)\to \mathbb{C}$ such that $u=\mathrm{Re}\,h$. Then $h\circ F$ is holomorphic on $D_r(z_0)$ and $u\circ F=\mathrm{Re}(h\circ F)$, so it is harmonic.

The converse follows by noting that $u=(u\circ F)\circ F^{-1}$.

### 1.4.2
We use conformal map to transform $\Omega$ ot $\mathbb{D}$.
$F(w)= \frac{1}{\pi}\log\left( \frac{1-w}{1+w}i \right)$, $G(z)= \frac{i-e^{\pi z}}{i+e^{\pi z}}$ 
$F:\mathbb{D}\to\Omega$. $G:\Omega \to \mathbb{D}$
![[Pasted image 20251117134919.png]]
$(F\circ G)(z)=z,\:(G\circ F)(w)=w$
Boundary behaviour
We set $L_{1}=\{z=x+iy|y=1\}$
$L_{0}=\{z=x+iy|y=0\}$
We can show that
$G(L_{1})$ is the lower half-circle
$G(L_{2})$ is the upper half-circle
We observe that, $G(\partial\Omega)\neq \mathbb{D}$​. There are two points missing, -1 and 1.
However, since $f(z)\to0,\lvert z \rvert\to0$
We see that $f\circ F:\begin{cases}\partial \mathbb{D}-\{-1,1\}\to \mathbb{R} \\ w\to f(F(w))\end{cases}$ extends to a contionuous function $g$ on $\partial \mathbb{D}$, by assigning $g(1)=0$ and $g(-1)=0$
Now we can solve the following Dirichlet problem in V
$$
\left\{\begin{array}{l}
\Delta V=0 \quad \text { in } \mathbb{D} \\
\left.V\right|_{\partial \mathbb{D}}=g
\end{array}\right.
$$
Such a solution exsists by convoluting with Poison Kernal Now we set $U=V \circ G$. Then $U$ is the solution of the initial Dirichlet Problem in $\Omega$

# 2. 扩张复平面上的共形映射

## 2.1 扩充复平面上共形映射的严谨定义
 
**定义A（基于亚纯性和无穷远点分析）**  
设 $f: \widehat{\mathbb{C}} \to \widehat{\mathbb{C}}$ 是一个双射。我们称 $f$ 为一个**共形映射**（或称**双全纯映射**），如果它满足以下条件：

1. **在有限复平面 $\mathbb{C}$ 上**：限制 $f|_{\mathbb{C}}: \mathbb{C} \setminus f^{-1}(\{\infty\}) \to \mathbb{C}$ 是一个**亚纯函数**。也就是说，它在 $\mathbb{C}$ 上除了一些孤立的点（这些点是 $f$ 的极点，被映射到 $\infty$）外是全纯的。

2. **在无穷远点 $\infty$ 处**：通过坐标变换来检验其全纯性：
    - 若 $f(\infty) = \infty$，则要求函数 $g(z) := f(1/z)$ 在 $z=0$ 处有**极点**
    - 若 $f(\infty) = a \in \mathbb{C}$，则要求函数 $g(z) := f(1/z)$ 在 $z=0$ 处是**全纯的**，且 $g(0)=a$。

**定义B（黎曼球面观点，更本质且优雅）**  
将 $\widehat{\mathbb{C}}$ 视为**黎曼球面**（一个一维复流形）。那么，一个映射 $f: \widehat{\mathbb{C}} \to \widehat{\mathbb{C}}$ 是一个**共形映射**，当且仅当它是黎曼球面到自身的一个**双全纯自同构**。  
具体来说，这要求存在两个复坐标卡覆盖 $\widehat{\mathbb{C}}$（例如，$U_1 = \mathbb{C}$ 与坐标 $z$， $U_2 = \widehat{\mathbb{C}} \setminus \{0\}$ 与坐标 $w = 1/z$），使得 $f$ 在每一个坐标卡下的表示都是全纯函数，并且其逆映射也是全纯的。

## 2.2 核心结论：分类定理
一个基本且重要的定理是：  
**任何扩充复平面 $\widehat{\mathbb{C}}$ 到自身的共形映射（即双全纯自同构），必为分式线性变换（Möbius变换）**，即具有形式：
$$
f(z) = \frac{az + b}{cz + d}, \quad a,b,c,d \in \mathbb{C}, \quad ad - bc \neq 0
$$
其中，约定 $f(-d/c) = \infty$ 且 $f(\infty) = a/c$（若 $c=0$，则 $f(\infty)=\infty$）。

这个结论与 **“在 $\mathbb{C}$ 上亚纯且在 $\infty$ 处至多有极点的函数必为有理函数”** 的定理（[[复分析07 Meromorphic function#3. Characterization of Rational Functions]]）一脉相承。分式线性变换正是满足这些条件的最简单的非平凡双射有理函数。
