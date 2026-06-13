---
epoch: 1781358173344
modelKey: "deepseek-v4-pro|deepseek"
topic: "Boundary Interior Disjointness Argument"



tags:
  - copilot-conversation
---

**user**: **第二部分老师给的方法:**
假设$p\in \partial M\cap \overset{{\circ}}{M}$ , 存在$p$的开领域$V$ 使得
$$
(V,p)\cong(\mathbb{R}_{+}^{^{2}},0),\quad (V,p)\cong(U,0),\:U\subset \mathbb{R}^{2}开集
$$
因此$\mathbb{R}^{2}_{+}-\{0\}\cong U-\{0\}$ 
则定义收缩映射: $r:U-0\to S^{1}(r)$, $x\to \frac{rx}{\left| x \right|}$ , 所以$r_{*}:\pi_{1}(U-0,y)\to \pi_{1}(S^{1}(r),-)\cong\mathbb{Z}$​	而且由于$r_{*}$是一个**满射**, 所以$\pi_{1}(U-0,y)\neq0$ 矛盾

**满射是因为**
$r \circ i=\operatorname{id}_{S^1(r)}$ 所以$r$是一个收缩映射, 这给出$r_{*}{\circ}i_{*}=id_{\pi_{1}(S^{1}(r))}$ , 所以$r_{*}$一定是满射

老师的做法是什么
[Context: Notes: 拓扑/10. 映射度&函子性&Van Kampen.md]
[Timestamp: 2026/06/13 21:42:53]

**ai**: 
<think>我们被问到“老师的做法是什么”，用户引用了笔记中关于“第二部分老师给的方法”的内容。用户可能想听我对老师做法的解释或总结。需要基于笔记中内容解释老师的方法。笔记中是习题11的证明，有学生自己做法和老师方法。老师方法的关键是：假设p在边界和内部交集，局部同胚于上半平面和R^2开集，导致U\{0}同胚于R^2_+\{0}，然后通过U\{0}的收缩映射r到S^1，诱导基本群满同态，推出矛盾。我需要清晰说明老师方法的逻辑。</think>老师的做法是利用**基本群的函子性**和**收缩映射诱导满同态**的性质，简洁地导出矛盾。具体思路如下：

---

1. **假设存在边界与内部的公共点**  
   设 $p \in \partial M \cap \overset{\circ}{M}$。由带边曲面的局部结构，存在 $p$ 的开邻域 $V$，使得：
   - 作为 $\partial M$ 上的点，有同胚 $(V, p) \cong (\mathbb{R}^2_+, 0)$；
   - 作为 $\overset{\circ}{M}$ 中的点，又有同胚 $(V, p) \cong (U, 0)$，其中 $U \subset \mathbb{R}^2$ 是某个开集。

   于是去掉点后得到同胚：
   $$
   \mathbb{R}^2_+ \setminus \{0\} \;\cong\; U \setminus \{0\}.
   $$

2. **构造 $U \setminus \{0\}$ 到 $S^1$ 的收缩映射**  
   对于 $\mathbb{R}^2$ 中的开集 $U$（包含原点），可以取一个足够小的圆 $S^1(r) \subset U$ 围绕 $0$，定义径向投影：
   $$
   r: U \setminus \{0\} \longrightarrow S^1(r), \quad
   x \longmapsto \frac{r x}{|x|}.
   $$
   这是一个连续映射，且限制在 $S^1(r)$ 上是恒等映射，即 $r \circ i = \operatorname{id}_{S^1(r)}$，其中 $i: S^1(r) \hookrightarrow U \setminus \{0\}$ 是包含映射。

3. **诱导基本群的满同态**  
   应用基本群函子 $\pi_1$，得到群同态：
   $$
   r_* : \pi_1(U \setminus \{0\}, y) \longrightarrow \pi_1(S^1(r), *) \cong \mathbb{Z}.
   $$
   由 $r \circ i = \operatorname{id}$ 可得 $r_* \circ i_* = \operatorname{id}_{\pi_1(S^1(r))}$，因此 $r_*$ **一定是满射**。

4. **导出矛盾**  
   另一方面，$\mathbb{R}^2_+ \setminus \{0\}$ 可强形变收缩为一点（例如沿径向收缩到上半平面的某条射线上的点），所以
   $$
   \pi_1(\mathbb{R}^2_+ \setminus \{0\}) = 0.
   $$
   由同胚 $\mathbb{R}^2_+ \setminus \{0\} \cong U \setminus \{0\}$，得
   $$
   \pi_1(U \setminus \{0\}, y) = 0.
   $$
   但 $r_*$ 是从平凡群到 $\mathbb{Z}$ 的满同态，这是不可能的。矛盾。

---

**老师方法的核心亮点**：  
不用像第一个方法那样构造复杂的包含链并讨论嵌入映射的合成，而是直接利用 $\mathbb{R}^2_+ \setminus \{0\}$ 的可缩性，再通过一个简单的径向收缩映射制造基本群的满射，从而一步得到矛盾。
[Timestamp: 2026/06/13 21:43:05]