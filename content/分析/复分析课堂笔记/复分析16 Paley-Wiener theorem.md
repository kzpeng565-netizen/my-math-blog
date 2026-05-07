---
tags:
  - 复分析
  - 分析
---

# 1. Paley-Wiener Theorem

## 1.1 Moderate Decrease Function

**Definition**: A function $f:\mathbb{R}\to \mathbb{C}$ is called **of moderate decrease** if $\exists A>0$, such that $\left| f(x) \right|\leq \frac{A}{1+x^{2}}$ for all $x\in \mathbb{R}$, and $f$ is continuous.

**Problem**: Assume $f$ and $\hat{f}$ are of moderate decrease, and Fourier inversion holds:
$$
\int_{-\infty}^{\infty} \hat{f}(\xi)e^{2\pi ix \xi} \, d\xi=f(x)
$$
**Question**: Can $f$ extend to some holomorphic function?

**Previous Result**: If $f$ extends to some holomorphic function on $S_{a}$ such that $f\in \mathcal{F}_{a}$, then $\hat{f}(\xi)\leq B e^{-2\pi a \left| \xi \right|}$. Thus it tends to zero faster than $\frac{A}{1+\left| \xi \right|^{2}}$ when $\left| \xi \right|\to +\infty$.

%%定理是之前观察的逆命题。之前提到，如果 $f$ 可以解析延拓到 $S_a$ 且满足一定增长条件，那么 $\hat{f}$ 具有指数衰减。这里反过来，由 $\hat{f}$ 的指数衰减推出 $f$ 的解析延拓。%%

## 1.2 Main Theorem: Paley-Wiener

>[!Paley-Wiener Theorem]
>Assume that $f:\mathbb{R}\to \mathbb{C}$ has moderate decrease, $f$ satisfies Fourier inversion and $\exists B>0, a>0$, such that $\left| \hat{f}(\xi) \right|\leq B e^{-2\pi a\left| \xi \right|}$.
>Then, $f$ extends to a holomorphic function $f$ on $S_{a}=\{z\in \mathbb{C}\mid \left| \mathrm{Im}(z) \right|<a \}$.

### 1.2.1 Proof of Paley-Wiener Theorem
$S_{a}=\bigcup_{0<b<a}S_{b}$.
Thus, we fix some $0<b<a$, and only need to prove that $f$ extends to a holomorphic function on $S_{b}$.
Here, we notice that the extension of $f$ is unique, by discreteness of zeros of holomorphic functions.%%因为如果实轴上相等, 在所有值都相等(刚性)%% 

Define $f_{n}(z)=\int_{-n}^{n} \hat{f}(\xi)e^{2\pi i\xi z} \, d\xi$ for any $n\in \mathbb{N}>0$ and $z\in S_{b}$.
%%形式地这么写, 在上一节的傅里叶变换当中是实数x, 这里取了一个带有小虚部的z%% **在这里$f_{n}(z)$是全纯函数**
We will show that $f_{n}(z)$ converges uniformly to $f(z)=\int_{-\infty}^{\infty} \hat{f}(\xi)e^{2\pi i z \xi} \, d\xi$ on $S_{b}$.

We note that, for $z\in S_{b}$ and $\xi\in \mathbb{R}$:
$$
\left| \hat{f}(\xi) e^{2\pi i z\xi}\right|\leq e^{-2\pi \left| \xi \right| a}\cdot e^{-2\pi \mathrm{Im}(z)\xi}\leq e^{-2\pi \left| \xi \right| a}e^{2\pi \left| \mathrm{Im}(z) \right| \cdot \left| \xi \right| }\leq e^{2\pi \left| \xi \right| (b-a)}
$$
Note that $b-a<0$.
The positive function $\xi \to e^{2\pi(b-a)\left| \xi \right|}$ is integrable on $\mathbb{R}$.
By the Dominated Convergence Theorem, we see that $f_{n}(z)$ converges uniformly to $f(z)$ on $z\in S_{b}$.
Since $f_{n}(z)$ is holomorphic on $z\in S_{b}$ (By Theorem 5.4 of Chapter 2),
It follows that $f(z)$ is holomorphic on $z\in S_{b}$.
By Fourier inversion, this function extends the original $f$.

# 2. Entire Functions of Exponential Type

## 2.1 Theorem 3.3: Entire Functions of Exponential Type

>[!Theorem 3.3]
>Let $f:\mathbb{R}\to \mathbb{C}$ be of moderate decrease. Then $f$ extends to an entire function (holomorphic on $\mathbb{C}$) with $f(z)\leq A\cdot e^{2\pi M\left| z \right|}$ for some $A, M>0$ and all $z\in \mathbb{C}$, **if and only if** $\hat{f}(\xi)=0$ for any $\left| \xi \right|>M$.

### 2.1.1 Proof (Forward Direction Started)
Assume that $\hat{f}(\xi)=0$ for $\left| \xi\right|>M$.
We set $f(z)=\int_{-\infty}^{\infty} \hat{f}(\xi)e^{2\pi i\xi z} \, d\xi=\int_{-M}^{M} \hat{f}(\xi)e^{2\pi i\xi z} \, d\xi$.

We have shown that $\hat{f}$ is supported in $[-M,M]\implies$f extends and $\left| f(z) \right|\leq e^{2\pi M\left| z \right|}$. We now prove that converse.

Assume that $\left| f(z) \right|\leq Ae^{2\pi M\left| z \right|}$ and will show that $\hat{f}(\xi)=0$ if $\left| \xi \right|>M$

Method:
We approximate f by various functions. We porve the property for the functions, and we use an argument of continuation to conclude.

### 2.1.2 Proof: Converse Direction (Step 1)
We first assume function that $\left| f(z) \right|\leq \frac{A'e^{2\pi M\left| \mathrm{Im}z \right|}}{1+\left| \mathrm{Re}z \right|^{2}}$ Here $A'>0$ is a constant.
We will show that $\hat{f}(\xi)=0$ if $\left| \xi \right|>M$
We have $\hat{f}(\xi)=\int_{-\infty}^{\infty} f(x)e^{-2\pi x\cdot \xi}dx$ We observe that, for any$a>0$ $f\in \mathcal{F}_{a}=\left\{ h:S_{a}\to \mathbb{C}\text{ holomorphic with }\left| h(z) \right|\leq \frac{A}{1+(\mathrm{Re}z)^{2}} \right\}$, where A is a positive constant.
We have seen that, for any $b<a$ for any $\xi>0$, we have
$$
\hat{f}(\xi)=\int_{-\infty}^{\infty} f(x)e^{-2\pi ix\xi}​	 \, dx=\int_{-\infty}^{\infty} f(x-ib)e^{-2\pi i(x-ib)\xi} \, dx
$$
%%这里是利用之前证明的性质, 沿着中间积分等于沿着-ib​积分, 如果\xi>0%%
Then $\left| \hat{f}(\xi) \right|\leq \int_{-\infty}^{\infty} \left| f(x-ib) \right|e^{-2\pi b\xi} \, dx\leq \int_{-\infty}^{\infty}  \frac{A'e^{2\pi Mb}}{1+x^{2}}e^{-2\pi b\xi} \, dx=A'e^{-2\pi b(\xi-M)}\int_{-\infty}^{+\infty} \frac{1}{1+x^{2}} \, dx$
$=\pi A'e^{-2\pi b(\xi-M)}$.
Assume that $\xi>M$. Then $\xi-M>0$
$\left| \hat{f}(\xi) \right|\leq \pi A'e^{-2\pi(\xi-M)\cdot b}$. We recall that, b is an arbitrary number in $(0,a)$. Moreover, $f\in \mathcal{F}_{a}$ for any $a>0$. Thus b can be any positive integer. %%那A不变吗%%
It follows that $\left| \hat{f}(\xi) \right|\leq \pi Ae^{-2\pi(\xi-M)\cdot n}$ for any $n\in \mathbb{N}$
If we let n tends to $+\infty$ we see that $-2\pi(\xi-M)\cdot n$ tends to $-\infty$
Thus $\left| \hat{f}(\xi) \right|=0$
We have show that $\hat{f}(\xi)=0$ if $\xi>M$
Similarly, for $\xi<-M$, we can show that
$\left| \hat{f}(\xi) \right|=\left| \int_{-\infty}^{+\infty} f(x+ib)e^{-2\pi i(x+ib)\xi} \, dx \right|\leq \pi A'e^{2\pi(\xi+M)b}$.
This implies that $\hat{f}(\xi)=0$ if $\xi<-M$

### 2.1.3 Proof: Converse Direction (Step 2)
We assume that $\left| f(z) \right|\leq Ae^{2\pi \left| \mathrm{Im}z \right|}$ for some constant $A>0$
We will show that $\left| \hat{f}(\xi) \right|=0$ if $\left| \xi \right|>M$
Firstly, we fix some $\xi>M$ for any $\varepsilon>0$, we set $f_{\varepsilon}(z)= \frac{f(z)}{(1+i\varepsilon z)^{2}}$. Note that $1+i\varepsilon z$ is 0 if and only if $z=\frac{1}{\varepsilon}i$
Thus, $f_{\varepsilon}(z)$ is holomorphic in the lower half plane
![[Pasted image 20251208141003.png|300]]
$\left| \hat{f}_{\varepsilon}(\xi)-\hat{f}(\xi) \right|\leq \int_{-\infty}^{+\infty} \left|  \frac{1}{(1+i\varepsilon z)^{2}}-1 \right|\left| f(x) \right|\left| e^{-2\pi ix\xi} \right|​	 \, dx\leq \int_{-\infty}^{+\infty} \left| \frac{1}{(1+i\varepsilon z)^{2}}-1 \right|\left| f(x) \right| \, dx$. We note that $|\frac{1}{(1+i\varepsilon x)^{2}-1}|= |\frac{\varepsilon^{2}x^{2}-2i\varepsilon x}{(1+i\varepsilon x)^{2}}|\leq \frac{\left| \varepsilon x \right|\left| \varepsilon x-2i \right|}{1+\varepsilon^{2}x^{2}}= \frac{\left| \varepsilon x \right|\cdot \sqrt{4+(\varepsilon x)^{2}}}{1+(\varepsilon x)^{2}}$
$\left| \hat{f}_{\varepsilon}(\xi)-\hat{f}(\xi) \right|\leq \int_{-\infty}^{+\infty} \frac{\varepsilon \left| x \right|\sqrt{4+(\varepsilon x)^{2}}}{1+\varepsilon^{2}x^{2}}\left| f(x) \right| \, dx$.
Recall that $\left| f(x) \right|\leq \frac{K}{1+x^{2}}$ for some $K>0$
Thsu $\left| \hat{f}_{\varepsilon}(\xi)-\hat{f}(\xi) \right|\leq K\int_{-\infty}^{+\infty} \frac{\varepsilon \left| x \right|\sqrt{4+(\varepsilon x)^{2}}}{(1+x^{2})(1+\varepsilon^{2}x^{2})} \, dx$
Then $\left| f_{\varepsilon}(x)\cdot e^{-2\pi i\xi x} \right|=\left| f_{\varepsilon}(x) \right|=\left| f(x) \right|\cdot \left| \frac{1}{1+i\varepsilon x} \right|\leq \left| f(x) \right|\leq \frac{K}{1+x^{2}}$
And $\int_{-\infty}^{+\infty} \frac{K}{1+x^{2}} \, dx=\pi K<+\infty$.
We also note that, for any fixed x, $f_{\varepsilon}(x)e^{-2\pi i\xi x}=f(x)e^{-2\pi i\xi x}\left(  \frac{1}{(1+i\varepsilon x)^{2}} \right)$
It tends to $f(x)\cdot e^{-2\pi i\xi x}$ when $\varepsilon \to0$.
Hence by dominate convergence theorem, we have
$$
\int_{-\infty}^{+\infty} f_{\varepsilon}(x)e^{-2\pi i\xi x} \, dx \to \int_{-\infty}^{+\infty} f(x)e^{-2\pi i\xi x} \, dx\quad \text{as}\:\varepsilon \to0
$$
​It means $\hat{f}_{\varepsilon}(\xi)\to \hat{f}(\xi)$
Note that $f_{\varepsilon}(z)\leq \frac{Ae^{2\pi M\left| \mathrm{Im}z \right|}}{1+(\varepsilon \mathrm{Re}z)^{2}}$ for all z with $\mathrm{Im}z\leq0$
By the calculus of step1 we see that $\hat{f}_{\varepsilon}(\xi)=0$ for $\xi>M$. Thus $\hat{f}(\xi)=0$ if $\xi>M$. For $\xi<-M$, we set
$f_{\varepsilon}(z)= \frac{f(z)}{(1-iz\varepsilon)^{2}}$ and use same method.

### 2.1.4 Proof: Converse Direction (Step 3)
Recall that we assume $\left| f(z) \right|\leq Ae^{2\pi M(z)}$. We will show that $\left| f(z) \right|\leq Ae^{2\pi M\left| z \right|}$ and $\left| f(x) \right|\leq \frac{A}{1=x^{2}}$ for $x\in \mathbb{R}$ implies $\left| f(z) \right|\leq A'e^{2\pi M\mathrm{Im}z}$
We first make some observation
$\forall x\in \mathbb{R}$, $\left| f(x) \right|\geq \frac{A}{1+x^{2}}$ implies that $f$ is bounded on $\mathbb{R}$
By considering $\frac{1}{A}f$ instead of f, we may assume that $\left| f(z) \right|\leq1$ for $x\in \mathbb{R}$
We will show that
**Lemma**:
Assume $f:\mathbb{C}\to \mathbb{C}$ holomorphic. $\left| f(x) \right|\leq1$ for $x\in \mathbb{R}$ and $\left| f(z) \right|\leq e^{2\pi M\left| z \right|}$. Then $\left| f(z) \right|\leq e^{2\pi M\left| \mathrm{Im}z \right|}$
Assume lemma for the tieme being, and we will finish the proof of Poley_Wierer theorem
For the function f in the statement, Lemma proves that, $\exists A'$ s/t/ $\left| f(z) \right|\leq A'\cdot e^{2\pi M\left| \mathrm{Im}z \right|}$.
By step2, we get that $\hat{f}(\xi)=0$ if $\left| \xi \right|>M$.

### 2.1.5 Supporting Theorem and Lemma Proof
We first show the following theorem.
**Theorem**.
Let $S=\left\{ z=\rho e^{i\theta}\quad\text{with}\:\rho>0,\theta\in\left( -\frac{\pi}{4},\frac{\pi}{4} \right) \right\}$​. Assume that $F:S\to \mathbb{C}$ is holomorphic and $F:\bar{S}\to \mathbb{C}$​ is continuous. Assume that $\left| F(z) \right|\leq Ce^{c\left| z \right|}$ for some $C,c>0$
And $\left| f(z) \right|\leq1$ on the boundary of $S$.
Then $\left| f(z) \right|\leq1$ for all $z\in S$
![[Pasted image 20251208145006.png|200]]
Proof:
Let $F_{\varepsilon}(z)=F(z)\cdot e^{-\varepsilon z^{\frac{3}{2}}}$. Hence, for $z=\rho e^{i\theta}$ with $\rho>0$, $\theta\in(-\pi,\pi)$
We define $z^{\frac{3}{2}}=\rho^{\frac{3}{2}}\cdot e^{i \frac{3}{2}\theta}<\frac{3}{8}\pi<\frac{\pi}{2}$
contained in the right hand plane
Then $\cos\left( \frac{3}{2}\theta \right)$ is positive for $z=\rho e^{i\theta}\in S$
For $z\in S$ fixed, we see that $F_{\varepsilon}(z)\to F(z)$. We will show that for any $\varepsilon>0$ $\left| F_{\varepsilon}(z) \right|\leq1$ for all $z\in S$.
( We think of Maximum principal )
First for $z\in S,z=\rho e^{i\theta}$, $e^{-\varepsilon z^{\frac{3}{2}}}=e^{-\varepsilon \rho e^{i \frac{3}{2}\theta}}=e^{-\varepsilon \rho\left( \cos \frac{3}{2}\theta+i\sin \frac{3}{2}\theta \right)}$. Then $\left| e^{-\varepsilon z^{\frac{3}{2}}} \right|=e^{-\varepsilon \rho^{\frac{3}{2}}cos\left( \frac{3}{2}\theta \right)}$ Since $\cos\left( \frac{3}{2}\theta \right)\geq \cos\left( \frac{3}{8}\pi \right)>0$
We see that
1. $\left| e^{-\varepsilon z^{\frac{3}{2}}} \right|\leq1$
2. $\left| e^{-\frac{\varepsilon 3}{2}z} \right|\leq e^{-\rho^{\frac{3}{2}}\cdot\varepsilon \cos\left( \frac{3}{8}\pi \right)}$ $\to0, as\:\rho \to0$
Hence $1\implies \left|F_{\varepsilon}(z) \right|\leq \left| F(z) \right|\leq1$​	for $z\in \partial S$
2.$\implies$ $\left| F_{\varepsilon}(z) \right|\to0$ as $\left| z \right|\to+\infty$
Now we apply the maximum principal to $F_{\varepsilon}$ on $\bar{S}$
$F_{\varepsilon}$ is bounded on $\bar{S}$ and is continuous on $\bar{S}$
$F_{\varepsilon}$ is holomorphic in $S$
The maximum principal $\implies$ $\sup_{z\in S}\left| F_{\varepsilon}(z) \right|\leq \sup_{z\in \partial S}\left| F(z) \right|\leq1$. Thus $\left| F_{\varepsilon}(z) \right|\leq1$.
Here we notice that the factor $e^{-\varepsilon z^{\frac{3}{2}}}$ is important to make $\left| F_{\varepsilon}(z) \right|$ bounded on $S$.
Thus $\left| F(z)\leq1 \right|$ for $z\in S$

**Proof of Lemma**
We divide $\mathbb{C}$ into four pieces
$S_{1}=\{\mathrm{Re}z>0,\mathrm{Im}z>0\}$
$S_{2}=\{\mathrm{Re}z<0,\mathrm{Im}z>0\}$
$S_{3}$
$S_{4}$
Ezch $S_{i}$ is the same as $S$ in the previous Theorem. For $S_{1}$, we apply the theorem to $F(z)=f(z)e^{2\pi iMz}$ Then we can cehck that $\left| F(z) \right|\leq1$ if $z\in \partial S_{1}$ and $\left| F(z) \right|\leq e^{4\pi M\left| z \right|}$
Theorem $\implies \left| F(z) \right|\leq1$ inside S
$\implies \left| f(z) \right|\leq e^{2\pi M\left| \mathrm{Im}z \right|}$ in S
we repeat the proof for $S_{2},\dots,S_{3}$