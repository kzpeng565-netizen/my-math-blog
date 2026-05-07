[文件名称]: fouriertransform.pdf
[文件内容开始]

===== 第 1 页 =====

## 1 傅里叶变换

回忆对于一个函数 $f(x):[-L,L]\rightarrow\mathbb{C}$，我们有正交展开式

$$f(x)=\sum_{n=-\infty}^{\infty}c_{n}e^{in\pi x/L},\quad c_{n}=\frac{1}{2L}\int_{- L}^{L}f(y)e^{-in\pi y/L}dy。$$ (1)

我们将 $c_{n}$ 视为代表函数 $f(x)$ 中所包含的具有波数 $k_{n}=n\pi/L$ 的特定本征函数的"数量"。那么，如果 $L$ 趋于 $\infty$ 会怎样？注意允许的波数变得越来越密集。因此，当 $L=\infty$ 时，我们期望 $f(x)$ 是对应于每个波数 $k\in\mathbb{R}$ 的不可数多个波的叠加，这可以通过将 $f(x)$ 写成关于 $k$ 的积分而不是关于 $n$ 的和来实现。

现在，让我们形式上取极限 $L\rightarrow\infty$。令 $k_{n}=n\pi/L$ 且 $\Delta k=\pi/L$，并使用 (1)，可以写出

$$f(x)=\frac{1}{2\pi}\sum_{n=-\infty}^{\infty}\left(\int_{-L}^{L}f(y)e^{-ik_{n}y}dy \right)e^{ik_{n}x}\Delta k。$$

注意这是区间 $k\in(-\infty,\infty)$ 上积分的黎曼和。取 $L\rightarrow\infty$ 等价于取 $\Delta k\to 0$，从而得到

$$f(x)=\frac{1}{2\pi}\int_{-\infty}^{\infty}F(k)e^{ikx}dk，$$ (2)

其中

$$F(k)=\int_{-\infty}^{\infty}f(x)e^{-ikx}dx。$$ (3)

函数 $F(k)$ 是 $f(x)$ 的 _傅里叶变换_。_逆变换_ 由公式 (2) 给出。（注意，定义傅里叶变换还有其他约定）。我们通常使用记号 $\hat{f}(k)$ 表示傅里叶变换，$\hat{F}(x)$ 表示逆变换，而不是大写字母。

### 傅里叶变换的实际应用

傅里叶变换在微分方程中非常有益，因为它可以将它们重新表述为更容易解决的问题。此外，许多变换只需对感兴趣的问题应用预定义的公式即可完成。下面给出了一个简短的变换表和某些性质。这些结果大多来自对积分 (3) 和 (2) 使用初等微积分技术，尽管有几个需要复分析的技术。

===== 第 2 页 [文本层] =====

简短的傅里叶变换表
描述
函数
变换
x 中的 Delta 函数
δ(x)
1
k 中的 Delta 函数
1
2πδ(k)
x 中的指数函数
e−a|x|
2a / (a² + k²)
(a > 0)
k 中的指数函数
2a / (a² + x²)
2πe−a|k|
(a > 0)
高斯函数
e−x²/2
√(2π) e−k²/2
x 的导数
f′(x)
ikF(k)
k 的导数
xf(x)
iF ′(k)
x 的积分
∫_{-∞}^{x} f(x′)dx′
F(k)/(ik)
x 方向的平移
f(x − a)
e^{-iak}F(k)
k 方向的平移
e^{iax}f(x)
F(k − a)
x 方向的伸缩
f(ax)
F(k/a)/a
卷积
f(x)*g(x)
F(k)G(k)
通常这些公式需要组合使用。通常需要一些预备步骤（就像使用积分表一样）来得到恰好是这些形式之一。这里有一些例子。
例 1. f′′(x) 的变换是（使用导数表公式）
$$(f′′(x))^{\wedge}= ik (f′(x))^{\wedge}= (ik)^{2} \hat{f}(k) = −k^{2} \hat{f}(k)。$$
注意这对微分方程意味着什么：微分算子可以转化为“乘法”算子。
例 2. 高斯函数 exp(−Ax²) 的变换，同时使用伸缩和高斯公式，
$$
\begin{aligned}
(\exp(-Ax^{2}))^{\wedge} &= (\exp(-[\sqrt{2A}x]^{2}/2))^{\wedge} \\
&= \frac{1}{\sqrt{2A}} (\exp(-x^{2}/2))^{\wedge}(k/\sqrt{2A}) \\
&= \sqrt{\frac{\pi}{A}} \exp(-[k/\sqrt{2A}]^{2}/2) = \sqrt{\frac{\pi}{A}} \exp(-k^{2}/(4A))。
\end{aligned}
$$
例 3. e^{2ik}/(k^{2}+1) 的逆变换，使用 x 方向的平移性质，然后是指数公式，
$$
\left(\frac{e^{2ik}}{k^{2}+1}\right)^{\vee} = \left(\frac{1}{k^{2}+1}\right)^{\vee} (x+2) = \frac{1}{2}e^{-|x+2|}。
$$
例 4. ke^{-k^{2}/2} 的逆变换使用高斯公式和 x 方向的导数公式：
$$
\begin{aligned}
(ke^{-k^{2}/2})^{\vee} &= -i (ik e^{-k^{2}/2})^{\vee} = -i \frac{d}{dx} (e^{-k^{2}/2})^{\vee} \\
&= -i \sqrt{2\pi} \frac{d}{dx} (\sqrt{2\pi} e^{-k^{2}/2})^{\vee} = -i \sqrt{2\pi} \frac{d}{dx} (e^{-x^{2}/2}) \\
&= \frac{ix}{\sqrt{2\pi}} e^{-x^{2}/2}。
\end{aligned}
$$

### 1.2 卷积

不幸的是，函数乘积的逆变换并不是逆变换的乘积。相反，它是一种称为卷积的二元运算，定义为

$$(f * g)(x) = \int_{-\infty}^{\infty} f(x-y)g(y)dy。$$ (4)

===== 第 3 页 =====

使用定义，其傅里叶变换为

$$(f*g)^{\wedge}=\int_{-\infty}^{\infty}\int_{-\infty}^{\infty}f(x-y)g(y)e^{-ikx}dy \,dx。$$

使用变量替换 $z=x-y$，这变为

$$\int_{-\infty}^{\infty}\int_{-\infty}^{\infty}f(z)g(y)e^{-ik(y+z)}dydz=\left(\int _{-\infty}^{\infty}f(z)e^{-ikz}dz\right)\left(\int_{-\infty}^{\infty}g(y)e^{- iky}dy\right)=\hat{f}(k)\hat{g}(k)，$$

这正是表中的最后一个公式。

### 作为广义函数的发散傅里叶积分

公式 (3) 和 (2) 假设 $f(x)$ 和 $F(k)$ 在无穷远处衰减以保证积分收敛。如果情况不是这样，那么积分必须在广义意义下解释。此外，表中的一些公式必须进行调整以考虑这一点。

注意 $\delta(x)$ 的变换等于 $\hat{f}(k)\equiv 1$，所以至少在形式上，$\hat{f}(k)$ 的逆变换应该是一个 delta 函数：

$$\delta(x)=\frac{1}{2\pi}\int_{-\infty}^{\infty}e^{ikx}dk。$$ (5)

这非常棘手：积分甚至不收敛，那么这样的陈述可能意味着什么？

当然，问题在于该积分表示的是一个广义函数，而不是一个常规函数。我们可以更一般地将 $F(k)$ 的逆变换定义为一个广义函数，它是以下常规函数的极限

$$f_{L}(x)=\frac{1}{2\pi}\int_{-L}^{L}\exp(ikx)F(k)dk$$

当 $L\to\infty$ 时（回想广义函数总是可以用常规函数逼近的事实）。这意味着逆变换 $f(x)$ 是一个广义函数，它作用于光滑函数的方式如下：

$$f[\phi]=\lim_{L\to\infty}\int_{-\infty}^{\infty}f_{L}(x)\phi(x)dx。$$ (6)

让我们看看 (5) 中的积分，看它代表了什么广义函数。对于这种情况，

$$f_{L}(x)=\frac{1}{2\pi}\int_{-L}^{L}\exp(ikx)dk=\frac{1}{\pi x}\sin(Lx)。$$

那么，如果问 $f_{L}$ 的极限如何作为一个广义函数作用，可以计算

$$f[\phi]=\lim_{L\to\infty}\frac{1}{\pi}\int_{-\infty}^{\infty}\frac{\sin(Lx)}{x }\phi(x)dx=\lim_{L\to\infty}\frac{1}{\pi}\int_{-\infty}^{\infty}\frac{\sin(y)} {y}\phi(y/L)dy。$$

极限 $L\to\infty$ 可以移到积分内部（这可以通过一些努力证明是合理的），结果为

$$f[\phi]=\frac{\phi(0)}{\pi}\int_{-\infty}^{\infty}\frac{\sin(y)}{y}dy=\phi(0)。$$

所以逆变换确实是 delta 函数！

===== 第 4 页 =====

## 2 使用变换求解微分方程

傅里叶变换的导数性质尤其吸引人，因为它将微分算子转化为乘法算子。在许多情况下，这允许我们消除其中一个自变量的导数。得到的问题通常更容易求解。当然，为了恢复原始变量中的解，需要进行逆变换。这通常是计算量最大的步骤。

### 实轴上的常微分方程

这里我们给出几个初步的例子，说明傅里叶变换在仅涉及一个变量函数的微分方程中的应用。

**例 1.** 让我们求解

$$-u^{\prime\prime}+u=f(x),\quad\lim_{|x|\to\infty}u(x)=0。$$ (7)

(7) 式两边的变换可以利用导数法则完成，得到

$$k^{2}\hat{u}(k)+\hat{u}(k)=\hat{f}(k)。$$ (8)

这只是一个代数方程，其解为

$$\hat{u}(k)=\frac{\hat{f}(k)}{1+k^{2}}。$$ (9)

我们可以通过逆变换恢复 $u(x)$。表达式 (9) 是 $\hat{f}(k)$ 和 $1/(1+k^{2})$ 的乘积，因此我们必须使用卷积公式：

$$u(x)=f(x)*\left(\frac{1}{1+k^{2}}\right)^{\vee}=\frac{1}{2}\int_{-\infty}^{\infty }e^{-|x-y|}f(y)dy。$$

这正是我们从格林函数表示中得到的结果，其中 $G(x,y)=e^{-|x-y|}/2$。还有一个谜团：(7) 中的远场条件似乎在任何地方都没有被使用。事实上，条件 (7) 已经内置在傅里叶变换中；如果被变换的函数在无穷远处不衰减，傅里叶积分将只能像 (6) 中那样作为广义函数定义。

**例 2.** _Airy_ 方程是

$$u^{\prime\prime}-xu=0，$$

它将受到与 (7) 相同的远场条件限制。变换使用了关于 $x$ 和 $k$ 的导数公式，给出

$$-k^{2}\hat{u}(k)-i\hat{u}^{\prime}(k)=0。$$

这仍然是一个关于变量 $k$ 的微分方程，但我们可以用分离变量法（即 ODE 版本）求解它。这导致 $d\hat{u}/\hat{u}=ik^{2}dk$，积分后得到

$$\hat{u}(k)=Ce^{ik^{3}/3}，$$

其中 $C$ 是任意积分常数。逆变换为

$$u(x)=\frac{C}{2\pi}\int_{-\infty}^{\infty}\exp(i[kx+k^{3}/3])dk。$$ (10)

这个积分无法进一步化简。当选择 $C=1$ 时，结果就是所谓的 _Airy 函数_，记为 Ai$(x)$。

===== 第 5 页 =====

### 偏微分方程的求解

现在我们考虑存在多个自变量的情况。在这种情况下，变换将只应用于一个变量。这将减少具有导数的变量数量，并常常使得使用 ODE 技术求解成为可能。

**例 1.** 考虑上半平面上的拉普拉斯方程

$$u_{xx}+u_{yy}=0,\quad-\infty<x<\infty,\quad y>0,\quad u(x,0)=g(x),\quad\lim_{y \to\infty}u(x,y)=0。$$ (11)

只对变量 $x$ 进行变换是有意义的，我们将其记为

$$U(k,y)=\int_{-\infty}^{\infty}e^{-ikx}u(x,y)dx。$$ (12)

我们注意到关于 $y$ 的导数与关于 $x$ 的傅里叶积分可交换，所以 $u_{yy}$ 的变换就是简单的 $U_{yy}$。那么 (11) 中的方程和边界条件变为

$$-k^{2}U+U_{yy}=0,\quad U(k,0)=\hat{g}(k),\quad\lim_{y\to\infty}U(k,y)=0。$$

这是一组常微分方程，每个 $k$ 值对应一个。通解为 $U=c_{1}e^{+|k|y}+c_{2}e^{-|k|y}$，其中 $c_{1,2}$ 可以依赖于 $k$。为了使 $U$ 在无穷远处为零，第一项必须为零。利用 $U(k,0)=\hat{g}(k)$，可得

$$U(k,y)=\hat{g}(k)e^{-|k|y}。$$

逆变换涉及卷积以及表中的 $k$ 方向指数公式。结果为

$$u(x,y)= g(x)*\left(e^{-|k|y}\right)^{\vee}=g(x)*\left(\frac{y}{\pi(x^{2}+y^ {2})}\right)$$ $$= \frac{1}{\pi}\int_{-\infty}^{\infty}\frac{yg(x_{0})}{(x-x_{0})^{2 }+y^{2}}dx_{0}。$$

这正是用格林函数方法得到的相同公式。

**例 2.** 现在让我们用类似的过程求解输运方程

$$u_{t}+cu_{x}=0,\quad-\infty<x<\infty,\quad t>0,\qquad u(x,0)=f(x)。$$

令 $U(k,t)$ 为仅关于变量 $x$ 的 $u$ 的变换，如 (12)。由于关于 $t$ 的导数与关于 $x$ 的积分可交换，问题转化为

$$U_{t}+ikcU=0,\quad U(k,0)=\hat{f}(k)。$$

这是一个简单的一阶微分方程，其解为

$$U(k,t)=e^{-ickt}\hat{f}(k)。$$

现在我们使用表中 $a=ct$ 的平移公式，这意味着逆变换是

$$u(x,t)=f(x-ct)。$$

这是一个 _行波解_，描述了形状为 $f(x)$ 的脉冲以速度 $c$ 匀速运动。

===== 第 6 页 =====

**例 3.** 考虑实轴上的波动方程

$$u_{tt}=u_{xx},\quad-\infty<x<\infty,\quad t>0,\quad u(x,0)=f(x),\quad u_{t}(x,0 )=g(x)。$$

令 $U(k,t)$ 为关于 $x$ 变量的变换，则问题变为

$$U_{tt}+k^{2}U=0,\quad U(k,0)=\hat{f}(k),\quad U_{t}(k,0)=\hat{g}(k)。$$

这正是一个谐振子的初值问题。其解为

$$U(k,t)=\hat{f}(k)\cos(kt)+\frac{\hat{g}(k)}{k}\sin(kt)。$$ (13)

注意正弦和余弦可以用复指数表示，所以

$$U(k,t)=\frac{1}{2}\hat{f}(k)(e^{ikt}+e^{-ikt})+\frac{1}{2ik}\hat{g}(k)(e^{ikt}-e^ {-ikt})。$$ (14)

现在逆变换很直接，利用指数和积分公式，

$$u(x,t)=\frac{1}{2}[f(x-t)+f(x+t)]+\frac{1}{2}\int_{-\infty}^{x}g(x^{\prime}+t)-g( x^{\prime}-t)dx^{\prime}。$$

该积分可以通过对第一项使用变量替换 $\xi=x^{\prime}+t$ 和对第二项使用 $\xi=x^{\prime}-t$ 来简化，

$$\int_{-\infty}^{x}g(x^{\prime}+t)-g(x^{\prime}-t)dx^{\prime}=\int_{-\infty}^{x +t}g(\xi)d\xi-\int_{-\infty}^{x-t}g(\xi)d\xi=\int_{x-t}^{x+t}g(\xi)d\xi。$$

最后，将所有这些放在一起，得到波动方程的 _d'Alembert_ 公式

$$u(x,t)=\frac{1}{2}[f(x-t)+f(x+t)]+\frac{1}{2}\int_{x-t}^{x+t}g(\xi)d\xi。$$ (15)

## 3 含时方程的基本解

涉及时间的偏微分方程也有格林函数，尽管它们通常被称为 _基本解_ 或 _源函数_。假设 $u(\mathbf{x},t):D\times\mathbb{R}\rightarrow\mathbb{R}$，其中 $D\subset\mathbb{R}^{n}$ 是某个空间区域，它求解

$$u_{t}(\mathbf{x},t)=\mathcal{L}u(\mathbf{x},t),\quad u(\mathbf{x},0)=f(\mathbf{ x}),$$ (16)

其中 $\mathcal{L}$ 是某个不依赖于 $t$ 的微分算子。该方程还补充了在 $\mathbf{x}\in\partial D$ 上的齐次边界条件（Dirichlet、Neumann 以及其他可能条件）。

我们将 (16) 的基本解定义为问题

$$S_{t}=\mathcal{L}_{x}S,\quad S(\mathbf{x},\mathbf{x}_{0},0)=\delta(\mathbf{x}-\mathbf{x}_{0}),$$

的解 $S(\mathbf{x},\mathbf{x}_{0},t)$，其边界条件与 $u$ 相同。

这与我们之前对格林函数的定义有一点不同：$\delta$ 函数是作为初始条件出现的，而不是方程中的非齐次项。当然，

===== 第 7 页 =====

$S$ 的初始条件仅在广义函数的意义上有意义，也就是说，当 $t\to 0$ 时，$S$ 趋近于一个 $\delta$-函数：

$$\lim_{t\to 0}\int_{D}S(\mathbf{x},\mathbf{x}_{0},t)\phi(\mathbf{x})dx=\int_{D} \delta(\mathbf{x}-\mathbf{x}_{0})\phi(\mathbf{x})dx=\phi(\mathbf{x}_{0}),$$ (17)

对于所有连续函数 $\phi:D\rightarrow\mathbb{R}$ 成立。

我们现在断言，初值问题 (16) 由以下公式求解

$$u(x,t)=\int_{-\infty}^{\infty}S(\mathbf{x},\mathbf{x}_{0},t)f(\mathbf{x}_{0})dx_ {0},$$ (18)

只要 $f$ 是连续的。其直观意义很清楚：该积分正是对初始条件 $f(\mathbf{x})$ 中包含的所有点源影响求和。让我们检查一下它是否有效。对于初始条件，我们在 (18) 中取 $t\to 0$ 并利用 (17)，

$$u(x,0)=\lim_{t\to 0}\int_{D}S(\mathbf{x},\mathbf{x}_{0},t)f(\mathbf{x}_{0})dx_ {0}=\int_{D}\delta(\mathbf{x}-\mathbf{x}_{0})f(x_{0})dx_{0}=f(\mathbf{x})。$$

将 $u$ 代入 (16) 中的方程，我们可以将时间导数移到积分内部：

$$u_{t}=\int_{D}S_{t}(\mathbf{x},\mathbf{x}_{0},t)f(\mathbf{x}_{0})dx_{0}=\int_{D }\mathcal{L}_{x}S(\mathbf{x},\mathbf{x}_{0},t)f(\mathbf{x}_{0})dx_{0}。$$

我们现在假设（作用于 $\mathbf{x}$ 变量的）算子可以移到关于 $\mathbf{x}_{0}$ 的积分之外（在大多数情况下可以证明这是合理的），得到

$$u_{t}=\mathcal{L}_{x}\int_{D}S(\mathbf{x},\mathbf{x}_{0},t)f(\mathbf{x}_{0})dx _{0}=\mathcal{L}_{x}u,$$

这意味着方程被满足。

### 使用傅里叶变换寻找基本解

当空间区域为 $D=\mathbb{R}$ 时，傅里叶变换通常可以用来寻找基本解。

**例 1.** 对于实轴上的扩散方程

$$u_{t}=Du_{xx},\quad-\infty<x<\infty,\quad u(x,0)=f(x),\lim_{|x|\rightarrow\infty }u(x,t)=0。$$

其基本解满足

$$S_{t}=DS_{xx},\quad-\infty<x<\infty,\quad S(x,x_{0},0)=\delta(x-x_{0}),\lim_{|x |\rightarrow\infty}S(x,x_{0},t)=0。$$

通过对 $x$ 进行傅里叶变换，令

$$\hat{S}(k,x_{0},t)=\int_{-\infty}^{\infty}S(x,x_{0},t)e^{-ikx}dx,$$

我们发现 $\hat{S}$ 满足一个简单的一阶 ODE，$\hat{S}_{t}=-Dk^{2}\hat{S}$。这个 ODE 的初始条件由 $\delta(x-x_{0})$ 的变换给出，根据平移性质，它是 $e^{-ix_{0}k}$ 乘以

===== 第 8 页 =====

$\delta(x)$ 的变换（等于 1）。由此可得 $\hat{S}=e^{-ix_{0}k-Dk^{2}t}$。逆变换使用平移和伸缩性质以及高斯函数的变换，给出

$$S(x,x_{0},t)=\frac{1}{\sqrt{4\pi Dt}}e^{-(x-x_{0})^{2}/(4Dt)}。$$ (19)

如果我们希望求解实轴上满足初始条件 $u(x,0)=f(x)$ 的扩散方程 $u_{t}=Du_{xx}$，我们可以使用模板 (18)，给出

$$u(x,t)=\int_{-\infty}^{\infty}\frac{f(x_{0})}{\sqrt{4\pi Dt}}e^{-(x-x_{0})^{2}/(4 Dt)}dx_{0}。$$ (20)

注意这与 (20) 相同。

**例 2.** 著名的 Korteweg - de Vries (KdV) 方程可以用线性初值问题来近似

$$u_{t}=-u_{xxx},\quad u(x,0)=f(x),\quad\lim_{|x|\to\infty}u(x,t)=0。$$ (21)

对应的基本解满足

$$S_{t}=-S_{xxx},\quad-\infty<x<\infty,\quad S(x,x_{0},0)=\delta(x-x_{0}),\lim_{|x |\to\infty}S(x,x_{0},t)=0。$$

像上一个例子那样进行变换，我们得到初值问题

$$\hat{S}_{t}=ik^{3}\hat{S},\quad\hat{S}(k,0)=e^{-ix_{0}k}，$$

其解为 $\hat{S}(k,t)=e^{-ix_{0}k}e^{ik^{3}t}$。回想 $e^{ik^{3}}$ 的逆变换是 Airy 函数 (10)，因此有

$$S(x,x_{0},t)=\left[e^{-ix_{0}k}e^{ik^{3}t}\right]^{\vee}=\left[\exp(i(k/a)^{3})\right]^{\vee}(x-x_{0})=a\text{Ai}\Big{(}a(x-x_{0})\Big{)},\quad a\equiv(3t)^{-1/3}。$$

因此，(21) 的解可以写成

$$u(x,t)=\frac{1}{(3t)^{1/3}}\int_{-\infty}^{\infty}\text{Ai}\left(\frac{x-y}{(3t)^ {1/3}}\right)f(y)dy。$$

### 基本解的镜像法

根据我们之前关于格林函数的讨论，我们知道在存在边界的情况下可以利用对称性。对于在满足边界条件 $u(0,t)=0$ 或 $u_{x}(0,t)$ 的半直线 $x>0$ 上的问题，全直线基本解的奇（或偶）对称反射将满足正确的边界条件。

例如，取扩散方程

$$u_{t}=Du_{xx},\quad u(x,0)=f(x),\,u(0,t)=0,\,\lim_{x\to\infty}u(x,t)=0。$$ (22)

我们显然不能使用傅里叶变换，因为 $x$ 的定义域不是整个实轴，而且基本解 (19) 不具有正确的边界条件。另一方面，奇反射 (19)

===== 第 9 页 =====

确实能得到正确的边界条件。此外，通过叠加原理 $S_{t}=S_{xx}$ 且 $S(x,x_{0},0)=\delta(x-x_{0})-\delta(x+x_{0})$。像在镜像法中通常一样，不在定义域内的 delta 函数 $\delta(x+x_{0})$ 可以被忽略。因此，(22) 的解就是

$$u(x,t)=\int_{0}^{\infty}\frac{f(x_{0})}{\sqrt{4\pi Dt}}\left[e^{-(x-x_{0})^{2}/( 4Dt)}-e^{-(x+x_{0})^{2}/(4Dt)}\right]dx_{0}。$$ (23)

[文件内容结束]