#时间管理 #时间管理 #时间管理 #任务管理 #任务管理 #任务管理
你是一个极其理性、硬核且深谙心理学的高阶时间管理教练与学术导师。你的核心任务是接管我的乱序输入，帮我建立清晰的执行边界，对抗拖延症，并屏蔽一切低级多巴胺的干扰（尤其是新闻和无意义的网络刺激）。你需要引导我把核心精力聚焦于数学复习、学术精进以及平稳的生活节奏上。

**提示, 你需要优先阅读**[[任务管理readme]]
%%AI可能面临的提问是: 完成任务管理, 完成时间管理, 完成规划%%


---

[[13.]]
# 1. 道路连通性、可缩空间与环面去点的同调群

> [!Note] 1
> 如果 $X$ 是道路连通的，则 $H_{0}(X) \cong \mathbb{Z}$。

$S_{0}(X)=Z_{0}(X)$ , 只需要注意$\forall x_{0},y_{0}\in X$, 存在$\alpha(0)=x_{0},\alpha(1)=y_{0}$​	的道路, 它的边缘$\partial(\alpha)=x_{0}-y_{0}$, 所以$[x_{0}]=[y_{0}]$ , 因此
$$
H_{0}(X)=S_{0}(X) / \sim =\mathbb{Z}
$$

> [!Note] 2
> 如果 $X$ 是可缩的，也就是 $X \simeq \{*\}$，则
>  $$
>  H_{q}(X)=
>  \begin{cases}
>  \mathbb{Z} & q=0 \\
>  0 & q>0
>  \end{cases}
>  $$

可缩空间是同伦的$\implies$ $H_{0}(X)=\mathbb{Z}$
根据同调群是同伦不变量, 我们只需要证明$\{*\}$的正数维同调群平凡. 
设$\sigma:\Delta^{q}\to \{*\}$, 则$\sigma$是常值映射, 定义
$$
\tau:\Delta^{q+1}\to \{*\},\: \tau(x)=*
$$
- 如果$q$是偶数
$\partial(\sigma)=\sum_{k=0}^{q}(-1)^{k}\sigma {\circ}F^{k}=\sigma {\circ}F^{0}:\Delta^{q-1}\to \{*\}$常值
因此$\sigma \not\in ker\partial^{q}$, 所以$ker\partial^{q}=0$ , 给出了$H_{q}(X)=0$
- 如果$q$是奇数
$\partial(\tau)=\sum_{k=0}^{q+1}(-1)^{k}\tau {\circ}F^{k}=\sigma$ 所以$\sigma\in \mathrm{Im}\partial^{q+1}$ 
所以$H_{q}(X)=0$ 

> [!Note] 3
> 证明 $H_{q}(T-\{x\}) \cong H_{q}(S^{1} \vee S^{1})$；$H_{q}(T-\{x,y\}) \cong H_{q}(S^{1} \vee S^{1} \vee S^{1})$。

![[Pasted image 20260607160846.png|400]]
$T\cong (S^{1}\vee S^{1})\cup_{f}D^{2}$ , 粘合前后圆盘内部是同胚的, $T-\{x\}\cong(S^{1}\vee S^{1})\cup_{f}(D^{2}-\{x_{0}\})\simeq(S^{1}\vee S^{1})\cup_{f}(S^{1}\times I)\simeq S^{1}\vee S^{1}$
从而$H_{q}(T-\{x\})\simeq H_{q}(S^{1}\vee S^{1})$

- $H_{q}(T-\{x,y\}) \cong H_{q}(S^{1} \vee S^{1} \vee S^{1})$
![[Pasted image 20260607163626.png]]
$$
D^{2}-D_{2}^{2} / \sim' \cong (S^{1}\vee S^{1}\vee S^{1})\cup_{f}(D^{2}-D_{2}^{2})\simeq \vee_{i=1}^{3}S^{1}
$$

# 2. 分裂引理、边界同态正合性与长正合序列的自然性

> [!Note] Lemma 4.4.1
> 如果 $0 \to A \overset{f}{\to} G \overset{g}{\to} B \to 0$ 是分裂的，那么 $G \cong A \oplus B$。



> [!Note] 证明 $\delta_{q}$ 是群同态
> $\delta_{q}$ 的定义不依赖于 $\widetilde{z}$ 的选择，证明 $\delta_{q}$ 是群同态。

> [!Note] 定理 4.4.2
> 长正合序列是正合的（即每个映射的像等于下一个映射的核），并且是自然的：对于任意连续映射对 $f: (X,A) \to (Y,B)$，诱导出长正合序列之间的同态，使得所有相关图表交换（即 $f^{*}$ 与序列中的映射可交换）。
> > ![[Pasted image 20260605133030.png|500]]

# 3. 短正合列 $0 \to \mathbb{Z}/4 \to G \to \mathbb{Z}/2 \to 0$ 的分类

> [!Note] 1
> 如果 $G$ 是交换群，确定 $G$。

> [!Note] 2
> 如果 $G$ 不是交换群，确定 $G$。

# 4. 短正合列 $0 \to \mathbb{Z}/2 \to G \to \mathbb{Z}/3 \to 0$ 及其对称情况

> [!Note] 1
> 设 $0 \to \mathbb{Z}/2 \to G \to \mathbb{Z}/3 \to 0$ 是一个短正合列，证明 $G$ 是交换群，而且 $G \cong \mathbb{Z}/6$。

> [!Note] 2
> 对于 $0 \to \mathbb{Z}/3 \to G \to \mathbb{Z}/2 \to 0$ 怎么样呢？

# 5. 自由交换群与短正合列的分裂性

> [!Note] 1
> 证明 $B$ 是自由群、(或)交换群，那么短正合列 $0 \to A \to G \to B \to 0$ 是分裂的。

# 6. 短正合列态射的图追踪同构

> [!Note] 1
> 假设有一个短正合列的态射
> ![[Pasted image 20260605114939.png|400]]
> 如果 $\varphi_{1}, \varphi_{2}, \varphi_{3}, \varphi_{4}$ 是同构，证明 $\varphi_{0}$ 是一个同构（提示：diagram chasing）。

# 7. 底空间同调群与约化同调群

> [!Note] 1
> 设 $(X, x_{0})$ 是一个底空间，证明
>  $$
>  H_{q}(X) \cong
>  \begin{cases}
>  H_{q}(X, x_{0}) & q>0 \\
>  H_{0}(X, x_{0}) \oplus \mathbb{Z} & q=0
>  \end{cases}
> $$
> 因此，$H_{*}(X, x_{0}) \cong \widetilde{H}(X)$ 是约化同调群。



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

0.证明满足平均值原理的连续函数是光滑的（只需要证明C2就可以得到调和，并得出解析，但也可以直接利用平均值公式证明是光滑的）
1.叙述并证明热方程的平均值原理
2.p106 3，5，6，9
3.p113 2，5（公式（1.8）处叙述了外问题，可尝试用极值原理，请在证明之前先陈述稳定性，6，7，8

---
[[分析/实分析/14.]]
习题 14．1．设 $\mathbb{R}^n \backslash\{0\}$ 被表示成 $\mathbb{R}_{+} \times \mathbb{S}^{n-1}$ ，其中 $\mathbb{R}_{+}=\{0<r<\infty\}$ ．证明： $\mathbb{R}^n \backslash\{0\}$ 中的每个开集能被写作这个乘积中开长方体的可列并。
提示 考察如下形式长方体的可列族

$$
\left\{r_j<r<r_k^{\prime}\right\} \times\left\{\gamma \in \mathbb{S}^{n-1}:\left|\gamma-\gamma_{\ell}\right|<1 / m\right\} .
$$


这里 $r_j$ 和 $r_k^{\prime}$ 取遍所有的正有理数，$\left\{\gamma_{\ell}\right\}$ 是 $\mathbb{S}^{n-1}$ 的一个可列稠密集．
习题 14．2．设 $\left(X_j, \mathcal{M}_j, \mu_j\right), 1 \leqslant j \leqslant k$ ，是有限个测度空间．证明：能够在 $X=X_1 \times X_2 \times \cdots \times X_k$ 上构造一个乘积测度 $\mu_1 \times \mu_2 \times \cdots \times \mu_k$ ．
提示 对任何 $E \subset X$ 具有形式 $E=E_1 \times E_2 \times \cdots \times E_k$ ，其中对所有 $j$ 有 $E_j \in \mathcal{M}_j$ ，定义 $\mu_0(E)=\prod_{j=1}^k \mu_j\left(E_j\right)$ 。验证 $\mu_0$ 可延拓成这类集合的有限互不相交并所构成的代数 $\mathcal{A}$ 上的一个准测度，然后应用 Carathéodory－Hahn 延拓定理．

习题 14．3．令 $X=Y=[0,1], \mathcal{M}=\mathcal{N}=\mathcal{B}_{[0,1]}, \mu=$ Lebesgue 测度，$\nu=$ 记数测度．证明：若 $D=\{(x, x): x \in[0,1]\}$ 是 $X \times Y$ 中的对角集，则 $\iint \chi_D d \mu d \nu$ ， $\iint \chi_D d \nu d \mu$ 和 $\int \chi_D d(\mu \times \nu)$ 均不相等。

习题 14．4．令 $X=Y=\mathbb{N}, \mathcal{M}=\mathcal{N}=\mathcal{P}(\mathbb{N}), \mu=\nu=$ 记数测度。定义

$$
f(m, n)= \begin{cases}1, & \text { 若 } m=n, \\ -1, & \text { 若 } m=n+1, \\ 0, & \text { 其它情形. }\end{cases}
$$


证明： $\int|f| d(\mu \times \nu)=\infty$ ，且 $\iint f d \mu d \nu$ 和 $\iint f d \nu d \mu$ 存在但不相等．
习题 14．5．对哪些 $a, b \in \mathbb{R},|x|^a|\ln | x| |^b$ 在 $\left\{x \in \mathbb{R}^n:|x|<1 / 2\right\}$ 上 Lebesgue 可积？在 $\left\{x \in \mathbb{R}^n:|x|>2\right\}$ 上呢？