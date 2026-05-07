---
tags:
  - 分析
title: 阿贝尔变换
aliases:
  - 阿贝尔变换
---
阿贝尔变换是指求和式 $\sum_{i=1}^n a_ib_i$ 的以下变换. 设 $A_k = \sum_{i=1}^k a_i$，再取 $A_0 = 0$，则
 $$
\begin{align*}
\sum_{i=1}^n a_ib_i &= \sum_{i=1}^n (A_i - A_{i-1}) b_i = \sum_{i=1}^n A_ib_i - \sum_{i=1}^n A_{i-1} b_i \\
&= \sum_{i=1}^n A_ib_i - \sum_{i=0}^{n-1} A_ib_{i+1} = A_nb_n - A_0b_1 + \sum_{i=1}^{n-1} A_i(b_i - b_{i+1}).
\end{align*}
$$
于是，
$$
\begin{align*}
\sum_{i=1}^n a_ib_i &= (A_nb_n - A_0b_1) + \sum_{i=1}^{n-1} A_i(b_i - b_{i+1}), 
\end{align*}
$$
即
$$\begin{align*}
\sum_{i=1}^n a_ib_i &= A_nb_n + \sum_{i=1}^{n-1} A_i(b_i - b_{i+1}), 
\end{align*}
$$
因为 $A_0 = 0$.

>[!阿贝尔-狄利克雷判别]
（1）$\sum a_{i}$收敛，$b_{i}$单调有界
（2）$\sum a_{i}$有界，$b_{i}$单调趋于0
以上条件成立其一，那么$\sum_{i=1}^{n}a_{i}b_{i}$是收敛的

^0a0364

