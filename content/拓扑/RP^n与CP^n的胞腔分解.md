## $\mathbb{R}P^{n}$的胞腔分解

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

**胞腔同调的计算**  
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

## **$\mathbb{C}P^n$ 的胞腔分解**  
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