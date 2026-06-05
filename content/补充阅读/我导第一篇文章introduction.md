# 自相似测度的Khintchine二分法

[文件内容开始]
===== 第 1 页 =====

1. 引言 1
2. 预备知识 6
3. 正维数 13
4. 维数自举 14
5. 从高维数到等分布 21
6. 双重等分布 25
7. 二分法 27
参考文献 34

## 1. 引言

实直线 $\mathbb{R}$ 上的一个 Borel 概率测度 $\sigma$ 称为自相似的，如果它满足

$$\sigma = \sum_{i = 1}^{\mathfrak{m}}\lambda_{i}\phi_{i\bullet}\sigma \quad (1.1)$$

对于某个整数 $\mathfrak{m}\geq 1$、某个概率向量 $(\lambda_{1},\dots ,\lambda_{\mathfrak{m}})\in \mathbb{R}_{\geq 0}^{\mathfrak{m}}$ 以及某些没有公共不动点的可逆仿射映射 $\phi_{1},\ldots ,\phi_{\mathfrak{m}}:\mathbb{R}\to \mathbb{R}$。这包含了缺失数字康托集上的 Hausdorff 测度。例如，三分康托集上的测度满足 (1.1)，其中 $\lambda_{1} = \lambda_{2} = 1 / 2$，$\phi_{1}:t\mapsto t / 3$ 和 $\phi_{2}:t\mapsto t / 3 + 2 / 3$。自相似测度的另一种标准定义要求所有映射 $\phi_{i}$ 都是压缩的。我们没有施加这样的条件，参见 §2.1 的进一步讨论。

探索自相似测度支集内点的丢番图性质尤其引人入胜。这个研究课题由 Mahler 在 [41, 第 2 节] 中提出，他询问三分康托集中的无理数能被有理数逼近到多好。解决 Mahler 问题的一种方法是

===== 第 2 页 =====

研究 Khintchine 定理是否能推广到三分康托集测度（如 Kleinbock-Lindenstrauss-Weiss 在 [30, 第 10.1 节] 中所问）。

让我们回顾经典的 Khintchine 定理。此后，$\psi :\mathbb{N}\to \mathbb{R}_{>0}$ 是一个函数，被称为逼近函数。一个点 $s\in \mathbb{R}$ 称为 $\psi$-可逼近的，如果存在无穷多对 $(p,q)\in \mathbb{Z}\times \mathbb{N}$ 使得

$$|qs - p| < \psi (q)。 \quad (1.2)$$

记 $W(\psi)$ 为 $\mathbb{R}$ 中 $\psi$-可逼近点的集合。关于 Lebesgue 测度的经典 Khintchine 定理 [27, 28] 指出：给定一个非增逼近函数 $\psi$，如果级数 $\sum_{q\in \mathbb{N}}\psi (q)$ 收敛，则集合 $W(\psi)$ 的 Lebesgue 测度为零；如果级数发散，则其测度为全。

在本文中，我们将 Khintchine 定理推广到 $\mathbb{R}$ 上所有自相似概率测度。

**定理 A (自相似测度的 Khintchine 定理)**。设 $\sigma$ 是 $\mathbb{R}$ 上的一个自相似概率测度，$\psi :\mathbb{N}\to \mathbb{R}_{>0}$ 是一个非增函数。那么

$$\sigma (W(\psi)) = \left\{ \begin{array}{ll}0 & \text{如果} \sum_{q\in \mathbb{N}}\psi (q) < \infty,\\ 1 & \text{如果} \sum_{q\in \mathbb{N}}\psi (q) = \infty。 \end{array} \right. \quad (1.3)$$

在发散情形下，对于 $\sigma$-典型的 $s\in \mathbb{R}$，我们还能得到不等式 (1.2) 在 $q$ 有界时的解数的估计，参见 (7.4) 和 (7.5)。

让我们简要介绍一下关于分形上 Khintchine 定理的研究现状。

对于收敛部分，$\psi (q) = 1 / q^{1 + \epsilon}$ 的情形由 Weiss [56] 处理，适用于满足某种衰减条件的测度，包括三分康托集测度。Weiss 的结果后来被 Kleinbock-Lindenstrauss-Weiss [30] 推广到 $\mathbb{R}^d$ 上的友好测度。另见 Pollington-Velani [44] 关于绝对友好测度的工作，以及 Das-Fishman-Simmons-Urbanski [16, 17] 关于拟衰减测度的工作。

对于发散部分，$\psi (q) = \epsilon /q$ 的情形由 Einsiedler-Fishman-Shapira [20] 处理，适用于缺失数字康托集测度。Simmons-Weiss [50] 随后显著推广了他们的结果，将其提升到 $\mathbb{R}^d$ 上的任意自相似测度（并附带若干改进）。

上述所有工作都专注于特定的逼近函数 $\psi$。在 $\psi$ 非增的唯一条件下，Khalil 和 Luethi [25] 成功地将 Khintchine 定理推广到 $\mathbb{R}^d$ 上的自相似测度 $\sigma$，前提是 $\sigma$ 具有大维数，且底下的 IFS $(\phi_i)_{1\leq i\leq m}$ 是压缩的、有理的，并满足开集条件。特别是，他们推导出了基数为 5 的缺失一位数字康托集的 Khintchine 定理。使用基于傅里叶分析的不同方法，Yu [58] 也实现了收敛部分，适用于一般的逼近函数，前提是 $\sigma$ 具有足够快的平均傅里叶衰减。发散部分最近由 Datta-Jana [18] 在类似限制下解决，覆盖了 [25] 未覆盖的一些情况，例如基数为 450 的缺失三位数字康托集。

所有上述工作都对分形测度成立 Khintchine 二分法 (1.3) 施加了各种限制。具体来说，它们都没有建立

===== 第 3 页 =====

Mahler 所宣传的三分康托集测度的情形 (1.3)。定理 A 不仅处理了这种情况，而且显著地推广了它。

**其他相关研究课题**。正如 Mahler 在 [41] 中指出的，研究康托集上的内在丢番图逼近也很有趣。这意味着询问分形集上的点能被分形集本身内部的有理点逼近到多好。关于这个方向的研究，我们推荐近期工作 [54, 13] 及其参考文献。

除了分形，Khintchine 定理在 $\mathbb{R}^d$ 的子流形上也得到了广泛研究。该领域的主要工作包括 [34, 55, 8, 9]。

定理 A 来自于齐次动力学中的一个有效等分布结果，我们现在给出这个结果。考虑实代数群 $G = \mathrm{SL}_2(\mathbb{R})$、一个格子 $\Lambda \subseteq G$，以及商空间 $X = G / \Lambda$，赋予标准的双曲度量 (§2.1) 和 Haar 概率测度 $m_X$。记 $\mathrm{inj}(x)$ 为 $x\in X$ 处的单射半径 (§2.1)。用 $B_{\infty ,1}^{\infty}(X)$ 表示 $X$ 上有界且一阶导数有界的光滑函数的集合，用 $S_{\infty ,1}(\cdot)$ 表示相关的 $C^1$-范数 (§2.1)。对于 $t > 0$ 和 $s\in \mathbb{R}$，记 $a(t), u(s) \in G$ 为如下给出的元素

$$
a(t) = \begin{pmatrix} t^{1/2} & 0 \\ 0 & t^{-1/2} \end{pmatrix}, \quad u(s) = \begin{pmatrix} 1 & s \\ 0 & 1 \end{pmatrix}.
$$

**定理 B (膨胀分形的有效等分布)**。设 $\sigma$ 是 $\mathbb{R}$ 上的一个自相似概率测度。存在常数 $c = c(\Lambda ,\sigma) > 0$，使得对所有 $t > 1$、$x\in X$、$f\in B_{\infty ,1}^{\infty}(X)$，我们有

$$\int_{\mathbb{R}} f(a(t)u(s)x) \, \mathrm{d}\sigma(s) = \int_X f \, \mathrm{d}m_X + O\bigl(\mathrm{inj}(x)^{-1} S_{\infty ,1}(f) t^{-c}\bigr) \quad (1.4)$$

其中 $O(\cdot)$ 中的隐含常数仅依赖于 $\Lambda$ 和 $\sigma$。

定理 B 表明，将测度 $\sigma$ 视为在基于 $x$ 的一段水平圆环上，并经过测地流作用膨胀后，其指数级等分布。等分布速率中的指数 $c$ 关于 $x$ 是一致的，然而当 $x$ 处于尖点高处时，等分布可能需要更多时间才能启动。这由速率中的项 $\mathrm{inj}(x)^{-1}$ 反映出来。我们还将建立定理 B 的一个处理双重等分布的细化版本，参见方程 (6.3)。

齐次动力学与丢番图逼近之间的联系被称为 Dani 对应 [15]。在 [35] 中，Kleinbock-Margulis 明确展示了如何使用动力学来获得经典 Lebesgue 测度 Khintchine 定理的新证明，另见 Sullivan [53] 的变体以及 Patterson [43] 的开创性工作。这种动力学视角为后来许多在不同方面推广 Khintchine 定理的工作奠定了基础，例如 [32, 14, 25]。特别地，从 (1.4) 到定理 A 收敛情形的蕴含关系已在 Khalil-Luethi [25, 定理 9.1] 的工作中给出。在额外的假设下，即 $\sigma$ 来自满足开集条件的压缩 IFS，他们还证明了 (1.4) 足以建立定理 A 的发散情形，参见 [25, 定理 12.1]。他们的证明依赖于一个精巧的逆 Borel-Cantelli 引理。这里，我们采用一种更接近 Schmidt [47] 对定量 Khintchine 定理的原始证明的方法。利用定理 B 的优势，这使我们能够摆脱额外的假设，并且具有更短且定量的双重优势，参见第 7 节。

===== 第 4 页 =====

除了在丢番图逼近中的应用，定理 B 本身也很有趣。它可以看作是 $X$ 上单幂流 Ratner 等分布定理的一个分形且有效的版本。回顾 Ratner 定理指出，有限体积齐性空间上的任何单幂轨道都在包含它的最小有限体积齐性子空间中等分布。不幸的是，该证明没有给出等分布速率的信息。在过去的几年里，人们为了获得 Ratner 定理的有效版本，即量化大的但有界的单幂轨道片段的等分布，做出了大量努力。在单幂轨道来自于一个 horospherical 子群作用的情况下，Kleinbock 和 Margulis 在 [33, 36] 中建立了在相应对角流作用下膨胀平移的有效等分布。最近，Einsiedler-Margulis-Venkatesh [21]、Strömbergsson [52]、Kim [29]、Lindenstrauss-Mohammadi [38]、Lindenstrauss-Mohammadi-Wang [39]、Yang [57] 以及 Lindenstrauss-Mohammadi-Wang-Yang [40] 在有效 Ratner 定理方面取得了重大进展。我们注意到这些工作关注的是单幂轨道上一段上的 Haar 测度的膨胀平移。在 [25] 中，Khalil 和 Luethi 获得了 $\mathrm{SL}_{d + 1}(\mathbb{R}) / \mathrm{SL}_{d + 1}(\mathbb{Z})$ 中单幂轨道上膨胀分形测度的第一个有效等分布结果。他们的论证基于底下的 IFS 是压缩的、有理的、满足开集条件，并且测度 $\sigma$ 足够厚。他们还要求起点 $x$ 属于一个与 IFS 相关的特定可数集。在 Datta-Jana [18] 中，在 $\mathrm{SL}_{2}(\mathbb{R}) / \mathrm{SL}_{2}(\mathbb{Z})$ 中也得到了膨胀测度的有效等分布，前提是足够快的平均傅里叶衰减以及对起点 $x$ 的限制。定理 B 推广了 Khalil-Luethi 和 Datta-Jana 在 $\mathrm{SL}_{2}(\mathbb{R}) / \mathrm{SL}_{2}(\mathbb{Z})$ 中的等分布结果，因为它允许任意的格子 $\Lambda$、任何起点 $x$，以及最重要的，任何自相似测度 $\sigma$。我们的误差项对起点的依赖性也更加精确。

**注记**。由定理 B 得到的弱-$^*$ 收敛 $\lim_{t\to +\infty} \int_{\mathbb{R}} a(t)u(s)x \, \mathrm{d}\sigma(s) = m_X$ 也是新的。无速率的收敛也在 Khalil-Luethi-Weiss [26] 关于所有维数有理 carpet IFS 的独立并行工作中得到处理。然而，请注意，有效性，更确切地说，如 (1.4) 中的多项式收敛速率，对于通过 Dani 对应推导 Khintchine 二分法 (1.3) 至关重要。

我们从随机游走的角度证明定理 B。膨胀分形的渐近行为与随机游走的渐近行为之间的联系源于 Simmons-Weiss [50] 的工作，并在 [45, 46, 25, 19, 1] 中得到了进一步利用。在本文中，这种联系以引理 5.4 的形式呈现。

我们建立了以下由膨胀上三角矩阵驱动的 $X$ 上随机游走的有效依分布等分布。在下面的陈述中，$\mathbb{R}^2$ 赋予通常的欧几里得结构，记 $e_1 \coloneqq (1,0) \in \mathbb{R}^2$。

**定理 C (随机游走的有效等分布)**。设 $\mu$ 是群

$$\{a(t)u(s): t > 0, s\in \mathbb{R}\} \subseteq G$$

上的一个有限支撑概率测度。假设 $\mu$ 的支撑集不是同时可对角化的，并且 $\mu$ 满足 $\int_{G} \log \| g e_1 \| \, \mathrm{d}\mu(g) > 0$。那么存在常数 $c = c(\Lambda, \mu) > 0$，使得对所有

===== 第 5 页 =====

$x\in X$、$n\geq 1$ 和 $f\in B_{\infty ,1}^{\infty}(X)$，我们有

$$\mu^{*n} * \delta_x(f) = m_X(f) + O\bigl(\mathrm{inj}(x)^{-1} S_{\infty ,1}(f) e^{-cn}\bigr),$$

其中 $O(\cdot)$ 中的隐含常数仅依赖于 $\Lambda$ 和 $\mu$。

定理 C 的证明受 [6] 的启发，其中第一和第二作者建立了由 $G$ 上的 Zariski 稠密概率测度驱动的 $X$ 上随机游走的有效等分布。然而，在我们的上下文中，作用群是可解的。证明包括三个阶段。每一步都涉及某个尺度下随机游走分布的维数。

首先，我们证明随机游走获得一些初始正维数：存在由 $\Lambda, \mu$ 决定的常数 $\kappa > 0$ 和 $A > 0$，使得对每个小的 $\rho > 0$、$x, y \in X$、以及每个 $n \geq |\log \rho| + A |\log \mathrm{inj}(x)|$，有

$$\mu^{*n} * \delta_x(B_\rho y) \leq \rho^{\kappa},$$

其中 $B_\rho y$ 表示 $X$ 中以 $y$ 为中心、半径为 $\rho$ 的开球。

其次，我们将指数 $\kappa$ 的值自举到任意接近 3，比如说达到 $3 - \epsilon$，前提是 $\rho \leq \rho_0(\epsilon, \Lambda, \mu)$ 且 $n \geq C_0(\epsilon, \Lambda, \mu) |\log \rho| + A |\log \mathrm{inj}(x)|$。该方法基于 [6] 中的多切片论证，而该论证又依赖于 Bourgain 式的离散化投影定理。迭代离散化投影定理以自举（粗糙）维数的思想可追溯到 Bourgain-Furman-Lindenstrauss-Mozes [12] 的工作，并在上述提及的有效化 Ratner 定理的最新进展中发挥了重要作用。在一个非常不同的背景下，它也在投影理论的最新发展中发挥了关键作用（例如 Orponen-Shmerkin-Wang [42]）。我们实现这种迭代的方式与这些工作不同，源自 [6]。

最后，一旦维数接近满维，我们使用作用在 $L^2(X)$ 上的卷积算子 $f \mapsto \mu * f$ 的谱间隙得出结论。

定理 B 通过使用引理 5.4 和概率论证从定理 C 推出。定理 A 的收敛部分则是定理 B（取 $\Lambda = \mathrm{SL}_2(\mathbb{Z})$）和 [25, 定理 9.1] 的直接推论。发散部分通过定理 B 关于双重等分布的一个细化版本获得，该版本受 [31] 的启发，并建立在 Schmidt [47] 对经典定量 Khintchine 定理的原始证明之上。

**允许 $\lambda$ 具有无限支撑**。我们的方法允许稍微更一般的陈述，将上述 Khintchine 二分法和等分布结果推广到由可能具有无限支撑的随机 IFS 产生的测度，只要满足有限指数矩条件。

令 $\mathrm{Aff}(\mathbb{R})$ 表示 $\mathbb{R}$ 的仿射群。对每个 $\phi \in \mathrm{Aff}(\mathbb{R})$，记 $\mathbf{r}_{\phi}\in \mathbb{R}^{*}$ 和 $\mathbf{b}_{\phi}\in \mathbb{R}$ 为唯一的数使得

$$\phi(t) = \mathbf{r}_{\phi} t + \mathbf{b}_{\phi}, \quad \forall t\in \mathbb{R}. \quad (1.5)$$

我们称 $\mathrm{Aff}(\mathbb{R})$ 上的概率测度 $\lambda$ 具有有限指数矩，如果存在 $\epsilon > 0$ 使得

$$\int_{\mathrm{Aff}(\mathbb{R})} \bigl( |\mathbf{r}_{\phi}|^{\epsilon} + |\mathbf{r}_{\phi}^{-1}|^{\epsilon} + |\mathbf{b}_{\phi}|^{\epsilon} \bigr) \, \mathrm{d}\lambda(\phi) < \infty. \quad (1.6)$$

**定理 A'**。设 $\lambda$ 是 $\mathrm{Aff}(\mathbb{R})$ 上的一个具有有限指数矩的概率测度，且 $\mathrm{supp}\lambda$ 没有全局不动点。设 $\sigma$ 是 $\mathbb{R}$ 上的一个满足 $\lambda * \sigma = \sigma$ 的概率测度。那么 $\sigma$ 满足 Khintchine 二分法 (1.3)。

===== 第 6 页 =====

**定理 B'**。在相同的假设下，$\sigma$ 满足方程 (1.4) 中关于膨胀平移的有效等分布。

回顾 $G$ 上的概率测度 $\mu$ 具有有限指数矩，如果存在 $\epsilon > 0$，使得

$$\int_{G} \| g\|^{\epsilon} \, \mathrm{d}\mu(g) < \infty. \quad (1.7)$$

**定理 C'**。当定理 C 中关于 $\mu$ 的有限支撑假设放宽为有限指数矩条件时，定理 C 仍然成立。

**论文结构**。在第 2 节中，我们为论文的其余部分固定符号，介绍自相似测度的矩和非浓度估计，并回顾 $X$ 上 $\mu$-游走的一些回复性质。在第 3 节中，我们推导出 $\mu^{*n}*\delta_x$ 在指数小尺度下的正维数。在第 4 节中，我们对维数进行自举，直到它达到任意接近 $3 = \dim X$ 的数。在第 5 节中，我们推导出等分布结论，即定理 B' 和定理 C'。在第 6 节中，我们将定理 B' 提升为双重等分布结论。在第 7 节中，我们证明每个满足某些等分布性质的 $\mathbb{R}$ 上概率测度的 Khintchine 二分法，从而特别推出定理 A'。

**致谢**。作者感谢 Nicolas de Saxcé 分享他对随机游走和丢番图逼近的见解，以及 Tushar Das、Shreyasi Datta、Larry Guth、Osama Khalil、Dmitry Kleinbock、Manuel Luethi、David Simmons、Sanju Velani 和匿名审稿人对本文早期版本提出的许多有益评论。W.H. 和 H.Z. 感谢 Barak Weiss 的启发性讨论。H.Z. 感谢石荣刚的鼓励。

## 2. 预备知识

在本节中，我们设定符号并收集对论文其余部分有用的基本事实。

### 2.1. 符号与约定
在本文中，$G = \mathrm{SL}_2(\mathbb{R})$，$\Lambda \subseteq G$ 是一个格子，$X = G / \Lambda$。

**度量**。我们在李代数 $\mathfrak{g} = \mathrm{Lie}(G)$ 中固定一个基 $(e_{-}, e_{0}, e_{+})$ 如下：

$$
e_{-} = \begin{pmatrix} 0 & 1 \\ 0 & 0 \end{pmatrix}, \quad e_{0} = \frac{1}{2} \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \quad e_{+} = \begin{pmatrix} 0 & 0 \\ 1 & 0 \end{pmatrix}.
$$

我们始终假设 $G$ 赋予了唯一的右不变黎曼度量，使得 $(e_{-}, e_{0}, e_{+})$ 是标准正交的。这诱导了 $G$ 和商空间 $X$ 上的一个距离，我们统称为 dist。给定 $\rho > 0$，记 $B_{\rho}$ 为 $G$ 中以单位元 $\mathrm{Id}$ 为中心、半径为 $\rho > 0$ 的开球。那么 $X$ 中以 $x$ 为中心、半径为 $\rho$ 的开球就等于 $B_{\rho} x$。

$X$ 在点 $x$ 处的单射半径为

$$\mathrm{inj}(x) = \sup \{\rho > 0: \text{映射 } B_{\rho} \to X, \; g \mapsto gx \text{ 是单射}\}.$$

[文件内容结束]