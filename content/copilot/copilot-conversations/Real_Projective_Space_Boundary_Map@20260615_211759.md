---
epoch: 1781529479150
modelKey: "deepseek-v4-pro|deepseek"
topic: "Real Projective Space Boundary Map"



tags:
  - copilot-conversation
---

**user**: 可以。这里关键不是“背 (0,2,0,2)”，而是要看清楚胞腔边界映射 (d_k) 的 degree 是怎么来的。

我们要证明：

[
d_k:C_k(\mathbb{R}P^n)\to C_{k-1}(\mathbb{R}P^n)
]

是

[
d_k=
\begin{cases}
0,& k\text{ 为奇数},\
2,& k\text{ 为偶数}.
\end{cases}
]

更精确地说，在选定合适方向后，偶数维是乘 (2)。如果方向选法不同，也可能写成乘 (-2)，但同调群不变。

---

## 1. (\mathbb{R}P^n) 的 CW 结构

实射影空间有自然滤过：

[
\mathbb{R}P^0\subset \mathbb{R}P^1\subset\cdots\subset \mathbb{R}P^n.
]

其中

[
\mathbb{R}P^k-\mathbb{R}P^{k-1}
]

是一个开 (k)-胞腔。因此 (\mathbb{R}P^n) 每一维都有一个胞腔：

[
e^0,e^1,e^2,\dots,e^n.
]

所以胞腔链群是

[
C_k(\mathbb{R}P^n)\cong \mathbb Z,\qquad 0\le k\le n.
]

现在关键就是计算每个

[
d_k:\mathbb Z\to \mathbb Z.
]

---

## 2. 第 (k) 个胞腔是怎么贴上的

(\mathbb{R}P^k) 是从 (\mathbb{R}P^{k-1}) 贴一个 (k)-cell 得到的：

[
\mathbb{R}P^k=\mathbb{R}P^{k-1}\cup_f e^k.
]

这个 (k)-cell 的闭包可以看成一个闭球 (D^k)，它的边界是 (S^{k-1})。

贴附映射是

[
f:S^{k-1}\to \mathbb{R}P^{k-1},
]

它就是自然商映射：

[
x\mapsto [x],
]

其中 ([x]) 表示把 (x) 和 (-x) 识别起来。也就是说，边界球面 (S^{k-1}) 上的对径点被识别：

[
x\sim -x.
]

所以第 (k) 个胞腔的边界映射本质上来自

[
S^{k-1}\to \mathbb{R}P^{k-1}.
]

---

## 3. 胞腔边界映射要算的是 degree

胞腔边界公式告诉我们，(d_k) 的系数等于下面这个复合映射的 degree：

[
S^{k-1}\xrightarrow{f}\mathbb{R}P^{k-1}\longrightarrow
\mathbb{R}P^{k-1}/\mathbb{R}P^{k-2}.
]

由于 (\mathbb{R}P^{k-1}/\mathbb{R}P^{k-2}) 正好把 ((k-2))-骨架压成一点，只剩下那个 ((k-1))-cell，所以

[
\mathbb{R}P^{k-1}/\mathbb{R}P^{k-2}\cong S^{k-1}.
]

因此我们要算的是一个映射

[
g:S^{k-1}\to S^{k-1}
]

的 degree。

也就是说：

[
d_k=\deg(g).
]

---

## 4. 关键：这个映射的 degree 是 (1+(-1)^k)

把边界球面 (S^{k-1}) 分成上下两个半球：

[
S^{k-1}=D_+^{k-1}\cup D_-^{k-1}.
]

这里 (D_+^{k-1}) 和 (D_-^{k-1}) 的公共边界是赤道 (S^{k-2})。

在射影空间里，对径点被识别，所以：

* 上半球 (D_+^{k-1}) 贴到 ((k-1))-cell 上；
* 下半球 (D_-^{k-1}) 也贴到同一个 ((k-1))-cell 上。

赤道 (S^{k-2}) 会落到 (\mathbb{R}P^{k-2})，而在商空间 (\mathbb{R}P^{k-1}/\mathbb{R}P^{k-2}) 中，赤道被压成一个点。

所以 (g:S^{k-1}\to S^{k-1}) 可以理解为：

上半球给出一次覆盖，下半球也给出一次覆盖，但两者的方向可能相同，也可能相反。

上半球的贡献取为 (+1)。

下半球和上半球之间差了一个对径映射：

[
A:S^{k-1}\to S^{k-1},\qquad A(x)=-x.
]

对径映射在 (S^{k-1}) 上的 degree 是

[
\deg(A)=(-1)^k.
]

因为一般地，(S^m) 上对径映射的 degree 是 ((-1)^{m+1})。这里 (m=k-1)，所以就是

[
(-1)^{(k-1)+1}=(-1)^k.
]

因此两个半球的 degree 贡献相加：

[
\deg(g)=1+(-1)^k.
]

所以

[
d_k=1+(-1)^k.
]

于是：

当 (k) 为奇数时，

[
1+(-1)^k=1-1=0.
]

当 (k) 为偶数时，

[
1+(-1)^k=1+1=2.
]

所以

[
d_k=
\begin{cases}
0,& k\text{ 为奇数},\
2,& k\text{ 为偶数}.
\end{cases}
]

---

## 5. 低维例子帮助理解

### (d_1=0)

(\mathbb{R}P^1) 是一个圆。它的 CW 分解有一个 (0)-cell 和一个 (1)-cell。

这个 (1)-cell 的两个端点都贴到同一个 (0)-cell 上，所以

[
d_1(e^1)=v-v=0.
]

因此

[
d_1=0.
]

---

### (d_2=2)

(\mathbb{R}P^2) 是在 (\mathbb{R}P^1\cong S^1) 上贴一个 (2)-cell。

它的边界是 (S^1)，贴附映射是

[
S^1\to \mathbb{R}P^1\cong S^1.
]

这个映射是二重覆盖，也就是边界绕底下的 (S^1) 两圈。

所以

[
d_2:\mathbb Z\to \mathbb Z
]

是乘 (2)。

因此

[
d_2(e^2)=2e^1.
]

这就是为什么

[
H_1(\mathbb{R}P^2)\cong \mathbb Z/2.
]

---

### (d_3=0)

(\mathbb{R}P^3) 是在 (\mathbb{R}P^2) 上贴一个 (3)-cell。

这时 (d_3) 要看

[
S^2\to \mathbb{R}P^2\to \mathbb{R}P^2/\mathbb{R}P^1\cong S^2.
]

边界 (S^2) 的上下两个半球都映到那个 (2)-cell 上，但由于 (k=3) 是奇数，它们的方向相反，一个贡献 (+1)，一个贡献 (-1)。

所以总 degree 是

[
1-1=0.
]

因此

[
d_3=0.
]

这就是为什么 (\mathbb{R}P^3) 有顶维同调

[
H_3(\mathbb{R}P^3)\cong \mathbb Z.
]

---

## 6. 最终链复形

所以 (\mathbb{R}P^n) 的胞腔链复形是

[
0\to \mathbb Z\xrightarrow{d_n}\mathbb Z\xrightarrow{d_{n-1}}\cdots
\xrightarrow{d_4}\mathbb Z\xrightarrow{d_3}\mathbb Z\xrightarrow{d_2}\mathbb Z\xrightarrow{d_1}\mathbb Z\to 0,
]

其中

[
d_k=
\begin{cases}
0,& k\text{ 为奇数},\
2,& k\text{ 为偶数}.
\end{cases}
]

也就是

[
\cdots\xrightarrow{2}\mathbb Z\xrightarrow{0}\mathbb Z\xrightarrow{2}\mathbb Z\xrightarrow{0}\mathbb Z.
]

一句话概括：

**(\mathbb{R}P^n) 的第 (k) 个胞腔边界来自 (S^{k-1}\to \mathbb{R}P^{k-1}) 的对径识别；上下两个半球都映到同一个 ((k-1))-cell。它们的方向贡献是 (1) 和 ((-1)^k)，所以 (d_k=1+(-1)^k)，即奇数为 (0)，偶数为 (2)。**


帮我把它转化为精炼的笔记式文字, 不要有大标题
[Context: Notes: 拓扑/RP^n与CP^n的胞腔分解.md]
[Timestamp: 2026/06/15 21:17:59]

**ai**: 
<think>我们需要理解用户需求。用户给出了一大段关于RP^n的胞腔分解和边界映射的详细解释，然后要求“帮我把它转化为精炼的笔记式文字, 不要有大标题”。同时，我们处于Obsidian笔记环境中，有一个活动笔记“RP^n与CP^n的胞腔分解.md”，内容是空的。用户希望把这段内容精炼成笔记，放入这个笔记中。而且要求“不要有大标题”，可能指不要使用一级标题（#），但可能保留二级标题或更小标题？用户说“不要有大标题”，通常指不要使用#这种大标题。可以转成二级标题或三级标题。不过，最好检查用户要求：把这段解释转化为精炼的笔记式文字，格式符合Obsidian，不要有大标题。可能需要将内容浓缩，保留关键步骤和结论，但简化冗长部分。由于活动笔记标题是“RP^n与CP^n的胞腔分解”，可能还要包括CP^n？用户只给出了RP^n部分，但可能后面还有CP^n的，不过目前只要求转化给出的这段RP^n。需要把这段数学解释转化为精炼笔记。

处理方式：将用户提供的内容精炼，去除一些口语化解释，保留核心定义、关键计算、最终链复形。同时保持数学严谨性。使用markdown，用LaTeX公式（$...$）。使用列表、小标题（如###）也可以，但不要有大标题（#）。我可以用加粗文本作为小节标题，或者直接用###。但用户说不要有大标题，那可能是指不要用一级标题#，但二级标题##可能允许？保险起见，就不用任何标题，仅用加粗分段。或者用无序列表形式。笔记式文字意味着简洁，有逻辑。我将把内容整理成几个部分：胞腔分解、贴附映射、边界映射计算（包括度计算、对径映射的度、公式）、最终链复形和同调推论（如果提到）。确保公式正确，用$...$，表格？可能不需要。注意不要使用大括号的LaTeX。原内容有很多align环境？但用户用了 \(...\) 和 \[...\]。应转为 $...$ 和 $$...$$，但Obsidian中行内用$，行间用$$。要求使用$，不要用\[。第5点说“Always use $'s instead of \[ etc. for LaTeX equations.” 所以所有方程都用$或$$。例如d_k可以用$d_k$。并且公式中d_k的cases等用$$。但是Obsidian中支持cases。需要将原文的\[...\]转为$$...$$，\(...\)转为$...$。精炼笔记中应该去掉“我们要证明”，直接给出结论。

我将这样构建笔记：

- 开头：RP^n的CW结构，每一维一个胞腔。
- 胞腔链群：$C_k(\mathbb{R}P^n) \cong \mathbb Z$。
- 边界映射$d_k$的计算：来自贴附映射$S^{k-1}\to \mathbb{R}P^{k-1}$，结合商映射到球面，度由上下半球贡献。
- 对径映射度：$\deg(A)=(-1)^k$，因此$d_k = 1 + (-1)^k$。
- 结论：$d_k$奇数为0，偶数为2。
- 低维例子（简化）。
- 最终链复形：序列，点明同调意义（H_1(RP^2) = Z/2等，但不是必须，如果精炼可以提）。原内容最后一句话总结。

因为不要大标题，我可以以“**RP^n的胞腔分解**”等粗体作为小节，但不要用#。可能需要添加Obsidian链接？没有需要。还要注意标签？不需要。最终输出笔记内容，直接放入活动笔记。但用户只是要求我帮转化为精炼笔记式文字，我应该输出这个文字，让他复制进去。可能直接回复内容。因为我是Copilot，要给出回答。在回复中，我可以给出精炼后的markdown文本。同时，由于活动笔记是空的，我可以提示这将被放入该笔记。最好直接回复精炼内容，用代码块？不用，直接用markdown。我会把内容整理好，用Obsidian兼容的格式。

还要注意保持语言为中文，原内容中文。精炼也要中文。避免英文除非术语。使用$...$。最终输出。用户不需要大标题，所以片段不应以#开头。

我会生成如下文本：

**$\mathbb{R}P^n$ 的胞腔分解** (粗体作为节标题)

- 自然滤过 $\mathbb{R}P^0 \subset \mathbb{R}P^1 \subset \cdots \subset \mathbb{R}P^n$，每个 $\mathbb{R}P^k \setminus \mathbb{R}P^{k-1}$ 是一个开 $k$-胞腔。故每个维数恰有一个胞腔 $e^0,\dots,e^n$。
- 胞腔链群 $C_k(\mathbb{R}P^n) \cong \mathbb Z$，$0\le k\le n$。

**贴附映射**

第 $k$ 个胞腔由贴附 $f:S^{k-1}\to \mathbb{R}P^{k-1}$ 得到，
$$
f(x)=[x],\quad x\sim -x.
$$
即边界球面的对径点被识别。

**边界映射的度**

胞腔边界 $d_k : C_k \to C_{k-1}$ 的系数等于复合映射的度：
$$
S^{k-1} \xrightarrow{f} \mathbb{R}P^{k-1} \twoheadrightarrow \mathbb{R}P^{k-1}/\mathbb{R}P^{k-2} \cong S^{k-1},
$$
记作 $g:S^{k-1}\to S^{k-1}$，于是 $d_k = \deg(g)$。

将 $S^{k-1}$ 分为上下两个半球 $D_+^{k-1}\cup D_-^{k-1}$，它们都映满唯一的 $(k-1)$-胞腔。上半球贡献 $+1$，下半球经对径映射 $A(x)=-x$ 后再贡献。
- 对径映射的度：$\deg(A)=(-1)^k$。
- 因此 $\deg(g) = 1 + (-1)^k$。

综上，
$$
d_k = 1+(-1)^k =
\begin{cases}
0, & k\text{ 为奇数},\\
2, & k\text{ 为偶数}.
\end{cases}
$$

**低维验证**
- $d_1=0$：$\mathbb{R}P^1\cong S^1$ 的 $1$-胞腔两端粘在同一点，边界为零。
- $d_2=2$：$S^1\to\mathbb{R}P^1\cong S^1$ 是二重覆盖，故乘 $2$；$H_1(\mathbb{R}P^2)\cong \mathbb Z/2$。
- $d_3=0$：$S^2$ 的上下半球方向相反，度抵消。

**链复形**
$$
0 \to \mathbb Z \xrightarrow{d_n} \mathbb Z \xrightarrow{d_{n-1}} \cdots
\xrightarrow{2} \mathbb Z \xrightarrow{0} \mathbb Z \xrightarrow{2} \mathbb Z \xrightarrow{0} \mathbb Z \to 0,
$$
其中 $d_k = 0$（$k$ 奇）或 $2$（$k$ 偶），即交替 $0,2,0,2,\dots$。

（注意：方向选择不同时，$d_k$ 可能为 $-2$，同调不变。）

一句总结：边界映射的度来自对径识别的上下半球贡献 $1$ 与 $(-1)^k$ 之和。

这样就完成了精炼。不要大标题，所以没有#或##。我用粗体作为标题，这样就是笔记式文字。同时对于Obsidian，内部链接可能不需要。我将在回复中输出这个内容，并可以说明“可以放入笔记中”。由于用户要求“帮我把它转化为精炼的笔记式文字”，我就直接给出。注意环境：活动笔记是空的，我应该输出这个精炼内容。另外，用户可能也想包含CP^n？但查询只给了RP^n，CP^n部分可能需要另行处理。我只能就提供的文本处理。所以最终回复提供这段精炼笔记。</think>**$\mathbb{R}P^n$ 的胞腔分解**  
自然滤过 $\mathbb{R}P^0 \subset \mathbb{R}P^1 \subset \cdots \subset \mathbb{R}P^n$，每个 $\mathbb{R}P^k \setminus \mathbb{R}P^{k-1}$ 是一个开 $k$-胞腔，故每个维数恰有一个胞腔 $e^0,\dots,e^n$。  
胞腔链群 $C_k(\mathbb{R}P^n) \cong \mathbb Z$，$0\le k\le n$。

**贴附映射**  
第 $k$ 个胞腔通过商映射粘贴：  
$$f:S^{k-1}\to \mathbb{R}P^{k-1},\quad f(x)=[x],\quad x\sim -x.$$  
即边界球面的对径点被识别。

**边界映射的度**  
$d_k: C_k \to C_{k-1}$ 的系数等于以下复合映射的度：  
$$S^{k-1} \xrightarrow{f} \mathbb{R}P^{k-1} \twoheadrightarrow \mathbb{R}P^{k-1}/\mathbb{R}P^{k-2} \cong S^{k-1},$$  
记作 $g:S^{k-1}\to S^{k-1}$，于是 $d_k = \deg(g)$。

将 $S^{k-1}$ 分为上下两个半球 $D_+^{k-1}\cup D_-^{k-1}$；它们都映满同一个 $(k-1)$-胞腔。上半球贡献 $+1$，下半球需经过对径映射 $A(x)=-x$ 再贡献。  
对径映射的度：$\deg(A)=(-1)^k$。  
因此  
$$\deg(g)=1+(-1)^k.$$

于是  
$$ d_k = 1+(-1)^k =
\begin{cases}
0, & k\text{ 为奇数},\\
2, & k\text{ 为偶数}.
\end{cases}
$$

**低维验证**  
- $d_1=0$：$1$-胞腔两端粘在同一点，边界为零。  
- $d_2=2$：$S^1\to \mathbb{R}P^1\cong S^1$ 是二重覆盖，故乘 $2$；这给出 $H_1(\mathbb{R}P^2)\cong \mathbb Z/2$。  
- $d_3=0$：$S^2$ 的上下半球方向相反，度抵消，因此 $H_3(\mathbb{R}P^3)\cong \mathbb Z$。

**链复形**  
$$
0 \to \mathbb Z \xrightarrow{d_n} \mathbb Z \xrightarrow{d_{n-1}} \cdots
\xrightarrow{2} \mathbb Z \xrightarrow{0} \mathbb Z \xrightarrow{2} \mathbb Z \xrightarrow{0} \mathbb Z \to 0,
$$
其中 $d_k$ 交替为 $0$（$k$ 奇）或 $2$（$k$ 偶）。若方向选择不同，可能出现 $-2$，同调群不变。

**一句话**  
边界映射的度来自对径识别下上下半球贡献 $1$ 与 $(-1)^k$ 之和。
[Timestamp: 2026/06/15 21:18:42]

**user**: 我们得到链复形之后, 怎么样计算出真正的胞腔同调, 给出简单的计算过程和结果
[Context: Notes: 拓扑/RP^n与CP^n的胞腔分解.md]
[Timestamp: 2026/06/15 21:19:39]

**ai**: 
<think>我们需要回答：在得到RP^n的胞腔链复形之后，如何计算胞腔同调，给出简单的计算过程和结果。注意我们已经有了链复形，即C_k都是Z，d_k交替是0或2（或乘2）。要计算同调群H_k = ker(d_k)/im(d_{k+1})。

我们需要针对不同的n和k，分情况计算。注意n固定，链复形从0到n。链复形中C_k = Z，如果k > n则为0。边界映射d_k: C_k -> C_{k-1}，对于k奇数d_k=0，对于k偶数d_k=乘法2（取生成元e_k乘2，即d_k(e_k)=2 e_{k-1}）。实际上，对于偶数k，d_k是乘以2的同态Z -> Z。对于奇数k，d_k是零同态。

要计算H_k，需要知道ker(d_k)和im(d_{k+1})。由于是整数系数的链复形，这些都是Z的子群。

我们分别考虑不同k的情况：

- 当k=0时，H_0 = ker(d_0)/im(d_1)。d_0: C_0 -> 0，所以ker(d_0)=C_0=Z。d_1: C_1 -> C_0。若n>=1，C_1存在。k=1是奇数，d_1=0。所以im(d_1)=0。因此H_0 = Z/0 = Z。通常RP^n是连通的，所以H_0=Z。注意n=0的情况？RP^0=pt，C_0=Z，d_0=0，没有C_1，所以H_0=Z。统一H_0=Z。

- 当k=n（顶维）时，C_{n+1}=0，所以im(d_{n+1})=0。需要看ker(d_n)。d_n: C_n -> C_{n-1}。根据d_n规则：n奇时d_n=0，所以ker(d_n)=Z；n偶时d_n=2（乘2），ker(d_n)=0（因为d_n(a e_n)=2a e_{n-1}=0仅当a=0）。因此：
  若n奇，H_n = Z/0 = Z。
  若n偶，H_n = 0/0 = 0？等等，ker(d_n)=0，所以H_n=0。但注意对于偶数n，比如n=2，RP^2的H_2是什么？我们已知H_2(RP^2)=0，因为它是不可定向紧流形，顶维同调是Z如果可定向，否则0。确实H_2=0。所以正确。

- 对于中间的k（0<k<n），需要区分k的奇偶性。同时要考虑d_k和d_{k+1}。

链复形片段：C_{k+1} -> C_k -> C_{k-1}。d_{k+1}和d_k。对于特定的k，我们需要知道d_{k+1}和d_k的规则，它们取决于k+1和k的奇偶性。注意k+1的奇偶性与k相反。所以有以下情况：

情况1：k是奇数。那么k奇数 => d_k = 0。k+1是偶数 => d_{k+1} = 乘法2。
因此，ker(d_k) = C_k = Z。im(d_{k+1}) = 2Z（由2生成的子群，即偶数）。所以H_k = Z / 2Z ≅ Z/2。

情况2：k是偶数（且0<k<n）。那么k偶数 => d_k = 乘法2。k+1是奇数 => d_{k+1} = 0。
此时，ker(d_k) = 0（因为乘2是单射？不，乘2从Z到Z，如果考虑一般群，乘2核为0；所以ker(d_k)=0）。im(d_{k+1}) = 0。所以H_k = 0/0 = 0。

因此，中间同调：奇数维为Z/2，偶数维为0（除了0和可能顶维n）。注意当n本身是偶数时，顶维n也是偶数，我们上面算的H_n=0，符合偶数维为0。当n奇数时，顶维n是奇数，H_n=Z，这与“奇数维中间为Z/2”不同，因为此时k=n，d_{n+1}=0，且d_n=0，所以H_n=Z，不是Z/2。所以我们需要区分0<k<n和k=n。另外k=0始终是Z。

总结：对于RP^n：
- H_0 = Z。
- 对于0<k<n：若k奇，H_k ≅ Z/2；若k偶，H_k = 0。
- H_n：
  - 若n奇，H_n = Z。
  - 若n偶，H_n = 0。

也可以统一写：当n为奇数时，H_n(RP^n)=Z，其余中间奇数维同调为Z/2，偶数维为0；当n为偶数时，所有大于0的偶数维同调为0，奇数维同调为Z/2（但n偶数时没有奇数维顶维？n本身偶数，所以顶维是偶数，同调0；中间奇数维< n都是Z/2）。例如：n=1: H_0=Z, H_1=Z (n=1奇数，所以H_1=Z)。n=2: H_0=Z, H_1=Z/2, H_2=0。n=3: H_0=Z, H_1=Z/2, H_2=0, H_3=Z。n=4: H_0=Z, H_1=Z/2, H_2=0, H_3=Z/2, H_4=0。等等。这些与已知同调相符。

现在要求“给出简单的计算过程和结果”，所以我会先写链复形，然后分情况计算ker和im，最后给出结果表。

需要用Obsidian笔记格式，精炼，不要大标题，用粗体小节。还要注意，我们之前已经有了链复形的那段笔记，现在要在其后补充计算同调的内容，或者作为单独部分？用户问的是“我们得到链复形之后, 怎么样计算出真正的胞腔同调, 给出简单的计算过程和结果”，我可以直接回答，仿佛在笔记中继续。之前回答的精炼笔记最后是链复形。现在继续写计算同调即可。所以我会输出以下内容：

**胞腔同调的计算**

（然后简要说明）已知链复形和d_k。然后分情况计算：

- $k=0$: $\ker d_0 = \mathbb Z$, $\operatorname{im} d_1 = 0$ $\Rightarrow H_0 = \mathbb Z$。
- $0<k<n$:
  - $k$ 奇: $d_k=0$, $d_{k+1}=2$ $\Rightarrow \ker d_k = \mathbb Z$, $\operatorname{im} d_{k+1} = 2\mathbb Z$ $\Rightarrow H_k \cong \mathbb Z/2$。
  - $k$ 偶: $d_k=2$, $d_{k+1}=0$ $\Rightarrow \ker d_k = 0$, $\operatorname{im} d_{k+1}=0$ $\Rightarrow H_k = 0$。
- $k=n$: $\operatorname{im} d_{n+1}=0$。
  - $n$ 奇: $d_n=0$ $\Rightarrow \ker d_n = \mathbb Z$ $\Rightarrow H_n = \mathbb Z$。
  - $n$ 偶: $d_n=2$ $\Rightarrow \ker d_n = 0$ $\Rightarrow H_n = 0$。

然后总结为表格或列表，给出 $H_k(\mathbb{R}P^n)$ 的结果。使用 $\mathbb Z$ 等。

由于是笔记，我会使用无序列表和公式。注意不要大标题，所以直接用粗体“胞腔同调的计算”开头。然后展示。

确保公式正确，$d_{k+1}$等。注意不要用\sum等，没问题。

最后输出。</think>**胞腔同调的计算**  
已有链复形  
$$
0 \to \mathbb Z \xrightarrow{d_n} \mathbb Z \xrightarrow{d_{n-1}} \cdots
\xrightarrow{2} \mathbb Z \xrightarrow{0} \mathbb Z \xrightarrow{2} \mathbb Z \xrightarrow{0} \mathbb Z \to 0,
$$
其中  
$$
d_k = 
\begin{cases}
0, & k\text{ 为奇数},\\
2\ (\text{即乘 }2), & k\text{ 为偶数}.
\end{cases}
$$
同调 $H_k = \ker d_k / \operatorname{im} d_{k+1}$，按 $k$ 的位置分别处理：

- $k = 0$  
  $d_0: C_0 \to 0$，故 $\ker d_0 = \mathbb Z$；$d_1 = 0$（$1$ 为奇数），故 $\operatorname{im} d_1 = 0$。  
  $\Rightarrow H_0 \cong \mathbb Z$。

- $0 < k < n$  
  - **$k$ 为奇数**：$d_k = 0 \Rightarrow \ker d_k = \mathbb Z$；  
    $k+1$ 为偶数，$d_{k+1} = 2 \Rightarrow \operatorname{im} d_{k+1} = 2\mathbb Z$。  
    $\Rightarrow H_k \cong \mathbb Z / 2\mathbb Z \cong \mathbb Z/2$。
  - **$k$ 为偶数**：$d_k = 2 \Rightarrow \ker d_k = 0$；  
    $k+1$ 为奇数，$d_{k+1} = 0 \Rightarrow \operatorname{im} d_{k+1} = 0$。  
    $\Rightarrow H_k = 0$。

- $k = n$（顶维）  
  $\operatorname{im} d_{n+1} = 0$。  
  - **$n$ 为奇数**：$d_n = 0 \Rightarrow \ker d_n = \mathbb Z$。 $\Rightarrow H_n \cong \mathbb Z$。  
  - **$n$ 为偶数**：$d_n = 2 \Rightarrow \ker d_n = 0$。 $\Rightarrow H_n = 0$。

**结果总结**  
| 维数 $k$ | $H_k(\mathbb{R}P^n)$ |
|:------:|:--------------------|
| $0$ | $\mathbb Z$ |
| $0<k<n$，$k$ 奇 | $\mathbb Z/2$ |
| $0<k<n$，$k$ 偶 | $0$ |
| $n$ 奇 | $\mathbb Z$ |
| $n$ 偶 | $0$ |

简言之：  
- 连通性给出 $H_0 = \mathbb Z$；  
- 中间奇数维为 $\mathbb Z/2$，中间偶数维为零；  
- 顶维：当 $n$ 为奇数时 $H_n = \mathbb Z$，当 $n$ 为偶数时 $H_n = 0$（与可定向性一致）。
[Timestamp: 2026/06/15 21:20:17]

**user**: 你考试时写 (\mathbb{C}P^n) 的胞腔同调，可以按下面这个模板来。重点是：**说明 CW 分解、列链群、说明边界映射全为零、得出同调群。**

---

## 考试参考写法

考虑复射影空间 (\mathbb{C}P^n)。它有自然的滤过

[
\mathbb{C}P^0\subset \mathbb{C}P^1\subset\cdots\subset \mathbb{C}P^n.
]

其中 (\mathbb{C}P^k) 是 (\mathbb{C}^{k+1}) 中复直线组成的空间。把 (\mathbb{C}P^{k-1}) 看成 (\mathbb{C}P^k) 中满足最后一个坐标为 (0) 的部分：

[
\mathbb{C}P^{k-1}={[z_0:\cdots:z_k]\in \mathbb{C}P^k\mid z_k=0}.
]

于是其补集为

[
\mathbb{C}P^k-\mathbb{C}P^{k-1}
===============================

{[z_0:\cdots:z_k]\mid z_k\neq 0}.
]

因为 (z_k\neq 0)，可以把齐次坐标归一化为 (z_k=1)，于是

[
[z_0:\cdots:z_{k-1}:z_k]
========================

\left[\frac{z_0}{z_k}:\cdots:\frac{z_{k-1}}{z_k}:1\right].
]

所以有同胚

[
\mathbb{C}P^k-\mathbb{C}P^{k-1}\cong \mathbb{C}^k.
]

而

[
\mathbb{C}^k\cong \mathbb{R}^{2k}.
]

因此 (\mathbb{C}P^n) 有一个 CW 分解：

[
\mathbb{C}P^n=e^0\cup e^2\cup e^4\cup\cdots\cup e^{2n}.
]

也就是说，(\mathbb{C}P^n) 在每个偶数维 (0,2,4,\dots,2n) 各有一个胞腔，在奇数维没有胞腔。

因此胞腔链群为

[
C_q(\mathbb{C}P^n)=
\begin{cases}
\mathbb{Z},& q=0,2,4,\dots,2n,\
0,& q\text{ 为奇数}.
\end{cases}
]

现在考虑胞腔边界映射

[
d_q:C_q(\mathbb{C}P^n)\to C_{q-1}(\mathbb{C}P^n).
]

若 (q) 为偶数，则 (C_q\cong \mathbb{Z})，但是 (C_{q-1}=0)，所以

[
d_q=0.
]

若 (q) 为奇数，则 (C_q=0)，所以

[
d_q=0.
]

因此所有胞腔边界映射都是零映射。胞腔链复形为

[
0\to \mathbb{Z}\to 0\to \mathbb{Z}\to 0\to\cdots\to 0\to \mathbb{Z}\to 0.
]

于是

[
H_q(\mathbb{C}P^n)
==================

\ker d_q/\operatorname{Im}d_{q+1}
\cong C_q.
]

所以

[
H_q(\mathbb{C}P^n)\cong
\begin{cases}
\mathbb{Z},& q=0,2,4,\dots,2n,\
0,& \text{其他维度}.
\end{cases}
]

---

## 最短考试版

如果题目不要求解释 CW 分解来源，你可以直接写：

(\mathbb{C}P^n) 有标准 CW 分解

[
\mathbb{C}P^n=e^0\cup e^2\cup e^4\cup\cdots\cup e^{2n}.
]

因此

[
C_q(\mathbb{C}P^n)=
\begin{cases}
\mathbb{Z},& q=0,2,\dots,2n,\
0,& q\text{ 为奇数}.
\end{cases}
]

由于没有奇数维胞腔，所有边界映射

[
d_q:C_q\to C_{q-1}
]

都为零。故

[
H_q(\mathbb{C}P^n)=\ker d_q/\operatorname{Im}d_{q+1}\cong C_q.
]

所以

[
H_q(\mathbb{C}P^n)\cong
\begin{cases}
\mathbb{Z},& q=0,2,4,\dots,2n,\
0,& \text{其他维度}.
\end{cases}
]

考试时写到这里基本就够了。关键句是：**(\mathbb{C}P^k-\mathbb{C}P^{k-1}\cong \mathbb{C}^k\cong \mathbb{R}^{2k})，所以每一步添一个 (2k)-cell。**
[Context: Notes: 拓扑/RP^n与CP^n的胞腔分解.md]
[Timestamp: 2026/06/15 21:23:49]

**ai**: 
<think>我们被要求将关于CP^n胞腔同调的考试参考写法转化为精炼的笔记式文字，不要有大标题。前文已经对RP^n做了精炼笔记。现在用户提供了CP^n的写法。我们应当输出精炼笔记，用于Obsidian笔记“RP^n与CP^n的胞腔分解”中。之前的笔记已经包含了RP^n部分。现在要添加CP^n部分。但是用户没有说把CP^n单独放一个笔记，而是让我们把这段CP^n的考试写法转化为精炼笔记。可能作为同一笔记的第二部分。我们可以在之前输出的RP^n部分之后加上“**$\mathbb{C}P^n$ 的胞腔分解与同调**”作为小节。要求不要大标题，所以用粗体。内容需要精炼，保留关键：CW分解、链群、边界全零、同调。要符合Obsidian格式，用LaTeX $...$和$$...$$。注意用户说“考试时写到这里基本就够了。关键句是...”，所以精炼笔记也要包含那个关键句。我们要把原内容浓缩成简洁的笔记式文字。注意原内容有使用\[...\]，需转换成$$...$$。另外，原内容有`\mathbb{C}P^k-\mathbb{C}P^{k-1}`等等。我会整理成：

**$\mathbb{C}P^n$ 的胞腔分解**

自然滤过 $\mathbb{C}P^0 \subset \mathbb{C}P^1 \subset \cdots \subset \mathbb{C}P^n$，其中 $\mathbb{C}P^{k-1} = \{ [z_0:\cdots:z_k] \in \mathbb{C}P^k \mid z_k=0 \}$，补集 $\mathbb{C}P^k \setminus \mathbb{C}P^{k-1} = \{ [z_0:\cdots:z_k] \mid z_k \neq 0 \}$。利用 $z_k \neq 0$ 归一化，得同胚
$$
\mathbb{C}P^k \setminus \mathbb{C}P^{k-1} \cong \mathbb{C}^k \cong \mathbb{R}^{2k}.
$$
因此 $\mathbb{C}P^n$ 有一个 CW 分解：
$$
\mathbb{C}P^n = e^0 \cup e^2 \cup e^4 \cup \cdots \cup e^{2n}.
$$
只有在偶数维有胞腔。

胞腔链群：
$$
C_q(\mathbb{C}P^n) =
\begin{cases}
\mathbb{Z}, & q = 0,2,4,\dots,2n,\\
0, & q \text{ 为奇数}.
\end{cases}
$$

**边界映射**  
因为奇数维链群为零，偶数维链群的目标 $C_{q-1}$ 为零（$q-1$ 为奇数），所有边界映射 $d_q$ 都是零映射。链复形为
$$
0 \to \mathbb{Z} \to 0 \to \mathbb{Z} \to 0 \to \cdots \to 0 \to \mathbb{Z} \to 0.
$$

**同调**  
由于 $d_q \equiv 0$，
$$
H_q(\mathbb{C}P^n) = \ker d_q / \operatorname{Im} d_{q+1} \cong C_q.
$$
故
$$
H_q(\mathbb{C}P^n) \cong
\begin{cases}
\mathbb{Z}, & q = 0,2,4,\dots,2n,\\
0, & \text{其他维度}.
\end{cases}
$$

**关键点**：$\mathbb{C}P^k \setminus \mathbb{C}P^{k-1} \cong \mathbb{C}^k \cong \mathbb{R}^{2k}$，每一步添加一个 $2k$-cell，导致只在偶数维有胞腔，边界全零，因此同调就是链群。

这就是精炼笔记。没有大标题，用粗体区分。还应提到这是考试最短版。但笔记不需要说“考试”，只要内容。所以可以。我们需输出这个文本。</think>**$\mathbb{C}P^n$ 的胞腔分解**  
自然滤过 $\mathbb{C}P^0 \subset \mathbb{C}P^1 \subset \cdots \subset \mathbb{C}P^n$，其中  
$\mathbb{C}P^{k-1} = \{[z_0:\cdots:z_k]\in\mathbb{C}P^k \mid z_k=0\}$，补集  
$\mathbb{C}P^k \setminus \mathbb{C}P^{k-1} = \{[z_0:\cdots:z_k]\mid z_k\neq 0\}$。  
令 $z_k=1$ 归一化，得同胚  
$$
\mathbb{C}P^k \setminus \mathbb{C}P^{k-1} \cong \mathbb{C}^k \cong \mathbb{R}^{2k}.
$$  
因此 $\mathbb{C}P^n$ 具有 CW 分解  
$$
\mathbb{C}P^n = e^0 \cup e^2 \cup e^4 \cup \cdots \cup e^{2n},
$$  
只在偶数维有胞腔。

胞腔链群  
$$
C_q(\mathbb{C}P^n) =
\begin{cases}
\mathbb{Z}, & q = 0,2,4,\dots,2n,\\
0, & q \text{ 为奇数}.
\end{cases}
$$

**边界映射**  
奇数维链群为零；偶数维时 $C_{q-1}$ 为奇数维，故 $d_q=0$。所有边界映射均为零映射，链复形为  
$$
0 \to \mathbb{Z} \to 0 \to \mathbb{Z} \to 0 \to \cdots \to 0 \to \mathbb{Z} \to 0.
$$

**胞腔同调**  
因 $d_q\equiv 0$，  
$$
H_q(\mathbb{C}P^n) = \ker d_q / \operatorname{Im} d_{q+1} \cong C_q.
$$  
故  
$$
H_q(\mathbb{C}P^n) \cong
\begin{cases}
\mathbb{Z}, & q = 0,2,4,\dots,2n,\\
0, & \text{其他维度}.
\end{cases}
$$

**要点**：$\mathbb{C}P^k \setminus \mathbb{C}P^{k-1} \cong \mathbb{R}^{2k}$，每一步添一个 $2k$-cell，胞腔只在偶数维，边界全零，同调即链群。
[Timestamp: 2026/06/15 21:24:11]

**user**: ### 题目 14-5：计算 (H_*(T^2)), (H_*(\mathrm{Klein\ Bottle}))

我们使用胞腔同调计算。对于由多边形边识别得到的闭曲面，通常有一个标准 CW 分解：一个 (0)-胞腔，若干个 (1)-胞腔，一个 (2)-胞腔。因此胞腔链复形形如

[
0\to C_2\xrightarrow{d_2}C_1\xrightarrow{d_1}C_0\to 0.
]

因为只有一个 (0)-胞腔，每个 (1)-胞腔的两个端点都贴到同一个顶点上，所以

[
d_1=0.
]

于是关键只剩下计算 (d_2)。若 (2)-胞腔的贴附词为 (w)，则 (d_2) 由 (w) 的交换化给出：每个字母正向出现一次贡献 (+1)，反向出现一次贡献 (-1)。

---

### 一、计算 (H_*(T^2))

环面 (T^2) 可由一个正方形按如下边识别得到：

[
aba^{-1}b^{-1}.
]

因此它有 CW 分解

[
T^2=e^0\cup e_a^1\cup e_b^1\cup e^2.
]

所以胞腔链群为

[
C_2\cong \mathbb Z,\qquad C_1\cong \mathbb Z\langle a,b\rangle,\qquad C_0\cong \mathbb Z.
]

由于只有一个 (0)-胞腔，

[
d_1=0.
]

下面计算 (d_2)。贴附词为

[
aba^{-1}b^{-1}.
]

在 (H_1) 中只看每个字母的指数和，因此

[
d_2(e^2)=a+b-a-b=0.
]

所以胞腔链复形为

[
0\to \mathbb Z\xrightarrow{0}\mathbb Z^2\xrightarrow{0}\mathbb Z\to 0.
]

于是

[
H_2(T^2)=\ker d_2\cong \mathbb Z,
]

[
H_1(T^2)=\ker d_1/\operatorname{Im}d_2\cong \mathbb Z^2/0\cong \mathbb Z^2,
]

[
H_0(T^2)=C_0/\operatorname{Im}d_1\cong \mathbb Z.
]

因此

[
H_k(T^2)\cong
\begin{cases}
\mathbb Z,& k=0,\
\mathbb Z^2,& k=1,\
\mathbb Z,& k=2,\
0,& k\ge 3.
\end{cases}
]

---

### 二、计算 (H_*(\mathrm{Klein\ Bottle}))

Klein bottle 可由一个正方形按如下边识别得到：

[
aba^{-1}b.
]

因此它有 CW 分解

[
K=e^0\cup e_a^1\cup e_b^1\cup e^2.
]

所以胞腔链群为

[
C_2\cong \mathbb Z,\qquad C_1\cong \mathbb Z\langle a,b\rangle,\qquad C_0\cong \mathbb Z.
]

同样地，因为只有一个 (0)-胞腔，

[
d_1=0.
]

现在计算 (d_2)。贴附词为

[
aba^{-1}b.
]

交换化后得到

[
d_2(e^2)=a+b-a+b=2b.
]

也就是说，在基 ({a,b}) 下，

[
d_2:\mathbb Z\to \mathbb Z^2,\qquad 1\mapsto (0,2).
]

所以胞腔链复形为

[
0\to \mathbb Z\xrightarrow{d_2}\mathbb Z^2\xrightarrow{0}\mathbb Z\to 0,
]

其中

[
d_2(1)=(0,2).
]

于是

[
H_2(K)=\ker d_2.
]

因为 (d_2(1)=(0,2)\neq 0)，所以 (d_2) 是单射，因此

[
H_2(K)=0.
]

再算一维同调：

[
H_1(K)=\ker d_1/\operatorname{Im}d_2.
]

由于 (d_1=0)，所以

[
\ker d_1=C_1\cong \mathbb Z^2.
]

而

[
\operatorname{Im}d_2=\langle 2b\rangle.
]

因此

[
H_1(K)\cong \mathbb Z\langle a,b\rangle/\langle 2b\rangle.
]

也就是

[
H_1(K)\cong \mathbb Z\oplus \mathbb Z/2.
]

最后

[
H_0(K)=C_0/\operatorname{Im}d_1\cong \mathbb Z.
]

因此

[
H_k(K)\cong
\begin{cases}
\mathbb Z,& k=0,\
\mathbb Z\oplus \mathbb Z/2,& k=1,\
0,& k=2,\
0,& k\ge 3.
\end{cases}
]

---

### 三、普遍情形：闭曲面的胞腔同调计算方法

对于标准闭曲面，通常可以用一个 (0)-胞腔、若干个 (1)-胞腔、一个 (2)-胞腔来表示。设

[
C_2\cong \mathbb Z,\qquad C_1\cong \mathbb Z^r,\qquad C_0\cong \mathbb Z.
]

因为只有一个 (0)-胞腔，所以

[
d_1=0.
]

关键是计算

[
d_2:C_2\to C_1.
]

若 (2)-胞腔的贴附词是 (w)，则 (d_2(1)) 等于 (w) 中各个字母的指数和组成的向量。

换句话说：

[
d_2(1)=\sum_i \epsilon_i a_i,
]

其中 (\epsilon_i) 是字母 (a_i) 在贴附词中正向出现次数减去反向出现次数。

因此：

[
H_2=\ker d_2,
]

[
H_1=\mathbb Z^r/\langle d_2(1)\rangle,
]

[
H_0\cong \mathbb Z.
]

对于可定向闭曲面 (\Sigma_g)，贴附词为

[
a_1b_1a_1^{-1}b_1^{-1}\cdots a_gb_ga_g^{-1}b_g^{-1}.
]

每个字母都正反各出现一次，所以指数和全部为 (0)。因此

[
d_2=0.
]

于是

[
H_2(\Sigma_g)\cong \mathbb Z,
]

[
H_1(\Sigma_g)\cong \mathbb Z^{2g},
]

[
H_0(\Sigma_g)\cong \mathbb Z.
]

所以

[
H_k(\Sigma_g)\cong
\begin{cases}
\mathbb Z,& k=0,\
\mathbb Z^{2g},& k=1,\
\mathbb Z,& k=2,\
0,& k\ge 3.
\end{cases}
]

对于不可定向闭曲面 (N_m=#^m\mathbb{R}P^2)，标准贴附词为

[
a_1^2a_2^2\cdots a_m^2.
]

因此

[
d_2(1)=2a_1+2a_2+\cdots+2a_m.
]

也就是说

[
d_2:\mathbb Z\to \mathbb Z^m,\qquad 1\mapsto (2,2,\dots,2).
]

因为 (d_2\neq 0)，所以

[
H_2(N_m)=0.
]

又因为

[
H_1(N_m)\cong \mathbb Z^m/\langle (2,2,\dots,2)\rangle,
]

由 Smith 标准型可得

[
\mathbb Z^m/\langle (2,2,\dots,2)\rangle\cong \mathbb Z^{m-1}\oplus \mathbb Z/2.
]

所以

[
H_k(N_m)\cong
\begin{cases}
\mathbb Z,& k=0,\
\mathbb Z^{m-1}\oplus \mathbb Z/2,& k=1,\
0,& k=2,\
0,& k\ge 3.
\end{cases}
]

特别地，Klein bottle 是 (N_2)，因此

[
H_1(K)\cong \mathbb Z\oplus \mathbb Z/2,\qquad H_2(K)=0.
]

---

### 四、总结

环面 (T^2) 的贴附词是

[
aba^{-1}b^{-1}.
]

交换化为

[
a+b-a-b=0.
]

所以

[
H_0(T^2)\cong \mathbb Z,\qquad H_1(T^2)\cong \mathbb Z^2,\qquad H_2(T^2)\cong \mathbb Z.
]

Klein bottle 的贴附词是

[
aba^{-1}b.
]

交换化为

[
a+b-a+b=2b.
]

所以

[
H_0(K)\cong \mathbb Z,\qquad H_1(K)\cong \mathbb Z\oplus \mathbb Z/2,\qquad H_2(K)=0.
]

帮我把它精简, 按照之前的要求. 同时改变latex的包裹格式
[Context: Notes: 拓扑/14. 正合三元组, 同调与映射度.md]
[Timestamp: 2026/06/15 23:32:07]

**ai**: 
<think>我们需要把用户提供的关于$T^2$和Klein bottle同调计算的详细解答，精简成符合之前要求的笔记形式。之前的要求是：转化为精炼的笔记式文字，不要有大标题（即不要#），但可以用粗体区分小节。另外注意LaTeX格式，不用\[...\]而用$$...$$，行内用$...$。这次用户还特别提到“同时改变latex的包裹格式”，就是要把原文中的\[...\]都改成$$...$$，以及\(...\)改成$...$。原文中有很多\[...\]和\(没用\)，可能用了\(...\)？用户原文中有`aba^{-1}b^{-1}`等用了\(...\)？其实原文用了`\(aba^{-1}b^{-1}\)`这样的行内公式？看用户消息中：`aba^{-1}b^{-1}` 没有用`\(`，而是直接文本？不，用户给出的原文是markdown，里面用了`\(...\)`？我检查一下：用户说“帮我把它精简, 按照之前的要求. 同时改变latex的包裹格式”。前面用户给出的原文中，我看到的片段是：`H_*(T^2)`, `H_*(\mathrm{Klein Bottle})`，然后正文用了`\(T^2\)`? 实际上，用户消息中有的地方是`\(T^2\)`，有的地方是`$$`？看原文：开头“我们使用胞腔同调计算。...一个标准 CW 分解：一个 0-胞腔，若干个 1-胞腔，一个 2-胞腔。因此胞腔链复形形如 \[ 0\to C_2\xrightarrow{d_2}C_1\xrightarrow{d_1}C_0\to 0. \]” 有\[...\]。所以需要改成$$...$$。另外行内公式如`\(d_1=0\)`等，需要改成`$d_1=0$`。我会在精简时统一改。此外，内容要精简：去掉“我们使用...”这类叙述，直接给出计算过程和结果，保留关键贴附词、链复形、d_2、同调。还要包含普遍情形：可定向曲面与不可定向曲面的同调，但可能只需要简要总结，因为题目要求计算$T^2$和Klein bottle，可能普遍情形作为补充。用户原文最后有“普遍情形”部分，可用于笔记。我们最终输出精炼笔记，加入到“14. 正合三元组, 同调与映射度”笔记中，作为第4节“曲面的同调群计算”下的内容。但用户现在要求的是精简这段解答，作为该题目的答案。活动笔记是“14. 正合三元组, 同调与映射度”，题目14-5就是计算曲面的同调。所以我们给出的精简笔记可以对应这个题目。需要包含$T^2$和$K$的计算，以及普遍方法。但注意不要大标题（可能不要#或##），可以使用**粗体**作为标题。

策略：输出如下内容：

**$T^2$ 的同调**  
- 贴附词：$aba^{-1}b^{-1}$，CW分解：$e^0\cup e_a^1\cup e_b^1\cup e^2$  
- 链群：$C_2\cong\mathbb Z$，$C_1\cong\mathbb Z\langle a,b\rangle$，$C_0\cong\mathbb Z$  
- $d_1=0$，$d_2$由交换化给出：$d_2(e^2)=a+b-a-b=0$，故$d_2=0$  
- 链复形：$0\to\mathbb Z\xrightarrow{0}\mathbb Z^2\xrightarrow{0}\mathbb Z\to0$  
- 同调：$H_2\cong\mathbb Z$，$H_1\cong\mathbb Z^2$，$H_0\cong\mathbb Z$，其余为0  

**Klein bottle 的同调**  
- 贴附词：$aba^{-1}b$，CW分解：$e^0\cup e_a^1\cup e_b^1\cup e^2$  
- $d_1=0$，$d_2(e^2)=a+b-a+b=2b$，即$d_2(1)=(0,2)$  
- $d_2$单射，故$H_2=0$；$\ker d_1=\mathbb Z^2$，$\operatorname{Im}d_2=\langle 2b\rangle$，所以$H_1\cong \mathbb Z\oplus \mathbb Z/2$  
- $H_0\cong\mathbb Z$，其余为0  

**普遍闭曲面**（可略，但可作为方法）  
- 一个0-cell，$r$个1-cell（与贴附词字母对应），一个2-cell；$d_1=0$  
- $d_2(1) = \sum \epsilon_i a_i$，其中$\epsilon_i$为字母的正向出现次数减反向出现次数  
- 可定向$\Sigma_g$：贴附词$\prod_{i=1}^g a_i b_i a_i^{-1} b_i^{-1}$，$d_2=0$，故$H_2=\mathbb Z$，$H_1=\mathbb Z^{2g}$，$H_0=\mathbb Z$  
- 不可定向$N_m$：贴附词$a_1^2\cdots a_m^2$，$d_2(1)=(2,\dots,2)$，故$H_2=0$，$H_1\cong\mathbb Z^{m-1}\oplus\mathbb Z/2$，$H_0=\mathbb Z$  
特别地，Klein bottle是$N_2$。

用简洁的列表式，避免长句。改公式包裹。不要用`\[`而是`$$`。不要用`\(`而是`$`。例如`d_1=0`写成`$d_1=0$`，数组用`$\mathbb Z^2$`等。

另外，原内容中有“因此胞腔链复形形如 \[ 0\to... \]”，我们改成`$$ 0\to ... \to 0. $$`。还要保证所有公式都是正确的。对于$d_2$映射，可以用`$d_2:\mathbb Z\to \mathbb Z^2$`。

还有，原文中`\operatorname{Im}`，保留。

最终输出精炼版。我将输出完整的精简笔记，可直接放入笔记中。注意不要大标题，所以我用粗体“$\mathbf{T^2}$ 的同调”等，不用`#`。

我们将在回答中提供这个精简内容。</think>**$T^2$ 的同调**  
- 贴附词：$aba^{-1}b^{-1}$。CW 分解：$e^0 \cup e_a^1 \cup e_b^1 \cup e^2$。  
- 链群：$C_2 \cong \mathbb Z$，$C_1 \cong \mathbb Z\langle a,b\rangle$，$C_0 \cong \mathbb Z$。  
- $d_1 = 0$（单一 0-cell）。交换化给出 $d_2(e^2) = a+b-a-b = 0$，所以 $d_2 = 0$。  
- 链复形：$$ 0 \to \mathbb Z \xrightarrow{0} \mathbb Z^2 \xrightarrow{0} \mathbb Z \to 0. $$  
- 同调：  
  $H_2(T^2) \cong \mathbb Z$，  
  $H_1(T^2) \cong \mathbb Z^2$，  
  $H_0(T^2) \cong \mathbb Z$，  
  其余 $0$。

**Klein bottle 的同调**  
- 贴附词：$aba^{-1}b$。CW 分解：$e^0 \cup e_a^1 \cup e_b^1 \cup e^2$。  
- 链群同 $T^2$，$d_1 = 0$。  
- 交换化得 $d_2(e^2) = a+b-a+b = 2b$，即 $d_2(1) = (0,2)$。  
- $d_2$ 是单射，故 $H_2(K) = 0$。  
- $\ker d_1 = \mathbb Z^2$，$\operatorname{Im} d_2 = \langle 2b \rangle$，于是  
  $H_1(K) \cong \mathbb Z\langle a,b\rangle / \langle 2b \rangle \cong \mathbb Z \oplus \mathbb Z/2$。  
- $H_0(K) \cong \mathbb Z$，其余 $0$。

**一般闭曲面的胞腔同调方法**  
设 $C_2 \cong \mathbb Z$，$C_1 \cong \mathbb Z^r$（$r$ 为 1-cell 个数），$C_0 \cong \mathbb Z$，$d_1=0$。  
$d_2(1) = \sum_i \epsilon_i a_i$，其中 $\epsilon_i$ 是贴附词中字母 $a_i$ 的正向次数减反向次数。  
- 可定向曲面 $\Sigma_g$：贴附词 $\prod_{i=1}^g a_i b_i a_i^{-1} b_i^{-1}$，所有 $\epsilon_i = 0$，故 $d_2 = 0$。  
  同调：$H_2 \cong \mathbb Z$，$H_1 \cong \mathbb Z^{2g}$，$H_0 \cong \mathbb Z$。  
- 不可定向曲面 $N_m = \#^m \mathbb{R}P^2$：贴附词 $a_1^2 a_2^2 \cdots a_m^2$，$d_2(1) = (2,2,\dots,2)$。  
  $d_2 \neq 0$ 单射 $\Rightarrow H_2 = 0$；  
  $H_1 \cong \mathbb Z^m / \langle (2,\dots,2) \rangle \cong \mathbb Z^{m-1} \oplus \mathbb Z/2$；  
  $H_0 \cong \mathbb Z$。  

特别地，$T^2 = \Sigma_1$，Klein bottle $= N_2$，与前述一致。
[Timestamp: 2026/06/15 23:32:40]

**user**: 不要项目符号
[Context: Notes: 拓扑/14. 正合三元组, 同调与映射度.md]
[Timestamp: 2026/06/15 23:32:47]

**ai**: 
<think>我们需要根据用户的最新要求调整之前生成的精简笔记。用户说“不要项目符号”，意思是不用无序列表 `-` 开头。之前的笔记中用了 `- ` 列表。所以我们需要改写成不使用项目符号的段落形式，但仍然保持精炼和笔记式。同时，仍要遵守之前的要求：不要大标题（即没有 `#`），但可以使用粗体作为小节标题；LaTeX 公式使用 `$...$` 和 `$$...$$`，不要 `\[ \]`。还要把内容整合到同一笔记中，可能是活动笔记“14. 正合三元组, 同调与映射度”下的第 4 节。我们已经提供了精简版但用了列表。现在要移除列表，改用连续的句子，可能用分段和粗体区分。

需要输出的内容包含 T^2 和 Klein bottle 的同调计算，以及一般闭曲面的方法。需要将它们串联起来，去掉项目符号。可以用类似这样的结构：粗体标题“T^2 的同调”，然后是一段文字叙述贴附词、CW 分解、链群、d_1、d_2 计算、链复形、同调结果。再类似地“Klein bottle 的同调”，以及“一般闭曲面”的段落。不要列表项。但可以使用分号或逗号分隔。确保数学公式在行内或行间。因为要求“笔记式文字”，可以保留简短的句子，但不要项目符号。例如：“它的 CW 分解为 ...，链群为 ...。由于只有一个 0-胞腔，d_1=0。交换化给出 d_2(e^2)=0，故 d_2=0。同调群为 H_2 ≅ Z, H_1 ≅ Z^2, H_0 ≅ Z。” 这样就行。

同时，注意之前我们生成了“一般闭曲面的胞腔同调方法”，也要改成无列表的段落。可以使用粗体“可定向曲面 Σ_g”和“不可定向曲面 N_m”分开叙述。

还要注意“改变latex的包裹格式”：原来回答中已经用了 $$ 和 $，没问题。这次只需要调整去掉项目符号。

最终回复应该只是精炼后的笔记内容，没有大标题，没有项目符号，公式正确。</think>**$T^2$ 的同调**  
$T^2$ 的贴附词为 $aba^{-1}b^{-1}$，CW 分解为 $e^0 \cup e_a^1 \cup e_b^1 \cup e^2$。胞腔链群 $C_2 \cong \mathbb Z$，$C_1 \cong \mathbb Z\langle a,b\rangle$，$C_0 \cong \mathbb Z$。因为只有一个 $0$-胞腔，$d_1 = 0$。交换化给出 $d_2(e^2) = a+b-a-b = 0$，即 $d_2 = 0$。链复形为 
$$ 0 \to \mathbb Z \xrightarrow{0} \mathbb Z^2 \xrightarrow{0} \mathbb Z \to 0. $$
于是 $H_2(T^2) \cong \mathbb Z$，$H_1(T^2) \cong \mathbb Z^2$，$H_0(T^2) \cong \mathbb Z$，其余维数为 $0$。

**Klein bottle 的同调**  
Klein bottle 的贴附词为 $aba^{-1}b$，CW 分解与 $T^2$ 相同：$e^0 \cup e_a^1 \cup e_b^1 \cup e^2$，故链群同样。仍由单一 $0$-胞腔得 $d_1 = 0$。交换化给出 $d_2(e^2) = a+b-a+b = 2b$，即 $d_2(1) = (0,2)$。$d_2$ 是单射，因此 $H_2(K) = 0$。$\ker d_1 = \mathbb Z^2$，$\operatorname{Im} d_2 = \langle 2b \rangle$，所以 $H_1(K) \cong \mathbb Z\langle a,b\rangle / \langle 2b \rangle \cong \mathbb Z \oplus \mathbb Z/2$。$H_0(K) \cong \mathbb Z$，其余为 $0$。

**一般闭曲面的胞腔同调方法**  
对由多边形边识别给出的闭曲面，常取一个 $0$-胞腔、$r$ 个 $1$-胞腔（与贴附词字母对应）和一个 $2$-胞腔。于是 $C_2 \cong \mathbb Z$，$C_1 \cong \mathbb Z^r$，$C_0 \cong \mathbb Z$ 且 $d_1=0$。$d_2$ 由贴附词决定：若贴附词为 $w$，则 $d_2(1) = \sum_i \epsilon_i a_i$，其中 $\epsilon_i$ 是字母 $a_i$ 的正向出现次数减去反向出现次数。  

**可定向曲面 $\Sigma_g$** 的贴附词 $\prod_{i=1}^g a_i b_i a_i^{-1} b_i^{-1}$ 使所有 $\epsilon_i = 0$，故 $d_2 = 0$。因此同调为 $H_2(\Sigma_g) \cong \mathbb Z$，$H_1(\Sigma_g) \cong \mathbb Z^{2g}$，$H_0(\Sigma_g) \cong \mathbb Z$。  

**不可定向曲面 $N_m = \#^m \mathbb{R}P^2$** 的贴附词 $a_1^2 a_2^2 \cdots a_m^2$ 给出 $d_2(1) = (2,2,\dots,2)$。此时 $d_2$ 是单射，故 $H_2(N_m) = 0$。$H_1(N_m) \cong \mathbb Z^m / \langle (2,\dots,2) \rangle \cong \mathbb Z^{m-1} \oplus \mathbb Z/2$，$H_0(N_m) \cong \mathbb Z$。  

特例：$T^2 = \Sigma_1$，Klein bottle $= N_2$，与前述计算一致。
[Timestamp: 2026/06/15 23:33:10]