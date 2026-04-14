# Track 1 IAA — v2.8 Rubric on Unrestricted Agent Guidance

**Date:** 2026-04-14
**Scorer 1:** Owl
**Scorer 2:** Raven
**Dataset:** 160 cases (8 journeys × 20), Track 1 (unrestricted — agent had full web access)
**Rubric:** v2.8 multi-dimensional

## Results

| Dimension | Weighted κ (quadratic) | Interpretation | Target | Status |
|-----------|----------------------|----------------|--------|--------|
| Diagnosis | 0.415 | Moderate | ≥0.80 | **Fails** |
| Actionability | 0.486 | Moderate | ≥0.80 | **Fails** |
| Fabrication | 0.000 | Slight | ≥90% agreement | 85% agreement — **Fails** |

### Comparison with Track 2 (doc-restricted) IAA

| Dimension | Track 2 κ (160 cases) | Track 2 κ (24 holdout) | Track 1 κ (160 cases) |
|-----------|----------------------|----------------------|----------------------|
| Diagnosis | 0.863 | 0.705 | **0.415** |
| Actionability | 0.885 | 0.853 | **0.486** |
| Fabrication | 96.2% | 100% | **85.0%** |

Track 1 IAA is dramatically lower than Track 2. The rubric works well for doc-restricted responses but breaks down on unrestricted responses.

## Root Cause Analysis

### 1. Systematic Bias: Owl scores lower than Raven

Both dimensions show the same pattern:
- **Diagnosis:** Owl mean 2.34, Raven mean 2.69 (bias: −0.35)
- **Actionability:** Owl mean 1.89, Raven mean 2.23 (bias: −0.34)

Owl used Diag=2 for 80/160 cases; Raven used Diag=2 for only 46. Owl used Act=1 for 43/160; Raven used Act=1 for only 26. Owl is systematically stricter.

### 2. Diagnosis: The 2/3 boundary (again)

Confusion matrix shows 45 cases where Owl=2, Raven=3. The same boundary that was borderline on the holdout set (κ=0.705) collapses further on Track 1 data.

**Why Track 1 makes the 2/3 boundary harder:** In Track 2, most responses follow a predictable pattern — either the docs cover it (specific fix) or they don't (gap acknowledgment). The 2/3 boundary is relatively clear. In Track 1, responses are more varied — the agent cites GitHub issues, blog posts, source code, and forum discussions. Judging whether the agent "named the specific mechanism" vs "named the right subsystem" is more subjective when the response draws from diverse sources.

### 3. Actionability: The 1/2 and 2/3 boundaries

- 32 cases where Owl=2, Raven=3: Owl judged these as partial solutions requiring further work; Raven credited them as standalone fixes.
- 14 cases where Owl=1, Raven=2: Owl applied the interchangeability test strictly (same advice for similar cases); Raven credited case specificity.
- 8 large disagreements (|diff|≥2), all Owl=1, Raven=3 — concentrated in J6 (Dynamic Shapes).

### 4. Fabrication: Complete disagreement

Owl flagged 24/160 cases (15.0%), Raven flagged 0/160 (0.0%). κ=0.000 (no better than chance).

**This is the critical finding.** The scorers have fundamentally different fabrication thresholds. Possible causes:
- Owl's sub-agents may have false-positive fabrication flags (flagging APIs that do exist)
- Raven may not be checking fabrication rigorously on Track 1 (where responses are longer and more complex)
- The v2.8 rubric's fabrication definition may be clear for Track 2 but ambiguous for Track 1

**Action needed:** Reconcile the 24 disputed cases. For each, determine whether the flagged API/config actually exists in PyTorch. The automated `verify_claims.py` detector should be the tiebreaker.

## Large Disagreements

### Diagnosis (|diff| ≥ 2): 3 cases
| Case | Owl | Raven | Δ |
|------|-----|-------|---|
| J5-1 | 1 | 3 | -2 |
| J6-4 | 1 | 3 | -2 |
| J6-10 | 1 | 3 | -2 |

### Actionability (|diff| ≥ 2): 8 cases
| Case | Owl | Raven | Δ |
|------|-----|-------|---|
| J4-8 | 1 | 3 | -2 |
| J5-1 | 1 | 3 | -2 |
| J5-7 | 1 | 3 | -2 |
| J6-4 | 1 | 3 | -2 |
| J6-5 | 1 | 3 | -2 |
| J6-6 | 1 | 3 | -2 |
| J6-7 | 1 | 3 | -2 |
| J6-10 | 1 | 3 | -2 |

**Pattern:** J6 (Dynamic Shapes) is over-represented. 5 of 8 large Act disagreements are in J6. This suggests the rubric handles this journey differently between scorers — likely the interchangeability test applied to `mark_dynamic` / `dynamic=True` advice.

## Interpretation

1. **The v2.8 rubric was designed for Track 2 (doc-restricted) and validated on Track 2 data.** The bright-line tests (template detection, imperative verb test) were calibrated against doc-restricted responses which follow predictable patterns. Track 1 responses are more varied, making these tests harder to apply consistently.

2. **Track 1 may need its own calibration round.** The rubric includes Track 1 rules (e.g., "docs don't cover this" = Diag=1 for Track 1), but these rules were never empirically validated with a calibration loop like the Track 2 rules were.

3. **Fabrication reconciliation is the first priority.** The 24 vs 0 disagreement on fabrication undermines the entire comparison. If many of Owl's flags are false positives (APIs that actually exist), then Owl's lower scores may be systematically inflated downward.

## Recommendation

Before running another rubric iteration:

1. **Reconcile fabrication:** Run `verify_claims.py` on the Track 1 guidance to get an objective fabrication count. Compare against Owl's 24 flags and Raven's 0 flags.
2. **Joint calibration on disagreements:** Have both scorers review the 8 large-disagreement cases with rationales visible. Identify which rubric rules are ambiguous for Track 1.
3. **Consider Track 1-specific boundary refinements:** The 2/3 boundaries may need different bright-line tests for unrestricted responses, where the "specificity" of a diagnosis depends on the richness of sources consulted.

---
*Analysis by Owl, 2026-04-14.*
