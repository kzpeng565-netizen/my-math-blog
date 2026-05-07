---
tags:
  - 复分析
  - 分析
---
定义
$$
\zeta(s)=\sum_{n=1}^{+\infty} \frac{1}{n^{s}}
$$
通过$s>1$时收敛定义, 类似于Gamma函数, 可以解析延拓到$\mathbb{C}$上

性质
$\zeta$可以延拓到一个全纯函数当$\mathrm{Re}(s)>1$.
Proof : Fix $\delta>0$, and we Consider s with $\operatorname{Re}(s) \geqslant 1 \times \delta>1$. Then, 

$$
\left|\frac{1}{n^s}\right|=\frac{1}{n^{\operatorname{Re}(s)}} \leqslant \frac{1}{n^{1+\delta}}
$$
因此$\sum \frac{1}{n^{s}}$在$\mathrm{Re}(s)>1+\delta$一致收敛, 因为$\frac{1}{n^{s}}$是全纯的, $\zeta(s)$在$\mathrm{Re}(s)>1+\delta$成立, $\delta$​	是任意的

为了延拓$\zeta$, 我们引入$\theta$函数
$\theta(t)=\sum_{n=-\infty}^{+\infty}e^{-\pi n^{2}t}$ 如果$f(x)=e^{-\pi xt}$, 那么$\theta(t)=\sum_{n=-\infty}^{+\infty}f(n)$ 
$f(x)$有一个moderate decrease, 我们考虑傅里叶变换
$\hat{f}(\xi)=t^{-\frac{1}{2}}e^{-\pi \xi^{2}t^{-1}}$ *(Page 120 if Chapter 4, Theorem 2.4)* 
傅里叶逆变换对$f(x)$成立.
因此, 我们可以用泊松求和公式
$$
\sum_{n=-\infty}^{+\infty} f(n)=\sum_{n=-\infty}^{+\infty} \hat{f}(n)
$$
因此, 我们有
$$
\sum_{n=-\infty}^{+\infty} e^{-\pi n^{2}t}=t^{-\frac{1}{2}}\sum_{n=-\infty}^{+\infty} e^{-\pi n^{2}t^{-1}}\iff \theta(t)=t^{-\frac{1}{2}}\theta(t^{-1})
$$
$$
\theta(t)=\sum_{n=-\infty}^{+\infty}e^{-\pi n^{2}t}=1+2\sum_{n=1}^{+\infty}e^{-\pi n^{2}t}
$$
$\left| \theta(t)-1 \right|\leq C\cdot e^{-\pi t}$ 对任意$t\geq​	1$ 对某个C成立;  $\theta(t)\leq C\cdot t^{-\frac{1}{2}}$ 对某个$C>0$, 任意$0<t<1$​	成立.

>[!三个函数的关系]
>如果$\mathrm{Re}(s)>1$, 那么
>$$
\pi^{-\frac{s}{2}}\Gamma\left( \frac{s}{2} \right)\zeta(s)=\frac{1}{2}\int_{0}^{+\infty} u^{\left( \frac{s}{2} \right)-1}[\theta(u)-1] \, du
>$$

$$
\int_{0}^{+\infty} e^{-\pi n^{2}u}u^{\frac{s}{2}-1} \, du=I_{n}
$$
令$t=\pi n^{2}u$ 换元得到
$$
I_{n}=\int_{0}^{+\infty} e^{-t}\left( \frac{t}{\pi n^{2}} \right)^{\frac{s}{2}-1}\cdot\left( \frac{1}{\pi n^{2}} \right) \, dt
$$
因为
$$
\Gamma\left( \frac{s}{2} \right)=\int_{0}^{+\infty} e^{-t}t^{\frac{s}{2}-1} \, dt
$$
代入得到
$$
I_{n}=\Gamma\left( \frac{s}{2} \right)(\pi n^{2})^{-\frac{s}{2}}=\pi^{-\frac{s}{2}}\Gamma\left( \frac{s}{2} \right)n^{-s}
$$

固定$s_{0}$, $\mathrm{Re}s_{0}\geq1+\delta>1$. 对于任意的$\left| s-s_{0} \right|<\frac{\delta}{2}$, $\mathrm{Re}s\geq\frac{\delta}{2}+1>1$. 
于是有
$$
\left| \left( u^{\frac{s}{2}-1} \right)(\theta(u)-1) \right|\leq u^{\frac{1+\delta}{2}-1}\cdot C\cdot u^{-\frac{1}{2}}\leq C\cdot u^{\frac{\delta}{2}-1}
$$
对某个常数$C$, $0<u\leq1,\left| s-s_{0} \right|<\frac{\delta}{2}$成立.
如果$\mathrm{Re}s_{0}\leq M$, 那么
$$
\left| \left( u^{\frac{s}{2}-1} \right)Ce^{-\pi u} \right| \leq u^{\frac{M+\delta}{2}}Ce^{-\pi u}
$$
对$u\geq1$, $\left| s-s_{0} \right|\leq\frac{\delta}{2},C>0$​	成立
因此如果 $\theta_{N}(u)=1+\sum_{n=1}^{N}e^{-\pi n^{2}u}$,则 $\theta_{N}(u)\to \theta(u),N\to+\infty$. 并且$\int_{0}^{+\infty} (\theta_{N}(u)-1)u^{\frac{s}{2}-1} \, du$ 是一致可积的.
对任意$N$, 任意$s$ 满足$\left| s-s_{0} \right|\leq\frac{\delta}{2}$
$$
\lim_{N\to\infty} \int_{0}^{+\infty} u^{\frac{s}{2}-1}[\theta_{N}(u)-1] \, du=\int_{0}^{+\infty} u^{\frac{s}{2}-1}(\lim_{N\to\infty} \theta_{N}(u)-1) \, du=\int_{0}^{+\infty}u^{\frac{s}{2}-1}(\theta(u)-1)​	  \, du   
$$
注意
$$
\int_{0}^{+\infty} u^{\frac{s}{2}-1}(\theta_{N}(u)-1) \, du=\int_{0}^{+\infty} u^{\frac{s}{2}-1}\left( 2\sum_{n=1}^{N} e^{-\pi n^{2}u} \right) \, du=2\sum_{n=1}^{N} I_{n}(s)=2\pi^{-\frac{s}{2}}\Gamma\left( \frac{s}{2} \right)\sum_{n=1}^{N} n^{-s}
$$
对$\mathrm{Re}s>1$​	成立, 因此
$$
\pi^{-\frac{s}{2}}\Gamma\left( \frac{s}{2} \right)\zeta(s)=\frac{1}{2}\int_{0}^{+\infty} u^{\left( \frac{s}{2} \right)-1}[\theta(u)-1] \, du
$$
定义$\xi(s)=\pi^{-\frac{s}{2}}\Gamma\left( \frac{s}{2} \right)\zeta(s)$称为$\xi$函数, 是$\zeta$函数的修正函数, $\xi(s)=\frac{1}{2}\int_{0}^{+\infty} u^{\frac{s}{2}-1}(\theta(u)-1) \, du$ 
>[!xi函数的性质]
>当$\mathrm{Re}(s)>1$​	时, $\xi$函数是全纯的. 并且可以解析延拓到整个复平面$\mathbb{C}$上全纯, 且$s=0,s=1$是它的极点, 而且是单的. 此外, 对于任意的$s\in \mathbb{C}$, 
>$$
\xi(s)=\xi(1-s)\quad \text{关于}\mathrm{Re}=\frac{1}{2}\text{对称}
$$

证明
$\theta(u)=u^{-\frac{1}{2}}\theta(u^{-1})$  for $u>0$. 令$\psi(u)=\frac{1}{2}(\theta(u)-1),\psi(u)=\sum_{n=1}^{+\infty}e^{-\pi n^{2}u}$.
$$
(2\psi(u)+1)=u^{-\frac{1}{2}}(2\psi(u^{-1})+1)
$$
$$
\psi(u)=u^{-\frac{1}{2}}\psi(u^{-1})-\frac{1}{2}+\frac{1}{2}u^{-\frac{1}{2}}
$$
根据上一个定理的结论, $\xi(s)=\frac{1}{2}\int_{0}^{+\infty} u^{\frac{s}{2}-1}(\theta(u)-1) \, du$
$$
\xi(s)=\int_{0}^{+\infty}u^{\frac{s}{2}-1}\psi(u)  \, du=\int_{0}^{1}+\int_{1}^{+\infty}=\int_{0}^{1} u^{\frac{s}{2}-1}\left( u^{-\frac{1}{2}}\psi\left( \frac{1}{u} \right)-\frac{1}{2}+\frac{1}{2}u^{-\frac{1}{2}} \right) \, du+\int_{1}^{+\infty} u^{\frac{s}{2}-1}\psi(u) \, du
$$
我们考虑
$$
A(s)=\int_{0}^{1} u^{\frac{s}{2}-1}\left( u^{-\frac{1}{2}}\psi(u^{-1}) -\frac{1}{2}+\frac{1}{2}u^{-\frac{1}{2}}\right) \, du
$$
$$
\int_{0}^{1} \frac{1}{2}u^{\frac{s}{2}-1} \, du=\frac{1}{s}
$$
$$
\int_{0}^{1} \frac{1}{2}u^{\frac{s-3}{2}} \, du= \frac{1}{s-1}
$$
​	$$
\int_{0}^{1} u^{\frac{s-3}{2}}\psi(u^{-1}) \, du=\int_{1}^{+\infty} t^{\frac{-s-2}{2}}\psi(t) \, dt\quad (t=u^{-1})
$$
我们计算得到
$$
A(s)=-\frac{1}{s}+\frac{1}{s-1}+\int_{1}^{+\infty} t^{\frac{-s-1}{2}}\psi(t)​	 \, dt
$$
$$
\xi(s)=\frac{1}{s-1}+\frac{1}{s}+\int_{1}^{+\infty} \left( u^{\frac{-s-1}{2}}+u^{\frac{s}{2}-1} \right)\psi(u) \, du
$$
注意到$\int_{1}^{+\infty} \left( u^{\frac{-s-1}{2}}+u^{\frac{s}{2}-1} \right)\psi(u) \, du$是一个$s\in \mathbb{C}$上全纯的函数, 因为$\psi(u)$在无穷远处指数衰减, $\psi (u)\le Ce^{-\pi u}$.
所以$\xi(s)$是$\mathbb{C}$上的全纯函数.

>[!zeta函数的极点]
>$\xi(s)$是$\mathbb{C}$上的亚全纯函数, 在1有唯一的单极点

证明
回忆$\frac{1}{\Gamma(s)}$是全纯函数, 具有单零点$0,-1,-2,\dots$ 因此$\frac{1}{\Gamma\left( \frac{s}{2} \right)}$有零点$0,-2,-4\dots$ 
$\xi(s)$在0, -1 有单极点, 因此$\zeta(s)$在$s=1$有唯一一个单极点
它的留数是
$$
\text{Res}_{i}\zeta=\frac{1}{\Gamma\left( \frac{s}{2} \right)}\pi^{\frac{1}{2}}\text{Res}(\xi)=\frac{1}{\sqrt{\pi}}\cdot \sqrt{\pi}\cdot1=1
$$

另一个$\zeta(s)$解析延拓证明
考虑 $\frac{1}{n^{s}}-\int_{n}^{n+1} \frac{1}{x^{s}} \, dx=\int_{n}^{n+1} \left( \frac{1}{n^{s}}-\frac{1}{x^{s}} \right) \, dx=\delta_{n}(s)$
注意到
$$
\sum_{k=1}^{N} \delta_{n}(s)=\sum_{n=1}^{N} \frac{1}{n^{s}}-\int_{1}^{n+1} \frac{1}{x^{s}} \, dx
$$
当$\mathrm{Re}s>1$,我们取$N\to+\infty$的极限, 得到了
$$
\sum_{n=1}^{+\infty} \delta_{n}(s)=\zeta(s)-\int_{1}^{+\infty} \frac{1}{x^{s}} \, dx =\zeta(s)-\frac{1}{s-1}
$$
对$s=\sigma+it,\sigma>0$​	
$$
\left| \delta_{n}(s) \right| \leq \int_{n}^{n+1} \left| \frac{1}{n^{s}}-\frac{1}{x^{s}} \right|​  \, dx 
$$​根据中值公式, $x\in[n,n+1],\exists y\in[n,x]$使得$\frac{1}{x^{s}}-\frac{1}{n^{s}}=(x-n)\cdot \frac{-s}{y^{s+1}}$
因此
$$
\left| \delta_{n}(s) \right| \leq \int_{n}^{n+1} \left| (x-n)\cdot  \frac{s}{y^{s+1}} \right|  \, dx \leq \int_{n}^{n+1} \frac{\left| s \right| }{n^{\delta+1}} \, dx = \frac{\left| s \right| }{n^{\delta+1}}
$$
因此, $\sum_{n=1}^{+\infty}\delta_{n}(s)$在$\{\mathrm{Re}s>0\}$的紧集内一致收敛
因此 $\sum_{n=1}^{+\infty}\delta_{n}(s)$是一个全纯函数在$\mathrm{Re}s>0$​	
我们设$H(s)=\sum_{n=1}^{+\infty}\delta_{n}(s)$, 然后 $\zeta(s)=\frac{1}{s-1}+H(s)$在$\mathrm{Re}s>0$​	

性质
假设$s=\sigma+it$ $\sigma>0$, 然后对$0\leq\sigma\leq1$, 任意$\varepsilon>0$, 存在常数 $C_{\varepsilon}$使得
1. $\left| \zeta(ss) \right|\leq C_{\varepsilon}\left| t \right|^{1-\sigma_{0}+\varepsilon}$​	如果$\sigma_{0}\leq\sigma,\left| t \right|\geq1$
2. $\left| \zeta(s) \right|\leq C_{\varepsilon}\left| t \right|^{s}$, 如果$1\leq\sigma$, $\left| t \right|\geq1$
这个性质是关于$\zeta(\sigma+it)$ 当$t\to+\infty$. 如果$\sigma\geq1$, $\left| \zeta(\sigma+it) \right|$的增长是相当缓慢的.
事实上, 对$\sigma>1$, $\left| \zeta(s) \right|\leq \zeta(\sigma)(\text{依赖于})t$
如果$\sigma<1$, 1.告诉我们$\left| \zeta(\sigma+it) \right|$增长得非常快, 如果$\sigma$接近于$1$

2是关于$\zeta$的相似性质

证明.
对于$\sigma>0$, 我们有$\zeta(s)= \frac{1}{s-1}+H(s)$. 
$$
\left| \zeta(s) \right| \leq \left| \frac{1}{s-1} \right| +\left| H(s) \right| \leq\frac{1}{\sqrt{s^{2}+(\sigma-1)^{2}}}+\left| H(s) \right| \leq\frac{1}{\left| t \right| }+\left| H(s) \right|
$$
$H(s)=\sum_{n=1}^{+\infty}\delta_{n}(s)$
我们可以看到$\left| \delta_{n}(s) \right|\leq \frac{\left| s \right|}{n^{1+\sigma}}$. 但是, $\left| \delta_{n}(s) \right|\leq \int_{n}^{n+1} \left( \left| \frac{1}{n^{s}} \right| +\left| \frac{1}{x^{s}} \right|\right) \, dx\leq \frac{2}{n^{s}}$ 
对任意的$0\leq\delta\leq1$, 我们考虑$\sigma\geq\sigma_{0}$ 
$$
\sigma_{n}(s)=\left| \delta_{n}(s) \right| ^{\delta}\left| \delta_{n}(s) \right| ^{1-\delta}\leq \frac{\left| s \right| ^{\delta}}{n^{(1+\sigma_{0})\delta}}\cdot \frac{2^{1-\delta}}{n^{\sigma_{0}(1-\delta)}}= 2^{1-\delta} \frac{\left| s \right| ^{\delta}}{n^{\delta+\sigma_{0}}}
$$
注意到$\left| s \right|^{\delta}\leq(\left| \sigma \right|+\left| t \right|)^{\delta}$. 为了求和$\sum \frac{1}{n^{\delta+\sigma_{0}}}$, 我们需要$\delta+\sigma_{0}>1$. 因此设$\delta=1-\delta_{0}+\varepsilon_{0}\implies \left| H(s) \right|\leq 2^{1-\delta}(\sum \frac{1}{n^{\delta+\sigma_{0}}})\cdot \left| s \right|^{10\delta_{0}+\varepsilon}$​	 

>[!命题:​]
>$s=\sigma+it$, 其中 $\sigma,t\in \mathbb{R}$, 那么对任意的$\sigma_{0}$$(0\leq\sigma_{0}\leq1)$ 和任意的$\varepsilon>0$, 存在常数$c_{\varepsilon}$使得
>1. 如果$\sigma_{0}\leq\sigma$, $\left| t \right|\geq1$, 那么 $\left| \zeta(s) \right|\leq c_{\varepsilon}\left| t \right|^{1-\sigma_{0}+\varepsilon}$
>2. 如果$1\leq\sigma,\: \left| t \right|\geq1$, 那么 $\left| \zeta'(s) \right|\leq c_{\varepsilon}\left| t \right|^{\varepsilon}$

