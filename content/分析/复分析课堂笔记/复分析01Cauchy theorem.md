---
tags:
  - 复分析
  - 分析
---
#复分析 #课堂笔记

柯西定理
$\Omega$上 f 全纯$\implies$$\Omega$上有原函数$\implies$$\int_{\gamma}f(z)dz=0,\forall \gamma$是$\Omega$内的简单闭曲线

全纯函数的五个等价定义
1. 复可微性
2. 柯西黎曼方程
3. 魏尔斯特拉斯的观点: 解析函数, $f(z)=\sum_{n=0}^{\infty}a_{n}(z-z_{0})^{n}$ , $\left| z-z_{0} \right|<r$
4. 保角性和保持定向性. 如果$\gamma_{1}',\gamma_{2}$
5. Morera定理: 如果$\int_{\gamma}f(z)dz=0\implies f(z)$有原函数, 所以全纯.

柯西积分公式
$$
f(x)= \frac{1}{2\pi i}\int_{C} \frac{f(\zeta)}{\zeta-z}dz
$$
柯西定理$\iff$ $\iff \int_{\gamma}f(z)dz=0\iff$全纯函数在单连通区域上有原函数

$$
\begin{align*}
f^{(n)}(z) = \frac{n!}{2\pi i} \int_{C} \frac{f(\zeta)}{(\zeta - z)^{n+1}} \, d\zeta
\end{align*}$$

# 1.Cauchy 定理的证明
## 1.1 证明全纯函数在开集内一定有原函数
>[!a basic theorem of primitive]
if a continuous function  has a primitive $F$ in$\Omega$ , and $\gamma$ is a curve in $\Omega$ that begins at $w_1$ and ends at $w_2$, then
>$$
\begin{align*}
\int_\gamma f(z) \, dz = F(w_2) - F(w_1).
\end{align*}
$$

$$
\begin{align*}
\int_{\gamma} f(z) \, dz &= \int_{a}^{b} f(z(t)) z'(t) \, dt \\
&= \int_{a}^{b} F'(z(t)) z'(t) \, dt \\
&= \int_{a}^{b} \frac{d}{dt} F(z(t)) \, dt \\
&= F(z(b)) - F(z(a)).
\end{align*}$$
So for any closed curve $\gamma$ , the integration equals 0

>[! theorem 1.1] 
>If $\Omega$ is an open set in $\mathbb{C}$, and $T \subseteq \Omega$ a triangle whose interior is also contained in $\Omega$, then$\int_{T} f(z) \, dz = 0\textit{whenever}$ $f$ is holomorphic in $\Omega$. 

![[Pasted image 20251013133848.png]]
$$
\begin{align*}
\int_{T^{(0)}}^{T} f(z) \, dz = \int_{T_1^{(1)}}^{T} f(z) \, dz + \int_{T_2^{(1)}}^{T_1} f(z) \, dz + \int_{T_3^{(1)}}^{T_2} f(z) \, dz+\int_{T_4^{(1)}}^{T_3} f(z) \, dz.
\end{align*}$$
For some $j$ we must have(we asume the integration with j is the largest)
$$
\begin{align*}
\left| \int_{T^{(0)}}^{T} f(z) \, dz \right| \leq 4 \left| \int_{T_j^{(1)}}^{T_1} f(z) \, dz \right|,
\end{align*}
$$
But the diameter and perimeter of $T^{n}$ is going to zero. And we get a sequence $T^{n}\supset T^{n+1}$. There is a unique point $z_{0}$ in every subset
$$
f(z)=f'(z_{0})(z-z_{0})+\psi(z)
$$
And we know $f'(z_{0})(z-z_{0})$ have primitives, while $\psi(z)\to0,\:z\to0$
So we can finish the approximation

Corollary 1.2
If $f$ is holomorphic in an open set $\Omega$ that contains a rectangle $R$ and its interior, then
$$
\begin{align*}
\int_{R} f(z) \, dz = 0.
\end{align*}
$$

>[! Theorem 2.1 主要定理]
>a holomorphic function in an open disc has a primitive in that disc

without loss of generality, we assume the center of the disc D is $0\in \mathbb{Z}$
![[Pasted image 20251013135003.png|400]]
Define
$$
\begin{align*}
F(z) = \int_{\gamma_z} f(w) \,dw.
\end{align*}
$$
The choice of $\gamma_z$ gives an unambiguous（含混不清的） definition of the function $F(z)$. We contend that $F$ is holomorphic in $D$ and $F'(z) = f(z)$. To prove this, fix $z\in D$ and let $h\in\mathbb{C}$ be so small that $z+h$ also belongs to the disc. Now consider the difference
$$
\begin{align*}
F(z+h) - F(z) = \int_{\gamma_{z+h}} f(w) \,dw - \int_{\gamma_z} f(w) \,dw.
\end{align*}
$$
![[Pasted image 20251013135348.png|500]]
Then, consider the difference, we complete the square and triangle, as the Figure 4 shows. We get a straight line from $z$ to $z+h$, denoting it by $\eta$
$$
F(z+h)-F(z)=\int_{\eta}f(w)dw=\int_{0}^{1} f(z+th)h \, dt
$$
Since f is continuous, $\lim_{h\to0}\int_{0}^{1} f(z+th)dt=f(z)$
$$
\begin{align*}
\lim_{h \to 0} \frac{F(z+h)-F(z)}{h} = f(z),
\end{align*}
$$
Therefore, $F$ is a primitive of $f$

Remark: we can extend the result to any simply counted open set
We only use Theorem1.1 and f is continuous

**Corollary**
If $f$ is holomorphic in a disc, then$$
\begin{align*}
\int_{\gamma} f(z) \, dz = 0
\end{align*}$$
for any closed curve $\gamma$ in that disc.

**Corollary**
Suppose $f$ is holomorphic in an open set $\Omega$ containing the circle $C$ and its interior. Then
$$
\begin{align*}
\int_C f(z) \, dz = 0.
\end{align*}
$$
due to the porperty of open set we can find a slightly open set that contains C but is in $\Omega$

**keyhole figure**
![[Pasted image 20251013143417.png|400]]
# 2. Cauchy integral formula

>[!Theorem 4.1]
> Suppose $f$ is holomorphic in an open set that contains the closure of a disc $D$. If $C$ denotes the boundary circle of this disc with the positive orientation, then
>$$
\begin{align*}
f(z) = \frac{1}{2\pi i} \int_C \frac{f(\zeta)}{\zeta - z} d\zeta \quad \text{for any point } z \in D.
\end{align*}$$

==注意条件要求包含圆盘的开邻域全纯== 
![[Pasted image 20251013143933.png|400]]
$\varepsilon$ refers to the radius of small circle, and $\delta$ refers to the distence between two straight lines
Since $F(\xi)= \frac{f(\xi)-f(z)}{\xi-z}$ is holomorphic at $\xi$ away from $z$, we have
$$
\begin{align*}
\int_{\Gamma \delta, \epsilon} F(\zeta) \, d\zeta = 0
\end{align*}$$
then, due to the continuity of $F$, we make $\delta\to 0$
[[路径积分的连续性]]
$$
0=\int_{\Gamma_{0,\varepsilon}} \frac{f(\xi)-f(z)}{\xi-z}d\xi=\int_{C} \frac{f(\xi)-f(z)}{\xi-z}-\int_{C_{\varepsilon}} \frac{f(\xi)-f(z)}{\xi-z}
$$
since f is differentiable at $z$ , we write $f(\xi)-f(z)=f'(z)(\xi-z)+o(h)$
so $\frac{f(\xi)-f(z)}{\xi-z}\to f'(z)$, but $C_{\varepsilon}\to 0$ , the latter integration equals 0 when $\varepsilon\to 0$
$$
\int_{C} \frac{f(\xi)-f(z)}{\xi-z}d\xi=0
$$
We compute $\int_{C} \frac{f(z)}{\xi-z}d\xi=2\pi if(z)$
Hence,
$$
f(z)= \frac{1}{2\pi i} \int_{C} \frac{f(\xi)}{\xi-z}d\xi
$$

>[! derivative for n tiems]
If $f$ is holomorphic in an open set $\Omega$, then $f$ has infinitely many complex derivatives in $\Omega$. Moreover, if $C \subset \Omega$ is a circle whose interior is also contained in $\Omega$, then
>$$
\begin{align*}
f^{(n)}(z) = \frac{n!}{2\pi i} \int_{C} \frac{f(\zeta)}{(\zeta - z)^{n+1}} \, d\zeta
\end{align*}$$
for all $z$ in the interior of $C$.

$$
\frac{\partial^{k}}{\partial z^{k}}\left(  \frac{f(\xi)}{\xi-z} \right)= \frac{k!f(\xi)}{(\xi-z)^{k+1}}
$$
and we know the integral and derivative can change the order

**Corollary**
$f:\Omega\to \mathbb{C}$ is holomorphic, $D$ disc centered at $z_{0}$ with $\bar{D} \subset K\subset \bar{K}\subset\Omega$
where $\bar{K}$ is compact.
Assume radius of D is R, and $C = \partial D$, then
$$
|f^{(n)}(z_{0})|\leq \frac{n!}{2\pi} \int_{C} \frac{|f(\xi)|}{|(\xi-z)^{n+1}|}d\xi\leq \frac{n!}{2\pi}\int_{C} \frac{\sup_{C}|f|}{R^{n+1}}d\theta\leq \frac{n!}{R^{n}} \sup_{C}|f|\leq \frac{n!}{R^{n}}\sup_{\bar{K}}|f|
$$
