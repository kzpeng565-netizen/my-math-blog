---
tags:
  - 复分析
  - 分析
---
#复分析 #课堂笔记
## 1.1 Runge's Theorem

>[!Theorem 5.7]
>Any function holomorphic in a neighborhood of a compact set $K$ (which means, $f:\Omega \to \mathbb{C},\Omega \supset K$) can be approximated uniformly on $K$ by rational functions whose singularities are in $K^c$.
>
>If $K^c$ is connected, any function holomorphic in a neighborhood of $K$ can be approximated uniformly on $K$ by polynomials.

^e9cedf

### 1.1.1 Remarks and Definitions

**Remark**: A **rational function** is $g(z)\sum_{i=1}^{n} a_{n}(z-z_{n})^{\alpha_{n}}$ for all $a\in \mathbb{C}-\{z_{1},\dots,z_{n}\}$, and $\alpha_1,\dots,\alpha_n \in \mathbb{Z}, a_{1},\dots,a_{n}\in \mathbb{C}$

**Example**: $f(z)= \frac{1}{z}+ \frac{1}{(z-2)^{2}}+ (z+1)^{2}$ is a rational function

**Remark**: If $h$ is a rational function, then $\exists$ polynomials $P,Q$ with $Q\neq0$ s.t. $h(z)= \frac{P(z)}{Q(z)}, \forall z\in \mathbb{C}, \: with \: Q(z)\neq0$

## 1.2 Key Lemma

>[!Lemma 4.8]
>With the same notation, there are paths $\gamma_1,\dots,\gamma_{N}$ such that $\gamma_n \subset \Omega-K$ and
>$$
>f(z)=\sum_{n=1}^{N} \int_{\gamma_{n}} \frac{f(\xi)}{\xi-z}d\xi
>$$

**The curve is fixed when $z\in K\subset\Omega$ 
### 1.2.1 Proof Idea and Construction

Recall Cauchy's integral formula:
$$
f(z)= \int_{C}\frac{f(\xi)}{\xi-z}d\xi
$$

In particular, if $\exists$ disc $D$ with $K\subset D\subset \bar{D}\subset\Omega$, then we can let $\gamma_{1}=C$ for this lemma. In general however such a $D$ does not exist, for example when $K$ is a line contained in $\Omega$.

**Proof Construction**:
We can divide $\mathbb{C}$ into a union of squares whose edges have length equal to 
$$
\inf_{x\in K,y\in\Omega^{c}} |x-y|
$$

![[Pasted image 20251022135303.png]]

Let $Q_{1},\dots,Q_{m}$ be the quares that intersect $K$. Then $\bar{Q_{1}},\dots,\bar{Q_{m}}\subset\Omega$ since the edges have length $\frac{1}{2}dist(K,\Omega^{c})$. Let $C_{1},\dots ,C_{m}$ be the boundary of $Q_{1},\dots,Q_{m}$. Then:
$$
\frac{1}{2\pi i}\int_{C_{i}} \frac{f(\xi)}{\xi-z}d\xi= 0 \quad \text{if } z\notin \bar{Q_{i}};\quad =f(z) \quad \text{if } z\in \bar{Q_{i}}
$$

### 1.2.2 Proof Process

Let $\gamma_{1},\dots,\gamma_{N}$ be the edges of $Q_{1},\dots,Q_{m}$ which only belong to one square of $Q_{1},\dots,Q_{m}$ (these represent the outermost edges of the selected squares).

Then:
$$
\int_{C_{1}}+\dots+\int_{C_{m}}=\int_{\gamma_1}+\dots+\int_{\gamma _{N}}
$$

Moreover, we notice that $\forall\gamma_{n},\: \gamma_{n}\cap K=\emptyset$.

Now, for any point $z\in K-(C_{1}\cup\dots \cup C_{m})$, we have:
$$
\begin{align}
f(z) &  = \frac{1}{2\pi i}\sum_{i=1}^{m}\int_{C_{i}} \frac{f(\xi)}{\xi-z}d\xi \\
 & =\frac{1}{2\pi i} \sum_{n=1}^{N} \int_{\gamma_{n}} \frac{f(\xi)}{\xi-z}d\xi
\end{align}
$$

## 1.3 Proof of Part 1 of Runge's Theorem

### 1.3.1 Approximation Strategy

We only need to approximate:
$$
\int_{\gamma_1} \frac{f(\xi)}{\xi-z}d\xi=g(z)
$$

Let $\gamma_{1}:[0,1]\to \mathbb{C}$ be a parametrization of the curve $\gamma$. Then:
$$
g(z)= \int_{0}^{1} \frac{f(\gamma_{1}(t))}{\gamma_{1}(t)-z}\gamma_{1}'(t)dt
$$

Let $F(z,t)= \frac{f(\gamma_1(t))}{\gamma_1(t)-z}\gamma_{1}'(t)$ for $(z,t)\in K\times[0,1]$. We write $g_{n}(z)=\sum_{i=0}^{n} \frac{1}{n}F\left( z, \frac{i}{n} \right)$
Next, we need to prove $g_{n}(z)\rightrightarrows g(z)$ as $n\to \infty$
$$
\begin{align}
  \lvert g(z)-g_{n} (z)\rvert =  &  \left\lvert  \sum _{i=0}^{n}\int_{\frac{i}{n}}^{\frac{i+1}{n}} F\left( z, \frac{i}{n} \right)-F(z,t) \, dt   \right\rvert  \\
\leq  & \sum_{i=0}^{n}\left\lvert  \int_{\frac{i}{n}}^{ \frac{i+1}{n} } F\left( z, \frac{i}{n} \right)-F(z,t) \, dt   \right\rvert  \\
\end{align}
$$​	Since singularity of $F(z,t)= \frac{f(\gamma_1(t))}{\gamma_1(t)-z}$ is out of $K$, so $F$​	is continuous on $K\times[0,1]$, and it's a compact set, so we have uniform continuity. $\forall\varepsilon>0,\: \exists\delta>0, \: s.t. \: \forall z\in K, \lvert F(z,t_{1})-F(z,t_{2}) \rvert<\varepsilon,\:when \:\lvert t_{1}-t_{2} \rvert<\delta$
$$
\lvert g(z)-g_{n}(z) \rvert \leq \sum_{i=0}^{n} \frac{\varepsilon}{n}=\varepsilon
$$
Hence we obtain the proof of part 1 of Runge's theorem.

## 1.4 Proof of Part 2 of Runge's Theorem

### 1.4.1 Reduction Strategy

Assume $\mathbb{C}-K$ is connected. By part 1, we only need to approximate functions of the shape $f(z)= \frac{1}{z-w}$ when $w\in \mathbb{C}$.

We discuss two cases. Since $K$ is compact, it is bounded. There is a disc $D$ centered at the origin such that $K\subset D$.
If $w\in \mathbb{C}-D$​	, $\frac{z}{w}\leq R<1$ , where $R= \sup_{z\in K} \frac{\lvert z \rvert}{\text{radius of }D}$
From the following lemma[[习题课2：一致收敛极限函数#^fd2a11]]​, since the convergence radiosu of $\frac{1}{1-\frac{z}{w}}$ is 1, $\frac{1}{z-w},z\in C-D$ can be approximated easily.

### 1.4.2 Case 1: $w\in \mathbb{C}-D$

Then $\frac{1}{z-w}= -\frac{1}{w}\cdot \frac{1}{1- \frac{z}{w}}$ for $z\in K$.

We notice that $\left| \frac{z}{w} \right|\leq R<1$ for some $R\in \mathbb{R}_{\geq0}$. Hence we have:
$$
\frac{1}{z-w}=- \frac{1}{w}\left( 1+ \frac{z}{w}+\dots+\left( \frac{z}{w} \right)^{n}+\dots \right)
$$

In other words, $- \frac{1}{w}\cdot \sum_{i=0}^{N}\left( \frac{z}{w} \right)^{i}$ converges uniformly to $\frac{1}{z-w}$ on $K$ when $N\to \infty$.

This proves Case 1.

### 1.4.3 Case 2: General Case

Let $w'$ be a point in $\mathbb{C}-D$. We link $w$ to $w'$ by a path contained in $\mathbb{C}-K$.

The idea is that we put points $w_{0}=w,w_{1},\dots,w_{k}=w'$ on $\gamma$ such that:
$$
\frac{1}{z-w_{j}} \text{ can be approximated by polynomials of } \frac{1}{z-w_{j+1}}
$$

Then step by step, we can approximate $\frac{1}{z-w}$ by polynomials in $\frac{1}{z-w'}$. The last polynomials can be approximated by polynomials by Case 1.

Let $\rho = \frac{1}{2}dist(K,\gamma)>0$. We choose $w_{0},\dots,w_{k}$ so that $|w_{j}-w_{j+1}|<\rho$.

Then:
$$
\frac{1}{z-w_{j}}= \frac{1}{(w_{j+1}-w_{j})+(z-w_{j+1})}= \frac{1}{z-w_{j+1}}\cdot \frac{1}{1- \frac{w_{j}-w_{j+1}}{z-w_{j+1}}}
$$

Notice that $|z-w_{j+1}|\geq dist(K,\gamma)=2\rho>2|w_{j}-w_{j+1}|$. Thus $\left|  \frac{w_{j}-w_{j+1}}{z-w_{j+1}} \right|< \frac{1}{2}$.

Hence:
$$
\frac{1}{z-w_{j}}= \sum_{i=0}^{\infty} \frac{(w_{j}-w_{j+1})^{i}}{(z-w_{j+1})^{i+1}}
$$

And the convergence of the right hand side is uniform on $K$.

This completes the proof.