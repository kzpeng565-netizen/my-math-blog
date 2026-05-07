---
tags:
  - 复分析
  - 分析
---
全纯函数可以有非孤立的奇点
例如$\frac{1}{\sin z}$​	在$\infty$的极点不是孤立的, 因为$z=k\pi$都是奇点
$\log z$没有孤立奇点

# 1. Meromorphic Functions

## 1.1 Definition of Meromorphic Function

**Definition** (Meromorphic function)
Let $\Omega \subset \mathbb{C}$ be an open subset. We say that f is **meromorphic function** on $\Omega$ if $\exists$ a sequence $\{z_{1},z_{2},\dots\}$ of points in $\Omega$ without accumulation point inside $\Omega$ such that f is a **holomorphic function** on $\Omega-\{z_{1},\dots\}$ and f has a **pole** or a **removable singularity** at each $z_{i}$.

## 1.2 Properties and Remarks

**Remark**
1. Sometimes, we pick $\{z_{1},\dots\}$ so that f has a pole at each $z_{i}$
2. Recall that, a point $l\in \mathbb{C}$ is an **accumulation point** of $z_{1},\dots$, if for any $\varepsilon>0$, for any N>0, $\exists$ integer $k\geq N,$ s.t. $z_{k}\in D_{\varepsilon}(l)-\{l\}$
3. We compare this definition with the theorem saying that zeros of a holomorphic function do not have accumulation point, unless the function is constant
4. In the definition, we see that if f is meromorphic, then it has at most countable poles
   Indeed, if $\Lambda \subset\Omega$ is subset with uncountably many points, then we can choose a sequence of distinct points in $\Lambda$, which converges to a limit in $\Omega$
5. Let f be a meromorphic function on $\Omega$, with poles $\{z_{1},z_{2},\dots\}=P$. Let $Z=\{z\in\Omega-P|f(z)=0\}$. Then f is holomorphic on $\Omega-P\cup Z$, which is an open of $\mathbb{C}$
   Assume $\Omega$ is connected, then $\Omega-P$ is again connected
   Then, by a theorem on zeros of holomorphic function, $Z$ does not have accumulation point. In particular, Z is at most countable
   We can consider $g=\frac{1}{f}$ over $\Omega-(P\cup Z)$. Then g is holomorphic on $\Omega-(P\cup Z)$. g has poles at points of Z. And g extends to a holomorphic function $\bar{g}$ on $\Omega-Z$, s.t. $\bar{g}(z)=0$ for any $z\in P$

With the view-point of 5, if f is meromorphic, we can consider $\frac{1}{f}$ is meromorphic
We also note that holomorphic functions are meromorphic
Thus if f is holomorphic, and f is not constantly zero on every connected component of $\Omega$, then $\frac{1}{f}$ can be considered as a meromorphic function
By introducing meromorphic functions, we can consider divisions by holomorphic functions

# 2. Riemann Sphere and Extended Complex Plane

## 2.1 Definition and Topology

**Definition** (Riemann Sphere and extended complex plane)
We consider a symbol $\infty$. The **extended complex plane** (or the **Riemann sphere**) is equal to the set $\mathbb{C}\cup \{\infty\}$
We denote it as $\mathbb{S}$ or $\mathbb{P}$
We define the topology on $\mathbb{S}$ as follows
A subset $F\subset \mathbb{S}$ is closed if and only if
1. either $F\subset \mathbb{C}$ and $F$ is compact
2. or $F=F'\cup \{\infty\}$, where $F'\subset \mathbb{C}$ is closed subset
In particular, $\mathbb{S}$ is compact

To visualize $\mathbb{S}$, we have the following property:
a sequence $\{z_{1},\dots\}$ of points in $\mathbb{C}$ converges to $\infty$ inside $\mathbb{S}$ if and only if $\lim_{i\to+\infty}\lvert z_{i} \rvert=+\infty$

We consider
$$
f:
\begin{cases}
 &  \mathbb{S}\to \mathbb{S} \\
 & z\in\mathbb{C}-\{0\}\to \frac{1}{z}\in\mathbb{C}-\{0\} \\
 & 0\to \infty \\
 & \infty \to0
\end{cases}
$$
Then f is continuous, bijective
$f|_{\mathbb{C}-\{0\}}$ is holomorphic, and has a pole at 0
So we may also consider $\frac{1}{0}=\infty$ for meromorphic functions (because the map is bijective and well-defined)

## 2.2 Meromorphic Functions on Riemann Sphere

**The definition of meromophic function on extended $\mathbb{C}$**
Now if f is meromorphic on $\Omega$, we can consider f as a function $f:\Omega \to \mathbb{S}$:
$$
f:
\begin{cases}
 \Omega \to \mathbb{S} \\
z\in\Omega-P \to f(z) &  \\
z\in P \to \infty 
\end{cases}
$$
where $P\subset\Omega$ is the set of poles of f

If $f:\Omega \to \mathbb{S}$ is meromorphic then $\frac{1}{f}$ is also meromorphic

Now if f is meromorphic on $\mathbb{C}$, we can view f as a meromorphic function on $\mathbb{S}-\{\infty\}$

**Definition of Singularity on $\infty$**
Let $g(z)=f\left(  \frac{1}{z} \right)$ for $z\neq 0$. Then we say that f has a **removable singularity** (respectively a **pole**, an **essential singularity**) at $\infty$ **if** g has removable singularity (respectively a pole, an essential singularity) at 0

# 3. Characterization of Rational Functions

>[! Theorem]
Assume that f is a meromorphic function on $\mathbb{C}$, such that f has pole or removable singularity at $\infty$
Then f is a **rational function**. That is, $\exists$ polynomials $P,Q$ with $Q\not\equiv 0$, s.t. $f=\frac{P}{Q}$

^22589f

## 3.1 Proof of the Theorem

### 3.1.1 Proof Idea
The first idea is connecting $f(z)$ with $g(z)=f\left( \frac{1}{z} \right)$, the key point is the singularity is one-to-one corresponding
The second idea is that, if the singularity is finite, we can minus every principal part of singularity to obtain a holomorphic function
The third ideas is Liouville's theorem, which is useful to handle with holomorphic function on $\mathbb{C}$​. By prove $F(z)=f(z)-g_{0}\left( \frac{1}{z}\right)-\sum_{k=1}^{n}f_{k}(z)$ is bounded, we complete the proof.

The proof uses the method of subtracting principal parts at finite poles and the behavior at infinity to construct a bounded entire function, which must be constant by Liouville's theorem ![[复分析02：Cauchy 积分公式的应用#^113820]]

### 3.1.2 Proof Process
We consider $g(z)=f(\frac{1}{z})$
By assumption, g is meromorphic on $\mathbb{C}$
Then the poles of g on $\mathbb{C}-\{0\}$ are one-to-one corresponding to the poles of f on $\mathbb{C}-\{0\}$​	​	​	*here we do not take $\infty$ into consideration*
Since poles of g do not have accumulation point, if g has infinitely many poles $z_{1},z_{2},\dots$ on $\mathbb{C}-\{0\}$, then $\lim_{i\to+\infty}\lvert z_i \rvert=+\infty$ since every $\overline{D_{R}}(0)$ is compact where $R>0$​	​	​	​	​	
*It means: if there are infinite singularities of g, then they must tend to infity, corresponding to tending to 0 of f, which contracdicts with f is meromorphic*
Thus the poles of g and f on $\mathbb{C}$ are finite

Assume that $p_{1},p_{2},\dots,p_{n}\in \mathbb{C}$ are the distinct poles of f
For each $p_k$, let $f_{k}$ be the **principal part** of f around $p_{k}$
Then 
$$
f_{k}(z)= \frac{a_{k,-m_{k}}}{(z-p_{k})^{m_{k}}}+\dots+ \frac{a_{k,-1}}{z-p_{k}}
$$
where $m_{k}\in \mathbb{Z}$, $a_{k,-m_{k}},\dots,a_{k,-1}\in \mathbb{C}$
It is a rational function. Moreover, $f-f_{k}$ is holomorphic around $p_{k}$

Now, we decompose $g$ around 0, $f\left( \frac{1}{z} \right)=g(z)$
We have
$$
g(z)=g_{0}(z)+h(z)
$$
where $g_{0}$ is the principal part if g has a pole at 0, and $g_{0}=0$ if g is holomorphic at 0, and h is holomorphic

We consider 
$$
F(z)=f(z)-g_{0}\left( \frac{1}{z}\right)-\sum_{k=1}^{n}f_{k}(z) 
$$
Note that $f_{\infty}(z)=g_{0}\left( \frac{1}{z} \right)$ is a polynomial. In particular, it is holomorphic on $\mathbb{C}$
F is holomorphic on $\mathbb{C}-\{p_{1},\dots,p_{n}\}$. Moreover, F is holomorphic around $p_{1},\dots,p_{n}$ by the definition of $f_{1},\dots,f_{n}$
Hence $F:\mathbb{C}\to \mathbb{C}$ is holomorphic

Next, we will show that F is bounded, and hence a constant by **Liouville's theorem**

To see this, we observe that
$$
\begin{align}
\lim_{|z|\to\infty} f_{k}(z) = 0 \\
\lim_{|z|\to\infty} \left( f(z)-g_{0}\left( \frac{1}{z} \right) \right) = \lim_{|z|\to0} \left( f\left( \frac{1}{z} \right)-g_{0}(z) \right) = \lim_{|z|\to 0} \left( g(z)-g_{0}(z) \right) = \lim_{|z|\to 0} h(z) = h(0)
\end{align}
$$
This proves that F is bounded on $\mathbb{C}$

Thus $F=C\in \mathbb{C}$ is constant
Hence $f(z)=f_{\infty}(z)+\sum_{k=1}^{n}f_{k}(z)+C$ is a rational function
$f_{\infty}$ is polynomial, $\sum f_{k}$ is rational, $C\in \mathbb{C}$

## 3.2 Discussion

**Remark**
>[!method of turn a meromorphic function to a holomorphic function]
In the proof, we use the following method
Every principal part is a meromorphic function on $\mathbb{C}$
Thus if f has finitely many poles $p_{1},\dots,p_{n}$ and $f_{1},\dots,f_{n}$ are the principal parts then 
>$$f-(f_{1}+\dots+f_{n})$$
>is holomorphic

# 4. Argument Principle

We know that every $z\in \mathbb{C}-\{0\}$ can be expressed as 
$$
z=\rho e^{i\theta}
$$
To extract $\theta$ we want to take "log"
Ideally, $\log z=\log \rho+ i \theta$
Unfortunately, log cannot be defined as a continuous function on $\mathbb{C}-\{0\}$ (consider $2\pi$ and 0)
On the other hand, we observe that log is a primitive of $x\to \frac{1}{x}$. Hence we may try to define log as a primitive of $\frac{1}{z}$ over certain domain
For example, for any $\bar{D}$ contained in $\mathbb{C}-\{0\}$, then $\frac{1}{z}$ is holomorphic around $\bar{D}$, and it has primitive by previous theorem

Note: use theorem4.5 for homework