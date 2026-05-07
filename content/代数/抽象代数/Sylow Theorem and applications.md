---
tags:
  - 抽象代数
  - 代数
---
# 1. P-Groups

## 1.1 Class Equation

>[!a theorem that counts a set by group action]
>Let X be a finite G-set(left action set), $Gx$ refers to an orbit. We have
>$$
\lvert X \rvert =\sum_{i=1}^{r}\lvert Gx_{i}​	 \rvert=\lvert X_{G} \rvert +\sum_{i=s+1}^{r}\lvert Gx_{i} \rvert
>$$
where $X_{G}=\{x\in X|gx=x,\:\forall g\in G\}$


>[! Corollary for  G is a p-group]
>Let G be a group of order $p^{n}$ and let $Z$​	be a finite G-set. Then
>$$
\lvert X \rvert \equiv \lvert X_{G} \rvert \quad \text{mod}\  p
$$


>[! Corollary for the set is the group itself]
>$$
\lvert G \rvert =\lvert Z(G) \rvert +n_{c+1}+\dots+n_{r}
>$$
>where $n_{i}$ refers to numbers of conjugation class

### 1.1.1 Proof Outline
The first theorem is obvious. Just need to prove the second and last one.

To avoid confusion, we rewrite the orbit generate by $Gx$ as $O(x)$, and the stable subgroup of x as $G_{x}$
We have a one-to-one map $\psi:O(x)\to G /G_{x},gx\to gG_{x}$. For one-to-one, $g_{1}G_{x}=g_{2}G_{x}\implies g_{2}^{-1}g_{1}\in G_{x}\implies g_{2}^{-1}g_{1}x=x\implies g_{1}x=g_{2}x$
For onto, $gG_{x}$ corresponding $g\in G$, so it's clear that $\psi$ is onto.
Hence, $\lvert O(x) \rvert= \lvert G \rvert/\lvert G_{x} \rvert$ is a factor that devides $\lvert G \rvert$. So $O(x)=p^{k},k\leq n$, which completes the proof.

The third one is because conjugation can be seen as a group action.


>[!Corollary:  Burnside theorem]
Let p be prime number. The center of any p-group is nontrivial.

Proof.
$\lvert G \rvert\equiv\lvert Z(G) \rvert\quad (p)$ . And we know $Z(G)\neq \emptyset$, So $\lvert Z(G) \rvert>1$ 
## 1.2 Cauchy theorem

**Definition** Let p be a prime. A group G is a **p-Group** if every element in G has a power of the prime p.

Cauchy Theorem tells us that a finite group G has a sungroup of a prime order dividing $\lvert G \rvert$​	

>[! Cauchy's theorem]
>Let p be a prime. Let G be a finite group and let p divide $\lvert G \rvert$. Then G has an element of order p and, consequently, a subgroup of order p.

We define $X=\{(g_{1},g_{2},\dots,g_{p})|g_{i}\in G\text{ and }g_{1}g_{2}\dots g_{p}=e\}$ (just let $g_{p}=(g_{1}\dots g_{p-1})^{-1}$, so $\lvert X \rvert=\lvert G \rvert^{p-1}$ which can be devided by p) . Then, let $\sigma$ be the cycle $(1,2,\dots,p)$ act on $X$ by changing the subscript of elements. 
Observing $\lvert <\sigma> \rvert=p$, we get $\lvert X \rvert\equiv\lvert X_{ <\sigma> } \rvert\quad\text{mod}\: p$. Since $X_{<\sigma>}=\{g_{1}=g_{2}=\dots=g_{p}\}$, we have at least one element $(e,\dots,e)$ that meets the condition. So $p|\lvert X_{<\sigma>} \rvert$, we just need one of them written as $a$ such that $a\neq e,a^{p}=e$

**Corollary**
Let G be a finite group. Then G is a p-group if and only if $\lvert G \rvert$ is a power of p.
**Proof**
Sufficiency. If $\lvert G \rvert$ is a power of p. From Langrange Theorem, every cyclic group $<a>$ has a order divdes $\lvert G \rvert$, which gets the result.
Necessary. If G is a p-group, but $\lvert G \rvert=p^{n}q$ (to simplify, q is a prime diffenrent from q). $q|\lvert G \rvert\implies \exists$ an element of order $q$

# 2. Sylow theorem

**Definition** Let $\mathcal{F}$ be the collection of all subgroups of $G$. we define a G conjugation action $H\in \mathcal{F}\to gHg^{-1}$. $G_{H}:=\{g\in G|gHg^{-1}=H,\: \forall g\in G\}$ is a **normalizer** of $H$. We rewrite $G_{H}$ as $N[H]$

>[!Lemma]
>Let H be a p-subgroup of a finite group G. Then
>$$(N[H]:H)\equiv(G:H)(\text{mod}\: p)
$$


^05529e


We denote $N[H]/H$ by $\mathcal{L}_{H}$ , $G / H$ by $\mathcal{L}$. we claim that $\mathcal{L}_{H}$​	is the stable subset of left action by $H$. 
1. $\forall aH\in N[H] /H,haH=hah^{-1}H=a'H\ (a,a'\in N[H])$ and we have $N[H] / H$ is a subset of stable set.
2. Consider the stable set of left action. we need $\forall h\in H,hgH=gH$. it deduce $g^{-1}hgH=H\implies g^{-1}hg\in H,\forall h\in H\implies g\in N[H]$
So, the claim is right. By the lemma$$
\lvert X \rvert \equiv \lvert X_{G} \rvert \quad \text{mod}\  p
$$​we completes the proof.

**Remark** the lemma tells us $N[H] / H$ is the stable set of $G /H$ under left action of H. It's intuitive. And, the conditionn tells us H is a p-group as an action group. The lemma holds when we integrate the two things.

**An important corollary**  Let H be a p-subgroup of a finite group G. If p divides $(G:H)$ (that means, $|G|=p^{k}m,H=p^{k'},k'<k$), then $N[H]\neq H$
This is a preparation for First Sylow Theorem.
## 2.1 First Sylow Theorem

>[! First Sylow Theorem]
>Let $G$ be a finite group and let $|G|=p^n m$ where $n \geq 1$ and where $p$ does not divide $m$. Then
>1. $G$ contains a subgroup of order $p^{i}$ for each $i$ where $1 \leq i \leq n$.
>2. Every subgroup $H$ of $G$ of order $p^{i}$ is a normal subgroup of a subgroup of order $p^{i+1}$ for $1 \leq i < n$.

### 2.1.1 Proof Outline
(1)
By Cauchy Theorem, we know that there is a subgroup of $G$ such that its order is p. Then, we use the induction to prove 1.
$N[H]$ is what we operate our induction, since $N[H]/H$ is always a group.
Let $H$ be a p-subgroup. If $\lvert H  \rvert = p^{k},k<n$, we obtain $N[H]\neq H$. Consider $N[H] /H$. the order of it is devided by $p$ since $|N[H] /H|\equiv |G /H|$ mod p
So, by Cauchy theorem, there is a subgroup of $N[H] / H$ such that its order is p, denoted by $M$.
Let $\gamma$ be the cannonical homormophic to factor group $N[H] / H$. $\gamma ^{-1}(M)$ is a subgroup of $G$, with order $p^{k+1}$. So we get the results.
(2)
Since $M\subset N[H] / H$, we have H is a normal subgroup of the preimage of M.
## 2.2 Second Sylow Theorem

**Definition** **Sylow p-subgroup** refers to the maximal p-subgroup. By First Sylow Theorem, we know it's precisely the p-subgroup of order $p^{n}$

>[! Second Sylow Theorem]
>Let $P_{1}$ and $P_{2}$ be Sylow p-subgroups of a finite group G. Then $P_{1}$ and $P_{2}$ are conjugate subgroups of $G$.

### 2.2.1 Proof
>[!Skill: How to prove two sets are conjugate]
>Let M and H be subsets of G. Let M act on the left coset of H, denoted by $\mathcal{L}$. If $\mathcal{L}_{M}\neq \emptyset$ (for left action), we obtain that M can be conjugated to a subgroup of H.

**只对p群有用**
$\lvert G /H \rvert\equiv |(G /H)_{M}|\quad\text{mod }p$
$\forall gH\in \mathcal{L}_{M},mgH=gH,m\in M$
It deduces $g^{-1}mg\in H,\forall m\in M$

---
Here we prove the theorem.
We make $M=P_{1},H=P_{2},\mathcal{L}=\text{left coset of}\:P_{2}$
$\lvert \mathcal{L} \rvert\equiv\lvert \mathcal{L}_{P_{2}} \rvert \:\text{mod }p$, and p do not divide $\lvert \mathcal{L} \rvert$. So $\mathcal{L}$ is not empty.
And the same is $M=P_{2}$ and $H=P_{1}$

## 2.3 Third Sylow Theorem

>[! Third Sylow Theorem]
>If G is a finite group and p divides $\lvert G \rvert$, then the number of Sylow $p$-subgroup is congruent to 1 modulo p and devides $\lvert G \rvert$

### 2.3.1 Proof   

Proof.
Since $\lvert \mathcal{F} \rvert\equiv\lvert \mathcal{F}_{P} \rvert\text{mod }p$, the result holds when $\lvert \mathcal{F}_{P} \rvert=1$
Let one of sylow p-subgroup be $P$ to act on $\mathcal{F}$, the collection of all sylow p-subgroups. Let $P_{1}$ belongs to $\mathcal{F}_{P}$ but it's different from $P$.
$\forall x\in P,xP_{1}x ^{-1}=P_{1}\implies P\leq N[P_{1}]$, and $P_{1}\leq N[P_{1}]$
From Second Sylow Theorem, P and $P_{1}$ are conjugate in $N[P_{1}]$
But $P_{1}$​	is only conjugate to itself. Therefore, $P=P_{1}$, which means $\mathcal{F}_{P}=\{P\}$. It follows $\lvert \mathcal{F} \rvert\equiv1\:\text{mod}\: p$
the order of $\mathcal{F}$ devides $\lvert G \rvert$ due to Langrange Theorem.
# 3. applications and examples

>[!Fraleigh(7ed) Example37.14] 
No group of order 36 is simple

*Such a group $G$ has either 1 or 4 subgroups of order 9 . If there is only one such subgroup, it is normal in $G$. If there are four such subgroups, let $H$ and $K$ be two of them. $H \cap K$ must have at least 3 elements, or $H K$ would have to have 81 elements, from $|H K|=|H||K| /|H \cap K|$. Thus the normalizer of $H \cap K$ has as order a multiple of $>1$ of 9 (**Since Lagrange Theorem**) and a divisor of 36 ; hence the order must be either 18 or 36 . If the order is 18 , the normalizer is then of index 2 and therefore is normal in $G$. If the order is 36 , then $H \cap K$ is normal in $G$.*

# 4. Sylow定理的技巧

如果Sylow子群的个数太小 $\left| G \right|\mid n_{p}!$  (假设是单群, 则任何同态都是单射)
如果Sylow 子群的个数太多, 需要考虑元素的个数
1. 先计算其他简单的Sylow子群的个数, 直接考虑Sylow子群的元素数量与群的阶
2. 如果不行, 假设两个Sylow没有交, 得出矛盾, 一定有交. 对于$p^{2}$的Sylow子群, 我们有办法处理. 考虑$P,Q$是两个子群, 那么他们一定是abel的, 则$P\cap Q$也是交换群, 并且要整除$P$的阶, 估计$P\cap Q$的大小
3. 考虑$PQ$, $\langle P,Q \rangle$ 或者$N_{G}(P\cap Q)$. 对于$P,Q$是abel的, 有$N_{G}(P\cap Q)\supset P,Q\implies N_{G}(P\cap Q)\supset \langle P,Q \rangle\supset PQ$ 
4. 根据公式$\left| PQ \right|= \frac{\left| P \right|\left| Q \right|}{\left| P\cap Q \right|}$ 计算每一个都关系
5. $\left| PQ \right|\geq\left| P \right|+\left| Q \right|-\left| P\cap Q \right|$
6. 注意正规关系, $P\cap Q\triangleleft P,Q\implies P,Q\subset N_{G}(P\cap Q)\implies P\cap Q\triangleleft \langle P,Q \rangle$, 也就是$P\cap Q$是四个群的正规子群