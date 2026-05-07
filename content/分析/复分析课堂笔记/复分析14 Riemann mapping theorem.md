---
tags:
  - 复分析
  - 分析
---
# 1. Riemann Mapping Theorem

>[!Theorem]
>If $\Omega \subset \mathbb{C}$, $\Omega\neq \mathbb{C}$, $\Omega\neq \emptyset$, and $\Omega$ is simply connected, then $\Omega$ is conformally equivalent to $\mathbb{D}$.

The proof proceeds in four main steps.

## 1.1 Step 1: Mapping $\Omega$ into $\mathbb{D}$

We construct a conformal map sending $\Omega$ to a subset of $\mathbb{D}$. Hence, we may assume $\Omega \subset \mathbb{D}$.

### 1.1.1 Proof Process
Since $\Omega\neq \mathbb{C}$, there exists some $\alpha\in \mathbb{C}-\Omega$.
Consider the function $z\to z-\alpha$. It is never zero on $\Omega$. Since $\Omega$ is simply connected, we can define $f(z)=\log(z-\alpha)$ on $\Omega$. That is, $f:\Omega \to \mathbb{C}$ is holomorphic and $e^{f(z)}=z-\alpha$ for all $z\in\Omega$.

We will show that $\mathbb{C}-f(\Omega)$ contains a closed disc centered at some point $z_{0}$ of radius $r_{0}$. Then, $z\to \frac{r_{0}}{f(z)-z_{0}}$ sends $\Omega$ into $\mathbb{D}$.

- Firstly, $f$ is conformal from $\Omega$ to $f(\Omega)$.
  Indeed, $f$ is injective. If $f(z_{2})=f(z_{1})$ for $z_{1},z_{2}\in\Omega$, then $z_{1}=e^{f(z_{1})}+\alpha=e^{f(z_{2})}+\alpha=z_{2}$. This proves that $f$ is injective.
  Now, $f:\Omega \to f(\Omega)$ is bijective. Moreover, $f:\Omega \to\mathbb{C}$ is holomorphic. By the open mapping theorem, $f(\Omega)$ is an open subset in $\mathbb{C}$. Thus $f:\Omega \to f(\Omega)$ is conformal.

%%从几何上看, 区域被映射成为了条状的, 长度为2\pi i, 所以能很容易找到一个点在区域外, 并且整个以该点为中心的圆盘都在区域外, 这样取一个倒数就可以转换到圆盘内%%
- Secondly, we claim that $\mathbb{C}-f(\Omega)$ contains a closed disc centered at $f(w)+2\pi i$ with some radius $r>0$, where $w\in\Omega$ is a point. We argue by contradiction.
  Fix $w\in\Omega$. If the assertion does not hold, then for any $n\in \mathbb{N}$, there is some $z_{n}\in\Omega$ such that $\displaystyle \left| f(z_{n})-(f(w)+2\pi i) \right|\leq \frac{1}{n}\iff f(z_{n})\in \overline{D_{\frac{1}{n}}(f(w)+2\pi i)}$.
  Thus, the sequence $\{f(z_{n})\}_{n\in N}$ converges to $f(w)+2\pi i$. 
  
  %%核心在于这个条件下z logz 是对应的, 单射, 连续性保证极限%%
  - **Contradiction**: Since the exponential map is continuous, the sequence $\{e^{f(z_{n})}\}$ converges to $e^{f(w)+2\pi i}=e^{f(w)}=w-\alpha$. We obtain that $z_{n}\to w,n\to \infty$. Since $f$ is continuous, we obtain that $f(z_{n})\to f(w)$. This is a contradiction since $f(w)\neq f(w)+2\pi i$. This proves that $\exists r>0$ s.t. $\overline{D_{r}(f(w)+2\pi i)}\subset \mathbb{C}-f(\Omega)$.

- We consider $\displaystyle F(z)= \frac{r}{f(z)-(f(w)+2\pi i)}$ on $\Omega$. Then $F$ is holomorphic, injective and $\lvert F(z) \rvert<1$ on $\Omega$.
  As before, we obtain that $F$ is conformal from $\Omega$ to $F(\Omega)$ and $F(\Omega)\subset \mathbb{D}$.

## 1.2 Step 2: Ensuring $0 \in \Omega$

We can translate $\Omega$ so that $0\in\Omega$. We consider all holomorphic functions $f:\Omega \to \mathbb{D}$ with $f(0)=0$.
![[Pasted image 20251126140651.png]]
Let $z_{0}\in F(\Omega)$. Let $d=1$. We consider the scaling $z\to \frac{1}{2}z$. Then we consider $g:z\to \frac{1}{2}(z-z_{0})$.
We claim that $g(F(\Omega))\subset \mathbb{D}$. $\left| g(z) \right|= \frac{1}{2}\left| z-z_{0} \right|\leq \frac{1}{2}(\left| z \right|+\left| z_{0} \right|)<1$.
And $g(z_{0})=0$.
Hence for $z_{0}\in\Omega$, we have the result.

So, we can assume $0\in\Omega \subset\mathbb{D}$ 
## 1.3 Step 3: The Function Family and Extremal Function

We consider the following family of functions on $\Omega$.
$$
\mathcal{F}=\{f:\Omega \to \mathbb{D}\text{ holomorphic s.t. }f\text{ is injective and }f(0)=0\}
$$
We will search for a conformal map from $\Omega$ to $\mathbb{D}$ inside this family.
%%根据第二步, 这个集合不是空集%%
For such a function, we consider $\displaystyle \sup_{f\in \mathcal{F}}\left| f'(0) \right|\in \mathbb{R}_{+}\cup \{+\infty\}$.
By definition, there is a sequence of functions $\{f_{n}\}$ inside $\mathcal{F}$ such that $\left| f_{n}'(0) \right|\to \sup_{f\in \mathcal{F}}\left| f_{n}'(0) \right|$.
%%可以取点的极限让它满足上式,得到一个对应的函数序列, 这个函数序列是正规族(因为定义值域在圆盘当中, 所以可以紧集一致收敛到函数h%%
From Montel's theorem, $\mathcal{F}$ is a normal family. (If $f\in \mathcal{F}$ then $\sup_{z\in\Omega}\left| f(z) \right|\leq1$.)
Thus there is a subsequence of $\{f_{n}\}$ which converges to a limit $h$, uniformly on every compact subset of $\Omega$. Then $h:\Omega \to \mathbb{C}$.
We replace $\{f_{n}\}$ by this subsequence, we may assume that the subsequence converges to $h$.
Then, since $\sup_{z\in\Omega}\left| f_{n}(z) \right|\leq1$ for all $n$, we get $\sup_{z\in\Omega}\left| h(z) \right|\leq1$.
By the maximum principle, we get $h(\Omega)\subset \mathbb{D}$. 
(Or by the open mapping theorem, $h(\Omega)$ is an open subset of $\overline{\mathbb{D}}$. Thus $h(\Omega)\subset \text{interior of } \overline{\mathbb{D}}=\mathbb{D}$.)
Since $f_{n}(0)=0$, we have $h(0)=0$.
Furthermore, we have $\{f_{n}'\}$ converges to $h'$ uniformly on any compact subset of $\Omega$.
In particular, $f_{n}'(0)\to h'(0),n\to \infty$.
Thus $\displaystyle \sup_{f\in \mathcal{F}}\left| f'(0) \right|=\left| h'(0)\right|$. We note that the identity $z\to z$ is contained in $\mathcal{F}$ .Thus , $\sup_{f\in \mathcal{F}}\left| f'(0) \right|\geq1>0$. Hence $\left| h'(0) \right|>0$.
In particular, $h$ is not constant.==By the proposition about Montel's theorem, $h$ is injective, since each $f_{n}$ is injective.== %%还没有验证%% 
In conclusion $h\in \mathcal{F}$
($h:\Omega \to \mathbb{D}$ holomorphic, $h$ injective, $h(0)=0$ and $\left| h'(0) \right|=\sup_{f\in \mathcal{F}}\left| f'(0) \right|$).

## 1.4 Step 4: Showing $h(\Omega) = \mathbb{D}$

We will show that $h(\Omega)=\mathbb{D}$. That is, $h:\Omega \to \mathbb{D}$ is conformal. This will complete the proof of the Riemann mapping theorem. Assume by contradiction that $h(\Omega)\neq \mathbb{D}$. Then $\exists\alpha\in \mathbb{D}-h(\Omega)$.
We consider the conformal map
$$
\psi_{\alpha}:\begin{cases}
\mathbb{D}\to \mathbb{D} \\
z\to \frac{\alpha-z}{1-\bar{\alpha}z}
\end{cases}
$$
which interchanges $0$ and $\alpha$.
We have $\psi_{\alpha}(0)=\alpha$, $\psi_{\alpha}(\alpha)=0$ and $(\psi_{\alpha}\circ \psi_{\alpha})(z)=z$. We consider $\psi_{\alpha}\circ h:\Omega \to \mathbb{D}$, then $0\not\in(\psi_{\alpha}\circ h)(\Omega)$ is conformal. We set $U=(\psi_{\alpha}\circ h)(\Omega)$, which is simply connected. %%U单连通区域, 但不包括0%%
Hence there is a logarithm function on $U$, we denote one of them by $w\to \log w$. We consider $g:\begin{cases} U\to \mathbb{C} \\ w\to e^{\frac{1}{2}\log w}\end{cases}$. ==这样定义函数是良定义的吗==
It is a square-root function on $U$. That is $(g(w))^{2}=w$.
$g$ is holomorphic, and we see that $g(U)\subset \mathbb{D}$.
Note that, $g$ ==is also injective== on $U$. We consider the following function
$$
H=\psi_{g(\alpha)}\circ g\circ \psi_{\alpha}\circ h
$$
Then $H:\Omega \to \mathbb{D}$ is holomorphic and injective. $H(0)=0$
Let $\rho(z)=z^{2}$ be the square function.
Then $(\rho \circ g)(w)=(g(w))^{2}=w$. We consider
$$
\psi_{\alpha}\circ \rho\circ \psi_{g(\alpha)}\circ H=\psi_{\alpha}\circ \rho\circ (\psi_{g(\alpha)}\circ \psi_{g(\alpha)})\circ g\circ \psi_{\alpha}\circ h=(\psi_{\alpha}\circ\psi_{\alpha})\circ h=h
$$
That is $h=\Phi\circ H$ with $\Phi=\psi_{\alpha}\circ \rho\circ \psi_{g(\alpha)}$.
$\Phi:\mathbb{D}\to \mathbb{D}$ is holomorphic, $\Phi(0)=0$ and $\Phi$ is 1-to-1.
Hence, by the Schwarz Lemma $\left| \Phi'(0) \right|<1$.
Thus, $\left| h'(0) \right|=\left| \Phi'(H(0))H'(0) \right|=\left| \Phi'(0) \right|\cdot \left| H'(0) \right|<\left| H'(0) \right|$.
This is a contradiction, since $H \in \mathcal{F}$ and $\left| h'(0) \right|=\sup_{f\in \mathcal{F}}\left| f'(0) \right|$. This completes the proof.
==这里平方根函数起到了什么作用==
