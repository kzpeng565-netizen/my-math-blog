---
tags:
  - 抽象代数
  - 代数
---

## 1.1 The Schreier Theorem

**Subnormal** (or **subinvariant**) series of a group
$G$ is a finite sequence $H_0, H_1, \cdots, H_n$ of subgroups of $G$ such that $H_i < H_{i+1}$ and $H_i$ is a normal subgroup of $H_{i+1}$ with $H_0 = \{e\}$ and $H_n = G$. A **normal** (or **invariant**series of} $G$ is a finite sequence $H_0, H_1, \cdots, H_n$ of normal subgroups of $G$ such that $H_i < H_{i+1}, H_0 = \{e\}$, and $H_n = G$.

 A subnormal (normal) series $(K_j)$ is a **refinement of a subnormal (normal) series**  $\{H_i\}$ of a group $G$ if $\{H_i\} \subseteq (K_j)$, that is, if each $H_i$ is one of the $K_j$.
### 1.1.1 Zassenhaus Lemma
> [!Note] Zassenhaus Lemma
> Let $H,K \leq G$ be subgroups and $H^* \leq H,K^* \leq K$ be normal subgroups of $H$ and $K$, respectively. Then
>1. $H^*(H \cap K^*)$ is a normal subgroup of $H^*(H \cap K)$,
>2. $K^*(H^* \cap K)$ is a normal subgroup of $K^*(H \cap K)$, and
>3. The factor groups $H^*(H \cap K)/H^*(H \cap K^*)$, $K^*(H \cap K)/K^*(H^* \cap K)$, and $(H \cap K)/(H^* \cap K)(H \cap K^*)$ are all isomorphic.

![[Pasted image 20251025222444.png|500]]

### 1.1.2  The Schreier Theorem and Proof
> [!Note] The Schreier Theorem and Proof 
>two series of groups must have isomorphic refinement

 Let $G$ be a group and let
$$\begin{align*}
(e) = H_0 < H_1 < H_2 < \cdots < H_n = G
\end{align*}$$
and
$$\begin{align*}
(e) = K_0 < K_1 < K_2 < \cdots < K_m = G
\end{align*}$$
 be two subnormal series for $G$. For $i$ where $0 \leq i \leq n-1$, form the chain of groups
$$\begin{align*}
H_i = H_i(H_{i+1} \cap K_0) \leq H_i(H_{i+1} \cap K_1) \leq \cdots \leq H_i(H_{i+1} \cap K_m) = H_{i+1}.
\end{align*}$$
This inserts $m - 1$ not necessarily distinct groups between $H_i$ and $H_{i+1}$. If we do this for each $i$ where $0 \leq i \leq n - 1$ and let $H_{ij} = H_i(H_{i+1} \cap K_j)$, then we obtain the chain of groups
$$\begin{align*}
\{e\} = H_{0,0} \leq H_{0,1} \leq H_{0,2} \leq \cdots \leq H_{0,m-1} \leq H_{1,0}
\end{align*}$$
$$\begin{align*}
&\leq H_{1,1} \leq H_{1,2} \leq \cdots \leq H_{1,m-1} \leq H_{2,0}
\end{align*}$$
$$\begin{align*}
&\leq H_{2,1} \leq H_{2,2} \leq \cdots \leq H_{2,m-1} \leq H_{3,0}
\end{align*}$$
$$\begin{align*}
&\leq H_{n-1,1} \leq H_{n-1,2} \leq \cdots \leq H_{n-1,m-1} \leq H_{n-1,m}\quad (3)
\end{align*}$$
This chain (3) contains $nm + 1$ not necessarily distinct groups, and $H_{l,0} = H_l$ for each $i$. By the Zassenhaus Lemma, chain (3) is a subnormal chain, that is, each group is normal in the following group. This chain refines the series (1).

In a symmetric fashion, we set $K_{j,l} = K_j(K_{j+1} \cap H_l)$ for $0 \leq j \leq m - 1$ and $0 \leq i \leq n$. This gives a subnormal chain
$$\begin{align*}
\{e\} &= K_{0,0} \leq K_{0,1} \leq K_{0,2} \leq \cdots \leq K_{0,n-1} \leq K_{1,0} \\
&\leq K_{1,1} \leq K_{1,2} \leq \cdots \leq K_{1,n-1} \leq K_{2,0} \\
&\leq K_{2,1} \leq K_{2,2} \leq \cdots \leq K_{2,n-1} \leq K_{3,0} \\
&\leq K_{m-1,1} \leq K_{m-1,2} \leq \cdots \leq K_{m-1,n-1} \leq K_{m-1,n} \\
&= G.
\end{align*}$$
 This chain (4) contains $mn + 1$  not necessarily distinct groups, and $K_{j,0} = K_j$ for each $j$.

This chain refines the series (2).

By the Zassenhaus Lemma 18.10, we have
$$\begin{align*}
H_l(H_{i+1} \cap K_{j+1}) H_l(H_{i+1} \cap K_j) \simeq K_l(K_{j+1} \cap H_{i+1}) / K_j(K_{j+1} \cap H_i),
\end{align*}$$
or
$$\begin{align*}
H_{i,j+1}/H_{i,j} \simeq K_{j,i+1}/K_{j,i} \tag{5}
\end{align*}$$
for $0 \leq i \leq n-1$ and $0 \leq j \leq m-1$. The isomorphisms of relation (5) give a one-toone correspondence of isomorphic factor groups between the subnormal chains (3) and (4). To verify this correspondence, note that $H_{l,0} = H_l$ and $H_{l,m} = H_{l+1}$, while $K_{j,0} = K_j$ and $K_{j,0} = K_{j+1}$. Each chain in (3) and (4) contains a rectangular array of $mn$  symbols $\leq$.
解释:
群论的 Schreier 定理证明中，公式 (5)：
$$
H_{i,j+1}/H_{i,j} \simeq K_{j,i+1}/K_{j,i} \tag{5}
$$

- 链 (3) 和 (4) 是通过在原始系列 (1) 和 (2) 之间插入群构造的，形成了一個矩形阵列（rectangular array），包含 $mn$ 个 $\leq$ 符号（每个符号代表一个子群包含关系）。
- 每个 $\leq$ 对应一个因子群（即商群 $H_{i,j+1}/H_{i,j}$ 或 $K_{j,i+1}/K_{j,i}$）。
- 具体来说：
  - 链 (3) 中，第 $r$ 行的所有 $\leq$ 产生的因子群对应于链 (4) 中第 $r$ 列的所有 $\leq$ 产生的因子群。
  - 例如，链 (3) 的第 $i$ 行对应链 (4) 的第 $i$ 列，反之亦然。
- 由于链 (3) 和 (4) 中可能包含重复的群（即相同的子群多次出现），通过删除这些重复群，我们可以得到两个由不同群组成的子正规系列。
- 这些新的系列是原始系列 (1) 和 (2) 的细化（即它们包含更多子群，但最终到达同一个群 $G$）。
- 更重要的是，由于公式 (5) 的同构关系，这些细化系列是“同构的”（isomorphic refinements），即它们的因子群序列在同构意义下相同。

## 1.2 Jordan-Holder Theorem
 A subnormal series $(H_i)$  of a group $G$ is a \textbf{composition series} if all the factor groups $H_{i+1}/H_i$ are simple. A normal series $(H_i)$  of $G$ is a  **principal** or  **chief** series if all the factor groups $H_{i+1}/H_i$ are simple.

> [!Note] Jordan-Holder Theorem
>Any two composition(principal) series of a group is isomorphic

due to Scherier Theorem, if $\{H_{i}\},\{K_{i}\}$ are composition series of G, then they must have ismorphic refinement. However, every factor decided by series is simple. That is, no more subnormal group can be added to the series.
Let $H_{i}\leq H_{i+1}$, if we add $H_{i}\leq M\leq H_{i+1}$, and it meet the condition that $H_{i+1} /H_{i}$ is simple. $M / H_{i}$​	is a factor group and M is a normal subgroup in $H_{i+1}$. Since the property of holomorphism (specially canonical holomorphism), $M / H_{i}$ is a normal subgroup of $H_{i+1} / H_{i}$, and it leads to a contradiction

## 1.3 Solvable Group

[[两种可解群定义的等价性]]
### 1.3.1 Defined by the center of groups
 A group $G$ is  **solvable** if it has a composition series $\{H_i\}$ such that all factor groups $H_{i+1}/H_i$ are abelian.

By the Jordan-Hilder theorem, we see that for a solvable group, every composition series $\{H_i\}$ must have abelian factor groups $H_{i+1}/H_i$.

 We mention one subnormal series for a group  $G$ that can be formed using centers of groups. Recall from Section 13 that the center $Z(G)$ of a group $G$ is defined by
$$\begin{align*}
Z(G) = \{ z \in G \mid z g = g z \text{ for all } g \in G \},
\end{align*}$$
and that $Z(G)$ is a normal subgroup of $G$. If we have the table for a finite group $G$, it is easy to find the center. An element $a$ is in the center of $G$ if and only if the row with header $a$ and the column with header $a$ list the elements of $G$ in the same order.

Now let $G$ be a group, and let $Z(G)$ be the center of $G$. Since $Z(G)$ is normal in $G$, we can form the factor group $G/Z(G)$ and find the center $Z(G/Z(G))$ of this factor group.

Since $Z(G/Z(G))$ is normal in $G/Z(G)$, if $\gamma:G \to G/Z(G)$ is the canonical map, then by Theorem 13.18, $\gamma^{-1}[Z(G/Z(G)])$ is a normal subgroup $Z_1(G)$ of $G$. We can then form the factor group $G/Z_1(G)$ and find its center, take $(\gamma_1)^{-1}$ of it to get $Z_2(G)$, and so on.

 The series
$$\begin{align*}
\{e\} \leq Z(G) \leq Z_1(G) \leq Z_2(G) \leq \cdots
\end{align*}$$
described in the preceding discussion is the **ascending central series of the group G.**

### Defined by Derived Subgroup
Let G is a group, $G'=<(x,y)>$, the commucator subgroup. Then, by induction, we can define commucator subgroup on the last commucator subgroup $G^{(k)}= <(x,y)>, x,y\in G^{(k-1)}$. we define

**Derived Series** as $G\triangleright G^{(1)}\dots \triangleright G^{(k+1)}\triangleright\dots$
If the series decline to $e$ , we say G is **solvable group**

**Descending central series** refers to the series
$$
G_{1}=G,\:G_{2}=G',\dots,G_{k+1}=(G_{k},G)=<(u,v)u\in G_{k},v\in G>
$$
It's easy to examine $G_{k}$ are all the normal subgroup of $G$

G is a **Nilpotent Group**, when the descending central series comes to be $\{e\}$
It c is the smallest integer that makes $G_{c}=\{e\}$ , c is called nilpotency class of G

> [!Note] Theorem
>If G is sovable group, then all the normal subgroup and factor group of G is solvable

The theorem of normal subgroup is trival
As for factor group, we only need to observe that $\gamma:G\to G /K$ preserve commucator in $G / K$

> [!Note]  Theorem
> G is a solvable group, and $K\triangleleft G$. Then, G is solvable if and only if both K and $G /K$ is solvable

Collorary
H and K are solvable subgroup of G, then HK is also a solvable subgroup
