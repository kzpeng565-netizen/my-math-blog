---
aliases:
  - 格点拓扑群R/Z
---

# 1. 商空间与基本表示

**等价关系**：在 $\mathbb R$ 上定义

$$
r\sim s\iff r-s\in\mathbb Z.
$$
数 $r$ 的等价类记作 $r+\mathbb Z=\{r+n:n\in\mathbb Z\}$，所有等价类组成商空间

$$
\mathbb T=\mathbb R/\mathbb Z.
$$
定义自然商映射 $q:\mathbb R\to\mathbb T$，$q(r)=r+\mathbb Z$。

**商拓扑**：在 $\mathbb T$ 上赋予由 $q$ 诱导的商拓扑，即 $U\subseteq\mathbb T$ 是开集，当且仅当 $q^{-1}(U)$ 是 $\mathbb R$ 中的开集。

**基本域**：每个等价类都存在唯一代表元 $t\in[0,1)$，所以 $[0,1)$ 是 $\mathbb Z$ 在 $\mathbb R$ 上平移作用的基本域。若使用 $[0,1]$，则代表元不唯一，因为 $0+\mathbb Z=1+\mathbb Z$。

**几何表示**：$\mathbb T$ 可以看作将区间 $[0,1]$ 的两个端点粘合起来得到的圆。

# 2. 圆上的度量

**定义**：在 $\mathbb T$ 上定义

$$
d(r+\mathbb Z,s+\mathbb Z)=\min_{m\in\mathbb Z}|r-s+m|.
$$
它表示在 $s$ 的所有整数平移中选取一个与 $r$ 距离最近的代表元。等价地，

$$
d(q(r),q(s))=\operatorname{dist}(r-s,\mathbb Z),
$$
因此总有 $0\le d(x,y)\le\frac12$。

**例子**：$d(0.9+\mathbb Z,0.1+\mathbb Z)=0.2$。在圆上从 $0.9$ 跨过端点到 $0.1$ 的距离是 $0.2$，而不是 $0.8$。

## 2.1 度量的良定义性与三角不等式

> [!Note] 结论
> 上述函数 $d$ 与代表元的选取无关，并满足三角不等式，因而给出 $\mathbb T$ 上的度量。

### 2.1.1 证明思路

1. **良定义性**：若更换代表元 $r'=r+k$、$s'=s+\ell$，则
   $r'-s'+m=r-s+(k-\ell+m)$。当 $m$ 遍历 $\mathbb Z$ 时，$k-\ell+m$ 仍遍历整个 $\mathbb Z$，所以最小值不变。
2. **三角不等式**：分别选取整数 $m,n$，使 $r-s+m$ 和 $s-t+n$ 实现对应的最短距离。由于 $m+n\in\mathbb Z$，有

$$
d(r+\mathbb Z,t+\mathbb Z)
\le |r-s+m|+|s-t+n|.
$$

# 3. 度量拓扑与商拓扑

记度量 $d$ 诱导的拓扑为 $\tau_d$，商拓扑为 $\tau_q$。

> [!Note] 结论
> $$
> \tau_d=\tau_q.
> $$

## 3.1 证明思路

分别证明两个包含关系：先利用商映射 $q$ 的连续性得到 $\tau_d\subseteq\tau_q$，再利用 $q^{-1}(U)$ 的开性，在每个点处构造度量开球，得到 $\tau_q\subseteq\tau_d$。

1. **证明 $\tau_d\subseteq\tau_q$**：由

$$
d(q(r),q(s))=\min_{m\in\mathbb Z}|r-s+m|\le |r-s|
$$
可知 $q:\mathbb R\to(\mathbb T,d)$ 是 $1$-Lipschitz 映射，从而连续。若 $U$ 是度量拓扑中的开集，则 $q^{-1}(U)$ 在 $\mathbb R$ 中开；根据商拓扑的定义，$U$ 也是商拓扑中的开集。

   特别地，对任意 $\varepsilon>0$，

$$
q^{-1}(B_d(q(r),\varepsilon))
=\bigcup_{m\in\mathbb Z}(r-m-\varepsilon,r-m+\varepsilon),
$$
这是实线上的开集。

2. **证明 $\tau_q\subseteq\tau_d$**：设 $U$ 是商拓扑中的开集，则 $q^{-1}(U)$ 在 $\mathbb R$ 中开。任取 $q(r)\in U$，存在 $\varepsilon>0$，使

$$
(r-\varepsilon,r+\varepsilon)\subseteq q^{-1}(U).
$$
若 $d(q(r),q(s))<\varepsilon$，则存在 $m\in\mathbb Z$ 使 $|r-s+m|<\varepsilon$，于是

$$
s-m\in(r-\varepsilon,r+\varepsilon)\subseteq q^{-1}(U).
$$
又因为 $q(s-m)=q(s)$，所以 $q(s)\in U$。因此 $B_d(q(r),\varepsilon)\subseteq U$，说明 $U$ 是度量开集。

# 4. $\mathbb T$ 的群结构

**定义**：在 $\mathbb T$ 上定义加法

$$
(r+\mathbb Z)+(s+\mathbb Z)=(r+s)+\mathbb Z.
$$

## 4.1 群运算的良定义性

**证明思路**：若 $r'=r+m$、$s'=s+n$，其中 $m,n\in\mathbb Z$，则 $r'+s'=r+s+(m+n)$，所以

$$
(r'+s')+\mathbb Z=(r+s)+\mathbb Z.
$$

## 4.2 阿贝尔群结构

- **单位元**：$0+\mathbb Z$；
- **逆元**：$-(r+\mathbb Z)=(-r)+\mathbb Z$；
- **结合律与交换律**：来自 $\mathbb R$ 上的加法。

> [!Note] 结论
> $\mathbb T$ 是阿贝尔群。

更抽象地说，$(\mathbb R,+)$ 是阿贝尔群，$\mathbb Z$ 是其子群；阿贝尔群的任意子群都是正规子群，因此可以构造商群 $\mathbb R/\mathbb Z$。

# 5. $\mathbb T$ 的紧致性

> [!Note] 结论
> $\mathbb T$ 是紧空间。

## 5.1 证明思路

考虑商映射在闭区间上的限制

$$
q|_{[0,1]}:[0,1]\to\mathbb T.
$$
每个等价类都有一个位于 $[0,1]$ 中的代表元，所以 $q([0,1])=\mathbb T$。由于 $[0,1]$ 是紧空间，$q$ 连续，而连续映射保持紧致性，因此 $\mathbb T$ 是紧空间。

**说明**：这里使用 $[0,1]$ 而不是基本域 $[0,1)$，因为 $[0,1)$ 在 $\mathbb R$ 中并不紧。虽然 $0$ 和 $1$ 在 $[0,1]$ 中是两个点，但在商空间中被映到同一个点。

# 6. 拓扑群结构

## 6.1 拓扑群的定义

**定义**：拓扑群是一个同时具有群结构和拓扑结构的集合 $G$，并且群运算与拓扑相容。

- 对于乘法群，要求乘法映射 $\mu:G\times G\to G$，$(x,y)\mapsto xy$ 连续，并且取逆映射 $\iota:G\to G$，$x\mapsto x^{-1}$ 连续。
- 对于加法群，条件写为 $+:G\times G\to G$，$(x,y)\mapsto x+y$ 连续，并且取负映射 $-:G\to G$，$x\mapsto-x$ 连续。

因此，一个集合同时是群和拓扑空间，并不自动意味着它是拓扑群。

## 6.2 $\mathbb T$ 是拓扑群

> [!Note] 结论
> $\mathbb T=\mathbb R/\mathbb Z$ 是紧阿贝尔拓扑群。

### 6.2.1 证明思路

利用圆上的度量，分别证明加法与取负连续。

1. **加法连续**：对于任意 $x,x',y,y'\in\mathbb T$，有

$$
d(x+y,x'+y')\le d(x,x')+d(y,y').
$$
分别选取实现 $d(x,x')$ 和 $d(y,y')$ 的整数平移，将两个整数相加，再使用实数绝对值的三角不等式，即可得到上述估计。因此 $(x,y)\mapsto x+y$ 连续。

2. **取负连续**：由

$$
d(-x,-y)=d(x,y)
$$
可知取负映射是等距映射，从而连续。

# 7. 拓扑群的基本性质

## 7.1 左右平移是同胚

> [!Note] 结论
> 对任意 $a\in G$，左平移与右平移都是同胚。

**证明思路**：固定 $a\in G$，定义左平移 $L_a:G\to G$，$L_a(x)=ax$。映射 $L_a$ 连续，其逆映射是 $L_{a^{-1}}$，也连续，所以 $L_a$ 是同胚。同理，右平移 $R_a(x)=xa$ 也是同胚。

对于加法群，平移写为 $T_a(x)=x+a$。在 $\mathbb T$ 中，平移还是等距映射：

$$
d(x+a,y+a)=d(x,y).
$$
因此，拓扑群在每个点附近的局部拓扑结构相同。

## 7.2 单位元附近的邻域

> [!Note] 结论
> 拓扑群的局部问题可以通过平移化为单位元处的问题。

若 $U$ 是单位元 $e$ 的邻域，则 $xU$ 是 $x$ 的邻域。在加法群中，若 $U$ 是 $0$ 的邻域，则 $x+U$ 是 $x$ 的邻域。

## 7.3 群同态的连续性

> [!Note] 结论
> 设 $\varphi:G\to H$ 是群同态。若 $\varphi$ 在单位元 $e_G$ 处连续，则它在每一点都连续。

**证明思路**：当 $x$ 接近 $x_0$ 时，$x_0^{-1}x$ 接近 $e_G$，并且

$$
\varphi(x)=\varphi(x_0)\varphi(x_0^{-1}x).
$$
利用单位元处的连续性以及 $H$ 中平移的连续性即可得到结论。

## 7.4 常见拓扑群

常见例子包括 $(\mathbb R^n,+)$、$(\mathbb C^\times,\cdot)$、$GL_n(\mathbb R)$、$O(n)$、$SO(n)$、$U(n)$、$\mathbb R/\mathbb Z$，以及任意赋予离散拓扑的群。

# 8. $\mathbb T$ 与单位圆 $S^1$

定义映射

$$
\Phi:\mathbb T\to S^1,\qquad \Phi(t+\mathbb Z)=e^{2\pi it}.
$$

> [!Note] 结论
> $\Phi$ 是拓扑群同构，即
> $$
> \mathbb R/\mathbb Z\cong S^1.
> $$

## 8.1 证明思路

1. **良定义性**：若 $t-s\in\mathbb Z$，则 $e^{2\pi it}=e^{2\pi is}$。
2. **群同态**：

$$
\Phi((s+\mathbb Z)+(t+\mathbb Z))
=e^{2\pi i(s+t)}
=e^{2\pi is}e^{2\pi it}.
$$
因此，$\mathbb T$ 上的加法对应于单位圆上的复数乘法。

3. **同胚性**：$\Phi$ 是连续双射。由于 $\mathbb T$ 紧，而 $S^1\subseteq\mathbb C$ 是 Hausdorff 空间，紧空间到 Hausdorff 空间的连续双射必为同胚。

# 9. 整体结构

这个例子的逻辑顺序是

$$
\mathbb R
\xrightarrow{\text{模 }\mathbb Z}
\mathbb T=\mathbb R/\mathbb Z
\xrightarrow[\cong]{\,t+\mathbb Z\mapsto e^{2\pi it}\,}
S^1.
$$

其中：

1. $\mathbb T$ 是 $\mathbb R$ 按整数平移得到的商空间；
2. 商拓扑等于圆周距离 $d$ 诱导的度量拓扑；
3. 商群加法使 $\mathbb T$ 成为阿贝尔群；
4. 加法和取负连续，所以 $\mathbb T$ 是拓扑群；
5. $\mathbb T$ 是紧区间 $[0,1]$ 的连续像，所以紧；
6. $\mathbb T$ 与通常的单位圆 $S^1$ 拓扑群同构。

> [!Note] 最终结论
> $\mathbb T=\mathbb R/\mathbb Z$ 是一个紧阿贝尔拓扑群，并且与 $S^1$ 同构。
