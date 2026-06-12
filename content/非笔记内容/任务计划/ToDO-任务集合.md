#时间管理 #时间管理 #时间管理 #任务管理 #任务管理 #任务管理

**提示, 你需要优先阅读**[[任务管理readme]]
%%AI可能面临的提问是: 完成任务管理, 完成时间管理, 完成规划%%
[[ToDo-已经规划好的任务]] 

---

实分析[[15.测度性质与分解习题]]
# 1. L-S测度的基本性质

> [!Note] 习题15.1
> 设 $F$ 递增且右连续，$\mu_{F}$ 为相应的测度．证明：$\mu_{F}(\{a\})=F(a)- F\left(a^{-}\right), \mu_{F}([a, b))=F\left(b^{-}\right)-F\left(a^{-}\right), \mu_{F}([a, b])=F(b)-F\left(a^{-}\right)$，和 $\mu_{F}((a, b))= F\left(b^{-}\right)-F(a)$.

# 2. 带号测度的基本性质

> [!Note] 习题15.2
> 设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的带号测度，证明：
> （i）$E \in \mathcal{M}$ 是 $\nu$－零集当且仅当 $|\nu|(E)=0$ ；
> （ii）$\nu \perp \mu$ 当且仅当 $|\nu| \perp \mu$ 当且仅当 $\nu^{+} \perp \mu$ 且 $\nu^{-} \perp \mu$ ．

> [!Note] 习题15.3
> 设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的带号测度，证明：
> （i）$L^{1}(X, \nu)=L^{1}(X,|\nu|)$ ．
> （ii）若 $f \in L^{1}(X, \nu)$ ，则 $\left|\int f d \nu\right| \leqslant \int|f| d|\nu|$ ．
> （iii）若 $E \in \mathcal{M}$ ，则 $|\nu|(E)=\sup \left\{\left|\int_{E} f d \nu\right|:|f| \leqslant 1\right\}$ ．

# 3. 带号测度 $\nu^{+},\nu^{-},|\nu|$ 的表达式

> [!Note] 习题15.4
> 设 $\nu$ 是可测空间 $(X, \mathcal{M})$ 上的带号测度，$E \in \mathcal{M}$ 。证明：
> （i）$\nu^{+}(E)=\sup \{\nu(F): F \in \mathcal{M}, F \subset E\}$ 和 $\nu^{-}(E)=-\inf \{\nu(F): F \in \mathcal{M}, F \subset E\}$.
> （ii）$|\nu|(E)=\sup \left\{\sum_{j=1}^{n}\left|\nu\left(E_{j}\right)\right|: n \in \mathbb{N}, E_{1}, \cdots, E_{n}\right.$ 互不相交且 $\left.\bigcup_{j=1}^{n} E_{j}=E\right\}$ 。

# 4. Lebesgue分解与Borel测度

> [!Note] 习题15.5
> 设 $F$ 是 $\mathbb{R}$ 上的递增规范化函数，设 $F=F_{A}+F_{C}+F_{J}$ 为 $F$ 的 Lebesgue 分解，其中 $F_{A}$ 绝对连续，$F_{C}$ 连续且 $F_{C}^{\prime}=0$ a．e，$F_{J}$ 为纯跳跃函数。设 $\mu=\mu_{A}+\mu_{C}+\mu_{J}$ ，其中 $\mu, \mu_{A}, \mu_{C}, \mu_{J}$ 分别为相应于 $F, F_{A}, F_{C}, F_{J}$ 的 Borel测度．证明：
> （i）$\mu_{A}$ 关于 Lebesgue 测度绝对连续，且对于每个 Lebesgue 可测集 $E$ 有 $\mu_{A}(E)=\int_{E} F^{\prime}(x) d x$.
> （ii）若 $F$ 绝对连续，则当 $f$ 和 $f F^{\prime}$ 可积时，有
> 
>  $$
>  \int f d \mu=\int f d F=\int f(x) F^{\prime}(x) d x
>  $$
> 
> （iii）$\mu_{C}+\mu_{J}$ 与 Lebesgue 测度是相互奇异的．

# 5. 带号测度关系的若干结论

> [!Note] 习题15.6
> 设 $\nu, \nu_{1}, \nu_{2}$ 是 $(X, \mathcal{M})$ 上的带号测度，$\mu$ 是 $\mathcal{M}$ 上的正测度，证明：
> （i）若 $\nu_{1} \perp \mu$ 且 $\nu_{2} \perp \mu$ ，则 $\nu_{1}+\nu_{2} \perp \mu$ ．
> （ii）若 $\nu_{1} \ll \mu$ 且 $\nu_{2} \ll \mu$ ，则 $\nu_{1}+\nu_{2} \ll \mu$ 。
> （iii）若 $\nu_{1} \perp \nu_{2}$ ，则 $\left|\nu_{1}\right| \perp\left|\nu_{2}\right|$ ．
> （iv）$\nu \ll|\nu|$ ．
> （v）若 $\nu \perp \mu$ 且 $\nu \ll \mu$ ，则 $\nu=0$ ．

# 6. 绝对连续与奇异性的等价刻画

> [!Note] 习题15.7
> 设 $\mu$ 为正测度，$\nu$ 为带号测度。证明：$\nu \ll \mu$ 当且仅当 $|\nu| \ll \mu$ 也当且仅当 $\nu^{+} \ll \mu$ 且 $\nu^{-} \ll \mu$ 。

# 7. 正测度序列的奇异与绝对连续性质

> [!Note] 习题15.8
> 设 $\mu$ 和 $\left\{\nu_{j}\right\}_{j=1}^{\infty}$ 均为正测度．证明：
> （i）若对所有 $j$ 有 $\nu_{j} \perp \mu$ ，则 $\sum_{j=1}^{\infty} \nu_{j} \perp \mu$ ；
> （ii）若对所有 $j$ 有 $\nu_{j} \ll \mu$ ，则 $\sum_{j=1}^{\infty} \nu_{j} \ll \mu$ ．

# 8. 积测度与Radon-Nikodym导数

> [!Note] 习题15.9
> 对 $j=1,2$ ，令 $\mu_{j}, \nu_{j}$ 是 $\left(X_{j}, \mathcal{M}_{j}\right)$ 上的 $\sigma$－有限测度且 $\nu_{j} \ll \mu_{j}$ 。证明：$\nu_{1} \times \nu_{2} \ll \mu_{1} \times \mu_{2}$ 且
> >
> > $$
> > \frac{d\left(\nu_{1} \times \nu_{2}\right)}{d\left(\mu_{1} \times \mu_{2}\right)}\left(x_{1}, x_{2}\right)=\frac{d \nu_{1}}{d \mu_{1}}\left(x_{1}\right) \frac{d \nu_{2}}{d \mu_{2}}\left(x_{2}\right), \quad\left(\mu_{1} \times \mu_{2}\right) \text {-a.e. }
> > $$

# 9. Lebesgue分解的反例

> [!Note] 习题15.10
> 令 $X=[0,1], \mathcal{M}=\mathcal{B}_{[0,1]}, m=$ Lebesgue 测度，$\mu=\mathcal{M}$ 上的计数测度．证明：
> （i）$m \ll \mu$ ，但对任何 $f$ 有 $d m \neq f d \mu$ 。
> （ii）$\mu$ 关于 $m$ 不存在 Lebesgue 分解．

# 10. 测度绝对连续的表示

> [!Note] 习题15.11
> 设 $\mu, \nu$ 是 $(X, \mathcal{M})$ 上的 $\sigma$－有限测度且 $\nu \ll \mu$ ，令 $\lambda=\mu+\nu$ 。证明：若 $f=d \nu / d \lambda$ ，则 $0 \leqslant f<1 \mu$－a．e．且 $d \nu / d \mu=f /(1-f)$ ．



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
[[14. ]]

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

