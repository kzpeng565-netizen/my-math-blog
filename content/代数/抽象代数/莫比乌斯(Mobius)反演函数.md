---
tags:
  - 抽象代数
  - 代数
---
#抽象代数 #数论
## 1. 定义
莫比乌斯（Möbius）反演公式及其应用 数论中由如下规则定义的函数称为莫比乌斯函数：

$$
\mu(n)= \begin{cases}1, & \text { 若 } n=1, \\ (-1)^k, & \text { 若 } n=p_1 \cdots p_k, \text { 诸 } p_i \text { 是不同的素数, } \\ 0, & \text { 若 } n \text { 被某个素数的平方整除. }\end{cases}
$$

很清楚，若 $\mu$ 在 $m$ 和 $n$ 处的值均不为 0 且 $m$ 和 $n$ 互素，则有 $\mu(m n)=\mu(m) \mu(n)$ ．这是说，$\mu$ 是乘性函数。同样显然，如 $n=p_1^{m_1} \cdots p_r^{m_r}$ ，则

$$
\sum_{d \mid n} \mu(d)=\sum_{d \mid n_0} \mu(d),
$$


其中 $n_0=p_1 \cdots p_r$ 是 $n$ 的不含素因子平方的最大因子．对于固定的 $s$ ，数 $n_0$ 的因子 $d=p_{i_1} \cdots p_{i_s}$ 的个数等于 $\binom{r}{s}$ ．因此，当 $n>1$ 时，有

$$
\sum_{d \mid n} \mu(d)=\sum_{d \mid n_0} \mu(d)=\sum_{s=0}^r\binom{r}{s}(-1)^s
$$
$$
(x+y)^r=\sum_{s=0}^r C_r^s x^{r-s} y^s\implies\sum _{s=0}^{r}C_{r}^{s}(-1)^{s}=(1-1)^{r=0}
$$
（左端的求和指标 $d$ 取遍整数 $n$ 的所有正整数因子）．最后得到公式
$$
\sum_{d \mid n} \mu(d)=\sum_{d \mid n}\mu\left( \frac{n}{d} \right)= \begin{cases}1, & \text { 若 } n=1, \\ 0, & \text { 若 } n>1 .\end{cases}
$$
然后我们给出它的推广
$$
\sum_{d|n| m} \mu\left(\frac{m}{n}\right)= \begin{cases}1, & \text { 若 } d=m, \\ 0, & \text { 若 } d \mid m, d<m\end{cases}
$$
证明是让$n=n'd,m=m'd$ 得到原有的式子

### 1.1 加法反演公式
设 $f$ 和 $g$ 是从正整数集合 $\mathbb{N} \backslash\{0\}$ 到 $M$ 的任意两个函数 $(M$ 等于 $\mathbb{Z}, \mathbb{R}, K[x]$等等），若它们由关系式
$$
f(n)=\sum_{d \mid n} g(d)
$$
联系起来，则
$$
g(n)=\sum_{d \mid n} \mu\left(\frac{n}{d}\right) f(d) .
$$

### 1.2 乘法反演公式

对乘法，有类似的反演公式：若 $f(n)=\prod_{d \mid n} g(d)$ ，则
$$
g(n)=\prod_{d \mid n} f(d)^{\mu(n / d)}
$$
证明只需要让$\tilde{f}(n)=\ln f(n),\tilde{g}(d)=\ln g(d)$ 

## 2. 应用

[[习题13 域扩张#练习5]] $x^{p^{n}}-x$在$\mathbb{F}_{p}$中的因式分解.

