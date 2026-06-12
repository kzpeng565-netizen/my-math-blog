#时间管理 #时间管理 #时间管理 #任务管理 #任务管理 #任务管理

**提示, 你需要优先阅读**[[任务管理readme]]
%%AI可能面临的提问是: 完成任务管理, 完成时间管理, 完成规划%%

---
群公告
第五章作业：6，8，15，16，贾老师第五章PPT最后一页3道题，共7题。

问题 1：观察实验中的 N₂ 光谱，为什么它是一组组“带”，而 Na 是两条“线”？
• 问题 2：为什么 CO₂ （线性三原子分子）有红外吸收，而 O₂ 没有？
• 问题 3：如果你是一位天体物理学家，发现一颗系外行星的大气光谱中发现水蒸气、二氧化碳、甲烷等分子的吸收谱线，你能推断出什么？
截止时间：6月7日晚23：00

第七八章作业：共7题，见word文档。
贾老师第七章PPT第89页和最后一页
贾老师第八章PPT第113页
截止时间：6月14日无23:00

---
[[分析/实分析/14.]]

习题 14．3．令 $X=Y=[0,1], \mathcal{M}=\mathcal{N}=\mathcal{B}_{[0,1]}, \mu=$ Lebesgue 测度，$\nu=$ 记数测度．证明：若 $D=\{(x, x): x \in[0,1]\}$ 是 $X \times Y$ 中的对角集，则 $\iint \chi_D d \mu d \nu$ ， $\iint \chi_D d \nu d \mu$ 和 $\int \chi_D d(\mu \times \nu)$ 均不相等。

习题 14．4．令 $X=Y=\mathbb{N}, \mathcal{M}=\mathcal{N}=\mathcal{P}(\mathbb{N}), \mu=\nu=$ 记数测度。定义

$$
f(m, n)= \begin{cases}1, & \text { 若 } m=n, \\ -1, & \text { 若 } m=n+1, \\ 0, & \text { 其它情形. }\end{cases}
$$


证明： $\int|f| d(\mu \times \nu)=\infty$ ，且 $\iint f d \mu d \nu$ 和 $\iint f d \nu d \mu$ 存在但不相等．
习题 14．5．对哪些 $a, b \in \mathbb{R},|x|^a|\ln | x| |^b$ 在 $\left\{x \in \mathbb{R}^n:|x|<1 / 2\right\}$ 上 Lebesgue 可积？在 $\left\{x \in \mathbb{R}^n:|x|>2\right\}$ 上呢？

---
微分方程[[13. 格林函数]]

# 1. 格林函数的对称性

> [!Note] 题目1
> 证明 $G(x,y)=G(y,x)$ （这里我们追求严格的数学证明，因此我们用 $G(x,y)=\Phi(x-y)=\phi^{x}(y)$ 这个定义作为出发点）

# 2. 上半平面的 Poisson 公式与傅立叶变换

> [!Note] 题目2
> 利用傅立叶方法推导上半平面的 Poisson 公式（特别的，计算 $\frac{1}{1+x^{2}}$ 的傅立叶变换）

# 3. 上半平面 Dirichlet 问题的边界连续性

> [!Note] 题目3
> 考虑上半平面的边值问题（假设边界值 $g$ 连续，假设 $u$ 在上半片面内部调和），证明（格林公式）给出的 $u$ 在边界连续，（即 $x$ 趋于边界上 $x^{*}$， 有 $u(x)$ 趋于 $g(x^{*})$）

# 4. 圆盘上的 Poisson 公式与边界连续性

> [!Note] 题目4
> 对圆盘平行的完成问题2，3

# 5. 格林函数的性质与半圆区域格林函数

> [!Note] 题目5-1
> 证明格林函数的性质 3 及性质 5 ．
> 性质 3 在区域 $\Omega$ 中成立着不等式：
> $$
> 0<G\left(M, M_0\right)<\frac{1}{4 \pi r_{M_0 M}}
> $$
> 性质 $5$ $\displaystyle\iint_{\Gamma} \frac{\partial G\left(M, M_0\right)}{\partial \boldsymbol{n}} \mathrm{d} S_M=-1$ ．

> [!Note] 题目5-2
> 求半圆区域上狄利克雷问题的格林函数．

# 6. 球内 Dirichlet 问题的 Poisson 公式应用

> [!Note] 题目6
> 利用泊松公式求边值问题
> $$
> \left\{\begin{array}{l}
> u_{x x}+u_{y y}+u_{z z}=0, \quad x^2+y^2+z^2<1, \\
> \left.u(r, \theta, \varphi)\right|_{r=1}=3 \cos 2 \theta+1 \quad(r, \theta, \varphi \text { 表示球面坐标 })
> \end{array}\right.
> $$

# 7. 圆盘上泊松方程 Dirichlet 问题

> [!Note] 题目7
> 求泊松方程狄利克雷问题
> $$
> \begin{cases}\Delta u=x^2 y, & x^2+y^2<a^2 \\ u=0, & x^2+y^2=a^2\end{cases}
> $$
> 的解．

# 8. 平行线间的格林函数

> [!Note] 题目8
> 求 $\mathbf{R}^2$ 中调和方程在两平行线间的格林函数．


---
拓扑[[14. 正合三元组, 同调与映射度]]
# 1. 正合三元组

> [!Note] 题目14-1
> 1. 证明$(S^{n},D^{n}_{+},D^{n}_{-})$ 是一个正合三元组

# 2. 悬垂同构与楔和的同调

> [!Note] 题目14-2
> 2. 如果$q>1$ $H_{q-1}(X)\cong H_{q}\left( \sum X \right)$
> $$
> \sum X:= \frac{X\times I}{X\times \{0\}\sim(x,0);\:X\times \{1\}\sim (x,1)}
> $$
> 是unreduced suspension of X (未约化双锥)

> [!Note] 题目14-3
> 3. $H_{q}(X\vee Y)\cong H_{q}(X)\oplus H_{q}(Y)$ 如果$q>0$, $X,Y$是胞腔复形

# 3. Barrett-Whitehead 定理

> [!Note] 题目14-4
> 4. The Barrett-Whitehead Theorem
> 给定一个阿贝尔群的交换图
> ![[Pasted image 20260610160108.png]]
> 使得行是正合的, $\gamma_{i}\cong$, 则存在一个正合序列
> $$
> \dots \to A_{i}\overset{(f_{i},\alpha_{i})}{\to}B_{i}\oplus A_{i}'\overset{\beta_{i}-f_{i}'}{\to}B_{i}\overset{h_{i}{\circ}\gamma_{i}^{-1}{\circ}g_{i}'}{\to}A_{i-1}\to\dots
> $$

# 4. 曲面的同调群计算

> [!Note] 题目14-5
> 5. 计算$H_{*}(T^{2})$, $H_{*}(\text{Klein Bottle})$ (你应该需要会计算普遍情形)

# 5. 映射的度

> [!Note] 题目14-6
> 6. 假设$g:S^{n}\to S^{n}$ 没有不动点, 证明$deg(g)=(-1)^{n+1}$

> [!Note] 题目14-7
> 7. 令$A\in O(n+1)$, 也就是正交矩阵. 定义$f_{A}:S^{n}\to S^{n},\:x\to Ax$ 
> ![[Pasted image 20260610165454.png]]
> $deg(f_{A})=?$

