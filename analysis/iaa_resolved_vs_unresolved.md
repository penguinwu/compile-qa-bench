# IAA Analysis: Resolved vs Unresolved Cases

**Date:** 2026-04-13
**Scorers:** Rocky (mode B adjusted scores) vs Raven (doc-restricted scores)
**Scale:** 0-3 (0=confidently wrong, 1=gap acknowledged, 2=partially helpful, 3=fully actionable)
**n=160 total** (80 resolved, 80 unresolved)

---

## Summary Comparison Table

| Metric | Resolved (n=80) | Unresolved (n=80) | All (n=160) |
|--------|:---:|:---:|:---:|
| **Exact agreement** | 36/80 (45.0%) | 18/80 (22.5%) | 54/160 (33.8%) |
| **Within +/-1** | 76/80 (95.0%) | 70/80 (87.5%) | 146/160 (91.2%) |
| **Cohen's kappa (linear)** | 0.122 | -0.053 | 0.014 |
| **Rocky mean** | 1.750 | 1.838 | 1.794 |
| **Raven mean** | 1.275 | 1.063 | 1.169 |
| **Mean diff (Rocky - Raven)** | +0.475 | +0.775 | +0.625 |
| **Rocky higher** | 39 cases | 59 cases | 98 cases |
| **Raven higher** | 5 cases | 3 cases | 8 cases |
| **Ties** | 36 cases | 18 cases | 54 cases |
| **Both score 1 (floor)** | 23 (29%) | 16 (20%) | 39 (24%) |
| **Both score >=2** | 17 (21%) | 2 (2.5%) | 19 (12%) |

---

## Key Findings

### 1. Hypothesis confirmed: Agreement is substantially worse on unresolved cases

Exact agreement drops from 45% (resolved) to 22.5% (unresolved). Cohen's kappa drops from 0.122 (slight agreement) to -0.053 (worse than chance). The within-+/-1 rate also degrades from 95% to 87.5%.

### 2. The disagreement is driven by systematic bias, not random noise

The dominant disagreement pattern is **Rocky=2, Raven=1**:
- Resolved: 33 cases (41% of subset)
- Unresolved: 51 cases (64% of subset)

Rocky credits partial diagnostic value ("right area, reasonable workaround") while Raven demands doc-grounded evidence ("no docs found, no guidance"). On unresolved cases, Rocky gives credit for plausible reasoning from code knowledge; Raven only scores what the docs explicitly cover.

### 3. Raven's scoring collapses on unresolved cases

Raven score distribution:
- Resolved: 60 score-1, 18 score-2, 2 score-3
- Unresolved: 75 score-1, 5 score-2, 0 score-3

Raven gives score=1 to **94% of unresolved cases** vs 75% of resolved cases. The unresolved category has almost no score variance from Raven (sigma=0.242), making kappa computation unreliable due to near-constant ratings.

### 4. Rocky maintains score variance across both subsets

Rocky score distribution:
- Resolved: 26 score-1, 48 score-2, 6 score-3
- Unresolved: 17 score-1, 53 score-2, 8 score-3 (+ 2 score-0)

Rocky's mean is actually slightly *higher* on unresolved cases (1.838 vs 1.750), suggesting Rocky evaluates answer quality independent of resolution status while Raven's scoring is heavily influenced by doc coverage (which is sparser for unresolved cases).

### 5. The bias is not fabrication-driven

Rocky fabrications are actually *lower* on unresolved cases (10/80 = 12.5%) than resolved (16/80 = 20%). The disagreement is not because Rocky is giving inflated scores to fabricated answers on unresolved cases.

---

## Score Distribution Detail

### Resolved (Rocky, Raven) pair counts:
```
(1, 1): 23    (1, 2): 3
(2, 1): 33    (2, 2): 13    (2, 3): 2
(3, 1): 4     (3, 2): 2
```

### Unresolved (Rocky, Raven) pair counts:
```
(0, 2): 2
(1, 1): 16    (1, 2): 1
(2, 1): 51    (2, 2): 2
(3, 1): 8
```

The (2,1) cell is the dominant disagreement pattern in both subsets but is far more pronounced in unresolved (51/80 vs 33/80).

---

## Per-Journey Breakdown

| Journey | Subset | Exact | +/-1 | Rocky Mean | Raven Mean |
|---------|--------|:-----:|:----:|:----------:|:----------:|
| J1 | Resolved | 2/10 (20%) | 9/10 (90%) | 2.20 | 1.50 |
| J1 | Unresolved | 2/10 (20%) | 8/10 (80%) | 1.90 | 1.10 |
| J2 | Resolved | 7/10 (70%) | 10/10 (100%) | 1.80 | 1.70 |
| J2 | Unresolved | 2/10 (20%) | 9/10 (90%) | 1.90 | 1.00 |
| J3 | Resolved | 4/10 (40%) | 10/10 (100%) | 1.60 | 1.00 |
| J3 | Unresolved | 2/10 (20%) | 8/10 (80%) | 2.00 | 1.00 |
| J4 | Resolved | 4/10 (40%) | 9/10 (90%) | 1.70 | 1.00 |
| J4 | Unresolved | 2/10 (20%) | 8/10 (80%) | 2.00 | 1.00 |
| J5 | Resolved | 7/10 (70%) | 10/10 (100%) | 1.30 | 1.20 |
| J5 | Unresolved | 5/10 (50%) | 10/10 (100%) | 1.60 | 1.10 |
| J6 | Resolved | 9/10 (90%) | 10/10 (100%) | 1.70 | 1.60 |
| J6 | Unresolved | 0/10 (0%) | 10/10 (100%) | 2.00 | 1.00 |
| J7 | Resolved | 1/10 (10%) | 9/10 (90%) | 1.80 | 1.20 |
| J7 | Unresolved | 4/10 (40%) | 10/10 (100%) | 1.70 | 1.10 |
| J8 | Resolved | 2/10 (20%) | 9/10 (90%) | 1.90 | 1.00 |
| J8 | Unresolved | 1/10 (10%) | 7/10 (70%) | 1.60 | 1.20 |

### Notable journey patterns:

- **J6 (Dynamic Shapes):** Most extreme split. Resolved has 90% exact agreement (both scorers converge at 1-2 where docs exist). Unresolved has 0% exact agreement (Rocky gives 2 to all 10 cases, Raven gives 1 to all 10).
- **J2 (Performance):** Strong resolved agreement (70% exact) collapses to 20% on unresolved, mirroring the overall pattern.
- **J3 (Correctness) and J4 (Graph Breaks):** Raven gives 1 to all 10 resolved J3 and J4 cases. Both journeys have uniformly low Raven scores regardless of resolution status -- Raven's boilerplate/template pattern dominates these journeys.
- **J8 (Advanced Features):** Worst unresolved +/-1 rate (70%), driven by two cases (J8-14, J8-15) where Rocky gives 0 but Raven gives 2 -- the only cases where Raven confidently scores higher.

---

## Failure Mode Clustering

### Where Raven gives 1 (floor score)

| Pattern | Resolved | Unresolved |
|---------|:--------:|:----------:|
| "No docs / no guidance / no actionable" | 21 | 42 |
| "Boilerplate / template / generic / identical" | 22 | 36 |
| Total Raven=1 cases | 60 | 75 |

The "no docs found" failure mode doubles from resolved to unresolved, confirming that Raven's doc-restricted scoring harshly penalizes gaps in documentation coverage. The boilerplate pattern is also more prevalent in unresolved cases, where the LLM response tends to fall back on generic templates.

### Disagreements >= 2 points

**Resolved (4 cases, all Rocky > Raven):**
- J1-4: Rocky=3 vs Raven=1 -- Rocky credits actionable Dockerfile fixes; Raven says "just restates problem"
- J4-10: Rocky=3 vs Raven=1 -- Rocky credits documented tensor-lr solution; Raven applies graph break template
- J7-3: Rocky=3 vs Raven=1 -- Rocky credits foreach=True/fused=True as correct fix; Raven says "no specific guidance"
- J8-6: Rocky=3 vs Raven=1 -- Rocky credits valid TF32 precision recommendations; Raven says "no guidance"

**Unresolved (10 cases):**
- 8 cases Rocky > Raven by 2: Rocky credits code-derived solutions (TORCHINDUCTOR_COMPILE_THREADS=1, libcuda.so symlink, XPU support, omp.h fix, torch.where/torch.cond, frozen dataclasses, once_differentiable, CUDA graph thread safety). Raven gives boilerplate "no docs" / "file GitHub issue."
- 2 cases Raven > Rocky by 2 (J8-14, J8-15): Rocky gives 0 for claiming torch.scan/associative_scan don't exist; Raven gives 2 for correctly identifying them as undocumented. These are the only cases where Rocky is confidently wrong and Raven is right.

---

## Systematic Bias Analysis

| Direction | Resolved | Unresolved |
|-----------|:--------:|:----------:|
| Rocky higher by 1 | 35 | 51 |
| Rocky higher by 2 | 4 | 8 |
| Raven higher by 1 | 5 | 1 |
| Raven higher by 2 | 0 | 2 |
| Tied | 36 | 18 |

Rocky consistently scores higher than Raven, with the bias amplified on unresolved cases. The asymmetry is stark: Rocky scores higher in 74% of unresolved cases vs 49% of resolved cases.

**Root cause:** The two scorers are applying fundamentally different rubrics:
- **Rocky** evaluates whether the *answer* provides useful diagnostic direction, regardless of whether official docs exist
- **Raven** evaluates whether the answer is grounded in *discoverable documentation*, penalizing answers that draw from code knowledge or general expertise

On resolved cases, these rubrics partially overlap (docs exist for the fix, so both can agree). On unresolved cases, the rubrics diverge sharply (no docs exist, so Raven floors the score while Rocky still credits the reasoning).

---

## Implications for Eval Design

1. **The kappa values (0.122 resolved, -0.053 unresolved) indicate the IAA is unreliable** for making fine-grained distinctions. The rubric needs revision before scores can be treated as ground truth.

2. **The resolved/unresolved split reveals a rubric ambiguity, not a case quality difference.** Both scorers are internally consistent -- the disagreement is about what "helpful" means when docs don't exist.

3. **Consider separate rubrics or anchoring:** For unresolved cases, the evaluation should explicitly define whether credit is given for (a) correct gap identification, (b) plausible workarounds from code knowledge, or (c) only doc-grounded guidance.

4. **Raven's near-constant scoring on unresolved cases (94% score=1) means those scores carry almost no discriminative information.** If the eval retains unresolved cases, the rubric must create meaningful score variance.

5. **The 2 cases where Rocky scores 0 (J8-14, J8-15) highlight a different failure mode:** Rocky was confidently wrong about API existence, while Raven correctly identified the gap. This suggests Rocky's code-derived answers, while generally more generous, carry fabrication risk that Raven avoids by staying closer to docs.
