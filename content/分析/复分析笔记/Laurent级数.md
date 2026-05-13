---
tags:
  - 复分析
  - 分析
---
设函数 $f(z)$ 在以 $b$ 为圆心的环形区域 $R_1 \leqslant|z-b| \leqslant R_2$ 内单值解析，则对于环域内的任意点 $z, ~ f(z)$ 都可以用幂级数展开为
$$
f(z)=\sum_{-\infty}^{\infty} a_n(z-b)^n, \quad R_1<|z-b|<R_2
$$
其中
$$
a_n=\frac{1}{2 \pi \mathrm{i}} \oint_C \frac{f(\zeta)}{(\zeta-b)^{n+1}} \mathrm{~d} \zeta
$$
$C$是任意一条绕一圈的闭合曲线

此外 $\sum_{n=0}^{\infty} a_n(z-b)^n$ 被称为 $f(z)$ 的正则部分（normal part）（有时也称解析部分），其在 $|z-b|<R_2$ 内绝对收敛。而 $\sum_{n=-\infty}^{-1} a_n(z-b)^n$ 被称作主要部分，简称主部（principal part），其在 $|z-b|>R_1$ 外绝对收敛。两部分合起来就构成了洛朗级数

洛朗级数在$r<\left| z-b \right|<R$内闭一致收敛于$f(z)$ 

**洛朗展开也具有唯一性**。因此使用不同方法展开得到的双边幂级数也就是同一个洛朗级数

洛朗级数展开的例题

![[4e2135c56c556597d7377362e93c9560.jpg]]
