---
tags:
  - 复分析
  - 分析
---

# 1. Gamma函数的定义与基本性质

## 1.1 定义与在右半平面的解析性
**定义**：对于 $s > 0$，定义
$$
\Gamma(s)=\int_{0}^{+\infty} e^{-t}t^{s-1}  dt
$$
我们可以将 $\Gamma(s)$ 延拓到上半平面 $\mathrm{Re}(s) > 0$。

>[!命题]
>函数 $\Gamma :s\to \int_{0}^{+\infty} e^{-t}t^{s-1}  dt$ 在区域 $\{s\in \mathbb{C}\mid\mathrm{Re}(s)>0\}$ 上是良定义的全纯函数。

### 1.1.1 证明思路与过程
**证明思路**：通过在有限区间 $[\varepsilon, 1/\varepsilon]$ 上定义全纯函数 $\Gamma_{\varepsilon}(s)$，并证明其在任意紧集 $S_{\delta,M}=\{s\in \mathbb{C}\mid \delta<\mathrm{Re}s<M\}$ 上一致收敛于 $\Gamma(s)$。
1.  定义 $\Gamma_{\varepsilon}(s)=\int_{\varepsilon}^{\frac{1}{\varepsilon}} e^{-t}t^{s-1}  dt$。对于固定的 $s$，有 $\Gamma_{\varepsilon}(s)\to\Gamma(s)$（当 $\varepsilon \to0$）。由于被积函数关于 $s$ 全纯，$\Gamma_{\varepsilon}(s)$ 在 $S_{\delta,M}$ 上全纯。
2.  估计差值：
    $$
    \left| \Gamma(s)-\Gamma_{\varepsilon}(s) \right| \leq \left| \int_{0}^{\varepsilon} e^{-t}t^{s-1}  dt  \right| +\left| \int_{\frac{1}{\varepsilon}}^{+\infty} e^{-t}t^{s-1}  dt  \right|
    $$
3.  对第一部分，在 $S_{\delta,M}$ 上有：
    $$
    \left| \int_{0}^{\varepsilon} e^{-t}t^{s-1}  dt  \right| \leq \int_{0}^{\varepsilon} t^{\mathrm{Re}s-1}  dt=\frac{\varepsilon^{\mathrm{Re}s}}{\mathrm{Re}s}\leq \frac{\varepsilon^{\delta}}{\delta} \to 0 \quad (\varepsilon\to 0)
    $$
4.  对第二部分，在 $S_{\delta,M}$ 上有：
    $$
    \left| \int_{\frac{1}{\varepsilon}}^{+\infty} e^{-t}t^{s-1}  dt \right|\leq \int_{\frac{1}{\varepsilon}}^{+\infty} e^{-t}t^{M-1}  dt \to 0 \quad (\varepsilon\to 0)
    $$
    因为 $\int_{1}^{+\infty} e^{-t}t^{M-1}  dt$ 收敛。
5.  因此，在 $S_{\delta,M}$ 上 $\Gamma_{\varepsilon} \to \Gamma$ 一致收敛，故 $\Gamma(s)$ 在 $S_{\delta,M}$ 上全纯。由于 $\delta, M$ 任意，$\Gamma(s)$ 在 $\mathrm{Re}(s)>0$ 上全纯。

我们证明 $\Gamma$ 可以延拓为一个 $\mathbb{C}$ 上的亚纯函数。然而当 $\mathrm{Re}s\leq0$ 时，这个积分式子并不是良定义的。

## 1.2 函数方程与递推关系
**引理**：如果 $\mathrm{Re}s>0$，则有函数方程 $\Gamma(s+1)=s\Gamma(s)$。
结果推出 $\Gamma(n+1)=n!$, $n=0,1,2,\dots$。
### 1.2.1 证明过程
考虑下面这个关系
$$
\int_{\varepsilon}^{\frac{1}{\varepsilon}} \frac{d}{dt}(e^{-t}t^{s})  dt=-\int_{\varepsilon}^{\frac{1}{\varepsilon}} e^{-t}t^{s}  dt+s\int_{\varepsilon}^{\frac{1}{\varepsilon}} e^{-t}t^{s-1}  dx  =-\Gamma(s+1)+s\Gamma(s)
$$
然后左边等于
$$
\left[ e^{-t}t^{s} \right] _{\varepsilon}^{\frac{1}{\varepsilon}}=e^{^{-\frac{1}{\varepsilon}}}t^{\frac{1}{\varepsilon}}-e^{-\varepsilon}\varepsilon^{s}
$$
由于 $\mathrm{Re}s>0$, 所以两项都趋近于0。
并且 $\Gamma(1)=1$, 得出了结论。

# 2. Gamma函数的解析延拓

## 2.1 延拓为亚纯函数
>[!定理 1.3]
>函数 $\Gamma(s)$ 首先是定义在 $\mathrm{Re}(s)>0$ 上的，它可以解析延拓到整个复数集 $\mathbb{C}$ 上的亚纯函数，它的极点都是单极点，并且就是负整数 $s=0,-1, \cdots$ 。函数 $\Gamma$ 在极点 $s=-n$ 处的留数为 $(-1)^n / n!$ ．

### 2.1.1 证明思路 (利用递推关系)
**证明**：
对任意的 $m\in \mathbb{N}_{>0}$, 我们定义 $F_{m}(s)= \frac{\Gamma(s+m)}{(s+m-1)\dots(s+1)s}$ 。对 $s\in \mathbb{C}$, $\mathrm{Re}s>-m$，该函数全纯。
当 $\mathrm{Re}s>0$ 时，$F_m(s) = \Gamma(s)$。
对任意的 $m\in \mathbb{N}_{>0}$，对任意 $s\in \mathbb{C},\mathrm{Re}s>0$，我们有
$$
F_{m}(s)= \frac{\Gamma(s+m)}{(s+m-1)\dots(s+1)s}= \frac{\Gamma(s+m-1)\cdot(s+m-{1})}{(s+m-1)\dots(s+1)\cdot s}=F_{m-1}(s)=\dots=F(s)
$$
这暗示我们 $F_{m}$ 可以扩张 $\Gamma$ 到 $\{\mathrm{Re}s>-m\}$ 。通过唯一的解析延拓，我们得出 $F_{m}(s)=F_{n}(s)$ 对任意的 $m,n\in \mathbb{N}_{>0}$，以及 $\forall s\in \mathbb{C}, \mathrm{Re}s\ge-m,\mathrm{Re}s>-n$。

这里我们为了获得唯一的 $\Gamma$ 扩张，把 $\{F_{m}\}_{m=1}^{+\infty}$ 并起来？

### 2.1.2 证明思路 (利用级数展开)
**第二个证明**
对于 $\mathrm{Re}s>0$
$\Gamma(s)=\int_{0}^{+\infty} e^{-t}t^{s-1}  dt=\int_{0}^{1} e^{-t}t^{s-1}  dt +\int_{1}^{+\infty} e^{-t}t^{s-1}  dt$，后面的部分是一致可积的。
我们注意，$\forall m\in \mathbb{N}_{>0}$，有 $\left| e^{-t}t^{s-1} \right|\leq e^{-t}\cdot t^{\mathrm{Re}s-1}\leq e^{-t}\cdot t^{m-1}$，对任意的 $s\in \{\mathrm{Re}s<m\}$。
通过控制收敛定理，$s\to \int_{1}^{+\infty} e^{-t}t^{s-1}  dt$ 是在 $\{\mathrm{Re}s<m\}$ 上全纯的。因此，$s\to \int_{1}^{+\infty} e^{-t}t^{s-1}  dt$ 是在 $\mathbb{C}$ 上全纯的。

---

对 $\int_{0}^{1} e^{-t}t^{s-1}  dt$，我们首先注意到 $e^{-t}=\sum_{n=0}^{+\infty} \frac{(-1)^{n}t^{n}}{n!}$ 在 $\mathbb{C}$ 上收敛。
于是
$$
\int_{0}^{1} e^{-t}t^{s-1}  dt =\sum_{n=0}^{+\infty}  \frac{(-1)^{n}}{n!(n+s)}
$$
因此
$$
\Gamma(s)=\sum_{n=0}^{+\infty}  \frac{(-1)^{n}}{n!(n+s)}+\int_{1}^{+\infty} e^{-t}t^{s-1}  dt\quad \mathrm{Re}(s)>0
$$
我们令
$$
G(s)=\sum_{n=0}^{+\infty}  \frac{(-1)^{n}}{n!(n+s)}
$$
它对任意 $S\neq0,-1,-2\dots$ 是良定义的。因为 $\sum \frac{1}{n!}$ 是收敛的，所以 $G(s)$ 在任意紧集上一致收敛。
因此 $G(s)$ 是在 $\mathbb{C}-\{0,-1,-2,\dots\}$ 上全纯的。我们也得到了 $G(s)$ 是在 $\mathbb{C}$ 上亚全纯的，它在 $-n$ 的主部分等于 $\frac{(-1)^{n}}{n!(n+s)}$，所以留数是 $\frac{(-1)^{n}}{n!}$。

# 3. Gamma函数的函数方程与余元公式

## 3.1 余元公式 (反射公式)
>[!定理]
>对任意 $s\in \mathbb{C}$,
>$$
>\Gamma(1-s)\Gamma(s)= \frac{\pi}{\sin(\pi s)}
>$$
>注意这里 $s$ 可以等于 $0,-1,\dots$。

### 3.1.1 证明所需的引理
**引理**：
任意 $0<a<1$，我们有
$$
\int_{0}^{+\infty} \frac{\nu^{a-1}}{1+\nu}  d\nu=\frac{\pi}{\sin \pi a}
$$
*证明*：
我们让 $\nu=e^{x}$，那么 $\int_{0}^{+\infty} \frac{\nu^{a-1}}{1+\nu}  d\nu=\int_{-\infty}^{+\infty}  \frac{e^{(a-1)x}\cdot e^{x}}{1+e^{x}}  dx=\int_{-\infty}^{+\infty} \frac{e^{ax}}{1+e^{x}}  dx$。
为了计算这个积分，我们选取长方形的围道，顶点是 $R,R+2\pi i,-R+2\pi i,-R$。

### 3.1.2 主要证明过程
**证明**：
回忆 $\sin z= \frac{e^{iz}-e^{-iz}}{zi}$ 对 $\forall z\in \mathbb{C}$。
$0<s<1$，我们有 $\Gamma(1-s)=\int_{0}^{+\infty} e^{-u}u^{-s}  du=\int_{0}^{+\infty} e^{-\nu t}(\nu t)^{-s}  d\nu t$ 对任意的 $t>0$，固定 $\Gamma(1-s)=t\cdot \int_{0}^{+\infty} e^{-\nu t}(\nu t)^{-s}  dt$。
现在对 $0<s<1$，
$$
\begin{aligned}
\Gamma(s)\Gamma(1-s)&=\int_{0}^{+\infty} e^{-t}t^{s-1}  dt\int_{0}^{+\infty} e^{-u}u^{-s}  du =\int_{0}^{+\infty} e^{-t}t^{s-1}\left( \int_{0}^{+\infty} e^{-u}u^{-s}  du  \right)  dt \\
&=\int_{0}^{+\infty} \left( e^{-t}t^{s-1}\cdot t\cdot \int_{0}^{+\infty} e^{-\nu t}(\nu t)^{-s}  d\nu  \right)  dt \\
&=\int_{0}^{+\infty} \int_{0}^{+\infty} e^{-t}t^{s-1}te^{-\nu t}(\nu t)^{-s}  d\nu t  d \\
&=\int_{0}^{+\infty} \int_{0}^{+\infty} e^{-t(1+\nu)}\nu^{-s}  d\nu  dt \\
&=\int_{0}^{+\infty} \left( \int_{0}^{+\infty} e^{-t(1+\nu)}\nu^{-s}  dt  \right)  d\nu \\
&=\int_{0}^{+\infty} \frac{\nu^{-s}}{1+\nu}  dt= \frac{\pi}{\sin s \pi}
\end{aligned}
$$
因此两个全纯函数 $\Gamma(s)\Gamma(1-s)$ 和 $\frac{\pi}{\sin \pi s}$ 在 $\{0<s<1\}$ 上是全纯的。
通过孤立零点性质，我们知道它们是相等的。

# 4. Gamma函数的性质与无穷乘积

## 4.1 倒数Gamma函数的性质
**推论**：由余元公式可得 $\frac{1}{\Gamma(s)}= \frac{\sin \pi s}{\pi}\cdot\Gamma(1-s)$。

>[!定理 1.6]
>1.  $\frac{1}{\Gamma(s)}$ 是一个整函数，整数 $s=0,-1,\dots$ 是它的单零点，并且它不存在其他的零点。
>2.  函数 $\frac{1}{\Gamma(s)}$ 是指数增长的，存在 $\left| \frac{1}{\Gamma(s)} \right|\leq c_{1}e^{c_{2}\left| s \right|\log \left| s \right|}$，因此 $\frac{1}{\Gamma(s)}$ 是一阶的，意思是对任意的 $\varepsilon>0$，存在有界函数 $c(\varepsilon)$ 使得 $\left| \frac{1}{\Gamma(s)} \right|\leq c(\varepsilon)e^{c_{2}\left| s \right|^{1+\varepsilon}}$。

### 4.1.1 证明思路
**证明**：
1.  $\frac{1}{\Gamma(s)}= \frac{\sin \pi s}{\pi}\cdot\Gamma(1-s)$ 是亚全纯函数。可能的极点只有 $\Gamma(1-s)$ 的极点，也就是 $1,2,3,\dots$。但是它们都是单极点，而 $\frac{\sin \pi s}{\pi}$ 在 $1,2,\dots$ 有零点，因此极点被消去了。
2.  回忆
    $$
    \int_{0}^{1} e^{-t}t^{s-1}  dt =\sum_{n=0}^{+\infty}  \frac{(-1)^{n}}{n!(n+s)}
    $$
    我们有
    $$
    \Gamma(s)=\sum_{n=0}^{+\infty}  \frac{(-1)^{n}}{n!(n+s)}+\int_{1}^{+\infty} e^{-t}t^{s-1}  dt
    $$
    我们首先证明，如果 $\sigma=\mathrm{Re}(s)>0$
    $$
    \int_{1}^{+\infty} \left| e^{-t}t^{s} \right|  dt=\int_{1}^{+\infty} e^{-t}t^{\sigma}  dt \leq e^{(\sigma+1)\log(\sigma+1)}
    $$
    选择 $\sigma\leq n\leq\sigma+1$，当 $n\in \mathbb{Z}$, $n=[\sigma]+1$。
    那么 $\int_{1}^{+\infty}  e^{-t}t^{\sigma}  dt\leq \int_{0}^{+\infty} e^{-t}t^{n}  dt=\Gamma(n)=n!\leq n^{n}\leq e^{n\log n}\leq e^{(\sigma+1)\log(\sigma+1)}$。

    $$
    \frac{1}{\Gamma(s)}=\Gamma(1-s)\cdot \frac{\sin \pi s}{\pi}\leq \sum \frac{1}{n!(n+1-s)}\cdot \frac{\sin \pi s}{pi}+\int_{1}^{+\infty} e^{-t}t^{-s}  dt \cdot \frac{\sin \pi s}{\pi}
    $$
    回忆 $\sin \pi s= \frac{e^{i\pi s}-e^{-i\pi s}}{2i}$。$\left| \sin \pi s \right|\leq e^{\pi \left| s \right|}$。
    $$
    \left| \int_{1}^{+\infty} e^{-t}t^{-s}  dt  \right| \leq \int_{1}^{+\infty} e^{-t}\left| t^{-s} \right|  dt =\int_{1}^{+\infty} e^{-t}t^{-\mathrm{Re}(s)}  dt\leq \int_{1}^{+\infty} e^{t}t^{\left| s \right| }  dt
    $$
    因此，$\int_{1}^{+\infty} e^{t}t^{\left| s \right|}  dt\leq e^{(\left| s \right|+1)\cdot \log(\left| s \right|+1)}$。
    $$
    \left| \left( \int_{1}^{+\infty} e^{-t}t^{-s}  dt  \right)\cdot \frac{\sin \pi s}{\pi} \right| \leq \frac{1}{\pi}e^{\pi \left| s \right| +(\left| s \right| +1)\log(\left| s \right| +1)}
    $$
    因此被 $b_{1}e^{b_{2}\left| s \right|\log \left| s \right|}$ 控制。
    我们还需要对 $\sum_{n=0}^{+\infty} \frac{(-1)^{n}}{(n+1-s)} \frac{\sin \pi s}{\pi}$ 进行估计。
    $\left| \mathrm{Im}(s) \right|>1$，于是 $\left| n+1-s \right|\geq \left| \mathrm{Im}(s) \right|>1$。$\left| \sum_{n=0}^{+\infty} \frac{(-1)^{n}}{n!(n+1-s)} \right|\cdot \left| \frac{\sin \pi s}{\pi} \right|\leq \left( \sum_{n=0}^{+\infty} \frac{1}{n!} \right)\cdot \frac{e^{\pi \left| s \right|}}{\pi}= \frac{e}{\pi}e^{\pi \left| s \right|}$。

    $\left| \mathrm{Im}(s) \right|\leq1$
    选择 $k\geq0$，使得 $k-\frac{1}{2}\leq \mathrm{Re}(s)\leq k+\frac{1}{2}\implies \left| k-\mathrm{Re}(s) \right|\leq \frac{1}{2}$。
    那么，$\left| n+1-s \right|\geq \frac{1}{2}$，如果 $n\neq k-1$。
    对 $n=k-1$
    $\left| \frac{1}{n!(n+1-s)}\cdot \frac{\sin \pi s}{\pi} \right|=\left| \frac{1}{(k-1)!(k-s)} \frac{\sin\pi s}{\pi} \right|\leq \left| \frac{\sin \pi s}{k-s} \right|\cdot \frac{1}{\pi}$。
    对 $\frac{\sin \pi s}{k-s}$，我们设 $u=s-k$，那么 $\left| \frac{\sin \pi s}{k-s} \right|= \left| \frac{\sin(\pi(u+k))}{u} \right|=\left| \frac{\sin \pi u}{u} \right|$。注意到 $\left| u \right|\leq 2$ (因为 $\left| \mathrm{Re}(u) \right|\leq \frac{1}{2}$，并且 $\mathrm{Im}(u)\leq \frac{1}{2}$)。
    通过 Mean Value Theorem，$\exists v$ 在介于 $0,u$ 的区间当中，使得 $\sin \pi u-\sin \pi0=u\cdot(\pi \cos \pi v)$，而 $\sup_{\left| v \right|\leq\frac{1}{2}}(\sin \pi)'(v)=\sup_{\left| v \right|\leq\frac{1}{2}}\pi \cos \pi v\leq K$。也就是 $\left| \frac{\sin \pi s}{\pi} \right|\leq \frac{K}{\pi}$。
    因此
    $$
    \left| \sum \frac{(-1)^{n}}{n!(n+1-s)}\cdot \frac{\sin \pi s}{\pi} \right| \leq \frac{e}{\pi}e^{\pi \left| s \right| }+ \frac{K}{\pi}
    $$
    这完成了证明。

## 4.2 无穷乘积表示（魏尔斯特拉斯乘积）
**定义**（欧拉常数）：
$$
\gamma = \lim_{N\to+\infty} \left( \sum_{n=1}^{N} \frac{1}{n}-\log N \right)
$$
为了证明 $\gamma$ 是良定义的，我们设 $u_{n}=\frac{1}{n}-\int_{n}^{n+1} \frac{1}{n}  dx$。因此，$u_{n}=\int_{n}^{+\infty} \left( \frac{1}{n}-\frac{1}{x} \right)  dx\leq \int_{n}^{+\infty} \left( \frac{1}{n}-\frac{1}{n+1} \right)  dx\leq \int_{n}^{n+1} \frac{1}{n(n+1)}  dx\leq \frac{1}{(n+1)^{2}}$。
然后 $\sum_{n=1}^{N}u_{n}=\sum_{n=1}^{N}1/n-\log(N+1)=\left( \sum_{n=1}^{N} \frac{1}{n }-\log N \right)-\log\left( 1+\frac{1}{N} \right)$。
因此，$\sum_{n=1}^{+\infty}u_{n}$ 是绝对收敛的，又因为 $\log\left( 1+\frac{1}{N} \right)\to0$ ，当 $N\to+\infty$，我们得到 $\gamma=\sum_{n=1}^{+\infty}u_{n}$。

>[!定理 1.7]
>$$
>\frac{1}{\Gamma(s)}=e^{\gamma s}\cdot s \prod_{n=1}^{+\infty} \left( 1+ \frac{s}{n} \right)e^{-\frac{s}{n}}
>$$

### 4.2.1 证明思路
**证明定理1.7**
根据哈达玛乘积公式，因为 $\frac{1}{\Gamma(s)}$ 的增长阶数为 $1$，存在 $A,B>0$，使得
$$
\frac{1}{\Gamma(s)}=e^{As+B}\cdot \prod_{n=1}^{+\infty}\left( 1+ \frac{s}{n} \right)e^{-\frac{s}{n}}
$$
回忆 $\Gamma(s)$ 在 $0$ 的留数是 $1$。
$$
1=e^{B}(\Gamma(s)\cdot s)\left( e^{_{As}}\prod_{n=1}^{+\infty} \left( 1+ \frac{s}{n} \right)e^{-\frac{s}{n}} \right)\to e^{B}\quad \text{as}\left| s \right| \to0
$$
所以 $e^{B}=1$。
因此我们选择 $B=0$。
为了找到 $A$，我们用 $\Gamma(1)=1$。然后 $$1=e^{As}\prod_{n=1}^{+\infty}\left( \left( 1+\frac{1}{n} \right)e^{-\frac{1}{n}} \right)\iff1=e^{As}\cdot \prod_{n=1}^{+\infty}e^{\log\left( 1+\frac{1}{n} \right)-\frac{1}{n}}=e^{As}\left( e^{\prod_{n=1}^{+\infty}e^{\log\left( 1+\frac{1}{n} \right)-\frac{1}{n}}} \right)$$ **确定常数 $A$ (完成您笔记中断的部分)，这一部分是AI提供的**：利用条件 $\Gamma(1)=1$，即 $\frac{1}{\Gamma(1)}=1$。代入上式 ($s=1$)：
    $$
    1 = e^{A \cdot 1} \cdot 1 \cdot \prod_{n=1}^{\infty} \left(1+\frac{1}{n}\right)e^{-\frac{1}{n}}
    $$
    即：
    $$
    e^{-A} = \prod_{n=1}^{\infty} \left(1+\frac{1}{n}\right)e^{-\frac{1}{n}}
    $$
    现在计算右边的无穷乘积。考虑其部分乘积：
    $$
    \begin{aligned}
    \prod_{n=1}^{N} \left(1+\frac{1}{n}\right)e^{-\frac{1}{n}}
    &= \left( \prod_{n=1}^{N} \frac{n+1}{n} \right) \cdot \exp\left( -\sum_{n=1}^{N} \frac{1}{n} \right) \\
    &= (N+1) \cdot \exp\left( -\sum_{n=1}^{N} \frac{1}{n} \right) \quad \text{(因为连乘项相消)}
    \end{aligned}
    $$
    根据欧拉常数的定义 $\gamma = \lim_{N\to\infty} \left( \sum_{n=1}^{N} \frac{1}{n} - \log N \right)$，我们有 $\sum_{n=1}^{N} \frac{1}{n} = \log N + \gamma + o(1)$，其中 $o(1)$ 表示当 $N \to \infty$ 时趋于0的量。代入上式：
    $$
    \begin{aligned}
    (N+1) \cdot \exp\left( -\sum_{n=1}^{N} \frac{1}{n} \right)
    &= (N+1) \cdot \exp\left( -(\log N + \gamma + o(1)) \right) \\
    &= \frac{N+1}{N} \cdot e^{-\gamma} \cdot e^{o(1)}
    \end{aligned}
    $$
    令 $N \to \infty$，由于 $\frac{N+1}{N} \to 1$ 且 $e^{o(1)} \to 1$，我们得到：
    $$
    \prod_{n=1}^{\infty} \left(1+\frac{1}{n}\right)e^{-\frac{1}{n}} = e^{-\gamma}
    $$
    代回 $e^{-A} = e^{-\gamma}$，即得 $A = \gamma$。

综上，我们证明了：
$$
\frac{1}{\Gamma(s)} = e^{\gamma s} \cdot s \prod_{n=1}^{\infty} \left( 1 + \frac{s}{n} \right) e^{-\frac{s}{n}}
$$
定理证毕。