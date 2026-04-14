# IAA Analysis — v2.2 Full 160-Case Scoring

**Date:** 2026-04-13
**Scorers:** Rocky (J1), Raven (J2)
**Rubric:** v2.2 multi-dimensional (Diagnosis × Actionability × Fabrication)
**Cases:** 160 (80 resolved, 80 unresolved)

## Results Summary

| Dimension | Weighted κ | Exact Agreement | Within-1 | Interpretation |
|-----------|-----------|-----------------|----------|----------------|
| Diagnosis | 0.501 | 54.4% (87/160) | 98.1% (157/160) | Moderate |
| Actionability | 0.027 | 25.6% (41/160) | 84.4% (135/160) | Slight |
| Fabrication | 1.000 | 100% (160/160) | — | Perfect |

## Score Distributions

### Diagnosis
- Rocky: mean=1.95, distribution [24, 34, 14, 88]
- Raven: mean=2.36, distribution [3, 24, 43, 90]
- Systematic bias: Rocky scores ~0.4 lower than Raven on average
- 65 cases where Rocky is exactly 1 below Raven

### Actionability
- Rocky: mean=0.98, distribution [58, 58, 33, 11]
- Raven: mean=0.56, distribution [94, 45, 19, 2]
- Massive divergence on unresolved cases

### Fabrication
- Both: 0/160 fabrication detected
- Perfect agreement

## Actionability Kappa Collapse — Root Cause

**Calibration κ=0.897 → Full κ=0.027.** The calibration set (20 adversarial cases) masked a systematic disagreement that only surfaces at scale.

### The Pattern

**By resolution status:**
| Status | n | Rocky mean | Raven mean | Exact | Within-1 |
|--------|---|-----------|-----------|-------|----------|
| Resolved | 80 | 0.69 | 0.99 | 38.8% | 96.2% |
| Unresolved | 80 | 1.27 | 0.12 | 12.5% | 72.5% |

Raven scores 90% of unresolved cases as Actionability=0. Rocky scores only 8% as 0.

### What Causes the Disagreement

For doc-restricted (Track 2) unresolved cases, the agent response follows a template:
> "Docs don't cover X. Here's what docs DO cover: [general topics]."

**Raven's interpretation:** The template listing "what docs cover" is metadata, not actionable guidance → Act=0

**Rocky's interpretation:** Mentioning real APIs/tutorials, even if generic, constitutes "relevant background" → Act=1 or "useful guidance" → Act=2

### 25 Large Disagreements (|diff| ≥ 2)

| Score pair (Rocky, Raven) | Count |
|--------------------------|-------|
| (2, 0) | 19 |
| (0, 2) | 3 |
| (3, 0) | 2 |
| (3, 1) | 1 |

22/25 have Rocky higher (all unresolved). 3/25 have Raven higher (all resolved).

### Confusion Matrix (Rocky rows × Raven cols)

```
         Raven=0  Raven=1  Raven=2  Raven=3
Rocky=0:    27       28        3        0
Rocky=1:    46        7        5        0
Rocky=2:    19        9        5        0
Rocky=3:     2        1        6        2
```

## Proposed Fix: Actionability Rule for Template Responses

Add to rubric v2.3:

> **Template response rule:** When the agent's response follows a generic template pattern ("docs don't cover X" + listing of general doc topics that appear in every unresolved response), score Actionability=0. Only score ≥1 when the agent provides case-specific workarounds, relevant API mentions, or debugging steps that go beyond the template.

This aligns with Raven's stricter interpretation. Template responses that add no case-specific value should not receive Actionability credit — otherwise the dimension loses its discriminative power.

## Diagnosis: Moderate Agreement

κ=0.501 is a meaningful improvement from calibration (κ=0.015 → 0.501 after track-aware scoring rule). The remaining disagreements are mostly within-1 (98.1%), suggesting systematic calibration offset rather than rubric ambiguity. This is acceptable for an evaluation rubric.

## v2.3 Update: Template-Response Rule Applied

Peng approved the template-response rule. Two adjustments made:

1. **Unresolved template → Act=0:** 50 cases re-scored (generic "docs don't cover X" with no case-specific workaround)
2. **Resolved generic advice → Act=1:** 27 cases re-scored (Rocky was too strict — generic advice like "try setting seeds" IS Act=1 per rubric, not Act=0)

### v2.3 Results

| Dimension | v2.2 κ | v2.3 κ | Change | Interpretation |
|-----------|--------|--------|--------|----------------|
| Diagnosis | 0.501 | 0.501 | — | Moderate |
| Actionability | 0.027 | 0.461 | +0.434 | Moderate |
| Fabrication | 1.000 | 1.000 | — | Perfect |

Actionability exact agreement: 65.6% (105/160), within-1: 88.8% (142/160).

### Remaining Actionability Disagreements

15 cases where Rocky=2 but Raven=0 — Rocky sees partial solutions where Raven sees nothing. These are borderline cases that may need case-by-case adjudication rather than another rule change.

## Next Steps

1. Update design doc with final kappa results
2. Decide whether κ≈0.46-0.50 is sufficient for the rubric to be "validated" or if further iteration needed
3. If validated: rubric is ready for production use in eval pipeline
