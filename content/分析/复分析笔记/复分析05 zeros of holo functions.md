---
tags:
  - 复分析
  - 分析
---
零点理论的结论:
1. 孤立性
2. 唯一性. 如果两个全纯函数在一个区域相等, 在两个函数是相等的
3. 存在一个小邻域$f(z)=(z-z_{0})^{n}g(z),g(z)\neq0$ . 邻域的大小取决于Taylor展开的半径, 也就是与奇点的距离.
4. 辐角原理 $k=\frac{1}{2\pi }\int_{\gamma} \frac{f'(z)}{f(z)}dz$ 
5. Rouche定理, 以及Rouche定理的推论 [[复分析习题08#例2|复分析习题08]] n阶零点意味着n次经过周围点

习题课补充的定理 
定理(Hunutz)
$\{f_{n}(z)\}\subset \mathcal{O}(\Omega)$ 内闭一致收敛到 $f(z)$. $\gamma \subset\Omega$ 可求长Jordan曲线, 则$\exists N$ 使得 $n\geq N$时, $f(z)$和$f_{n}(z)$在$\gamma$内部零点个数相同

## 1.1 Zeros of holomorphic functions

**Definition**: Let $f:\Omega \to \mathbb{C}$ be a holomorphic function. A point $z\in\Omega$ is called a **zero** of $f$ if $f(z)=0$.

> [!Note] Theorem 1.1: the decompostion of f on a zero point(just like the order of a zero in real number)
>Assume that $f$ is not constant. Let $z_{0}\in\Omega$ be a zero of $f$. Then there is a unique $n\in \mathbb{N}$, a neighborhood $D$ of $z_{0}$, and a nowhere zero holomorphic function $g$ on $D$ such that
>$$
>f(z)=(z-z_{0})^{n}\cdot g(z)
>$$

### 1.1.1 Proof of Theorem 1.1

We choose $D$ so that $f$ has a series expansion
$$
f(z) = \sum_{k=0}^{\infty} a_k (z - z_0)^k.
$$
Since $f$ is not identically zero near $z_0$, there exists a smallest integer $n$ such that $a_n \neq 0$. Then, we can write
$$
f(z) = (z - z_0)^n [a_n + a_{n+1}(z - z_0) + \cdots] = (z - z_0)^n g(z),
$$
where $g$ is defined by the series in brackets, and hence is holomorphic, and is nowhere vanishing for all $z$ close to $z_0$ (since $a_n \neq 0$). 

To prove the uniqueness of the integer $n$, suppose that we can also write
$$
f(z) = (z - z_0)^n g(z) = (z - z_0)^m h(z)
$$
where $h(z_0) \neq 0$. If $m > n$, then we may divide by $(z - z_0)^n$ to see that
$$
g(z) = (z - z_0)^{m-n} h(z)
$$
and letting $z \rightarrow z_0$ yields $g(z_0) = 0$, a contradiction. If $m < n$ a similar argument gives $h(z_0) = 0$, which is also a contradiction. We conclude that $m = n$, thus $h = g$, and the theorem is proved.

**Definition**: Such $n$ is called the **multiplicity** or the **order** of the zero $z_{0}$ of $f$. $z_{0}$ is called **simple** if $n=1$.

## 1.2 Poles of holomorphic functions

**Definition**: A **deleted neighborhood** of $z_{0}$ is an open disc centered at $z_{0}$, minus the point $z_{0}$, that is, the set
$$
\{z : 0 < |z - z_{0}| < r\}
$$
for some $r > 0$.

**Definition**: We say that a function $f$ defined in a deleted neighborhood of $z_{0}$ has a **pole** at $z_{0}$, if the function $1/f$, defined to be zero at $z_{0}$, is holomorphic in a full neighborhood of $z_{0}$.

Alternatively, we say that $f$ has a pole at $z_{0}$ if the following function is holomorphic in a neighborhood of $z_{0}$:
$$
g(z)=
\begin{cases}
\frac{1}{f(z)} & \text{if } z\neq z_{0}\\
0 & \text{if } z=z_{0}
\end{cases}
$$

The **order** of the pole $z_{0}$ of $f$ is defined as the order of the zero $z_{0}$ of $g$.

> [!Note] Theorem 1.2
>If $f$ has a pole at $z_0 \in \Omega$, then in a neighborhood of that point there exist a non-vanishing holomorphic function $h$ and a unique positive integer $n$ such that
>$$
>f(z) = (z - z_0)^{-n} h(z).
>$$

### 1.2.1 Proof of Theorem 1.2

By the previous theorem we have $1/f(z) = (z - z_0)^n g(z)$, where $g$ is holomorphic and non-vanishing in a neighborhood of $z_0$, so the result follows with $h(z) = 1/g(z)$.


> [!Note] Theorem 1.3
>If $f$ has a pole of order $n$ at $z_0$, then
>$$
>f(z) = \frac{a_{-n}}{(z - z_0)^n} + \frac{a_{-n+1}}{(z - z_0)^{n-1}} + \cdots + \frac{a_{-1}}{(z - z_0)} + G(z),
>$$
>where $G$ is a holomorphic function in a neighborhood of $z_0$.

### 1.2.2 Proof of Theorem 1.3

The proof follows from the multiplicative statement in the previous theorem. Indeed, the function $h$ has a power series expansion
$$
h(z) = A_0 + A_1(z - z_0) + \cdots
$$
so that
$$
f(z) = (z - z_0)^{-n} (A_0 + A_1(z - z_0) + \cdots) = \frac{a_{-n}}{(z - z_0)^n} + \frac{a_{-n+1}}{(z - z_0)^{n-1}} + \cdots + \frac{a_{-1}}{(z - z_0)} + G(z).
$$

The sum
$$
\frac{a_{-n}}{(z - z_0)^n} + \frac{a_{-n+1}}{(z - z_0)^{n-1}} + \cdots + \frac{a_{-1}}{(z - z_0)}
$$
is called the **principal part** of $f$ at the pole $z_0$, and the coefficient $a_{-1}$ is the **residue** of $f$ at that pole.

### 1.2.3 Alternative Proof of Theorem 1.3

We prove that $(z-z_{0})^{n}\cdot f(z)=h(z)$ is a holomorphic function in a neighborhood of $z_{0}$ and $h(z)\neq0$. To see this, we observe that $g(z)= \frac{1}{f(z)}$ can be written as $g(z)=(z-z_{0})^{n}\cdot b(z)$ where $b$ is holomorphic and nowhere zero near $z_{0}$.

Meanwhile, $h(z)=\sum_{i=0}^{+\infty}c_{i}(z-z_{0})^{i}$ with $c_{0}\neq0$ in a neighborhood of $z_{0}$. By dividing by $(z-z_{0})^{n}$ we obtain $f(z)=\sum_{i=0}^{+\infty} c_{i}(z-z_{0})^{i-n}$ for $z\neq z_{0}$. This completes the proof.

## 1.3 Remarks

**Remark**:
1. The principal part may have more than 1 term (more than $\frac{a_{-n}}{(z-z_{0})^{n}}$).
2. The principal part can be written as $\frac{p(z)}{(z-z_{0})^{n}}$ where $p$ is a polynomial of degree $\leq n-1$ and $p(z_{0})\neq0$.

