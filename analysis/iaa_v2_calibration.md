# V2 Multi-Dimensional Rubric: Inter-Annotator Agreement

**Date:** 2026-04-13
**Scorers:** Rocky, Raven (independent)
**Cases:** 20 (large-disagreement cases from v1, intentionally adversarial selection)

## Results Summary

| Metric             | Kappa  | Weighted κ | Exact Agree | Within-1 |
|--------------------|--------|------------|-------------|----------|
| v1 single-score    | 0.000  | -0.050     | 0%          | —        |
| **v2 Diagnosis**   | 0.027  | 0.015      | 20%         | 50%      |
| **v2 Actionability** | **0.815** | **0.897** | **95%** | **100%** |
| **v2 Fabrication** | 0.000  | n/a        | 95%         | n/a      |

## Key Findings

### 1. Actionability is solved (κ=0.897, Almost Perfect)

The Actionability dimension achieved near-perfect agreement. 19/20 cases exact match, the remaining one (J1-1) differed by only 1 point (Rocky=3, Raven=2). Both scorers consistently rated template gap-acknowledgment responses as Actionability=0, and both recognized genuinely useful guidance when present.

**This validates the core v2 design hypothesis:** separating "what the agent diagnosed" from "how useful the guidance is" resolves the conflation that broke v1.

### 2. Diagnosis still broken (κ=0.015, Slight)

The Diagnosis dimension reproduces the v1 disagreement almost exactly. The pattern:

- **Rocky:** "Agent correctly identifies docs don't cover X" → Diagnosis=3
- **Raven:** "Agent just says 'not addressed' — no real diagnosis" → Diagnosis=1

16 of 20 cases disagree on Diagnosis. In every case, Rocky scores 1-2 points higher than Raven.

**Root cause:** The rubric says `3 = Correct root cause (includes correctly identifying 'docs don't cover this')`. Rocky reads this literally — gap acknowledgment IS correct diagnosis when the gap is real. Raven reads "correct root cause" as requiring technical analysis of WHY the problem occurs, not just WHETHER docs cover it.

This is a genuine rubric ambiguity. Both interpretations are defensible.

### 3. Fabrication: 1 disagreement (J1-1)

- **Rocky:** `save_cache_artifacts()` and `load_cache_artifacts()` are real — verified in `torch._inductor.standalone_compile`
- **Raven:** These are fabricated — "do not exist in the PyTorch API"

This is a factual verification question, not a rubric issue. One scorer is right.

## Diagnosis Disagreement Analysis

All 16 disagreement cases follow the identical pattern:

| Case | Rocky | Raven | Agent Response Pattern |
|------|-------|-------|----------------------|
| J7-12 | 3 | 1 | "17-30 min compile time not addressed in docs" |
| J7-13 | 3 | 1 | "Loop compilation speed not documented" |
| J7-14 | 3 | 1 | "pick_vec_isa overhead not documented" |
| J7-19 | 3 | 1 | "FSDP mixed precision + compile not documented" |
| J8-11 | 3 | 1 | "Custom ops + compile memory access not documented" |
| J8-12 | 3 | 1 | "FlexAttention + compile errors not documented" |
| J8-13 | 3 | 1 | "Compiled CUDA graphs thread safety not documented" |
| J8-16 | 3 | 1 | "Symmetric memory + compile not documented" |
| J8-19 | 3 | 1 | "FlexAttention + Triton LLVM crash not documented" |
| J8-20 | 3 | 1 | "Compiled flex_attention wrong gradients not documented" |

Raven's rationale consistently says: "No diagnosis. Doesn't explain [specific technical mechanism]. Just says 'not addressed.'"

Rocky's rationale consistently says: "Correctly identifies that [topic] is not documented. This is an accurate characterization."

## Interpretation

The v2 rubric partially succeeded:
- **Actionability separates cleanly** — both scorers agree on what's useful
- **Diagnosis inherits the v1 ambiguity** — the disagreement moved dimensions but didn't disappear

### The real question for Peng:

**Is "docs don't cover X" a correct diagnosis?**

- **If yes (Rocky's view):** Most doc-restricted responses get Diagnosis=3, Actionability=0. This cleanly separates "the agent understands the problem" from "the agent can't help." Diagnosis becomes a measure of problem understanding.
- **If no (Raven's view):** Most doc-restricted responses get Diagnosis=1, Actionability=0. Diagnosis becomes a measure of technical depth — did the agent explain WHY the problem occurs, not just THAT docs don't cover it.

Both are valid evaluation frameworks. They answer different questions.

## Recommendations

1. **Keep Actionability as-is.** It works.
2. **Resolve Diagnosis ambiguity by fiat.** Pick one interpretation and add explicit examples to the rubric. This is a design decision, not an empirical question.
3. **Verify J1-1 fabrication.** Check whether `save_cache_artifacts()` actually exists in PyTorch source.
4. **Re-run calibration** after Diagnosis clarification to confirm κ improves.
