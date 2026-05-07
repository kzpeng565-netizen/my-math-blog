---
tags:
  - 抽象代数
  - 代数
---
命题 4.34 设整数 $n \geqslant 2$ ，其素因子分解是 $n=p_1^{m_1} \cdots p_k^{m_k}$ ，那么
（1）$Z_n \simeq Z_{p_1^{m_1}} \oplus \cdots \oplus Z_{p_k^{m_k}}$（环的直和）；
（2）$U\left(Z_n\right) \simeq U\left(Z_{p_1^{m_1}}\right) \times \cdots \times U\left(Z_{p_k^{m_k}}\right)$（群的直积）．


**证明**（1）对不同的 $i, j$ ，由于 $p_i^{m_i}$ 和 $p_j^{m_j}$ 互素，从而 $p_i^{m_i} \mathbb{Z}+p_j^{m_j} \mathbb{Z}=\mathbb{Z}$ ．对环 $\mathbb{Z}$ 和理想 $p_1^{m_1} \mathbb{Z}, \cdots, p_k^{m_k} \mathbb{Z}$ 运用推论 4．32 [[孙子定理(中国剩余定理)]]，知有满同态
$$
\theta: \mathbb{Z} \rightarrow Z_{p_1^{m_1}} \oplus \cdots \oplus Z_{p_k^{m_k}}, \quad x \rightarrow\left(x+p_1^{m_1} \mathbb{Z}, \cdots, x+p_k^{m_k} \mathbb{Z}\right),
$$
核为 $\operatorname{Ker} \theta=p_1^{m_1} \mathbb{Z} \cap \cdots \cap p_k^{m_k} \mathbb{Z}=n \mathbb{Z}$ ．

（2）因为 $Z_{p_1^{m_1}} \oplus \cdots \oplus Z_{p_k^{m_k}}$ 中的元素 $\left(x_1, \cdots, x_n\right)$ 可逆当且仅当诸 $x_i$ 在 $Z_{p_i^{m_i}}$中可逆，所以有群同构
$$
U\left(Z_{p_1^{m_1}} \oplus \cdots \oplus Z_{p_k^{m_k}}\right) \simeq U\left(Z_{p_1^{m_1}}\right) \times \cdots \times U\left(Z_{p_k^{m_k}}\right) .
$$
因此，要证的同构由（1）中的同构给出．

---


对于小于 $n$ 的正整数 $a$ ，它在 $Z_n$ 中是可逆的当且仅当 $a$ 与 $n$ 互素．这样的正整数的个数就是欧拉函数在 $n$ 处的值 $\varphi(n)$ 。换句话说，有

$$
|U(\mathbb{Z} / n \mathbb{Z})|=\varphi(n) .
$$
由命题 4．34知 $\varphi(n)=\prod_{i=1}^k \varphi\left(p_i^{m_i}\right)$ ．易见，$\varphi\left(p^m\right)=p^{m-1}(p-1)$ ．至此 $U\left(Z_n\right)$ 的阶是很清楚了．

**欧拉定理的证明**
有限群的元素的阶是群的阶的因子，因此对于和 $n$ 互素的整数 $a$ ，有
$$
a^{\varphi(n)} \equiv 1(\bmod n) .
$$
