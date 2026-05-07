---
tags:
  - 抽象代数
  - 代数
---
#抽象代数 #习题 

> [!Note] 练习1-1
>设 $p$ 和 $q$ 是两个不同的素数，$p<q$。证明：阶为 $pq$ 的群 $G$ 只有如下两种可能：
>（i）循环群；
>（ii）$G$ 是非交换的，此时其 Sylow $q$－子群是正规的，而且 $p \mid (q-1)$。
>特别，群 $G$ 是可解群，15阶群一定是循环群。
设 $\lvert G \rvert=pq$。

### 证明
考虑 Sylow $q$-子群。设 $N_{q}$ 为 $q$-子群的数量。根据 Sylow 第三定理，有 $N_{q}|pq$ 且 $N_{q}\equiv1(\text{mod }q)$。所以 $N_{q}$ 不整除 $q$，这告诉我们 $N_{q}|q$。由于 $p<q$，唯一的选择是 $N_{q}=1$。由 Sylow 第二定理，我们知道所有 $q$-子群是共轭的。因此，唯一的 $q$-子群与自身共轭，这意味着它是正规的。因此，无论 $G$ 是否是阿贝尔群，Sylow $q$-子群都是正规的。

现在，考虑 Sylow $p$-子群。  
(i) $G$ 是阿贝尔群。根据阿贝尔群的基本定理，存在一个阶为 $p$ 的正规子群 $P$，使得 $G=Q\times P$，因为 $Q$ 的阶是 $q$。由于 $gcd(p,q)=1$，$Q\times P$ 显然是循环的。  
(ii) $G$ 不是阿贝尔群。与 (i) 相比，我们知道没有正规的 $p$-子群，这告诉我们 $N_{p}\neq​	1$。因此，$N_{p}=q$，且 $N_{p}\equiv1(\text{mod }p)$。所以，$q\equiv1(\text{mod }p)$。
​$Q$正规子群, $G/Q$的阶数等于p, 所以是一个循环群, Q也是一个循环群, $\{e\}\triangleleft Q\triangleleft G$

$5\equiv2(\text{mod }3)\implies$ 阶为 $15$ 的群是阿贝尔群。每个有限阿贝尔群都是可解的。

### 习题课补充
$$
\lvert HK \rvert =\frac{\lvert H \rvert \lvert K \rvert }{\lvert H\cap K \rvert },\quad H,K\leq Q
$$
证明: $HK /K \to H/ H\cap K$

1. 与我的过程相同, 得到$n_{q}=1$
​	​	   所以$G=PQ$ 根据半直积定义得到G​是Q与P的半直积
2. 如果$n_{p}=1$, 那么是
3. 如果$n_{p}=q$ 此时$p|(q-1)$

（ii）若 $n_p=q$ ，那么 $p \mid(q-1)$ 。则 $G$ 是亚循环（metacyclic）群，其同构于

$$
\left\langle a, b \mid a^q=b^p=1, b a b^{-1}=a^r\right\rangle
$$

其中 $r^p \equiv 1(\bmod q)$ 且 $r \not \equiv 1(\bmod q)$ 。
此时 $Q \triangleleft G$ ，于是我们有半直积

$$
G=Q \rtimes P
$$

设 $Q=\langle a\rangle$ 且 $P=\langle b\rangle$ 。那么共轭作用 $b^i \mapsto \phi_{b^i}\left(a^j\right)=b^i a^j b^{-i}$ 是 $P \cong C_p$ 到 $\operatorname{Aut}\left(C_q\right)=C_{q-1}$的非平凡同态。设 $\phi_b(a)=a^r$ 即可得到之前的表现。如果 $r_1, r_2$ 是两个不同的解，则存在 $n \not \equiv 0(\bmod q)$ 使得 $r_2=n r_1$ ，用 $a^n$ 替代 $a$ 即可知得到上述表现与 $r$ 无关。
最后，我们知道 $G$ 一定是亚循环群（循环群被循环群的扩张），故 $G$ 可解。当 $|G|=15$ 时，因 $3 \nmid(5-1)=4$ ，我们知道 15 阶群只能为循环群。

> [!Note] 练习1-2
> 设 $p$ 和 $q$ 是奇素数。证明: 阶为 $2pq$ 的群是可解的。

根据六个条件: $n_{2}\equiv 1(\text{mod }2);\: n_{p}\equiv 1(\text{mod }p);\:n_{q}\equiv 1(\text{mod q})$$n_{2}|2pq;\:n_{p}|2pq;\:n_{q}|2pq$ 
得到$n_{2}=p,q,pq;\:n_{q}=1,p,2p;\:n_{p}=1,q,2q$
我们希望证明, 存在一个sylow subgroup​	是正规的, 这样根据sylow 定理的强版本, 可以得到一个合成列,并且​因子是素数阶群, 从而是可解.
不妨假设$p\leq q$. 反证假设$n_{p}\neq1,n_{q}\neq1,n_{2}\neq1$.
1. 如果$n_{q}=p$, 则$p\equiv1(mod \:q)$ 与$p\leq q$矛盾
2. 如果$n_{q}=2p$, $q|(2p-1)$ $p\leq q$推出$q=2p-1$
3. 如果$n_{p}=q$, 则$q\equiv1(\text{mod }p)$, 但$q=2p-1$, 推出$p|2$矛盾
4. 因此$n_{p}=2q$ $2q\equiv1(\text{mod }p)$ 代入$q=2p-1$ 推出$p=3,q=5$
现在只需要证明30阶群不符合条件.
$n_{p}=10;\:n_{q}=6,;\:n_{2}=3,5,or \:15$
由于素数阶群一定是循环群, 因此Sylow p子群之间的交群是平凡的.  并且素数不同的Sylow子群之间交集显然平凡(元素的阶决定)
计数: $\lvert G \rvert\geq20+24=44>30$, 矛盾
从而一定存在一个正规的Sylow群. 根据强的Sylow定理形式, 我们知道可解性.
![[Pasted image 20251111205527.png|500]]

### 习题课补充
引理: $n$是奇数, 且G是2n阶群, 那么G有n阶正规子群
证明:
由G在自身上的左乘作用, 得到忠实作用
$$
\phi:G\to S_{2n}
$$
由Sylow/ Cauchy, G中有2n阶元$\sigma$ $\phi(\sigma)=(a_{1},b_{1})\dots(a_{n},b_{n})$形如此
$$G\to S_{2n}\to \{\pm1\},\sigma \to p(\sigma)\to-1\: \text{is onto, then}\:ker(sgn(\phi))​	​	​	​	​	​	​	\triangleleft G $$​	​	**例** 90阶群不是单群

> [!Note] 练习1-3
>设 $G$ 为一个单群，阶为 $p^{\alpha} m$，其中 $\alpha \geqslant 1$，且 $m$ 不被 $p$ 整除。记 $n_{p}$ 为 $G$ 的 Sylow $p$－子群个数。证明 $|G| \mid n_{p}!$。

记所有的Sylow p-subgroup的集合为$\mathcal{L}$, $\lvert \mathcal{L} \rvert=n_{p}$
观察到$S(\mathcal{L})$ 的阶数$n_{p}!$ 我们选择共轭作用构造一个$\gamma:G\to S(\mathcal{L}),g\to gPg^{-1}$
由于$G$是一个单群, 所有的核都必须是平凡的, $ker(\gamma)=G\implies n_{p}=1\implies$不是单群. 从而$ker(\gamma)=e$
所以$G\cong H\subset S(\mathcal{L})$ , 这完成了证明.
### 习题课补充(非常常用, 值得背诵)
下面这个方法适用于$n_{p}$小, $\lvert G \rvert$大, $G$非单
$G\curvearrowright Sylo(G)$, 有同态$\rho:G\to S_{n_{p}},g\to \{P\to gPg^{-1}\}$ $ker(\rho)=\{e\}$ $\lvert G \rvert|n_{p}!$

> [!Note] 练习1-4
>证明：若群的阶为 $p^{m} q^{n}$，其中 $p<q$，$1 \leqslant m \leqslant 2$，$n \geqslant 1$，则该群不是单群。

假设该群是单群, 则Sylow子群每一个共轭类至少与两个元素.
(1) m=1
$n_{q}\equiv1(\text{mod }q),n_{q}|pq^{n}$ 推出$n_{q}=p$ 矛盾
(2​)m=2
$p^{2}\equiv1(\text{mod }q)$ ​	$\implies q|(p+1)(p-1)\implies q|p+1\implies q=p+1\implies p=2,q=3$
$n_{p}\equiv1 \quad(\text{mod }p)=1\quad(\text{mod 2})$​	所以$n_{p}=3^{k}$
$n_{q}=n_{3}=4$ $\lvert G \rvert|n_{3}! =24$ 然而$\lvert G \rvert=4\cdot3^{n}$


> [!Note] 练习1-5
>证明：阶为 $p^{2} q$ 或 $p^{3} q$ 的群都不是单群。

假设不是单群
(1)$p^{2}q$
同样地计算可以得到, $n_{p}=q;\:n_{q}=p\:or\: p^{2}$ 
由于$n_{p}=q,\:n_{p}\equiv1(\text{mod p})$ 可以得到​	$q>p$
根据练习1-4可以知道一定是单群
(2)$p^{3}q$
计算可得$n_{p}=q,n_{q}=p,p^{2},p^{3}$
$n_{p}=q$ 可以得到$q>p$
1. $n_{q}=p$ 得到$q<p$矛盾
2. $n_{q}=p^{2}\implies q|p^{2}-1\implies q=p+1,p=2,q=3$
​	​	$G$的阶数$24$, 同样考虑群作用, 应当有$\lvert G \rvert\:|\:24$, 发现刚好满足, 所以$G\cong S_{4}$, 然而$S_{4}$有正规子群$A_{4}$, 与假设矛盾

### 习题课补充
($nq=p^{3}$​) 如果$n_{p}$大,$p$小, 计算元素
所有的Sylow q-子群的并$-\{e\}$, 有$p^{3}(q-1)$个元, 正好留下来$p^{3}$​	个元组成$Sylow$ p-子群是唯一的. 所以$G$ 不是单群.

> [!Note] 练习1-6
>试证明，若群 $G$ 的阶 $\leq 59$，则该群可解。

![[习题课6.pdf#page=3&rect=62,264,541,410|习题课6, p.3]]

![[习题课6.pdf#page=3&rect=58,91,541,270|习题课6, p.3]]

引理2．设 $n$ 是一个奇数且 $G$ 是 $2 n$ 阶群。证明 $G$ 含有 $n$ 阶正规子群。
证明．考虑 $G$ 在自身上的左乘作用诱导的置换表示： ^2d1a88
$$
\phi: G \rightarrow S_{2 n} .
$$
由 Cauchy 定理（或者 Sylow 定理），$G$ 中有 2 阶元 $\sigma$ 。由于 $\phi$ 是单射，$\phi(\sigma)$ 是一个 2 阶的置换，而且没有固定点。所以 $\phi(\sigma)$ 的轮换分解中恰好有 $n$ 个 2 －轮换。据此可知，$\phi(\sigma)$ 是一个奇置换。我们知道同态的复合
$$
G \xrightarrow{\phi} S_{2 n} \xrightarrow{\text { sgn }}\{ \pm 1\}
$$
是一个满同态。其核即为 $G$ 的一个 $n$ 阶正规子群。
没有固定点: $\phi(\sigma)$是一个二阶的置换, 如果$\phi(\sigma)g=g\implies \phi(\sigma)=e\implies \sigma=e'$矛盾
二阶置换一定是n个不相交的对换的乘积. n是奇数, 从而是奇置换. 偶置换取单位元. 从而同态的复合是一个满同态, 核为一个n阶正规子群

**证明144阶群可解**
2．假设 $|G|=144=2^4 \times 3^2$ 。我们有 $n_3=4$ 或 16 ，且 $n_2 \geq 3$ 。但是 $|G| \nmid 4!$ ，因此必有 $n_3=16$ 。假设 $P$ 和 $Q$ 是两个不同的 Sylow 3－子群。那么 $M=P \cap Q$ 的阶是 1 或者 3 ，因而

$$
|P Q|=\frac{|P||Q|}{|M|} \geq 27
$$


同样 $\langle P, Q\rangle$ 的阶大于 27 且是 9 的倍数。所以 $|\langle P, Q\rangle|=36,72$ 或 144 。显然 $|\langle P, Q\rangle|$ 不能为 72 。如果 $|\langle P, Q\rangle|=144$ ，此时由于 $P$ 和 $Q$ 是交换群，我们有 $P \cap Q \triangleleft\langle P, Q\rangle$ ，于是 $|M|=1$ 。而所有 Sylow 3－子群一共包含除单位元外共 $16 \times(9-1)=128$ 个元素。而剩余的 16 个元素将导致 $n_2$ 只能为 1 ，矛盾。所以 $|\langle P, Q\rangle|=36$ 。此时 $G$ 在 $|\langle P, Q\rangle|$ 的左陪集上的作用诱导由 $G$ 到 $S_4$ 的单同态。但是又有 $|G| \nmid 4$ ！。因此 $G$ 一定非单。


> [!Note] 练习2-1
>在 $A_{5}$ 中找出 Sylow 2－子群、Sylow 3－子群、Sylow 5－子群的个数。


(1)
根据同余以及60的因子, 可能有$n_{5}=1,6$, 但$A_{5}$ 是单群, 所以$n_{5}=6$ 共有24个不同的5阶元
(2)​	
$n_{3}=1,4,10$ 同样排除1. 如果$n_{3}=4$, 不满足$\lvert G \rvert\:|16$的群同态单射条件(构造$A_{5}\to S_{3}$), 所以$n_{3}=10$ 共有20个不同的3阶元
(3)
$n_{2}=1,3,5,15$
排除1
排除3, 因为$\lvert S_{3} \rvert<\lvert A_{5} \rvert$
考虑15. 四阶群只有循环群和Klein群, 四阶循环群是奇置换, 不在$A_{5}$中. 因此我们假设有15个Klein群. (不会推)

---
一种解答: 
$$\begin{align*}
V := \{1, (12)(34), (13)(24), (14)(23)\}
\end{align*}$$
is a Sylow 2-subgroup of $A_5$, and there are four more subgroups of this form, so $n_2 \geq 5$. On the other hand, any conjugate of $V$ is clearly one of these five subgroups.
Since Syl_2(A_5) is a conjugacy class, it follows that these five subgroups are the only Sylow 2-subgroups.

### 补充
设$x$是2阶元
那么 $\lvert  \rvert$

> [!Note] 练习2-2
>设 $G$ 为一个阶为 60 的单群。证明 $G$ 的 2－Sylow 子群的个数等于 5 或 15。

$n_{2}$是奇数, 所以$n_{2}=3,5,15$, 只需排除3
设$\mathcal{L}$是所有Sylow 2-子群的集合, $\varphi:G\to S(\mathcal{L}),g\to gPg^{-1}$ 是一个群同态, 由于G是单群, $\varphi$是单同态. $\lvert S(\mathcal{L}) \rvert=6<\lvert G \rvert$, 与单射矛盾, 因此只可能为5, 15

> [!Note] 练习2-3
>由此推得 $G$ 一定含有一个阶为 12 的子群。

如果$n_{2}=5$, 设$\mathcal{S}$是所有Sylow 2-子群的集合, 由于$G$的共轭作用在$\mathcal{S}$上只有一个轨道. $|\mathcal{S}|=|O(P)|=|G /Stab(P)|= \frac{|G|}{|N(P)|}$ where $N(P)$ is normalizer of P.
$|N(P)|=12$, 因此满足条件.
还需要证明$n_{2}\neq15$

### 补充
1. 讨论$n_{p}$
2. 讨论$N_{G}(P)$
3. $N(P)\cap N(Q)$
4. $N_{G}(\dots)$

$n_{2}=15$ $n_{3}\equiv1(\text{mod 3})$ $n_{3}|20$​	所以$n_{3}=10$​	取$Q\in Sylo(G)$ , $\lvert N_{G}(Q) \rvert= \frac{\lvert G \rvert}{n_{3}}=6$
$P\in Sylo(G),\lvert P\cap N_{G}(Q) \rvert=2$
$\lvert PN_{G}(Q) \rvert = \frac{\lvert P \rvert\lvert N_{G}(Q) \rvert}{\lvert P\cap N_{G}(Q) \rvert}$
所以 $<P,N_{G()}$

---
上一个证明失效, 考虑新的证明
对素数2, 假设不相交, 一共有46个元. 对素数5, 假设不相交, 共有25个元, 超过了群都阶数
因此存在$P,Q\in Sylo_{2}(G),\: s.t. \:P\cap Q\neq \{e\},\: <P,Q>\leq C_{G}(k)\implies<P,Q>4$
$P\in Sylo_{2}(G)$
所以$\lvert C_{G}(k) \rvert>4$, G is simple. If $[G:C_{G}(k)]\leq4$, left coset $G\to S_{4}$ is one to one
$\lvert C_{G}(k) \rvert<15$​	, so $\lvert C_{G}(k) \rvert>12$
由$G\to S_{5}$ 是单同态, 所以$G\cong A_{5}$

解答．1．若 $n_2=5$ ：此时我们有 $\left[G: N_G(P)\right]=n_2=5$ (轨道-稳定子定理, 令G共轭作用于P上, 则轨道是所有P子群的集合, 得到这个公式)。因而 $N_G(P)$ 是 $G$ 的一个阶为 12 的子群。

2．若 $n_2=15$ ：如果所有 Sylow 2－子群的交是平凡的，那么这些子群一共有 $1+15 \times(4-1)=46$个元素。又因为 $n_5 \geq 6$ ，全体 Sylow 5－子群除了单位元一共有 $6 \times(5-1)=25$ 个元素。这导致矛盾。因此存在 $P, Q \in \operatorname{Syl}_2(G)$ 使得 $P$ 和 $Q$ 的交非平凡。由于 $P$ 和 $Q$ 都是 Abel群， $P \cap Q$ 是 $P$ 和 $Q$ 的正规子群。因而 $P, Q \leq N_G(P \cap Q)$ 。所以 $4\left|\left|N_G(P \cap Q)\right|\right| 60$ 而且 $\left|N_G(P \cap Q)\right| \geq|P|+|Q|-|P \cap Q|>4$ 。又因为 $\left|N_G(P \cap Q)\right|<15$ ，我们知道 $N_G(P \cap Q)=12$ 。



> [!Note] 练习2-4
>作出你的结论。

解答。考虑 $G$ 在左陪集 $G / H$ 上的左乘作用，我们知道 $G$ 同构于 $S_5$ 的子群。而 $A_5$ 是 $S_5$ 的唯一指数为 2 的子群（因为任意元素的平方都在 $A_5$ 内）。所以必有 $G$ 同构于 $A_5$ 。

### 习题课补充
$\lvert G \rvert=112,120,132,144$

112
$n_{p}\geq5$. G嵌入$S_{n_{p}}$, $G\cap A_{n_{p}}=G$, $\frac{\lvert G \rvert}{\lvert G\cap A_{n_{p}} \rvert}=1,2$​	
$G\to A_{n_{p}}\quad \lvert G \rvert| \frac{1}{2}n_{p}!$
$G\to A_{\sigma}$, index is 3 


### 补充

$act:GL_{n}(\mathbb{F}_{q})\to \mathbb{F}_{q}^{\times},\lvert \mathbb{F} ^{\times}​	\rvert=q-1$
Therefore, we have $\lvert SL_{n}(\mathbb{F}_{q}) \rvert= \frac{\lvert GL_{n}(\mathbb{F}_{q}) \rvert}{q-1}$
$\lvert PSL_{n}(\mathbb{F}_{q}) \rvert= \frac{\lvert SL_{n}(\mathbb{F})_{q} \rvert}{gcd(n,q-1)}$​	

> [!Note] 练习3-1
>求 $\mathrm{GL}_{n}(\mathbb{F}_{p})$ 的阶。

对第一行分析, 第一行不能为0, 有$p^{n}-1$种
对第二行, 第二行不能是第一行的线性组合, 第一行的线性组合共有$p$种, 因此第二行有$p^{n}-p$
第三行不能是一二行的线性组合, 有$p^{n}-p^{2}$​	种
...
$\lvert GL_{n}(\mathbb{F}_{p}) \rvert=\prod_{k=0}^{n-1}(p^{n}-p^{k})$ 

> [!Note] 练习3-2
>写出一个 $\mathrm{GL}_{n}(\mathbb{F}_{p})$ 的 $p$－Sylow 子群。

$\lvert GL_{n}(\mathbb{F}_{p}) \rvert=\prod_{k=0}^{n-1}(p^{n}-p^{k})=p^{\frac{n(n-1)}{2}}(p^{n}-1)(p^{n-1}-1)\dots(p-1)$ 
所以Sylow p-group​ is of order $p^{\frac{n(n-1)}{2}}$
$$
\begin{pmatrix}
1  &  \star  & \dots & \star \\
0 & 1 & \star  &  \star \\
\vdots &  &  & \vdots \\
0  & 0 & \dots & 1 
\end{pmatrix}
$$​	矩阵在 $\star$ 处取任意值, 对角线是1 下三角全为0.
可以看出, 这样的矩阵构成一个乘法群, 阶为$p^{\frac{n(n-1)}{2}}$

> [!Note] 练习3-3
>计算 $\mathrm{GL}_{n}(\mathbb{F}_{p})$ 的 $p$－Sylow 子群的个数（给出显式公式）。

思路: 已经得到了一个p-子群, 那么只需要计算共轭类即可. 如果能知道3-2中的群的正规子群阶数, 问题就能被解决.
设$U_{n}(\mathbb{F})$为3-2中的群, $B_{n}(\mathbb{F})$是可逆上三角矩阵群
可以验证$B_{n}(\mathbb{F})\subset N(U_{n}(\mathbb{F}))$ 
只需证明$N(U_{n}(\mathbb{F}))\subset B_{n}(\mathbb{F})$ 

引理[[旗]]: $U_{n}(\mathbb{F})$稳定唯一的完全旗，即标准旗$F_{1}:<e_{1}>\subset<e_{1},e_{2}>\subset\dots<e_{1},e_{2},\dots,e_{n}>$ 
设 $g \in N(U_{n}(\mathbb{F}_{p}))$，则 $g U_{n}(\mathbb{F}_{p}) g^{-1} = U_{n}(\mathbb{F}_{p})$
$U_{n}(\mathbb{F}_{p})$ 稳定标准旗 $F_{0}$，因此 $g U_{n}(\mathbb{F}_{p}) g^{-1} = U_{n}(\mathbb{F}_{p})$ 稳定旗 $g F_{0}$。
由引理，$U_{n}(\mathbb{F}_{p})$ 稳定唯一的完全旗 $F_{0}$，故 $g F_{0} = F_{0}$, 所以 $g$ 稳定 $F_{0}$，即 $g \in B_{n}(\mathbb{F}_{p})$（因为 $B_{n}(\mathbb{F}_{p})$ 是 $F_{0}$ 的稳定子
因此，$N(U_{n}(\mathbb{F}_{p})) \subset B_{n}(\mathbb{F}_{p})$, 有 $N(U_{n}(\mathbb{F}_{p})) = B_{n}(\mathbb{F}_{p})$

计算公式:
$|B_{n}(\mathbb{F}_{p})| = (p-1)^{n} p^{\frac{n(n-1)}{2}}$ 
$$
  n_{p} = \frac{|\mathrm{GL}_{n}(\mathbb{F}_{p})|}{|N(U_{n}(\mathbb{F}_{p}))|} = \frac{|\mathrm{GL}_{n}(\mathbb{F}_{p})|}{|B_{n}(\mathbb{F}_{p})|} = \frac{p^{\frac{n(n-1)}{2}} \prod_{j=1}^{n} (p^{j} - 1)}{(p-1)^{n} p^{\frac{n(n-1)}{2}}} = \frac{\prod_{j=1}^{n} (p^{j} - 1)}{(p-1)^{n}} = \prod_{j=1}^{n} \frac{p^{j} - 1}{p - 1}.

$$


> [!Note] 练习3-4
>验证上述个数满足 Sylow 第三定理。

$n_{p}=\prod_{j=1}^{n}(1+p+p^{2}+\dots+p^{j-1})$ ​	对每一项显然有$1+p+\dots+p^{j-1}\equiv1(\text{mod p})$ 
$\lvert GL_{n}(\mathbb{F}_{p}) \rvert=p^{\frac{n(n-1)}{2}}(p^{n}-1)(p^{n-1}-1)\dots(p-1)$ 
$n_{p}=\prod_{j=1}^{n} \frac{p^{j} - 1}{p - 1}$ 
​所以$n_{p}\:|\:\lvert GL_{n}(\mathbb{F}_{p})​	​	 \rvert$

> [!Note] 练习4-1
>当 $n>2$ 且 $n \neq 6$ 时，$S_{n}$ 的所有自同构都是内自同构。

### 补充的引导题目
练习 2．5．11．本题的目标是证明当 $n \neq 6$ 时， $\operatorname{Aut}\left(S_n\right)=\operatorname{Inn}\left(S_n\right)$ 。设 $n \neq 6$ 是一个整数。
（1）设 $\sigma \in \operatorname{Aut}(G), \mathcal{C}$ 是 $G$ 的一个共轭类，证明 $\sigma(\mathcal{C})$ 也是 $G$ 的一个共轭类；
（2）设 $\mathcal{C}$ 是 $S_n$ 中由对换组成的共轭类， $\mathcal{C}^{\prime}$ 是 $S_n$ 的另一个共轭类，并且 $\mathcal{C}^{\prime}$ 包含一个阶为 2 的非对换元素。证明 $|\mathcal{C}| \neq\left|\mathcal{C}^{\prime}\right|$ ；
（3）设 $\sigma \in \operatorname{Aut}\left(S_n\right)$ ，证明存在互不相同的整数 $a, b_2, b_3 \ldots, b_n$ 使得 $\sigma((1 k))=\left(a b_k\right), k=2, \ldots, n$ ；
（4）证明 $S_n$ 可由（12），（13），$\ldots,(1 n)$ 生成。由此证明 $\operatorname{Aut}\left(S_n\right)=\operatorname{Inn}\left(S_n\right)$ 。
练习 2．5．12．本题的目标是研究 $S_6$ 的自同构群。

### 证明过程 
(1)检验后显然
(2)

> [!Note] 引理: 两个置换共轭当且仅当循环分解具有相同类型

证明: 对任意 $\tau \in S_n$ ，有 $\tau\left(i_1 i_2 \ldots \ldots i_r\right) \tau^{-1}=\left(\tau\left(i_1\right) \tau\left(i_2\right) \ldots \ldots \tau\left(i_r\right)\right)$设 $\alpha$ 和 $\beta$ 有相同的轮换结构。
$$
\begin{aligned}
& \alpha=\left(i_1 i_2 \ldots \ldots i_r\right)\left(j_1 j_2 \ldots \ldots j_s\right) \ldots \ldots\left(l_1 l_2 \ldots \ldots l_t\right) \\
& \beta=\left(a_1 a_2 \ldots \ldots a_r\right)\left(b_1 b_2 \ldots \ldots b_s\right) \ldots \ldots\left(d_1 d_2 \ldots \ldots d_t\right) \\
& \text { 令 } \tau=\left(\begin{array}{llll}
\ldots \ldots i_1 \ldots \ldots i_r & j_1 \ldots \ldots j_s & \ldots \ldots & l_1 \ldots \ldots l_t \ldots \ldots \\
\ldots \ldots a_1 \ldots \ldots a_r & b_1 \ldots \ldots b_s & \ldots \ldots & d_1 \ldots \ldots d_t \ldots \ldots
\end{array}\right) \in S_n
\end{aligned}
$$

> [!Note] 共轭类计算公式
对于共轭类型形如$1^{a_{1}}2^{a_{2}}\dots k^{a_{k}}$的置换, $a_{i}$代表在一个置换中长度为i循环的个数, 并且$a_{1}+2a_{2}+\dots+ka_{k}=n$则共轭类的大小为 
>$$
>  \frac{n!}{\prod_{i=1}^{k} (i^{a_{i}}a_{i}!)}
> $$

证明: 每一个长度为$i$的循环可以有$i$种写法, 并且循环之间的成绩不重要, 从而要除以分母这些数来排除重复.

$S_{n}$中$1^{n-2r}2^{r}$型置换个数
$$
 \frac{n!}{1^{n-2r}2^{r}(n-2r)!r!}=\begin{pmatrix}
n \\
2r 
\end{pmatrix}
(2r-1)!!
$$
特别地, $\lvert c \rvert= \begin{pmatrix}n \\ 2\end{pmatrix}$



> [!Note] 练习4-2
>$S_{6}$ 存在不是内自同构的自同构。

$S_6$ 有外自同构，可将传递置换表示映射到另一类共轭类（如将 15 个对换映射到 15 个三元积对换）。

1．证明例2．4．5诱导的映射 $\psi: S_5 \rightarrow S_X \simeq S_6$ 是单射。
2．证明上述映射保持置换的奇偶性，即将奇置换映为奇置换，偶置换映为偶置换。
3．记 $H$ 为 $\psi$ 的像，并记 $Y$ 为 $H$ 在 $S_6$ 中的左陪集组成的集合，易知 $|Y|=6$ 。 $S_6$ 在 $Y$ 上的左乘作用给出了群同态 $F: S_6 \rightarrow S_6$ 。证明 $F$ 是单射，从而证明 $F$ 是同构。
4．通过计算 $F\left(\begin{array}{ll}1 & 2\end{array}\right)$ 不是对换证明 $F$ 不是内自同构。
5．证明 $\operatorname{Aut}\left(S_6\right) \simeq \operatorname{Inn}\left(S_6\right) \rtimes\langle F\rangle$ 。（提示：考虑 $S_6$ 中的对换个数以及形如（12）（34）（56）的置换个数）
![[b6b2e85d756978d151a5c0d79d4612e8 1.jpg]]

# 课本&讲义其余习题
10．设 $P$ 是有限群 $G$ 的西罗子群，$N$ 是 $G$ 的正规子群．证明 $P \cap N$ 是 $N$ 的西罗子群．举例说明如果 $N$ 不是正规的，则该断言不成立．
注意到 $NP$中素数​	$p$的幂次与$P$相同, $N\cap P$一定是P群, 根据$\left| NP \right|= \frac{\left| N \right|\left| P \right|}{\left| N\cap P \right|}\implies \frac{\left| N \right|}{\left| N\cap P \right|}= \frac{\left| NP \right|}{\left| P \right|}$ 

**计算$S_{n}$中的共轭类**
假设循环分解类型为$\prod i^{m_{i}}$ 
共轭类的大小公式为：

$$
|C(\sigma)|=\frac{n!}{\prod_{i=1}^k i^{m_i} m_{i}!}
$$


简单理解
共轭类大小可以通过以下方式简单理解：
- 共有 $n!$ 种方式排列 $n$ 个元素。
- 对于每个长度为 $i$ 的循环，有 $i$ 种不同的表示（循环可以旋转），因此每个循环贡献因子 $i$ 。
- 相同长度的 $m_i$ 个循环可以互换顺序而不改变循环结构，因此贡献因子 $m_i$ ！。

所以，分母为 $\prod_i i^{m_i} m_{i}!$ 。
**计算$A_{5}$中的所有Sylow-2子群个数**
3．$(p=2) A_5$ 的 2 阶元素形如 $1^1 2^2$ ，共有 $5!/\left(2!\times 2^2\right)=15$ 个。由于 Sylow 2 －子群阶为 4 ，而 $A_5$ 中无4－循环，故 Sylow 2－子群皆同构于 $F_4$ ，每个含 3 个 2 阶元素。任取 2阶元素 $x$ ，==其共轭类大小为 15 ==，故

$$
\left|C_{A_5}(x)\right|=\frac{60}{15}=4,
$$

等于包含 $x$ 的唯一 $F_4$ 。于是每 3 个 2 阶元素只落在一个 Sylow 2－子群中，因而

$$
n_2=\frac{15}{3}=5
$$

与 $n_2 \mid 15, n_2 \equiv 1(\bmod 2)$ 一致。

==共轭类为15的证明==
$A_n$ 是 $S_n$ 的指数为 2 的正规子群。对于 $x \in A_n$ ，其在 $A_n$ 中的共轭类可能小于在 $S_n$ 中的共轭类。具体地：
- 若 $C_{S_n}(x) \subseteq A_n$ ，则 $x$ 在 $A_n$ 中的共轭类分裂为两个大小相等的类。
- 若 $C_{S_n}(x) \nsubseteq A_n$ ，则 $x$ 在 $A_n$ 中的共轭类与在 $S_n$ 中相同。
在 $S_5$ 中，该共轭类大小为 15。现在检查是否在 $A_5$ 中分裂：
取 $x=(12)(34) \in A_5$ ，计算其中心化子 $C_{S_5}(x)$ 的阶。根据公式：

$$
\left|C_{S_5}(x)\right|=\prod_k\left(k^{a_k} \cdot a_{k}!\right)=1^1 \cdot 1!\cdot 2^2 \cdot 2!=1 \cdot 1 \cdot 4 \cdot 2=8
$$

由于 $C_{S_5}(x)$ 包含奇置换（如交换两个2－循环的置换），故 $C_{S_5}(x) \nsubseteq A_5$ 。因此，$x$ 在 $A_5$ 中的共轭类与在 $S_5$ 中相同，大小仍为 15 。