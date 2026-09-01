---
epoch: 1788245641494
modelKey: "deepseek-v4-flash|deepseek"
topic: "Rotation and Bernoulli factors"



tags:
  - copilot-conversation
---

**user**: 圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。
[Context: Notes: 分析/遍历论/习题2.1 保测系统与同构.md]
[Timestamp: 2026/09/01 14:54:01]

**ai**: 
<think>我们 need answer user's query in Chinese. Need parse context. User asks: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" They reference note exercises. Need explain: circle rotation's factors, and if Bernoulli shift on {0,1}^Z is invertible, what are factors. Need answer based on context, maybe from note: Exercise 2.1.5 asks find nontrivial factor maps. Need discuss.

Let's parse user query carefully. The active note contains notes about exercises. User asks: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。"

Translation: "What are the factors with circle rotation? Also Bernoulli shift is invertible (if consider {0,1}^Z), what is the factor?" They may want examples of nontrivial factor maps for circle rotation and invertible Bernoulli shift. Need answer.

Need define factor map: measurable map φ: X→Y? But exercise says φ: X→X (factor map into itself? Actually factor map φ: X→Y where Y is a factor system, but they ask find φ: X→X maybe factor map from system to itself? Hmm note says "Find a measure-preserving system (X,B,μ,T) with a non-trivial factor map φ:X→X." That is unusual: a factor map usually φ: X→Y. But if Y=X? Non-trivial factor map to itself? Maybe they mean "nontrivial factor" of itself? Need interpret. In exercise 2.1.5-a and b, they ask "Find a measure-preserving system (X,B,μ,T) with a non-trivial factor map φ: X → X." Wait maybe typo: φ: X → X? Could be they want a factor map φ: X→X not isomorphism? A factor map from a system to itself is an endomorphism. Nontrivial factor map to itself could mean invariant sub-sigma-algebra? Let's examine note: It lists:
> (a) Find a measure-preserving system (X,mathscr B, μ, T) with a non-trivial factor map φ:X→X.
Then note: "常见的保测度系统: ... 保测度系统非平凡因子： (T,m,T2) ≅ ({0,1}^N, μ, σ) ... φ:(T,m)→(X,μ), sum a_k/2^k → (a1,a2,...) satisfies φ(T(x)) = σ(φ(x))"

So they gave example for (a): φ: T → {0,1}^N, not X→X? Actually X became {0,1}^N, but original system T, factor is one-sided Bernoulli. Is that "non-trivial factor map φ: X→X"? No, map from T to {0,1}^N. Maybe they mean find system with nontrivial factor map φ from the system to another system, but wrote X→X in note? Wait exercise text in note says φ: X → X. But their example φ: (T,m) -> (X,μ) with X={0,1}^N. Hmm.

Let's understand concept. A factor of a measure-preserving system (X,B,μ,T) is another system (Y,C,ν,S) together with a factor map π: X→Y satisfying π∘T=S∘π, π_*μ=ν. Nontrivial means not isomorphism and not trivial one-point system. In part (a) maybe "non-trivial factor map φ: X → X" could mean φ is a factor map from (X,B,μ,T) to itself? That's an endomorphism. Nontrivial endomorphism? For circle doubling T2, the map φ(x)=2x mod1? Wait φ: T→T, φ(x)=2x mod1. Check φ∘T2? T2(x)=2x; φ(T2(x))=4x; T2(φ(x))=2*(2x)=4x. So φ is an endomorphism of (T,B,m,T2). Is it nontrivial? It is not invertible, so nontrivial factor map to itself. Could be that. But in note, example given for (a) is coding T to {0,1}^N, not φ:X→X. Maybe they misunderstood? Need be careful.

User asks: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" They likely refer to exercises 2.1.5: find nontrivial factor map for circle rotation and invertible Bernoulli shift. They want examples.

So answer should explain:
- For circle rotation R_α on T (example 2.2) is minimal, ergodic? Factors of irrational rotation? Let's think. Circle rotation R_α(x)=x+α mod1. What are its factors? Factors of an irrational rotation are again irrational rotations (or trivial). Specifically, if α irrational, any nontrivial factor is isomorphic to a rotation on a finite quotient? Wait, the factors of irrational rotations are exactly rotations by β on a torus? Let's recall.

Given system (T, R_α), α irrational. An eigenfunction is e^{2π i n x} with eigenvalue e^{2π i n α}. Factors correspond to closed invariant subspaces maybe. Since rotation is ergodic, factor map π: T→Y with S. The induced map on L^2(Y) is an isometry. The factor is determined by eigenfunctions of S. Since all eigenvalues of R_α are {e^{2π i n α}: n∈Z}. A factor corresponds to a subgroup of eigenvalues? Need identify.

Maybe simpler: For any integer q≥1, define π_q: T→T by π_q(x)=q x mod1. Then π_q(R_α x)=q(x+α)=π_q(x)+qα, so it factors onto rotation R_{qα} (mod1). This is a nontrivial factor if qα not same? But if q=1 identity trivial. For q>1, not invertible (unless? q>1 not one-to-one), nontrivial factor. However is R_{qα} on T a factor with invariant measure Lebesgue. So circle rotation has factors given by multiplication by q, giving rotations by qα.

But wait, for irrational rotation, factor map x→ q x mod1 is measurable and onto, and indeed (T, R_α) → (T, R_{qα}) factor. Is S=R_{qα}; yes. For rational rotations? If α rational, factors more complex? But example 2.2 likely circle rotation R_α maybe any α? Need discuss.

Also factors of irrational rotation are exactly rotations on quotient groups T/K? Let's derive: Any factor of an irrational rotation is measurably isomorphic to a rotation on a compact monothetic group? Actually for irrational rotation, it is strictly ergodic, has discrete spectrum; any factor corresponds to a closed subgroup of the dual group? For rotation on compact abelian group G with dual Γ and translation by a, eigenfunctions are characters. Factor corresponds to quotient Γ/Λ where Λ is invariant under multiplication by a? Hmm.

Simpler answer: For circle rotation R_α, for each positive integer q, define φ_q(x)=q x mod1. Then φ_q∘R_α = R_{qα}∘φ_q. These are nontrivial factor maps if q>1. E.g., R_α's factor is rotation by 2α.

But need check if q>1, R_{qα} might be isomorphic to R_α? For α irrational, R_α and R_{qα} are measurably isomorphic? Are they? Isomorphism between rotations requires eigenvalue sets equal. Eigenvalues of R_α: {e^{2π i n α}: n∈Z}; of R_{qα}: {e^{2π i n qα}: n∈Z} = {e^{2π i (qn) α}: n∈Z} subset of eigenvalues of R_α. Since α irrational, the sets are not equal unless q=±1? Actually {qn} are multiples of q, so subset not all integers. Thus not isomorphic. So φ_q is a nontrivial factor, not isomorphism.

Question phrase "圆的旋转与什么是因子" maybe "圆的旋转与...?" Maybe "圆的旋转与什么是因子" means "What is a factor with circle rotation?" We'll interpret.

Then "此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" They note in their notes: "伯努利平移 X={0,1}^Z" as invertible. They ask "factor is what?" Need give examples of nontrivial factor maps for Bernoulli shift on {0,1}^Z.

A Bernoulli shift (two-sided) is (X={0,1}^Z, B, μ=(1/2,1/2)^Z, shift σ). It is invertible. Need find nontrivial factor map. Nontrivial factors are many. Examples:

1. One-sided Bernoulli shift: define projection π: {0,1}^Z → {0,1}^N or {0,1}^{Z_{\ge0}} by forgetting negative coordinates: π(x)_n = x_n for n≥0. Then π∘σ = σ_+∘π, where σ_+ is one-sided shift on {0,1}^N. This is a factor map onto the one-sided Bernoulli shift, non-invertible, so nontrivial. This matches note's example for T2. Since two-sided shift invertible, one-sided shift is a non-invertible factor.

2. Even/odd coordinate maps? More generally, for any k? Define φ: {0,1}^Z → {0,1}^Z by φ(x)_n = x_{2n} (subsequence even coordinates). Does it factor? Check φ(σ x)_n = (σ x)_{2n}=x_{2n+1}; σ^? Need S such that S(φ(x))? Want φ(σ x) = ? If S is shift, S(φ(x))_n = φ(x)_{n+1}=x_{2n+2}; not equal. Need define S as shift by 2? But factor map should go to same system? Actually if S = shift, φ(σ x)_n = x_{2n+1}; cannot be written as shift of sequence of even coordinates. Unless use two-sided Bernoulli and define block factor.

Better: Many factors of Bernoulli shifts are Bernoulli shifts (Ornstein). For example, any continuous factor of a Bernoulli shift is Bernoulli? There are many.

Simplest nontrivial factor for two-sided Bernoulli shift: quotient by a coordinate? For instance, map to {0,1}^Z itself? Need an endomorphism? Let's construct.

We want measure-preserving system (X,B,μ,σ) and a factor map φ: X→Y (or X→X?). The note's part (b) asks find invertible system with nontrivial factor map φ: X→X. For Bernoulli shift on {0,1}^Z, one can define φ: X→X by φ(x)_n = x_n + x_{n+1} mod 2? Let's check factor relation with shift σ.

Define φ: {0,1}^Z → {0,1}^Z by (φ(x))_n = x_n ⊕ x_{n+1}? Then φ(σ x)_n = (σ x)_n ⊕ (σ x)_{n+1} = x_{n+1} ⊕ x_{n+2}. σ(φ(x))_n = (φ(x))_{n+1} = x_{n+1} ⊕ x_{n+2}. So φ∘σ = σ∘φ. Nice! It is an endomorphism of the Bernoulli shift. Is it measure-preserving? The distribution of (x_n⊕x_{n+1}) is Bernoulli(1/2)? For iid fair bits, sum mod2 is fair; but not independent across n? Actually if define y_n = x_n ⊕ x_{n+1}, are y_n iid Bernoulli(1/2)? They are not independent? Let's check correlation: y_0 and y_1: (x0⊕x1, x1⊕x2). They are independent? Cov? For independent uniform bits, y0 and y1 independent because mapping (x0,x1,x2) -> (x0⊕x1, x1⊕x2) is bijective on {0,1}^3? Is it bijective? Matrix [[1,1,0],[0,1,1]] rank 2, not bijective, but with three bits, two outputs. Are outputs independent uniform? Distribution: y0,y1 are uniform each; P(0,0) = P(x0=x1, x1=x2) = 2/8=1/4, yes. For longer, Markov? Actually y_n = x_n ⊕ x_{n+1}. The sequence y is a Markov chain? It has memory one? It is a factor but not iid. Is it isomorphic to Bernoulli? Maybe the endomorphism is not invertible (since not one-to-one); measure-preserving? Need check φ_* μ is shift-invariant and is it the same probability measure? For iid fair, the process y_n has uniform one-dimensional but not independent? Let's test y_n and y_{n+2}: y0=x0⊕x1, y2=x2⊕x3 independent because disjoint, so 2-dependence. Thus not iid. But is φ_* μ equal to μ (iid Bernoulli)? No, because y has dependence. However factor map to itself in measure-preserving sense: φ_* μ is a shift-invariant measure on {0,1}^Z, not necessarily μ. Wait if factor map is to (X, μ) same measure, need φ_* μ = μ. Does y distribution equal iid? No. So φ is not measure-preserving as map (X,μ)→(X,μ). It is measure-preserving onto (Y,ν) with ν = φ_*μ. If we require φ: X→X and the system on X is same measure, then no.

Maybe use measure-preserving endomorphism of Bernoulli shift? Are there any nontrivial measure-preserving endomorphisms of a Bernoulli shift? I think Bernoulli shifts are "finitely determined" maybe any factor of a Bernoulli shift is Bernoulli, but an endomorphism of Bernoulli shift that is measure-preserving onto itself must be an isomorphism? Wait Ornstein's theorem: any factor of a Bernoulli shift is a Bernoulli shift. But a measure-preserving factor map from (X,μ,σ) to itself where target measure is μ is a measure-preserving endomorphism. Does there exist non-invertible measure-preserving endomorphisms of Bernoulli shift? If a factor map to the same shift, it would imply the factor is isomorphic to the full shift (Bernoulli). Since factor map to Bernoulli shift with same entropy? The entropy of the image under φ_*? If φ_* μ = μ, entropy same h=log2. A factor of a Bernoulli shift with same entropy is isomorphic to the original? I recall if a factor has same entropy as Bernoulli, then the factor is isomorphic to the Bernoulli shift, implying factor map is an isomorphism (maybe with a.e. invertibility). Thus nontrivial endomorphism may not exist. But problem asks "invertible measure-preserving system with a nontrivial factor map φ: X → X" maybe indeed impossible? Wait they ask find one, so maybe possible? Let's think.

Actually for an invertible measure-preserving system, a factor map φ: X→X? If φ is measure-preserving and equivariant, does φ need to be invertible? Not necessarily. Example: identity? Need nontrivial. Consider product of Bernoulli shift with itself, T=S×id? Invertible? If T=S×id on X×Y, map projection π:X×Y→X is factor to S, but not to same space. But to same X? If factor map from (X,μ,T) to itself, that's an endomorphism. Could be non-invertible for some systems? Let's search memory: A measure-preserving transformation T on a non-atomic probability space can have non-invertible measure-preserving endomorphisms commuting with T. For Bernoulli shift, any endomorphism is invertible? I think Bernoulli shifts are "or-finitary"? Let's recall: A measure-preserving transformation T is "Bernoulli" if it is a Bernoulli shift. Is every endomorphism of a Bernoulli shift an isomorphism? Since Bernoulli shifts have "very weak Bernoulli" maybe factors are Bernoulli; if entropy same then isomorphic. If endomorphism onto itself means entropy equal, so factor is isomorphic to original. The factor map π:X→Y where Y is isomorphic to X, but the factor map itself might not be invertible? If π_* μ = μ (same measure), and (Y,C,ν,S)=(X,B,μ,T). A factor map π with same entropy to Bernoulli is an isomorphism by Ornstein (any factor of Bernoulli with same entropy is isomorphic). But isomorphism could be via another map ψ:Y→X, not necessarily π invertible? However if π_* μ=μ and entropy equal, I think π is a.e. invertible? Need not? Let's test: Consider probability space [0,1] with identity T=id. Define φ(x)=2x mod1. φ_* Leb? It is not Lebesgue (Leb after doubling? Actually φ_* Leb = Leb, yes? For A, Leb(φ^{-1}A)=? φ not one-to-one; preimage length is Leb(A) because two halves each half length, yes Leb(φ^{-1}A)=Leb(A). So φ is measure-preserving endomorphism of ([0,1], Leb, id). It is non-invertible. But system is not invertible? T=id is invertible, and φ is nontrivial factor map to itself! Wait T=id is invertible, identity is measure-preserving and invertible. φ∘id=id∘φ. φ_*Leb=Leb. Indeed φ non-invertible. So there is an invertible system with nontrivial factor map to itself. But is that considered "invertible measure-preserving system"? Yes (X, B, μ, id) is invertible. But perhaps they want a nontrivial factor map φ: X→X, not necessarily surjective? For (T,m,T2?) Hmm.

Another example: (T, m, R_α) with factor map φ_q(x)=q x mod1. φ_q∘R_α=R_{qα}∘φ_q. But if target system is same? For factor map to itself (same T and same rotation), we need R_{qα}=R_α? That requires (q-1)α ∈ Z. For irrational α, impossible for q≠1. So no nontrivial φ to same rotation. But for identity map T=id, any measure-preserving φ gives factor to itself. Could be too trivial but valid.

But the problem in note: "Find an invertible measure-preserving system (X,B,μ,T) with a nontrivial factor map φ:X→X." Maybe they mean "with a nontrivial factor map φ: X→X" as an endomorphism, likely they want an invertible system where there is a factor (not necessarily to itself) but φ from X to X? Wait notation "φ:X→X" explicit. Could solve by taking T=id and φ(x)=2x mod1. But perhaps they intended "factor map" in the sense of "factor map φ: X → X" where the factor is a subsystem? Let's not overcomplicate. For user's question specifically: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" They want factors of circle rotation and Bernoulli shift. We can mention both in the sense of factor maps to other systems.

Let's think about circle rotation factors more.

Example 2.2 likely: Circle rotation R_α: T→T, x↦x+α mod1. It is measure-preserving for Lebesgue. It is invertible. What are its nontrivial factors? If α is irrational, the system is ergodic and has discrete spectrum. Any factor is again an irrational rotation (or trivial). More concretely:
- For every integer q>0, define φ_q: T→T, φ_q(x)=q x mod1. Then φ_q∘R_α = R_{qα}∘φ_q. This gives a factor map onto (T,B,m,R_{qα}). If q>1 and α irrational, φ_q is not one-to-one, so nontrivial. (If α rational with denominator n, qα may reduce modulo 1; still factor.)
- Also, if α=p/q rational, there are finite factors? Because R_α has finite orbits? It is not ergodic but has factors like permutation on q points? Actually R_{p/q} decomposes into q cycles, and there is a factor map to a finite cyclic permutation by considering residue of n? But maybe not necessary.

But wait: Are all factors of irrational rotation of form R_{qα}? Let's verify: Suppose π: T→Y factor. Since π is measurable, maybe π∘R_α = S∘π. π is not necessarily a group homomorphism. But if Y is a rotation on some compact group? By Halmos-von Neumann, any ergodic system with discrete spectrum is isomorphic to a rotation on a compact abelian group. The factor of (T,R_α) corresponds to quotient of dual group Z by a subgroup Λ stable under multiplication by α. Since dual group of T is Z. A factor's group is dual of a subgroup? Let's derive: Rotation on compact group G by a has eigenfunctions characters of G with eigenvalues χ(a). For G=T, dual Z, eigenvalues e^{2π i n α}. Factor corresponds to a subset of eigenvalues closed under multiplication? The possible factors correspond to subgroups H of the dual group? Actually if factor map π:G→G/K, where K is a closed subgroup? Then for T, closed subgroups are finite or T. Quotient T/K is finite if K finite, or trivial. That would not give R_{qα} for irrational? Wait multiplication q: T→T is a surjective continuous homomorphism with kernel finite cyclic of order q. By first isomorphism theorem, quotient T/\{0,1/q,...\} ≅ T, not a finite quotient. So K closed subgroup? The kernel of q is finite, not a closed subgroup? It is closed finite. Quotient by finite subgroup is T (as topological groups). So factors correspond to kernels of homomorphisms n↦? More generally, any continuous homomorphism T→T is x↦q x mod1. So yes, R_α factors onto R_{qα}.

But are there non-homomorphic factors? For irrational rotations, due to pure point spectrum, the factor map is essentially a group homomorphism? I think yes, because the factor has discrete spectrum, and eigenfunctions of the factor pull back to eigenfunctions of R_α. Eigenfunctions of R_α are characters χ_n(x)=e^{2π i n x}. Thus the factor's eigenfunctions are among these. The factor can be represented by a subfamily; to get a factor system, the set of eigenvalues must be closed under multiplication? Since if χ_n is in factor, its powers χ_{kn} are also? Actually eigenfunctions form a group under multiplication: χ_n · χ_m = χ_{n+m}. If factor map π has eigenfunctions that are functions of π, the set of n such that χ_n is measurable w.r.t. the factor's σ-algebra is a subgroup of Z? Let's check: If χ_n and χ_m are functions of π, then χ_n χ_m = χ_{n+m} is also function of π. So S = {n: χ_n ∈ L^2(π)} is a subgroup of Z. Subgroups of Z are dZ for some d≥0. Thus factor corresponds to dZ. The factor generated by characters χ_{d k} is exactly the σ-algebra generated by q? If d? Wait χ_n for n=0,±d,±2d,...; the factor is the "coarsening" that only sees x mod 1/d? Let's test d=1 gives full system; d=2 gives functions of 2x? Because e^{2π i 2k x} depend on 2x mod1. So factor is multiplication by 2. Thus yes, nontrivial factors correspond to multiplication by d≥2, giving rotation R_{dα}. Also d=0? subgroup {0} yields trivial factor. So indeed.

But if α rational, the eigenvalue group is finite? Actually R_α may not be ergodic if α rational, but still factors may include finite rotations? Let's not go deep unless user asks.

Now Bernoulli shift.

If we consider two-sided Bernoulli shift ({0,1}^Z, μ, σ). It is invertible. Nontrivial factors?

The simplest nontrivial factor map:
- Let π: {0,1}^Z → {0,1}^{\mathbb{N}} (or {0,1}^{Z_{\ge0}}) be the truncation to nonnegative coordinates: π(x)_n = x_n for n≥0. Then π∘σ = σ_+∘π, where σ_+ is the one-sided shift. The image measure is the one-sided Bernoulli(1/2) measure. This is a measure-preserving factor map. It is non-invertible because it forgets negative coordinates. So one-sided Bernoulli shift is a nontrivial factor of two-sided Bernoulli shift.

Also, more generally, the two-sided Bernoulli shift has many factors, including any Bernoulli shift with entropy ≤ log2 (by Ornstein theory), and also non-Bernoulli factors? Wait factors of Bernoulli shifts are Bernoulli shifts (Ornstein). Any Bernoulli shift with entropy h ≤ log2 is a factor. For example, the two-sided k-ary Bernoulli shift with k≤2? Since entropy h=log k ≤ log2, so a k-ary Bernoulli shift is a factor. But need explicit map? Could use blocking: map pairs of bits to a 4-ary symbol? But entropy log4 > log2, not possible. For a factor with lower entropy, e.g., a Bernoulli shift with alphabet size 2 but probabilities not 1/2? It is also Bernoulli with entropy h(p)<log2. By Ornstein, it is a factor of the (1/2) Bernoulli shift. But explicit factor maps are nontrivial (coding) and not easy.

Simpler explicit factor maps:
- Coordinate deletion: one-sided shift.
- Sum modulo 2 with shift? As discussed, y_n = x_n ⊕ x_{n+1}; this is a two-step Markov chain, not Bernoulli? But is it a factor of the Bernoulli shift? Yes, because it is a function of the shift coordinates (a block factor), so it is a factor. The invariant measure ν is not the Bernoulli(1/2) measure, but it's still a factor system. This is a good nontrivial factor in the sense of factor map to another system (not necessarily to same X). But if user asks "因子是什么" maybe want a factor system, not necessarily Bernoulli.

If they specifically say "伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" They might ask: In the note part 2.1.5-b, they need an invertible system with nontrivial factor map. Since Bernoulli shift on {0,1}^Z is invertible, what is a factor? The answer: the one-sided Bernoulli shift is a factor; or maybe the two-sided shift restricted to even coordinates? Let's see if there is a factor map from {0,1}^Z to itself? We want an invertible system with nontrivial factor map φ:X→X. Is there one for Bernoulli? Let's explore more.

Maybe there is a nontrivial factor map from two-sided Bernoulli shift to itself? Is that possible? Let's search memory. A factor map from a Bernoulli shift to itself must be an isomorphism if it is onto the same Bernoulli shift (same entropy). But if the factor map is not required to be surjective? Factor map definition usually requires π(X) has full measure in Y; if Y=X and π_*μ=μ, it is onto a.e. Then as argued, if entropy same, maybe isomorphism. So no non-invertible endomorphism to itself. But maybe there are non-invertible factor maps from X to X if the transformation on target is not the same σ? But "factor map φ:X→X" says same X and same T? It does, because factor map φ: X→X requires φ∘T = T∘φ. So endomorphism. For two-sided Bernoulli, any measure-preserving endomorphism is an automorphism? I recall "A Bernoulli shift has no proper factors of the same entropy", but an endomorphism to itself would have same entropy. I think it implies invertible. There are "endomorphisms of Bernoulli shifts are automorphisms" (a known result? For Markov shifts, non-invertible endomorphisms exist? Let's test with 2-shift, define φ(x)_n = x_n + x_{n+1} mod2; the image measure is not Bernoulli, so endomorphism not to same measure. But if target is same X with different T? You could set T on target as something else. But statement φ:X→X often means to same measure space but could have a different transformation? No, factor map between systems (X,B,μ,T) and (X,B,μ,S)? Hmm, if both systems share same X but transformations differ, φ∘T = S∘φ. Could there be noninvertible S? But (X,μ,S) is another system on same space. But factor map usually to same system? It says "nontrivial factor map φ:X→X" maybe indeed endomorphism of the same system, so T on both sides.

Wait, exercise 2.1.5 in context: "Find a measure-preserving system (X,mathscr B, μ,T) with a non-trivial factor map φ: X → X." If "factor map" is a map between systems, then a map φ:X→X from a system to itself is an endomorphism. Non-trivial endomorphisms may or may not exist. For (T,m,T2) example, φ(x)=2x? Let's test: T2 on T, φ(x)=2x? Then φ∘T2 = 4x mod1, T2∘φ = 2(2x)=4x. Yes! So φ is a nontrivial endomorphism of (T,m,T2). It is measure-preserving? For Lebesgue, φ_*Leb = Leb? For doubling map, yes (preimage of interval length l is two intervals length l/2 total l). So that's a valid example for (a) (non-invertible system with endomorphism). For (b), they need invertible system with nontrivial endomorphism. A simple one: (T,m,id) with φ(x)=2x mod1 as above. Or rotation? Need φ commuting with R_α and measure-preserving endomorphism to same system. For R_α irrational, only φ(x)=x? Let's see measure-preserving maps commute with irrational rotation? Are they necessarily rotations? Not necessarily? There are many measurable maps commuting with irrational rotation? By ergodicity? If φ∘R_α=R_α∘φ, then φ is invariant under? Actually φ(x+α)=φ(x)+α. This implies φ(x)-x is invariant under R_α? φ(x+α)-(x+α)=φ(x)-x. Since R_α ergodic, φ(x)-x = c constant a.e. So φ(x)=x+c=R_c. For φ to be measure-preserving on T, R_c is measure-preserving and invertible, so it is an automorphism. To be nontrivial endomorphism, not isomorphism? But R_c is isomorphism. So no nontrivial endomorphism for irrational rotation. For rational rotation, maybe there are. But identity system is easiest.

Now, user specifically mentions invertible Bernoulli shift {0,1}^Z. They might be considering exercise (b): Find invertible measure-preserving system with nontrivial factor map φ:X→X. They ask "伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" Maybe they want a factor (not endomorphism) of Bernoulli shift? Let's parse exact Chinese: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" It could be read as: "For circle rotations, what is a factor? Moreover, Bernoulli shift is invertible (if considering {0,1}^Z), what is a factor?" They may not ask about endomorphism to itself, but about nontrivial factor maps for these systems. We should answer with both direct examples and clarify definitions.

Let's formulate answer:

- 定义: 一个保测系统的因子是另一个保测系统 $(Y,\mathscr C,\nu,S)$ 与一个满测的、保持测度的、共轭映射 $\pi:X\to Y$，即 $\pi\circ T=S\circ\pi$ 且 $\pi_*\mu=\nu$。通常称 $\pi$ 为因子映射。若 $\pi$ 不是同构且 $Y$ 不是单点系统，则称非平凡因子。

- 圆的旋转 $R_\alpha$:
  - For any positive integer $q$, define $\pi_q:\mathbb T\to\mathbb T$, $\pi_q(x)=q x\bmod1$. Then $\pi_q(R_\alpha x)=R_{q\alpha}(\pi_q(x))$ and $\pi_q$ pushes Lebesgue forward to Lebesgue. Thus $(\mathbb T,\mathscr B,m,R_{q\alpha})$ is a factor of $(\mathbb T,\mathscr B,m,R_\alpha)$. For $q>1$, $\pi_q$ is not one-to-one, so nontrivial. Example: factor $R_{2\alpha}$ via $x\mapsto2x$.
  - (If α irrational, these are essentially all nontrivial factors, up to isomorphism; if α is rational, there are also finite permutation factors, but maybe skip or mention briefly.)

- Bernoulli shift:
  - Two-sided Bernoulli shift $(\{0,1\}^{\mathbb Z},\mathscr B,\mu,\sigma)$ is invertible.
  - A nontrivial factor: one-sided Bernoulli shift $(\{0,1\}^{\mathbb N},\mathscr B',\mu_+,\sigma_+)$ via projection $\pi((x_n)_{n\in\mathbb Z})=(x_n)_{n\ge0}$ (or $n\ge1$). It forgets all negative coordinates. It is measurable, measure-preserving, and satisfies $\pi\circ\sigma=\sigma_+\circ\pi$. Since projection is not injective, factor is nontrivial.
  - Another nontrivial factor: take a block code like $y_n=x_n\oplus x_{n+1}$; it is a factor to a 2-step Markov shift, not the full Bernoulli shift. But if you're looking for an endomorphism of the two-sided Bernoulli shift to itself, note: a measure-preserving endomorphism of a Bernoulli shift that maps onto the same shift must be an isomorphism (because entropy is the same), so there is no non-invertible factor map to itself. However other factors exist. Wait this statement might be too strong? Let's verify with a concrete non-invertible measure-preserving map from {0,1}^Z to itself with σ-equivariance and image measure μ? Could there be due to "almost isomorphism"? Let's search memory: "Endomorphism of a Bernoulli shift is Bernoulli and has same entropy? A measure-preserving transformation on the same probability space commuting with shift" Let's test with a finite-dimensional analogue: The shift σ on {1,...,k}^Z is a factor of itself by a non-invertible map? For finite alphabet, any continuous, shift-commuting, measure-preserving map to itself? There are cellular automata that are surjective and measure-preserving but not invertible? E.g., elementary cellular automaton rule 150 (XOR with neighbors) on the full shift. Is it surjective and measure-preserving? For the uniform Bernoulli measure, the image of rule 150 (x_n -> x_{n-1}⊕x_n⊕x_{n+1}) is uniform? It is a linear CA over F2. Is the linear map L = I + σ + σ^{-1} on {0,1}^Z. Is L surjective? Over F2, polynomial 1+z+z^2 has roots primitive cube roots, but over F2? Does it have a root? In F2, z^2+z+1 is irreducible, so not a divisor of 1? The map L as linear operator on vector space ∏Z F2. Is it surjective? For any y, need solve x_n+x_{n+1}+x_{n+2}=y_n. This linear recurrence has solution if characteristic polynomial has root? Over F2, z^2+z+1 has no roots in F2, so it is invertible as a left shift? Actually recurrence x_{n+2}=x_n+x_{n+1}+y_n; given initial x0,x1, can extend both directions uniquely? For bi-infinite sequences, the operator may be bijective? Since polynomial is invertible in formal power series ring? z^2+z+1 is not a unit in F2[[z]]? It has constant term 1, so yes unit in formal power series, so inverse is infinite one-sided but as map on bi-infinite sequences, can solve using series? Let's check kernel: x_n+x_{n+1}+x_{n+2}=0. Characteristic poly z^2+z+1 has no root in F2, but over extension F4 it has roots. Nonzero periodic kernel solutions exist (period 3: 110110...). So kernel nontrivial, not injective. Surjectivity? For any y, recurrence x_{n+2}=x_n+x_{n+1}+y_n. For bi-infinite sequence, starting at n=0 with x0,x1, can determine to the right; to left, solve x_n = x_{n+1}+x_{n+2}+y_n for n=-1? Actually recurrence for n=-2? Given x_{-1},x_0? Need choose two values; all choices give solutions, so surjective? Let's test y=all zero, kernel nonzero; to solve general y, choose x0,x1 and propagate right; left propagation also works because recurrence can be rearranged x_n = x_{n+1}+x_{n+2}+y_n? For n=-2, x_{-2}=x_{-1}+x_0+y_{-2}; yes. So all solutions. Thus L is surjective, not injective. Is L measure-preserving w.r.t. uniform Bernoulli? For any cylinder, preimage count? Since kernel size? The map is 2-to-1? Let's test preimage of a cylinder maybe measure same? For L = 1+σ+σ^{-1}, the sum of three independent fair bits is biased mod2? Actually x_{n-1}+x_n+x_{n+1} mod2 has distribution? Over F2, sum of three fair bits: P(0)=P(1)=1/2? Let's check parity of 3 fair bits: P(even)=? 000 even, 011 even, 101 even, 110 even => 4/8=1/2. So each bit uniform. But correlations? Need measure of finite cylinder. For a block y_0,...,y_{m-1}, the preimage condition is a set of linear equations; number of solutions in a finite block may vary, but because L is surjective and kernel has full shift? Wait kernel is a closed shift-invariant subspace of dimension? For a finite segment, the map from x block of length m+2 to y block of length m is linear with matrix; preimage count is 2^2 for every y? Because rank m? Let's compute for m=1, y0 = x_{-1}+x_0+x_1; for each x block length3, 4 outputs? Actually each output has 2 preimages (since 8/4=2). For length m, number of variables m+2, output length m, rank m, so preimage size 4. So preimage of any cylinder has measure 4*2^{-(m+2)}=2^{-m}=μ(cylinder). Thus L is measure-preserving! And L is shift-equivariant, non-invertible. So there is a nontrivial endomorphism of the two-sided Bernoulli shift to itself! Wait but earlier entropy argument? The image measure is μ? We just computed preimage of every cylinder has measure equal to cylinder measure, so L_* μ=μ. L is a non-invertible measure-preserving endomorphism. This contradicts "any endomorphism of Bernoulli shift is automorphism"? Let's verify: L(x)_n = x_{n-1}+x_n+x_{n+1}. Is L_*μ=μ? For finite cylinder fixing y_{0..m-1}, preimage is union of cylinders? The linear equations are not necessarily independent? We assumed rank m; need ensure for every output block, number of input blocks length m+2 giving that output is constant 4. The matrix is m x (m+2) with rows representing shifts of (1,1,1). Is the matrix full row rank m? Yes, because first m columns? Let's write for y0..ym-1 and variables x_{m+1}? Use recurrence. The rows are independent because leading terms? Let's test m=2, equations:
y0 = x_{-1}+x_0+x_1
y1 = x0+x1+x2
Variables 4, rank 2 likely; each output has 4 preimages. For m=3, equations y0 uses x-1,x0,x1; y1 uses x0,x1,x2; y2 uses x1,x2,x3. Matrix rows: [1 1 1 0 0], [0 1 1 1 0], [0 0 1 1 1], rank 3? yes. So constant. So L is measure-preserving. Thus Bernoulli shift has nontrivial endomorphisms! My entropy argument was wrong: entropy of factor (X, μ, T) same, but factor map not necessarily isomorphic? However Ornstein says any factor of Bernoulli is Bernoulli; if entropy same, it is isomorphic to the Bernoulli shift, but the factor map itself may not be an isomorphism; the factor system is isomorphic but the map from original to factor could be non-invertible while still image measure same. That is possible: The target measure μ is Bernoulli; the factor map non-invertible but the target system is same Bernoulli. So nontrivial endomorphisms exist. Good.

Wait, is L a factor map to (X, μ, σ)? Yes L∘σ=σ∘L. L_*μ=μ. L is non-invertible. So a much simpler example for (b): two-sided Bernoulli shift with φ(x)_n = x_{n-1}+x_n+x_{n+1} mod2 (or maybe x_n⊕x_{n+1}? Let's check if x_n⊕x_{n+1} is measure-preserving to same μ? Earlier we thought image not iid. Let's check y_n = x_n⊕x_{n+1}. Is y sequence iid? We tested y0,y1 independent? But need all finite blocks. Is the map y = D x where D = 1+σ? Is D surjective? Over F2, polynomial 1+z is not a unit? It has kernel constant sequences (0 or all 1) because (1+σ)x=0 implies x constant; so kernel size 2. Is D surjective? Need solve x_n + x_{n+1}=y_n. This recurrence x_{n+1}=x_n+y_n. For a given y, choose x0; then x_n determined for all n; need consistency around the circle? For bi-infinite, any choice yields a sequence? For n negative, recurrence can be inverted x_n=x_{n+1}+y_n. So yes two solutions. Is D_*μ=μ? Let's compute preimage of a cylinder: variables x_{0..m} for outputs y_0..y_{m-1}; m equations, m+1 variables, rank? Matrix rows:
[1 1 0 0 ...]
[0 1 1 0 ...]
...
rank m? Yes, so preimage size 2 for each output; measure 2 * 2^{-(m+1)} = 2^{-m}=μ. So D is also measure-preserving! But earlier I thought y_n not independent because y0 = x0⊕x1, y1 = x1⊕x2. I computed P(y0=0,y1=0)=1/4? Let's recalc: For fair independent x0,x1,x2, y0=x0⊕x1, y1=x1⊕x2. P(y0=0,y1=0)=P(x0=x1 and x1=x2)=P(x0=x1=x2)=2/8=1/4. If independent Bernoulli(1/2), product=1/4. So they are pairwise independent. Check y0,y1,y2? y2=x2⊕x3. y0,y1,y2: P(y0=0,y1=0,y2=0) = P(x0=x1, x1=x2, x2=x3) = 2/16=1/8, product=1/8. So y sequence seems iid! Wait why did I think dependency? Because y0 and y1 involve x1 but mapping is not two-to-one? It is measure-preserving and maybe D is actually an isomorphism? D = 1+σ on the two-sided shift is surjective non-injective (kernel constants). It should map uniform Bernoulli to uniform Bernoulli because it is a factor of Bernoulli, but the image of a Bernoulli shift under any factor is Bernoulli? Actually factors of Bernoulli are Bernoulli, so yes D_*μ is Bernoulli with entropy ≤ log2; since D_*μ has entropy? Could be log2? Let's compute entropy of y. If y is iid, entropy log2. Since D has kernel size 2, entropy unchanged? The map D is not invertible but factors can have same entropy. So y might be iid! Let's test independence of y0,y1,y2 with overlapping. In general, y block of length m is linear map from x block length m+1 with full row rank m, so each output block has exactly 2 preimages, each of measure 2^{-(m+1)}, so measure 2^{-m}. Thus y is iid fair. Yes! So D is a nontrivial measure-preserving factor map from Bernoulli shift to itself? Wait D(x)_n = x_n ⊕ x_{n+1}; D is shift-equivariant? Check D(σx)_n = (σx)_n ⊕ (σx)_{n+1}=x_{n+1}⊕x_{n+2}. σ(Dx)_n = (Dx)_{n+1}=x_{n+1}⊕x_{n+2}. Yes. D_*μ=μ as shown. D is non-invertible (kernel contains constant sequences 000... and 111...). Thus this is a very simple nontrivial factor map from two-sided Bernoulli shift to itself! Nice.

But wait, if D maps to itself and is measure-preserving, then the two-sided Bernoulli shift is a factor of itself via a non-invertible map. Does that violate any theorem? It's fine. The factor system is the same Bernoulli shift, but factor map not an isomorphism. "Non-trivial factor" usually means the associated sub-sigma-algebra is not the full one; but the target system can be isomorphic to the original. Here D^{-1}(B) is a proper sub-sigma-algebra? Actually D is not invertible, so the factor σ-algebra D^{-1}(B) is a proper sub-σ-algebra, but the factor is isomorphic to original via D? Wait D^{-1}(B) is the σ-algebra of sets invariant under? Let's see: D is shift-equivariant and measure-preserving. The factor is (X, D^{-1}(B), μ, σ) where σ acts. Is it isomorphic to the Bernoulli shift? Since D_*μ=μ, but D itself maps (X,B) to (X,B) not injective. The factor represented by subalgebra D^{-1}B is isomorphic to the quotient (X,B,μ,σ) via the map? The standard factor is Y=X with measure μ; so yes factor is the Bernoulli shift. The nontriviality lies in the factor map not being an isomorphism (the subalgebra is proper). So part (b) can use D.

This is a great example. For user "伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么" We can give D and also one-sided projection. Need decide which to include.

Let's return to user's query. They wrote:
"圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。"

Maybe they are asking about "factor" in the context of exercise 2.1.5. In the note, for exercise 2.1.5-a, they gave example using T2 and one-sided Bernoulli shift. For 2.1.5-b, they need invertible system with nontrivial factor. They mention "伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么" likely asking: if using two-sided Bernoulli shift as invertible system, what is the factor map? Need answer with a concrete φ.

Let's craft a robust answer:

- Start by clarifying "因子映射" definition and "非平凡" means not isomorphism (or not one-point factor).
- For circle rotation:
  - For any $q\ge1$, $\pi_q(x)=qx\pmod 1$ is a factor map from $R_\alpha$ to $R_{q\alpha}$:
    $$\pi_q(R_\alpha x)=q(x+\alpha)=R_{q\alpha}(\pi_q(x))\pmod1.$$
    And $\pi_q$ sends $m_\mathbb T$ to $m_\mathbb T$. If $q>1$, it is not one-to-one, so it is a nontrivial factor (except trivial cases). For example $R_\alpha\to R_{2\alpha}$.
  - Maybe mention if α irrational, nontrivial factors are exactly these $R_{q\alpha}$, $q\ge2$, up to isomorphism.

- For Bernoulli shift:
  - If the base is two-sided $X=\{0,1\}^{\mathbb Z}$, then shift $\sigma$ is invertible.
  - A simple factor map to a *different* (non-invertible) factor is forgetting negative coordinates:
    $$\pi((x_n)_{n\in\mathbb Z})=(x_n)_{n\ge0}\in\{0,1\}^{\mathbb N}.$$
    This factors $\sigma$ onto the one-sided shift $\sigma_+$. It is non-injective, so nontrivial.
  - If you want a nontrivial factor map *to the same two-sided Bernoulli shift itself* (i.e. an endomorphism), define
    $$\phi(x)_n=x_n\oplus x_{n+1}\pmod2,\quad n\in\mathbb Z.$$
    Then $\phi\circ\sigma=\sigma\circ\phi$, and $\phi_*(\text{Bernoulli})=\text{Bernoulli}$ (each finite block of $\phi(x)$ has exactly two preimage blocks of equal measure), but $\phi$ is not invertible (the two constant sequences both map to the zero sequence). So it is a valid nontrivial factor map for part (b).

Need verify "each finite block has exactly two preimage blocks of equal measure" for D. Let's formalize if needed.

Let's test D measure preservation more rigorously:
For any $u=(u_0,\ldots,u_{m-1})\in\{0,1\}^m$, consider $E=\{x: \phi(x)_0=u_0,\dots,\phi(x)_{m-1}=u_{m-1}\}$. This is determined by $x_0,\dots,x_m$ satisfying
$$x_i\oplus x_{i+1}=u_i,\quad i=0,\dots,m-1.$$
Given $x_0$, the rest are uniquely determined; both choices $x_0=0,1$ give exactly one $x_1,\dots,x_m$ satisfying the equations? Actually the equations determine x_{i+1} = x_i ⊕ u_i. For each choice of x0, we get a distinct block of length m+1. Thus exactly two x-blocks of length m+1. Each has measure $2^{-(m+1)}$ under μ (for cylinder fixing m+1 coordinates). So total measure $2^{-m}$. The cylinder $\{y: y_0=u_0,\dots,y_{m-1}=u_{m-1}\}$ also has measure $2^{-m}$. Thus φ_*μ=μ on cylinders; by uniqueness extends. Good.

For circle rotation π_q: measure preservation:
For interval $[a,b)$, $m(\pi_q^{-1}([a,b])) = \sum_{j=0}^{q-1} m(\frac{a+j}{q},\frac{b+j}{q}) = q \cdot \frac{b-a}{q}=b-a$. So yes.

Need also mention "factor map" must satisfy π_*μ=ν. For circle rotation, $\pi_q$ maps Lebesgue to Lebesgue. For R_{qα}, the target is same circle with Lebesgue.

What about "圆的旋转与什么是因子" maybe "圆的旋转与什么是因子" could mean "What is the relationship between circle rotation and factor?" Maybe "圆的旋转与什么是因子" maybe a fragment: "圆的旋转与[...] 什么是因子" Let's parse: "圆的旋转与什么是因子" literally "circle rotation and what is a factor" maybe they ask "what are the factors of circle rotation?" We'll answer.

Need maybe reference note's exercise 2.1.5. The note's part (a) says "Find a measure-preserving system with a non-trivial factor map φ: X → X." They gave example: $(\mathbb{T},m,T_2) \cong (\{0,1\}^{\mathbb{N}},\mu,\sigma)$ then φ: T→X? Actually that φ maps to the one-sided Bernoulli, not X->X. But perhaps in their note they used factor map φ: (\mathbb T,m,T2) -> ({0,1}^N, μ, σ). Hmm.

We can include all relevant examples.

Let's perhaps structure answer:

1. 定义要点.
2. 圆旋转的例子:
   - System: $(\mathbb{T}, \mathscr{B}_\mathbb{T}, m_\mathbb{T}, R_\alpha)$ with $R_\alpha(x)=x+\alpha\mod1$.
   - Factor map: $\pi_q(x)=qx\mod1$ onto $(\mathbb{T},m,R_{q\alpha})$.
   - Nontrivial because $q>1$ not injective; $m$ preserved.

3. 伯努利位移:
   - $X=\{0,1\}^{\mathbb{Z}}$, $\mu=(\frac12\delta_0+\frac12\delta_1)^{\otimes\mathbb{Z}}$, shift $\sigma$ invertible.
   - Factor to one-sided: $\pi((x_n)_{n\in\mathbb Z})=(x_n)_{n\ge0}$ onto $(\{0,1\}^{\mathbb{N}},\mu_+,\sigma_+)$.
   - Also endomorphism to itself: $\phi(x)_n=x_n\oplus x_{n+1}$; verify commutativity and measure preservation; non-invertible.

Need maybe address "非平凡" nuance: A factor is nontrivial if it is not isomorphic to the original and not the one-point system. For the endomorphism φ to same system, is it "nontrivial factor" if target is isomorphic to original? The factor map itself is non-invertible, so as a factor map it is not an isomorphism; the factor (target system) is actually isomorphic to original, but the map is non-injective. Some definitions of "nontrivial factor" might require the factor system not to be isomorphic to the original. If so, $\phi$ to same Bernoulli would be considered trivial factor? Let's examine. In ergodic theory, "factor" is often an invariant sub-σ-algebra modulo null sets; a factor is "nontrivial" if it is neither the full σ-algebra nor the trivial σ-algebra. The factor generated by φ (the σ-algebra φ^{-1}(B) or φ*?) might be proper even if quotient system is isomorphic? For D, φ^{-1}(B) is a proper sub-σ-algebra, so it is nontrivial. But if "nontrivial factor map" means not invertible as a map, then D qualifies. Let's check if D^{-1}(B) is proper: Since D not injective, D^{-1}(B) does not separate the constant sequences? B separates points; preimage under D cannot separate points in same fiber, so proper. Yes.

But if a "factor" is defined as quotient system, the two-sided Bernoulli shift is a factor of itself via D? The target system is the same, but factor map not invertible. Is that allowed? Usually factor map is onto, not necessarily injective; so yes.

Alternatively, a simpler non-trivial factor where target is not isomorphic to original is one-sided Bernoulli shift. Use that if concerned. We can present both.

Maybe also mention for invertible system part, the one-sided shift factor is not invertible (the target system is non-invertible), and factor map non-injective. That's enough for "factor". If they need "factor map φ:X→X" specifically, use φ(x)_n=x_n⊕x_{n+1}. We'll include both to cover.

Need perhaps mention circle rotation $R_\alpha$ is itself invertible, but its factors via multiplication q are also circle rotations, and target is invertible too. Wait if target is $R_{qα}$, the map π_q is q-to-1 not invertible, but target system is invertible. That's fine.

Let's think if there are any pitfalls with $R_{qα}$ factor: $R_{qα}$ on $\mathbb T$ is well-defined: $R_{qα}(y)=y+qα\mod1$. Yes.

Maybe if α rational, qα could be 0 mod1, giving identity rotation on T; that's still a factor? If qα∈Z, target is identity system, but it's not one-point; is it "nontrivial"? If target is identity on T, the factor map is non-injective and target has infinite entropy? Actually identity entropy 0. The factor is not isomorphic to source, so nontrivial. But maybe they only care about irrational rotation. We can add "如果 α 是无理数，这些都是非平凡因子；若 α 为有理数，还会有有限旋转因子，不过上面的例子已经够用."

Let's consider "圆的旋转与什么是因子" maybe "circle rotation and what is factor" perhaps they ask "Why is circle rotation not measurably isomorphic to T2" from exercise 2.1.6? Hmm user query: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" This is in context of the note's exercises. The note has section 4 "非平凡因子映射" with exercises 2.1.5-a and b. They ask about circle rotation and Bernoulli shift. So yes.

Let's prepare final response in Chinese with LaTeX. Need follow instructions: use $ for LaTeX, not \[. Use markdown lists with "- ". Use [[title]]? Not necessary. Avoid wrapping Obsidian internal links. No tags. Use Chinese. Keep moderate detail.

Let's draft final:

"先明确：因子映射 $\pi:(X,\mathscr B,\mu,T)\to(Y,\mathscr C,\nu,S)$ 满足 $\pi\circ T=S\circ\pi$ 且 $\pi_*\mu=\nu$（即 $\mu(\pi^{-1}C)=\nu(C)$）。$\pi$ 可测、满测即可。非平凡通常指 $\pi$ 不是同构（且 $Y$ 不是单点系统）。"

"圆旋转的例子：... For any q≥1, π_q(x)=q x mod1. Check:
π_q(R_α x)=q(x+α)=q x + qα = R_{qα}(π_q x).
Lebesgue 测度被 π_q 推到 Lebesgue 测度。因此 $(T,m,R_{qα})$ 是因子。q>1 时 π_q 不是单射，所以非平凡。例如 q=2, factor R_{2α}."

"伯努利位移：... 双边的 shift σ is invertible. 因子可以取如下:
- 忘掉负坐标：π((x_n)_{\mathbb Z})=(x_n)_{\mathbb N_0}. Then π∘σ=σ_+∘π, image measure is one-sided Bernoulli. Non-injective.
- 如果想找 $\phi:X\to X$（同空间上的因子映射），可令 φ(x)_n=x_n⊕ x_{n+1}. Then φ commutes with σ; it preserves Bernoulli measure (for block, exactly 2 preimage blocks); but not invertible (常数序列 000... 和 111... 都映到 000...). 因此是很好的非平凡因子映射."

Need maybe mention if "因子是什么" they might want "factor" singular; we'll give both.

Let's ensure correctness of "for block, exactly 2 preimage blocks" for φ(x)_n=x_n⊕x_{n+1}. Let's write:
For any block $u=(u_0,\dots,u_{m-1})$, the event $\{\phi(x)_0=u_0,\dots,\phi(x)_{m-1}=u_{m-1}\}$ is determined by $x_0,\dots,x_m$ satisfying $x_i\oplus x_{i+1}=u_i$. Given $x_0$ there is exactly one solution; so $2$ allowed blocks $(x_0,\dots,x_m)$, each of measure $2^{-(m+1)}$. Total $2^{-m}$, equal to measure of cylinder $u$. Thus φ_*μ=μ. This is a neat proof.

Need also show φ not injective: φ(000...)=000..., φ(111...) =? For 111... each x_n⊕x_{n+1}=0, so also 000...; yes.

Need maybe mention "one-sided Bernoulli shift is not invertible; two-sided shift is invertible" and "one-sided shift is a factor of two-sided shift by projection." That covers.

Let's also maybe include "for irrational rotation, factors are essentially R_{qα}"? Should I state? It might be useful but not necessary. Let's include as a note: "事实上对无理旋转，非平凡因子（在同构意义下）正是这些 R_{qα}；对有理旋转还可能出现有限因子." But if not asked, maybe too much. It's okay.

Let's think about "圆的旋转与什么是因子" maybe they ask "What is a factor of circle rotation?" Could mention "circle rotation has no nontrivial factors if α is irrational?" Wait is that possible? Let's re-evaluate: If R_α is irrational rotation, factors include R_{2α}. Is R_{2α} a factor? I verified $\pi_2(x)=2x \mod1$. Let's check measure-preserving: preimage of interval length l is union of two intervals length l/2, total l. Good. Non-injective. So yes nontrivial factors exist. But maybe "circle rotation" Example 2.2 is $R_\alpha$ with α irrational? It is measurably isomorphic to any $R_{qα}$? No, but factor.

Let's test with eigenfunctions: For R_α, eigenvalue e^{2π i α} corresponds to χ_1. For factor R_{2α}, eigenfunction χ_1(y)=e^{2π i y} pulls back to χ_1(2x)=e^{4π i x}=χ_2(x), which is indeed an eigenfunction with eigenvalue e^{4π i α}=e^{2π i 2α}. So factor.

Now, perhaps "圆的旋转与什么是因子" maybe they mean "circle rotation and $T_2$: what is a factor" For example, $T_2$ has factor one-sided Bernoulli, and circle rotation's factor? Hmm.

Let's also consider exercise 2.1.5-a in note: They sought "non-trivial factor map φ:X→X" but gave φ from T to {0,1}^N. Maybe their answer for (a) was actually "T2 is a factor of T4"? Let's examine note: It says "保测度系统非平凡因子：`(\mathbb{T},m,T_{2})\cong(\{0,1\}^{\mathbb{N}},\mu,\sigma)` ... φ:(\mathbb{T},m)->(X,\mu), sum a_k/2^k -> (a1,a2,...) satisfies φ(T(x))=σ(φ(x))". That's a factor map from circle doubling to one-sided Bernoulli shift. But exercise 2.1.5-a asks "Find a measure-preserving system (X,B,μ,T) with a non-trivial factor map φ:X→X." Maybe they are trying to find a system with nontrivial factor map; φ from T to one-sided Bernoulli is not X→X, but note says "from (T,m,T2) to (X,μ,σ)" where X={0,1}^N. Wait if the original system is T, the factor is X. But the statement says φ:X→X? Maybe there is a typo in the exercise, maybe it should be "φ: X→Y" with "Y" not "X"? Let's check common exercise maybe from "Ergodic Theory with a view towards Number Theory" by Einsiedler/Ward? Exercise 2.1.5? I recall exercises in that book.

Let's search memory: In "Ergodic Theory with a view towards Number Theory" by Einsiedler and Ward, Chapter 2? Exercises:
2.1.1? 2.1.2? Maybe
- Exercise 2.1.2: Show T_4 isomorphic to T_2×T_2.
- Exercise 2.1.3: For a map T and sets...
- Exercise 2.1.4: What happens to Example 2.5 if T only continuous homomorphism?
- Exercise 2.1.5: Find a measure-preserving system (X,ℬ,μ,T) with a non-trivial factor map φ:X→X? Perhaps "non-trivial factor map" means "an endomorphism which is not an isomorphism" indeed. Let's recall: In their book, Section 2.1 "Measure-preserving systems" includes "Factor maps" maybe. Exercise 2.1.5 might be "Give an example of a measure-preserving system with a non-trivial factor map" where factor map defined between systems (X,ℬ,μ,T) and (Y,𝒞,ν,S), so φ:X→Y. But the note says φ:X→X maybe because user typed? Let's check active note section title: "非平凡因子映射" with "(a) Find a measure-preserving system (X, \mathscr{B}, \mu, T) with a non-trivial factor \operatorname{map} \phi: X \rightarrow X." Then part (b): "Find an invertible measure-preserving system ( $X, \mathscr{B}, \mu, T$ ) with a nontrivial factor map $\phi: X \rightarrow X$." It explicitly says X→X both. So yes endomorphism.

Could there be a known exercise: "Find a measure-preserving system with a non-trivial factor map" not necessarily onto itself. Maybe book has "nontrivial factor map" as endomorphism? Let's not worry; we can mention both interpretations.

Let's maybe in final answer say "如果你指的是从系统到自身的因子映射（即与 T 可交换的非平凡保测变换），可用..." This addresses both.

Let's think about another example for invertible system with nontrivial factor map to itself from the note's perspective. They may want "invertible measure-preserving system" not necessarily Bernoulli. The two-sided Bernoulli shift with φ(x)_n=x_n⊕x_{n+1} is excellent and directly answers "伯努利位移是可逆的...因子是什么". We'll lead with that for Bernoulli.

Let's verify measure-preserving of φ(x)_n=x_n⊕x_{n+1} under two-sided Bernoulli. We proved for block from x0..xm. But note φ depends on x_n and x_{n+1}, so the condition for y_0..y_{m-1} involves x_0..x_m (if indexing starts at n=0). Good.

Let's perhaps use "$\oplus$" but ensure readers know mod 2 addition. Define.

Let's consider if $\phi(x)_n=x_n\oplus x_{n+1}$ maps to same measure μ? We proved. But is φ measurable? Yes, continuous (Cantor product) and cylinder preimages cylinders. Good.

Let's maybe include "这是一个因子的例子，但不是同构：常数序列 0^Z 和 1^Z 都对应 0^Z." Actually $\phi(1^\mathbb{Z})_n = 1⊕1=0$ for all n; yes.

Now, what about circle rotation with φ_q to itself? For R_α, could define φ(x)=2x? But commutation fails unless R_{2α}=R_α. So no. For rational rotation, maybe φ(x)=2x gives factor to R_{2α}, but if target system same transformation? Only if 2α=α mod1. So generally no. For identity case, φ(x)=2x works. But user asks "圆的旋转与什么是因子" not "endomorphism". We can mention as factor to another rotation.

Let's maybe also include a note "因子映射和目标系统可以不同；若是找 $X\to X$ 的因子映射，则要求目标变换是同一个 T." Good.

Let's decide final formatting:

````markdown
先澄清定义：...

**圆旋转的例子。** 令 ... For every q...
- ...
- ...

**伯努利位移的例子。** ...
- 若允许因子系统不同：...
- 若想要 $X\to X$ 的因子映射：...
````

Need follow instruction: use bullet "- " with no leading spaces. Good.

Let's produce final answer in Chinese.

Before final, let's think if "圆的旋转与什么是因子" could be asking "圆的旋转与什么是因子" maybe "circle rotation and what is factor" maybe they want "circle rotation's factors are circle rotations with alpha scaled by d" exactly.

Let's include "如果 $R_\alpha$ 中 $\alpha$ 是无理数，那么所有这些 $q$ 给出互不同构的非平凡因子；事实上，无理旋转的非平凡因子（在同构意义下）都是这种形式." Is "互不同构" true? $R_{qα}$ vs $R_{pα}$ isomorphic iff q=±p? Since eigenvalue groups {n q α mod1} vs {n p α}; for α irrational, groups dZ? Actually if p and q differ by sign, same group; otherwise not. So yes.

For Bernoulli shift, one-sided projection is a factor but not an endomorphism. Let's detail:
Let $X^+=\{0,1\}^{\mathbb{N}_0}$ with product measure $\mu^+$ and left shift $\sigma^+(x)_n=x_{n+1}$ (n≥0). Define $\pi((x_n)_{n\in\mathbb Z})=(x_n)_{n\ge0}$. Then $\pi(\sigma x)=(\sigma x)_n? Wait for n≥0, $\pi(\sigma x)_n=(\sigma x)_n=x_{n+1}$. And $\sigma_+(\pi(x))_n=\pi(x)_{n+1}=x_{n+1}$. So yes. It is measure-preserving because projection onto coordinates ≥0 of iid sequence is iid. It is onto a.e. (all sequences). Not injective.

If using $\mathbb{N}$ vs $\mathbb{N}_0$, fine.

Let's also perhaps mention "one-sided Bernoulli shift is not invertible, so this shows an invertible system can have a non-invertible factor." Good.

Let's think about "factor map φ:X→X" in note part (b). They might prefer φ on two-sided Bernoulli to itself. The projection to one-sided is a map from X to X^+, not X→X. So include both to be safe.

Let's maybe mention "If the problem literally asks for $\phi:X\to X$, take $\phi(x)_n=x_n\oplus x_{n+1}$." That is directly helpful.

Let's ensure no conflict with "non-trivial factor" definition: If φ is an endomorphism to itself and non-invertible, some might call it a "non-invertible factor map" but not a "nontrivial factor" if the factor system is same? It is still non-invertible, so it is a nontrivial factor map. Good.

Let's consider if $\phi(x)_n=x_n\oplus x_{n+1}$ is surjective? It is surjective (for any y, choose x0=0 and recursively define x). So factor map onto the whole space. Good.

Maybe for one-sided projection, the factor is one-sided Bernoulli, not "invertible" but factor map from invertible system to non-invertible factor. That's allowed; factors of invertible systems can be non-invertible.

Let's maybe use "严格地说" to avoid definition ambiguity.

Let's produce final.

Wait, user's query "圆的旋转与什么是因子" maybe "圆的旋转与[什么]是因子" They might be asking "圆的旋转与[那个什么是因子]" Not sure. We'll answer with examples.

Let's also perhaps mention "the factor map must preserve measure, so not every surjective map is factor." Good.

Let's final now.</think>先明确一点：**因子映射** 是指  
\[
\pi:(X,\mathscr B,\mu,T)\to (Y,\mathscr C,\nu,S)
\]
满足
\[
\pi\circ T=S\circ \pi,\qquad \pi_*\mu=\nu.
\]
后者就是
\[
\mu(\pi^{-1}(C))=\nu(C),\quad \forall C\in\mathscr C.
\]
如果 $\pi$ 不是同构，就称这个因子是非平凡的。

---

## 1. 圆旋转的因子

设圆旋转系统为
\[
(\mathbb T,\mathscr B_{\mathbb T},m_{\mathbb T},R_\alpha),
\qquad R_\alpha(x)=x+\alpha\pmod 1.
\]

对任意正整数 $q$，定义
\[
\pi_q:\mathbb T\to\mathbb T,\qquad \pi_q(x)=qx\pmod 1.
\]
则
\[
\pi_q(R_\alpha x)=q(x+\alpha)=qx+q\alpha
= R_{q\alpha}(\pi_q(x))\pmod 1.
\]
并且 $\pi_q$ 把勒贝格测度推到勒贝格测度。因此
\[
(\mathbb T,\mathscr B_{\mathbb T},m_{\mathbb T},R_{q\alpha})
\]
是 $(\mathbb T,\mathscr B_{\mathbb T},m_{\mathbb T},R_\alpha)$ 的一个因子。

当 $q>1$ 时，$\pi_q$ 不是单射，所以这是**非平凡因子**。  
例如 $q=2$ 时，$R_\alpha$ 以
\[
\pi_2(x)=2x\pmod 1
\]
为因子映射，其因子是 $R_{2\alpha}$。

---

## 2. 伯努利位移的因子

双边伯努利位移
\[
(X,\mathscr B,\mu,\sigma),\qquad X=\{0,1\}^{\mathbb Z},
\]
其中 $\mu$ 是每个坐标独立取 $0,1$ 且概率各为 $1/2$ 的乘积测度，$\sigma$ 是左平移。这个系统是**可逆**的。

### 因子 1：投影到单边伯努利位移

定义
\[
\pi:X\to \{0,1\}^{\mathbb N_0},\qquad
\pi((x_n)_{n\in\mathbb Z})=(x_n)_{n\ge 0}.
\]
也就是忘掉所有负数坐标。则
\[
\pi\circ\sigma=\sigma_+\circ\pi,
\]
其中 $\sigma_+$ 是单边伯努利位移。$\pi$ 保测，但不是单射，因此是**非平凡因子映射**。

### 因子 2：若要求 $\phi:X\to X$ 到自身

如果题目要求的是从系统到自身的非平凡因子映射，即
\[
\phi\circ\sigma=\sigma\circ\phi,
\]
可以取
\[
\phi(x)_n=x_n\oplus x_{n+1}\pmod 2.
\]
它和 $\sigma$ 交换：
\[
\phi(\sigma x)_n=x_{n+1}\oplus x_{n+2}
=(\sigma\phi(x))_n.
\]
它也保持伯努利测度：对任意有限块 $u_0,\dots,u_{m-1}$，
\[
\phi(x)_0=u_0,\dots,\phi(x)_{m-1}=u_{m-1}
\]
等价于
\[
x_i\oplus x_{i+1}=u_i,\quad i=0,\dots,m-1.
\]
给定 $x_0$ 后这些方程唯一确定 $x_1,\dots,x_m$，所以正好有 $2$ 个长度为 $m+1$ 的原像块，总测度为
\[
2\cdot 2^{-(m+1)}=2^{-m},
\]
和对应柱集的测度相同。因此 $\phi_*\mu=\mu$。

但 $\phi$ 不是单射：常数序列 $0^{\mathbb Z}$ 和 $1^{\mathbb Z}$ 都映到 $0^{\mathbb Z}$。所以它是非平凡的因子映射。
[Timestamp: 2026/09/01 14:57:26]

**user**: 圆旋转你是不是做错了，把它的因子展示给我看
[Context: Notes: 分析/遍历论/习题2.1 保测系统与同构.md]
[Timestamp: 2026/09/01 15:12:13]

**ai**: 
<think>The user is questioning: "圆旋转你是不是做错了，把它的因子展示给我看" = "Did you make a mistake with circle rotation? Show me its factors."

They doubt my previous answer about circle rotation factors. Need re-examine.

I claimed: circle rotation R_α has factor R_{qα} via π_q(x)=q x mod1. Need verify if this is indeed a factor map. Let's check: π_q: T → T, π_q(x)=q x mod1. Then π_q(R_α x)=π_q(x+α)=q(x+α)=q x + q α = R_{qα}(π_q x). Yes. Measure preservation: π_q_* m = m? Let's check carefully: For q>1, Lebesgue on T, π_q map: preimage of interval (a,b) is union of q intervals each length (b-a)/q, total b-a. So yes.

But perhaps the user thinks I made an error because for irrational rotation, factors are not just this? Or maybe because π_q is not a factor map to R_{qα} with Lebesgue? It is. But maybe "factor" requires the factor map to be *onto* and the pushforward measure exactly the target. Yes.

However, there is subtlety: R_{qα} on T may be measurably isomorphic to R_α? No, not isomorphic for irrational α? Let's check: For α irrational, R_α and R_{qα} might actually be isomorphic if qα is in the same circle of eigenvalue group? Wait, eigenvalues of R_α are {e^{2π i n α}: n∈Z}. Eigenvalues of R_{qα} are {e^{2π i n q α}: n∈Z} = {e^{2π i k α}: k∈qZ}. For α irrational, these sets are different unless q=±1. So they are not isomorphic. But for q=2, factor.

But wait, there's a deeper issue: A factor map between measure-preserving systems must map the measure μ to ν. We have that. However, is π_q a *measurable* map? Yes.

Could the user be referring to "circle rotation" meaning the rotation on the circle by an irrational angle? Maybe they know that irrational rotations are not factors of themselves? But they asked "圆旋转你是不是做错了" perhaps because in the original note, exercise 2.1.5-a asks for a measure-preserving system with nontrivial factor map *φ: X→X*, and I gave for circle rotation a factor to a different system, not to itself. Maybe they think I misunderstood. Or they know that circle rotation has no nontrivial endomorphisms? Let's examine.

If the task is find nontrivial factor map φ: X→X for circle rotation R_α, then my π_q gives factor onto R_{qα}, not same transformation. If they want φ: X→X, then for R_α, φ must commute with R_α: φ(R_α x)=R_α(φ(x)). For irrational α, one can show φ(x)=x+c almost everywhere (because R_α is ergodic, φ(x)-x is invariant mod? Let's see). So φ is a rotation itself, which is an isomorphism, so no nontrivial endomorphism for an irrational rotation. For rational rotation, there may be nontrivial endomorphisms because dynamics has finite orbits? Actually if α=p/q rational, then R_α is periodic with period q (not ergodic). There may be factor maps to itself that are not invertible. For example, R_{1/2} on T: map φ(x)=2x mod1. Does φ commute with R_{1/2}? φ(R_{1/2} x)=2x+1≡2x; R_{1/2}(φ(x))=2x+1/2 not equal. So not.

For general rational α=p/q, solve φ(x+α)=φ(x)+α. We can find non-invertible solutions? Suppose α=p/q. The map T decomposes into q circles; a factor to itself could permute fibers? Need condition φ(x+α)=φ(x)+α. Let φ(x)=k x + c mod1. Then k(x+α)+c ≡ k x + c + kα. Need kα ≡ α mod1, i.e., (k-1)p/q ∈ Z. So k ≡ 1 mod q (if gcd(p,q)=1). If k=1+q, then φ(x)=(1+q)x+c. This is non-invertible? For k>1 not coprime to q? gcd(k,q)=gcd(1+q,q)=1, so multiplication by k is invertible as a group automorphism! Because gcd(k,q)=1. So φ is measure-preserving isomorphism? Multiplication by k on T is invertible if gcd(k,q)=1; as a map on T, k invertible mod1? Actually any integer k gives map x→k x; this is not invertible unless k=±1 as a map of the circle? Wait x→kx mod1 is not invertible on T as a measure-preserving transformation unless |k|=1, because kernel has q elements if k=q. But as a group homomorphism, if gcd(k,q)=1, the kernel is {x: kx∈Z} which has k points? For k=3, kernel has 3 points, not invertible. The map is k-to-1 for any |k|>1. But condition kα≡α required k≡1 mod q. If k=1+q, k and q are coprime, still map is k-to-1, not invertible. So it is a nontrivial endomorphism for rational rotation! But the user may not care.

Let's return: User says "圆旋转你是不是做错了，把它的因子展示给我看" likely they want to see the actual factor map/map explicitly, perhaps pointing out that my "circle rotation has factor R_{qα}" is wrong because the factor map should be *onto* and *measure-preserving* but maybe π_q doesn't preserve measure? It does. Or perhaps because for an irrational rotation, R_α and R_{2α} are not isomorphic? But factor doesn't require isomorphic.

Maybe the issue is: In my previous answer, I said "If α is irrational, all nontrivial factors are of form R_{qα}". Is that true? Let's verify carefully. For an ergodic measure-preserving system with discrete spectrum, factors correspond to subgroups of the eigenvalue group. For rotation R_α on T, eigenvalue group is {e^{2π i n α}: n∈Z}. The factor corresponding to multiplication by q has eigenfunctions {e^{2π i q n x}: n∈Z}, which correspond to the subgroup qZ of Z. But could there be a factor corresponding to a rotation on a finite group? For irrational α, e^{2π i n α} for n≠0 are all distinct and never 1. A finite extension factor would have eigenvalues roots of unity, which are not among eigenvalues unless n such that nα∈Z, impossible. So no finite factors. Factors correspond to subgroups of the dual group Z, which are dZ. So yes, only R_{dα} factors. This is a theorem.

But maybe the user is asking "circle rotation and what is a factor" in the context of exercise 2.1.5: "Find a measure-preserving system with a non-trivial factor map φ: X→X." For circle rotation, if they want a nontrivial factor map to itself, my previous answer did not provide one for irrational rotation. Maybe they are pointing out that I made a mistake by giving a factor to a *different* system when the exercise asks for φ:X→X? The original context note indeed says "Find a measure-preserving system (X,B,μ,T) with a non-trivial factor map φ: X → X." The user then asked "圆的旋转与什么是因子" maybe in response to my previous answer? Actually the initial assistant answer (the prior context) was about exercises; then user asked "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" I answered with circle rotation factor R_{qα} and Bernoulli. Now user says "圆旋转你是不是做错了，把它的因子展示给我看" — likely they think my answer was wrong.

Let's scrutinize my previous answer for potential actual error. I wrote:

"对任意正整数 q，定义 π_q(x)=qx mod1. 则 π_q(R_α x)=q(x+α)=qx+qα=R_{qα}(π_q x)." This is correct.

"并且 π_q 把勒贝格测度推到勒贝格测度." Correct.

"因此 (T,B,m,R_{qα}) 是因子." Correct.

Maybe the issue: $R_{qα}$ is not a **measure-preserving system on the circle** because if qα is irrational, yes it is; if qα = 0 mod1 (e.g., α=1/2, q=2), then R_0 = identity, which is still measure-preserving. Fine.

Could the issue be: The map $\pi_q$ is not a **homomorphism** in the sense of "factor map" if the target is $R_{q\alpha}$ but the source is $R_\alpha$? It's just a measurable factor, not topological. OK.

Maybe the user knows that for irrational rotation, $R_\alpha$ is measurably isomorphic to $R_{q\alpha}$? Wait maybe they are isomorphic after all? Let's check: Is $R_{2\alpha}$ isomorphic to $R_\alpha$ for irrational α? On a probability space, an isomorphism is a measure-preserving bijection a.e. commuting. The eigenvalue group of R_α is $G_\alpha = \{e^{2π i nα}: n∈Z\}$. The eigenvalue group of R_{2α} is $G_{2α} = \{e^{2π i n 2α}: n∈Z\} = \{e^{2π i m α}: m∈2Z\}$, a proper subgroup. For measure-preserving isomorphism, the sets of eigenvalues must be equal (as subsets of unit circle) because the Koopman operators are unitarily conjugate. For α irrational, $G_{2α} \subsetneq G_\alpha$ because $e^{2π i α}$ is not in $G_{2α}$: would require $e^{2π i α}=e^{2π i 2nα}$ for some n, i.e., (1-2n)α∈Z, impossible for irrational α. So not isomorphic. So factor nontrivial.

Maybe user thinks circle rotation is *minimal* and *rigid*, and any factor of an irrational rotation is either trivial or isomorphic? No, my factor is correct. Let's maybe compute an explicit example with α irrational to show π_2 indeed factor:
- Let α = √2/2? Actually mod1 irrational. R_α(x)=x+α.
- Define φ(x)=2x mod1.
- φ(R_α(x)) = 2x+2α mod1 = R_{2α}(φ(x)).
- φ_* Leb = Leb.

This is definitely a factor map. So no mistake.

But wait, maybe for the factor map to be onto in the measure sense, we need π_q(X) has full measure in target. π_q(T)=T, so fine.

Let's consider another possible "mistake": In my previous answer, I said "如果 α 是无理数，这些都是非平凡因子；若 α 为有理数，还会有有限旋转因子" — maybe "finite rotation factors" statement could be wrong? For rational rotation R_{p/q}, the system is not ergodic; it's a union of q periodic orbits. Finite factors? There are indeed finite permutation factors: e.g., map x ↦ k mod q if x lies in a certain interval? But since the system is not ergodic, factor map to a finite permutation can be obtained by quotienting the finite orbits modulo something. For R_{1/q}, consider map π(x) = floor(q x) mod q? It maps each x to its "orbit index" maybe; does it commute? R_{p/q} shifts orbit index by p. Specifically, define φ(x)=k when x∈[k/q,(k+1)/q). Then φ(R_{1/q}(x)) = φ(x)+1 mod q if x not exactly at boundary. This is a factor onto the finite permutation on q points. Yes, finite factors exist for rational rotations. Not relevant.

Maybe user's "因子" in Chinese mathematical context could mean "factor" as in "eigenfunction" or "character"? In ergodic theory, "factor" sometimes translated "因子". They might ask "圆的旋转与什么是因子" meaning "What is a factor of a circle rotation?" Maybe they want the factor map itself displayed, and they question because maybe they expected a factor map to a rotation on a finite set? Let's think.

Let's examine the note in prior context: Section 4 "非平凡因子映射" and Exercise 2.1.5-a: "Find a measure-preserving system (X,B,μ,T) with a non-trivial factor map φ: X → X." Then the note's ideas: "常见的保测度系统: 1. finite set permutation 2. circle rotation 3. circle doubling binary Bernoulli 4. Bernoulli shift..." Then "保测度系统非平凡因子: `(T,m,T2)≅({0,1}^N,μ,σ)` ... φ:(T,m)->(X,μ), ∑ a_k/2^k -> (a1,a2,...) satisfies φ(T(x))=σ(φ(x))". They are constructing a factor map from T2 to one-sided Bernoulli. That is not circle rotation.

Exercise 2.1.5-b: "Find an invertible measure-preserving system (X,B,μ,T) with a non-trivial factor map φ:X→X." The user mentions Bernoulli shift {0,1}^Z is invertible. So they are working on part (b). For part (b), perhaps they need an invertible system and a non-trivial factor map φ:X→X. The circle rotation is not the right example because it has no non-trivial factor map to itself unless α rational? Let's check: For irrational α, any endomorphism is an automorphism. Actually let's prove: If φ commutes with R_α and is measure-preserving, then φ is of form φ(x)=x+c? Let's prove:
φ(x+α) = φ(x)+α. Let g(x)=φ(x)-x mod1. Then g(x+α)=g(x). Since R_α is ergodic, g is constant a.e. Thus φ(x)=x+c. This is a rotation, an automorphism. So no non-trivial endomorphism. Thus circle rotation (irrational) cannot satisfy part (b). The user might be saying "圆旋转你是不是做错了" because I proposed circle rotation factor to R_{qα}, but that's a factor to a *different* system, not a factor map from X to X. The exercise asks for φ:X→X. So my answer didn't address the exercise's requirement. That's likely the complaint.

Let's re-read user's original query: "圆的旋转与什么是因子，此外伯努利位移是可逆的（如果考虑{0,1}^Z)，因子是什么。" In Chinese: "For circle rotation, what is a factor? Moreover Bernoulli shift is invertible (if {0,1}^Z is considered), what is a factor?" They may be asking: "In the context of needing a factor map, what can be a factor for circle rotation? And since Bernoulli shift is invertible, what can be a factor?" They might have expected examples of factor maps for the exercise. My reply gave circle rotation factor to R_{qα}. Now they say "圆旋转你是不是做错了，把它的因子展示给我看" = "Did you get circle rotation wrong? Show me its factors." This could be because they think circle rotation has no nontrivial factor (or no factor to itself). They want me to demonstrate.

We need respond carefully: Clarify two notions:
1. If "factor" means a factor map $\pi:X\to Y$ between two systems (Y possibly different), then circle rotation $R_\alpha$ has nontrivial factors $R_{q\alpha}$ via multiplication q. This is correct.
2. If the task instead asks for a **factor map from the system to itself**, i.e., $\phi:X\to X$ with $\phi\circ R_\alpha=R_\alpha\circ\phi$, then for an irrational rotation, any such $\phi$ is a.e. a rotation $x\mapsto x+c$, hence an isomorphism. Thus there is no nontrivial self-factor map. So circle rotation is **not** a valid example for Exercise 2.1.5-b.

Maybe the user wants "show me its factors" in the sense of factor maps to itself. Let's provide both and say "If by factor you mean the usual factor to another system, here it is; if you mean φ:X→X as in the exercise, circle rotation (irrational) doesn't work."

Let's also consider circle rotation with rational α can have nontrivial self-factor maps? Let's explore to be thorough. If α=p/q rational, R_α has period q. Are there non-invertible endomorphisms? Let's solve general measurable φ commuting with R_α. Condition φ(x+α)=φ(x)+α. We can look for φ(x)=k x + c with k∈Z. Then need kα ≡ α mod1, i.e., kp/q - p/q ∈ Z => (k-1)p/q ∈ Z => q | (k-1) (since gcd(p,q)=1). So k=1+qm. Then φ(x)=(1+qm)x+c. As a map on T, this is (1+qm)-to-1, so non-invertible for m≠0. It is measure-preserving: multiplication by integer n on T pushes Lebesgue to Lebesgue (as shown). So for rational rotation, e.g., R_{1/2}, take φ(x)=3x mod1? Check commutes: φ(R_{1/2} x)=3(x+1/2)=3x+1.5 ≡3x+0.5; R_{1/2}(φ(x))=3x+0.5. Yes! So φ is nontrivial endomorphism. Thus for rational rotation, there are nontrivial self-factors. For irrational rotation, none. Maybe this is the nuance the user wants.

But the user says "圆的旋转与什么是因子" without specifying irrational. In examples, circle rotation often means $R_\alpha$ with irrational α (Example 2.2 probably: Let α irrational? In the note, Example 2.2 is circle rotation; could be any α. But in ergodic theory, circle rotation is often studied for irrational α to be ergodic. We should mention both.

Let's also think about "把它的因子展示给我看" maybe they want me to "show the factor" explicitly, i.e., demonstrate with a diagram or equations. I can write:

For any $q$:
\[
\pi_q: \mathbb T \to \mathbb T,\quad \pi_q(x)=qx \mod 1
\]
\[
\pi_q(R_\alpha x)=q(x+\alpha)=qx+q\alpha=R_{q\alpha}(\pi_q x)
\]
\[
(\pi_q)_* m = m \quad (\text{因为每个区间被分成 } q \text{ 等份})
\]
Therefore the factor is:
\[
(\mathbb T, \mathscr B, m, R_{q\alpha}),
\quad R_{q\alpha}(y)=y+q\alpha\mod1.
\]
Example with α irrational and q=2:
\[
\pi_2(x)=2x\mod1,\quad \pi_2(R_\alpha x)=R_{2\alpha}(\pi_2 x).
\]
This is a factor because it is measurable, surjective, measure-preserving, and intertwines.

Then address "if you meant self-factor":

For irrational α, suppose $\phi$ commutes with $R_\alpha$:
\[
\phi(x+\alpha)=\phi(x)+\alpha\pmod1.
\]
Then
\[
\phi(x)-x \text{ is } R_\alpha\text{-invariant}.
\]
Since $R_\alpha$ is ergodic, $\phi(x)-x=c$ a.e., so $\phi(x)=x+c=R_c(x)$, an automorphism. Thus no nontrivial $\phi:\mathbb T\to\mathbb T$. Hence circle rotation (irrational) is **not** an example for the exercise that asks for a map to itself.

For rational α=p/q, choose k=1+q, then φ(x)=kx mod1 commutes with R_α and is not injective, giving a nontrivial self-factor. But perhaps unnecessary; can mention as a side note.

Maybe the user just wants to see the factor displayed, and thinks I made an error because they didn't realize factor targets different system. We'll be explicit.

Let's also double-check the factor map $\pi_q$ "surjective": Multiplication by q is surjective. Measure-preserving: preimage of interval length l is union of q intervals each length l/q, total l. But note: The target measure is Lebesgue. Good.

Could there be an issue with "onto" in factor map: π_q(T)=T, yes.

Let's perhaps draw a simple example:
Take α = √2 mod 1 irrational, q=2.
System A: (T, m, R_α)
System B: (T, m, R_{2α})
Map φ(x)=2x mod1.
- φ(R_α(x)) = 2(x+α)=2x+2α = R_{2α}(2x)=R_{2α}(φ(x)).
- φ_*m = m.
So B is a factor of A. φ is not one-to-one because φ(0)=φ(1/2)=0, but as measure-preserving map on circle, it's 2-to-1. So nontrivial.

This is a complete demonstration.

Let's also maybe mention "If the definition of factor in your course requires $Y$ to be a factor system and $\pi$ to be **onto** in the measure-theoretic sense, this example satisfies it."

Let's answer now in Chinese, acknowledging the possible confusion. Use $ notation. Use bullets. Keep it friendly.

Potential final response structure:

- "我没有做错；要看是哪一种'因子'。"
- "按标准定义（因子映射可到另一个系统），圆旋转的因子如下..."
- Explicit equations and example.
- "如果你指的是题目中 $\phi:X\to X$ 的情形，那么对无理旋转，确实不存在非平凡自因子，理由... 所以圆旋转不能作为那道题的例子；有理旋转则可以，比如 R_{1/2} 取 φ(x)=3x mod1."

Let's decide if to include rational rotation example. It might be useful to fully address "圆旋转你是不是做错了". Include briefly.

Let's verify rational example: α=1/2, R_α(x)=x+1/2. Let φ(x)=3x mod1. φ(R_α(x))=3x+3/2 ≡3x+1/2 (mod1). R_α(φ(x))=3x+1/2. Yes. φ is 3-to-1, measure-preserving, non-invertible. Thus a nontrivial factor map from (T,m,R_{1/2}) to itself. Good.

But wait, is R_{1/2} "circle rotation" as in Example 2.2? Could be. If the exercise asks for any system, this works. But for irrational rotation, no.

Let's also think if for irrational rotation there exist *non-invertible* measurable factor maps to itself not of form φ(x)=x+c but still measure-preserving? The ergodicity proof assumes φ(x)-x invariant: φ(x+α)=φ(x)+α for all x. Since φ∘R_α=R_α∘φ, yes φ(x+α)=φ(x)+α. Then g(x+α)=g(x). Ergodicity means g constant a.e. So φ=R_c a.e., which is invertible. So no.

Thus if the user expects an example from circle rotation for part (b), we can say it's impossible for irrational, possible for rational.

Let's final answer with clarity:

```
你可能指的是两种不同的“因子”：
1. 因子映射到另一个系统：... (this is what I gave)
2. 因子映射到自身 φ:X→X：...
```

Let's not overdo. Use equations.

Let's produce final.</think>我没有做错，只是“因子”有两种理解。我把圆旋转的因子明确写出来，你看是不是这个意思。

## 按一般定义：因子可以到另一个系统

\[
R_\alpha(x)=x+\alpha\pmod 1
\]

对任意正整数 \(q\)，定义

\[
\pi_q:\mathbb T\to\mathbb T,\qquad \pi_q(x)=qx\pmod 1.
\]

它满足

\[
\pi_q(R_\alpha x)=q(x+\alpha)=qx+q\alpha
= R_{q\alpha}(\pi_q x).
\]

并且 \(\pi_q\) 把勒贝格测度推回自己：

\[
m(\pi_q^{-1}([a,b]))=m([a,b]).
\]

所以

\[
(\mathbb T,\mathscr B_{\mathbb T},m_{\mathbb T},R_{q\alpha})
\]

是圆旋转系统

\[
(\mathbb T,\mathscr B_{\mathbb T},m_{\mathbb T},R_\alpha)
\]

的一个因子。

例子：取 \(\alpha\) 为无理数，\(q=2\)，因子映射为

\[
\pi_2(x)=2x\pmod 1,
\]

因子系统为

\[
(\mathbb T,\mathscr B,m,R_{2\alpha}).
\]

这是非平凡的，因为 \(\pi_2\) 不是单射，例如

\[
\pi_2(0)=\pi_2(1/2)=0.
\]

---

## 如果你指的是“到自身的因子映射” \(\phi:X\to X\)

也就是要求

\[
\phi\circ R_\alpha=R_\alpha\circ\phi,
\]

那对**无理旋转**来说，确实不存在非平凡的例子。

因为若有

\[
\phi(x+\alpha)=\phi(x)+\alpha,
\]

则

\[
g(x)=\phi(x)-x
\]

满足

\[
g(x+\alpha)=g(x).
\]

由于 \(R_\alpha\) 是遍历的，\(g\) 几乎处处为常数，所以

\[
\phi(x)=x+c.
\]

这只是旋转，而是同构。因此无理旋转不能作为“有非平凡自因子”的例子。

如果你取**有理旋转**就可以，例如

\[
R_{1/2}(x)=x+\frac12\pmod 1,
\]

取

\[
\phi(x)=3x\pmod 1,
\]

则

\[
\phi(R_{1/2}(x))=3x+\frac32\equiv 3x+\frac12
= R_{1/2}(\phi(x)).
\]

而 \(\phi\) 是三对一的，不是同构，所以是 \(X\to X\) 的非平凡因子映射。
[Timestamp: 2026/09/01 15:13:19]