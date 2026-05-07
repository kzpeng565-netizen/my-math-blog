---
tags:
  - 复分析
  - 分析
---
# 1. Jensen Formula

> [!Note] Jensen Formula(零点个数与模长对数平均)
>设 $\Omega$ 表示包含圆盘 $D_R$ 的闭包的开集，$f$ 在 $\Omega$ 上全纯，$f(0) \ne 0$，在 $C_R$ 上不等于 0。如果 $z_1, \dots, z_N$ 表示 $f$ 在圆盘内的零点（包含重数），那么
>$$
> \log |f(0)| = \sum_{k=1}^{N} \log\left( \frac{|z_k|}{R} \right) + \frac{1}{2\pi}\int_{0}^{2\pi} \log |f(R e^{i\theta})| \, d\theta
>$$

**Remark**
$\frac{1}{2\pi}\int_{0}^{2\pi} \log |f(re^{i\theta})| \, d\theta = \frac{1}{2\pi R}\int_{0}^{2\pi} \log |f(Re^{i\theta})| \, R d\theta$ 是平均值。

## 1.1 证明

### 1.1.1 第一步：乘积性质
如果 $f_1, f_2$ 都满足 Jensen Formula，那么 $f_1 f_2$ 也满足公式，这是因为 $\log(|f_1 f_2|) = \log |f_1| + \log |f_2|$。

### 1.1.2 第二步：构造无零点函数
考虑
$$
g(z) = \frac{f(z)}{(z-z_1)\dots(z-z_N)}
$$
这个函数在每一个 $z_j$ 附近有界。
因为，在 $z_j$ 局部，$f(z) = (z-z_j)^{n_j} h(z)$，$h(z) \ne 0$ 在 $z_j$ 邻域中。但我们已经把零点除去，所以在局部是有界的，并且是全纯的（全纯通过局部性质验证）。
我们有
$$
f(z) = g(z) \cdot \prod_{k=1}^{N} (z-z_k)
$$

### 1.1.3 第三步：无零点情形
首先证明在 $D_R$ 的闭包上没有零点的函数 $g$ 满足公式。
$$
\log |g(0)| = \frac{1}{2\pi}\int_{0}^{2\pi} \log |g(Re^{i\theta})| \, d\theta
$$
这是调和函数的性质（[[复分析10 Complex Logarithm#2.1 Mean Value Equality| Mean Value Equality]]）。
调和函数在单连通区域内一定是一个调和函数的实部。因为 $g$ 是连续的，并且 $g(z) \ne 0$ 对所有的闭包 $\overline{D_R}$ 内，所以我们可以把圆盘的范围放大。在这个圆盘内没有零点，由于是单连通区域，存在对数。
我们可以记 $g(z) = e^{h(z)}$，那么 $|g| = e^{\mathrm{Re}\, h}$，所以 $\mathrm{Re}\, h = \log |g|$。

### 1.1.4 第四步：基本因子情形
我们证明函数形如 $f(z) = z - w$ 满足 Jensen 公式，其中 $w \in D_R$。也就是要证明
$$
\log |w| = \log(|w|/R) + \frac{1}{2\pi}\int_{0}^{2\pi} \log |Re^{i\theta} - w| \, d\theta
$$
因为 $\log(|w|/R) = \log |w| - \log R$，$\log |Re^{i\theta} - w| = \log R + \log |e^{i\theta} - \frac{w}{R}|$，只要证明当 $|a| < 1$ 时，有
$$
\int_{0}^{2\pi} \log |e^{i\theta} - a| \, d\theta = 0 \iff \int_{0}^{2\pi} \log |1 - a e^{i\theta}| \, d\theta = 0
$$
设 $F(z) = 1 - az$，$z \in D_R$，$|a| < 1$。*（原笔记为 $|a| > 1$，根据上下文逻辑应为 $|a| < 1$）*
因此 $F(z)$ 在略大于 $D_R$ 的开圆盘中存在全纯函数 $G$ 使得 $F(z) = e^{G(z)}$，也就是 $\log |F(z)| = \mathrm{Re}\, G(z)$。根据调和函数的平均值性质，
$$
\int_{0}^{2\pi} \log |F(\theta)| \, d\theta = \mathrm{Re}\, G(0) = 0
$$
这就完成了 Jensen 公式的证明。

# 2. Infinite Products

给出复数序列 $\{a_n\}$，我们说乘积 $\prod_{n=1}^{+\infty} (1+a_n)$ 是收敛的，只要 $\lim_{N\to\infty} \prod_{n=1}^{N} (1+a_n)$ 极限存在。
%%在一些文献中还会要求极限不等于0%%

> [!Note] Proposition
>假定 $\sum_{n=1}^{+\infty} |a_n| < +\infty$，那么 $\prod_{n=1}^{+\infty} (1+a_n)$ 是收敛的。而且，$\prod_{n=1}^{+\infty} (1+a_n) = 0 \iff \exists k, a_k = -1$。

**证明思路：**
存在 $N \in \mathbb{N}$，使得 $|a_n| < \frac{1}{2}$。此时，可以取 $\log(1+a_n)$，并且此对数只要 $|z| < 1$ 就有 $1+z = e^{\log(1+z)}$。
$$
\prod_{n=1}^{N} (1+a_n) = \prod_{n=1}^{N} e^{\log(1+a_n)} = e^{B_N}
$$
其中 $b_n = \log(1+a_n)$，$B_N = \sum_{n=1}^{N} b_n$。根据幂级数展开可以知道，如果 $|z| < \frac{1}{2}$，那么 $|\log(1+z)| \le 2 |z|$。 %%由于复对数在模长上的处理与实数相同，也可以通过实数的结论推出%%
因此 $|b_n| \le 2 |a_n|$，根据 Cauchy 收敛定理（或者比较收敛），$b_n$ 也是收敛的，收敛到 $B$。

## 2.1 全纯函数无穷乘积的性质

$\{F_n\}$ 是定义在 $\Omega$ 开集的全纯函数列，存在常数 $c_n > 0$ 使得 $\forall z \in \Omega$ 满足
$$
\sum c_n < +\infty,\ \text{ and } |F_n(z) - 1| \le c_n
$$
那么：
1. $\prod_{n=1}^{+\infty} F_n(z)$ 在 $\Omega$ 内一致收敛于全纯函数 $F(z)$。
2. 如果 $F_n$ 都不等于 0，那么 $\frac{F'(z)}{F(z)} = \sum_{n=1}^{+\infty} \frac{F_n'(z)}{F_n(z)}$。

**证明：**
### 2.1.1 一致收敛性证明
先证明 1。
与前面相同。我们假定 $c_n < \frac{1}{2}$。设 $G_N(z) = \prod_{n=1}^{N} F_n(z)$。首先我们假设 $\Omega$ 是单连通的。那么 $\log F_n(z)$ 存在。
因为 $|F_n(z)| = |F_n(z)-1+1| \ge 1 - |c_n| > \frac{1}{2}$，所以 $\sum_{n=1}^{+\infty} \log F_n(z)$ 一致收敛，收敛速度被 $\sum c_n$ 控制。因此
$$
\lim_{N\to\infty} G_N = \prod_{n=1}^{+\infty} F_n(z) = e^{\sum_{n=1}^{+\infty} \log F_n(z)}
$$
一致收敛于 $\Omega$。

在普遍的情形下，$\Omega$ 不是单连通的。但是 $\Omega$ 可以被单连通的开圆盘覆盖。正如我们所言，$\prod F_n(z)$ 可以在这些开圆盘内一致收敛，速度被 $\sum c_n$ 控制，因此 $\prod F_n(z)$ 在 $\Omega$ 上一致收敛。

### 2.1.2 对数导数公式证明
证明 2。
$\sum_{n=1}^{N} \log F_n(z)$ 在 $D_R(z)$ 内一致收敛到 $\log F(z)$，因此
$$
\frac{d}{dz}\left( \sum_{n=1}^{N} \log F_n(z) \right) \text{ converge to } \frac{d}{dz}(\log F(z)) \text{ uniformly on } D_{\frac{r}{2}}(z)
$$
这意味着
$$
\frac{F'(z)}{F(z)} = \sum_{n=1}^{+\infty} \frac{F_n'(z)}{F_n(z)}
$$

# 3. Weierstrass Product

> [!Note] Theorem
>给定任意 $a_n$，$\lim_{n\to\infty} |a_n| = +\infty$，存在整函数 $f$，满足 $z=a_n$ 处为 0，其余地方没有零点。
进一步地，对于任何其他的整函数 $F$，我们有 $F(z) = f(z) e^{g(z)}$，这里 $g(z)$ 是某一个整函数。

**证明思路：**
假设 $f$ 存在，那么 $\frac{F(z)}{f(z)}$ 是在 $\mathbb{C}$ 上全纯函数，并且没有零点。
因为 $\mathbb{C}$ 是单连通的，我们有 $\frac{F(z)}{f(z)} = e^{g(z)}$。

现在我们构造 $f$。
一个简单的想法是，令 $f(z) = \prod_{n=1}^{+\infty} \left( 1 - \frac{z}{a_n} \right)$，这可能不收敛，例如 $a_n = n$，因此我们需要对 $1 - \frac{z}{a_n}$ 进行修改。
对于 $k \in \mathbb{Z}_{\ge 0}$，我们定义 $E_0(z) = 1-z$，$E_k(z) = (1-z)e^{z + \frac{z^2}{2} + \dots + \frac{z^k}{k}}$。
那么，$E_k(z)$ 是一个整函数，并且在 1 处有且只有一个零点。
通过除去 $\{a_n\}$ 中的 0，我们可以选择 $f(z) = z^m \prod_{n=1}^{+\infty} E_n \left( \frac{z}{a_n} \right)$。
接下来证明这个乘积是收敛的，并且符合要求。

> [!Note] Lemma
>假定 $|z| \le \frac{1}{2}$，则 $|E_k(z) - 1| \le c \cdot |z|^{k+1}$ 对 $k \ge 1$，这里 $c = 2e$。

**引理证明：**
在 $D_{\frac{2}{3}}(0)$ 这个圆盘内，$z \to 1-z$ 这个函数是没有零点的，所以可以定义 $\log(1-z)$，使得 $\log(1-0)=0$ *（$\log$ 是多值函数，这里取其中一支）*。
我们把 $\log(1-z)$ 在这个圆盘上级数展开，使得收敛半径至少为 $\frac{2}{3}$。
我们有 $\log(1-z) = -z - \frac{z^2}{2} - \frac{z^3}{3} - \dots$。
因此
$$
|E_k(z) - 1| = \left| e^{\log(1-z) + \sum_{n=1}^{k} \frac{z^n}{n}} - 1 \right| = \left| e^{-\sum_{n=k+1}^{\infty} \frac{z^n}{n}} - 1 \right|
$$
对任意 $k \ge 1$，$|z| \le \frac{1}{2}$。
令 $w = -\sum_{n=k+1}^{+\infty} \frac{z^n}{n}$。然后 $|w| \le \sum_{n=k+1}^{+\infty} |z|^n = \frac{|z|^{n+1}}{1-|z|} \le |z|^{k+1} \cdot \frac{1}{1-\frac{1}{2}} = 2|z|^{k+1}$。
然后 $|w| \le 2 \cdot \left| \frac{1}{2} \right|^{k+1} \le \frac{1}{2}$。
回忆 $e^t - 1 = e^s t$ 存在 $s$ 位于 $0, t$ 之间的线段上，$t \in \mathbb{C}$。*（这里老师应该写的不对，应该写成模长有微分中值）*
因此，$|e^{-W} - 1| = |e^s \cdot (-W)|$ 对某个 $s$ 介于 $W, 0$ 之间成立。
因为 $|w| \le \frac{1}{2}$，我们有 $|s| \le \frac{1}{2}$，所以 $|e^s| = e^{\mathrm{Re}\, s} \le e^{|s|} \le e$。
这可以推出
$$
|E_k(z) - 1| = |e^{-w} - 1| = |e^s (-w)| \le e \cdot |w| \le 2e |z|^{k+1}
$$
这完成了证明。

**定理的构造证明：**
现在，我们继续证明定理。
通过移除 $a_n$ 中的 0，我们假定对于任意的 $n, a_n \ne 0$。
我们令 $f(z) = \prod_{n=1}^{+\infty} E_n \left( \frac{z}{a_n} \right)$。我们可以断言：$f$ 定义了一个整函数。我们只需要证明对任意固定的 $R > 0$，$f$ 在 $D_R(0)$ 上全纯。
固定 $R > 0$，因为 $|a_n| \to +\infty$，存在 $k \in \mathbb{N}_{\ge 2}$ 使得 $|a_n| \ge 2R$ 如果 $n \ge k$。
我们写成 $f(z) = \underbrace{\prod_{n=1}^{k} E_n \left( \frac{z}{a_n} \right)}_{h(z)} \underbrace{\prod_{n=k+1}^{+\infty} E_n \left( \frac{z}{a_n} \right)}_{\varphi(z)}$。
我们只需要证明 $\varphi(z)$ 是全纯的在 $D_R(0)$ 内。
由于我们有 $\left| \frac{z}{a_n} \right| \le \frac{R}{2R} = \frac{1}{2}$，所以 $\left| E_n \left( \frac{z}{a_n} \right) - 1 \right| \le 2e \cdot \left| \frac{z}{a_n} \right|^{n+1} \le 2e \cdot \left( \frac{1}{2} \right)^{n+1}$。
因此这个无穷乘积是一致收敛的，从而定义了一个全纯函数，完成了证明。

# 4. 有限阶函数 Function of finite order

**定义**: 令$f$是一个整函数, 我们说$f$的**阶小于**$\rho\in \mathbb{R}$, 如果$\exists A,B>0$, 使得 $\left| f(z) \right|\leq A\cdot e^{B\left| z \right|^{\rho}}$ 
这关系到$f$在无穷远处的行为. 我们定义**函数f的阶**$\rho_{f}=\inf\rho$, $\rho$是满足阶数大于$f$的值

> [!Note] 哈达马因子分解定理 (Hadamard Factoriaztion Theorem)
令$f:\mathbb{C}\to \mathbb{C}$是一个增长阶数为$\rho_{0}$的整函数. $k=[\rho_{0}]$代表向下取整的整数.
如果$\{a_{n}\}$是$f$的零点, 且$a_{n}\neq0\forall n$, 那么存在多项式$P$, $\text{degree }P\leq k$ 使得
>$$
>f(z)=e^{P(z)}z^{m}\prod_{n=1}^{+\infty}E_{n}\left( \frac{z}{a_{n}} \right)
>$$

**Remark** 不是所有的整函数都是有限阶增长的, 例如$f(z)=e^{e^{z}}$​	

%%老师没有讲解定理的证明%%