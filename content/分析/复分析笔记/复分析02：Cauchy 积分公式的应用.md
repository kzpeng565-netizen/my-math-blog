---
tags:
  - 复分析
  - 分析
---
#复分析 #课堂笔记 

> [!Note] Theorem: the power series expansion of a holomorphic function
>Suppose f is holomorphic at a open disc centered at $z_{0}$, and the closure is contained in $\Omega$, then f has power series expansion at $z_{0}$
>$$\begin{align*}
> f(z) = \sum_{n=0}^{\infty} a_n (z - z_0)^n
> \end{align*}$$


$a_{n}= \frac{f^{(n)}}{n!}$And the convergent radius is at list the radius of D

Proof 
We first impose $a_{n}= \frac{f^{(n)}}{n!}$，we first show that the series $\sum_{n=0}^{\infty}a_{n}(z-z_{0})^{n}$ has radius of convergence at least equal to R of D
By assumption, $\bar{D} \subset\Omega$​	
If $C=\partial D$, then(我们可以把圆中的每一个点的函数值都写成一个统一的积分公式)
$$
f(z)= \frac{1}{2\pi i}\int_{c} \frac{f(\xi)}{\xi-z}d\xi
$$​
for $z\in D$ by Cauchy theorem And $f^{(n)}(z)= \frac{n!}{2\pi i}\int \frac{f(\xi)}{(\xi-z)^{n+1}}d\xi$.
It follows that $|f^{(n)}(z_{0})|\leq \frac{n!}{R^{n}}\sup_{z\in \bar{D}}|f(z)|$
Let $M = \sup \dots$ , then$|f^{n}(z_{0})|\leq \frac{n!}{R^{n}}M$. Thus $|a_{n}|\leq \frac{M}{R^{n}}$
$$
limsup_{n\to \infty} |a_{n}|^{1/n}\leq limsup_{n\to \infty} \frac{1}{R}M^{1/n}= \frac{1}{R}
$$
So the convergent radius is at least R


Fix $z \in D$. By the Cauchy integral formula, we have
$$\begin{align*}
f(z) = \frac{1}{2\pi i} \int_C \frac{f(\zeta)}{\zeta - z} \, d\zeta,
\end{align*}
$$
where $C$ denotes the boundary of the disc and $z \in D$. The idea is to write
$$\begin{align*}
\frac{1}{\zeta - z} = \frac{1}{\zeta - z_0 - (z - z_0)} = \frac{1}{\zeta - z_0} \frac{1}{1 - \left(\frac{z - z_0}{\zeta - z_0}\right)},
\end{align*}
$$
and use the geometric series expansion. Since $\zeta \in C$ and $z \in D$ is fixed, there exists $0 < r < 1$ such that
$$\begin{align*}
\left| \frac{z - z_0}{\zeta - z_0} \right| < r,
\end{align*}
$$

therefore
$$
\begin{align*}
\frac{1}{1 - \left(\frac{z - z_0}{\zeta - z_0}\right)} = \sum_{n=0}^{\infty} \left(\frac{z - z_0}{\zeta - z_0}\right)^n,
\end{align*}$$
Then, we prove the convergence is uniform
$R=|\xi-z_{0}|,\: r=|z-z_{0}|$
$$
\left|  \frac{(z-z_{0})^{n}f(\xi)}{(\xi-z_{0})^{n}} \right| \leq \frac{r^{n}}{R^{n}}M
$$
And the right hand side is uniform confergent
the series converges uniformly for $\zeta \in C$. This allows us to interchange the infinite sum with the integral
$$\begin{align*}
f(z) = \sum_{n=0}^{\infty} \left( \frac{1}{2\pi i} \int_C \frac{f(\zeta)}{(\zeta - z_0)^{n+1}} d\zeta \right) \cdot (z - z_0)^n.
\end{align*}
$$

> [!Note] 推论：常规全纯函数在连通集中没有无限阶零点
>设 $\Omega$ 是 $\mathbb{C}$ 的一个连通开子集，令 $f:\Omega\to \mathbb{C}$ 是一个全纯映射，令 $z_{0}\in\Omega$ 为一个点。
>假设 $f^{(n)}(z_{0})=0$ 对所有 $n\geq0$ 成立，那么 $f(z)=0$ 对所有 $z\in\Omega$ 成立。

*连通开集意味着我们不能将集合分解成两个不相交的子集。因此根据定义，只有空集和整个集合本身既是闭集又是开集。*

**证明**：
**步骤1**：我们可以证明 $f(z)=0$ 在以 $z_{0}$ 为中心的圆盘 $D$ 内成立。
**步骤2**：我们将其扩展到整个 $\Omega$。
令
$$
Z= \{z\in\Omega| f^{(n)}(z)=0\},\quad \forall n\geq0
$$
由于 $f^{(n)}$ 是连续的，$Z$ 是闭集。
此外，$Z \neq \emptyset$，因为 $z_{0}\in Z$。
另外，如果 $z\in Z$，那么由步骤1，存在一个以 $z$ 为中心的圆盘使得 $f(z)=0$，所以 $Z$ 也是一个开集（或者说包含一个开圆盘）。
由于 $\Omega$ 是连通的，我们得到 $Z= \Omega$。

> [!Note] Theorem: the isolated zeros property of holomorphic functions
> Let $\Omega$ be a connected open subset of $\mathbb{C}$, and let $f: \Omega \to \mathbb{C}$ be a holomorphic function. Suppose there exists a sequence $\{z_n\}$ such that $f(z_n) = 0$ for all $n$, and $\{z_n\}$ converges to  with $z_\infty \notin \{z_n\}$ (excluding the case where the sequence is eventually constant at ). Then $f \equiv 0$ on $\Omega$.

^eb9556

Remark $z_{\infty } \not\in \{z_{n}\}$​	 exclude the case that $z_{0}=z_{1}=\dots$
这个定理说的是，一个在连通集上不全为0 的全纯函数 等于0的点不可能构成极限点

证明思路：
使用级数展开，对函数的零点情况考虑。除开等于0的前面几项，把$(z-z_{_{\infty}})^{m}$提出来，对后面的函数估计，可以找到一个小圆盘内后面的函数不等于0，从而整个函数在以$z_{\infty}$为中心的小圆盘上不等于0. 这与序列极限趋于$z_{\infty}$矛盾
**Proof**:  
Assume, for contradiction, that $f \not\equiv 0$. Since $z_\infty \in \Omega$ and $f$ is holomorphic, there exists an open disk $D \subset \Omega$ centered at $z_\infty$ such that $f$ has a power series expansion in $D$:
$$
f(z) = \sum_{n=0}^{\infty} a_n (z - z_\infty)^n, \quad \text{for all } z \in D.
$$
Because $\{z_n\}$ converges to $z_\infty$, there exists $N \in \mathbb{N}$ such that $z_n \in D$ for all $n > N$. Without loss of generality, we may assume $z_n \in D$ for all $n$.

Since $f \not\equiv 0$, not all coefficients $a_n$ are zero. Let $m$ be the smallest non-negative integer such that $a_m \neq 0$. Then we can write:
$$
f(z) = a_m (z - z_\infty)^m + a_{m+1} (z - z_\infty)^{m+1} + \cdots = a_m (z - z_\infty)^m \left( 1 + \frac{a_{m+1}}{a_m} (z - z_\infty) + \frac{a_{m+2}}{a_m} (z - z_\infty)^2 + \cdots \right).
$$
Define the function $g(z)$ by:
$$
g(z) = \sum_{k=1}^{\infty} \frac{a_{m+k}}{a_m} (z - z_\infty)^k.
$$
This series converges in $D$, so $g(z)$ is holomorphic in $D$ and satisfies $g(z_\infty) = 0$. Therefore,
$$
f(z) = a_m (z - z_\infty)^m (1 + g(z)), \quad \text{for all } z \in D.
$$
Since $g$ is continuous and $g(z_\infty) = 0$, there exists an open disk $D' \subset D$ centered at $z_\infty$ such that $|g(z)| < 1$ for all $z \in D'$. Consequently, for all $z \in D' \setminus \{z_\infty\}$, we have $1 + g(z) \neq 0$ and $a_m (z - z_\infty)^m \neq 0$ (because $z \neq z_\infty$), so $f(z) \neq 0$.

However, since $\{z_n\}$ converges to $z_\infty$, there exists $M \in \mathbb{N}$ such that $z_n \in D'$ for all $n > M$. By assumption, $z_n \neq z_\infty$, so $f(z_n) \neq 0$, which contradicts $f(z_n) = 0$.

This contradiction implies that our initial assumption $f \not\equiv 0$ is false, hence $f \equiv 0$ on $\Omega$.

**Corollary**: Let $f, g: \Omega \to \mathbb{C}$ be holomorphic functions on a connected open set $\Omega$. If $f = g$ on a sequence $\{z_n\}$ that converges to $z_\infty \in \Omega$ with $z_\infty \notin \{z_n\}$, then $f \equiv g$ on $\Omega$.  
**Proof**: Apply the theorem to the function $f - g$.

This theorem demonstrates the *isolated zeros* property of holomorphic functions: if a holomorphic function on a connected open set is not identically zero, then its zeros must be isolated.


> [!Note] Liouville's theorem
> Assume that $f:\mathbb{C}\to \mathbb{C}$ is holomorphic. If f is bounded, then f is constant.

^113820

Proof
We will show that $f'(z)=0$ for all $z\in \mathbb{C}$,
Let $D_{R}(z)$ be the open disc centered at z with radius R
Let $C_{R}(z)=\partial D_{R}(z)$
By cauchy theorem
$$
f'(z)= \frac{1}{2\pi i} \int_{C_{R}} \frac{f(\xi)}{(\xi-z)^{2}}d\xi$$
Then
$$\left| f'(z) \right| \leq \frac{\sup_{C_{R}}|f|}{R}$$
Then we let $R\to \\\infty$
we will get $f'(z)=0$
So f is constant


Example of the domain must be $\mathbb{C}$
Let $f:\mathbb{C}-\overline{D_{1}(0)}\to \mathbb{C},\: z\to \frac{1}{z}$
Then f is holomorphic and bounded by 1
Buf f is not constant

Theorem(代数学基本定理)
Let $f(z)=z^{n}+a_{n-1}z^{n-1}+\dots+a_{0}$ be a polynomial in $\mathbb{C}$
1 Then f has aroot in $\mathbb{C}$
2 We can factorize f into 
$$
f(z)=(z-z_{1})(z-z_{2})\dots
$$

Proof
The second part is a conseqence of the first part by using Euclidean division,
We will now prove 1
Assume by contradiction that $f(z)\neq0$ forall $z\in \mathbb{C}$
Let $g(z)=\frac{1}{f(z)}$. Then g is holomorphic on $\mathbb{C}$
we will use Liouvill theorem on g (proove g is bounded)
we see that 
$$
\left| f(z) \right| \geq |z|^{n}-(|a_{n-1}z^{n-1}|+\dots+|a_{0}|)
$$
Due to the value of $f(z)$ is dominated by $z^{n}$
Hence, there is R >0 s.t.
$$
|a_{n-1}z^{n-1}|+\dots+|a_{0}| \leq \frac{1}{2}|z^{n}|, \: if |z| \geq R
$$
Now we docompose $\mathbb{C}$ into two points
$\mathbb{C} = \overline{D_{R}(0)}\bigcup(\mathbb{C}-D_{R}(0))$
Since $\overline{D_{R}(0)}$ is compact
$\sup_{\overline{D_{R}(0)}}|g|$​ is a real number and it's finite
If $|z|\geq R$ ,then
$$
|g(z)|\leq \frac{1}{|f(z)|}\leq \frac{1}{|z|^{n}-(|a_{n-1}z^{n-1}|+\dots+|a_{n}|)}\leq \frac{1}{|z^{n}|- \frac{1}{2}|z|^{n}}= \frac{2}{|z^{n}|} \leq \frac{2}{R^{n}}
$$

In conclusion, for any $z\in \mathbb{C}$
$$
|g(z)|\leq \frac{2}{R^{n}}+\sup_{\overline{D_{n}(0)}}|g|
$$
Hence by Liouvilli;s theroem , g is constant
This is a contradiction

Because the degree of f must $\geq1$
