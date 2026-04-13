# Inter-Annotator Agreement: Doc-Restricted Mode B Evaluation

**Date:** 2026-04-13
**Scorers:** Rocky, Raven
**Dataset:** 160 torch.compile cases (J1-1 through J8-20)
**Condition:** Mode B, doc-restricted (agent limited to official pytorch.org documentation only)
**Scale:** 0-3 ordinal (0 = no help, 1 = gap identified only, 2 = partially actionable, 3 = fully resolves)

---

## Summary Table

| Metric | Value |
|--------|-------|
| N (cases) | 160 |
| Exact agreement | 46/160 (28.7%) |
| Within +/-1 agreement | 139/160 (86.9%) |
| Cohen's kappa (linear weighted) | 0.077 |
| Cohen's kappa (quadratic weighted) | 0.148 |
| Cohen's kappa (unweighted) | 0.015 |
| Krippendorff's alpha (interval) | 0.033 |
| Spearman rho | 0.507 |
| Pearson r | 0.261 |
| Mean absolute difference | 0.844 |
| RMSD | 1.052 |
| Rocky mean (SD) | 1.725 (0.908) |
| Raven mean (SD) | 1.169 (0.407) |
| Rocky median | 2.0 |
| Raven median | 1.0 |
| Systematic bias (Rocky - Raven) | +0.556 |
| Cases with >= 2 point gap | 21/160 (13.1%) |

**Bottom line:** Agreement is poor. Kappa values near zero indicate agreement barely above chance. The root cause is a fundamental rubric interpretation difference: Rocky awards score=3 for correctly acknowledging a documentation gap (21 cases), while Raven scores those same cases as 1 (generic/no actionable guidance). This single pattern accounts for 20 of 21 large disagreements and inflates Rocky's mean by ~0.5 points.

---

## 1. Exact Agreement Rate

46 of 160 cases (28.7%) have identical scores between Rocky and Raven.

This is low for a 4-point ordinal scale, where chance agreement with these marginal distributions would be approximately 27-30%. The agreement rate is effectively at chance level.

## 2. Within +/-1 Agreement Rate

139 of 160 cases (86.9%) have scores within 1 point of each other.

The remaining 21 cases (13.1%) have a gap of exactly 2 points. No cases have a gap of 3 points. This suggests both scorers operate in roughly the same region of the scale but with a systematic offset.

## 3. Cohen's Kappa

| Variant | Kappa | Interpretation |
|---------|-------|----------------|
| Unweighted | 0.015 | Slight (effectively chance) |
| Linear weighted | 0.077 | Slight |
| Quadratic weighted | 0.148 | Slight |

All kappa values are in the "slight" range (< 0.20) per Landis & Koch benchmarks. The linear weighted kappa of 0.077 means the scorers agree only marginally better than two random raters with the same marginal distributions.

**Why kappa is so low despite 86.9% within-1 agreement:** Raven's extreme concentration on score=1 (84.4% of all ratings) means the expected chance agreement is already high, leaving little room for kappa to register meaningful above-chance agreement. Additionally, the systematic bias (Rocky consistently higher) is exactly the kind of disagreement kappa penalizes.

**Binary kappa at threshold >= 2:** 0.085 (agreement = 45.6%). Rocky rates 102/160 cases as >= 2, Raven rates only 25/160 as >= 2.

## 4. Mean Score Comparison

| Scorer | Mean | SD | Median | Min | Max |
|--------|------|----|--------|-----|-----|
| Rocky | 1.725 | 0.908 | 2.0 | 0 | 3 |
| Raven | 1.169 | 0.407 | 1.0 | 1 | 3 |

Rocky rates 0.556 points higher on average (a 32% relative difference on the 0-3 scale). Rocky also uses the full range (0-3) with meaningful spread (SD=0.908), while Raven is compressed into a narrow band around 1 (SD=0.407).

## 5. Score Distribution

| Score | Rocky | Raven |
|-------|-------|-------|
| 0 | 18 (11.2%) | 0 (0.0%) |
| 1 | 40 (25.0%) | 135 (84.4%) |
| 2 | 70 (43.8%) | 23 (14.4%) |
| 3 | 32 (20.0%) | 2 (1.2%) |

Key observations:
- **Raven never uses score=0.** Rocky uses it for 18 cases where no documentation exists at all. Raven's floor is 1.
- **Raven rarely uses score=3.** Only 2 cases (J1-9, J2-1) vs. Rocky's 32.
- **Raven's modal score is 1** (84.4%). This extreme concentration suggests either (a) a stricter rubric interpretation, or (b) a default/template scoring behavior.
- **Rocky's modal score is 2** (43.8%), producing a more Gaussian-like distribution.

## 6. Systematic Bias

| Direction | Count | % |
|-----------|-------|---|
| Rocky higher | 92 | 57.5% |
| Equal | 46 | 28.7% |
| Raven higher | 22 | 13.8% |

Rocky rates higher than Raven in 57.5% of cases and lower in only 13.8%. The bias is strongly directional.

### Difference Distribution (Rocky - Raven)

| Diff | Count |
|------|-------|
| -2 | 1 |
| -1 | 21 |
| 0 | 46 |
| +1 | 72 |
| +2 | 20 |

The +1 category dominates (72 cases), confirming a consistent 1-point upward bias from Rocky across the dataset.

### Bias by Journey

| Journey | Rocky Mean | Raven Mean | Diff |
|---------|-----------|------------|------|
| J1 (Getting Started) | 1.90 | 1.30 | +0.60 |
| J2 (Performance) | 1.90 | 1.35 | +0.55 |
| J3 (Correctness) | 1.50 | 1.00 | +0.50 |
| J4 (Graph Breaks) | 1.95 | 1.00 | +0.95 |
| J5 (Advanced Perf) | 1.15 | 1.15 | +0.00 |
| J6 (Dynamic Shapes) | 1.75 | 1.30 | +0.45 |
| J7 (Compilation Time) | 1.85 | 1.15 | +0.70 |
| J8 (Advanced Features) | 1.80 | 1.10 | +0.70 |

- **J5 is the only journey with zero bias.** Both scorers agree this journey has poor doc coverage.
- **J4 has the largest bias (+0.95).** Rocky rates J4 cases (graph breaks) as mostly 2, while Raven rates them as uniformly 1. Rocky views the generic graph break template as "partially actionable" (mentions real tools like TORCH_LOGS); Raven views it as "cookie-cutter, non-specific."
- **J7 and J8 have +0.70 bias.** This is driven by the "acknowledges gap = score 3" pattern (see Section 7).

## 7. Disagreement Analysis (>= 2 Point Gap)

21 cases have a gap of 2 or more points. 20 of 21 are Rocky > Raven; only 1 is Raven > Rocky.

### All Cases with >= 2 Point Difference

| Case | Rocky | Raven | Diff | Pattern |
|------|-------|-------|------|---------|
| J1-1 | 3 | 1 | +2 | Fabrication penalty (Raven caps at 1 due to invented API names) |
| J1-20 | 3 | 1 | +2 | Gap acknowledgment scored as 3 by Rocky |
| J2-11 | 3 | 1 | +2 | Gap acknowledgment scored as 3 by Rocky |
| J5-10 | 0 | 2 | -2 | Rocky sees no relevant docs; Raven sees partial actionability |
| J7-11 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-12 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-13 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-14 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-15 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-17 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-18 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-19 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J7-20 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-11 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-12 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-13 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-16 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-17 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-18 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-19 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |
| J8-20 | 3 | 1 | +2 | Gap acknowledgment (cookie-cutter) |

### Root Cause: The "Gap Acknowledgment" Disagreement

**20 of 21 large disagreements** stem from the same rubric interpretation conflict:

- **Rocky's interpretation:** When the agent correctly identifies that official documentation does not cover the user's issue, that IS the correct answer for a doc-restricted evaluation. The agent did the best it could -- it searched, found nothing, and honestly reported the gap. Rocky scores this as 3 ("correctly acknowledges official documentation does not cover this unresolved issue").

- **Raven's interpretation:** The agent gave a generic template response with no specific guidance. Regardless of whether the gap acknowledgment is technically correct, the user gets no actionable help. Raven scores this as 1 ("generic template / no guidance").

This is not a calibration error -- it is a substantive disagreement about what the rubric measures. Rocky evaluates *accuracy of the response given the constraint* (doc-restricted). Raven evaluates *actionable value to the user*.

### Quantifying the Impact

If we re-score Rocky's 21 "gap acknowledgment = 3" cases as 1 (matching Raven's interpretation):
- Rocky's mean would drop from 1.725 to 1.462
- The bias would shrink from +0.556 to +0.294
- Exact agreement would rise from 28.7% to ~41%
- The within-1 agreement would remain at ~87%

### The Single Raven > Rocky Case

**J5-10** (compiling optimizer step): Rocky=0, Raven=2. Rocky found the optimizer docs irrelevant to the compilation error; Raven credited the practical tip ("compile training step function, not optimizer directly") as partially actionable. This is a genuine judgment call about whether generic-but-useful advice counts.

### Fabrication Impact

Only 1 case (J1-1) has a fabrication flag from Raven. Raven capped the score at 1 because the response implied nonexistent functions (`save_cache_artifacts()`/`load_cache_artifacts()`). Rocky scored 3, apparently evaluating the overall correct answer about `TORCHINDUCTOR_FX_GRAPH_CACHE` rather than penalizing the fabricated function names.

---

## Confusion Matrix

Rows = Rocky, Columns = Raven:

|  | Raven=0 | Raven=1 | Raven=2 | Raven=3 |
|--|---------|---------|---------|---------|
| **Rocky=0** | 0 | 17 | 1 | 0 |
| **Rocky=1** | 0 | 36 | 4 | 0 |
| **Rocky=2** | 0 | 62 | 8 | 0 |
| **Rocky=3** | 0 | 20 | 10 | 2 |

Notable: The Rocky=2/Raven=1 cell dominates at 62 cases (38.8% of all cases). This is the workhorse of the disagreement -- Rocky sees generic-but-relevant guidance as "partially actionable" (2), while Raven sees it as "gap identified only" (1).

---

## Recommendations for Rubric Alignment

1. **Resolve the "gap acknowledgment" question explicitly.** The rubric must specify: when docs don't cover the issue and the agent honestly reports this, is that a 3 (correct answer given the constraint) or a 1 (no actionable guidance)? This single decision point accounts for 20/21 large disagreements and 13% of all cases.

2. **Define score=2 vs score=1 boundary more precisely.** The Rocky=2/Raven=1 block (62 cases) suggests the scorers disagree on whether "mentions real tools/docs but doesn't engage with specifics" constitutes partial actionability. Add examples to the rubric for borderline cases.

3. **Clarify fabrication penalty policy.** Raven caps at 1 if any fabrication is detected (even if the overall answer is correct). Rocky does not apply this penalty. The rubric should specify whether fabrication is a cap or a deduction.

4. **Consider whether Raven's floor of 1 is appropriate.** Raven never assigns 0 even when no docs exist and no guidance is given. Rocky uses 0 for 18 such cases. The rubric should specify what constitutes a 0 vs 1.

---

## Appendix: Full Score Comparison

| Case | Rocky | Raven | Diff |
|------|-------|-------|------|
| J1-1 | 3 | 1 | +2 |
| J1-2 | 3 | 2 | +1 |
| J1-3 | 1 | 2 | -1 |
| J1-4 | 1 | 1 | 0 |
| J1-5 | 3 | 2 | +1 |
| J1-6 | 1 | 1 | 0 |
| J1-7 | 0 | 1 | -1 |
| J1-8 | 0 | 1 | -1 |
| J1-9 | 3 | 3 | 0 |
| J1-10 | 2 | 1 | +1 |
| J1-11 | 3 | 2 | +1 |
| J1-12 | 2 | 1 | +1 |
| J1-13 | 1 | 1 | 0 |
| J1-14 | 2 | 1 | +1 |
| J1-15 | 2 | 1 | +1 |
| J1-16 | 2 | 1 | +1 |
| J1-17 | 2 | 1 | +1 |
| J1-18 | 2 | 1 | +1 |
| J1-19 | 2 | 1 | +1 |
| J1-20 | 3 | 1 | +2 |
| J2-1 | 3 | 3 | 0 |
| J2-2 | 2 | 2 | 0 |
| J2-3 | 3 | 2 | +1 |
| J2-4 | 2 | 1 | +1 |
| J2-5 | 2 | 2 | 0 |
| J2-6 | 3 | 2 | +1 |
| J2-7 | 0 | 1 | -1 |
| J2-8 | 0 | 1 | -1 |
| J2-9 | 3 | 2 | +1 |
| J2-10 | 1 | 1 | 0 |
| J2-11 | 3 | 1 | +2 |
| J2-12 | 2 | 1 | +1 |
| J2-13 | 2 | 1 | +1 |
| J2-14 | 1 | 1 | 0 |
| J2-15 | 2 | 1 | +1 |
| J2-16 | 1 | 1 | 0 |
| J2-17 | 2 | 1 | +1 |
| J2-18 | 2 | 1 | +1 |
| J2-19 | 2 | 1 | +1 |
| J2-20 | 2 | 1 | +1 |
| J3-1 | 1 | 1 | 0 |
| J3-2 | 1 | 1 | 0 |
| J3-3 | 1 | 1 | 0 |
| J3-4 | 1 | 1 | 0 |
| J3-5 | 1 | 1 | 0 |
| J3-6 | 1 | 1 | 0 |
| J3-7 | 1 | 1 | 0 |
| J3-8 | 1 | 1 | 0 |
| J3-9 | 1 | 1 | 0 |
| J3-10 | 1 | 1 | 0 |
| J3-11 | 2 | 1 | +1 |
| J3-12 | 2 | 1 | +1 |
| J3-13 | 2 | 1 | +1 |
| J3-14 | 2 | 1 | +1 |
| J3-15 | 2 | 1 | +1 |
| J3-16 | 2 | 1 | +1 |
| J3-17 | 2 | 1 | +1 |
| J3-18 | 2 | 1 | +1 |
| J3-19 | 2 | 1 | +1 |
| J3-20 | 2 | 1 | +1 |
| J4-1 | 2 | 1 | +1 |
| J4-2 | 2 | 1 | +1 |
| J4-3 | 2 | 1 | +1 |
| J4-4 | 2 | 1 | +1 |
| J4-5 | 2 | 1 | +1 |
| J4-6 | 2 | 1 | +1 |
| J4-7 | 1 | 1 | 0 |
| J4-8 | 2 | 1 | +1 |
| J4-9 | 2 | 1 | +1 |
| J4-10 | 2 | 1 | +1 |
| J4-11 | 2 | 1 | +1 |
| J4-12 | 2 | 1 | +1 |
| J4-13 | 2 | 1 | +1 |
| J4-14 | 2 | 1 | +1 |
| J4-15 | 2 | 1 | +1 |
| J4-16 | 2 | 1 | +1 |
| J4-17 | 2 | 1 | +1 |
| J4-18 | 2 | 1 | +1 |
| J4-19 | 2 | 1 | +1 |
| J4-20 | 2 | 1 | +1 |
| J5-1 | 1 | 2 | -1 |
| J5-2 | 1 | 1 | 0 |
| J5-3 | 1 | 1 | 0 |
| J5-4 | 0 | 1 | -1 |
| J5-5 | 1 | 1 | 0 |
| J5-6 | 0 | 1 | -1 |
| J5-7 | 0 | 1 | -1 |
| J5-8 | 0 | 1 | -1 |
| J5-9 | 1 | 1 | 0 |
| J5-10 | 0 | 2 | -2 |
| J5-11 | 2 | 1 | +1 |
| J5-12 | 2 | 1 | +1 |
| J5-13 | 2 | 1 | +1 |
| J5-14 | 1 | 1 | 0 |
| J5-15 | 1 | 2 | -1 |
| J5-16 | 2 | 1 | +1 |
| J5-17 | 2 | 1 | +1 |
| J5-18 | 2 | 1 | +1 |
| J5-19 | 2 | 1 | +1 |
| J5-20 | 2 | 1 | +1 |
| J6-1 | 2 | 2 | 0 |
| J6-2 | 0 | 1 | -1 |
| J6-3 | 1 | 1 | 0 |
| J6-4 | 1 | 1 | 0 |
| J6-5 | 3 | 2 | +1 |
| J6-6 | 2 | 2 | 0 |
| J6-7 | 2 | 2 | 0 |
| J6-8 | 2 | 2 | 0 |
| J6-9 | 1 | 1 | 0 |
| J6-10 | 2 | 2 | 0 |
| J6-11 | 2 | 1 | +1 |
| J6-12 | 2 | 1 | +1 |
| J6-13 | 2 | 1 | +1 |
| J6-14 | 1 | 1 | 0 |
| J6-15 | 2 | 1 | +1 |
| J6-16 | 2 | 1 | +1 |
| J6-17 | 2 | 1 | +1 |
| J6-18 | 2 | 1 | +1 |
| J6-19 | 2 | 1 | +1 |
| J6-20 | 2 | 1 | +1 |
| J7-1 | 1 | 2 | -1 |
| J7-2 | 1 | 1 | 0 |
| J7-3 | 1 | 1 | 0 |
| J7-4 | 1 | 1 | 0 |
| J7-5 | 1 | 1 | 0 |
| J7-6 | 0 | 1 | -1 |
| J7-7 | 0 | 1 | -1 |
| J7-8 | 0 | 1 | -1 |
| J7-9 | 2 | 2 | 0 |
| J7-10 | 0 | 1 | -1 |
| J7-11 | 3 | 1 | +2 |
| J7-12 | 3 | 1 | +2 |
| J7-13 | 3 | 1 | +2 |
| J7-14 | 3 | 1 | +2 |
| J7-15 | 3 | 1 | +2 |
| J7-16 | 3 | 2 | +1 |
| J7-17 | 3 | 1 | +2 |
| J7-18 | 3 | 1 | +2 |
| J7-19 | 3 | 1 | +2 |
| J7-20 | 3 | 1 | +2 |
| J8-1 | 1 | 1 | 0 |
| J8-2 | 1 | 1 | 0 |
| J8-3 | 1 | 1 | 0 |
| J8-4 | 1 | 1 | 0 |
| J8-5 | 1 | 1 | 0 |
| J8-6 | 0 | 1 | -1 |
| J8-7 | 0 | 1 | -1 |
| J8-8 | 1 | 1 | 0 |
| J8-9 | 0 | 1 | -1 |
| J8-10 | 0 | 1 | -1 |
| J8-11 | 3 | 1 | +2 |
| J8-12 | 3 | 1 | +2 |
| J8-13 | 3 | 1 | +2 |
| J8-14 | 3 | 2 | +1 |
| J8-15 | 3 | 2 | +1 |
| J8-16 | 3 | 1 | +2 |
| J8-17 | 3 | 1 | +2 |
| J8-18 | 3 | 1 | +2 |
| J8-19 | 3 | 1 | +2 |
| J8-20 | 3 | 1 | +2 |
