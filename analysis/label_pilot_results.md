# Label-Based Scoring Pilot — Results

**Date:** 2026-04-14
**Cases:** 20 (Track 1, 10 prior disagreements + 10 agreements)
**Scorer 1:** Owl | **Scorer 2:** Raven

## Headline Result

| Method | Act κ_w (same 20 cases) | Improvement |
|--------|------------------------|-------------|
| v2.8 direct scoring | 0.429 | — |
| Label-derived scoring | 0.769 | +0.341 |

**The label approach nearly doubled reliability on this sample.**

## Per-Label Agreement

| Label | Owl (true) | Raven (true) | Agreement | κ |
|-------|-----------|-------------|-----------|---|
| standalone_fix | 6/20 | 9/20 | 17/20 (85%) | 0.687 |
| has_imperative | 20/20 | 20/20 | 20/20 (100%) | 1.000 |
| case_specific | 19/20 | 19/20 | 20/20 (100%) | 1.000 |
| is_template | 1/20 | 0/20 | 19/20 (95%) | 0.000* |

*is_template κ=0.000 due to near-zero prevalence (only 1 case flagged by one scorer). This is a statistical artifact, not a reliability problem.

## Key Findings

### 1. The formula resolved 7/10 prior disagreements
Of the 10 cases selected for prior Act disagreements, 7 now agree under the label approach. The formula handles priority automatically — no scorer judgment needed.

### 2. `standalone_fix` is the only discriminating label on Track 1
Raven's observation is correct: has_imperative=true for all 20, case_specific=true for 19/20, is_template=false for 19/20. The formula effectively collapses to:
- standalone_fix=true → Act=3
- standalone_fix=false → Act=2
- (edge case: not case_specific and not template → Act=1)

### 3. Three `standalone_fix` disagreements remain
| Case | Owl | Raven | Owl's reasoning | Raven's reasoning |
|------|-----|-------|-----------------|-------------------|
| J1-6 | false | true | Multiple version-dependent approaches | "Exact ordering fix: parallelize first, compile second" |
| J4-18 | false | true | Known limitation, workarounds only | "Clear fix: don't compile code needing double backward" |
| J8-9 | false | true | General version upgrade, no specific fix | "Primary fix: upgrade to 2.2+" |

**Pattern:** Raven considers "upgrade to version X" or "don't use feature Y" as standalone fixes. Owl considers these as workarounds, not fixes. This is a definitional disagreement that needs a calibration decision.

### 4. New disagreements created: 0 large (|Δ|≥2), 3 small (|Δ|=1)
The label approach created 3 new Δ1 disagreements (J1-6, J4-18, J8-9) — all from the standalone_fix boundary. But it eliminated 7 prior disagreements. Net: 7 resolved, 3 created = 4 fewer disagreements.

## Formula Effectiveness on Track 1

The 4-label formula collapses to effectively 1 label (standalone_fix) on Track 1 because Track 1 guidance is always imperative and case-specific. This is not a design flaw — it means the formula correctly identifies that the ONLY meaningful distinction on Track 1 is whether the guidance provides a standalone fix.

On Track 2 (doc-restricted), we'd expect more variance in has_imperative and case_specific because doc-restricted responses may be more generic.

## Recommendation

1. **Adopt label-based scoring for Act** — the evidence is strong (κ: 0.429 → 0.769)
2. **Calibrate standalone_fix boundary** — one calibration session on "is version upgrade a standalone fix?" resolves the remaining 3 disagreements
3. **Run on Track 2 sample** to validate label variance on doc-restricted cases
4. **Consider simplifying to 2 labels** for Track 1: standalone_fix + case_specific (since has_imperative and is_template add no information)
