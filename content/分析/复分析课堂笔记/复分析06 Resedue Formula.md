---
tags:
  - 复分析
  - 分析
---
#复分析 #课堂笔记 
# 1. Residue Formula

## 1.1 Residue at a Pole

>[! Theorem]
>Assume f has a pole of order n of $z_{0}$
>Then $a_{-1}= \frac{1}{(n-1)!}\left( \frac{d}{dz} \right)^{n-1}((z-z_{0})^{n}f(z))$

Proof: exercise

**Definition** $a_{-1}$ is called the **residue** of f at $z_{0}$, we denote $a_{-1}=\text{res}_{z_{0}}f$

>[! Theorem]
>$f: \Omega -\{z_{0}\}\to \mathbb{C}$ is holomorphic with a pole at $z_{0}$
>Assume that the disc $\bar{D}$ containing $z_{0}$ is contained in $\Omega$. Let $C=\partial \bar{D}$ Then
>$$
>\text{res}_{z_{0}}f= \frac{1}{2\pi i}\int_{C}f
>$$

### 1.1.1 Proof of Residue Formula

We consider the keyhole contours $C_{\eta,\epsilon}$. f is holomorphic in a neighbourhood of $C_{\eta,\varepsilon}$ and its interior. Thus, $\int_{C_{\eta,\varepsilon}}f=0$

$\eta \to0\implies \int_{C}f=\int_{C_{\varepsilon}}f$

Here $C_{\varepsilon}$ is the circle centered at $z_{0}$ with radius $\varepsilon$

By choosing $\varepsilon>0$ small, we can assume that
$$
f(z)= \left( \frac{a_{-n}}{(z-z_{0})^{n}}+\dots+\frac{a_{-1}}{z-z_{0}} \right)+G(z)
$$
for z in a disc containing $C_{\varepsilon}$ and its interior
here G is holomorphic

Then
$$
\int_{C_{\varepsilon}}f=\int_{C_{\varepsilon}}\left(  \frac{a_{-n}}{(z-z_{0})^{n}}+\dots+\frac{a_{-1}}{z-z_{0}} \right)+\int_{C_{\varepsilon}}G(z)=\int_{C_{\varepsilon}}\left(  \frac{a_{-n}}{(z-z_{0})^{n}}+\dots+\frac{a_{-2}}{(z-z_{0})^{2}}\right)+\int_{C_{\varepsilon}} \frac{a_{-1}}{z-z_{0}} 
$$

We remark that, for $i=2,\dots,n$
$$
\frac{d}{dz}\left( -\frac{1}{i-1}\cdot \frac{a_{-i}}{(z-z_{0})^{i-1}} \right)= \frac{a_{-i}}{(z-z_{0})^{i}}
$$

This implies that
$$
\int_{C_{\varepsilon}}\left(  \frac{a_{-n}}{(z-z_{0})^{n}}+\dots+ \frac{a_{-2}}{(z-z_{0})^{2}} \right)dz=0
$$

Hence 
$$
\int_{C}f=\int_{C_{\varepsilon}}f=\int_{C_{\varepsilon}} \frac{a_{-1}}{z-z_{0}}dz
$$

By Cauchy formula, we have $a_{-1}=\frac{1}{2\pi i}\int_{C}f$

## 1.2 Residue Formula for Multiple Poles

**Corollary** (Residue formula for more poles)
Suppose that $f$ is holomorphic in an open set containing a circle $C$ and its interior, except for poles at the points $z_1, \ldots, z_N$ inside $C$. Then
$$\begin{align*}
\int_C f(z) \, dz = 2\pi i \sum_{k=1}^N \text{res}_{z_k} f.
\end{align*}$$

Proof: We adapt the proof of multiple keyhole
![[Pasted image 20251027152349.png|300]]
**Remark** Compact residue formula and Cauchy's integral formula
Cauchy's formula $f(z_{0})= \frac{1}{2\pi i}\int_{C} \frac{f(\xi)}{\xi-z_{0}}d\xi$ 
If $g(\zeta)= \frac{f(\zeta)}{\zeta-z_{0}}$, then it has at most one pole which is $z_{0}$

## 1.3 Example: Integral of 1/(x²+1)

$$
\int_{-\infty}^{+\infty} \frac{dx}{x^{2}+1}  =\pi
$$

We set $f(z)= \frac{1}{z^{2}+1} = \frac{1}{(z-i)(z+i)}$

We consider $\gamma_{R}$ as follows
![[Pasted image 20251027141126.png|400]]

We see that the residue of $f$ at $i$ is simply $1/2i$. Therefore, if $R$ is large enough, we have
$$\begin{align*}
\int_{\gamma_R} f(z) \, dz = \frac{2\pi i}{2i} = \pi.
\end{align*}$$

If we denote by $C_{R}^{+}$ the large half-circle of radius $R$, we see that
$$
|\int_{C_{R}^{+}}f(z)dz| \leq \int \left|  \frac{1}{z^{2}+1} \right|dz\leq \int_{C_{R}^{+} } \frac{2}{R^{2}}dz= \pi R\cdot \frac{2}{R^{2}}\to0,\text{when }R\to\infty
$$

Thus $\int_{-\infty}^{+\infty} \frac{1}{x^{2}+1}  dx = \pi$

# 2. Meromorphic Functions and Singularities

## 2.1 Types of Singularities

Assume $f:\Omega-\{z_{0}\}\to \mathbb{C}$ is holomorphic, when $z_{0}\in\Omega$
We call $z_{0}$ a **singularity** of f

**Definition**: If there is a holomorphic function $\bar{f}:\Omega \to \mathbb{C}$ s.t. $f=\bar{f} |_{\Omega-\{z_{0}\}}$ then we say that $z_{0}$ is a **removable singularity** of f
In this case, we say that f extends to a holomorphic function on $\Omega$

## 2.2 Riemann's Theorem on Removable Singularities

>[! Theorem]
>Let $f:\Omega  -\{z_{0}\}\to \mathbb{C}$ be a holomorphic function
>Assume that f is locally bounded around $z_{0}$. Then $z_{0}$ is a removable singularity

>[!Lemma: the derivative of an integral with parameters]
>Let $C$ be a simple closed curve. Let $K(z,\zeta)$ is holomorphic on $\Omega$, for every $\zeta\in C$. If $K(z,\zeta)$ is continuous on $(\Omega,C)$, we have

$$
\frac{\partial}{\partial z}\int_{C}K(z,\zeta)d\zeta=\int_{C} \frac{\partial K}{\partial z}(z,\zeta)d\zeta 
$$



**Remark**: f is locally bounded around $z_{0}$ $\longleftrightarrow$ exists punctured disc $D-\{z_{0}\}$ centered at $z_{0}$, such that $\Vert{f}\Vert_{D-\{z_{0}\}}$ is bounded function
($\longleftrightarrow \exists A>0,\:s.t. \: \sup_{z\in D-\{z_{0}\}}\lvert f(z) \rvert\leq A$)

### 2.2.1 Proof of Riemann's Th​eorem
We consider the contours $C_{\eta,\varepsilon}$
![[Pasted image 20251027152438.png|400]]
Let $\bar{D}$ be a disc containing $z_{0}$ and contained in $\Omega$
Let $C=\partial \bar{D}$. We only need to prove that $f$ extends to a holomorphic function on D.

We set
$$
g(z)= \frac{1}{2\pi i}\int_{C} \frac{f(\zeta)}{\zeta-z}d\zeta
$$
for $z\in D$

Then, g is a holomorphic function on D, since $\frac{d}{d\zeta} \frac{f(\zeta)}{\zeta-z}$ are uniformly integrable for z contained in any closed disc inside D

Next, we will show that
$g(z)=f(z)$ for $z\in D-\{z_{0}\}$
This will imply the theorem

Fix any $z\in D-\{z_{0}\}$ we consider the contours $C_{\eta,\varepsilon}$
Since $\zeta\to \frac{f(\zeta)}{\zeta-z}$ is holomorphic in $\Omega-\{z_{0},z\}$ we deduce that $\int_{C_{\eta,\varepsilon}} \frac{f(\zeta)}{\zeta-z}d\zeta=0$

Let $\gamma_{\varepsilon}= \partial D_{\varepsilon}(z)=C_{\varepsilon}(z)$
$\gamma_{\varepsilon}' = \partial D_{\varepsilon}(z_{0})=\partial C_{\varepsilon}(z_{0})$

Let $\eta$ tend to 0, then we get
$$
\int_{C} \frac{f(\zeta)}{\zeta-z}d\zeta =\int_{\gamma_{\varepsilon}} \frac{f(\zeta)}{\zeta-z}d\zeta+\int_{\gamma_{\varepsilon}'} \frac{f(\zeta)}{\zeta-z}d\zeta
$$

Note that f is holomorphic on $D-\{z_{0}\}$
Thus, $\int_{\gamma_{\varepsilon}} \frac{f(\zeta)d\zeta}{\zeta-z}= 2\pi if(z)$ by Cauchy's Formula

Thus 
$$
g(z)= \frac{1}{2\pi i} \int_{C} \frac{f(\zeta)}{\zeta-z}d\zeta=f(z) + \frac{1}{2\pi i} \int_{\gamma_{\varepsilon}'} \frac{f(\zeta)}{\zeta-z}d\zeta
$$

In the next step, we will tend $\varepsilon$ to 0
By assumption, f is locally bounded around $z_{0}$
Then, $\exists M>0$ s.t.
$$
0\leq \left\lvert  \int_{\gamma_{\varepsilon}'}\frac{f(\zeta)}{\zeta-z} d\zeta \right\rvert \leq \int_{\gamma_{\varepsilon}'} \left\lvert  \frac{f(\zeta)}{\zeta-z}  \right\rvert d\zeta\leq \int_{\gamma_{\varepsilon}'}Md\zeta=2\pi\varepsilon M
$$
*这里放缩有一点点问题, 但不影响结论*
Thus, $\int_{\gamma_{\varepsilon}'} \frac{f(\zeta)}{\zeta-z}d\zeta \to 0,\:\text{when}\: \varepsilon \to0$
Hence, $g(z)=f(z)$ for all $z\in D-\{z_{0}\}$

## 2.3 Characterization of Poles

**Corollary**: Assume that $f:\Omega-\{z_{0}\}\to \mathbb{C}$ is holomorphic. Then f has a pole at $z_{0}$ with order at least 1, if and only if
$$
\lim_{z\to z_{0}} \lvert f(z) \rvert \to +\infty
$$

### 2.3.1 Proof

1. Assume that f has a pole at $z_{0}$
then $\lim_{z\to z_{0}} \left\lvert  \frac{1}{f(z)}  \right\rvert=0$
Thus $\lim_{z\to z_{0}}\lvert f(z) \rvert=+\infty$

2. Assume that $\lim_{z\to z_{0}}\lvert f(z) \rvert=+\infty$	
Then $f(z )\neq0$ for z in a punctured disc $D-z_{0}$ centered at $z_{0}$
Thus $\frac{1}{f}$ is holomorphic on $D-\{z_{0}\}$
Moreover $\lim_{z\to z_{0}}\left\lvert   \frac{1}{f(z)}  \right\rvert=0$
In particular, $\frac{1}{f}$ is locally bounded near $z_{0}$. By Riemann's theorem, $\frac{1}{f}$ extends to a holomorphic function g on D. Moreover, we see that $g(z_{0})=0$ since g is continuous,
Hence f has a pole at $z_{0}$

## 2.4 Classification of Singularities

**Notation**. $f:\Omega-\{z_{0}\}\to \mathbb{C}$, a holomorphic function. We say that $z_{0}$ is 
1. a **removable singularity** if f is locally bounded around $z_{0}$
2. a **pole** if $\lim_{z\to z_{0}} \lvert f(z) \rvert=+\infty$	
3. an **essential singularity** otherwise
![[Pasted image 20251027152108.png|400]]
## 2.5 Casorati-Weierstrass Theorem

>[! Theorem] 本性奇点充要条件
>Suppose $f$ is holomorphic in the punctured disc $D_r(z_0) - \{z_0\}$ and has an essential singularity at $z_0$. Then, the image of $D_r(z_0) - \{z_0\}$ under $f$ is dense in the complex plane​	 $\mathbb{C}$.

Proof. Assume by contradiction that $A=D_{r}(z_{0})-\{z_{0}\}$ is not dense in $\mathbb{C}$
Then, $\exists w\in \mathbb{C}, and \exists\delta>0, s.t. \:A\cap D_{_{\delta}}(w)=\emptyset$
We now consider the function
$$
g(z)= \frac{1}{f(z)-w}
$$
for $a\in D_{r}(z_{0})-\{z_{0}\}$
By assumption, $\lvert f(z)-w \rvert\geq\delta$

Hence $\lvert g(z) \rvert\leq \frac{1}{\delta}$ for all $z\in D_{r}(z_{0})$
Hence, by Riemann's removable singularity theorem, g has a removable singularity at $z_{0}$​	
Hence g extends to $\bar{g}:D_{r}(z_{0})\to \mathbb{C}$ which is holomorphic
Then $f(z)-w= \frac{1}{g(t)}$ has either a pole $(\bar{g}(z_{0})=0)$ or a removable singularity $(\bar{g}(z_{0}))\neq0$​	at $z_{0}$
Thus, f has either a polo or a removable singularity at $z_{0}$​	
​​This is a contradiction 

>[!example] 非多项式的整函数$\infty$点性质(本性奇点)
>Let $f(z)$ be an entire function which is not a polynomial. Show that for every $c \in \mathbb{C}$ there exists a complex sequence $\left\{z_n\right\}$ with $z_n \rightarrow \infty$ such that $f\left(z_n\right) \rightarrow c$.

**证明思路** 
首先, 我们知道, 扩充复平面上的亚纯函数是一个有理函数, 当且仅当$\infty$是一个可去奇点或者极点. 
对于$f(z)$是$\mathbb{C}$上的整函数, 且不是多项式, 我们得到$\infty$是$f(z)$的本性奇点. 否则$f(z)$是一个有理函数, 进而由于全纯性是一个多项式.​	
设$g(z)=f\left( \frac{1}{z} \right)$, 我们得到$z=0$是$g(z)$的本性奇点. 根据Casorati-Weirestrass定理, 对于任意小的去心圆$D_{r}(0)$, $g(D_{r}(0))$是$\mathbb{C}$的稠密子集, 因此可以选取$w_{n}\in D_{\frac{1}{n}}(0)$使得$\left| g(w_{n})-c \right|<\frac{1}{n}$. $w_{n}$满足$\lim_{n\to\infty}w_{n}=0$. 我们令$z_{n}=\frac{1}{w_{n}},\lim_{n\to\infty}z_{n}=\infty$, 满足$f(z_{n})\to c$.