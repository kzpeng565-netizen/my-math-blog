---
tags:
  - 复分析
  - 分析
---
#复分析 #习题 
> [!Note] 2.1
>Prove that
>$$
>\int_0^\infty \sin(x^2)  dx = \int_0^\infty \cos(x^2)  dx = \frac{\sqrt{2\pi}}{4}.
>$$
>These are the **Fresnel integrals**. Here, $\int_0^\infty$ is interpreted as $\lim_{R \to \infty} \int_0^R.$
>**Hint:** Integrate the function $e^{-x^2}$ over the path in Figure 14. Recall that
>$$
>\int_{-\infty}^{\infty} e^{-x^2}  dx = \sqrt{\pi}.
>$$

![[Pasted image 20251026204557.png|400]]
Since $e^{-x^{2}}$ is a holomorphic function, we have
$$
\left( \int_{\gamma_{1}}+\int_{\gamma_{2}}+\int_{\gamma_{3}} \right)e^{-x^{2}}dx=0\quad \text{where}\gamma_{1}\text{ refers to}[0,R],\: \text{and }\gamma_{3}\text{ refers to }R e^{i \pi/4}\to0
$$
- integrate on $\gamma_{1}$. $\lim_{R\to\infty}\int_{0}^{R}e^{-x^{2}}= \frac{\sqrt{\pi}}{2}$
- integrate on $\gamma_{3}$. Let $\gamma_{2}:t\in[0,1]\to tRe^{i \pi/4}$, and $w=tR$
​	$$
\begin{align}
-\int_{0}^{1}  e^{tR e^{i \pi/4}}R e^{i \pi/4}\, dx= & \int_{0}^{R} e^{-w^{2}i}e^{i \pi/4} \, dw \\
=  & -\int_{0}^{R} (\cos w^{2}-i\sin w^{2}) \, dw \\
=  & - \frac{\sqrt{2}}{2} \left( \int_{0}^{R} \cos w^{2}+\sin w^{2} \, dw  \right)-i \frac{\sqrt{2}}{2}\left( \int_{0}^{R} \cos w^{2} -\sin w^{2}\, dw  \right)
\end{align}
$$
- integrate on $\gamma_{2}$. $w:t\in[0,\pi/4]\to e^{it}$
$$
\lim_{R\to\infty} \int_{0}^{\pi/4} e^{-R e^{2i\varphi}}iR e^{i\varphi} \, d\varphi =\lim_{R\to\infty} \mathrm{Re}^{-R^{2}}\int_{w}e^{w^{2}}dw=\lim_{R\to\infty} R e^{-R^{2}}C=0
$$
Therefore, by property of holomorphism
$$
\begin{cases}
 & - \frac{\sqrt{2}}{2}  \int_{0}^{\infty} \cos w^{2}+\sin w^{2} \, dw +\frac{\sqrt{\pi}}{2} & =0 \\
 & i \frac{\sqrt{2}}{2}\left( \int_{0}^{\infty} \cos w^{2} -\sin w^{2}\, dw  \right)=0
\end{cases}
\implies \int_{0}^{\infty} \cos w^{2} \, dw=\int_{0}^{\infty} \sin w^{2} \, dw =\frac{\sqrt{2\pi}}{4} 
$$​	

> [!Note] 2.12
>Let $u$ be a real-valued function defined on the unit disc $\mathbb{D}$. Suppose that $u$ is twice continuously differentiable and harmonic, that is,
>$$
>\triangle u(x, y) = 0
>$$
>for all $(x, y) \in \mathbb{D}$.
>(a) Prove that there exists a holomorphic function $f$ on the unit disc such that
>$$
>\text{Re}(f) = u.
>$$
>Also show that the imaginary part of $f$ is uniquely defined up to an additive (real) constant. [Hint: From the previous chapter we would have $f'(z) = 2\partial u/\partial z$. Therefore, let $g(z) = 2\partial u/\partial z$ and prove that $g$ is holomorphic. Why can one find $F$ with $F' = g$? Prove that $\text{Re}(F)$ differs from $u$ by a real constant.]

Let $v(x,y)=\int_{(x_{0},y_{0})}^{(x,y)}- u_{y} \, dx+u_{x}dy$
Observe differential form is closed $d(-u_{y}dx+u_{x}dy)=0$, So the integral is well-defined. And it suffices to show $v$ meet Cauchy-Riemann Equation. $u_{x}=v_{y};\:u_{y}+v_{x}=0$
Hence, $f(z)=u+iv$ is a holomorphic function.



> [!Note] (b)
>(b) Deduce from this result, and from Exercise 11, the Poisson integral representation formula from the Cauchy integral formula: If $u$ is harmonic in the unit disc and continuous on its closure, then if $z = re^{i\theta}$ one has
>$$
>u(z) = \frac{1}{2\pi} \int_0^{2\pi} P_r(\theta - \varphi) u(\varphi)  d\varphi
>$$
>where $P_r(\gamma)$ is the Poisson kernel for the unit disc given by
>$$
>P_r(\gamma) = \frac{1 - r^2}{1 - 2r \cos \gamma + r^2}.
>$$

Let $f=u+iv$. By the conditions, it's easy to see that Cauchy integral equation holds on unit circle.
From Exercise 11, it follows that 
$$
u+iv=\frac{1}{2\pi}\int_{0}^{2\pi} f(e^{i\varphi})\mathrm{Re}\left( \frac{R e^{i\varphi}+re^{i\theta}}{R e^{i\varphi}-re^{i\theta}} \right)u(\varphi)​	 \, d\varphi 
$$
$\mathrm{Re}\left( \frac{R e^{i\varphi}+re^{i\theta}}{R e^{i\varphi}-re^{i\theta}} \right)= \frac{R^{2}-r^{2}}{R^{2}+r^{2}-2Rr\cos(\theta-\varphi)}=P_{r}(\theta-\varphi)$
*where $R$ is equal to 1*
Then, we only use the real paty
$$
u=\frac{1}{2\pi} \int_{0}^{2\pi} u(\varphi)P_{r}(\theta-\varphi) \, d\varphi 
$$

> [!Note] 2.13
>Suppose $f$ is an analytic function defined everywhere in $\mathbb{C}$ and such that for each $z_0 \in \mathbb{C}$ at least one coefficient in the expansion
>$$
>f(z) = \sum_{n=0}^{\infty} c_n (z - z_0)^n
>$$
>is equal to 0. Prove that $f$ is a polynomial.
>**Hint:** Use the fact that $c_n n! = f^{(n)}(z_0)$ and use a countability argument.

Let N(z​) be the subscript of the vanished coeffcient.
Let $S(n)=\{z\in \mathbb{C}|N(z)=n\}$
$$
\mathbb{C} =\bigcup _{i=0}^{\infty}S(i)
$$
Since $\mathbb{C}$ is uncountable set, least one $S(k)$ must be uncountable.
Assume conversly, $f^{(k)}\neq0$. Then the zero of $f^{(k)}$ must be isolated, which implies $S(k)$ is countable on $\mathbb{C} \cong\mathbb{R}\times \mathbb{R}$​	. That leads to a contradiction.  ^a2b9e0
