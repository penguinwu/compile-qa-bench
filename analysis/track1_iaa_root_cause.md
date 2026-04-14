# Track 1 IAA — Root Cause Analysis

**Date:** 2026-04-14
**Context:** Track 1 IAA shows Diag κ=0.415, Act κ=0.486, Fab κ=0.000. All below the 0.80 target.

## Three Distinct Root Causes

### Root Cause 1: Fabrication — Raven didn't check (not a rubric problem)

**Finding:** The automated detector flagged 21 cases. Owl flagged 24 (20 true positives, 4 false positives). Raven flagged 0. Ground truth: 28 cases have fabrication (17.5%).

**Diagnosis:** Raven simply skipped fabrication checking on Track 1. This is not a rubric ambiguity — the definition is clear. It's an operational failure: Raven likely optimized for speed on 160 cases and skipped the verification step.

**Fix:** Re-run Raven's Track 1 scoring with explicit fabrication checking enabled. Or: use the automated detector as the fabrication scorer (it has zero false positives on Track 2) and only use manual scoring for the ordinal dimensions.

**Impact on κ:** Fabrication κ should jump from 0.000 to ~0.80+ once Raven actually checks.

### Root Cause 2: Actionability — The interchangeability test conflicts with "standalone fix" on Track 1

**Finding:** 8 large disagreements (all Owl=1, Raven=3), concentrated in J6 (Dynamic Shapes). The pattern:

1. Agent gives `mark_dynamic(tensor, dim)` or `dynamic=True` as a fix
2. Raven scores Act=3: "standalone fix, user can apply immediately"
3. Owl scores Act=1: "same advice appears in J6-1, J6-4, J6-5, J6-6, J6-7 — interchangeable"

**The rubric contradiction:** v2.8 says the Act=3 "standalone fix" test takes priority over interchangeability. But the interchangeability test exists precisely because generic advice shouldn't get credit. When a response IS a correct standalone fix AND the same fix applies to many similar cases, the two tests conflict.

**On Track 2 this never surfaced** because doc-restricted responses rarely provide standalone fixes — most are gap acknowledgments (Act=0) or partial guidance (Act=1-2). Track 1 responses are more actionable, so the conflict appears.

**Owl's reasoning is valid:** If 5 out of 20 J6 cases get the exact same `mark_dynamic` response, the agent isn't demonstrating case-specific understanding — it's pattern-matching "dynamic shape problem → mark_dynamic." Each response is technically a standalone fix, but the agent's approach is template-level.

**Raven's reasoning is also valid:** Per v2.8 §"Interchangeability Scope," the interchangeability test "applies at the 1/2 boundary only" and "does NOT cap Act=3." A correct fix is a correct fix regardless of whether other users get the same answer.

**Fix:** The rubric needs a Track 1 clarification. Two options:

**Option A (Raven's reading):** A correct standalone fix = Act=3, always. Accept that the interchangeability test doesn't apply to Act=3. This means generic-but-correct advice gets full credit.

**Option B (Owl's reading):** Add a Track 1-specific rule: "If the same fix appears verbatim across 3+ cases in a journey, score Act=2 for each occurrence after the first, regardless of whether it's a standalone fix. The agent should demonstrate it understood WHY mark_dynamic is the right fix for THIS case, not just that it IS the right fix."

**My recommendation:** Option A with an annotation. The user gets the same value regardless of whether other users got the same advice. But annotate cases where the same fix appears across 3+ cases, so downstream analysis can assess agent pattern-matching separately from user value.

### Root Cause 3: Diagnosis — Owl applies a stricter "precision threshold" than Raven

**Finding:** 45 cases where Owl=2, Raven=3. Spread across all journeys (not concentrated). Pattern from rationale analysis:

- Owl requires the agent to "name the specific mechanism" (e.g., "guard specialization on sequence_length dimension")
- Raven credits "correct subsystem + correct outcome" (e.g., "identifies FX Graph Cache as the fix")
- Both interpretations are defensible under v2.8's "Precision Threshold" rule

**The rule says:** "Diag=3 requires naming the specific mechanism the fix addresses. Diag=2: names the correct subsystem but not the specific mechanism."

**The ambiguity:** "Specific mechanism" is subjective on Track 1 where responses draw from rich sources. On Track 2, responses are formulaic — either they name the mechanism or they don't. On Track 1, there's a spectrum: "FX Graph Cache env var" → "Inductor caching system" → "Compilation caching." Where does "subsystem" end and "mechanism" begin?

**Fix:** Add examples specific to Track 1 responses. The Track 2 calibration produced worked examples at each boundary — the same is needed for Track 1. Propose 5 Track 1 examples spanning the 2/3 boundary, have both scorers apply them, and iterate until agreement.

## Corrected IAA Estimate

If we fix Root Cause 1 (Raven re-checks fabrication) and Root Cause 2 (adopt Option A — standalone fix = Act=3):

- **Fabrication:** κ should rise to ~0.80+ (both scorers now checking)
- **Actionability:** Correcting the 8 J6 cases from Owl=1 to Owl=3 (accepting Raven's reading):
  - Current within-1: 152/160 (95.0%)
  - Corrected: all 8 large disagreements eliminated, ~158/160 within-1
  - κ increase: rough estimate 0.486 → ~0.65-0.70
- **Diagnosis:** No quick fix. Needs calibration examples at the 2/3 boundary.

Even with Roots 1 and 2 fixed, Track 1 IAA will likely be in the 0.65-0.75 range — lower than Track 2. This is expected: richer responses create more scoring ambiguity.

## Recommended Next Steps

1. **Adopt Option A for Act 2/3 boundary** — accept that standalone fixes = Act=3 regardless of interchangeability
2. **Re-score Owl's 8 large-disagreement cases** with the clarified rule
3. **Use automated detector for fabrication** instead of manual scoring on Track 1
4. **Create 5 Track 1 worked examples** for the Diag 2/3 boundary
5. **Run one calibration round** on 20 Track 1 disagreement cases with the new examples
6. **Re-score all 160 Track 1 cases** with both scorers using the calibrated rubric

---
*Analysis by Owl, 2026-04-14.*
