# Scoring Rubric v2: Multi-Dimensional Agent Guidance Quality

**Version:** 2.4
**Date:** 2026-04-13
**Replaces:** Single-score 0-3 rubric in `methodology.md` (Sections "Scoring for resolved issues" and "Scoring for unresolved issues")
**Applies to:** Mode B evaluation (full-context agent guidance), both Track 1 (unrestricted) and Track 2 (doc-restricted)

---

## Why This Rubric Exists

The v1 single-score rubric (0-3) produced near-chance inter-annotator agreement (Cohen's kappa = 0.077, n=160). The root cause, documented in `analysis/iaa_doc_restricted.md`, is that one score conflated two independent judgments:

1. **Did the agent correctly understand the problem?** Rocky scored "correctly identifies docs don't cover this" as 3 (accurate diagnosis). Raven scored the same cases as 1 (no actionable help). Both are defensible readings of the v1 rubric -- it just failed to separate these concerns.

2. **Can the user act on the guidance?** The Rocky=2 / Raven=1 block (62 of 160 cases, 38.8%) reflects disagreement on whether "mentions real tools but doesn't engage with specifics" is actionable. Again, the rubric didn't define the boundary.

3. **Is the guidance trustworthy?** Fabrication (invented APIs, flags, env vars) was handled inconsistently: Raven capped fabrication cases at 1; Rocky did not penalize fabrication if the overall answer was directionally correct. The rubric said nothing about it.

This v2 rubric separates these into three independent dimensions. Each dimension has a clear question, a tight scale, and worked examples. A scorer should be able to score any dimension without thinking about the others.

**Expected impact on IAA:** The "gap acknowledgment" pattern that caused 20 of 21 large disagreements is now unambiguous -- a correct gap acknowledgment scores Diagnosis=3, Actionability=0. No more forcing scorers to compress two judgments into one number.

---

## The Three Dimensions

### Overview

| Dimension | Question | Scale | Type |
|-----------|----------|-------|------|
| **Diagnosis** | Did the agent correctly identify the problem? | 0-3 | Ordinal |
| **Actionability** | Can the user actually solve their problem with this guidance? | 0-3 | Ordinal |
| **Fabrication** | Does the guidance contain fabricated technical claims? | Yes/No | Binary |

Score each dimension independently. A case can have Diagnosis=3 and Actionability=0 (correct diagnosis, no fix). A case can have Diagnosis=1 and Actionability=2 (wrong root cause but the suggested workaround happens to help). These are real patterns in our data.

---

## Dimension 1: Diagnosis (0-3)

**Question:** Did the agent correctly identify what is causing the user's problem?

For resolved issues, compare against the actual resolution from the GitHub issue thread. For unresolved issues, assess whether the agent's characterization of the problem is consistent with the evidence in the issue body (error messages, stack traces, code).

| Score | Label | Definition |
|-------|-------|------------|
| **3** | Correct root cause | Agent identifies the actual root cause, OR correctly identifies that this is an open/undocumented issue with no known fix. |
| **2** | Right area, imprecise | Agent identifies the correct subsystem or component but is imprecise about the mechanism, or identifies one cause when there are multiple. |
| **1** | Tangential | Agent discusses a related topic but misses the actual problem, or focuses on the wrong aspect of a multi-part issue. |
| **0** | Wrong | Agent identifies the wrong root cause, or fabricates an explanation that contradicts the evidence. |

### Diagnosis Examples

**Score 3 -- Correct root cause (resolved issue):**
> User: "torch.compile with `dynamic=True` recompiles every iteration with different sequence lengths"
> Agent: "The recompilation is caused by Dynamo creating overly tight guards on tensor shapes. Each new sequence length triggers a new guard failure. Set `torch._dynamo.config.automatic_dynamic_shapes = True` to let Dynamo widen guards automatically."
> Why 3: Correctly identifies guard behavior as the root cause. Matches the actual resolution.

**Score 3 -- Correct gap identification (unresolved issue):**
> User: "compiled autograd doesn't work with `torch.utils.checkpoint` using non-reentrant mode"
> Agent: "This appears to be an unsupported interaction -- compiled autograd does not currently handle non-reentrant checkpointing. This is tracked as an open limitation."
> Why 3: Correctly identifies that this is an open limitation. The honest "not supported yet" IS the correct diagnosis when that's the ground truth.

**Score 2 -- Right area, imprecise:**
> User: "AOTAutograd cache misses on every run despite identical inputs"
> Agent: "This is related to the compilation cache. The compile cache may not be persisting across process restarts."
> Why 2: Correctly points to caching, but conflates inductor cache with AOTAutograd cache -- different subsystems with different persistence mechanisms.

**Score 1 -- Tangential:**
> User: "torch.compile produces wrong results when model uses in-place operations on views"
> Agent: "torch.compile can sometimes be slower than eager mode. Consider using `mode='reduce-overhead'` for better performance."
> Why 1: Discusses torch.compile but addresses performance rather than the correctness issue. The user has a correctness bug, not a performance problem.

**Score 0 -- Wrong:**
> User: "Graph break on `torch.autograd.grad()` inside compiled function"
> Agent: "torch.autograd.grad is not supported under torch.compile. You need to use torch.func.grad instead."
> Why 0: torch.autograd.grad IS supported under compile (as of PyTorch 2.x). The agent fabricated an incompatibility that doesn't exist.

### Diagnosis Scoring Rules

**For RESOLVED issues (J{n}-1 through J{n}-10):**
- The ground truth is the actual fix from the GitHub issue. A diagnosis is "correct" if it identifies the root cause that the fix addresses.
- If the agent identifies a real contributing factor that isn't the primary root cause, score 2.
- If the agent says "this might be a bug" and it IS a bug, that's score 3 (correct characterization), not 2.

**For UNRESOLVED issues (J{n}-11 through J{n}-20):**
- There is no confirmed fix, so diagnosis is assessed against the evidence in the issue.
- Correctly identifying that this is an open/unsupported/undocumented issue = score 3. This was the core IAA disagreement in v1, and this rubric resolves it: the diagnosis is correct; actionability is scored separately.
- Speculating about a plausible root cause that is consistent with the error = score 2.
- Confidently naming a wrong cause = score 0.

### CRITICAL: Track-Aware Diagnosis Scoring

Diagnosis scoring MUST account for the agent's access constraints. What counts as "correct diagnosis" depends on what the agent was allowed to use.

**Track 2 (doc-restricted):** The agent can ONLY use official pytorch.org documentation. If the docs genuinely don't cover the user's problem, then "this is not covered in official documentation" IS a correct diagnosis (score 3) — it is the most accurate statement the agent can make within its constraints. Do NOT score this as Diagnosis=1 on the grounds that the agent "didn't explain the technical mechanism." The agent had no access to source code, GitHub issues, or forums where that mechanism might be described.

**Track 1 (unrestricted):** The agent has full access to web, GitHub, forums, source code. In this context, "docs don't cover this" is NOT sufficient for Diagnosis=3 — the agent had other sources and should have investigated further. Score 1-2 depending on how much the agent engaged with the problem.

| Agent response | Track 2 (doc-restricted) | Track 1 (unrestricted) |
|---------------|--------------------------|----------------------|
| "Not covered in official docs" (accurate) | Diagnosis=3 | Diagnosis=1 |
| "Not covered in docs" + explains WHY from source code | n/a (can't access source) | Diagnosis=3 |
| "Not covered in docs" + links to GitHub issue | n/a (can't access GitHub) | Diagnosis=2-3 |

**Why this matters:** v2 calibration round 1 produced Diagnosis κ=0.015 because one scorer (Raven) applied Track 1 standards to Track 2 data. All 16 disagreement cases followed this pattern: Rocky scored Diagnosis=3 (accurate gap identification under doc constraint), Raven scored Diagnosis=1 (no technical analysis). Both readings were defensible under the old rubric text — this section removes the ambiguity.

**IMPORTANT: Track-aware scoring applies to UNRESOLVED issues only.** For resolved issues, Diagnosis is always scored against the actual fix, regardless of track. If a resolved issue has a known root cause and the agent says "not documented" instead of identifying that root cause, score Diagnosis=1 (tangential), not 3 — even in Track 2. The agent may be constrained, but the ground truth still exists and the diagnosis is still wrong.

---

## Dimension 2: Actionability (0-3)

**Question:** Can the user take the agent's guidance and solve (or meaningfully progress on) their problem?

This dimension measures practical value to the user, regardless of whether the diagnosis is correct. Score based on what the user can DO with the response.

| Score | Label | Definition |
|-------|-------|------------|
| **3** | Complete solution | The user can directly apply the guidance to fix their problem. Includes code changes, config settings, or workarounds that resolve the issue. |
| **2** | Partial solution | The guidance gets the user materially closer but requires additional steps the agent didn't provide. The user knows what to do next, just not the full path. |
| **1** | Generic advice | The advice is real but not specific to this problem. Could apply to any torch.compile issue. ("Try setting TORCH_LOGS=dynamo", "Check for graph breaks") |
| **0** | No actionable guidance | The user cannot do anything concrete with this response. Includes: mere gap acknowledgment, pure diagnosis with no suggested actions, or "not documented" with nothing further. |

### Actionability Examples

**Score 3 -- Complete solution:**
> User: "How do I persist the compile cache across restarts?"
> Agent: "Set `TORCHINDUCTOR_FX_GRAPH_CACHE=1` and optionally `TORCHINDUCTOR_CACHE_DIR=/path/to/cache` to persist compiled graphs across process restarts."
> Why 3: User can set these env vars and immediately get persistent caching. Directly solves the stated problem.

**Score 2 -- Partial solution:**
> User: "torch.compile is 10x slower than eager on my transformer model"
> Agent: "The slowdown is likely from excessive recompilation due to dynamic shapes. You can diagnose with `TORCH_LOGS=recompiles` and then mark specific dimensions as dynamic using `torch.compile(dynamic=True)` or `torch._dynamo.mark_dynamic()`."
> Why 2: Gives real diagnostic tools and a real approach, but doesn't walk through interpreting the recompile log output or show exactly how to mark the right dimensions. User has to figure out the last mile.

**Score 1 -- Generic advice:**
> User: "Custom op with torch.library breaks under fullgraph=True"
> Agent: "When encountering issues with torch.compile, try using `TORCH_LOGS=dynamo` to see what Dynamo is doing. Also check if there are graph breaks using `torch._dynamo.explain(model, input)`."
> Why 1: These are real tools, but "enable logging and check for graph breaks" could be the response to any torch.compile question. No specific guidance about custom op registration with torch.library.

**Score 0 -- No actionable guidance:**
> User: "How do I compile a model using flex_attention with custom masking?"
> Agent: "This specific use case does not appear to be covered in the official PyTorch documentation."
> Why 0: The user has nothing to do with this information. Even if the diagnosis is correct (Diagnosis=3: docs don't cover it), the user still has no path forward. Also score 0 for responses that only restate the problem without suggesting any action.

### Actionability Scoring Rules

**For RESOLVED issues:**
- Score 3 requires a concrete fix the user can apply. "You need to upgrade to PyTorch 2.2+" counts as 3 if that's actually the fix. "You should file a bug" does NOT count as 3 -- that's not a solution, it's a redirect.
- Score 2 requires that the user is materially closer to solving the problem after reading the guidance, even if they need additional steps.
- If the guidance contains the correct fix buried in irrelevant advice, score based on the fix's quality, not the noise around it.

**For UNRESOLVED issues:**
- Score 3 requires a viable workaround the user can apply NOW, even if it's not a full fix. Example: "This is an open bug with `compile + DDP`. Workaround: wrap the DDP module after compilation rather than before." That's actionable even without an upstream fix.
- Score 2: Suggests useful debugging steps or points the user to the right issue tracker / PR. The user knows where to look next.
- Score 1: Generic debugging advice not tailored to this specific problem.
- Score 0: "This is not documented" or "this may be a bug" with nothing further. The gap acknowledgment has zero actionable value, regardless of how accurate the diagnosis is.

### CRITICAL: Template Response Rule for Actionability

When the agent's response follows a generic template pattern — "docs don't cover X" followed by listing general doc topics that appear identically across many unresolved responses — score Actionability=0. This applies regardless of whether the template mentions real APIs or tutorials by name.

**The test:** Would this exact Actionability section appear nearly verbatim in the agent's response to a *different* unresolved issue? If yes → Act=0 (template, not case-specific).

**Score Act≥1 only when the agent provides case-specific guidance:**
- A workaround or debugging step specific to THIS problem (not generic "enable logging")
- A pointer to a specific GitHub issue, PR, or known upstream fix
- A concrete API call or config change tailored to the user's error

**Why this rule exists:** v2.2 full 160-case scoring showed Actionability κ collapsed from 0.897 (calibration) to 0.027. Root cause: 90% of unresolved doc-restricted responses use the same template ("docs don't cover X, here's what docs DO cover: [general topics]"). One scorer gave credit for mentioning general topics (Act=1-2), the other did not (Act=0). Template responses add no case-specific value and should not receive Actionability credit.

### Diagnosis: Track 2 Unresolved Gap Identification

For Track 2 (doc-restricted) unresolved cases, if the agent accurately identifies the specific documentation gap — naming what topic or API is not covered — score Diagnosis=3. Only score Diagnosis=2 if the agent mischaracterizes WHICH aspect is missing. Vague but accurate ("this specific issue is not addressed") still qualifies as Diag=3 when the gap identification is factually correct.

### Diagnosis: Right Subsystem = Diag 2, Not 1

For resolved cases where the agent identifies the correct subsystem or interaction (e.g., "AMP + compile", "C++ compiler requirement") but is vague on the mechanism, score Diagnosis=2 (right area). Reserve Diagnosis=1 for cases where the agent discusses the wrong subsystem entirely (e.g., discusses performance when the issue is correctness).

### Actionability: Same Generic Workaround Across Cases = Act 1

When the same workaround appears verbatim across multiple cases of the same type (e.g., "use `torch.compiler.disable()` to skip unsupported code" for every graph-break case), score Act=1 (generic advice) not Act=2 (partial solution). Act=2 requires guidance tailored to the specific case's circumstances.

### Actionability: Problem Characterization Without Steps = Act 0

For unresolved cases where the agent characterizes the limitation ("this appears to be an undocumented limitation where X conflicts with Y") but provides no next steps (no workaround, no issue link, no debugging command), score Act=0. Characterizing a problem is not the same as giving actionable guidance — that value is captured in the Diagnosis dimension.

### The Gap Acknowledgment Pattern (Key Disambiguation)

This is the pattern that caused 20 of 21 large disagreements in v1 (see `analysis/iaa_doc_restricted.md`, Section 7). In v2, it scores as:

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Diagnosis | **3** | Correctly identifying "docs don't cover this" is an accurate diagnosis. The agent found the right answer. |
| Actionability | **0** | The user has nothing actionable. "Not documented" gives them no path forward. |
| Fabrication | **No** | No fabricated claims. |

If the agent acknowledges the gap AND provides a workaround or points to the relevant GitHub issue:

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Diagnosis | **3** | Same -- correct identification of the gap. |
| Actionability | **2** | The workaround or issue link gives the user a next step. |
| Fabrication | **No** | (Assuming the workaround is real.) |

This decomposition eliminates the ambiguity. Rocky's "the agent got it right" and Raven's "the user got no help" are both captured -- just on different axes.

---

## Dimension 3: Fabrication (Binary)

**Question:** Does the guidance contain any fabricated APIs, config flags, environment variables, or other technical claims that do not exist in PyTorch?

| Label | Definition |
|-------|------------|
| **Yes** | The guidance references at least one API, config option, env var, function, or method that does not exist in the version of PyTorch under evaluation. |
| **No** | All technical claims in the guidance reference real, verifiable PyTorch functionality. |

### What Counts as Fabrication

**Fabricated (mark Yes):**
- Invented config flags: `torch._inductor.config.skip_guard_on_globals_unsafe` (doesn't exist)
- Invented env vars: `TORCHINDUCTOR_COMPILE_BISECTOR` (doesn't exist)
- Invented API methods: `torch._dynamo.utils.compile_profiler.reset()` (doesn't exist)
- Invented function signatures: `torch.compile(skip_warmup=True)` (no such parameter)
- Invented modules: `from torch._dynamo.utils import compile_profiler` (no such module)

**NOT fabrication (mark No):**
- Real API used in wrong context (semantic error, not fabrication)
- Correct API name with slightly wrong explanation of behavior
- Deprecated but once-real API (note it in rationale, but don't flag as fabrication)
- General-knowledge claims like "graph breaks reduce performance" (not a verifiable technical claim)
- Hedged suggestions: "if such a config exists" (the agent explicitly disclaims certainty)

### Fabrication and the Automated Detector

The automated fabrication detector (`scripts/verify_claims.py`) catches fabricated names with zero false positives (validated on 160 cases, `analysis/iaa_doc_restricted.md`). The manual fabrication flag in this rubric serves as a cross-check and catches cases the automated detector misses (e.g., fabricated parameter names in function calls, invented module paths outside the 10 regex categories).

**Scoring workflow:**
1. Score Fabrication manually during annotation.
2. Run `verify_claims.py` on the same responses.
3. Any discrepancy (manual=No but detector=Yes, or vice versa) must be resolved by checking PyTorch source. The detector's verified result takes precedence for name-based fabrication; the manual flag takes precedence for types the detector cannot catch.

### Fabrication and Overall Scoring

Fabrication does NOT override Diagnosis or Actionability scores. A response can have:
- Diagnosis=3, Actionability=3, Fabrication=Yes -- the overall answer is correct and actionable but includes a fabricated claim alongside real guidance.
- Diagnosis=0, Actionability=0, Fabrication=No -- the agent is wrong and unhelpful, but didn't invent anything.

Fabrication is recorded as a separate flag. Downstream analysis can apply penalties (e.g., "cap effective score at 1 if Fabrication=Yes") but that is an analysis decision, not a scoring decision. Scorers report what they see; they do not apply caps.

**Rationale:** In v1, Raven applied an implicit fabrication cap (J1-1: capped at 1 due to invented API names) while Rocky did not. Making fabrication a separate dimension eliminates this source of disagreement.

---

## Scoring Process

For each test case:

1. **Read** the user's question and the agent's response.
2. **Score Diagnosis (0-3):** Does the agent identify the right problem? Compare against ground truth (resolved) or issue evidence (unresolved).
3. **Score Actionability (0-3):** Can the user do something concrete with this guidance? Evaluate the practical steps provided.
4. **Score Fabrication (Yes/No):** Does the response contain any invented technical claims? When in doubt, search PyTorch source.
5. **Record** all three scores plus a one-sentence rationale for each.

Do NOT let one dimension influence another. Score each independently. If you find yourself thinking "but the diagnosis was wrong so the actionability doesn't count" -- stop. A wrong diagnosis with a helpful workaround is Diagnosis=0, Actionability=2. Score what you see on each axis.

---

## Edge Cases and Disambiguation

### Edge Case 1: Correct diagnosis but fabricated fix

> Agent correctly identifies that recompilation is caused by changing tensor shapes, then recommends `torch._dynamo.config.suppress_recompile = True` (doesn't exist).

- Diagnosis: **3** (correct root cause)
- Actionability: **0** (the recommended fix doesn't exist, so user can't apply it)
- Fabrication: **Yes**

### Edge Case 2: Wrong diagnosis but accidentally useful advice

> Agent says the error is caused by an unsupported op (wrong), but recommends `torch.compiler.disable()` on the offending function, which happens to fix it.

- Diagnosis: **0** (wrong root cause)
- Actionability: **3** (the user can apply `torch.compiler.disable()` and it works)
- Fabrication: **No** (`torch.compiler.disable` is real)

### Edge Case 3: Agent says "file a bug"

> Agent correctly diagnoses an open issue and says "you should file a bug report on pytorch/pytorch."

- Diagnosis: **3** if the issue is indeed a bug, **2** if the root cause identification is vague
- Actionability: **1** -- "file a bug" is advice, but it's generic and doesn't help the user solve their immediate problem. Score 2 if the agent also links to the specific existing issue (gives the user a concrete tracking point).

### Edge Case 4: Multiple solutions offered, one is fabricated

> Agent suggests three approaches. Two are real and helpful. One references a fabricated config.

- Diagnosis: Score based on the overall diagnostic accuracy (likely 2 or 3 if the real solutions reflect correct understanding).
- Actionability: Score based on the real solutions only (likely 2 or 3).
- Fabrication: **Yes** -- any fabrication triggers the flag regardless of other content.

### Edge Case 5: Cookie-cutter template response

> Agent gives a boilerplate response: "torch.compile may have issues with this pattern. Try `TORCH_LOGS=dynamo` to investigate, check for graph breaks, consider using `torch._dynamo.explain()`."

- Diagnosis: **1** (tangential -- doesn't engage with the specific problem)
- Actionability: **1** (generic debugging advice, not tailored)
- Fabrication: **No** (all tools mentioned are real)

This was the bulk of the Rocky=2 / Raven=1 disagreement block (62 cases). In v2, it scores consistently: generic on both axes.

### Edge Case 6: Unresolved issue with a real workaround

> Agent: "This is a known limitation of compiled autograd with checkpointing. Until it's fixed upstream, you can work around it by disabling compile on the checkpoint wrapper: `torch.compiler.disable(torch.utils.checkpoint.checkpoint)`."

- Diagnosis: **3** (correctly identifies known limitation)
- Actionability: **3** (concrete workaround the user can apply now)
- Fabrication: **No** (assuming the disable pattern is valid)

### Edge Case 7: Doc-restricted agent with no docs available

> In Track 2 (doc-restricted), the agent searches pytorch.org, finds nothing, and says: "The official PyTorch documentation does not appear to cover this use case."

- Diagnosis: **3** (this is factually correct -- the docs don't cover it)
- Actionability: **0** (nothing the user can do with this)
- Fabrication: **No**

This is the cleanest decomposition of the "gap acknowledgment" pattern. The agent performed correctly given its constraint (doc-restricted), and the actionability score reflects the user's reality.

---

## Resolved vs. Unresolved Scoring Summary

### Resolved Issues (J{n}-1 through J{n}-10)

Ground truth is the actual fix from the GitHub issue thread.

| Diagnosis Score | Resolved Meaning |
|----------------|------------------|
| 3 | Agent identifies the same root cause as the actual fix |
| 2 | Agent identifies the right subsystem but wrong mechanism or incomplete cause |
| 1 | Agent discusses a related topic, misses the actual problem |
| 0 | Agent's root cause is wrong or contradicted by the actual fix |

| Actionability Score | Resolved Meaning |
|--------------------|------------------|
| 3 | Agent provides the actual fix or an equally effective alternative |
| 2 | Agent provides partial fix or gets user significantly closer |
| 1 | Generic advice that any torch.compile user would get |
| 0 | No concrete steps, or steps that wouldn't help |

### Unresolved Issues (J{n}-11 through J{n}-20)

No confirmed fix exists. Assess against issue evidence and honest uncertainty.

| Diagnosis Score | Unresolved Meaning |
|----------------|-------------------|
| 3 | Agent correctly characterizes the issue (including "this is unsupported/open/a bug") |
| 2 | Agent identifies the right area but speculates beyond the evidence |
| 1 | Agent addresses a tangentially related problem |
| 0 | Agent fabricates a root cause that contradicts the evidence |

| Actionability Score | Unresolved Meaning |
|--------------------|-------------------|
| 3 | Agent provides a viable workaround the user can apply now |
| 2 | Agent provides useful next steps (specific debugging, links to tracking issue/PR) |
| 1 | Generic advice: "enable logging," "file a bug," "check docs" |
| 0 | No actionable guidance at all |

---

## Recording Format

For each case, record:

```
Case: J{journey}-{number}
Resolution: resolved | unresolved
Diagnosis: 0 | 1 | 2 | 3
Diagnosis rationale: <one sentence>
Actionability: 0 | 1 | 2 | 3
Actionability rationale: <one sentence>
Fabrication: yes | no
Fabrication detail: <if yes, list the specific fabricated claim(s)>
```

Example:

```
Case: J7-15
Resolution: unresolved
Diagnosis: 3
Diagnosis rationale: Correctly identifies that compilation time profiling is not covered in official docs.
Actionability: 0
Actionability rationale: Response only states the gap exists; no workaround or debugging approach suggested.
Fabrication: no
Fabrication detail: n/a
```

---

## Relationship to v1 Rubric and Proposed 0-4 Scale

This rubric **replaces** the single-score 0-3 rubric (v1) and **supersedes** the proposed 0-4 scale in `methodology.md` (Section "Refined Scoring Rubric").

The 0-4 proposal attempted to fix the score-2 cluster (72.5% of cases) by adding granularity within a single dimension. This multi-dimensional approach is better because:

1. The score-2 cluster conflates cases that differ on **independent axes** (good diagnosis + generic advice vs. vague diagnosis + useful workaround). A finer single scale still forces scorers to weigh these against each other.
2. The gap-acknowledgment disagreement (20/21 large disagreements) cannot be resolved by adding scale points -- it requires separating "is the answer correct?" from "is the answer useful?"
3. Binary fabrication is cleaner than embedding it as a score cap. Scorers report facts; analysis applies policy.

**Migration path:** Existing v1 scores can be approximately mapped to v2 for trend analysis, but should not be treated as equivalent. Re-scoring a calibration subset (e.g., the 21 large-disagreement cases) under v2 is recommended before full re-scoring.

---

## Calibration Protocol

Before scoring the full 160-case dataset:

1. Both scorers independently score a calibration set of 20 cases (select from the 21 large-disagreement cases in `analysis/iaa_doc_restricted.md`, Section 7, plus a few consensus cases as sanity checks).
2. Compare scores dimension by dimension. Target: kappa >= 0.60 on each dimension independently.
3. Discuss any disagreements. Amend this rubric with additional examples if a recurring ambiguity is found.
4. Only proceed to full scoring after calibration passes.

---

*Rubric v2.0 -- 2026-04-13. Motivated by IAA analysis showing kappa=0.077 on single-score rubric (see `analysis/iaa_doc_restricted.md`). Splits into Diagnosis, Actionability, and Fabrication to eliminate the gap-acknowledgment ambiguity and the fabrication-penalty inconsistency.*

*Rubric v2.1 -- 2026-04-13. Added track-aware Diagnosis scoring rules after calibration round 1 showed Diagnosis κ=0.015. Root cause: Raven applied unrestricted standards to doc-restricted data. Also corrected save_cache_artifacts/load_cache_artifacts fabrication example (they are real APIs in torch.compiler). See `analysis/iaa_v2_calibration.md`.*

*Rubric v2.2 -- 2026-04-13. Clarified that track-aware scoring (gap ID = Diag 3) applies to unresolved issues only. For resolved issues, always score against the actual fix regardless of track. Resolves J5-10 disagreement from v2.1 calibration. Rubric validated: within-1 agreement 95%, systematic bias eliminated. Ready for full 160-case deployment.*

*Rubric v2.3 -- 2026-04-14. Added Template Response Rule for Actionability. Full 160-case scoring revealed κ=0.027 on Actionability (down from 0.897 on calibration). Root cause: 90% of unresolved doc-restricted responses use generic template ("docs don't cover X + general topics"). Rocky scored Act=1-2 (relevant background), Raven scored Act=0 (no actionable guidance). Raven's interpretation is correct — template responses that appear identically across cases add no case-specific value. New rule: template = Act=0; only case-specific workarounds/pointers get credit.*

*Rubric v2.4 -- 2026-04-14. Tightened four scoring boundaries after analyzing all remaining disagreement clusters. (1) Track 2 unresolved gap ID always = Diag 3 if factually accurate. (2) Right subsystem = Diag 2, wrong subsystem = Diag 1. (3) Same generic workaround across cases = Act 1, not 2. (4) Problem characterization without steps = Act 0. Result: Diagnosis κ=0.868 (Almost Perfect), Actionability κ=0.825 (Almost Perfect). Both above 0.80 threshold. Rubric validated.*
