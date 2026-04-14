# Ontology Ground Truth Trial — 10 Cases

**Date:** 2026-04-14
**Source:** Prof's PT2 Ontology (6,167 oncall:pt2 issues from Hive)
**Coverage:** 8/10 trial cases found in dataset (2 missing: #110666, #121989)

## Purpose

Test whether Prof's PT2 Ontology can serve as external ground truth for validating our scoring rubric. The ontology provides: resolution type, symptom classification, component mapping, linked fix PRs, and workarounds — independently of our rubric scoring.

## Trial Comparison

| Case | Ontology Component | Ontology Resolution | Rubric Diag (R/Rv) | Rubric Act (R/Rv) | Alignment? |
|---|---|---|---|---|---|
| J1-1 | compile_cache | user_adaptation (docs) | 3/3 | 3/3 | ✅ Agent correctly identified cache API — matches ontology |
| J3-1 | torchinductor | user_adaptation (upgrade) | 1/1 | 1/0 | ✅ Low scores justified: agent gave generic troubleshooting, ontology says fix is "upgrade to ≥2.9.0" — agent missed specific fix |
| J4-1 | flexattention, torchdynamo | compiler_fix (#164349, #164923) | 1/1 | 1/1 | ✅ Low scores justified: agent gave generic graph break advice, ontology shows root cause was inspect.signature incompatibility — agent missed it |
| J5-1 | pt2_cudagraph, torchinductor | user_workaround | 0/1 | 1/1 | ✅ Low scores justified: ontology says root cause is cudagraph mutation replay, agent fabricated explanation about CUDA graphs / kernel selection |
| J6-1 | dynamic_shapes | compiler_fix + workaround | 1/3 | 1/1 | ⚠️ Scorer disagreement: Rocky scored Diag=1 (generic), Raven scored Diag=3. Ontology confirms mark_dynamic is the correct workaround — Raven's score better calibrated here |
| J8-1 | pt2_dispatch | user_adaptation (docs) | 1/1 | 0/0 | ✅ Low scores justified: agent pointed to Triton tutorial (wrong), ontology says custom ops need to be Python-decomposable — completely different guidance needed |
| J1-11 | compile_cache | unresolved | 3/3 | 1/0 | ✅ Correct unresolved identification, low actionability appropriate |
| J1-12 | torchdynamo | unresolved (feature gap) | 3/3 | 0/0 | ✅ Correct identification of undocumented limitation |

## Findings

### Alignment Rate
**7/8 cases (87.5%)** show full alignment between ontology ground truth and rubric scores. The rubric correctly identifies:
- When agents get the right answer (J1-1: Diag=3, matches ontology)
- When agents give generic advice that misses the specific fix (J3-1, J4-1, J5-1, J8-1: Diag≤1, ontology confirms specific fix was missed)
- When issues are genuinely unresolved (J1-11, J1-12: Diag=3 for honest identification)

### One Disagreement (J6-1)
Rocky scored Diag=1, Raven scored Diag=3. The ontology confirms the agent mentioned `mark_dynamic` — the correct workaround per the ontology. This suggests Raven's scoring is better calibrated for this case. Worth investigating whether Rocky's scoring was too strict or whether the agent's explanation was too generic despite mentioning the right tool.

### What the Ontology Adds
1. **Component ground truth** — we can mechanically check: did the agent identify the right PyTorch component? The ontology labels each issue with specific components (torchinductor, torchdynamo, compile_cache, dynamic_shapes, etc.)
2. **Fix specificity** — the ontology has specific PRs and workarounds. We can check: did the agent's guidance match the actual fix, or was it generic?
3. **Resolution type** — distinguishes compiler_fix (need new PyTorch version) from user_workaround (user can act now) from user_adaptation (docs/guidance sufficient). This maps to Actionability: user_workaround cases should have higher actionability potential.

### Limitations
1. **~80% coverage** — 2/10 cases not in Hive. Full 160-case mapping may have similar gaps.
2. **Diagnosis alignment is coarse** — ontology says "component: torchinductor" but doesn't grade granularity of diagnosis. Our rubric distinguishes "right area" (Diag=1) from "right mechanism" (Diag=2) from "correct root cause" (Diag=3). The ontology can confirm/deny component match but not grade depth.
3. **Workaround ≠ Actionability** — knowing the workaround exists (ontology) doesn't mean the agent explained it actionably (rubric). These are complementary, not redundant.

## Recommendation

**Proceed with full 160-case mapping.** The ontology provides genuine external ground truth that our rubric lacks. Proposed use:
1. **Rubric calibration check** — are Diag=3 cases consistently ones where the agent identified the ontology's component and root cause?
2. **Fabrication cross-check** — do fabricated claims correlate with cases where the ontology has no matching component/workaround?
3. **Scorer calibration** — on the J6-1 type disagreements, does the ontology consistently favor one scorer's judgment?

The ontology doesn't replace the rubric — it validates it from an independent data source.

---
*Trial analysis by Owl, 2026-04-14.*
