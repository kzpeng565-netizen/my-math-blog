---
tags:
  - 复分析
  - 分析
---
# 1. Preliminaries and Definitions
%%一般的傅里叶变换是怎么做的%%
**Fourier Transform and Fourier Series Comparison**
- For $f:\mathbb{R}\to \mathbb{C}$, the Fourier transform is defined as $\hat{f}(\xi)=\int_{-\infty}^{+\infty} f(x)e^{-2\pi ix \xi}​	 \, dx$, with the inversion $f(x)=\int_{-\infty}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi$.
- Compare with Fourier series: $f(x)=\sum_{n=0}^{\infty}e^{2\pi nix}$, where $a_{n}=\int_{0}^{1} f(x)e^{-2\pi inx} \, dx$.

## 1.1 The Function Space $\mathcal{F}_{a}$ and $\mathcal{F}$
- Fix $a>0$, define the strip $S_{a}=\{z\in \mathbb{C}\mid -a<\mathrm{Im}(z)<a\}$.
![[Pasted image 20251201134013.png|300]]
- **Definition**: Define a space of holomorphic functions:
$\mathcal{F}_{a}=\left\{ f:S_{a}\to \mathbb{C}\text{ holomorphic and }\exists A>0, \text{s.t. } \left| f(x+iy) \right|\leq \frac{A}{1+x^{2}},\: \forall z=x+iy\in S_{a} \right\}$.
- Define $\mathcal{F}= \bigcup_{a>0}\mathcal{F}_{a}$.
- Thus, $f\in \mathcal{F}$ iff there exists $a>0$ such that $f:S_{a}\to \mathbb{C}$ is holomorphic and satisfies $\left| f(z) \right|\leq \frac{A}{1+(\mathrm{Re}z)^{2}}$ for some $A>0$ (dependent on $f$ but not on $z$).
- For $f\in \mathcal{F}$, its restriction $f|_{\mathbb{R}}$ is a $C^{\infty}$ function satisfying $\left| f(x) \right|\leq \frac{A}{1+x^{2}}, \forall x\in \mathbb{R}$. Consequently, $\hat{f}(\xi)$ is well-defined for all $\xi\in \mathbb{R}$, and the Fourier inversion holds.

# 2. Main Theorems

## 2.1 Exponential Decay of the Fourier Transform
> [!Note] Theorem
>Assume that $f\in \mathcal{F}_{a}$ for some $a>0$. Then for any $0<b<a$, $\exists B>0$ such that $\left| \hat{f}(\xi) \right|<Be^{-2\pi b\left| \xi \right|}$.

### 2.1.1 Proof Sketch and Details
**Proof Outline**: Fix $0<b<a$ and $\xi>0$. For a large $R>0$, consider a rectangular contour with vertices $R, -R, -R-ib, R-ib$.
![[Pasted image 20251201135618.png|300]]
Define $g(z)=f(z)\cdot e^{-2\pi i\xi z}$. By Goursat's theorem, the integral of $g$ over the closed contour is zero. The proof estimates the integrals over the vertical sides ($L_2$, $L_4$) and the bottom side ($L_3$) to bound $\hat{f}(\xi)$.

**Proof Details**:
- $\hat{f}(\xi)=\int_{-\infty}^{+\infty} g(x) dx = \lim_{R\to\infty}\int_{-R}^{R} g(x) dx = -\lim_{R\to+\infty} \int_{L_{1}}g(z)dz$.
- Since $\int_{L_{1}+L_{2}+L_{3}+L_{4}}g(z)dz=0$, we have $\int_{L_{1}}g(z)dz = - (\int_{L_{2}}g(z)dz + \int_{L_{3}}g(z)dz + \int_{L_{4}}g(z)dz)$.
- **Estimate for $L_2$**:
$$
\begin{align}
\left| \int_{L_{2}}g(z)dz \right|&= \left| \int_{L_{2}}f(z)e^{-2\pi i\xi z}dz \right|  \\
&\leq \int_{L_{2}}\left| f(z) \right| |e^{2\pi i\xi z}|dz \\
&=\int_{0}^{b} \left| f(-R-iy) \right| \cdot \left| e^{-2\pi i(\xi R-i\xi y)} \right|  \, dy \\
&\leq \int_{0}^{b} \frac{A}{1+R^{2}}e^{-2\pi y\xi} \, dy  \\
&\leq \frac{A\cdot b}{1+R^{2}} \quad (\text{since } e^{-2\pi y\xi}\leq1 \text{ for } y, \xi \geq 0).
\end{align}
$$
- Similarly, $\left| \int_{L_{4}}g(z)dz \right|\leq \frac{A\cdot b}{1+R^{2}}$.
- **Estimate for $L_3$**:
$$
\left| \int_{L_{3}}g(z) dz\right| =\left| \int_{-R}^{R} f(-x-ib)e^{-2\pi i\xi(x-ib)} \, dx  \right| \leq e^{-2\pi b\xi}\int_{-R}^{R} \frac{A}{1+x^{2}} \, dx \leq e^{-2\pi b\xi}A\pi.
$$
Let $B=\pi A$. Then, $\left| \int_{L_{1}}g \right|\leq \left| \int_{L_{2}}g \right|+\left| \int_{L_{3}}g \right|+\left| \int_{L_{4}}g \right|\leq2 \frac{Ab}{1+R^{2}}+Be^{-2\pi b\xi}$.
- Letting $R\to +\infty$, we obtain $\left| \hat{f}(\xi) \right|\leq Be^{-2\pi b\xi}$ for $\xi>0$.
- The case for $\xi<0$ is handled by considering a rectangle reflected in the real axis.%%只需要考虑上半平面%% 

**Remark**: $B$ is independent of $b$. We can pick $B=\pi A$ where $\left| f(x+ib) \right|\leq \frac{A}{1+x^{2}}$.
%%能延拓的越远(a越大), 指数衰减越快%%

## 2.2 Fourier Inversion Formula
> [!Note] Theorem
>If $f\in \mathcal{F}$, then the Fourier inversion holds. That is $f(x)=\int_{-\infty}^{+\infty} \hat{f}(\xi)e^{2\pi ix \xi}​	 \, d\xi$ for all $x\in \mathbb{R}$.

### 2.2.1 A Useful Lemma
**Lemma**: Let $A\in \mathbb{R}_{>0},B\in \mathbb{R}$. Then $\int_{0}^{+\infty} e^{-(A+iB)\xi} \, d\xi= \frac{1}{A+iB}$.
*Proof*: Since $\int_{0}^{+\infty} \left| e^{-(A+iB)\xi} \right| \, d\xi=\int_{0}^{+\infty}e^{-A\xi}d\xi<+\infty$, we can compute:
$\int_{0}^{+\infty} e^{-(A+iB)\xi} \, d\xi=\lim_{R\to+\infty}\int_{0}^{R} e^{-(A+iB)\xi} \, d\xi=\lim_{R\to+\infty}\left. \frac{e^{-(A+iB)\xi}}{-(A+iB)}\right|_{0}^{R} = \frac{1}{A+iB}$.

### 2.2.2 Proof of the Inversion Formula
**Proof Setup**:
$\int_{-\infty}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi=\int_{-\infty}^{0} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi+\int_{0}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi$.

**Step 1: Integral for $\xi>0$**.
From the proof of Theorem 2.1, for $\xi>0$, we have $\hat{f}(\xi)=\int_{-\infty}^{+\infty} f(u-ib)e^{-2\pi i\xi(u-ib)} \, du$ (for $0<b<a$). %%因为在上一个定理中, 两个"短边" 会趋于0, 只需要考虑第三条长边%%
Substitute this into the integral:
$$
\begin{align}
\int_{0}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi &= \int_{0}^{+\infty} \int_{-\infty}^{+\infty} f(u-ib)e^{-2\pi i\xi(u-ib)} \, du \ e^{2\pi i\xi x} \, d\xi \\
&= \int_{0}^{+\infty} \int_{-\infty}^{+\infty} f(u-ib)e^{-2\pi i\xi(u-ib-x)} \, du \, d\xi.
\end{align}
$$
Since the double integral is absolutely integrable, we swap the order of integration:
$$
= \int_{-\infty}^{+\infty} \left( \int_{0}^{+\infty} e^{-2\pi i\xi(u-ib-x)} \, d\xi \right)f(u-ib) \, du.
$$
Applying the Lemma with $A=2\pi b$, $B=2\pi (u-x)$ (noting that $e^{-2\pi i\xi(u-ib-x)} = e^{-2\pi b\xi}e^{-2\pi i\xi(u-x)}$), we get:
$$
\int_{0}^{+\infty} e^{-2\pi i\xi(u-ib-x)} \, d\xi = \frac{1}{2\pi i (u-ib-x)}.
$$
Therefore,
$$
\int_{0}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi = \frac{1}{2\pi i}\int_{-\infty}^{+\infty} \frac{f(u-ib)}{u-ib-x} \, du.
$$
Set $\theta=u-ib$, with $L=\{ \theta\in \mathbb{C}\mid \mathrm{Im}(\theta)=-b\}$. Then:
$$
\int_{0}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi = \frac{1}{2\pi i}\int_{L} \frac{f(\theta)}{\theta-x}d\theta.
$$
![[Pasted image 20251201144631.png|300]]

**Step 2: Integral for $\xi<0$**.
By a similar method (using a rectangle above the real axis), we obtain:
$$
\int_{-\infty}^{0} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi = -\frac{1}{2\pi i}\int_{L'} \frac{f(\theta)}{\theta-x}d\theta,
$$
where $L'=\{z\in \mathbb{C}\mid \mathrm{Im}(z)=b\}$.

**Step 3: Combining and Applying Residue Theorem**.
Now consider the rectangular contour $\gamma$ with vertices $R+ib, -R+ib, -R-ib, R-ib$, traversed positively.
![[Pasted image 20251201145641.png|300]]
By the Residue Theorem, since $f(z)/(z-x)$ has a simple pole at $z=x$ inside $\gamma$ (for large $R$), we have:
$$
\frac{1}{2\pi i}\int_{\gamma} \frac{f(\theta)}{\theta-x}d\theta = f(x).
$$
We can decompose $\gamma$ into $L'$ (top, right to left), $\gamma_1$ (left side), $L$ (bottom, left to right), and $\gamma_2$ (right side):
$$
\frac{1}{2\pi i}\left(\int_{L'} + \int_{\gamma_1} + \int_{L} + \int_{\gamma_2} \right) \frac{f(\theta)}{\theta-x}d\theta = f(x).
$$
Note that $\int_{L'}$ is from right to left, so $-\int_{L'} = \int_{-L'}$ (left to right). From Steps 1 & 2:
$$
\frac{1}{2\pi i}\int_{L} \frac{f(\theta)}{\theta-x}d\theta - \frac{1}{2\pi i}\int_{L'} \frac{f(\theta)}{\theta-x}d\theta = \int_{0}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi + \int_{-\infty}^{0} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi = \int_{-\infty}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi.
$$
Thus,
$$
f(x) = \int_{-\infty}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi + \frac{1}{2\pi i}\left( \int_{\gamma_1} + \int_{\gamma_2} \right) \frac{f(\theta)}{\theta-x}d\theta.
$$
**Step 4: Showing the side integrals vanish as $R \to \infty$**.
Estimate for $\gamma_1$ (the left vertical segment):
$$
\begin{align}
\left| \int_{\gamma_{1}} \frac{f(\theta)}{\theta-x} d\theta \right| &= \left| \int_{b}^{-b} \frac{f(-R+iy)}{-R+iy-x} \, dy \right| \\
&\leq \int_{-b}^{b} \frac{A}{1+R^{2}} \cdot \frac{dy}{\sqrt{(R+x)^{2}+y^{2}}} \\
&\leq \frac{2bA}{(1+R^{2})(R-|x|)} \quad \text{(for sufficiently large $R$)}.
\end{align}
$$
This tends to $0$ as $R \to \infty$. Similarly, $\left| \int_{\gamma_{2}} \frac{f(\theta)}{\theta-x} d\theta \right| \to 0$.
Therefore, taking the limit $R \to \infty$, we conclude:
$$
f(x) = \int_{-\infty}^{+\infty} \hat{f}(\xi)e^{2\pi i\xi x} \, d\xi.
$$

# 3. Poisson Summation Formula
> [!Note] Theorem
>Let $f\in \mathcal{F}$. Then $\sum_{n\in \mathbb{Z}}f(n)=\sum_{n\in \mathbb{Z}}\hat{f}(n)$.

## 3.1 Proof of Poisson Summation Formula
**Preliminary Observations**: The summations are absolutely convergent because:
- $|f(n)| \leq \frac{A}{1+n^{2}}$.
- $|\hat{f}(n)| \leq Be^{-2\pi b|n|}$ for some $0<b<a$ if $f\in \mathcal{F}_{a}$.

**Proof Setup**:
Assume $f\in \mathcal{F}_{a}$. Pick $b\in(0,a)$. For an integer $N>0$, consider the rectangular contour $\gamma_N$ with vertices $\pm (N+\frac{1}{2}) \pm ib$.
![[Pasted image 20251203135129.png]]
Consider the meromorphic function $g(z)= \frac{f(z)}{e^{2\pi iz}-1}$ on $S_a$. Its poles are simple and located at all integers $z=n \in \mathbb{Z}$. The residue at $z=n$ is $\frac{f(n)}{2\pi i e^{2\pi i n}} = \frac{f(n)}{2\pi i}$.

**Applying the Residue Theorem**:
By the Residue Theorem, the integral of $g(z)$ over $\gamma_N$ equals $2\pi i$ times the sum of residues inside the contour. The integers from $n=-N$ to $n=N$ lie inside $\gamma_N$. Therefore:
$$
\frac{1}{2\pi i}\int_{\gamma_N} \frac{f(z)}{e^{2\pi iz}-1}dz = \sum_{n=-N}^{N} \text{Res}(g, n) = \sum_{n=-N}^{N} f(n).
$$
Thus, we have:
$$
\sum_{n=-N}^{N}f(n)= \frac{1}{2\pi i}\int_{\gamma_N} \frac{f(z)}{e^{2\pi iz}-1}dz.
$$
**Taking the limit $N \to \infty$**:
- The left-hand side converges to $\sum_{n\in \mathbb{Z}}f(n)$.
- The goal is to show the right-hand side converges to $\sum_{n\in \mathbb{Z}}\hat{f}(n)$. The proof typically involves evaluating the contour integral by splitting it into top and bottom horizontal segments, relating these to integrals of $f(x\pm ib)$, and then recognizing these as Fourier transform expressions evaluated at integer points. (The note's proof is cut off at this point, but the standard argument completes the result).

Since $e^{2\pi i(h+h)}-1=e^{2\pi in}(e^{2\pi ih}-1)=(2\pi ih)+ \frac{(2\pi ih)^{2}}{2!}+\dots$ 
$g(z)= \frac{f(n+h)}{e^{2\pi i(h+n)}-1}= \frac{f(n)}{2\pi ih}(1+o(h))$​
By residue formula, if $\gamma$ is the rectangle, then $\frac{1}{2\pi i}\int_{\gamma}g=\sum_{-n\leq k\leq n}f(n)$. If we denote $\gamma=\gamma_{1}+\gamma_{2}+\gamma_{3}+\gamma_{4}$​	as in the pincture, then $\int_{\gamma_{2}}g(z)dz=\int_{-b}^{b} g\left( -N-\frac{1}{2}+iy \right) \, dy$. Then $\left| \int_{\gamma_{2}}g(z) \right|\leq \int_{-b}^{b} \frac{\left| f\left( -N-\frac{1}{2}+iy \right) \right|}{\left| e^{2\pi i\left( -N-\frac{1}{2}+iy \right)}-1 \right|} \, dy \displaystyle$ 
For the numerator, we recall that $\exists A>0 ,s.t.$ $\left| f(x+iy) \right|\leq \frac{A}{1+x^{2}}$ for $z\in S_{a}$
Thus $\left| f\left( -N-\frac{1}{2}+iy \right) \right|\leq \frac{A}{1+\left( N+\frac{1}{2} \right)^{2}}$​	 for any $-b\leq y\leq b$​	
For the donominatr
$$
\begin{align}
\left| e^{2\pi i\left( -N-\frac{1}{2}+iy \right)}-1  \right| = & \left| e^{2\pi i\left( iy-\frac{1}{2} \right)} \right|  \\
 = & \left| -e^{-2\pi y}-1 \right|   \\
  & =1+e^{-2\pi y}>1 
\end{align}
$$
Thus $\left| \int_{\gamma_{2}}g(z) \right|\leq \int_{-b}^{b} \frac{\frac{A}{1+\left( N+\frac{1}{2} \right)^{2}}}{1} \, dy=\frac{2bA}{1+\left( N+\frac{1}{2} \right)^{2}}$
Similarly, we see that $\left| \int_{\gamma_{2}}g(z) \right|\leq \frac{2bA}{1+\left( N+\frac{1}{2} \right)^{2}}$. Now we will let $N$ tend to $+\infty$ in the equality.
$\sum_{-N<n<N}f(n)=\int_{\gamma_{1}}+\dots \int_{\gamma_{4}}$, then $\int_{\gamma_{2}},\int_{\gamma_{4}}\to0$. So $\int_{\gamma_{1}}g\to \int_{L_{2}}-g$, where $L_{2}=\{y=b\}$
Note that $-\int_{L_{2}}g=-\int_{-\infty}^{+\infty} g(x+ib) \, dx$. And $\sum_{-N\leq n\leq N}f(n)$ tends to $\sum_{n\in \mathbb{N}}f(n)$. In conclusion $\sum_{n\in \mathbb{N}}f(n)=\int_{L_{1}}g-\int_{L_{2}}g$
In the next step, we note that, if $\sum_{n=0}^{+\infty}w^{n}$ converge absolutely to $\frac{1}{1-w}$​	on any compact subset in $\mathbb{D}$.
Therefore, if $z\in L_{2}$, then we hvae $\left| e^{2\pi iz} \right|=\left| e^{2\pi i(x+ib)} \right|=e^{-2\pi b}<1$
Thus, $\frac{1}{1-e^{2\pi iz}}=\sum ^{+\infty}_{n=0}e^{2\pi inz}$. 
The right-hand-side converge uniformly on $L_{2}$ 
That is, for any $\varepsilon>0$, $\exists N\in \mathbb{N},s.t.$, $\left| \frac{1}{1-e^{2\pi iz}}-\sum_{n=0}^{m}e^{2\pi inz} \right|\leq\varepsilon$ 
for any $m\geq N$ and anu $z\in L_{2}$. Now, since $\left| f(z) \right|\leq \frac{A}{1+(\mathrm{Re}z)^{2}}$, we see that $f$ is bounded on $L_{2}$ . It follows that $\sum_{n=0}^{+\infty}f(z)e^{2\pi inz}$ converges uniformly to $\frac{f(z)}{1-e^{2\pi iz}}=-g(z)$ in $L_{2}$
It follows that
$-\int_{L_{2}}g=\int_{L_{2}}-g=\int \sum_{n=0}^{+\infty}f(z)e^{2\pi inz}dz=\sum_{n=0}^{+\infty}\int_{L_{2}}f(z)e^{2\pi nz}=\sum_{n=0}^{+\infty}\int_{-\infty}^{+\infty} f(x+ib)e^{2\pi in(x+ib)} \, dx$
$$
\sum_{n=0}^{+\infty}\int_{-\infty}^{+\infty} f(x+ib)e^{2\pi in(x+ib)} \, dx=\sum_{n=0}^{+\infty}\int_{-\infty}^{+\infty} f(x)e^{2\pi inx} \, dx
$$
根据[[复分析15 Fourier Transform#2.1.1 Proof Sketch and Details|上文的计算]], 这个等号成立
This means that
$$
-\int_{L_{2}}g=\sum_{n=0}^{+\infty}\hat{f}(-n)
$$
For $a\in L_{1}$, $\left| e^{2\pi iz} \right|=\left| e^{2\pi i(x-ib)} \right|=e^{2\pi b}>1,\left| e^{-2\pi iz} \right|=e^{-2\pi b}​	<1$ 
Then $\frac{1}{e^{2\pi iz}-1}=\frac{1}{e^{2\pi iz}}\cdot \frac{1}{1-e^{-2\pi iz}}=\frac{1}{e^{2\pi iz}}\left( \sum_{n=o}^{+\infty}e^{-2\pi inz} \right)=\sum_{n=1}^{+\infty}e^{-2\pi inz}$ 
The convergence is uniform on $L_{1}$ 
By the same reasoning, we get 
$$
\int_{l_{1}}g=\int_{L_{1}}\sum_{n=1}^{+\infty} f(z)e^{-2\pi inz}dz=\sum_{n=1}^{+\infty} \int_{L_{1}}f(z)e^{-2\pi inz}dz=\sum_{n=1}^{+\infty} \int_{-\infty}^{+\infty} f(x-ib)e^{-2\pi in(x-ib)} \, dx=\sum_{i=1}^{+\infty}\int_{-\infty}^{+\infty} f(x)e^{-2\pi inx} \, dx
$$
Finaly, $\int_{L_{1}}g=\sum_{i=1}^{+\infty}\hat{f}(n)$. Thus $\sum_{n=1}^{+\infty}f(n)=\int_{L_{1}}-\int_{L_{2}}g=\sum_{n\in N}\hat{f}(n)$

- [x] #task 阅读并且弄懂复分析课堂笔记(45分钟) 🔼 📅 2025-12-08 ✅ 2025-12-10