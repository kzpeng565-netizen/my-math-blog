[文件名称]: 有限生成Abel群-Smith form.pdf

[文件内容开始]

===== 第 1 页 =====

**有限生成阿贝尔群速成课**

一个阿贝尔群被称为**有限生成**的，如果它的每个元素都可以通过取一个称为生成集的有限子集中元素的（整数倍）和来得到。一个有限生成阿贝尔群 $G$ 是**自由**的，如果存在某个生成集 $\{g_{1},\ldots ,g_{n}\}$，使得 $\Sigma_{i = 1}^{n}k_{i}g_{i} = 0$ 当且仅当所有 $k_{i} = 0$。此时，该生成集称为**基**，$n$ 称为 $G$ 的**秩**。有限生成自由阿贝尔群的任何子群也是有限生成自由阿贝尔群，其秩小于或等于原群的秩。每个非平凡的有限生成自由阿贝尔群都同构于某个整数 $n\geq 1$ 对应的 $\mathbb{Z}^{n}$，并且这些群都是互不相同的。

注意，$\mathbb{Z} / 3\mathbb{Z} = \{[0],[1],[2]\}$ 不是自由群。（方括号表示等价类。）集合 $\{[1]\}$ 生成它，但不是基。例如，$[2] = 2\cdot [1] = 4\cdot [1]$，因此我们没有唯一性。可以证明，对于任何生成子集都会发生这种情况。

设 $A$ 是一个 $m\times n$ 整数矩阵。那么 $A:\mathbb{Z}^{n}\to \mathbb{Z}^{m}$ 是一个同态。其像，记作 $A\mathbb{Z}^{n}$，是 $\mathbb{Z}^{m}$ 的一个子群。因此，商群 $\mathbb{Z}^{m} / A\mathbb{Z}^{n}$ 是良定义的。可以证明，每个有限生成阿贝尔群都同构于某个（不唯一的）整数矩阵 $A$ 对应的 $\mathbb{Z}^{m} / A\mathbb{Z}^{n}$。

存在一个著名的算法来判断 $\mathbb{Z}^{m} / A\mathbb{Z}^{n}$ 和 $\mathbb{Z}^{k} / B\mathbb{Z}^{p}$ 是否同构。它涉及应用行和列操作将每个矩阵化为规范形式。允许的操作如下：

(1) 交换两行（或两列）。
(2) 将一行（或一列）乘以 $-1$。
(3) 将一行（或一列）的倍数加到另一行（或另一列）。

如果 $A$ 和 $B$ 是同尺寸的方阵，这些操作就足够了。目前先这样假设。

允许行操作的动机应该是清楚的。它们完全类似于在像 $\mathbb{R}$ 这样的域上解方程组时允许的行操作。但是，我们不能乘以除了 $\pm 1$ 之外的整数，因为这可能会影响结果。例如，$\mathbb{Z} / 2\mathbb{Z}$ 不同构于 $\mathbb{Z} / 3\mathbb{Z}$，但等于 $\mathbb{Z} / (- 2)\mathbb{Z}$。（注意环 $\mathbb{Z}$ 的单位只是 $\pm 1$，而 $\mathbb{R}$ 的单位是所有非零实数。）每个列操作对应于生成元的一个改变。当你在 $\mathbb{R}$ 上解方程组时，变量名可能具有物理意义，如时间或压力。因此，交换它们会改变解空间。但我们的生成元没有特殊意义，因此允许这三种列操作。

可以证明，使用 (1)、(2) 和 (3)，任何方整数矩阵都可以化为对角形式：

$$\left[ \begin{array}{cccc}d_1 & & & \\ & \ddots & & \\ & & d_n \end{array} \right]$$

===== 第 2 页 =====

使得 $d_{1}|d_{2}$ , $d_{2}|d_{3}$，依此类推。这称为**史密斯标准型**。你的教材给出了一个标准的算法来实现这一点。我将用 $A \hookrightarrow B$ 表示 $B$ 可以通过允许的操作从 $A$ 推导出来。一旦我们得到一个史密斯标准型矩阵，就很容易理解相应群的结构。

**例子**

1. 设 $A = \begin{bmatrix} 2 & -2 & -4\\ 4 & 0 & -8\\ 4 & 20 & 12 \end{bmatrix}$。那么，$A \hookrightarrow \begin{bmatrix} 2 & -2 & -4\\ 0 & 4 & 0\\ 0 & 24 & 20 \end{bmatrix} \hookrightarrow \begin{bmatrix} 2 & 0 & 0\\ 0 & 4 & 0\\ 0 & 0 & 20 \end{bmatrix}$。因此，$\frac{\mathbb{Z}^3}{A\mathbb{Z}^3} \cong \mathbb{Z} / 2\mathbb{Z} \oplus \mathbb{Z} / 4\mathbb{Z} \oplus \mathbb{Z} / 20\mathbb{Z}$。

2. 设 $B = \begin{bmatrix} 1 & 2 & 0\\ 3 & 0 & -1\\ 0 & 0 & 0 \end{bmatrix}$。那么，如你所验证的，$B \hookrightarrow \begin{bmatrix} 1 & 0 & 0\\ 0 & 1 & 0\\ 0 & 0 & 0 \end{bmatrix}$。因此，$\frac{\mathbb{Z}^3}{B\mathbb{Z}^3} \cong \mathbb{Z} / \mathbb{Z} \oplus \mathbb{Z} / \mathbb{Z} \oplus \mathbb{Z} / 0\mathbb{Z} \cong \mathbb{Z}$。

3. 设 $C = \begin{bmatrix} 1 & -6 & 8 & 6 & 2\\ 0 & 3 & 0 & 0 & 0\\ 0 & 0 & 4 & 3 & 1\\ 0 & 0 & 2 & 3 & 1\\ 1 & 3 & 4 & 6 & 2 \end{bmatrix}$。经过一些计算，其史密斯标准型为：

$$\begin{bmatrix} 1 & 0 & 0 & 0 & 0\\ 0 & 1 & 0 & 0 & 0\\ 0 & 0 & 1 & 0 & 0\\ 0 & 0 & 0 & 6 & 0\\ 0 & 0 & 0 & 0 & 0 \end{bmatrix}$$

因此，$\frac{\mathbb{Z}^5}{C\mathbb{Z}^5} \cong \mathbb{Z} / \mathbb{Z} \oplus \mathbb{Z} / \mathbb{Z} \oplus \mathbb{Z} / \mathbb{Z}\oplus \mathbb{Z} / 6\mathbb{Z} \oplus \mathbb{Z} / 0\mathbb{Z} \cong \mathbb{Z} / 6\mathbb{Z} \oplus \mathbb{Z}$。

你应该能看到，史密斯标准型中的 1 产生一个平凡因子，0 产生一个 $\mathbb{Z}$ 因子，而整数 $d > 1$ 产生一个 $\mathbb{Z} / d\mathbb{Z}$ 因子。

利用史密斯标准型可以证明，任何有限生成阿贝尔群都可以写成以下形式：

$$G\cong \mathbb{Z} / d_{1}\mathbb{Z}\oplus \dots \oplus \mathbb{Z} / d_{n}\mathbb{Z}\cong \mathbb{Z}^{b}\oplus \mathbb{Z} / d_{1}\mathbb{Z}\oplus \dots \oplus \mathbb{Z} / d_{k}\mathbb{Z},$$

其中 $d_{i}|d_{i + 1}$，且所有 $d_{i} \neq 1$。整数 $b = n - k$ 是等于零的 $d_{i}$ 的个数，称为**贝蒂数**，$T = \mathbb{Z} / d_{1}\mathbb{Z} \oplus \dots \oplus \mathbb{Z} / d_{k}\mathbb{Z}$ 称为**挠子群**，

===== 第 3 页 =====

非零的 $d_{i}$ 称为**挠系数**。这些数 $b,d_{1},\ldots ,d_{k}$ 完全决定了 $G$ 的同构类。

下面的矩阵操作也很有用。如果第 $i$ 行和第 $i$ 列除了对角线上的 1 之外全为零，那么它们可以被删除而不改变对应的群。也就是说，假设 $B$ 是以这种方式从 $A$ 得到的，且 $A$ 是 $n\times n$ 的。那么

$$\frac{\mathbb{Z}^n}{A\mathbb{Z}^n}\cong \frac{\mathbb{Z}^{n - 1}}{B\mathbb{Z}^{n - 1}}.$$

因此，方整数矩阵 $A$ 和 $B$ 即使大小不同，也可以给出同构的群。

对于非方阵，很容易转换为等价的方阵。我们给出两个这样的例子。

**例子**

4. 注意

$$\begin{bmatrix} a & b & 0\\ c & d & 0 \end{bmatrix}:\mathbb{Z}^3\to \mathbb{Z}^2\qquad \mathrm{和}\qquad \begin{bmatrix} a & b\\ c & d \end{bmatrix}:\mathbb{Z}^2\to \mathbb{Z}^2$$

在 $\mathbb{Z}^2$ 中有相同的像。

5. 同样，

$$\begin{bmatrix} a & b & c\\ d & e & f\\ 0 & 0 & 0 \end{bmatrix}:\mathbb{Z}^3\to \mathbb{Z}^3\qquad \mathrm{和}\qquad \begin{bmatrix} a & b\\ d & e\\ 0 & 0 \end{bmatrix}:\mathbb{Z}^2\to \mathbb{Z}^3$$

在 $\mathbb{Z}^3$ 中有相同的像。

如果列数多于行数，则使用列操作清除额外的列，然后删除它们。如果行数多于列数，则添加零列以使矩阵成为方阵。

**练习**

1. 证明 $\begin{bmatrix} 2 & 0\\ 0 & 3 \end{bmatrix}$ 的史密斯标准型是 $\begin{bmatrix} 1 & 0\\ 0 & 6 \end{bmatrix}$。这证明了 $\mathbb{Z} / 2\mathbb{Z}\oplus$ $\mathbb{Z} / 3\mathbb{Z}\cong \mathbb{Z} / 6\mathbb{Z}$。请直接验证这一点。

2. 尝试证明 $\begin{bmatrix} 2 & 0\\ 0 & 4 \end{bmatrix}$ 等价于 $\begin{bmatrix} 1 & 0\\ 0 & 8 \end{bmatrix}$。你做不到！直接证明 $\mathbb{Z} / 2\mathbb{Z}\oplus \mathbb{Z} / 4\mathbb{Z}\neq \mathbb{Z} / 8\mathbb{Z}$。

===== 第 4 页 =====

在计算同调群时，我们常常需要求 $G / H$，其中 $G$ 是自由阿贝尔群，$H$ 是由基或生成集指定的子群。例如，如果 $G = \mathbb{Z}^{3}$ 且 $H$ 有基 $\{(1,0,0)\}$，那么模掉 $H$ 将产生一个同构于 $\mathbb{Z}^{2}$ 的群。但 $H$ 如何嵌入 $G$ 中可能并不明显。下面的定理处理了这一点。

**定理**。设 $G$ 是一个具有基 $\{g_{1},\ldots ,g_{k}\}$ 的自由阿贝尔群。设 $H$ 是一个具有生成集 $\{h_{1},\ldots ,h_{p}\}$ 的子群。令

$$h_{j} = \Sigma_{i = 1}^{k}n_{ij}g_{i},\quad j = 1,\ldots ,p.$$

令 $N$ 为 $k\times p$ 矩阵 $[n_{ij}]$；如果 $p< k$，可以通过添加 $k - p$ 列零来增广 $N$，使得 $N$ 成为方阵。那么

$$G / H\cong \frac{\mathbb{Z}^k}{N\mathbb{Z}^k}.$$

**例子**

5. 设 $G = \langle g_{1},g_{2},g_{3}\rangle$ 且 $H = \langle h_{1},h_{2}\rangle$，其中 $h_{1} = 2g_{1} + g_{2} - g_{3}$ 且 $h_{2} = g_{1} + 5g_{2} + g_{3}$。求 $G / H$ 的同构类。

我们令 $N = \begin{bmatrix} 2 & 1 & - 1\\ 1 & 5 & 1\\ 0 & 0 & 0 \end{bmatrix}$。史密斯标准型为 $\begin{bmatrix} 1 & 0 & 0\\ 0 & 3 & 0\\ 0 & 0 & 0 \end{bmatrix}$。因此 $G / H\cong \mathbb{Z}\oplus \mathbb{Z} / 3\mathbb{Z}$。

6. 设 $G = \langle a,b,c,d\rangle$ 且 $H = \langle a + b,2b + c,a + 3b + c,a - d,b + d\rangle$。注意我们为 $H$ 指定了太多生成元，因此我们没有基。我们可以进行列操作，通过消除冗余生成元来推导出一个基，然后找到史密斯标准型。但是，由于获得一个基所需的列操作是求史密斯标准型时允许的步骤，我们不妨跳过第一步，直接计算史密斯标准型。

令 $N = \begin{bmatrix} 1 & 0 & 1 & 1 & 0\\ 1 & 2 & 3 & 0 & 1\\ 0 & 1 & 1 & 0 & 0\\ 0 & 0 & 0 & - 1 & 1 \end{bmatrix}$。史密斯标准型是 $\begin{bmatrix} 1 & 0 & 0 & 0 & 0\\ 0 & 1 & 0 & 0 & 0\\ 0 & 0 & 0 & 0 & 0\\ 0 & 0 & 0 & 0 & 0 \end{bmatrix}$。因此 $G / H\cong \mathbb{Z}^{2}$。

下面的定理也很有用。

**定理**。设 $A$ 是一个方整数矩阵且 $G = \mathbb{Z}^{n} / A\mathbb{Z}^{n}$。令 $|G|$ 表示 $G$ 的阶。那么我们有

$$|G| = \left\{ \begin{array}{cc}|\operatorname {det}(A)| & \mathrm{if}\ \operatorname {det}(A)\neq 0, \\ \infty & \mathrm{if}\ \operatorname {det}(A) = 0. \end{array} \right.$$

===== 第 5 页 =====

**参考文献**

- *Elements of Algebraic Topology*, Munkres, §§4 & 11。
- *Rings, Modules and Linear Algebra*, Hartley & Hawkes, Chapter 10。
- *Computational Homology*, Kaczynski et al.
  © 2014, Michael C. Sullivan，可用于非营利性教育目的。

[文件内容结束]