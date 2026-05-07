# 群作用

## 基思·康拉德（Keith Conrad）

## 1. 引言

对称群 $S_{n}$ 根据其定义，表现为对集合 $\{1,2, \ldots, n\}$ 的置换。对于 $n \geq 3$ 的二面体群 $D_{n}$，虽然几何上可以解释为保持正 $n$ 边形不变的某些平面运动，但也可以仅视为对 $n$ 个顶点的置换群；顶点的刚性运动决定了正 $n$ 边形其余部分的位置。如果我们用从 1 到 $n$ 的数字以确定的方式标记这 $n$ 个顶点，那么我们可以将 $D_{n}$ 视为 $S_{n}$ 的一个子群。

例 1.1. 下面对正方形的标记使我们能够将 $D_{4}$ 中 90 度逆时针旋转 $r$ 视为 4-轮换 (1234)，将关于平分正方形的水平线的反射 $s$ 视为对换 (24)。$D_{4}$ 的其余元素，作为顶点的置换，列在正方形下方的表格中。
![](https://cdn.mathpix.com/cropped/0a27da81-90ab-414a-b918-984f98c130c0-01.jpg?height=323&width=317&top_left_y=1263&top_left_x=966)

| 1 | $r$ | $r^{2}$ | $r^{3}$ | $s$ | $r s$ | $r^{2} s$ | $r^{3} s$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $(1)$ | $(1234)$ | $(13)(24)$ | $(1432)$ | $(24)$ | $(12)(34)$ | $(13)$ | $(14)(23)$ |

如果我们以不同的方式标记顶点（例如，交换标签 1 和 2），那么我们将 $D_{4}$ 变成了 $S_{4}$ 的一个不同的子群（例如，交换 1 和 2 会把 $r$ 变成 $(2134)=(1342)$）。

更抽象地说，如果我们给定一个集合 $X$（不一定是正方形的顶点集），那么 $X$ 的所有置换的集合 $\operatorname{Sym}(X)$ 在复合运算下构成一个群，而 $X$ 的偶置换的子群 $\operatorname{Alt}(X)$ 在复合运算下也构成一个群。如果我们以确定的顺序列出 $X$ 的元素，比如 $X=\left\{x_{1}, \ldots, x_{n}\right\}$，那么我们可以将 $\operatorname{Sym}(X)$ 视为 $S_{n}$，将 $\operatorname{Alt}(X)$ 视为 $A_{n}$，但不同的顺序排列会导致 $\operatorname{Sym}(X)$ 与 $S_{n}$ 以及 $\operatorname{Alt}(X)$ 与 $A_{n}$ 有不同的等同方式。$^{1}$

“抽象”的对称群 $\operatorname{Sym}(X)$ 确实自然地出现：
定理 1.2 (凯莱). 每个有限群 $G$ 都可以嵌入到一个对称群中。
证明. 对每个 $g \in G$，定义左乘函数 $\ell_{g}: G \rightarrow G$，其中 $\ell_{g}(x)=g x$，$x \in G$。每个 $\ell_{g}$ 都是 $G$ 作为一个集合的置换，其逆为 $\ell_{g^{-1}}$。所以 $\ell_{g}$ 属于 $\operatorname{Sym}(G)$。由于 $\ell_{g_{1}} \circ \ell_{g_{2}}=\ell_{g_{1} g_{2}}$（即对所有 $x \in G$ 有 $g_{1}\left(g_{2} x\right)=\left(g_{1} g_{2}\right) x$），将 $g$

映射到 $\ell_{g}$ 给出了一个群同态 $G \rightarrow \operatorname{Sym}(G)$。这个同态是单射，因为 $\ell_{g}$ 决定了 $g$（毕竟 $\ell_{g}(e)=g$）。因此对应关系 $g \mapsto \ell_{g}$ 是将 $G$ 作为子群嵌入到 $\operatorname{Sym}(G)$ 中。

允许一个群像凯莱定理证明中那样表现为一个集合上的置换，是一个非常有用的想法，当这种情况发生时，我们说该群**作用**于该集合。

定义 1.3. 群 $G$ 在集合 $X$ 上的一个**作用**是指，对每个 $g \in G$，选择一个置换 $\pi_{g}: X \rightarrow X$，使得以下两个条件成立：

- $\pi_{e}$ 是恒等映射：对每个 $x \in X$，$\pi_{e}(x)=x$，
- 对 $G$ 中的每个 $g_{1}$ 和 $g_{2}$，$\pi_{g_{1}} \circ \pi_{g_{2}}=\pi_{g_{1} g_{2}}$。

例 1.4. 群 $S_{n}$ 以通常的方式作用在 $X=\{1,2, \ldots, n\}$ 上：对所有 $i$，$\pi_{\sigma}(i)=\sigma(i)$。那么对所有 $i \in X$ 有 $\pi_{1}(i)=i$，并且 $\pi_{\sigma}\left(\pi_{\sigma^{\prime}}(i)\right)=\pi_{\sigma}\left(\sigma^{\prime}(i)\right)=\sigma\left(\sigma^{\prime}(i)\right)=\left(\sigma \sigma^{\prime}\right)(i)=\pi_{\sigma \sigma^{\prime}}(i)$。

例 1.5. 每个群 $G$ 通过左乘函数作用在自身上（$X=G$）。也就是说，我们令 $\pi_{g}: G \rightarrow G$ 为 $\pi_{g}(h)=g h$，对所有 $g \in G$ 和 $h \in G$。那么成为群作用的条件是：对所有 $h \in G$ 有 $e h=h$，以及对所有 $g_{1}, g_{2}, h \in G$ 有 $g_{1}\left(g_{2} h\right)=\left(g_{1} g_{2}\right) h$，这两个条件都成立，因为 $e$ 是单位元且 $G$ 中的乘法是结合的。（这是凯莱定理背后的思想。）

实际上，$\pi_{g}(x)$ 被简单地写作 $g \cdot x$ 或 $g x$。这不是来自两个可能不同集合 $G$ 和 $X$ 的元素的真正乘法。它只是表示 $g$（实际上是与之关联的置换）对元素 $x$ 的作用效果的符号，它给出了 $X$ 中的一个元素 $g \cdot x$。在这种记法中，定义 1.3 中群作用的两个条件采取以下形式：

- 对每个 $x \in X$，$e \cdot x=x$。
- 对每个 $g_{1}, g_{2} \in G$ 和 $x \in X$，$g_{1} \cdot\left(g_{2} \cdot x\right)=\left(g_{1} g_{2}\right) \cdot x$。

群作用的基本思想是，群的元素被视作一个集合上的置换，使得相应置换的复合与群中的运算是相容的。

为了习惯这个记法，我们来证明一个基本结果。
定理 1.6. 设群 $G$ 作用在集合 $X$ 上。如果 $x \in X, g \in G$，且 $y=g \cdot x$，那么 $x=g^{-1} \cdot y$。如果 $x \neq x^{\prime}$，那么 $g \cdot x \neq g \cdot x^{\prime}$。

证明. 由 $y=g \cdot x$ 得 $g^{-1} \cdot y=g^{-1} \cdot(g \cdot x)=\left(g^{-1} g\right) \cdot x=e \cdot x=x$。为了证明 $x \neq x^{\prime} \Longrightarrow g x \neq g x^{\prime}$，我们证明其逆否命题：如果 $g \cdot x=g \cdot x^{\prime}$，那么两边同时应用 $g^{-1}$ 得到 $g^{-1} \cdot(g \cdot x)=g^{-1} \cdot\left(g \cdot x^{\prime}\right)$，所以 $\left(g^{-1} g\right) \cdot x=\left(g^{-1} g\right) \cdot x^{\prime}$，因此 $x=x^{\prime}$。

有各种类型的符号被用来表达“$G$ 作用于 $X$”这个意思，例如 $G \odot X$ 和 $G \curvearrowright X$，但我们这里不使用这些符号。

在群作用的研究中，群论中的许多概念自然地出现：

- **陪集和共轭类是一个群作用的轨道的特例。**
- **在群作用中将一个点移动到另一个点的群元素构成某个子群的一个陪集。**
- **当比较在同一轨道中固定不同点的群元素时，会出现共轭子群。**
- **群 $G$ 的中心中的元素，以及 $G$ 的正规子群，可以解释为 $G$ 的某些作用的不动点。**

**同态也存在：群 $G$ 的一个作用可以解释为定义在 $G$ 上的一种特殊同态。以下是详细说明。**

定理 1.7. 群 $G$ 在集合 $X$ 上的作用等同于从 $G$ 到 $X$ 的置换群 $\operatorname{Sym}(X)$ 的群同态。

证明. 假设我们有 $G$ 在 $X$ 上的一个作用。我们将 $g \cdot x$ 视为 $x$ 的函数（$g$ 固定）。也就是说，对每个 $g \in G$，我们有一个函数 $\pi_{g}: X \rightarrow X$，定义为 $\pi_{g}(x)=g \cdot x$。公理

$$
e \cdot x=x
$$

说明 $\pi_{e}$ 是 $X$ 上的恒等函数。公理

$$
g_{1} \cdot\left(g_{2} \cdot x\right)=\left(g_{1} g_{2}\right) \cdot x
$$

说明 $\pi_{g_{1}} \circ \pi_{g_{2}}=\pi_{g_{1} g_{2}}$，所以 $X$ 上函数的复合对应于 $G$ 中的乘法。此外，$\pi_{g}$ 是一个可逆函数，因为 $\pi_{g^{-1}}$ 是其逆：$\pi_{g}$ 和 $\pi_{g^{-1}}$ 的复合是 $\pi_{e}$，即 $X$ 上的恒等函数。因此 $\pi_{g} \in \operatorname{Sym}(X)$ 且 $g \mapsto \pi_{g}$ 是一个同态 $G \rightarrow \operatorname{Sym}(X)$。

反之，假设我们有一个同态 $f: G \rightarrow \operatorname{Sym}(X)$。对每个 $g \in G$，我们在 $X$ 上有一个置换 $f(g)$，且 $f\left(g_{1} g_{2}\right)=f\left(g_{1}\right) \circ f\left(g_{2}\right)$。令 $g \cdot x=f(g)(x)$ 定义了 $G$ 在 $X$ 上的一个群作用，因为 $f$ 的同态性质产生了群作用的定义性质。

从这个观点来看，平凡作用（即对所有 $x \in X$ 有 $g \cdot x=x$）的 $g \in G$ 的集合正是与作用相关的同态 $G \rightarrow \operatorname{Sym}(X)$ 的核。因此那些在 $X$ 上平凡作用的 $g$ **被称为属于该作用的核。**

在第 6 节之前，我们**不会经常使用定理 1.7 的解释**。在那之前，我们采取更具体的观点，**将群作用视为 $g$ 与 $x$ 的一种乘积 $g \cdot x$，取值于 $X$，并服从性质 $e \cdot x=x$ 和 $g_{1} \cdot\left(g_{2} \cdot x\right)=\left(g_{1} g_{2}\right) \cdot x$。**

以下是后面各节的概要。第 2 节描述了群作用的几个具体例子以及适用于所有群的一些一般作用。第 3 节描述了重要的轨道-稳定化子公式。简短的第 4 节分离出了 $p$-群作用的一个重要不动点同余式。第 5 节和第 6 节给出了群作用在群论中的应用。在附录 A 中，群作用被用来推导数论中的三个经典同余式。

## 2. 例子

例 2.1. 我们可以让 $\mathbf{R}^{n}$ 通过平移作用于自身：对 $\mathbf{v} \in \mathbf{R}^{n}$，令 $T_{\mathbf{v}}: \mathbf{R}^{n} \rightarrow \mathbf{R}^{n}$ 为 $T_{\mathbf{v}}(\mathbf{w})=\mathbf{w}+\mathbf{v}$。群作用的公理是：$T_{\mathbf{0}}(\mathbf{w})=\mathbf{w}$ 和 $T_{\mathbf{v}_{1}}\left(T_{\mathbf{v}_{2}}(\mathbf{w})\right)= T_{\mathbf{v}_{1}+\mathbf{v}_{2}}(\mathbf{w})$。这些由向量加法的性质成立：

$$
\mathbf{w}+\mathbf{0}=\mathbf{w}, \quad\left(\mathbf{w}+\mathbf{v}_{2}\right)+\mathbf{v}_{1}=\mathbf{w}+\left(\mathbf{v}_{1}+\mathbf{v}_{2}\right) .
$$

（这是例 1.5 使用加法记法的一个特例。）
例 2.2. 对于 $n \geq 3, D_{n}$ 作为刚体运动作用于正 $n$ 边形。我们也可以将 $D_{n}$ 视为仅作用于正 $n$ 边形的 $n$ 个顶点。这不会丢失信息，因为知道顶点在刚体运动下的去向就决定了其他所有东西的去向。通过关注 $D_{n}$ 在 $n$ 个顶点上的作用，并以某种方式用 $1,2, \ldots, n$ 标记它们，我们使 $D_{n}$ 作用于 $\{1,2, \ldots, n\}$（$n=4$ 的情况为例 1.1）。

我们也可以让 $D_{n}$ 作用于正 $n$ 边形的对角线集合，因为刚体运动将对角线发送到对角线。

例 2.3. 群 $\mathrm{GL}_{n}(\mathbf{R})$ 以通常的方式作用于 $\mathbf{R}^{n}$ 中的向量：矩阵可以与（列）向量相乘：$A \cdot \mathbf{v}=A \mathbf{v}$。群作用的公理是矩阵-向量乘法的性质：$I_{n} \mathbf{v}=\mathbf{v}$ 和 $A(B \mathbf{v})=(A B) \mathbf{v}$，这是矩阵-向量乘法的标准性质。在这个作用下，原点 $\mathbf{0}$ 被每个 $A$ 固定，而其他向量则被移动（随着 $A$ 变化）。
例 2.4. 仿射线性变换群 $f: \mathbf{R}^{n} \rightarrow \mathbf{R}^{n}$，其中 $f(\mathbf{v})= A \mathbf{v}+\mathbf{b}$，$A \in \mathrm{GL}_{n}(\mathbf{R})$ 且 $\mathbf{b} \in \mathbf{R}^{n}$（一个可逆线性映射加上一个平移），通过 $f \cdot \mathbf{v}=f(\mathbf{v})=A \mathbf{v}+\mathbf{b}$ 对所有 $\mathbf{v} \in \mathbf{R}^{n}$ 作用在 $\mathbf{R}^{n}$ 上。在这个作用下，原点 $\mathbf{O}$ 被移动到 b。仿射线性映射 $f$ 知道其公式中的 $A$ 和 $\mathbf{b}$ 是什么：$\mathbf{b}$ 是 $f(\mathbf{0})$，而 $A$ 的列是 $f\left(\mathbf{e}_{i}\right)-f(\mathbf{0})$，其中 $1 \leq i \leq n$。将 $f$ 写成 $f_{A, \mathbf{b}}$，群中的单位元是 $f_{I_{n}, \mathbf{0}}$，乘法是 $f_{A, \mathbf{b}} \circ f_{A^{\prime}, \mathbf{b}^{\prime}}=f_{A A^{\prime}, A \mathbf{b}^{\prime}+\mathbf{b}}$（比较两边在每个 $\mathbf{v}$ 的值），且 $f_{A, \mathbf{b}}^{-1}=f_{A^{-1},-A^{-1} \mathbf{b}}$。

在这个设定下，群作用的公理说对所有 $\mathbf{v} \in \mathbf{R}^{n}$ 有 $f_{A, \mathbf{b}} \cdot\left(f_{A^{\prime}, \mathbf{b}^{\prime}} \cdot \mathbf{v}\right)=\left(f_{A, \mathbf{b}} \circ f_{A^{\prime}, \mathbf{b}^{\prime}}\right) \cdot \mathbf{v}$，读者应验证这确实成立。
例 2.5. 令 $G$ 为 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 上的仿射线性变换群，即映射 $f:(\mathbf{Z} / 2 \mathbf{Z})^{2} \rightarrow(\mathbf{Z} / 2 \mathbf{Z})^{2}$，其中 $f(\mathbf{v})=A \mathbf{v}+\mathbf{b}$，$A \in \mathrm{GL}_{2}(\mathbf{Z} / 2 \mathbf{Z})$ 且 $\mathbf{b} \in(\mathbf{Z} / 2 \mathbf{Z})^{2}$。每个 $f$ 知道其 $A$ 和 $\mathbf{b}: \mathbf{b}=f(\mathbf{0})$ 且 $A$ 的列为 $f\left(\binom{1}{0}\right)-\mathbf{b}$ 和 $f\left(\binom{0}{1}\right)-\mathbf{b}$。通过计数 $A$ 和 b 的数量，$|G|=\left|\mathrm{GL}_{2}(\mathbf{Z} / 2 \mathbf{Z})\right|\left|(\mathbf{Z} / 2 \mathbf{Z})^{2}\right|=(6)(4)=24$。那么 $G \cong S_{4}$ 吗？

由于 $G$ 的每个元素都是可逆函数 $(\mathbf{Z} / 2 \mathbf{Z})^{2} \rightarrow(\mathbf{Z} / 2 \mathbf{Z})^{2}$，因此 $G$ 作用在 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 上。（这类似于前一个例子，只是将 $\mathbf{R}^{n}$ 替换为 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$。）$G$ 的每个元素完全由其在 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 上的效果决定，而 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 的大小为 4，因此 $G$ 在 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 上的作用给了我们一个单射同态 $G \rightarrow \operatorname{Sym}\left((\mathbf{Z} / 2 \mathbf{Z})^{2}\right) \cong S_{4}$。由于 $|G|=24$，这个同态必然是一个同构，所以 $G \cong S_{4}$。

为了将 $G$ 的元素解释为 $S_{4}$ 中的置换，让我们用 $1,2,3,4$ 标记 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 的元素，例如 $\binom{0}{0} \leftrightarrow 1,\binom{1}{0} \leftrightarrow 2,\binom{0}{1} \leftrightarrow 3$，且 $\binom{1}{1} \leftrightarrow 4$。要在 $G$ 中实现置换 (12) 意味着在 $(\mathbf{Z} / 2 \mathbf{Z})^{2}$ 上找到一个仿射线性映射 $f$，它交换 $\binom{0}{0}$ 与 $\binom{1}{0}$ 并固定 $\binom{0}{1}$ 和 $\binom{1}{1}$（如果 $f$ 固定了 $\binom{0}{1}$ 和 $\binom{1}{1}$ 中的一个，则迫使 $f$ 固定另一个，因为另一个向量无处可去）。记 $f(\mathbf{v})=A \mathbf{v}+\mathbf{b}$，我们需要 $f\binom{0}{0}=\binom{1}{0}$ 且 $f\binom{1}{0}=\binom{0}{0}$，所以 $\mathbf{b}=\binom{1}{0}$ 且 $A\binom{1}{0}+\mathbf{b}=\binom{0}{0}$。因此 $A\binom{1}{0}=-\mathbf{b}=\mathbf{b}=\binom{1}{0}$：$A$ 的第一列是 $\binom{1}{0}$。而 $f\binom{0}{1}=\binom{0}{1}$ 表明 $A\binom{0}{1}+\binom{1}{0}=\binom{0}{1}$，所以 $A\binom{0}{1}=\binom{0}{1}-\binom{1}{0}=\binom{1}{1}$：$A$ 的第二列是 $\binom{1}{1}$。因此 $f(\mathbf{v})=\left(\begin{array}{ll}1 & 1 \\ 0 & 1\end{array}\right) \mathbf{v}+\binom{1}{0}$。

检查你能否自己推导出在 $G$ 中实现 (13) 和 (14) 的仿射线性映射是 $f(\mathbf{v})=\left(\begin{array}{ll}1 & 0 \\ 1 & 1\end{array}\right) \mathbf{v}+\binom{0}{1}$ 和 $f(\mathbf{v})=\left(\begin{array}{ll}0 & 1 \\ 1 & 0\end{array}\right) \mathbf{v}+\binom{1}{1}$。不要只是检查它们有效：要能够推导出每种情况下 $f$ 的这些表达式。
例 2.6. 物理定律对于一个观察者来说，在每个位置、每个时间、每个方向上，以及以固定速度沿固定方向运动时，都应该是相同的。所有这些物理定律不应改变的条件可以用一个 10 维群在 $\mathbf{R}^{4}$（时空）上的作用来描述，无论是在相对论还是非相对论的情况下。更多细节请参见附录 B。
例 2.7. 群 $S_{n}$ 通过置换变量作用于多项式 $f\left(T_{1}, \ldots, T_{n}\right)$：

$$
\begin{equation*}
(\sigma \cdot f)\left(T_{1}, \ldots, T_{n}\right)=f\left(T_{\sigma(1)}, \ldots, T_{\sigma(n)}\right) \tag{2.1}
\end{equation*}
$$

其效果是将 $f\left(T_{1}, \ldots, T_{n}\right)$ 中每个地方的 $T_{i}$ 替换为 $T_{\sigma(i)}$。例如，在 $S_{3}$ 中 (12)(23)= (123)，并且 (12) $\cdot\left((23) \cdot\left(T_{2}+T_{3}^{2}\right)\right)=(12) \cdot\left(T_{3}+T_{2}^{2}\right)=T_{3}+T_{1}^{2}$ 以及 (123) $\cdot\left(T_{2}+T_{3}^{2}\right)=T_{3}+T_{1}^{2}$，两种方式得到相同的结果。

显然有 (1) $\cdot f=f$。为了检查对所有 $S_{n}$ 中的 $\sigma$ 和 $\sigma^{\prime}$ 有 $\sigma \cdot\left(\sigma^{\prime} \cdot f\right)=\left(\sigma \sigma^{\prime}\right) \cdot f$，从而说明 (2.1) 是 $S_{n}$ 在 $n$ 变量多项式上的一个群作用，注意 $\sigma^{\prime} \cdot f$ 将 $f$ 中的每个 $T_{i}$ 替换为 $T_{\sigma^{\prime}(i)}$。将 $\sigma$ 应用于一个多项式会将其中的每个 $T_{j}$ 替换为 $T_{\sigma(j)}$，所以它把每个 $T_{\sigma^{\prime}(i)}$ 替换为 $T_{\sigma\left(\sigma^{\prime}(i)\right)}$。因此先应用 $\sigma^{\prime}$ 再应用 $\sigma$ 的效果是

$$
f\left(T_{1}, \ldots, T_{n}\right) \stackrel{\sigma^{\prime}}{\mapsto} f\left(T_{\sigma^{\prime}(1)}, \ldots, T_{\sigma^{\prime}(n)}\right) \stackrel{\sigma}{\mapsto} f\left(T_{\sigma\left(\sigma^{\prime}(1)\right)}, \ldots, T_{\sigma\left(\sigma^{\prime}(n)\right)}\right) .
$$

最后一个表达式是 $f\left(T_{\left(\sigma \sigma^{\prime}\right)(1)}, \ldots, T_{\left(\sigma \sigma^{\prime}\right)(n)}\right)$，即 $\sigma \sigma^{\prime} \cdot f$，所以 $\sigma \cdot\left(\sigma^{\prime} \cdot f\right)=\left(\sigma \sigma^{\prime}\right) \cdot f$。
由于 $f$ 和 $\sigma \cdot f$ 次数相同，并且如果 $f$ 是齐次的，那么 $\sigma \cdot f$ 也是齐次的，$S_{n}$ 在 $n$ 变量多项式上的这个作用可以限制到具有固定次数的 $n$ 变量多项式，或者具有固定次数的齐次 $n$ 变量多项式。一个例子是 $S_{n}$ 作用在齐次线性多项式 $\left\{a_{1} T_{1}+\cdots+a_{n} T_{n}\right\}$ 上，其中

$$
\begin{equation*}
\sigma \cdot\left(c_{1} T_{1}+\cdots+c_{n} T_{n}\right)=c_{1} T_{\sigma(1)}+\cdots+c_{n} T_{\sigma(n)}=c_{\sigma^{-1}(1)} T_{1}+\cdots+c_{\sigma^{-1}(n)} T_{n} \tag{2.2}
\end{equation*}
$$

拉格朗日对例 2.7 中群作用的研究（约 1770 年）标志着对称群在代数中的首次系统使用。拉格朗日想理解为什么没有人找到四次以上多项式根的求根公式的类似物。他并不完全成功，尽管他通过这个群作用发现 $n \leq 4$ 和 $n=5$ 的情况有一些不同的特征。

例 2.8. 这是一个微妙的例子，请仔细注意。让 $S_{n}$ 通过置换坐标作用在 $\mathbf{R}^{n}$ 上：对 $\sigma \in S_{n}$ 和 $v=\left(c_{1}, \ldots, c_{n}\right) \in \mathbf{R}^{n}$，令 $\pi_{\sigma}(v)=\left(c_{\sigma(1)}, \ldots, c_{\sigma(n)}\right)$。

例如，令 $n=3, \sigma=(12), \sigma^{\prime}=(23)$，且 $v=(5,7,9)$。那么

$$
\pi_{\sigma}\left(\pi_{\sigma^{\prime}}(v)\right)=\pi_{(12)}\left(\pi_{(23)}(5,7,9)\right)=\pi_{(12)}(5,9,7)=(9,5,7)
$$

并且

$$
\pi_{\sigma \sigma^{\prime}}(5,7,9)=\pi_{(123)}(5,7,9)=(7,9,5),
$$

两者不一致，所以将 $v$ 发送到 $\mathbf{R}^{n}$ 中的 $\pi_{\sigma}(v)$ 并不是 $S_{n}$ 在 $\mathbf{R}^{n}$ 上的群作用。
如果我们在一般情况下计算 $\pi_{\sigma}\left(\pi_{\sigma^{\prime}}(v)\right)$ 和 $\pi_{\sigma \sigma^{\prime}}(v)$ 来看看出了什么问题，会发生一件奇特的事情，因为很容易让自己相信我们确实有一个群作用：

$$
\begin{aligned}
\pi_{\sigma}\left(\pi_{\sigma^{\prime}}\left(c_{1}, \ldots, c_{n}\right)\right) & =\pi_{\sigma}\left(c_{\sigma^{\prime}(1)}, \ldots, c_{\sigma^{\prime}(n)}\right) \\
& =\left(c_{\sigma\left(\sigma^{\prime}(1)\right)}, \ldots, c_{\sigma\left(\sigma^{\prime}(n)\right)}\right) \\
& =\left(c_{\left(\sigma \sigma^{\prime}\right)(1)}, \ldots, c_{\left(\sigma \sigma^{\prime}(n)\right.}\right) \\
& =\pi_{\sigma \sigma^{\prime}}\left(c_{1}, \ldots, c_{n}\right)
\end{aligned}
$$

这表明 $\pi_{\sigma} \circ \pi_{\sigma^{\prime}}=\pi_{\sigma \sigma^{\prime}}$，但这并不是我们在上面的数值例子中看到的。发生了什么事？！？错误确实在一般计算中，而不是在例子中。试着在继续阅读之前找出错误。

错误出现在第二行，当我们通过将 $\sigma$ 应用于指标 $\sigma^{\prime}(i)$ 来计算 $\pi_{\sigma}\left(c_{\sigma^{\prime}(1)}, \ldots, c_{\sigma^{\prime}(n)}\right)$ 时。一个向量在其坐标被置换后并不记住其坐标的指标：要计算 $\pi_{(12)}\left(\pi_{(23)}(5,7,9)\right)=\pi_{(12)}(5,9,7)$，下一步将 $(5,9,7)$ 视为一个坐标按顺序索引为 $1,2,3$ 的新向量，尽管坐标顺序已从原来的 ( $5,7,9$ ) 改变。$\pi_{\sigma}(v)$ 的计算总是需要 $v$ 的坐标指标按该顺序从 1 到 $n$。因此当计算 $\pi_{(12)}\left(\pi_{(23)}\left(c_{1}, c_{2}, c_{3}\right)\right)=\pi_{(12)}\left(c_{1}, c_{3}, c_{2}\right)$ 时，在下一步中，记 $\left(c_{1}, c_{3}, c_{2}\right)=\left(d_{1}, d_{2}, d_{3}\right)$。那么

$$
\pi_{(12)}\left(\pi_{(23)}\left(c_{1}, c_{2}, c_{3}\right)\right)=\pi_{(12)}\left(c_{1}, c_{3}, c_{2}\right)=\pi_{(12)}\left(d_{1}, d_{2}, d_{3}\right)=\left(d_{2}, d_{1}, d_{3}\right)=\left(c_{3}, c_{1}, c_{2}\right),
$$

这与

$$
\pi_{(12)(23)}\left(c_{1}, c_{2}, c_{3}\right)=\pi_{(123)}\left(c_{1}, c_{2}, c_{3}\right)=\left(c_{2}, c_{3}, c_{1}\right) .
$$

不一致。
一般来说，对于 $S_{n}$ 中的 $\sigma$ 和 $\sigma^{\prime}$，以及 $\mathbf{R}^{n}$ 中的 $v=\left(c_{1}, \ldots, c_{n}\right)$，

$$
\begin{aligned}
\pi_{\sigma}\left(\pi_{\sigma^{\prime}}(v)\right) & =\pi_{\sigma}\left(c_{\sigma^{\prime}(1)}, \ldots, c_{\sigma^{\prime}(n)}\right) \\
& =\pi_{\sigma}\left(d_{1}, \ldots, d_{n}\right) \text { 其中 } d_{i}=c_{\sigma^{\prime}(i)} \\
& =\left(d_{\sigma(1)}, \ldots, d_{\sigma(n)}\right) \\
& =\left(c_{\sigma^{\prime}(\sigma(1))}, \ldots, c_{\sigma^{\prime}(\sigma(n))}\right) \\
& =\left(c_{\left(\sigma^{\prime} \sigma\right)(1)}, \ldots, c_{\left(\sigma^{\prime} \sigma\right)(n)}\right) \\
& =\pi_{\sigma^{\prime} \sigma}(v)
\end{aligned}
$$

所以 $\pi_{\sigma} \circ \pi_{\sigma^{\prime}}$ 是 $\pi_{\sigma^{\prime} \sigma}$，而不是 $\mathbf{R}^{n}$ 上的 $\pi_{\sigma \sigma^{\prime}}$，如果 $\sigma^{\prime} \sigma \neq \sigma \sigma^{\prime}$（例如，$n \geq 3, \sigma=(12), \sigma^{\prime}=(23)$）。
在不使用用另一个字母重写坐标的技巧的情况下，解释为什么 $\pi_{\sigma} \circ \pi_{\sigma^{\prime}}=\pi_{\sigma^{\prime} \sigma}$ 的一种方法是，将公式 $\pi_{\sigma}\left(\left(c_{1}, \ldots, c_{n}\right)\right)=\left(c_{\sigma(1)}, \ldots, c_{\sigma(n)}\right)$ 表示为 $\left(\pi_{\sigma}(v)\right)_{i}= v_{\sigma(i)}$，其中 $i=1, \ldots, n$（例如，当 $v=\left(c_{1}, \ldots, c_{n}\right)$ 且 $i=1$ 时，$\left(\pi_{\sigma}(v)\right)_{i}$ 和 $v_{\sigma(i)}$ 都是 $c_{\sigma(1)}$）。那么对所有 $v \in \mathbf{R}^{n}$ 和 $i=1, \ldots, n$，

$$
\left(\pi_{\sigma}\left(\pi_{\sigma^{\prime}}(v)\right)\right)_{i}=\left(\pi_{\sigma^{\prime}}(v)\right)_{\sigma(i)}=v_{\sigma^{\prime}(\sigma i)}=v_{\left(\sigma^{\prime} \sigma\right)(i)}=\left(\pi_{\sigma^{\prime} \sigma}(v)\right)_{i}
$$

所以 $\pi_{\sigma} \circ \pi_{\sigma^{\prime}}=\pi_{\sigma^{\prime} \sigma}$ 在 $\mathbf{R}^{n}$ 上成立。
为了在这里有一个真正的群作用，重新定义 $S_{n}$ 在 $\mathbf{R}^{n}$ 上的效果，使用 $S_{n}$ 中的逆：令 $\sigma \cdot v=\left(c_{\sigma^{-1}(1)}, \ldots, c_{\sigma^{-1}(n)}\right)$，或者等价地，对所有 $i$，$(\sigma \cdot v)_{i}=v_{\sigma^{-1}(i)}$。那么 $\sigma \cdot\left(\sigma^{\prime} \cdot v\right)=\left(\sigma \sigma^{\prime}\right) \cdot v$，我们就得到了 $S_{n}$ 在 $\mathbf{R}^{n}$ 上的一个群作用，这实际上本质上就是前一个例子中 $S_{n}$ 在齐次线性多项式上的作用（见 (2.2)）。确实，如果 $e_{1}, \ldots, e_{n}$ 是 $\mathbf{R}^{n}$ 的标准基且 $v=\sum_{i=1}^{n} c_{i} e_{i}$，那么

$$
\sigma \cdot \sum_{i=1}^{n} c_{i} e_{i}=\left(c_{\sigma^{-1}(1)}, \ldots, c_{\sigma^{-1}(n)}\right)=\sum_{i=1}^{n} c_{\sigma^{-1}(i)} e_{i}=\sum_{i=1}^{n} c_{i} e_{\sigma(i)},
$$

这就是 (2.2) 用 $e_{i}$ 代替 $T_{i}$ 后的样子。换句话说，每个 $\sigma \in S_{n}$ 在 $\mathbf{R}^{n}$ 上的作用是 $\mathbf{R}$-线性的，并且置换基向量 $\left\{e_{i}\right\}$（而不是系数！）的方式与它置换指标的方式相同：$\sigma\left(e_{i}\right)=e_{\sigma(i)}$。

从最后这两个例子中得到的教训是，当 $S_{n}$ 置换多项式中的变量时，它“直接”作用，但当 $S_{n}$ 置换向量中的坐标时，它必须使用逆来作用。当 $S_{n}$ 作用在变量或坐标上时，它在一个情况下不使用逆作用，在另一个情况下使用逆作用，但很容易忘记哪种情况是哪种。至少要记住你需要小心。

例 2.9. 令 $G$ 为一个作用于集合 $X$ 的群，$S$ 为一个集合。记 $\operatorname{Map}(X, S)$ 为所有函数 $f: X \rightarrow S$ 的集合。很自然地尝试通过以下规则定义 $G$ 在集合 $\operatorname{Map}(X, S)$ 上的作用：

$$
\begin{equation*}
\left(\pi_{g} f\right)(x)=f(g x) \tag{2.3}
\end{equation*}
$$

其中 $g x$ 是 $g \in G$ 在 $x \in X$ 上的作用。虽然 $\pi_{g} f$ 是一个函数 $X \rightarrow S$，但将每个 $f$ 发送到 $\pi_{g} f$ 通常并不是 $G$ 在 $\operatorname{Map}(X, S)$ 上的作用，尽管很容易让自己误以为是：对 $G$ 中的 $g$ 和 $h$，以及 $x \in X$，

$$
\pi_{g}\left(\left(\pi_{h} f\right)(x)\right)=\pi_{g}(f(h x))=f(g(h x))=f((g h) x)=\left(\pi_{g h} f\right)(x)
$$

这对所有 $x \in X$ 都成立，所以 $\pi_{g}\left(\pi_{h} f\right)=\pi_{g h} f$，对吗？不对。上面的计算是错误的，因为第一个表达式 $\pi_{g}\left(\left(\pi_{h} f\right)(x)\right)$ 是无意义的：$\left(\pi_{h} f\right)(x)=f(h x)$ 属于 $S$，而 $G$ 尚未在 $S$ 上定义作用，所以 $\pi_{g}(f(h x))$ 没有定义。即使 $G$ 作用于 $S$，$\pi_{g}$ 也是应用于函数 $X \rightarrow S$，而不是应用于 $S$ 的元素。这个错误在于混淆了 (2.3) 中的 ( $\pi_{g} f$ )( $x$ ) 和无意义的表达式 $\pi_{g}(f(x))$。

一个正确的计算是

$$
\left(\pi_{g}\left(\pi_{h} f\right)\right)(x)=\left(\pi_{h} f\right)(g x)=f(h(g x))=f((h g) x)=\left(\pi_{h g} f\right)(x) .
$$

因此 $\pi_{g}\left(\pi_{h} f\right)=\pi_{h g} f$。这种指标的反转类似于例 2.8 中的错误作用。为了在 $G$ 已经（从左）作用于 $X$ 的情况下获得 $G$ 在 $\operatorname{Map}(X, S)$ 上的一个群作用，将 (2.3) 中的 $g$ 替换为 $g^{-1}$：令

$$
(g \cdot f)(x)=f\left(g^{-1} x\right)
$$

现在

$$
(g \cdot(h \cdot f))(x)=(h \cdot f)\left(g^{-1} x\right)=f\left(h^{-1}\left(g^{-1} x\right)\right)=f\left((g h)^{-1} x\right)=((g h) \cdot f)(x),
$$

所以 $g \cdot(h \cdot f)=(g h) \cdot f$。这是 $G$ 在 $\operatorname{Map}(X, S)$ 上的一个群作用。
如果 $G$ 是 $S_{n}, X$ 是具有其自然 $S_{n}$-作用的 $\{1, \ldots, n\}$，且 $S=\mathbf{R}$，那么 $\operatorname{Map}(X, S)=\mathbf{R}^{n}$：写下向量 $v=\left(c_{1}, \ldots, c_{n}\right)$ 相当于按顺序列出坐标，而按顺序列出的坐标就是一个函数 $f:\{1,2, \ldots, n\} \rightarrow \mathbf{R}$，其中 $f(i)=c_{i}$。定义 $(g \cdot f)(i)=f\left(g^{-1} i\right)$ 相当于说 $g \cdot\left(c_{1}, \ldots, c_{n}\right)=\left(c_{g^{-1}(1)}, \ldots, c_{g^{-1}(n)}\right)$，这正是例 2.8 末尾 $S_{n}$ 在 $\mathbf{R}^{n}$ 上的有效作用。

**一个一般群有三个基本作用：在自身上的左乘、在自身上的共轭，以及在子群的左陪集上的左乘。现在将描述所有这些。请仔细阅读！**

例 2.10. 为了使 $G$ 通过左乘作用在自身上，我们令 $X=G$，并且 $g \cdot x$（对于 $g \in G$ 和 $x \in G$ ）是 $G$ 中 $g$ 和 $x$ 的通常乘积。这个例子在凯莱定理的证明和例 1.5 中已经使用过，群作用的定义由 $G$ 中的乘法公理满足，例如，$g_{1} \cdot\left(g_{2} \cdot x\right)=\left(g_{1} g_{2}\right) \cdot x$ 来自 $G$ 中的结合律。

注意，$G$ 在自身上的右乘，由 $r_{g}(x)=x g$ 给出（对于 $G$ 中的 $g$ 和 $x$），不是一个作用，因为复合的顺序被颠倒了：$r_{g_{1}} \circ r_{g_{2}}=r_{g_{2} g_{1}}$。但是如果我们令 $r_{g}(x)=x g^{-1}$，那么我们就得到一个作用。这可以被称为通过右逆乘的作用（非标准术语）。

例 2.11. 为了使 $G$ 通过共轭作用在自身上，令 $X=G$ 并令 $g \cdot x=g x g^{-1}$。这里 $g \in G$ 且 $x \in G$。由于 $e \cdot x=e x e^{-1}=x$ 且

$$
\begin{aligned}
g_{1} \cdot\left(g_{2} \cdot x\right) & =g_{1} \cdot\left(g_{2} x g_{2}^{-1}\right) \\
& =g_{1}\left(g_{2} x g_{2}^{-1}\right) g_{1}^{-1} \\
& =\left(g_{1} g_{2}\right) x\left(g_{1} g_{2}\right)^{-1} \\
& =\left(g_{1} g_{2}\right) \cdot x,
\end{aligned}
$$

共轭是一个群作用。
例 2.12. 对于子群 $H \subset G$，考虑左陪集空间 $G / H=\{a H: a \in G\}$。（我们不关心是否 $H \triangleleft G$，因为我们只是将 $G / H$ 视为一个集合。）令
$G$ 通过左乘作用在 $G / H$ 上。也就是说，对于 $g \in G$ 和一个左陪集 $a H(a \in G)$，令

$$
g \cdot a H=g a H=\{g y: y \in a H\} .
$$

这是 $G$ 在 $G / H$ 上的一个作用，因为 $e a H=a H$ 且

$$
\begin{aligned}
g_{1} \cdot\left(g_{2} \cdot a H\right) & =g_{1} \cdot\left(g_{2} a H\right) \\
& =g_{1} g_{2} a H \\
& =\left(g_{1} g_{2}\right) \cdot a H
\end{aligned}
$$

例 2.10 是 $H$ 平凡时的特例。
例 2.13. 令 $G=\mathbf{Z} /(4)$ 通过加法作用在自身上（$X=G$）。例如，加 1 的效果是 $0 \mapsto 1 \mapsto 2 \mapsto 3 \mapsto 0$。因此，在 $\mathbf{Z} /(4)$ 上加 1 是一个 4-轮换 ( 0123 )。加 2 的效果是 $0 \mapsto 2,1 \mapsto 3,2 \mapsto 0$，和 $3 \mapsto 1$。因此，作为 $\mathbf{Z} /(4)$ 上的置换，加 2 是 (02)(13)，是两个 2-轮换的乘积。这两个置换的复合是 $(0123)(02)(13)=(0321)$，这是由加 3 描述的 $G$ 的置换，并且在 $\mathbf{Z} /(4)$ 中 $3=1+2$。（这是例 2.10 使用加法记法的一个特例。）

我们回到群 $G$ 通过左乘和共轭作用在自身上的情况，并将这些作用推广到子集而不只是点。

例 2.14. 当 $A$ 是 $G$ 的一个子集，且 $g \in G$，子集 $g A=\{g a: a \in A\}$ 与 $A$ 大小相同。因此 $G$ 通过左乘作用在 $G$ 的子集上，甚至是具有固定大小的子集上。例 2.10 是 $G$ 的单点子集的特例。注意，当 $H \subset G$ 是一个子群时，$g H$ 通常不是 $G$ 的子群，所以 $G$ 在其子集上的左乘作用并不将子群变成其他子群。

例 2.15. 作为例 2.14 的一个特例，令 $S_{4}$ 通过规则 $\sigma \cdot\{a, b\}=\{\sigma(a), \sigma(b)\}$ 作用在 $\{1,2,3,4\}$ 的成对元素上。

有 6 对：

$$
x_{1}=\{1,2\}, x_{2}=\{1,3\}, x_{3}=\{1,4\}, x_{4}=\{2,3\}, x_{5}=\{2,4\}, x_{6}=\{3,4\}
$$

(12) 在这些对上的效果是

$$
\begin{array}{lll}
(12) x_{1}=x_{1}, & (12) x_{2}=x_{4}, & (12) x_{3}=x_{5} \\
(12) x_{4}=x_{2}, & (12) x_{5}=x_{3}, & (12) x_{6}=x_{6}
\end{array}
$$

因此，作为集合 $\left\{x_{1}, \ldots, x_{6}\right\}$ 上的置换，(12) 的作用类似于 $\left(x_{2} x_{4}\right)\left(x_{3} x_{5}\right)$。这很有趣：我们使得 $S_{4}$ 中的一个对换看起来像 $S_{6}$ 中两个 2-轮换的乘积。特别是，我们使得 $\{1,2,3,4\}$ 的一个奇置换看起来像一个新集合上的偶置换。这是一个嵌入 $S_{4} \hookrightarrow A_{6}$。
例 2.16. 令 $G$ 为一个群。当 $A \subset G, g A g^{-1}$ 是一个与 $A$ 大小相同的子集。此外，与 $G$ 在其子集上的左乘作用不同，$G$ 在其子集上的共轭作用将子群变为子群：当 $H \subset G$ 是子群时，$g H g^{-1}$ 也是子群。例如，$S_{4}$ 中大小为 4 的（七个）子群中的三个是

$$
\begin{gathered}
\{(1),(1234),(13)(24),(1432)\}, \quad\{(1),(2134),(23)(14),(2431)\}, \\
\{(1),(12)(34),(13)(24),(14)(23)\} .
\end{gathered}
$$

在 $S_{4}$ 的共轭下，前两个子群可以互相变换，但这两个子群都不能共轭到第三个子群：第一个和第二个子群有一个阶为 4 的元素，而第三个没有。

虽然 $G$ 在自身上（例 2.10）的**左乘作用使不同的群元素变成不同的置换**，但 $G$ 在**自身上（例 2.11）的共轭作用可以使不同的群元素以相同的方式作用**：如果 $g_{1}=g_{2} z$，其中 $z$ 在 $G$ 的中心中，那么 $g_{1}$ 和 $g_{2}$ 在 $G$ 上有相同的共轭作用。群中不同元素以不同方式作用的群作用有一个特殊的名称：

定义 2.17. 如果 $G$ 的不同元素在 $X$ 上以不同的方式作用，则称群 $G$ 在 $X$ 上的作用是**忠实的**（或**有效的**）：当 $g_{1} \neq g_{2}$ 在 $G$ 中时，存在一个 $x \in X$ 使得 $g_{1} \cdot x \neq g_{2} \cdot x$。

注意，当我们说 $g_{1}$ 和 $g_{2}$ 作用不同时，我们的意思是它们在某处作用不同，而不是处处不同。这与说两个函数不相等的含义是一致的：它们在某个地方取值不同，而不是处处不同。

例 2.18. $G$ 通过左乘作用在自身上是忠实的：不同的元素将 $e$ 发送到不同的地方。

例 2.19. $G$ 通过共轭作用在自身上是忠实的当且仅当 $G$ 有平凡中心，因为对所有 $g \in G$，$g_{1} g g_{1}^{-1}=g_{2} g g_{2}^{-1}$ 当且仅当 $g_{2}^{-1} g_{1}$ 在 $G$ 的中心中。当 $D_{4}$ 通过共轭作用在自身上时，该作用不是忠实的，因为 $r^{2}$ 平凡作用（它在中心中），所以 1 和 $r^{2}$ 以相同的方式作用。

例 2.20. 当 $H$ 是 $G$ 的子群且 $G$ 通过左乘作用在 $G / H$ 上时（例 2.12），$G$ 中的 $g_{1}$ 和 $g_{2}$ 在 $G / H$ 上以相同的方式作用恰好当对所有 $g \in G$ 有 $g_{1} g H=g_{2} g H$，这意味着 $g_{2}^{-1} g_{1} \in \bigcap_{g \in G} g H g^{-1}$。所以 $G$ 在 $G / H$ 上的左乘作用是忠实的当且仅当子群 $g H g^{-1}$（随着 $g$ 变化）有平凡交集。

例 2.21. $\mathrm{GL}_{2}(\mathbf{R})$ 在 $\mathbf{R}^{2}$ 上的作用是忠实的，因为我们可以通过它在 $\binom{1}{0}$ 和 $\binom{0}{1}$ 上的作用来恢复矩阵的列。

将群作用视为同态（定理 1.7），$G$ 在 $X$ 上的忠实作用是一个单射同态 $G \rightarrow \operatorname{Sym}(X)$。不忠实的作用作为群同态是非单射的。许多重要的同态不是单射。

备注 2.22. 我们一直称之为群作用的东西可以被称为左群作用，而右群作用，记作 $x g$，具有性质 $x e=x$ 和 $\left(x g_{1}\right) g_{2}=x\left(g_{1} g_{2}\right)$。指数记法 $x^{g}$ 代替 $x g$ 在这里很好用，特别是将群中的单位元写作 1：$x^{1}=x$ 和 $\left(x^{g_{1}}\right)^{g_{2}}=x^{g_{1} g_{2}}$。左作用和右作用的区别在于乘积 $g g^{\prime}$ 如何作用：在左作用中 $g^{\prime}$ 先作用，$g$ 后作用，而在右作用中 $g$ 先作用，$g^{\prime}$ 后作用。

$G$ 在自身上的右乘（或者更一般地，$G$ 在子群 $H$ 的右陪集空间上的右乘）是右作用的一个例子。举一个更具体的例子，$\mathrm{GL}_{n}(\mathbf{R})$ 在长度为 $n$ 的行向量上的作用最自然地是一个右作用，因为当 $\mathbf{v}$ 是行向量且 $A \in \mathrm{GL}_{n}(\mathbf{R})$ 时，乘积 $\mathbf{v} A$（而不是 $A \mathbf{v}$）是有意义的。例 2.8 和 2.9 中错误的定义 $\pi_{g}$，因为公式倒过来了（$\pi_{g} \circ \pi_{h}=\pi_{h g}$），是 $G$ 的合法的右作用。

许多群论学家（与大多数其他数学家不同）喜欢将 $h$ 被 $g$ 的共轭定义为 $g^{-1} h g$ 而不是 $g h g^{-1}$，并且这个约定与右（但不是左）共轭作用配合得很好：令 $h^{g}=g^{-1} h g$，我们有 $h^{1}=h$ 和 $\left(h^{g_{1}}\right)^{g_{2}}=h^{g_{1} g_{2}}$。

群的左作用和右作用之间的区别在很大程度上是虚幻的，因为在群中将 $g$ 替换为 $g^{-1}$ 会将左作用变为右作用，反之亦然，因为逆运算
颠倒了 $G$ 中乘法的顺序。我们在例 2.8、2.9 和 2.10 中看到了这个思想的作用。我们将不使用右作用（除了例 3.26），所以对我们来说，“群作用”指的是“左群作用”。

## 3. 轨道和稳定化子

群作用中编码的信息有两个基本部分：一部分告诉我们点去了哪里，另一部分告诉我们点如何保持不动。以下术语指的是这些思想。

定义 3.1. 设群 $G$ 作用于集合 $X$。对每个 $x \in X$，其**轨道**是

$$
\operatorname{Orb}_{x}=\{g \cdot x: g \in G\} \subset X
$$

其**稳定化子**是

$$
\operatorname{Stab}_{x}=\{g \in G: g \cdot x=x\} \subset G .
$$

（$x$ 的稳定化子在文献中常记为 $G_{x}$，其中 $G$ 是群。）当 $g \cdot x=x$ 对每个 $g \in G$ 都成立时，即当 $\operatorname{Orb}_{x}=\{x\}$ 时（或者等价地，当 $\operatorname{Stab}_{x}=G$ 时），我们称 $x$ 为作用的一个**不动点**。

用语言写出轨道和稳定化子的定义，点的轨道是一个几何概念：该点可以被群作用移动到的位置的集合。点的稳定化子是一个代数概念：固定该点的群元素的集合。

我们将经常把 $X$ 的元素称为点，并将轨道的大小称为其长度。如果 $X=G$，如例 2.10 和 2.11，那么当 $G$ 的元素作用在 $G$ 上时，我们将它们视为置换，而当它们被作用时，则视为点。

例 3.2. 当 $\mathrm{GL}_{2}(\mathbf{R})$ 以通常的方式作用在 $\mathbf{R}^{2}$ 上时，$\mathbf{0}$ 的轨道是 $\{\mathbf{0}\}$，因为对每个 $\mathrm{GL}_{2}(\mathbf{R})$ 中的 $A$，有 $A \cdot \mathbf{0}=\mathbf{0}$。$\mathbf{0}$ 的稳定化子是 $\mathrm{GL}_{2}(\mathbf{R})$。

$\binom{1}{0}$ 的轨道是 $\mathbf{R}^{2}-\{\mathbf{0}\}$，换句话说，每个非零向量都可以通过对 $\binom{1}{0}$ 应用一个合适的可逆矩阵得到。确实，如果 $\binom{a}{b} \neq \mathbf{0}$，那么我们有 $\binom{a}{b}=\left(\begin{array}{cc}a & 1 \\ b & 0\end{array}\right)\binom{1}{0}$ 和 $\binom{a}{b}=\left(\begin{array}{ll}a & 0 \\ b & 1\end{array}\right)\binom{1}{0}$。矩阵 $\left(\begin{array}{ll}a & 1 \\ b & 0\end{array}\right)$ 或 $\left(\begin{array}{ll}a & 0 \\ b & 1\end{array}\right)$ 中有一个是可逆的（因为 $a$ 或 $b$ 不为零），所以 $\binom{a}{b}$ 在 $\binom{1}{0}$ 的 $\mathrm{GL}_{2}(\mathbf{R})$-轨道中。$\binom{1}{0}$ 的稳定化子是 $\left\{\left(\begin{array}{ll}1 & x \\ 0 & y\end{array}\right): y \neq 0\right\} \subset \mathrm{GL}_{2}(\mathbf{R})$。

例 3.3. 当群 $\mathrm{GL}_{2}(\mathbf{Z})$ 以通常的方式作用在 $\mathbf{Z}^{2}$ 上时，$\mathbf{0}$ 的轨道是 $\{\mathbf{0}\}$，稳定化子是 $\mathrm{GL}_{2}(\mathbf{Z})$。但与例 3.2 相反，$\binom{1}{0}$ 在 $\mathrm{GL}_{2}(\mathbf{Z})$ 下的轨道不是 $\mathbf{Z}^{2}-\{\mathbf{0}\}$。确实，$\mathrm{GL}_{2}(\mathbf{Z})$ 中的矩阵 $\left(\begin{array}{ll}a & b \\ c & d\end{array}\right)$ 将 $\binom{1}{0}$ 发送到 $\binom{a}{c}$，这是一个坐标互素的向量，因为 $a d-b c= \pm 1$。（例如，$\mathrm{GL}_{2}(\mathbf{Z})$ 不能将 $\binom{1}{0}$ 发送到 $\binom{2}{0}$。）反之，$\mathbf{Z}^{2}$ 中每个坐标互素的向量 $\binom{m}{n}$ 都在 $\binom{1}{0}$ 的 $\mathrm{GL}_{2}(\mathbf{Z})$ 轨道中：我们可以对某些整数 $x$ 和 $y$ 解 $m x+n y=1$，所以 $\left(\begin{array}{cc}m & -y \\ n & x\end{array}\right)$ 在 $\mathrm{GL}_{2}(\mathbf{Z})$ 中（其行列式为 1），且 $\left(\begin{array}{cc}m & -y \\ n & x\end{array}\right)\binom{1}{0}=\binom{m}{n}$。

作为练习检查：在 $\mathrm{GL}_{2}(\mathbf{Z})$ 作用下，$\mathbf{Z}^{2}$ 中的轨道是坐标具有固定最大公约数的向量。每个轨道包含一个形如 $\binom{d}{0}$ 的向量，其中 $d \geq 0$，并且对于 $d>0$，$\binom{d}{0}$ 的稳定化子是 $\left\{\left(\begin{array}{ll}1 & x \\ 0 & y\end{array}\right): y= \pm 1\right\} \subset \mathrm{GL}_{2}(\mathbf{Z})$。

例 3.4. 将 $\mathbf{Z} /(2)$ 等同于 $\mathrm{GL}_{n}(\mathbf{R})$ 的子群 $\left\{ \pm I_{n}\right\}$，给出了 $\mathbf{Z} /(2)$ 在 $\mathbf{R}^{n}$ 上的一个作用，其中 0 作为恒等作用，1 通过对 $\mathbf{R}^{n}$ 取负作用。我们可以将这个 $\mathbf{Z} /(2)$ 的作用限制到 $\mathbf{R}^{n}$ 的单位球面上，然后它被称为**对径作用**，因为其轨道是球面上的对对点（称为**对径点**）。

例 3.5. 令 $G$ 为魔方群：魔方上所有动作序列的集合（保持中心颜色不变）。这个群作用在 8 个角块和 12 个棱块上，这是两个不同的轨道。
例 3.6. 对于 $n \geq 2$，考虑 $S_{n}$ 在其对 $\{1,2, \ldots, n\}$ 的自然作用上。整数 $i \in\{1,2, \ldots, n\}$ 的稳定化子是什么？它是固定 $i$ 的 $\{1,2, \ldots, n\}$ 的置换集合，可以认为是 $\{1,2, \ldots, n\}-\{i\}$ 的置换集合。这是 $S_{n}$ 中一个同构于 $S_{n-1}$ 的副本（一旦我们以确定的方式将 $\{1,2, \ldots, n\}-\{i\}$ 与从 1 到 $n-1$ 的数字等同起来）。对 $S_{n}$ 在 $\{1,2, \ldots, n\}$ 上的自然作用，$\{1,2, \ldots, n\}$ 中每个数字的稳定化子都同构于 $S_{n-1}$。
例 3.7. 对于 $n \geq 2$，固定数字 $k$ 的 $\{1,2, \ldots, n\}$ 的偶置换可以与 $\{1,2, \ldots, n\}-\{k\}$ 的偶置换等同，所以在 $A_{n}$ 的自然作用中，每个点的稳定化子本质上是 $A_{n-1}$（重标记后）。

备注 3.8. 当试图将一个集合视为几何对象时，将其元素称为点是有帮助的，无论它们实际上可能是什么。例如，当我们把 $G / H$ 视为 $G$ 作用（通过左乘）的集合时，将 $H$ 的陪集（即 $G / H$ 的元素）视为 $G / H$ 中的点是有用的。但同时，陪集是 $G$ 的子集。在这两种解释之间存在一种张力：$H$ 的左陪集是 $G / H$ 中的一个点还是 $G$ 的一个子集？两者都是，重要的是能够从两种方式思考陪集。

我们所有将群作用应用于群论的方法都将源于轨道、稳定化子和不动点之间的关系，我们现在在我们的三个基本群作用例子中明确这些关系。

例 3.9. 当一个群 $G$ 通过左乘作用在自身上时，

- 只有一个轨道（因为 $g=g e \in \mathrm{Orb}_{e}$），
- $\mathrm{Stab}_{a}=\{g: g a=a\}=\{e\}$ 是平凡的，
- 没有不动点（如果 $|G|>1$）。

例 3.10. 当一个群 $G$ 通过共轭作用在自身上时，

- $a$ 的轨道是 $\operatorname{Orb}_{a}=\left\{g a g^{-1}: g \in G\right\}$，即 $a$ 的共轭类，
- $\operatorname{Stab}_{a}=\left\{g: g a g^{-1}=a\right\}=\{g: g a=a g\}$ 是 $a$ 的中心化子，记为 $Z(a)$，
- 当 $a$ 与 $G$ 的所有元素交换时，$a$ 是一个不动点，因此共轭的不动点构成中心 $Z(G)$。
例 3.11. 当一个群 $G$（对于一个子群 $H$ ）通过左乘作用在 $G / H$ 上时，
- 只有一个轨道（因为 $g H=g \cdot H \in \mathrm{Orb}_{H}$），
- $\operatorname{Stab}_{a H}=\{g: g a H=a H\}=\left\{g: a^{-1} g a \in H\right\}=a H a^{-1}$，
- 没有不动点（如果 $H \neq G$）。

这些例子说明了几个事实：一个作用不一定有不动点（例 3.9 中 $G$ 非平凡时），不同的轨道可以有不同的长度（例 3.10 中 $G=S_{3}$ 时），并且在同一轨道中的点不一定共享相同的稳定化子（例 3.11 中如果 $H$ 不是正规子群）。
例 3.12. 当 $G$ 通过共轭作用在其子群上时，$\operatorname{Stab}_{H}=\left\{g: g H g^{-1}=H\right\}$ 是正规化子 $\mathrm{N}(H)$，而不动点是 $G$ 的正规子群。

当一个群 $G$ 作用在一个集合 $X$ 上时，$G$ 的每个子群 $H$ 也作用在 $X$ 上。让我们看几个例子。

例 3.13. 当 $H$ 通过左乘作用在 $G$ 上时，

- $a \in G$ 的轨道是 $\{h a: h \in H\}=H a$，一个右 $H$-陪集，
- $\mathrm{Stab}_{a}=\{h: h a=a\}=\{e\}$ 是平凡的，
- 没有不动点（如果 $|H|>1$）。

例 3.14. 当 $H$ 通过右逆乘（见例 2.10）作用在 $G$ 上时，

- $a \in G$ 的轨道是 $\operatorname{Orb}_{a}=\left\{a h^{-1}: h \in H\right\}=a H$，一个左 $H$-陪集，
- $\operatorname{Stab}_{a}=\left\{h: a h^{-1}=a\right\}=\{e\}$ 是平凡的，
- 没有不动点（如果 $|H|>1$）。

例 3.15. 当 $H$ 通过共轭作用在 $G$ 上时，

- $a$ 的 $H$-轨道是 $\operatorname{Orb}_{a}=\left\{h a h^{-1}: h \in H\right\}$，没有特殊名称（这是 $G$ 中与 $a$ $H$-共轭的元素），
- $\operatorname{Stab}_{a}=\left\{h \in H: h a h^{-1}=a\right\}=\{h: h a=a h\}$ 是与 $a$ 交换的 $H$ 的元素（这是 $H \cap Z(a)$，其中 $Z(a)$ 是 $a$ 在 $G$ 中的中心化子）。
- 当 $a$ 与 $H$ 的所有元素交换时，$a$ 是一个不动点。

在下方的汇总表中，$G$ 是一个群，$H$ 是 $G$ 的一个子群。

| 群       | 集合                 | 作用                         | $x$ 的轨道            | $x$ 的稳定化子                               |
| :------ | :----------------- | :------------------------- | :----------------- | :-------------------------------------- |
| $S_{n}$ | $\{1, \ldots, n\}$ | $\sigma \cdot i=\sigma(i)$ | $\{1, \ldots, n\}$ | $\{\sigma: \sigma(x)=x\} \cong S_{n-1}$ |
| G       | G                  | $g \cdot x=g x$            | G                  | \{e\}                                   |
| G       | G                  | $g \cdot x=g x g^{-1}$     | $x$ 的共轭类           | $\{g: g x=x g\}$                        |
| $H$     | G                  | $h \cdot x=h x$            | $H x$              | \{e\}                                   |
| H       | $G$                | $h \cdot x=x h^{-1}$       | $x H$              | \{e\}                                   |
| G       | $G / H$            | $g \cdot a H=g a H$        | $G / H$            | $a H a^{-1}(x=a H)$                     |

以下是关于群作用的基本定理。
定理 3.16. 设群 $G$ 作用于集合 $X$。
a) 作用的不同轨道互不相交，并构成 $X$ 的一个划分。
b) 对每个 $x \in X$，$\operatorname{Stab}_{x}$ 是 $G$ 的一个子群，且对所有 $g \in G$，$\operatorname{Stab}_{g x}=g \operatorname{Stab}_{x} g^{-1}$。
c) 对每个 $x \in X$，存在一个双射 $\operatorname{Orb}_{x} \rightarrow G / \operatorname{Stab}_{x}$，由 $g x \mapsto g \operatorname{Stab}_{x}$ 给出。更具体地说，$g x=g^{\prime} x$ 当且仅当 $g$ 和 $g^{\prime}$ 位于 $\mathrm{Stab}_{x}$ 的同一个左陪集中，并且 $\mathrm{Stab}_{x}$ 的不同左陪集对应于 $\mathrm{Orb}_{x}$ 中的不同点。特别地，如果 $x$ 和 $y$ 在同一轨道中，那么 $\{g \in G: g x=y\}$ 是 $\operatorname{Stab}_{x}$ 的一个左陪集，并且

$$
\begin{equation*}
\left|\operatorname{Orb}_{x}\right|=\left[G: \operatorname{Stab}_{x}\right] \tag{3.1}
\end{equation*}
$$

部分 $b$ 和 $c$ 展示了在群作用中，共轭子群和子群的陪集所扮演的角色。部分 (c) 中将轨道长度与轨道中一点的稳定化子在 $G$ 中的指数联系起来的公式，被称为**轨道-稳定化子公式**。

证明. a) 我们通过证明两个重叠的轨道必然重合来证明群作用中的不同轨道是互不相交的。$^{2}$ 假设 $\operatorname{Orb}_{x}$ 和 $\operatorname{Orb}_{y}$ 有一个公共元素 $z$：

$$
z=g_{1} x, \quad z=g_{2} y
$$

我们想证明 $\operatorname{Orb}_{x}=\operatorname{Orb}_{y}$。证明 $\operatorname{Orb}_{x} \subset \operatorname{Orb}_{y}$ 就足够了，因为然后我们可以交换 $x$ 和 $y$ 的角色得到反向包含。

[^1] 对每个点 $u \in \operatorname{Orb}_{x}$，记 $u=g x$，其中 $g \in G$。由于 $x=g_{1}^{-1} z$，

$$
u=g\left(g_{1}^{-1} z\right)=\left(g g_{1}^{-1}\right) z=\left(g g_{1}^{-1}\right)\left(g_{2} y\right)=\left(g g_{1}^{-1} g_{2}\right) y
$$

这表明 $u \in \operatorname{Orb}_{y}$。因此 $\operatorname{Orb}_{x} \subset \operatorname{Orb}_{y}$。
$X$ 的每个元素都在某个轨道中（它自己的轨道），所以轨道将 $X$ 划分为互不相交的子集。
b) 为了看出 $\operatorname{Stab}_{x}$ 是 $G$ 的子群，我们有 $e \in \operatorname{Stab}_{x}$，因为 $e x=x$，并且如果 $g_{1}, g_{2} \in \operatorname{Stab}_{x}$，那么

$$
\left(g_{1} g_{2}\right) x=g_{1}\left(g_{2} x\right)=g_{1} x=x
$$

所以 $g_{1} g_{2} \in \operatorname{Stab}_{x}$。因此 $\operatorname{Stab}_{x}$ 对乘法封闭。最后，

$$
g x=x \Longrightarrow g^{-1}(g x)=g^{-1} x \Longrightarrow x=g^{-1} x,
$$

所以 $\operatorname{Stab}_{x}$ 对取逆封闭。
为了证明对所有 $x \in X$ 和 $g \in G$，有 $\operatorname{Stab}_{g x}=g \operatorname{Stab}_{x} g^{-1}$，注意

$$
\begin{aligned}
h \in \operatorname{Stab}_{g x} & \Longleftrightarrow h \cdot(g x)=g x \\
& \Longleftrightarrow(h g) x=g x \\
& \Longleftrightarrow g^{-1}((h g) x)=g^{-1}(g x) \\
& \Longleftrightarrow\left(g^{-1} h g\right) x=x \\
& \Longleftrightarrow g^{-1} h g \in \operatorname{Stab}_{x} \\
& \Longleftrightarrow h \in g \operatorname{Stab}_{x} g^{-1}
\end{aligned}
$$

所以 $\operatorname{Stab}_{g x}=g \operatorname{Stab}_{x} g^{-1}$。
c) 条件 $g x=g^{\prime} x$ 等价于 $x=\left(g^{-1} g^{\prime}\right) x$，这意味着 $g^{-1} g^{\prime} \in \operatorname{Stab}_{x}$，或 $g^{\prime} \in g \operatorname{Stab}_{x}$。因此，$g$ 和 $g^{\prime}$ 对 $x$ 有相同效果当且仅当 $g$ 和 $g^{\prime}$ 位于 $\mathrm{Stab}_{x}$ 的同一个左陪集中。（回忆一下，对于 $G$ 的所有子群 $H$，$g^{\prime} \in g H$ 当且仅当 $g^{\prime} H=g H$。）

由于 $\operatorname{Orb}_{x}$ 由变化 $g$ 得到的点 $g x$ 组成，并且我们证明了 $G$ 的元素对 $x$ 有相同效果当且仅当它们位于 $\mathrm{Stab}_{x}$ 的同一个左陪集中，我们通过 $g x \mapsto g \operatorname{Stab}_{x}$ 得到了轨道中点和 $\operatorname{Stab}_{x}$ 的左陪集之间的一个双射。（仔细想想为什么这是良定义的。）因此，$x$ 的轨道的基数 $\left|\operatorname{Orb}_{x}\right|$ 等于 $G$ 中 $\operatorname{Stab}_{x}$ 的左陪集的基数。

例 3.17. 对于有限群 $G$ 中的 $a$，其共轭类有多大？共轭类是 $G$ 在自身上通过共轭作用下 $a$ 的轨道，所以 (3.1) 说共轭类的大小是指数 $\left[G: \operatorname{Stab}_{a}\right]$，其中

$$
\operatorname{Stab}_{a}=\left\{g \in G: g a g^{-1}=a\right\}=\{g \in G: g a=a g\} .
$$

这个子群是与 $a$ 交换的元素，称为 $a$ 的**中心化子**，记作 $Z(a)$。（注意 $Z(a)$ 不是中心 $Z(G)$，中心是与所有 $G$ 交换的元素。）由于 $[G: Z(a)]=|G| /|Z(a)|$ 整除 $|G|$，每个共轭类的大小整除 $|G|$。

例如，$S_{3}$ 的共轭类是 $\{(1)\},\{(123),(132)\}$，和 $\{(12),(13),(23)\}$，它们的大小 1,2，和 3 都是 6 的因子。$S_{4}$ 的共轭类由 (1), (1234), (12)(34), (123), 和 (12) 代表，它们的共轭类大小分别是 1,6 , 3,8 , 和 6。所有这些都是 24 的因子。

例 3.18. 对于 $n \geq 2$ 和 $k \in\{1, \ldots, n-1\}$，群 $G=S_{n}$ 以通常的方式作用在 $\{1,2, \ldots, n\}$ 的 $k$-元子集上：$\sigma\left(\left\{i_{1}, \ldots, i_{k}\right\}\right)=\left\{\sigma\left(i_{1}\right), \ldots, \sigma\left(i_{k}\right)\right\}$。这个群作用只有一个轨道，因为 $\left\{i_{1}, \ldots, i_{k}\right\}=\sigma(\{1, \ldots, k\})$，其中 $\sigma$ 是置换 $\left(\begin{array}{ccc}1 & 2 \cdots k \\ i_{1} i_{2} \cdots i_{k}\end{array}\right)$。

$\{1, \ldots, n\}$ 的 $k$-元子集的数量是 $\binom{n}{k}$，根据二项式系数的组合定义，所以定理 3.16(c) 意味着 $\binom{n}{k}=\left[S_{n}: \operatorname{Stab}_{\{1, \ldots, k\}}\right]$。$\{1, \ldots, k\}$ 的稳定化子是什么？它是所有满足 $\{\sigma(1), \ldots, \sigma(k)\}=\{1, \ldots, k\}$（集合相等，而不是有序集合或 $k$-元组）的 $\sigma \in S_{n}$，这等价于说 $\sigma$ 置换 $\{1, \ldots, k\}$ 从而也置换 $\{k+1, \ldots, n\}$。因此 $\operatorname{Stab}_{\{1, \ldots, k\}} \cong S_{k} \times S_{n-k}$，所以

$$
\binom{n}{k}=\left[S_{n}: \operatorname{Stab}_{\{1, \ldots, k\}}\right]=\frac{n!}{k!(n-k)!}
$$

这是使用群作用推导 $\binom{n}{k}$ 标准公式的一种方法。
例 3.19. 群作用的轨道不相交，这包括了群论中两个基本的不相交性结果：子群的左陪集（相应地，右陪集）和群的共轭类是不相交的。子群的左陪集（相应地，右陪集）是该子群通过右逆乘（相应地，通过左乘）作用在群上的轨道：见例 2.10, 3.13, 和 3.14。群的共轭类是群通过共轭作用在自身上的轨道（见例 2.11 和 3.10）。

例 3.20. $S_{n}$ 中每个置换 $\sigma$ 有一个不相交轮换分解，这是一个群作用在集合上具有不相交轨道的特例，其中群是 $\langle\sigma\rangle$，集合是 $\{1, \ldots, n\}$。最好先通过一个例子来理解不相交轮换。

令 $S_{9}$ 中的 $\sigma=\binom{123456789}{518324967}$ 且 $X=\{1,2,3,4,5,6,7,8,9\}$。你将 $\sigma$ 分解为不相交轮换的方法是：在 $X$ 中选取一个 $x$，从 $x$ 开始重复应用 $\sigma$ 直到回到 $x$，然后如果 $X$ 的某些部分还未被到达，则在 $X$ 中选取一个新的 $y$，从 $y$ 开始重复应用 $\sigma$ 直到回到 $y$，如此继续直到 $X$ 的所有部分都被到达：

- $\sigma$ 的迭代将 1 发送到 5,2，和 $1\left(\sigma(1)=5, \sigma^{2}(1)=\sigma(5)=2, \sigma^{3}(1)=\sigma(2)=1\right)$，
- 3 不在 $\{1,5,2\}$ 中，它被 $\sigma$ 的迭代按顺序发送到 $8,6,4$，和 3，
- 7 不在 $\{1,5,2\}$ 或 $\{3,8,6,4\}$ 中，它被 $\sigma$ 的迭代发送到 9 和 7。

所有 $X$ 都已被到达，所以 $\langle\sigma\rangle$-轨道是 $\{1,5,2\},\{3,8,6,4\}$，和 $\{7,9\}$ 且 $\sigma$ 有不相交轮换分解 (152)(3864)(79)。为什么 $\langle\sigma\rangle$-轨道是 $\sigma$ 的不相交轮换？

使用定理 3.16(c)，让我们解释为什么包含数字 $x$ 的 $\langle\sigma\rangle$-轨道是通过重复对 $x$ 应用 $\sigma$ 直到首次回到 $x$ 且没有先前的重复来创建的。令 $S_{n}$ 中 $\sigma$ 的阶为 $m$，令 $\operatorname{Stab}_{x}$ 的阶为 $d$。那么 $d \mid m$，因为 $\operatorname{Stab}_{x}$ 是 $\langle\sigma\rangle$ 的一个子群，且 $\left|\operatorname{Orb}_{x}\right|=|\langle\sigma\rangle| /\left|\operatorname{Stab}_{x}\right|=m / d$。由于 $\sigma^{m / d}$ 的阶为 $d$，并且像 $\langle\sigma\rangle$ 这样的循环群每个大小有一个子群，所以 $\operatorname{Stab}_{x}=\left\langle\sigma^{m / d}\right\rangle$。$\operatorname{Orb}_{x}$ 的元素与 $\langle\sigma\rangle$ 中 $\operatorname{Stab}_{x}$ 的左陪集一一对应，也就是 $\langle\sigma\rangle$ 中 $\left\langle\sigma^{m / d}\right\rangle$ 的左陪集。作为左陪集代表，我们可以使用 $0 \leq r<m / d$ 的 $\sigma^{r}$，所以 $\operatorname{Orb}_{x}=\left\{\sigma^{r}(x): 0 \leq r<m / d\right\}$ 且没有重复，而下一个数字 $\sigma^{m / d}(x)$ 就是 $x$，因为 $\sigma^{m / d} \in \operatorname{Stab}_{x}$。

推论 3.21. 设有限群 $G$ 作用于集合 $X$。
a) $X$ 中每个轨道的长度整除 $G$ 的大小。
b) 在同一轨道中的点有共轭的稳定化子，特别地，轨道中所有点的稳定化子大小相同。

证明. a) 对 $x \in X$，$x$ 的轨道长度是 $\left[G: \operatorname{Stab}_{x}\right]$，它整除 $|G|$。
b) 如果 $x$ 和 $y$ 在同一轨道中，记 $y=g x$。那么 $\operatorname{Stab}_{y}=\operatorname{Stab}_{g x}=g \operatorname{Stab}_{x} g^{-1}$，所以 $x$ 和 $y$ 的稳定化子是共轭子群。

例 3.22. 在有限群 $G$ 中，每个共轭类的大小整除 $|G|$，因为共轭类是 $G$ 作用在自身上的轨道。我们在例 3.17 中看到了这一点。

部分 (b) 的逆一般不成立：具有共轭稳定化子的点不一定在同一轨道中。甚至具有相同稳定化子的点也不一定在同一轨道中。例如，如果 $G$ 平凡地作用在自身上，那么所有点的稳定化子都是 $G$，所有轨道的大小都是 1。对于一个更有趣的例子，令 $A_{4}$ 通过共轭作用在自身上。那么 (123) 和 (132) 在不同的轨道中（它们在 $A_{4}$ 中不共轭），但它们的稳定化子都是 $\{(1),(123),(132)\}$。对于每个 3-轮换 $g \in A_{4}$，$g$ 和 $g^{-1}$ 也具有相同的特征。

推论 3.23. 设群 $G$ 作用于有限集合 $X$。令 $X$ 的不同轨道由 $x_{1}, \ldots, x_{t}$ 代表。那么

$$
\begin{equation*}
|X|=\sum_{i=1}^{t}\left|\operatorname{Orb}_{x_{i}}\right|=\sum_{i=1}^{t}\left[G: \operatorname{Stab}_{x_{i}}\right] \tag{3.2}
\end{equation*}
$$

证明. 集合 $X$ 可以写成其轨道的并集，这些轨道互不相交。轨道-稳定化子公式告诉我们每个轨道有多大。

例 3.24. $D_{6}$ 中哪些元素与反射 $s$ 交换？这要求的是 $\left\{g \in D_{6}: g s=s g\right\}$。三个这样的元素是 $1, s$，和 $r^{3}$（因为对于偶数 $n$，$r^{n / 2} \in Z\left(D_{n}\right)$）。

让我们将条件 $g s=s g$ 解释为 $g s g^{-1}=s$：现在的任务是计算当 $D_{6}$ 通过共轭作用在自身上时，$s$ 的稳定化子。为了计算稳定化子，让我们先计算轨道：当 $g$ 跑遍 $D_{6}$ 时，$g s g^{-1}$ 有多少不同的值？$D_{6}$ 的元素是 $r^{k}$（旋转）和 $r^{k} s$（反射，所以等于其逆）。由

$$
r^{k} s r^{-k}=r^{2 k} s, \quad\left(r^{k} s\right) s\left(r^{k} s\right)^{-1}=r^{k} s s r^{k} s=r^{k} r^{k} s=r^{2 k} s
$$

随着 $g$ 在 $D_{6}$ 中变化，不同的 $g s g^{-1}$ 是 $\left\{r^{\text {even }} s\right\}=\left\{s, r^{2} s, r^{4} s\right\}$。
由于 $s$ 的 $D_{6}$-轨道大小为 3，$s$ 的稳定化子在 $D_{6}$ 中的指数为 3，因此其大小是 $\left|D_{6}\right| / 3=12 / 3=4$。我们已经知道 $1, s$，和 $r^{3}$ 在稳定化子中，所以作为一个群，意味着 $r^{3} s$ 也在稳定化子中。那是第四个元素，并且稳定化子大小为 4，所以 $\left\{g \in D_{6}: g s=s g\right\}=\left\{1, s, r^{3}, r^{3} s\right\}$。

例 3.25. 我们现在检查一个几何例子。下图中的图形 $F$ 是一个六边形，里面画了一个 X。当 $D_{6}$ 以自然的方式作用在它上面时，$D_{6}$ 的哪些元素保持这个图形不变？
![](https://cdn.mathpix.com/cropped/0a27da81-90ab-414a-b918-984f98c130c0-15.jpg?height=272&width=355&top_left_y=1995&top_left_x=941)

对 $g \in D_{6}$，$g(F)=F$ 意味着 $g \in \operatorname{Stab}_{F}$。为了计算 $\operatorname{Stab}_{F}$，我们首先计算 $F$ 的轨道：弄清楚 $F$ 可以如何变化比弄清楚 $F$ 如何保持不变更容易，并且这些通过轨道-稳定化子公式相关联。通过旋转和反射，很明显，当 $g$ 跑遍 $D_{6}$ 时，$g(F)$ 只有以下 3 个结果。
![](https://cdn.mathpix.com/cropped/0a27da81-90ab-414a-b918-984f98c130c0-16.jpg?height=278&width=364&top_left_y=356&top_left_x=489)
![](https://cdn.mathpix.com/cropped/0a27da81-90ab-414a-b918-984f98c130c0-16.jpg?height=272&width=360&top_left_y=360&top_left_x=936)
![](https://cdn.mathpix.com/cropped/0a27da81-90ab-414a-b918-984f98c130c0-16.jpg?height=272&width=364&top_left_y=360&top_left_x=1379)

令 $r$ 为保持六边形形状的 60 度逆时针旋转，令 $s$ 为关于平分 $F$ 的水平线的反射。由于 $F$ 有一个大小为 3 的轨道，它在 $D_{6}$ 中的稳定化子指数为 3，所以 $\left|\operatorname{Stab}_{F}\right|=\left|D_{6}\right| / 3=12 / 3=4$。由 $F$ 的 180 度旋转对称性，$r^{3} \in \operatorname{Stab}_{F}$。由于 $s(F)=F$，$s \in \operatorname{Stab}_{F}$。由于 $\operatorname{Stab}_{F}$ 是 $D_{6}$ 的子群，$\operatorname{Stab}_{F}$ 也包含 $r^{3} s$。因此 $\left\{1, r^{3}, s, r^{3} s\right\} \subset \operatorname{Stab}_{F}$，并且我们就完成了，因为我们知道 $\left|\operatorname{Stab}_{F}\right|=4$：$\operatorname{Stab}_{F}=\left\{1, r^{3}, s, r^{3} s\right\}=\left\langle r^{3}, s\right\rangle$。

虽然 $F^{\prime}$ 看起来像 $F$，但它不等于 $F$。那么 $\operatorname{Stab}_{F^{\prime}}$ 和 $\left\{g \in D_{6}: g(F)=F^{\prime}\right\}$ 是什么？一旦我们知道一个将 $F$ 发送到 $F^{\prime}$ 的 $g$，我们就可以确定这些。由于 $F^{\prime}=r(F)$，我们可以取 $g=r$。那么定理 3.16(b) 说

$$
\operatorname{Stab}_{F^{\prime}}=\operatorname{Stab}_{r(F)}=r \operatorname{Stab}_{F} r^{-1}=r\left\{1, r^{3}, s, r^{3} s\right\} r^{-1}=\left\{1, r^{3}, r^{2} s, r^{5} s\right\}
$$

且定理 3.16(c) 说

$$
\left\{g \in D_{6}: g(F)=F^{\prime}\right\}=r \operatorname{Stab}_{F}=r\left\{1, r^{3}, s, r^{3} s\right\}=\left\{r, r^{4}, r s, r^{4} s\right\} .
$$

类似地，由于 $F^{\prime \prime}=r^{-1}\left(F^{\prime \prime}\right)$，

$$
\operatorname{Stab}_{F^{\prime \prime}}=\operatorname{Stab}_{r^{-1}(F)}=r^{-1} \operatorname{Stab}_{F}\left(r^{-1}\right)^{-1}=r^{-1}\left\{1, r^{3}, s, r^{3} s\right\} r=\left\{1, r^{3}, r^{4} s, r s\right\}
$$

且

$$
\left\{g \in D_{6}: g(F)=F^{\prime \prime}\right\}=r^{-1} \operatorname{Stab}_{F}=r^{-1}\left\{1, r^{3}, s, r^{3} s\right\}=\left\{r^{5}, r^{2}, r^{5} s, r^{2} s\right\} .
$$

例 3.26. 那些列和等于 1 的 $2 \times 2$ 矩阵 $\left(\begin{array}{cc}a & b \\ c & d\end{array}\right) \in \mathrm{GL}_{2}(\mathbf{R})$ 构成一个子群 $H$。这可以通过繁琐的计算来检查。也可以通过观察列和是向量-矩阵乘积 $\left(\begin{array}{ll}1 & 1\end{array}\right)\left(\begin{array}{ll}a & b \\ c & d\end{array}\right)$ 中的元素来看出，所以 $H$ 中的矩阵是那些满足 $\left(\begin{array}{ll}1 & 1\end{array}\right)\left(\begin{array}{ll}a & b \\ c & d\end{array}\right)=\left(\begin{array}{ll}1 & 1\end{array}\right)$ 的矩阵。因此 $H$ 是 $\left(\begin{array}{ll}1 & 1\end{array}\right)$ 在 $\mathrm{GL}_{2}(\mathbf{R})$ 在 $\mathbf{R}^{2}$ 上（视为行向量）的（右！）作用中的稳定化子，其中 $\mathbf{v} \cdot A=\mathbf{v} A$。因此 $H$ 是 $\mathrm{GL}_{2}(\mathbf{R})$ 的一个子群，因为点的稳定化子总是一个子群。（读者应制定并验证定理 3.16 对右群作用的版本。）

此外，因为 $\left.\left(\begin{array}{ll}0 & 1\end{array}\right)\left(\begin{array}{cc}0 & -1 \\ 1 & 1\end{array}\right)=\left(\begin{array}{ll}1 & 1\end{array}\right), \operatorname{Stab}_{(1}^{1} 1\right)$ 和 $\operatorname{Stab}_{(0} 1$ ) 是 $\mathrm{GL}_{2}(\mathbf{R})$ 中的共轭子群。由于 $\operatorname{Stab}_{(01)}=\left\{\left(\begin{array}{cc}a & b \\ 0 & 1\end{array}\right) \in \mathrm{GL}_{2}(\mathbf{R})\right\}=\operatorname{Aff}(\mathbf{R})$，我们有

$$
H=\operatorname{Stab}_{\left(\begin{array}{ll}
1 & 1
\end{array}\right)}=\operatorname{Stab}_{\left(\begin{array}{ll}
0 & 1
\end{array}\right)\left(\begin{array}{cc}
0 & -1 \\
1 & 1
\end{array}\right)}=\left(\begin{array}{rr}
0 & -1 \\
1 & 1
\end{array}\right)^{-1} \operatorname{Aff}(\mathbf{R})\left(\begin{array}{rr}
0 & -1 \\
1 & 1
\end{array}\right) .
$$

例 3.27. 作为轨道-稳定化子公式的一个巧妙应用，我们解释为什么对于有限群 $G$ 的子群 $H$ 和 $K$，有 $|H K|= |H||K| /|H \cap K|$。这里 $H K=\{h k: h \in H, k \in K\}$ 是乘积的集合，通常只是 $G$ 的一个子集（不是子群）。为了计数 $H K$ 的大小，令直积群 $H \times K$ 像这样作用在 $G$ 上：$(h, k) \cdot g=h g k^{-1}$。检查这给出了一个群作用（群是 $H \times K$，集合是 $G$）且 $H K$ 是 $e$ 的轨道。因此轨道-稳定化子公式告诉我们

$$
|H K|=\frac{|H \times K|}{\left|\operatorname{Stab}_{e}\right|}=\frac{|H||K|}{|\{(h, k):(h, k) \cdot e=e\}|} .
$$

条件 $(h, k) \cdot e=e$ 意味着 $h k^{-1}=e$，因此 $\operatorname{stab}_{e}=\{(h, h): h \in H \cap K\}$。所以 $\left|\operatorname{Stab}_{e}\right|=|H \cap K|$ 且 $|H K|=|H||K| /|H \cap K|$。

例 3.28. 我们现在讨论群论中拉格朗日定理的原始形式。他证明了对于每个 $n$ 变量多项式 $f\left(T_{1}, \ldots, T_{n}\right)$，我们通过置换其变量从 $f\left(T_{1}, \ldots, T_{n}\right)$ 得到的不同多项式的数量是 $n!$ 的一个因子。

例如，考虑多项式 $T_{1}$ 和 $n=3$。如果我们遍历 $\left\{T_{1}, T_{2}, T_{3}\right\}$ 的所有六个置换，并将每个应用于 $T_{1}$，我们得到 3 个不同的结果：$T_{1}, T_{2}$，和 $T_{3}$。多项式 $T_{1} T_{2}^{2}+T_{2} T_{3}^{2}+T_{3} T_{1}^{2}$ 在每次变量变换下只有 2 种可能性：它本身和 $T_{2} T_{1}^{2}+T_{1} T_{3}^{2}+T_{3} T_{2}^{2}$（检查这个）。多项式 $T_{1}+T_{2}^{2}+T_{3}^{3}$ 有 6 种不同的可能性。在每种情况下，不同多项式的数量都是 $3!$ 的因子。

为了解释拉格朗日的一般观察，我们将轨道-稳定化子公式应用于例 2.7 中的群作用。那是 $S_{n}$ 通过变量置换在 $n$ 变量多项式上的作用。对于一个 $n$ 变量多项式 $f\left(T_{1}, \ldots, T_{n}\right)$，我们通过置换其变量得到的不同多项式正是其 $S_{n}$-轨道中的多项式。由轨道-稳定化子公式，我们通过置换 $f\left(T_{1}, \ldots, T_{n}\right)$ 的变量得到的不同多项式的数量是 $\left[S_{n}: H_{f}\right]$，其中 $H_{f}=\operatorname{Stab}_{f}=\left\{\sigma \in S_{n}: \sigma \cdot f=f\right\}$，并且这个指数整除 $n!$。柯西在 1815 年引入了术语“指数”来表示我们通过置换单个多项式的变量得到的不同多项式的数量，而将其解释为 $\left[S_{n}: H_{f}\right]$ 就是为什么我们在群论中使用术语指数来表示 $[G: H]$。

在群作用中，轨道的长度整除 $|G|$，但轨道的数量通常不整除 $|G|$。例如，$D_{4}$ 和 $Q_{8}$ 各有 5 个共轭类，而 5 不整除 8。但是轨道的数量与群作用之间有一个有趣的关系。

定理 3.29. 设有限群 $G$ 作用于有限集合 $X$，有 $r$ 个轨道。那么 $r$ 是群元素不动点数量的平均值：

$$
r=\frac{1}{|G|} \sum_{g \in G}\left|\operatorname{Fix}_{g}(X)\right|
$$

其中 $\operatorname{Fix}_{g}(X)=\{x \in X: g x=x\}$ 是被 $g$ 固定的 $X$ 的元素集合。
不要混淆集合 $\operatorname{Fix}_{g}(X)$ 与作用的不动点：$\operatorname{Fix}_{g}(X)$ 只是被元素 $g$ 固定的点。$G$ 的作用的不动点的集合是 $\operatorname{Fix}_{g}(X)$ 在 $g$ 跑遍群时的交集。

证明. 我们将用两种方式计数 $\{(g, x) \in G \times X: g x=x\}$。
通过先对 $g$ 计数，我们必须将满足 $g x=x$ 的 $x$ 的数量相加，所以

$$
|\{(g, x) \in G \times X: g x=x\}|=\sum_{g \in G}\left|\operatorname{Fix}_{g}(X)\right| .
$$

接下来我们对 $x$ 计数，必须将满足 $g x=x$ 的 $g$ 的数量相加，即满足 $g \in \operatorname{Stab}_{x}$ 的 $g$：

$$
|\{(g, x) \in G \times X: g x=x\}|=\sum_{x \in X}\left|\operatorname{Stab}_{x}\right| .
$$

使这两个计数相等得

$$
\sum_{g \in G}\left|\operatorname{Fix}_{g}(X)\right|=\sum_{x \in X}\left|\operatorname{Stab}_{x}\right| .
$$

由轨道-稳定化子公式，$|G| /\left|\operatorname{Stab}_{x}\right|=\left|\operatorname{Orb}_{x}\right|$，所以

$$
\sum_{g \in G}\left|\operatorname{Fix}_{g}(X)\right|=\sum_{x \in X} \frac{|G|}{\left|\operatorname{Orb}_{x}\right|} .
$$

除以 $|G|$：

$$
\frac{1}{|G|} \sum_{g \in G}\left|\operatorname{Fix}_{g}(X)\right|=\sum_{x \in X} \frac{1}{\left|\operatorname{Orb}_{x}\right|}
$$

让我们考虑来自单个轨道中的点的右侧贡献。如果一个轨道有 $n$ 个点，那么该轨道上的点的和是 $n$ 项 $1 / n$ 的和，等于 1。因此，一个轨道上的点的部分和是 1，这使得右边的和等于轨道的数量，即 $r$。

定理 3.29 通常被称为伯恩赛德引理，但它并非源于他 [7]。他将这个结果包含在他的群论书中，并归功于弗罗贝尼乌斯 $[1, § 118]$。

例 3.30. 我们将使用定理 3.29 的一个特例来证明：对所有 $a \in \mathbf{Z}$ 和 $m \in \mathbf{Z}^{+}$，

$$
\begin{equation*}
\sum_{k=1}^{m} a^{(k, m)} \equiv 0 \bmod m \tag{3.3}
\end{equation*}
$$

当 $m=p$ 是素数时，左边是 $(p-1) a+a^{p}=\left(a^{p}-a\right)+p a$，所以 (3.3) 变成 $a^{p} \equiv a \bmod p$，这就是费马小定理。因此 (3.3) 可以被视为费马小定理对所有模的推广，本质上不同于称为欧拉定理的推广，欧拉定理说如果 $(a, m)=1$，则 $a^{\varphi(m)} \equiv 1 \bmod m$：(3.3) 对所有 $a \in \mathbf{Z}$ 成立。

我们导致 (3.3) 的设置始于一个有限群 $G$，源自 [5]。对于一个正整数 $a$，$G$ 通过 $(g \cdot f)(h)=f\left(g^{-1} h\right)$ 对 $g, h \in G$ 作用在函数集合 $\operatorname{Map}(G,\{1,2, \ldots, a\})$ 上。这是例 2.9 末尾群作用的一个特例，其中 $G$ 通过左乘作用在自身上。我们想将定理 3.29 应用于这个作用，所以我们需要理解每个 $g \in G$ 的不动点（实际上是不动函数）。我们有 $g \cdot f=f$ 当且仅当对所有 $h \in G$ 有 $f\left(g^{-1} h\right)=f(h)$，这等价于说 $f$ 在 $G$ 中的每个左陪集 $\langle g\rangle h$ 上是常数。$\langle g\rangle$ 在 $G$ 中的左陪集数量是 $[G:\langle g\rangle]=m / \operatorname{ord}(g)$，其中 $m=|G|$ 且 $\operatorname{ord}(g)$ 是 $g$ 的阶，所以被 $g$ 固定的函数的数量是 $a^{m / \operatorname{ord}(g)}$，因为函数在每个陪集上的值可以在 $\{1, \ldots, a\}$ 中任意选择。因此定理 3.29 意味着 $(1 / m) \sum_{g \in G} a^{m / \operatorname{ord}(g)}$ 是一个正整数，所以

$$
\begin{equation*}
\sum_{g \in G} a^{m / \operatorname{ord}(g)} \equiv 0 \bmod m \tag{3.4}
\end{equation*}
$$

由于 (3.4) 仅通过 $a \bmod m$ 的值依赖于 $a$，它对所有 $a \in \mathbf{Z}$ 成立，不仅仅是 $a>0$。
取 $G=\mathbf{Z} /(m)$，每个 $k \in G$ 的加性阶是 $m /(k, m)$，所以 (3.4) 变成

$$
\sum_{k=1}^{m} a^{(k, m)} \equiv 0 \bmod m
$$

接下来我们转向一个群的两种不同作用本质相同的思想。
定义 3.31. 如果存在一个双射 $f: X \rightarrow Y$，使得对所有 $g \in G$ 和 $x \in X$ 有 $f(g x)=g(f(x))$，则称群 $G$ 在集合 $X$ 和 $Y$ 上的两个作用是**等价的**。

当 $G$ 在适当匹配两个集合后以相同的方式置换两个集合中的元素时，$G$ 在两个集合上的作用是等价的。当 $f: X \rightarrow Y$ 是群作用在 $X$ 和 $Y$ 上的一个等价时，$g x=x$ 当且仅当 $g(f(x))=f(x)$，所以 $x \in X$ 和 $f(x) \in Y$ 的稳定化子群是相同的。

例 3.32. 让 $\mathbf{R}^{\times}$ 通过缩放作用在线性子空间 $\mathbf{R} v_{0} \subset \mathbf{R}^{n}$ 上。这等价于 $\mathbf{R}^{\times}$ 在 $\mathbf{R}$ 上通过缩放的自然作用：令 $f: \mathbf{R} \rightarrow \mathbf{R} v_{0}$ 为 $f(a)=a v_{0}$。那么 $f$ 是一个双射，且对所有 $\mathbf{R}^{\times}$ 中的 $c$ 和 $a \in \mathbf{R}$，有 $f(c a)=(c a) v_{0}=c\left(a v_{0}\right)=c f(a)$。

例 3.33. 令 $\mathrm{GL}_{2}(\mathbf{R})$ 以自然的方式作用在 $\mathbf{R}^{2}$ 的有序基集合 $\mathcal{B}$ 上：对 $A \in \mathrm{GL}_{2}(\mathbf{R})$，$A\left(e_{1}, e_{2}\right):=\left(A e_{1}, A e_{2}\right)$ 是 $\mathbf{R}^{2}$ 的另一个有序基。$\mathrm{GL}_{2}(\mathbf{R})$ 在 $\mathcal{B}$ 上的这个作用等价于 $\mathrm{GL}_{2}(\mathbf{R})$ 通过左乘作用在自身上。原因是，$\mathrm{GL}_{2}(\mathbf{R})$ 中矩阵的列是 $\mathbf{R}^{2}$ 的一组基（第一列和第二列是基向量的一个排序：第一列是第一个基向量，第二列是第二个基向量），并且两个方矩阵通过列的乘法相乘：$A\left(\begin{array}{ll}a & b \\ c & d\end{array}\right)=\left(A\binom{a}{c} A\binom{b}{d}\right)$。令 $f: \mathcal{B} \rightarrow \mathrm{GL}_{2}(\mathbf{R})$ 为 $f\left(\binom{a}{c},\binom{b}{d}\right)=\left(\begin{array}{ll}a & b \\ c & d\end{array}\right)$ 给出一个双射，且对所有 $A \in \mathrm{GL}_{2}(\mathbf{R})$ 和 $\left(e_{1}, e_{2}\right) \in \mathcal{B}$，有 $f\left(A\left(e_{1}, e_{2}\right)\right)=A \cdot f\left(e_{1}, e_{2}\right)$。

例 3.34. 令 $S_{3}$ 通过共轭作用在其共轭类 $\{(12),(13),(23)\}$ 上。这个在 3 元集合上的作用，如下表 1 上半部分所述，看起来像 $S_{3}$ 在 $\{1,2,3\}$ 上的通常作用（表 1 下半部分），如果我们将 (12) 等同于 3，(13) 等同于 2，(23) 等同于 1（简而言之，将 ( $i j$ ) 等同于 $k$，其中 $k \notin\{i, j\}$）。那么 $S_{3}$ 通过共轭在 $\{(12),(13),(23)\}$ 上的作用等价于 $S_{3}$ 在 $\{1,2,3\}$ 上的自然作用。

| $\pi$ | $\pi(12) \pi^{-1}$ | $\pi(13) \pi^{-1}$ | $\pi(23) \pi^{-1}$ | $\pi(3)$ | $\pi(2)$ | $\pi(1)$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $(1)$ | $(12)$ | $(13)$ | $(23)$ | 3 | 2 | 1 |
| $(12)$ | $(12)$ | $(23)$ | $(13)$ | 3 | 1 | 2 |
| $(13)$ | $(23)$ | $(13)$ | $(12)$ | 1 | 2 | 3 |
| $(23)$ | $(13)$ | $(12)$ | $(23)$ | 2 | 3 | 1 |
| $(123)$ | $(23)$ | $(12)$ | $(13)$ | 1 | 3 | 2 |
| $(132)$ | $(13)$ | $(23)$ | $(12)$ | 2 | 1 | 3 |

表 1。

例 3.35. 令 $H$ 和 $K$ 是 $G$ 的子群。群 $G$ 通过左乘作用在 $G / H$ 和 $G / K$ 上。如果 $H$ 和 $K$ 是共轭子群，那么这些作用是等价的：固定某个 $g_{0} \in G$ 给出的表示 $K=g_{0} H g_{0}^{-1}$，并令 $f: G / H \rightarrow G / K$ 为 $f(g H)=g g_{0}^{-1} K$。这是良定义的（与 $g H$ 的陪集代表无关），因为对于 $h \in H$，

$$
f(g h H)=g h g_{0}^{-1} K=g h g_{0}^{-1} g_{0} H g_{0}^{-1}=g H g_{0}^{-1}=g g_{0}^{-1} K .
$$

读者可以检查对所有 $G$ 中的 $g$ 和 $G / H$ 中的 $g^{\prime} H$，有 $f\left(g\left(g^{\prime} H\right)\right)=g f\left(g^{\prime} H\right)$，且 $f$ 是一个双射。（映射 $f$ 可能依赖于 $g_{0}$，但这没有问题。在两个等价的群作用之间可能存在多个等价，就像在两个同构的群之间可能存在多个同构一样。）

如果 $H$ 和 $K$ 不共轭，那么 $G$ 在 $G / H$ 和 $G / K$ 上的作用不等价：等价作用中的对应点有相同的稳定化子群，但 $G / H$ 中左陪集的稳定化子群共轭于 $H$，而 $G / K$ 中的共轭于 $K$，并且前者和后者没有相等的。

$G$ 在左陪集空间 $G / H$ 上的左乘作用有一个轨道。事实证明，所有具有一个轨道的作用本质上都是这种形式：

定理 3.36. 具有一个轨道的 $G$ 的作用等价于 $G$ 在某个左陪集空间上的左乘作用。
​	
证明. 假设 $G$ 作用在集合 $X$ 上，有一个轨道。固定 $x_{0} \in X$ 并令 $H=\operatorname{Stab}_{x_{0}}$。我们将证明 $G$ 在 $X$ 上的作用等价于 $G$ 在 $G / H$ 上的左乘作用。

每个 $x \in X$ 具有形式 $g x_{0}$，其中 $g \in G$，并且左陪集 $g H$ 中的所有元素对 $x_{0}$ 有相同的效果：对所有 $h \in H$，$(g h)\left(x_{0}\right)=g\left(h x_{0}\right)=g\left(x_{0}\right)$。令 $f: G / H \rightarrow X$ 为 $f(g H)=g x_{0}$。正如我们刚才看到的，这是良定义的。此外，$f\left(g \cdot g^{\prime} H\right)=g f\left(g^{\prime} H\right)$，因为两边都等于 $g g^{\prime}\left(x_{0}\right)$。我们将证明 $f$ 是一个双射。

由于 $X$ 有一个轨道，$X=\left\{g x_{0}: g \in G\right\}=\{f(g H): g \in G\}$，所以 $f$ 是满射。如果 $f\left(g_{1} H\right)=f\left(g_{2} H\right)$，那么 $g_{1} x_{0}=g_{2} x_{0}$，所以 $g_{2}^{-1} g_{1} x_{0}=x_{0}$。由于 $x_{0}$ 的稳定化子是 $H$，有 $g_{2}^{-1} g_{1} \in H$，所以 $g_{1} H=g_{2} H$。因此 $f$ 是单射。

定理 3.36 的一个特殊情况说，$G$ 的一个作用等价于 $G$ 在自身上的左乘作用当且仅当该作用有一个轨道且稳定化子群是平凡的。

定义 3.37. 当每个点都有平凡稳定化子时，称 $G$ 在 $X$ 上的作用是**自由的**。

例 3.38. 一个群在自身上的左乘作用（例 3.9）是自由的，有一个轨道。

例 3.39. $\mathbf{Z} /(2)$ 在球面上的对径作用（例 3.4）是一个自由作用。有不可数多个轨道。

自由作用经常出现在拓扑学中。例 3.39 是这种情况的一个典型例子。
例 3.40. 对于一个整数 $n \geq 2$，令 $X_{n}$ 为 $\mathbf{C}^{\times}$ 中 $n$ 次单位根的集合，所以 $^{3}\left|X_{n}\right|=\varphi(n)$。（例如，$X_{4}=\{i,-i\}$。）群 $(\mathbf{Z} /(n))^{\times}$ 通过 $a \cdot \zeta=\zeta^{a}$ 作用在 $X_{n}$ 上。（这是良定义的，因为 $a \equiv b \bmod n \Rightarrow \zeta^{a}=\zeta^{b}$。）由于 $X_{n}$ 的每个元素都是 $X_{n}$ 中其他元素的幂，指数与 $n$ 互素，$(\mathbf{Z} /(n))^{\times}$ 的这个作用有一个轨道。由于 $\zeta^{a}=\zeta$ 仅当 $a \equiv 1 \bmod n$（$\zeta$ 的阶为 $n$），所有稳定化子都是平凡的（自由作用）。因此，$(\mathbf{Z} /(n))^{\times}$ 作用在 $X_{n}$ 上等价于 $(\mathbf{Z} /(n))^{\times}$ 在自身上的乘法作用，只是 $X_{n}$ 中没有自然显著的元素（当 $\varphi(n)>1$，即 $n>2$ 时），而 1 是 $(\mathbf{Z} /(n))^{\times}$ 中的一个显著元素。

值得比较忠实作用和自由作用。一个作用是忠实的（定义 2.17）当 $G$ 中的 $g_{1} \neq g_{2}$ 意味着对某个 $x \in X$ 有 $g_{1} x \neq g_{2} x$（$G$ 的不同元素在 $X$ 的某点作用不同），而一个作用是自由的当 $G$ 中的 $g_{1} \neq g_{2}$ 意味着对所有 $x \in X$ 有 $g_{1} x \neq g_{2} x$（$G$ 的不同元素在 $X$ 的每点作用不同）。所以所有自由作用都是忠实的。由于 $g_{1} x=g_{2} x$ 当且仅当 $g_{2}^{-1} g_{1} x=x$，我们可以用不动点来描述忠实和自由作用：一个作用是忠实的当每个 $g \neq e$ 满足 $\operatorname{Fix}_{g}(X) \neq X$，而一个作用是自由的当每个 $g \neq e$ 满足 $\operatorname{Fix}_{g}(X)=\emptyset$。

[^2]
## 4. $p$-群的作用

具有素数幂大小的群的作用有特殊之处。当 $|G|=p^{k}$，其中 $p$ 是素数时，我们称 $G$ 为一个 $p$-群。例如，$(\mathbf{Z} /(5))^{\times}=\{1,2,3,4\}$ 和 $D_{4}$ 是 2-群。$p$-群的作用有特殊之处。因为 $p$-群的所有子群都有 $p$ 幂指数，在 $p$-群作用下，轨道的长度可被 $p$ 整除，除非该点是不动点，此时其轨道长度为 1。这导致了一个关于 $p$ 的重要同余式，用于 $p$-群的作用。

定理 4.1 (不动点同余式). 令 $G$ 为一个有限 $p$-群，作用于有限集合 $X$ 上。那么

$$
|X| \equiv \mid\{\text { 不动点 }\} \mid \bmod p
$$

证明. 令 $X$ 中的不同轨道由 $x_{1}, \ldots, x_{t}$ 代表，那么推论 3.23 导致

$$
\begin{equation*}
|X|=\sum_{i=1}^{t}\left|\operatorname{Orb}_{x_{i}}\right| \tag{4.1}
\end{equation*}
$$

由于 $\left|\operatorname{Orb}_{x_{i}}\right|=\left[G: \operatorname{Stab}_{x_{i}}\right]$ 且 $|G|$ 是 $p$ 的幂，除非 $\operatorname{Stab}_{x_{i}}=G$，否则 $\left|\operatorname{Orb}_{x_{i}}\right| \equiv 0 \bmod p$，而当 $\operatorname{Stab}_{x_{i}}=G$ 时，$\operatorname{Orb}_{x_{i}}$ 长度为 1，即 $x_{i}$ 是一个不动点。因此，当我们将 (4.1) 两边模 $p$ 约化时，右边的所有项都消失，除了每个不动点贡献 1。这意味着

$$
|X| \equiv \mid\{\text { 不动点 }\} \mid \bmod p .
$$

请记住，定理 4.1 中的同余式仅对具有素数幂大小的群的作用成立。当大小为 9 的群作用时，我们得到模 3 的同余式，但当大小为 6 的群作用时，我们得不到模 2 或 3 的同余式。

推论 4.2. 令 $G$ 为一个有限 $p$-群，作用于有限集合 $X$ 上。如果 $|X|$ 不能被 $p$ 整除，那么在 $X$ 中至少有一个不动点。如果 $|X|$ 能被 $p$ 整除，那么不动点的数量是 $p$ 的倍数（可能为 0）。

证明. 当 $|X|$ 不能被 $p$ 整除时，不动点的数量也不能（由不动点同余式），所以不动点的数量不能等于 0（毕竟，$p \mid 0$）因此是 $\geq 1$。另一方面，当 $|X|$ 能被 $p$ 整除时，不动点同余式表明不动点的数量 $\equiv 0 \bmod p$，所以这个数量是 $p$ 的倍数。

例 4.3. 令 $G$ 为 $\mathrm{GL}_{n}(\mathbf{Z} /(p))$ 的一个 $p$-子群，其中 $n \geq 1$。那么存在一个非零的 $v \in(\mathbf{Z} /(p))^{n}$，使得对所有 $g \in G$ 有 $g v=v$。确实，因为 $G$ 是一个矩阵群，它自然地作用在集合 $V=(\mathbf{Z} /(p))^{n}$ 上。（单位矩阵是恒等函数，并且由矩阵-向量乘法的规则有 $g_{1}\left(g_{2} v\right)=\left(g_{1} g_{2}\right) v$。）由于集合 $V$ 的大小为 $p^{n} \equiv 0 \bmod p$，不动点的数量可被 $p$ 整除。不动点的数量至少为 1，因为零向量是一个不动点，所以不动点的数量至少为 $p$。

一个矩阵群的**非零**不动点可以解释为具有特征值 1 的**同时特征向量**。这些是 $G$ 在 $(\mathbf{Z} /(p))^{n}$ 中唯一可能的同时特征向量，因为 $G$ 的每个元素都有 $p$-幂阶，并且 $(\mathbf{Z} /(p))^{\times}$ 中唯一的 $p$-幂阶元素是 1（所以 $G$ 在 $(\mathbf{Z} /(p))^{n}$ 中的同时特征向量对群中的每个元素必须有特征值 1）。

如果我们能够将一个问题的解释用不动点来表达，定理 4.1 可以用来（非构造性地）证明关于有限群的存在性定理。例如，群 $G$ 的一个元素在中心中恰好当它是 $G$ 在自身上通过共轭作用的一个不动点。所以如果我们想证明一类群有非平凡中心，我们可以尝试证明除了单位元之外，共轭作用还有不动点。

## 5. 使用群作用的新证明

在本节中，我们使用群作用（特别是定理 4.1）证明两个结果：有限 $p$-群有非平凡中心，以及如果 $p||G|$，那么 $G$ 有一个阶为 $p$ 的元素。

定理 5.1. 令 $G$ 为一个非平凡 $p$-群。那么 $G$ 的中心的大小可被 $p$ 整除。特别地，$G$ 有一个非平凡中心。

这个定理归功于西罗。$^{4}$
证明. $a$ 位于 $G$ 的中心的条件可以写成对所有 $g$ 有 $a=g a g^{-1}$，所以 $a$ 被所有共轭固定。证明的主要思想是考虑 $G$ 在自身上（$X=G$）通过共轭的作用并计数不动点。

我们照常记 $G$ 的中心为 $Z(G)$。由于 $G$ 是一个 $p$-群，并且这里 $X=G$，不动点同余式（定理 4.1）意味着 $|G| \equiv|Z(G)| \bmod p$。由于 $|G|$ 是 $p$ 的幂，我们得到 $0 \equiv|Z(G)| \bmod p$，所以 $p||Z(G)|$。因为 $| Z(G) \mid \geq 1$，由 $p||Z(G)|$ 得 $|Z(G)| \geq p$，所以 $Z(G) \neq\{e\}$。

推论 5.2. 对素数 $p$，每个阶为 $p^{2}$ 的群是阿贝尔群。
证明. 令 $|G|=p^{2}$。$G$ 的非平凡元素阶为 $p$ 或 $p^{2}$。如果 $G$ 有一个阶为 $p^{2}$ 的元素，那么 $G$ 是循环群，因此是阿贝尔群。所以假设 $G$ 的非平凡元素阶为 $p$。

由定理 5.1，存在 $x \neq e$ 在 $Z(G)$ 中，所以 $x$ 的阶为 $p$。令 $y \notin\langle x\rangle$。由于 $x \in Z(G)$，$x$ 和 $y$ 交换，所以所有幂 $x^{i}$ 和 $y^{j}$ 交换。因此 $\left\{x^{i} y^{j}: i, j \in \mathbf{Z}\right\}$ 是 $G$ 的一个阿贝尔子群。它比 $\langle x\rangle$ 大，因为它包含 $y$，所以它的阶是 $p^{2}$（阶整除 $p^{2}$ 且大于 $p$）。因此 $\left\{x^{i} y^{j}: i, j \in \mathbf{Z}\right\}=G$，所以 $G$ 是阿贝尔群。

用几乎不比定理 5.1 的证明多的工作，我们可以证明一个更强的结果。
定理 5.3. 对于每个非平凡 p-群 $G$，对所有非平凡正规子群 $N \triangleleft G$，有 $N \cap Z(G) \neq\{e\}$。也就是说，每个非平凡正规子群都与 $G$ 的中心非平凡相交。

证明. 像定理 5.1 的证明那样论证，但让 $G$ 通过共轭作用在 $N$ 上。由于 $N$ 是一个非平凡 $p$-群，不动点同余式（定理 4.1）意味着 $N \cap Z(G)$ 的大小可被 $p$ 整除。因此 $N \cap Z(G)$ 是非平凡的。

定理 5.4 (柯西). 令 $G$ 为一个有限群，$p$ 为 $|G|$ 的一个素因子。那么 $G$ 有一个阶为 $p$ 的元素。

证明. 我们给出的论证归功于詹姆斯·麦凯 $^{5}$。我们寻找方程 $g^{p}=e$ 除 $g=e$ 以外的解。事先并不明显存在这样的解。我们要做的是处理一个更一般的方程，它有很多解，然后认识到原始方程 $g^{p}=e$ 的解是该更一般方程的解集在某个群作用下的不动点。

[^3] 我们将方程 $g^{p}=e$ 推广到 $g_{1} g_{2} \cdots g_{p}=e$。这是一个有 $p$ 个未知数的方程。如果我们给定 $g_{1}, \ldots, g_{p-1}$ 的选择，那么 $g_{p}$ 被唯一确定为 $g_{1} g_{2} \cdots g_{p-1}$ 的逆。因此，这个方程的解的总数是 $|G|^{p-1}$。相比之下，我们不知道 $g^{p}=e$ 有多少个解，并且我们只知道一个解，即我们不感兴趣的平凡解。

考虑推广方程的解集：

$$
X=\left\{\left(g_{1}, \ldots, g_{p}\right): g_{i} \in G, g_{1} g_{2} \cdots g_{p}=e\right\}
$$

我们上面提到 $|X|=|G|^{p-1}$，所以这个集合很大。这个解集的一个好的特性是，一个解的循环移位给了我们更多的解：如果 $\left(g_{1}, g_{2}, \ldots, g_{p}\right) \in X$，那么 $\left(g_{2}, \ldots, g_{p}, g_{1}\right)$ 也在 $X$ 中。确实，$g_{1}=\left(g_{2} \cdots g_{p}\right)^{-1}$ 且元素与其逆可交换，所以 $g_{2} \cdots g_{p} g_{1}=e$。解中坐标的连续移位可以解释为 $\mathbf{Z} /(p)$ 在 $X$ 上的一个群作用：对 $j \in \mathbf{Z} /(p)$，令 $j \cdot\left(g_{1}, \ldots, g_{p}\right)=\left(g_{1+j}, \ldots, g_{p+j}\right)$，其中下标按模 $p$ 理解。这个移位是一个群作用。由于执行作用的群是 $p$-群 $\mathbf{Z} /(p)$，不动点同余式（定理 4.1）告诉我们

$$
\begin{equation*}
|G|^{p-1} \equiv \mid\{\text { 不动点 }\} \mid \bmod p \tag{5.1}
\end{equation*}
$$

$X$ 中被 $\mathbf{Z} /(p)$ 固定的点是什么？循环移位最终将每个坐标带到第一个位置，所以 $X$ 的一个不动点是所有坐标都相等的点。令公共值为 $g$，我们有 $(g, g, \ldots, g) \in X$ 恰好当 $g^{p}=e$。因此 (5.1) 变成

$$
\begin{equation*}
|G|^{p-1} \equiv\left|\left\{g \in G: g^{p}=e\right\}\right| \bmod p . \tag{5.2}
\end{equation*}
$$

到目前为止，我们还没有使用条件 $p||G|$。也就是说，(5.2) 对所有有限群 $G$ 和素数 $p$ 都有效。这在附录 A 中将很有用。

由于 $p$ 整除 $|G|$，(5.2) 的左边模 $p$ 为零，所以右边是 $p$ 的倍数。因此 $\left|\left\{g \in G: g^{p}=e\right\}\right| \equiv 0 \bmod p$。由于 $\left|\left\{g \in G: g^{p}=e\right\}\right|>0$，必须存在某个 $g \neq e$ 满足 $g^{p}=e$。

柯西定理有其他证明 $^{6}$，它们以不同的方式处理阿贝尔和非阿贝尔 $G$。上述证明以相同的方式处理所有有限群。

备注 5.5. 令 $G$ 为一个有限群，其中 $p||G|$，(5.2) 说

$$
\begin{equation*}
\left|\left\{g \in G: g^{p}=e\right\}\right| \equiv 0 \bmod p \tag{5.3}
\end{equation*}
$$

弗罗贝尼乌斯证明了一个更一般的结果：当 $d||G|$ 时，

$$
\left|\left\{g \in G: g^{d}=e\right\}\right| \equiv 0 \bmod d
$$

除数 $d$ 不必是素数。然而，证明不像素数除数的情形那样直接，我们不再更仔细地研究这一点。

## 6. 群作用在群论中的更多应用

在定理 1.7 中，我们看到了如何将 $G$ 的群作用解释为 $G$ 到对称群的一个特殊同态。我们现在将运用这个思想。

定理 6.1. 每个 6 阶非阿贝尔群同构于 $S_{3}$。

[^4] 证明. 令 $G$ 为 6 阶非阿贝尔群。我们将让 $G$ 置换一个大小为 3 的集合。
由柯西定理，$G$ 有阶为 2 的元素 $a$ 和阶为 3 的元素 $b$。如果 $a$ 和 $b$ 交换，那么 $a b$ 的阶为 6，所以 $G$ 是循环群，这不成立。因此 $a$ 和 $b$ 不交换，所以 $b a b^{-1}$ 不是 1 或 $a$。令 $H:=\langle a\rangle=\{1, a\}$，它不是 $G$ 的正规子群，因为 $b a b^{-1} \notin H$。在 $G$ 中有 3 个左 $H$-陪集。让 $G$ 通过左乘作用在它们上。这个群作用是一个同态 $\ell: G \rightarrow \operatorname{Sym}(G / H) \cong S_{3}$。如果 $g \in \operatorname{ker}(\ell)$，那么 $g H=H$，所以 $g \in H$。因此 $\operatorname{ker}(\ell)$ 是 $\{1\}$ 或 $H$。由于 $H \not \triangleleft G$，$H$ 不能是核，所以 $\operatorname{ker}(\ell)=\{1\}$：$\ell$ 是单射。$G$ 和 $S_{3}$ 的阶都是 6，所以 $\ell$ 是一个同构 $G \rightarrow S_{3}$。

定理 6.2. 令 $G$ 为一个有限群，$H$ 为一个 $p$-子群，使得 $p \mid[G: H]$。那么 $p \mid[\mathrm{N}(H): H]$。特别地，$\mathrm{N}(H) \neq H$。

我们这里不假设 $G$ 是 $p$-群。当 $G$ 也是 $p$-群时，将出现在推论 6.4 中。

证明. 令 $H$（不是 $G!$）通过左乘作用在 $G / H$ 上。由于 $H$ 是一个 $p$-群，不动点同余式定理 4.1 告诉我们

$$
\begin{equation*}
[G: H] \equiv \mid\{\text { 不动点 }\} \mid \bmod p . \tag{6.1}
\end{equation*}
$$

这里的不动点是什么？它是一个陪集 $g H$，使得对所有 $h \in H$ 有 $h g H=g H$。这意味着对每个 $h \in H$ 有 $h g \in g H$，这等价于 $g^{-1} H g=H$。这个条件意味着 $g \in \mathrm{~N}(H)$，所以不动点是满足 $g \in \mathrm{~N}(H)$ 的陪集 $g H$。因此 (6.1) 说

$$
[G: H] \equiv[\mathrm{N}(H): H] \bmod p
$$

这个同余式对所有有限群 $G$ 的 $p$-子群 $H$ 都有效。当 $p \mid[G: H]$ 时，我们从同余式看出指数 $[\mathrm{N}(H): H]$ 不能是 1，所以 $\mathrm{N}(H) \neq H$。

例 6.3. 令 $G=A_{4}$ 且 $H=\{(1),(12)(34)\}$。那么 $2 \mid[G: H]$，所以 $\mathrm{N}(H) \neq H$。事实上，$\mathrm{N}(H)=\{(1),(12)(34),(13)(24),(14)(23)\}$。

推论 6.4. 令 $G$ 为一个有限 $p$-群。每个指数为 $p$ 的子群是正规子群。

证明. 我们给出两个证明。首先，令子群为 $H$，所以 $H \subset \mathrm{~N}(H) \subset G$。由于 $[G: H]=p$，这些包含关系中有一个是等式。由定理 6.2，$\mathrm{N}(H) \neq H$，所以 $\mathrm{N}(H)=G$。这意味着 $H \triangleleft G$。

对于第二个证明，考虑 $G$ 在左陪集空间 $G / H$ 上的左乘作用。由定理 1.7，这个作用可以看作一个群同态 $\ell: G \rightarrow \operatorname{Sym}(G / H) \cong S_{p}$。令 $K$ 为 $\ell$ 的核，所以 $K \triangleleft G$。我们将证明 $H=K$。商 $G / K$ 嵌入到 $S_{p}$ 中，所以 $[G: K] \mid p!$。由于 $[G: K]$ 是 $p$ 的幂，$[G: K]=1$ 或 $p$。每个 $g \in K$ 满足 $g H=H$，所以 $g \in H$。换句话说，$K \subset H$，所以 $[G: K]>1$。因此 $[G: K]=p$，所以 $[H: K]=[G: K] /[G: H]=1$，即 $H=K \triangleleft G$。

推论 6.5. 令 $G$ 为一个有限群，$p$ 为素数，满足 $p^{n}| | G \mid$。那么存在一个子群链

$$
\{e\}=H_{0} \subset H_{1} \subset \cdots \subset H_{n} \subset G
$$

其中 $\left|H_{i}\right|=p^{i}$。
证明. 我们可以取 $n \geq 1$。由于 $p||G|$，由柯西定理存在一个大小为 $p$ 的子群，所以我们有 $H_{1}$。假设对于某个 $i<n$，我们有一个直到 $H_{i}$ 的子群链，我们将找到一个包含 $H_{i}$ 的大小为 $p^{i+1}$ 的子群 $H_{i+1}$。

由于 $p \mid\left[G: H_{i}\right]$，由定理 $6.2$ 有 $p \mid\left[\mathrm{N}\left(H_{i}\right): H_{i}\right]$。由于 $H_{i} \triangleleft \mathrm{~N}\left(H_{i}\right)$，我们可以考虑商群 $\mathrm{N}\left(H_{i}\right) / H_{i}$。它的大小可被 $p$ 整除，所以由柯西定理存在一个大小为 $p$ 的子群。这个子群在约化映射 $\mathrm{N}\left(H_{i}\right) \rightarrow \mathrm{N}\left(H_{i}\right) / H_{i}$ 下的原像是一个群 $H_{i+1}$，其大小为 $p\left|H_{i}\right|=p^{i+1}$。

定理 6.6 (C. 乔丹). 如果一个非平凡有限群作用在一个大小大于 1 的有限集合上，并且该作用只有一个轨道，那么某个 $g \in G$ 没有不动点。

证明. 由定理 3.29，

$$
1=\frac{1}{|G|} \sum_{g \in G}\left|\operatorname{Fix}_{g}(X)\right|=\frac{1}{|G|}\left(|X|+\sum_{g \neq e}\left|\operatorname{Fix}_{g}(X)\right|\right) .
$$

假设所有 $g \in G$ 至少有一个不动点。那么

$$
1 \geq \frac{1}{|G|}(|X|+|G|-1)=1+\frac{|X|-1}{|G|}
$$

因此 $|X|-1 \leq 0$，所以 $|X|=1$。这是一个矛盾。
备注 6.7. 使用有限单群的分类，可以证明 [3] 定理 6.6 中的 $g$ 可以选为具有素数幂阶。有一些例子表明可能无法选出一个具有素数阶的 $g$。

定理 6.8. 如果一个群 $G$ 有一个具有有限指数的子群 $H$，那么 (i) $G$ 有一个包含在 $H$ 中的具有有限指数的正规子群，并且 (ii) 有限多个 $G$ 的子群包含 $H$。

证明. (i) 令 $G \rightarrow \operatorname{Sym}(G / H)$ 为左乘作用，并令 $N$ 为其核。每个 $n \in N$ 满足对所有 $x \in G$ 有 $n x H=x H$，所以特别地 $n H=H$。因此 $n \in H$，所以 $N \subset H$。由于 $G / N$ 嵌入到 $\operatorname{Sym}(G / H)$ 中，而 $\operatorname{Sym}(G / H)$ 因 $[G: H]$ 有限而有限，所以 $[G: N]$ 有限。
(ii) 包含 $H$ 的 $G$ 的子群也包含 $N$，并且由于 $G / N$ 有限，只有有限多个 $G$ 的子群包含 $N$，所以只有有限多个 $G$ 的子群包含 $H$。

下面的定理，在一个特殊情况下，归功于庞加莱 [2], [6, p. 410]。其证明方法与定理 6.8(i) 类似，因此该结果也常归功于庞加莱。

定理 6.9. 如果一个群 $G$ 有子群 $H$ 和 $K$ 具有有限指数，那么 $G$ 有一个包含在 $H \cap K$ 中的具有有限指数的正规子群。特别地，$H \cap K$ 在 $G$ 中有有限指数。

证明. 令 $G \rightarrow \operatorname{Sym}(G / H \times G / K)$ 为 $G$ 在 $G / H \times G / K$ 上的左乘作用，其中 $g(x H, y K)=(g x H, g y K)$。令 $N$ 为核。那么群 $G / N$ 嵌入到有限群 $\operatorname{Sym}(G / H \times G / K)$ 中，所以 $[G: N]$ 有限。

每个 $n \in N$ 满足对所有 $x, y \in G$ 有 $n x H=x H$ 和 $n y K=y K$，所以特别地 $n H=H$ 和 $n K=K$。因此 $n \in H \cap K$，所以 $N \subset H \cap K$。因此 $[G: H \cap K]$ 有限。

定理 6.10. 令 $G$ 为一个有限群，$H$ 为一个真子群。那么 $G \neq \bigcup_{g \in G} g H g^{-1}$。也就是说，与真子群共轭的子群的并不覆盖整个群。

证明. 我们将给出两个证明。第二个将使用群作用。

每个子群 $g H g^{-1}$ 有相同的大小，即 $|H|$。有多少不同的共轭子群 $g H g^{-1}$（随着 $g$ 变化）？对 $g_{1}, g_{2} \in G$，

$$
\begin{aligned}
g_{1} H g_{1}^{-1}=g_{2} H g_{2}^{-1} & \Longleftrightarrow g_{2}^{-1} g_{1} H g_{1}^{-1} g_{2}=H \\
& \Longleftrightarrow g_{2}^{-1} g_{1} H\left(g_{2}^{-1} g_{1}\right)^{-1}=H \\
& \Longleftrightarrow g_{2}^{-1} g_{1} \in \mathrm{~N}(H) \\
& \Longleftrightarrow g_{1} \in g_{2} \mathrm{~N}(H) \\
& \Longleftrightarrow g_{1} \mathrm{~N}(H)=g_{2} \mathrm{~N}(H)
\end{aligned}
$$

因此，随着 $g$ 变化，不同子群 $g H g^{-1}$ 的数量是 $[G: \mathrm{N}(H)]$。这些子群都包含单位元，所以它们不是不相交的。因此，由于在单位元处重叠，$\bigcup_{g \in G} g H g^{-1}$ 的大小严格小于

$$
[G: \mathrm{N}(H)]|H|=\frac{|G|}{|\mathrm{N}(H)|}|H|=\frac{|H|}{|\mathrm{N}(H)|}|G| \leq|G|
$$

所以所有 $g H g^{-1}$ 的并不等于整个 $G$。
对于第二个证明，我们将定理 6.6 应用于 $G$ 在 $X=G / H$ 上通过左乘的作用。对于一个'点' $g H$ 在 $G / H$ 中，其稳定化子是 $g H g^{-1}$。由定理 6.6，某个 $a \in G$ 没有不动点，这意味着 $a \notin \bigcup_{g \in G} g H g^{-1}$。
备注 6.11. 定理 6.10 对无限群并不总是成立。例如，令 $G=\mathrm{GL}_{2}(\mathbf{C})$。$G$ 中的每个矩阵都有一个特征向量，所以我们可以将 $G$ 中的每个矩阵共轭到形式 $\left(\begin{array}{cc}a & b \\ 0 & d\end{array}\right)$。因此 $G=\bigcup_{g \in G} g H g^{-1}$，其中 $H$ 是上三角矩阵的真子群。当指数 $[G: H]$ 有限时，定理 6.10 对无限 $G$ 成立：由定理 6.8，$G$ 有一个包含在 $H$ 中的具有有限指数的正规子群 $N$，所以如果 $G=\bigcup_{g \in G} g H g^{-1}$，那么两边模 $N$ 约化得到 $G / N=\bigcup_{\bar{g} \in G / N} \bar{g}(H / N) \bar{g}^{-1}$，这与定理 6.10 矛盾，因为 $G / N$ 是有限的。

备注 6.12. 这是定理 6.10 在数论中的一个深刻应用。假设 $\mathbf{Z}[X]$ 中的一个多项式 $f(X)$ 是不可约的，并且对每个 $p$ 模 $p$ 有根。那么 $f(X)$ 是线性的。这个证明需要定理 6.10 和复分析。

备注 6.13. 如果 $H \not \triangleleft G$，那么 $\bigcup_{g \in G} g H g^{-1}$ 不一定是一个子群，但它可以是，例如，如果 $G=S_{4}$ 且 $H=\langle(12)\rangle$，那么 $\bigcup_{g \in G} g H g^{-1}=\{(1),(12)(34),(13)(24),(14)(23)\}$ 是 $S_{4}$ 中唯一的 4 阶正规子群。一般来说，由 $\bigcup_{g \in G} g H g^{-1}$ 生成的 $G$ 的子群称为 $H$ 在 $G$ 中的**正规闭包**。
推论 6.14. 如果 $H$ 是有限群 $G$ 的一个真子群，那么在 $G$ 中存在一个共轭类，它与 $H$ 及其共轭子群不相交。

证明. 选取一个 $x \notin \bigcup_{g \in G} g H g^{-1}$ 并使用 $x$ 的共轭类。
定理 6.15. 令 $G$ 为一个有限群，$|G|>1$，且 $p$ 为 $|G|$ 的最小素因子。$G$ 中每个指数为 $p$ 的子群是正规子群。

推论 6.4 是定理 6.15 的一个特例。群作用没有出现在定理 6.15 的陈述中，但它们将在其证明中发挥作用。根据 [4, pp. 3-4]，定理 6.15 是由恩斯特·施特劳斯在他还是学生时猜想并证明的。

证明. 令 $H$ 为 $G$ 的一个子群，指数为 $p$，所以 $G / H$ 是一个大小为 $p$ 的集合。我们将用两种使用群作用的方式证明 $H \triangleleft G$。

方法 1. 我们将证明 $H$ 是一个从 $G$ 出发的同态的核，因此是 $G$ 的一个正规子群。论证将类似于推论 6.4 的第二个证明。

令 $G$ 通过左乘作用在 $G / H$ 上，这（由定理 1.7）给出了一个群同态

$$
\begin{equation*}
G \rightarrow \operatorname{Sym}(G / H) \cong S_{p} \tag{6.2}
\end{equation*}
$$

这个同态将每个 $g \in G$ 发送到 $G / H$ 的置换 $\ell_{g}$，其中 $\ell_{g}(a H)=g a H$。我们将证明这个同态的核是 $H$。

记同态 (6.2) 的核为 $K$，所以 $K \triangleleft G$。群 $G / K$ 嵌入到 $S_{p}$ 中，所以 $[G: K] \mid p!$。由于 $[G: K]$ 整除 $|G|$，而 $|G|$ 的最小素因子是 $p$，所以 $(|G|, p!)=p$。因此 $[G: K]$ 是 1 或 $p$。每个 $g \in K$ 满足 $g H=H$，所以 $g \in H$。因此 $K \subset H$，所以 $[G: K]=[G: H][H: K]=p[H: K]$。因此 $[G: K]=p$ 且 $[H: K]=1$，所以 $H=K \triangleleft G$。

方法 2. $^{7}$ 令 $H$ 通过左乘作用在 $G / H$ 上，这（由定理 1.7）给出了一个群同态

$$
\begin{equation*}
H \rightarrow \operatorname{Sym}(G / H) \cong S_{p} \tag{6.3}
\end{equation*}
$$

$H$ 在这个 $p$ 元集合上的作用固定了陪集 $H$，所以每个轨道的大小至多为 $p-1$。由轨道-稳定化子公式，轨道的长度整除 $|H|$，而 $|H|$ 整除 $|G|$。$|G|$ 中不超过 $p-1$ 的唯一因子是 1（为什么？），所以 (6.3) 中 $H$-作用的所有轨道长度为 1。这意味着 (6.3) 是一个平凡作用：对每个 $h \in H$ 和 $g \in G$，有 $h g H=g H$。因此 $g^{-1} h g H=H$，所以 $g^{-1} h g \in H$，这意味着（随着 $h$ 变化）$g^{-1} H g \subset H$，所以 $g^{-1} H g=H$，因为两边大小相同。由于最后一个等式对所有 $g \in G$ 成立，所以 $H \triangleleft G$。

定理 6.15 的一些特殊情况值得单独记录。
推论 6.16. 令 $G$ 为一个有限群。
a) 如果 $H$ 是一个指数为 2 的子群，那么 $H \triangleleft G$。
b) 如果 $G$ 是一个 $p$-群且 $H$ 是一个指数为 $p$ 的子群，那么 $H \triangleleft G$。
c) 如果 $|G|=p q$，其中 $p<q$ 是不同的素数，那么 $G$ 中每个大小为 $q$ 的子群是正规子群。

证明. 部分 (a) 和 (b) 是定理 6.15 的直接推论。对于部分 c，注意大小为 $q$ 的子群是指数为 $p$ 的子群。这就完成了证明。

部分 (a) 可以直接检查，无需定理 6.15 的推理：如果 $[G: H]=2$ 且 $a \notin H$，那么 $H$ 的两个左陪集是 $H$ 和 $a H$，而 $H$ 的两个右陪集是 $H$ 和 $H a$。因此 $a H=G-H=H a$，所以 $H \triangleleft G$。部分 (b) 已经在推论 6.4 中看到。（事实上，我们推论 6.4 的第二个证明使用了与定理 6.15 的证明相同的思想。）部分 (c) 也可以直接用西罗定理直接检查，西罗定理表明 $G$ 中阶为 $q$ 的子群不仅是正规的，而且实际上是唯一的。在定理 6.15 中，这些不同的结果被统一为一个单一的陈述。

我们在本节中所有将群作用应用于群论的例子都是针对有限群的。这里有一个应用于无限群的例子。

定理 6.17. 一个有限生成群对每个整数 $n \geq 1$ 只有有限多个指数为 $n$ 的子群。

[^5] 证明. 令 $G$ 为一个有限生成群，$H$ 为一个具有有限指数的子群，比如指数 $n$。$G$ 在 $G / H$ 上的左乘作用是一个群同态 $\ell: G \rightarrow \operatorname{Sym}(G / H)$。在这个作用中，陪集 $H$ 的稳定化子是 $H$（$g H=H$ 当且仅当 $g \in H$）。

枚举 $G / H$ 中的 $n$ 个陪集，使得陪集 $H$ 对应数字 1。这个枚举给出了一个同构 $\operatorname{Sym}(G / H) \cong S_{n}$，所以我们可以让 $G$ 作用在集合 $\{1,2, \ldots, n\}$ 上，并且 1 的稳定化子是 $H$。因此，我们从每个指数为 $n$ 的子群 $H \subset G$ 构造了 $G$ 在 $\{1,2, \ldots, n\}$ 上的一个作用，其中 $H$ 是 1 的稳定化子。由于 $H$ 可以从作用中恢复，$G$ 中指数为 $n$ 的子群的数量以从 $G$ 到 $S_{n}$ 的同态的数量为上界。由于 $G$ 是有限生成的，它到有限群 $S_{n}$ 的同态只有有限多个。因此 $G$ 有有限多个指数为 $n$ 的子群。

我不知道这个定理有根本上不同于上述证明的证明。

这可能是提醒读者关于有限生成群的一个虚假性质的好地方：有限生成群的子群不一定有限生成！然而，有限生成群的每个有限指数子群是有限生成的：如果原始群有 $d$ 个生成元，那么指数为 $n$ 的子群最多有 $(d-1) n+1$ 个生成元。这归功于施赖尔。

## 附录 A. 群作用在数论中的应用

我们应用定理 4.1 中的不动点同余式及其推论 (5.2) 来推导三个经典的模 $p$ 同余式：费马、威尔逊和卢卡斯的同余式。

定理 A. 1 (费马). 如果 $n \not \equiv 0 \bmod p$，那么 $n^{p-1} \equiv 1 \bmod p$。
证明. 取 $n>0$ 就足够了，因为 $(-1)^{p-1} \equiv 1 \bmod p$。（这对奇数 $p$ 是显然的，因为 $p-1$ 是偶数，而对 $p=2$，使用 $-1 \equiv 1 \bmod 2$。）将 (5.2) 应用于加法群 $G=\mathbf{Z} /(n)$：

$$
\begin{equation*}
n^{p-1} \equiv|\{a \in \mathbf{Z} /(n): p a \equiv 0 \bmod n\}| \bmod p \tag{A.1}
\end{equation*}
$$

由于 $(p, n)=1$，同余式 $p a \equiv 0 \bmod n$ 等价于 $a \equiv 0 \bmod n$，所以 (A.1) 的右边是 1。

定理 A. 2 (威尔逊). 对素数 $p$，$(p-1)!\equiv-1 \bmod p$。
证明. 我们考虑 (5.2) 中 $G=S_{p}$ 的情况：

$$
0 \equiv\left|\left\{\sigma \in S_{p}: \sigma^{p}=(1)\right\}\right| \bmod p
$$

$S_{p}$ 的一个元素具有 $p$ 次幂 (1) 当它是 (1) 或一个 $p$-轮换。$p$-轮换的数量是 $(p-1)!$，加上 1 得到总计数，所以 $0 \equiv(p-1)!+1 \bmod p$。

定理 A. 3 (卢卡斯). 令 $p$ 为素数，$n \geq m$ 为非负整数。将它们按基 $p$ 写成

$$
n=a_{0}+a_{1} p+a_{2} p^{2}+\cdots+a_{k} p^{k}, \quad m=b_{0}+b_{1} p+b_{2} p^{2}+\cdots+b_{k} p^{k}
$$

其中 $0 \leq a_{i}, b_{i} \leq p-1$。那么

$$
\binom{n}{m} \equiv\binom{a_{0}}{b_{0}}\binom{a_{1}}{b_{1}} \cdots\binom{a_{k}}{b_{k}} \bmod p .
$$

证明. 我们将以下形式证明这个同余式：当 $n \geq m \geq 0$，且 $n= p n^{\prime}+a_{0}$，$m=p m^{\prime}+b_{0}$，其中 $0 \leq a_{0}, b_{0} \leq p-1$，我们有

$$
\binom{n}{m} \equiv\binom{a_{0}}{b_{0}}\binom{n^{\prime}}{m^{\prime}} \bmod p
$$

读者应验证这通过归纳法意味着卢卡斯的同余式。
将 $\{1,2, \ldots, n\}$ 分解为 $p$ 个连续的 $n^{\prime}$ 个整数的块的并集，从 1 到 $p n^{\prime}$，后面跟着一个长度为 $a_{0}$ 的最终块。也就是说，令

$$
A_{i}=\left\{i n^{\prime}+1, i n^{\prime}+2, \ldots,(i+1) n^{\prime}\right\}
$$

其中 $0 \leq i \leq p-1$，所以

$$
\{1,2, \ldots, n\}=A_{0} \cup A_{1} \cup \cdots \cup A_{p-1} \cup\left\{p n^{\prime}+1, \ldots, p n^{\prime}+a_{0}\right\} .
$$

对 $1 \leq t \leq n^{\prime}$，令 $\sigma_{t}$ 为 $p$-轮换

$$
\sigma_{t}=\left(t, n^{\prime}+t, 2 n^{\prime}+t, \ldots,(p-1) n^{\prime}+t\right)
$$

这个轮换循环置换 $A_{0}, A_{1}, \ldots, A_{p-1}$ 中模 $n^{\prime}$ 余 $t$ 的数字。不同 $t$ 的 $\sigma_{t}$ 是不相交的，所以它们交换。令 $\sigma=\sigma_{1} \sigma_{2} \cdots \sigma_{n^{\prime}}$。那么 $\sigma$ 作为 $\{1,2, \ldots, n\}$ 上的置换（固定所有大于 $p n^{\prime}$ 的数字）的阶为 $p$。

令 $X$ 为 $\{1,2, \ldots, n\}$ 的 $m$-元子集的集合，所以 $|X|=\binom{n}{m}$。令群 $\langle\sigma\rangle$ 作用在 $X$ 上。由于 $\sigma$ 的阶为 $p$，定理 4.1 告诉我们

$$
|X| \equiv \mid\{\text { 不动点 }\} \mid \bmod p
$$

左边是 $\binom{n}{m}$。我们将证明右边是 $\binom{a_{0}}{b_{0}}\binom{n^{\prime}}{m^{\prime}}$。
什么时候一个 $m$-元子集 $M \subset\{1,2, \ldots, n\}$ 被 $\sigma$ 固定？如果 $M$ 包含一个从 1 到 $p n^{\prime}$ 的数字，那么 $\sigma$-不变性意味着 $M$ 包含一个从 1 到 $n^{\prime}$ 的数字，即 $M \cap A_{0} \neq \emptyset$。假设 $M$ 包含 $q$ 个在 $A_{0}$ 中的数字。那么 $M$ 是这些数字及其在每个集合 $A_{0}, \ldots, A_{p-1}$ 中的平移的并集，再加上一些从 $p n^{\prime}+1$ 到 $p n^{\prime}+a_{0}$ 的数字，设为 $\ell$ 个。那么 $|M|=p q+\ell$。由于 $M$ 的大小为 $m=p m^{\prime}+b_{0}$，我们有 $b_{0} \equiv \ell \bmod p$。$b_{0}$ 和 $\ell$ 都在 $[0, p-1]$ 中，所以 $\ell=b_{0}$。因此 $q=m^{\prime}$。

因此在 $\sigma$ 下选择 $X$ 中的一个不动点等同于从 1 到 $n^{\prime}$ 选择 $m^{\prime}$ 个数字，然后从 $p n^{\prime}+1$ 到 $p n^{\prime}+a_{0}$ 选择 $b_{0}$ 个数字。所以不动点的数量是 $\binom{n^{\prime}}{m^{\prime}}\binom{a_{0}}{b_{0}}$，即使在 $a_{0}<b_{0}$ 的情况下也成立（在这种情况下有 0 个不动点，与在这种情况下 $\binom{a_{0}}{b_{0}}=0$ 一致）。

## 附录 B. 物理学中的一个群作用

在本节中，我们扩展例 2.6 关于空间和时间变换的内容，物理定律在这些变换下应保持不变，

我们时空的模型将是 $\mathbf{R}^{4}$。在非相对论（经典）物理中，$\mathbf{R}^{4}$ 中的点被标记为 $(t, \mathbf{x})=(t, x, y, z)$，其中 $t$ 是时间，$x, y, z$ 是 3 个空间坐标。这被称为伽利略时空。在相对论物理中，$\mathbf{R}^{4}$ 被称为闵可夫斯基时空，其点被写作 $(c t, \mathbf{x})=(c t, x, y, z)$，其中 $c$ 是光速。由于 $c$ 是速度，$t$ 是时间，$c t$ 具有长度单位，就像 $\mathbf{x}$ 的每个分量一样。（研究相对论的物理学家选择单位使得 $c=1$，所以 $t$ 作为时间或作为长度具有相同的值。）非相对论和相对论物理之间的两个区别在表 2 中描述：在非相对论物理中，速度不受限制，空间中的运动不影响时间，而在相对论物理中，速度（物理对象的）保持在 $c$ 以下，并且我们将看到的一些运动以非平凡的方式混合时间和空间坐标。这种混合是为什么
通过使用 $c t$ 代替 $t$ 的装置使时间坐标与空间坐标具有相同单位是好的。

|  | 允许速度 | 时间/空间坐标 |
| :---: | :---: | :---: |
| 非相对论 | 任意 | 无混合 |
| 相对论 | 小于 $c$ | 允许混合 |
| 表 2. 非相对论和相对论比较 |  |  |

不改变物理定律的基本时空变换是 (i) 空间和时间的平移，(ii) 空间的旋转，以及 (iii) 沿固定方向以恒定速度运动。(iii) 中的变换被称为“推动”，在非相对论和相对论物理中是不同的。(i) 和 (ii) 中的变换在两种情况下是相同的。

非相对论时空变换
(i) 空间和时间的平移。这些是 $(t, \mathbf{x}) \mapsto(t+s, \mathbf{x}+\mathbf{y})$，时间改变（或时间偏移） $s$，空间改变 $\mathbf{y}$。
(ii) 空间的旋转。这些是 $(t, \mathbf{x}) \mapsto(t, A \mathbf{x})$，其中 $A$ 是固定原点的 $\mathbf{R}^{3}$ 的旋转。这样的旋转构成群 $\mathrm{O}(3)=\left\{A \in \mathrm{M}_{3}(\mathbf{R}): A A^{\top}=I_{3}\right\}$。
(iii) 以速度 $\mathbf{v}$ 推动（固定速度 $\|\mathbf{v}\|$ 和方向 $\widehat{\mathbf{v}}=\mathbf{v} /\|\mathbf{v}\|$）。沿正 $x$-轴以速度 $v$ 的推动是 $(t, x, y, z) \mapsto(t, t v+x, y, z)$。更一般地，以速度 $\mathbf{v}$ 的推动 $B_{\mathbf{v}}$ 是 $B_{\mathbf{v}}(t, \mathbf{x})=(t, t \mathbf{v}+\mathbf{x})$。这里 $\mathbf{v}$ 是 $\mathbf{R}^{3}$ 中的一个任意（速度）向量。$B_{\mathbf{v}}$ 对 ( $t, \mathbf{x}$ ) 的效果可以描述为一个 $4 \times 4$ 矩阵变换，其中我们将 $\mathbf{v}$ 的坐标写作 $\left(v_{x}, v_{y}, v_{z}\right)$：

$$
\left(\begin{array}{llll}
1 & 0 & 0 & 0 \\
v_{x} & 1 & 0 & 0 \\
v_{y} & 0 & 1 & 0 \\
v_{z} & 0 & 0 & 1
\end{array}\right)\left(\begin{array}{l}
t \\
x \\
y \\
z
\end{array}\right)
$$

非相对论推动的复合是一个非相对论推动：$B_{\mathbf{v}} \circ B_{\mathbf{w}}= B_{\mathbf{v}+\mathbf{w}}$。
相对论时空变换
(i) 空间和时间的平移。这些是 $(c t, \mathbf{x}) \mapsto(c(t+s), \mathbf{x}+\mathbf{y})$，时间改变 $s$，空间改变 $\mathbf{y}$。这与上面的 (i) 相同，除了在时间坐标中使用 ct。
(ii) 空间的旋转。这些是 $(c t, \mathbf{x}) \mapsto(c t, A \mathbf{x})$，其中 $A \in \mathrm{O}(3)$。这与 (ii) 匹配，除了在时间坐标中使用 $c t$。
(iii) 以速度 $\mathbf{v}$ 推动（固定速度 $\|\mathbf{v}\|<c$ 和方向 $\widehat{\mathbf{v}}=\mathbf{v} /\|\mathbf{v}\|$）。沿正 $x$-轴以速度 $v$ 的推动是 $(c t, x, y, z) \mapsto\left(c \gamma\left(t+x v / c^{2}\right), \gamma(t v+x), y, z\right)$，其中 $\gamma=1 / \sqrt{1-v^{2} / c^{2}}$。更一般地，以速度 $\mathbf{v}$ 的相对论推动是

$$
\begin{equation*}
(c t, \mathbf{x}) \mapsto\left(\gamma c t+\gamma \frac{\mathbf{v}}{c} \cdot \mathbf{x}, \gamma t \mathbf{v}+\mathbf{x}+\frac{\gamma-1}{\|\mathbf{v}\|^{2}}(\mathbf{x} \cdot \mathbf{v}) \mathbf{v}\right), \tag{B.1}
\end{equation*}
$$

其中 $\gamma=1 / \sqrt{1-\|\mathbf{v}\|^{2} / c^{2}}=1 / \sqrt{1-\mathbf{v} \cdot \mathbf{v} / c^{2}}$。因子 $\gamma$ 依赖于速度 $\|\mathbf{v}\|$，大于 1。由二项式定理，其一阶近似是 $1+\frac{1}{2}\|\mathbf{v}\|^{2} / c^{2}$。作为一个 $4 \times 4$ 矩阵变换，以 $\mathbf{v}$ 的相对论推动是

$$
\left(\begin{array}{cccc}
\gamma & \frac{\gamma v_{x}}{c} & \frac{\gamma v_{y}}{c} & \frac{\gamma v_{z}}{c} \\
\frac{\gamma v_{x}}{c} & 1+\frac{(\gamma-1) v_{x}^{2}}{\|\mathbf{v}\|^{2}} & \frac{(\gamma-1) v_{x} v_{y}}{\|\mathbf{v}\|^{2}} & \frac{(\gamma-1) v_{x} v_{z}}{\|\mathbf{v}\|^{2}} \\
\frac{\gamma v_{y}}{c} & \frac{(\gamma-1) v_{x} v_{y}}{\|\mathbf{v}\|^{2}} & 1+\frac{(\gamma-1) v_{y}^{2}}{\|\mathbf{v}\|^{2}} & \frac{(\gamma-1) v_{y} v_{z}}{\|\mathbf{v}\|^{2}} \\
\frac{\gamma v_{z}}{c} & \frac{(\gamma-1) v_{x} v_{z}}{\|\mathbf{v}\|^{2}} & \frac{(\gamma-1) v_{y} v_{z}}{\|\mathbf{v}\|^{2}} & 1+\frac{(\gamma-1) v_{z}^{2}}{\|\mathbf{v}\|^{2}}
\end{array}\right)\left(\begin{array}{c}
c t \\
x \\
y \\
z
\end{array}\right)
$$

作为一个压缩的 $2 \times 2$ 矩阵（右下角是一个 $3 \times 3$ 矩阵），这是

$$
\left(\begin{array}{cc}
\gamma & \gamma \mathbf{v}^{\top} / c  \tag{B.2}\\
\gamma \mathbf{v} / c & I_{3}+\frac{(\gamma-1) \mathbf{v} \mathbf{v}^{\top}}{\|\mathbf{v}\|^{2}}
\end{array}\right)\binom{c t}{\mathbf{x}} .
$$

当 $\|\mathbf{v}\|$ 远小于 $c$（即 $\|\mathbf{v}\| / c$ 接近 0）时，$\gamma$ 接近 1，这使得 (B.1) 中的公式近似为 ( $c t, t \mathbf{v}+\mathbf{x}$ )。如果伽利略时空中的点被标记为 ( $c t, \mathbf{x}$ )，那么这就是以 $\mathbf{v}$ 的非相对论推动，这说明了相对论物理如何在速度远低于光速时变成经典物理。（这里我们没有考虑任何涉及质量的因素，质量在相对论中即使在低速下也有其自身的影响。）

虽然非相对论推动只影响空间坐标，但相对论推动影响时间和空间坐标，因此两个相对论推动的复合不一定是一个相对论推动。

例 B.1. 我们看看沿正 $x$ 和 $y$ 轴的相对论推动，分别由 $(3 / 5) c \mathbf{e}_{1}$ 和 $(3 / 5) c \mathbf{e}_{2}$ 给出。由于 $\gamma((3 / 5) c)=1 / \sqrt{1-(3 / 5)^{2}}=5 / 4$，这两个推动分别是

$$
\left(\begin{array}{cccc}
5 / 4 & 3 / 4 & 0 & 0  \tag{B.3}\\
3 / 4 & 5 / 4 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{array}\right) \quad \text { 和 } \quad\left(\begin{array}{cccc}
5 / 4 & 0 & 3 / 4 & 0 \\
0 & 1 & 0 & 0 \\
3 / 4 & 0 & 5 / 4 & 0 \\
0 & 0 & 0 & 1
\end{array}\right)
$$

它们以任意顺序的乘积都不是一个相对论推动：相对论推动矩阵是对称的，而 (B.3) 中矩阵以任意顺序的乘积都不是对称的。

在非相对论和相对论物理中，我们都可以将类型 (i)、(ii) 和 (iii) 的变换组合成单个群在 $\mathbf{R}^{4}$ 上的作用。

非相对论时空变换
平移向量 $(s, \mathbf{y}) \in \mathbf{R}^{4}$ 以自然的方式作用在 $\mathbf{R}^{4}$ 上：$(s, \mathbf{y})(t, \mathbf{x}):=(s+t, \mathbf{y}+\mathbf{x})$。旋转矩阵 $A \in \mathrm{O}(3)$ 和速度向量 $\mathbf{v} \in \mathbf{R}^{3}$ 一起作用在 $\mathbf{R}^{4}$ 上，结合了空间的旋转和推动：

$$
\begin{equation*}
(\mathbf{v}, A)(t, \mathbf{x})=\mathbf{v} \cdot(A \cdot(t, \mathbf{x}))=\mathbf{v} \cdot(t, A \mathbf{x})=(t, t \mathbf{v}+A \mathbf{x}) \tag{B.4}
\end{equation*}
$$

$\mathbf{R}^{3}$ 的等距群是所有函数 $\mathbf{x} \mapsto \mathbf{v}+A \mathbf{x}$，其中 $\mathbf{v} \in \mathbf{R}^{3}$ 且 $A \in \mathrm{O}(3)$。在函数复合下，等距的群运算是 $\left(\mathbf{v}^{\prime}, A^{\prime}\right)(\mathbf{v}, A)=\left(\mathbf{v}^{\prime}+A^{\prime} \mathbf{v}, A^{\prime} A\right)$，这使得 (B.4) 成为 $\mathbf{R}^{3}$ 的等距群在 $\mathbf{R}^{4}$ 上的一个作用（请验证！）。这样的 $\mathbf{R}^{4}$ 变换被称为伽利略变换。非相对论推动是 (B.4) 中 $A=I_{3}$ 时的特例，这就是为什么非相对论推动被称为“无旋转”伽利略变换。

$\mathbf{R}^{n}$ 的等距群记为 $\mathrm{E}(n)$，因为距离是 $\mathbf{R}^{n}$ 作为欧几里得空间几何的基础。将上述 $\mathbf{R}^{4}$ 和 E(3) 在 $\mathbf{R}^{4}$ 上的作用结合起来，

$$
\begin{equation*}
(s, \mathbf{y})((\mathbf{v}, A)(t, \mathbf{x}))=(s, \mathbf{y})(t, t \mathbf{v}+A \mathbf{x})=(s+t, \mathbf{y}+t \mathbf{v}+A \mathbf{x}) . \tag{B.5}
\end{equation*}
$$

由于

$$
(\mathbf{v}, A)((s, \mathbf{y})(t, \mathbf{x}))=(\mathbf{v}, A)(s+t, \mathbf{y}+\mathbf{x})=(s+t,(s+t) \mathbf{v}+A \mathbf{y}+A \mathbf{x})
$$

$\mathbf{R}^{4}$ 和 $\mathrm{E}(3)$ 在 $\mathbf{R}^{4}$ 上的效果不交换。
让对 $((s, \mathbf{y}),(\mathbf{v}, A)) \in \mathbf{R}^{4} \times \mathrm{E}(3)$ 根据 (B.5) 作用在 $\mathbf{R}^{4}$ 上：

$$
\begin{equation*}
((s, \mathbf{y}),(\mathbf{v}, A))(t, \mathbf{x}):=(s+t, \mathbf{y}+t \mathbf{v}+A \mathbf{x}) . \tag{B.6}
\end{equation*}
$$

$\left(\left(s^{\prime}, \mathbf{y}^{\prime}\right),\left(\mathbf{v}^{\prime}, A^{\prime}\right)\right)$ 和 $((s, \mathbf{y}),(\mathbf{v}, A))$ 对 $(t, \mathbf{x})$ 的作用的复合是

$$
\begin{aligned}
\left(\left(s^{\prime}, \mathbf{y}^{\prime}\right),\left(\mathbf{v}^{\prime}, A^{\prime}\right)\right)(((s, \mathbf{y}),(\mathbf{v}, A))(t, \mathbf{x})) & =\left(\left(s^{\prime}, \mathbf{y}^{\prime}\right),\left(\mathbf{v}^{\prime}, A^{\prime}\right)\right)(s+t, \mathbf{y}+t \mathbf{v}+A \mathbf{x}) \\
& =\left(s^{\prime}+(s+t), \mathbf{y}^{\prime}+(s+t) \mathbf{v}^{\prime}+A^{\prime}(\mathbf{y}+t \mathbf{v}+A \mathbf{x})\right) \\
& =\left(s^{\prime}+s+t,\left(\mathbf{y}^{\prime}+A^{\prime} \mathbf{y}+s \mathbf{v}^{\prime}\right)+t\left(\mathbf{v}^{\prime}+A^{\prime} \mathbf{v}\right)+\left(A^{\prime} A\right) \mathbf{x}\right)
\end{aligned}
$$

将最终结果写作 $((?, ?),(?, ?))(t, \mathbf{x})$ 以适应 (B.6) 表明我们应该通过以下规则将 $\mathbf{R}^{4} \times \mathrm{E}(3)$ 的元素相乘：

$$
\begin{equation*}
\left(\left(s^{\prime}, \mathbf{y}^{\prime}\right),\left(\mathbf{v}^{\prime}, A^{\prime}\right)\right)((s, \mathbf{y}),(\mathbf{v}, A))=\left(\left(s^{\prime}+s, \mathbf{y}^{\prime}+A^{\prime} \mathbf{y}+s \mathbf{v}^{\prime}\right),\left(\mathbf{v}^{\prime}+A^{\prime} \mathbf{v}, A^{\prime} A\right)\right) . \tag{B.7}
\end{equation*}
$$

由于 $\mathrm{E}(3)$ 的元素通过 $\left(\mathbf{v}^{\prime}, A^{\prime}\right)(\mathbf{v}, A)=\left(\mathbf{v}^{\prime}+A^{\prime} \mathbf{v}, A^{\prime} A\right)$ 复合，我们可以将 (B.7) 重写为

$$
\left(\left(s^{\prime}, \mathbf{y}^{\prime}\right),\left(\mathbf{v}^{\prime}, A^{\prime}\right)\right)((s, \mathbf{y}),(\mathbf{v}, A))=\left(\left(s^{\prime}, \mathbf{y}^{\prime}\right)+\left(\mathbf{v^{\prime}}, A^{\prime}\right)(s, \mathbf{y}),\left(\mathbf{v}^{\prime}, A^{\prime}\right)(\mathbf{v}, A)\right),
$$

其中 ( $\left.\mathbf{v}^{\prime}, A^{\prime}\right)(s, \mathbf{y})=\left(s, A^{\prime} \mathbf{y}+s \mathbf{v}^{\prime}\right)$，这是 $\mathrm{E}(3)$ 通过 (B.4) 作用在 $\mathbf{R}^{4}$ 上的方式。因此 (B.7) 可以被描述为一个半直积群 $\mathbf{R}^{4} \rtimes_{\varphi} \mathrm{E}(3)$，其中 $\varphi$ 来自 (B.4)。这个半直积群是伽利略时空 $\mathbf{R}^{4}$ 的伽利略群。群 $\mathbf{R}^{4} \rtimes_{\varphi} \mathrm{E}(3)$ 通过 (B.6) 作用在 $\mathbf{R}^{4}$ 上，并且 $\mathbf{R}^{4}$ 的非相对论变换 (i)、(ii) 和 (iii) 是 (B.6) 的特例，通过取 $\mathbf{R}^{4} \rtimes_{\varphi} \mathrm{E}(3)$ 中的某些分量为平凡而得到。

备注 B.2. 在 (B.6) 中，原点 $(t, \mathbf{x})=(0, \mathbf{0})$ 被固定当且仅当 $(s, \mathbf{y})=(0, \mathbf{0})$，所以伽利略群中固定原点的元素是伽利略变换。为了区分整个伽利略群和固定原点的子群，整个群被称为**非齐次伽利略群**，固定 $\mathbf{0}$ 的子群被称为**齐次伽利略群**，类似于高中代数中线性函数 $m x+b$ 由于常数项而被称为“非齐次”，而线性代数中的线性函数 $m x$ 由于常数项为 0 而被称为“齐次”。

## 相对论时空变换

闵可夫斯基时空的变换 (i)、(ii) 和 (iii) 组合起来给出了一个群在 $\mathbf{R}^{4}$ 上的作用，方法与在非相对论情况中相同。首先，我们让 $\mathbf{R}^{4}$ 作为时间和空间平移作用在闵可夫斯基时空上，就像在非相对论情况中一样：对 $(c t, \mathbf{x}) \in \mathbf{R}^{4}$ 和 $(c s, \mathbf{y}) \in \mathbf{R}^{4}$，令 $(c s, \mathbf{y})(c t, \mathbf{x})=(c(s+t), \mathbf{y}+\mathbf{x})$。每个 $A \in \mathrm{O}(3)$ 通过 $A(c t, \mathbf{x})=(c t, A \mathbf{x})$ 作用在 $\mathbf{R}^{4}$ 上。每个速度向量 $\mathbf{v} \in \mathbf{R}^{3}$ 通过相对论推动 (B.1) 作用在 $\mathbf{R}^{4}$ 上。将这三个变换放在一起导致了闵可夫斯基时空的所有“对称性”，它们有一个复杂的复合公式。这些变换及其乘积构成庞加莱群。其固定原点的子群由旋转和推动构成（无非零平移），被称为洛伦兹群。

伽利略群和庞加莱群的维数都是 $4+6=10$。在 $\mathbf{R}^{n+1}$（$n$ 个空间坐标和 1 个时间坐标）上的类似物具有维数 $(n+1)(n+2) / 2$。

## 参考文献

[1] W. Burnside, Theory of Groups of Finite Order, Cambridge Univ. Press, Cambridge, 1897. URL https://archive.org/details/in.ernet.dli.2015.168629/page/n183/mode/2up.
[2] Georg Essl, Answer to "Source of Poincaré's theorem on subgroups with finite index", History of Science and Mathematics Stack Exchange. April 21, 2025. URL https://hsm.stackexchange. com/questions/18494
[3] B. Fein, W. M. Kantor, M. Schacher, Relative Brauer groups II, J. Reine Angew. Math. 328 (1981), 39-57.
[4] B. R. Gelbaum and J. M. H. Olmstead, Theorems and Counterexamples in Mathematics, Springer, New York, 1990.
[5] I. M. Isaacs and M. R. Pournaki, "Generalizations of Fermat's Little Theorem Using Group Theory," Amer. Math. Monthly 112 (2005), 734-740.
[6] H. Poincaré, Les fonctions fuchsiennes et l'Arithmétique, J. Math. Pures Appl. 3 (1887), 405-464. URL https://www.numdam.org/item/JMPA_1887_4_3_405_0.pdf
[7] Wikipedia, Burnside's lemma, http://en.wikipedia.org/wiki/Burnside\'s_lemma.


[^0]:    ${ }^{1}$ 当 $X=\emptyset$ 时，将 $\operatorname{Sym}(X)$ 和 $\operatorname{Alt}(X)$ 视为平凡群。大小为 0 的集合的置换数为 $0!=1$。

[^1]:    ${ }^{2}$ 论证将类似于证明子群的不同左陪集不相交：如果陪集重叠，它们就重合。

[^2]:    ${ }^{3}$ 阶为 $n$ 不仅仅满足 $z^{n}=1$：没有更小的幂可以是 1，所以当 $n>1$ 时 $X_{n}$ 不是所有 $n$ 次单位根。

[^3]:    ${ }^{4}$ 参见 p. 588 of Théorèmes sur les groupes de substitutions, Mathematische Annalen 5 (1872), 584-594; URL https://eudml.org/doc/156588. 英文翻译由 Robert Wilson, URL http://www.maths. qmul.ac.uk/~raw/pubs_files/Sylow.pdf.
    ${ }^{5}$ J. McKay, Another Proof of Cauchy's Theorem, Amer. Math. Monthly 66 (1959), 119.

[^4]:    ${ }^{6}$ 参见 https://kconrad.math.uconn.edu/blurbs/grouptheory/cauchypf。

[^5]:    ${ }^{7}$ 我从 Bar Alon 的回答中学到了这一点 https://math.stackexchange.com/questions/164244/ normal-subgroup-of-prime-index.