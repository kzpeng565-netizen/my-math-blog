---
epoch: 1781963170189
modelKey: deepseek-reasoner|deepseek
tags:
  - copilot-conversation
topic: Green's Functions Conformal Invariance
---

**user**: 1. 理论迁移：为什么格林函数是共形不变量？回忆一下，区域 $\Omega_z$ 内的格林函数 $G(z, z_0)$ 必须满足三个铁律：内部调和： 在 $\Omega_z \setminus \{z_0\}$ 内，$\Delta_z G = 0$。边界为零： 当 $z \to \partial\Omega_z$ 时，$G = 0$。对数奇点： 在源点 $z_0$ 附近，它的核心长得像 $-\frac{1}{2\pi}\ln|z-z_0|$。现在我们构造一个新函数：$g(z) = G_{\Omega_w}(f(z), f(z_0))$。我们来看看这个新函数是否满足上面三个铁律：检验边界： 因为 $f(z)$ 把 $\partial\Omega_z$ 映射到了 $\partial\Omega_w$。当 $z$ 走向边界时，$f(z)$ 也走向了 $w$ 空间的边界。而 $G_{\Omega_w}$ 在它的边界上是 $0$。所以 $g(z)$ 在边界上完美等于 $0$。检验调和性： 根据我们上一节聊的“共形映射保持调和性”，既然 $G_{\Omega_w}$ 是调和的，把它和一个解析函数 $f(z)$ 复合，得到的新函数 $g(z)$ 必然也是调和的。检验奇点（最精妙的一击）：在 $w$ 空间里，奇点长这样：$-\frac{1}{2\pi}\ln|w-w_0|$。代入映射 $w = f(z)$ 和 $w_0 = f(z_0)$，因为 $f(z)$ 是解析的且导数 $f'(z_0) \neq 0$，利用一阶泰勒展开，在 $z_0$ 附近有：$$f(z) - f(z_0) \approx f'(z_0)(z-z_0)$$代入对数中：$$-\frac{1}{2\pi}\ln|f'(z_0)(z-z_0)| = -\frac{1}{2\pi}\ln|z-z_0| - \frac{1}{2\pi}\ln|f'(z_0)|$$看！那个最重要的奇点 $-\frac{1}{2\pi}\ln|z-z_0|$ 被原封不动地保留了下来。多出来的那个 $-\frac{1}{2\pi}\ln|f'(z_0)|$ 只是一个常数，它会被吸收到用于修正边界的正则调和函数里。既然 $g(z)$ 完美满足了这三大铁律，由格林函数的唯一性定理，$g(z)$ 就是 $\Omega_z$ 的格林函数。

帮我把它写成适合放在笔记当中的文本, 去掉多余的修辞, 保留重点, 精简内容
[Context: Notes: 分析/微分方程/13. 格林函数.md]
[Timestamp: 2026/06/20 21:46:10]