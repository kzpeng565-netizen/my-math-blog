$$
\left\{\begin{array}{l}
\frac{\partial^2 u}{\partial t^2}-a^2 \frac{\partial^2 u}{\partial x^2}=f(x, t) \\
t=0: u=0, \frac{\partial u}{\partial t}=0
\end{array}\right.
$$

根据物理学, $f(x,t)$的物理意义是, 在$t$时刻, $x$位置, 单位质量受到的外力.

**物理想法:** 我们在$\tau$时刻, 极小时间范围内考虑一个力的作用, 在这种情况下, 由于作用时间极短, 只改变了初始的速度, 仍然为齐次演化, 波函数记为$W(x,t,\tau)$. 由于波函数线性叠加, 把$W(x,t,\tau)$每一个时间$\tau$都求和, 就得到了$u(x,t)$.

在$\Delta t_{1}$的时刻, $f(x,t)=f(x,t_{1})$, 
根据动量定理$f(x,t_{1})\Delta t_{1}$代表受力转化为的速度
$$
\begin{cases}
\frac{\partial^{2}W}{\partial t^{2}} -a^{2}\frac{\partial^{2}W}{\partial x^{2}} =0 \\
t=t_{1} : W=0,\frac{\partial W}{\partial t} =f(x,t_{1})\Delta t_{1} 
\end{cases}
$$
于是
$$
u=\lim_{\lambda(P)\to0} \sum W_{i}
$$
但是, 由于$W_{i}$在初始的速度是一个无穷小量, 不太符合教科书的通用函数的定义, 取$W_{i}'=\frac{W_{i}}{\Delta t_{1}}$, 也就是初值取为$f(x,t_{1})$. 这样
$$
u=\lim_{\lambda(P)\to0} \sum W_{i}'\Delta t_{i}=\int_{0}^{t} W(x,t,\tau) \, d\tau
$$

