# Holdout Set IAA — Rubric v2.8 Generalization Test

**Date:** 2026-04-14
**Scorer 1:** Owl (replaced Rocky)
**Scorer 2:** Raven
**Dataset:** 24 held-out cases (3 per journey × 8 journeys), Track 2 (doc-restricted)
**Rubric:** v2.8 multi-dimensional

## Purpose

Test whether the v2.8 rubric generalizes to new cases not used during rubric development. The 160-case IAA (Diag κ=0.863, Act κ=0.885) could be inflated if scorers learned case-specific patterns during iterative calibration.

## Results

| Dimension | Weighted κ (quadratic) | Interpretation | Target | Status |
|-----------|----------------------|----------------|--------|--------|
| Diagnosis | 0.705 | Substantial | ≥0.80 | Below target |
| Actionability | 0.853 | Near-perfect | ≥0.80 | **Passes** |
| Fabrication | 1.000 | Near-perfect | ≥0.90% | **Passes** |

### Diagnosis Detail

- Exact agreement: 15/24 (62.5%)
- Within ±1: 24/24 (100.0%) — no large disagreements
- Scorer 1 (Owl) mean: 2.25, dist: [0, 4, 10, 10]
- Scorer 2 (Raven) mean: 2.38, dist: [0, 6, 3, 15]
- Bias: Owl −0.12 vs Raven (Owl slightly lower)

**Pattern:** Raven is more bimodal (Diag=1 or Diag=3), while Owl uses Diag=2 more frequently (10 vs 3). Five cases where Owl=2, Raven=3 — Owl judged the mechanism identification as imprecise where Raven credited it as correct. Three cases where Owl=2, Raven=1 — Owl credited a case-specific causal chain where Raven called it tangential.

The Diag 2/3 boundary is the primary source of disagreement. This mirrors the 160-case experience where the "precision threshold" rule had to be iterated multiple times (v2.5 → v2.8).

### Actionability Detail

- Exact agreement: 17/24 (70.8%)
- Within ±1: 24/24 (100.0%)
- Scorer 1 (Owl) mean: 1.75, dist: [2, 8, 8, 6]
- Scorer 2 (Raven) mean: 1.54, dist: [3, 12, 2, 7]
- Bias: Owl +0.21 vs Raven (Owl slightly higher)

**Pattern:** Five cases where Owl=2, Raven=1. These follow the interchangeability boundary — Owl credited partial specificity, Raven applied the interchangeability test strictly. Despite this, the κ exceeds the 0.80 threshold, indicating the bright-line tests (template rule, imperative test) are working.

## Interpretation

1. **Actionability generalizes well (κ=0.853).** The bright-line tests (template detection, imperative verb test, interchangeability test) transfer cleanly to new cases. This is the dimension that collapsed to κ=0.027 in the first v2 attempt — the v2.8 fixes are durable.

2. **Diagnosis is borderline (κ=0.705).** The 2/3 boundary remains the weakest joint. The "could a developer write the fix from this diagnosis?" test is inherently more subjective than the mechanical tests used for Actionability. However, 100% within-1 agreement and zero large disagreements indicate the rubric prevents catastrophic disagreement.

3. **No scorer overfitting detected.** If scorers had memorized 160-case patterns, we'd expect holdout κ to drop sharply. The Actionability drop (0.885→0.853) is minimal. The Diagnosis drop (0.863→0.705) is meaningful but the 160-case κ may have been slightly inflated by the calibration loop (scorers saw each other's disagreements and converged).

4. **Fabrication is trivially reliable.** Both scorers found zero fabrications in the holdout set. This doesn't test discrimination — it confirms both scorers ignore false positives from well-formed responses.

## Recommendation

The rubric is production-ready for Actionability and Fabrication. Diagnosis needs a decision:

**Option A:** Accept κ=0.705 as "good enough." It's Substantial per Landis & Koch, within-1 is 100%, and the remaining disagreements are at a boundary (2 vs 3) where the practical difference is small (both indicate the agent understood the problem area).

**Option B:** Add one more refinement to the Diag 2/3 boundary. Possible rule: "If the agent names the specific API, function, or config that needs to change → Diag=3. If the agent names only the subsystem or interaction → Diag=2." This would make the 2/3 boundary as mechanical as the Actionability boundaries.

**My recommendation:** Option A. The marginal gain from further refinement is small, and each iteration risks overfitting the rubric to scorer idiosyncrasies. A κ=0.705 on fresh data with 100% within-1 is a stronger validity signal than a κ=0.90 achieved through 8 rounds of mutual calibration.

---
*Analysis by Owl, 2026-04-14.*
