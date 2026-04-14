# Skill: Evaluation Lessons Learned

Hard-won lessons from building and validating the torch.compile doc eval rubric. These are the things that cost us time to discover — a new agent inheriting this project should internalize them before touching the rubric.

## Lesson 1: Scoring Is Reading, Not Pattern Matching

**What happened:** Rocky scored 160 cases by programmatically matching keywords in agent responses. This inflated kappa to 0.825 by overfitting Rocky's scores to match Raven's. When re-scored properly (LLM reading each response), real kappa was 0.466.

**Principle:** Judgment tasks require reading. Every case must be evaluated by reading the full response and applying the rubric criteria. There are no shortcuts. 160 cases takes minutes, not hours — the cost of proper scoring is low.

## Lesson 2: Generic ≠ Case-Specific

**What happened:** Rocky counted generic causal truths ("graph breaks cause performance loss") as Diagnosis=2 (case-specific reasoning). Raven required the causal chain to reference the user's specific problem. They agreed on Diag=2 once in 160 cases.

**Principle:** Apply the interchangeability test. If the same statement would make sense as a response to a different user's question, it's generic (lower score). Case-specific means it references something unique to THIS user's model, error, config, or use case.

## Lesson 3: Templates Are Not Actionable

**What happened:** Actionability κ was 0.027 because 90% of unresolved doc-restricted responses use the same template ("docs don't cover X, here's what docs DO cover"). One scorer gave credit for mentioning general topics (Act=1-2), the other didn't (Act=0).

**Principle:** Template responses that appear verbatim across cases add zero case-specific value. Score Act=0 regardless of content. The template rule overrides all other Actionability rules, including the imperative verb test.

**How to detect templates:** Compare 3+ responses within the same journal. If the actionable advice section is word-for-word identical across different problems, it's a template.

## Lesson 4: Both Scorers, Same Version, Always

**What happened:** Rocky scored with v2.5 while Raven scored with v2.2. Kappa was meaningless because the rules had changed between versions. Only after both re-scored with v2.5 did we get a valid comparison.

**Principle:** IAA validation requires both scorers on the same rubric version. Intermediate comparisons (one scorer updated, one not) are useful for development, but never cite as final kappa.

## Lesson 5: Rubric Iteration ≠ Overfitting

**What happened:** Each disagreement analysis led to rubric changes that moved Rocky's scores toward Raven's. This looked like improvement but was actually circular — Rocky was adjusting to match Raven, not to match ground truth.

**Principle:** Rubric changes must fix genuine ambiguity, not engineer agreement. The test: does the new rule make the rubric clearer for a THIRD scorer who's never seen the data? If yes, it's a real fix. If it only makes sense in the context of specific disagreement cases, it's overfitting.

## Lesson 6: Track Context Changes Everything

**What happened:** Diagnosis κ was 0.015 in early calibration because Raven applied unrestricted standards ("the agent should have investigated further") to doc-restricted data (the agent CAN'T investigate further — it only has docs).

**Principle:** What counts as "correct diagnosis" depends on what the agent was allowed to use. A doc-restricted agent saying "docs don't cover this" is Diag=3 (correct given constraints). An unrestricted agent saying the same thing is Diag=1 (lazy). The rubric must explicitly define track-aware scoring.

## Lesson 7: Gap Identification IS Diagnosis

**What happened:** For unresolved issues in doc-restricted mode, the agent correctly identifying "this is not covered in docs" is the most accurate diagnosis possible. Rocky initially downgraded these to Diag=2 by over-applying the causal assertion rule, when the gap-ID rule should have taken precedence (Diag=3).

**Principle:** Priority rules must be explicit. When gap-ID and causal-chain rules conflict, gap-ID wins for unresolved Track 2 cases. The gap identification IS the correct diagnosis.

## Lesson 8: Audit Boundaries Before Testing

**What happened:** We went through 5 rounds of score-analyze-fix before proactively auditing all boundaries. The audit found issues (template vs imperative conflict, fuzzy "materially closer") that could have been caught upfront.

**Principle:** Before deploying a rubric for scoring, audit every boundary for: bright-line test existence, subjective terms, edge case coverage, inter-rule conflicts. Fix FUZZY boundaries before the first scoring round. It's cheaper to think than to re-score.

## Lesson 9: Re-Scoring Is Cheap — Just Do It

**What happened:** Rocky kept asking Peng for permission to send the updated rubric to Raven for re-scoring. This added unnecessary round-trips when the cost of re-scoring 160 cases is a few minutes.

**Principle:** After any rubric change, immediately send the updated version to all scorers for re-scoring. Don't ask, don't wait, don't checkpoint. The cost is low and the information value is high.

## Lesson 10: Kappa Without Granularity Is Meaningless

**What happened:** We could achieve κ=0.825 by collapsing Diagnosis to binary (topic-mention vs correct-ID). But this would lose the ability to detect improvement as documentation gets better.

**Principle:** Kappa measures agreement, not usefulness. A binary scale with κ=0.90 that can't distinguish "good" from "great" is worse than a 4-level scale with κ=0.80 that can track improvement over time. Optimize for measurement sensitivity within the constraint of reproducibility (κ≥0.80).
