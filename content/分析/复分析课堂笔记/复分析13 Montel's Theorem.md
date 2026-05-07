---
tags:
  - 复分析
  - 分析
---
# 1. Riemann Mapping Theorem and Montel's Theorem

## 1.1 Riemann Mapping Theorem
**Theorem** (Riemann Mapping theorem)
> [!Riemann Mapping Theorem]
> Every simply connected proper open subset $\Omega \subset \mathbb{C}$ is conformal to the unit disk $\mathbb{D}$.

**Idea of Proof**: Consider all holomorphic maps from $\Omega$ to $\mathbb{D}$ and find an "extreme" element, then show it is a conformal map.

**Definition**: An open subset $\Omega \subset \mathbb{C}$ is called **proper** if $\Omega \neq \mathbb{C}$ and $\Omega \neq \emptyset$.

## 1.2 Normal Families and Related Concepts

### 1.2.1 Definition of a Normal Family
**Definition**: Let $\Omega \subset \mathbb{C}$ be an open set, and $\mathcal{F}$ be a family of holomorphic functions on $\Omega$. We say $\mathcal{F}$ is a **normal family** if every sequence of functions in $\mathcal{F}$ admits a subsequence that converges uniformly on every compact subset of $\Omega$. (The limit function is not required to be in $\mathcal{F}$).
任何$\mathcal{F}$中的函数序列都存在子序列内闭一致收敛

Recall the precise meaning of uniform convergence on compact subsets: A sequence of continuous functions $\{f_{n}\}$ on $\Omega$ converges uniformly to $f$ on every compact subset of $\Omega$ if for any compact $K \subset \Omega$, $\lim_{n\to\infty}(\sup_{z\in K}|f_{n}(z)-f(z)|)=0$.

### 1.2.2 Uniform Boundedness on Compact Subsets
**Definition**: A family $\mathcal{F}$ of functions on $\Omega$ is called **uniformly bounded on compact subsets** if for every compact $K \subset \Omega$, there exists $M_K > 0$ such that $\sup_{z \in K} |f(z)| \leq M_K$ for all $f \in \mathcal{F}$.
在子集上一致有界(弱于一致有界)

**Example**:
Set $f_n(z) = z + \frac{1}{n}$ for all $n \in \mathbb{N}_{>0}, z \in \mathbb{C}$. Then $\{f_n\}$ is uniformly bounded on compact sets of $\mathbb{C}$ because for any compact $K \subset \mathbb{C}$, $\sup_{z\in K}|f_n(z)| \leq \sup_K |z| + 1 < \infty$. However, $\{f_n\}$ is **not** uniformly bounded on all of $\mathbb{C}$.

### 1.2.3 Equicontinuity
**Definition**: A family of functions $\mathcal{F}$ on $\Omega$ is called **equicontinuous on a subset** $K \subset \Omega$ if for every $\varepsilon > 0$, there exists $\delta > 0$ such that for all $f \in \mathcal{F}$ and for all $z_1, z_2 \in K$ with $|z_1 - z_2| < \delta$, we have $|f(z_1) - f(z_2)| < \varepsilon$.
[[微积分02：连续函数空间的紧子集和稠密子集]] 使用了类似的定义


**Theorem** (Montel's Theorem)
> [!Montel's Theorem] 一致有界全纯函数族就是满足紧子集等度连续的正规族
> Assume that $\mathcal{F}$ is a family of holomorphic functions on $\Omega$ which is uniformly bounded on any compact subset.
> Then,
> 1.  $\mathcal{F}$ is equicontinuous on compact sets.
> 2.  $\mathcal{F}$ is a normal family.

## 1.3 Technical Preliminaries: Exhaustion by Compact Sets

**Definition**: Let $\Omega \subset \mathbb{C}$ be an open set. A sequence $\{K_l\}_{l=1,2,\dots}$ of compact subsets of $\Omega$ is called an **exhaustion** if:
1.  $K_l \subset K_{l+1}^\circ$ (i.e., $K_l$ is contained in the interior of $K_{l+1}$).
2.  $\bigcup_{l=1}^{\infty} K_l = \Omega$, which is equivalent to: For any compact $K \subset \Omega$, there exists an $l$ such that $K \subset K_l$.

**Lemma**: Any open $\Omega \subset \mathbb{C}$ admits an exhaustion by compact subsets.
**Proof**:
-   If $\Omega$ is bounded, set $K_l = \{ z \in \Omega \mid \text{dist}(z, \partial \Omega) \geq 1/l \}$.
-   In general (possibly unbounded), set $K_l = \{ z \in \Omega \mid \text{dist}(z, \partial \Omega) \geq 1/l, \text{ and } |z| \leq l \}$.

## 1.4 Proof of Montel's Theorem

### 1.4.1 Proof of Equicontinuity (Part 1)

**Proof (Part 1 - Equicontinuity)**:
Fix a compact subset $K \subset \Omega$. We need to prove $\mathcal{F}$ is equicontinuous on $K$.

**Step 1: Setup and choice of radius**.
Let $r > 0$ be such that $D_{3r}(z) \subset \Omega$ for all $z \in K$. A concrete choice is $r = \frac{1}{3} \text{dist}(K, \partial\Omega) > 0$.
Choose any $z, w \in K$ such that $|z - w| < r$. Note that both $z$ and $w$ lie in $D_r(w)$.

**Step 2: Application of Cauchy's integral formula**.
For any $f \in \mathcal{F}$, we apply Cauchy's integral formula on the circle $C_{2r}(z)$ centered at $z$ with radius $2r$:
$$
f(z) - f(w) = \frac{1}{2\pi i} \left( \int_{C_{2r}(z)} \frac{f(\xi)}{\xi - w} d\xi - \int_{C_{2r}(z)} \frac{f(\xi)}{\xi - z} d\xi \right) = \frac{1}{2\pi i} \int_{C_{2r}(z)} f(\xi) \cdot \frac{z - w}{(\xi - w)(\xi - z)} d\xi.
$$

**Step 3: Estimation of the integral**.
Taking absolute values gives:
$$
|f(w) - f(z)| \leq \frac{1}{2\pi} \int_{C_{2r}(z)} |f(\xi)| \frac{|z - w|}{|\xi - w| |\xi - z|} |d\xi|.
$$
We now bound the terms in the integrand for $\xi \in C_{2r}(z)$:
- $|\xi - z| = 2r$ (by definition of the circle).
- $|\xi - w| \geq |\xi - z| - |z - w| \geq 2r - r = r$ (by the triangle inequality and since $|z-w|<r$).

**Step 4: Using uniform boundedness**.
Define the compact set $K' = \{ \xi \in \Omega \mid \text{dist}(\xi, K) \leq 2r \}$. Since $C_{2r}(z) \subset K'$ for any $z \in K$, and by the uniform boundedness assumption on compact sets, there exists a constant $c > 0$ such that $\sup_{\xi \in K'} |f(\xi)| \leq c$ for **all** $f \in \mathcal{F}$.

**Step 5: Final calculation**.
Substituting these bounds:
$$
|f(w) - f(z)| \leq \frac{1}{2\pi} \int_{C_{2r}(z)} c \cdot \frac{|z - w|}{r \cdot 2r} |d\xi| = \frac{1}{2\pi} \cdot c \cdot \frac{|z - w|}{2r^2} \cdot \text{length}(C_{2r}(z)).
$$
Since $\text{length}(C_{2r}(z)) = 2\pi \cdot 2r = 4\pi r$, we get:
$$
|f(w) - f(z)| \leq \frac{1}{2\pi} \cdot c \cdot \frac{|z - w|}{2r^2} \cdot (4\pi r) = \frac{c}{r} |z - w|.
$$

**Step 6: Verifying equicontinuity**.
The bound $|f(z) - f(w)| \leq \frac{c}{r} |z - w|$ holds for all $f \in \mathcal{F}$ and all $z, w \in K$ with $|z-w| < r$. The constant $\frac{c}{r}$ depends only on $K$ and $\Omega$, not on the specific function $f$.
Therefore, for any $\varepsilon > 0$, choose $\delta = \min \left\{ \frac{\varepsilon \cdot r}{c}, r \right\}$. Then for all $z, w \in K$ with $|z-w| < \delta$ and all $f \in \mathcal{F}$, we have $|f(z) - f(w)| \leq \frac{c}{r} \cdot \delta \leq \varepsilon$.
This proves $\mathcal{F}$ is equicontinuous on $K$.

**Key Insight**: For nested compacts $K \subset K'$, we can control $\sup_K |f'|$ by $\sup_{K'} |f|$ using Cauchy's estimates, with constants depending only on the geometry of $K$ and $K'$, independent of $f$.

### 1.4.2 Proof of Normality (Part 2)

**Proof (Part 2 - Normality)**:
We now prove the implication: $\mathcal{F}$ is equicontinuous on every compact subset + uniformly bounded on every compact set $\implies$ $\mathcal{F}$ is a normal family.

**Step 1: Recall the Arzelà-Ascoli (AA) Theorem**.
If a family of continuous functions is uniformly bounded and equicontinuous on a **specific** compact set $K$, then any sequence in that family has a subsequence that converges uniformly on $K$ to a continuous function.

**Step 2: Strategy using an exhaustion and diagonalization**.
Fix an exhaustion $\{K_l\}_{l \geq 1}$ of $\Omega$ by compact sets (which exists by the Lemma).
Fix an arbitrary sequence $\{f_n\}$ in $\mathcal{F}$.
Our goal is to construct a single subsequence $\{h_n\}$ of $\{f_n\}$ that converges uniformly on **every** $K_l$. Since any compact $K \subset \Omega$ is contained in some $K_l$, this subsequence will then converge uniformly on all compact subsets of $\Omega$.

**Step 3: Constructing convergent subsequences on each $K_l$**.
-   On $K_1$: The family $\mathcal{F}$ is uniformly bounded and equicontinuous on the compact set $K_1$. Apply the AA theorem to the sequence $\{f_n\}$ to extract a subsequence $\{f_{n,1}\}_{n \geq 1}$ that converges uniformly on $K_1$ to a continuous limit function $g_1$.
-   On $K_2$: Consider the sequence $\{f_{n,1}\}$ (which is a subsequence of the original). This sequence is also in $\mathcal{F}$, and $\mathcal{F}$ is uniformly bounded and equicontinuous on $K_2$. Apply the AA theorem again to extract a further subsequence $\{f_{n,2}\}_{n \geq 1}$ of $\{f_{n,1}\}$ that converges uniformly on $K_2$ to a limit $g_2$. Since $\{f_{n,2}\}$ is a subsequence of $\{f_{n,1}\}$, its limit on $K_1$ must agree with $g_1$, so $g_2|_{K_1} = g_1$.
-   **Inductive Step**: Assume we have constructed a sequence $\{f_{n,l}\}$ converging uniformly on $K_l$ to $g_l$. On $K_{l+1}$, apply the AA theorem to $\{f_{n,l}\}$ to extract a subsequence $\{f_{n,l+1}\}$ converging uniformly on $K_{l+1}$ to a limit $g_{l+1}$. By construction, $g_{l+1}|_{K_l} = g_l$.

**Step 4: The diagonal sequence**.
Now define the "diagonal" sequence: $h_n = f_{n,n}$.
We claim $\{h_n\}$ converges uniformly on every $K_L$.
Proof of the claim: Fix an index $L \geq 1$. For any $n \geq L$, the element $h_n = f_{n,n}$ belongs to the set $\{f_{1,L}, f_{2,L}, f_{3,L}, \dots\}$ because when we take the diagonal, for $n \geq L$, the $n$-th term of the diagonal comes from the $n$-th term of the sequence constructed at the $L$-th step or later. More formally, for $n \geq L$, $f_{n,n}$ is a member of the subsequence $\{f_{n,L}\}_{n \geq L}$. Therefore, $\{h_n\}_{n \geq L}$ is a subsequence of $\{f_{n,L}\}_{n \geq L}$, which converges uniformly to $g_L$ on $K_L$. Hence, $\{h_n\}$ itself converges uniformly to $g_L$ on $K_L$.

**Step 5: Properties of the limit function**.
Define a function $g: \Omega \to \mathbb{C}$ by $g(z) = g_l(z)$ for any $l$ such that $z \in K_l$. The consistency condition $g_{l+1}|_{K_l} = g_l$ ensures $g$ is well-defined. The construction shows $g$ is continuous on $\Omega$ (as it is the uniform limit of continuous functions on each compact set).
Since $\{h_n\}$ is a sequence of **holomorphic** functions converging uniformly on compact subsets of $\Omega$ to $g$, a standard theorem in complex analysis (e.g., Chapter 2, Theorem 5.2 in the notes) implies that the limit function $g$ is also holomorphic on $\Omega$.

This completes the proof that $\mathcal{F}$ is a normal family.

## 1.5 A Property of Limits of Sequences of Injective Functions

**Property**: Let $\Omega \subset \mathbb{C}$ be open, and $\{f_n\}$ a sequence of holomorphic functions on $\Omega$ converging to a limit $f$ uniformly on any compact set. If every $f_n$ is injective, then $f$ is either injective or constant.

**Proof**:
Assume for contradiction that $f$ is **not** injective and **not** constant.

**Step 1: Setup**.
Since $f$ is not injective, there exist distinct points $z_1 \neq z_2 \in \Omega$ such that $f(z_1) = f(z_2)$.
Define a new sequence $g_n(z) = f_n(z) - f_n(z_1)$. Then:
- Each $g_n$ is holomorphic and injective (since $f_n$ is injective).
- $g_n(z_1) = 0$ for all $n$.
- $g_n$ converges uniformly on compact sets to $g(z) = f(z) - f(z_1)$.
- By our assumption, $g(z_1) = g(z_2) = 0$, and $g$ is not identically zero (since $f$ is not constant).

**Step 2: Isolating the zero $z_2$ of $g$**.
Since $g$ is holomorphic and non-constant, its zeros are isolated. Therefore, we can choose a circle $\gamma$ centered at $z_2$ with sufficiently small radius such that:
1.  $\gamma$ and its interior are contained in $\Omega$.
2.  $g$ has no other zeros inside or on $\gamma$ except at $z_2$.
Let $K$ denote the compact set consisting of $\gamma$ and its interior.
By continuity of $g$ and compactness of $\gamma$, there exists $\lambda > 0$ such that $|g(z)| \geq \lambda$ for all $z \in \gamma$.

**Step 3: Uniform convergence near $\gamma$**.
Since $g_n \to g$ uniformly on the compact set $K$ (which contains $\gamma$), there exists an integer $N > 0$ such that for all $n \geq N$ and all $z \in \gamma$:
$$
|g_n(z) - g(z)| \leq \lambda / 2.
$$
By the reverse triangle inequality, for $n \geq N$ and $z \in \gamma$:
$$
|g_n(z)| \geq |g(z)| - |g_n(z) - g(z)| \geq \lambda - \lambda/2 = \lambda/2 > 0.
$$
Thus, for $n \geq N$, $g_n$ has **no zeros on $\gamma$**.

**Step 4: Applying the Argument Principle**.
The number of zeros of $g_n$ inside $\gamma$ (counted with multiplicity) is given by the integral:
$$
\frac{1}{2\pi i} \int_\gamma \frac{g_n'(z)}{g_n(z)} dz.
$$
We know two things:
1.  Since $f_n$ (and hence $g_n$) is injective, $g_n$ has exactly one zero in $\Omega$, which is at $z_1$. If $\gamma$ is chosen small enough so that $z_1$ is **not** inside $\gamma$, then $g_n$ should have **zero** zeros inside $\gamma$ for all $n$.
2.  We can also examine the limit of this integral. Since $g_n \to g$ and $g_n' \to g'$ uniformly on compact sets (by Weierstrass' theorem on uniform convergence of derivatives), the integrands converge uniformly on $\gamma$: $\frac{g_n'}{g_n} \to \frac{g'}{g}$. Therefore,
    $$
    \lim_{n \to \infty} \frac{1}{2\pi i} \int_\gamma \frac{g_n'(z)}{g_n(z)} dz = \frac{1}{2\pi i} \int_\gamma \frac{g'(z)}{g(z)} dz.
    $$
    The right-hand side is the number of zeros of $g$ inside $\gamma$ (counted with multiplicity), which is at least 1 (due to the zero at $z_2$).

**Step 5: Deriving the contradiction**.
From point 2 above, the limit of the integrals is positive. Hence, there exists an integer $M \geq N$ such that for all $n \geq M$:
$$
\frac{1}{2\pi i} \int_\gamma \frac{g_n'(z)}{g_n(z)} dz > 0.
$$
This implies that for $n \geq M$, $g_n$ has at least one zero inside $\gamma$. However, from point 1, if $\gamma$ is chosen not to contain $z_1$, then $g_n$ should have no zeros inside $\gamma$ (as its only zero is at $z_1$). This is a contradiction.

**Conclusion**: Our initial assumption that $f$ is neither injective nor constant must be false. Therefore, $f$ is either injective or constant.

**Main Idea of Proof**: If a non-constant limit $f$ were not injective, the Argument Principle would force the injective approximants $f_n$ to have extra zeros near the points where $f$ fails injectivity, contradicting their injectivity.