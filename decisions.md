# Design Decisions Log

Captures WHY key design choices were made, not just WHAT. These decisions were reconstructed during the Rocky→Owl handoff (2026-04-14) and confirmed with Rocky and Peng.

---

## D1: Two LLM Scorers, No Human Ground Truth

**Decision:** Use two LLM agent scorers (Rocky, Raven) with no human scorer in the loop.

**Rationale:** Practical constraint — no human annotator was available for 160-case scoring rounds with rapid iteration (7 rubric versions in one day). LLM scorers can re-score 160 cases in minutes, enabling fast iteration.

**Risk:** κ≥0.80 between two LLMs doesn't guarantee the rubric captures what a human expert would consider "correct." The rubric could be internally consistent but calibrated to LLM judgment rather than human judgment.

**Mitigation considered:** PT2 Ontology project (Prof) may provide independently-derived ground truth for cross-validation. Third-scorer validation is a known open item.

**Status:** Accepted risk. Flagged for future validation.

---

## D2: No Held-Out Validation Set

**Decision:** All 160 cases used for both rubric iteration and final validation. No held-out set.

**Rationale:** The argument was that bright-line tests are mechanical enough to generalize — if the rule is "does the response contain an imperative verb?", that test works regardless of which cases it's applied to.

**Risk:** Classic overfitting — rubric rules may be tuned to specific disagreement patterns in the 160 cases. κ≥0.80 might not hold on new data.

**Validation path:** Score a new batch of 20+ cases without rubric changes. If κ holds, generalization is confirmed.

**Status:** Untested. Open item for Owl.

---

## D3: Keep Diag=2 Despite Empty Level

**Decision:** Preserve the 4-level Diagnosis scale (0-3) even though Diag=2 is used in 0 cases (Rocky) and 6 cases (Raven) in v2.8.

**Decided by:** Peng Wu.

**Rationale:** The scale is designed for measuring documentation improvement over time. As docs improve, agent guidance should become more precise — moving from "right topic" (Diag=1) to "right mechanism" (Diag=2) to "correct root cause" (Diag=3). Collapsing to 3 levels would lose the ability to detect this progression.

**Status:** Final. Do not collapse.

---

## D4: Quadratic Weights for Kappa

**Decision:** Use quadratic-weighted Cohen's kappa for ordinal dimensions.

**Rationale:** Quadratic weights penalize large disagreements more than small ones, which is appropriate for ordinal scales where a 2-point disagreement is qualitatively worse than a 1-point disagreement. This is the standard approach (Fleiss & Cohen, 1973).

**Note:** The iaa-validation.md skill document shows a linear-weight formula, but the actual reported kappa values were computed with quadratic weights. The compute_iaa.py script now defaults to quadratic and reports both.

**Status:** Documented. Script updated.

---

## D5: Track 2 Only for IAA Validation

**Decision:** All IAA validation rounds used Track 2 (doc-restricted) data only.

**Rationale:** Track 2 was the primary evaluation mode — it measures doc sufficiency, which is the project's core question. Track 1 (unrestricted) was run for comparison but not IAA-validated.

**Risk:** The rubric includes Track 1 scoring rules (e.g., "docs don't cover this" = Diag=1 for unrestricted agents) that have never been empirically tested. Applying the rubric to Track 1 data may produce lower κ.

**Status:** Known gap. Track 1 IAA is an open item.

---

## D6: Rocky as Scorer AND Rubric Designer

**Decision:** Rocky both designed the rubric and served as one of the two scorers.

**Rationale:** Practical constraint — Rocky had the deepest understanding of the evaluation domain and the rubric's intent. Separating design from scoring would have required a third agent with sufficient domain knowledge.

**Risk:** Each rubric iteration analyzed Rocky-vs-Raven disagreements and adjusted the rubric, typically moving Rocky's scores toward Raven's. This creates a structural bias toward agreement between these two specific scorers.

**Mitigation:** eval-lessons.md Lesson 5 warns about this. The test for each rubric change: "Would a third scorer who's never seen the data find this rule clearer?" But this test was applied by Rocky himself, not independently verified.

**Status:** Accepted risk. Third-scorer validation is an open item.

---

## D7: Mode A × Mode B Cross-Reference

**Decision:** ~~Designed conceptually but not computed.~~ Computed (2026-04-14).

**Rationale:** The cross-reference matrix (Coverage × Discoverability → Agent Quality) is described in methodology.md as the key actionable output.

**Key findings (see `analysis/cross_reference.md`):**
- **Diagnosis is doc-independent** (Spearman ρ=0.043) — agents diagnose equally well without docs
- **Actionability is doc-dependent** (Spearman ρ=0.450) — Full coverage → 0.86 mean act vs None → 0.12
- **Partial coverage is the fabrication danger zone** (5.4% fab rate vs 0% Full, 2.3% None)
- **J3 (Correctness) has 30% fabrication rate** with zero Full coverage — highest-risk journey
- **J8 (Custom Ops) has zero actionability** despite 5 Full coverage docs — doc quality, not discoverability

**Status:** ✅ Resolved.

---

## D8: Equal Journey Weighting

**Decision:** All 8 journeys weighted equally (20 cases each), despite issue volume varying from 320 (J2) to 2,053 (J4) in the source corpus.

**Rationale:** Each journey represents a distinct doc gap pattern. Volume weighting would over-index on J4 (Graph Breaks) and under-represent rare but important journeys like J2 (Performance Diagnosis) and J7 (Compile-Time Performance).

**Status:** Final.
