# Scoring Rubric v3: Label-Based Multi-Dimensional Agent Guidance Quality

**Version:** 3.0
**Date:** 2026-04-14
**Replaces:** Rubric v2.9 (`rubric_v2_multidimensional.md`)
**Applies to:** Mode B evaluation (full-context agent guidance), both Track 1 (unrestricted) and Track 2 (doc-restricted)

---

## What Changed in v3.0

v2.9 achieved high inter-rater reliability on calibration sets but failed on full scoring (Track 1: Diag κ=0.415, Act κ=0.486). Analysis of the 8 largest disagreements revealed they were **synthesis problems** — scorers agreed on observable features but combined them differently into ordinal scores. Eight rubric iterations (v2.0–v2.8) with sharper boundaries, more examples, and bright-line tests produced diminishing returns because the scoring task itself was structurally prone to synthesis disagreement.

**v3.0 decomposes scoring into two steps:**
1. **Classification:** Assign binary labels (true/false) to observable features. Each label has a bright-line test.
2. **Synthesis:** Apply a deterministic formula to map labels → score. The formula encodes priority rules that scorers no longer apply through judgment.

**Validation results:**

| Dimension | v2.8 Direct κ | v3.0 Labels Post-Cal κ | Pilot Size |
|-----------|---------------|-------------------------|------------|
| Act | 0.429 | **1.000** | 40 cases (20 T1 + 20 T2) |
| Diag | 0.182 | **1.000** | 20 cases (Track 1) |

Full methodology documented in `protocol/rubric_design_methodology.md`.

---

## The Three Dimensions

### Overview

| Dimension | Question | Method | Scale |
|-----------|----------|--------|-------|
| **Diagnosis** | Did the agent correctly identify the problem? | 5 binary labels → formula | 0-3 |
| **Actionability** | Can the user solve their problem with this guidance? | 4 binary labels → formula | 0-3 |
| **Fabrication** | Does the guidance contain fabricated technical claims? | Direct binary | Yes/No |

Score each dimension independently. A case can have Diagnosis=3 and Actionability=0 (correct diagnosis, no fix). A case can have Diagnosis=1 and Actionability=2 (wrong root cause but the suggested workaround happens to help). These are real patterns in our data.

---

## Dimension 1: Diagnosis (0-3) — Label-Based

**Question:** Did the agent correctly identify what is causing the user's problem?

### Labels

For each case, classify on **five binary labels** (true/false):

#### D1: `correct_subsystem`

**Question:** Does the guidance identify the correct area of PyTorch responsible for the issue (e.g., Dynamo, Inductor, AOTAutograd, SDPA, distributed)?

- **true** = Correctly names or describes the subsystem where the problem originates.
- **false** = Wrong subsystem, vague ("something in the compiler"), or no diagnosis at all.

**Bright-line test:** If you removed all other content and just kept the subsystem attribution, would an engineer know which team/component to assign the bug to?

#### D2: `names_mechanism`

**Question:** Does the guidance name the specific technical mechanism causing the issue?

- **true** = Names a specific config option, API, env var, code path, or internal function. Examples: "cache_size_limit", "guard failure on tensor shape", "tl.dot codegen", "TORCHINDUCTOR_FX_GRAPH_CACHE".
- **false** = Stays at subsystem level: "this is a Dynamo issue", "related to the cache", "compilation overhead problem."

**Bright-line test:** Could a developer grep the PyTorch source code for the named mechanism and find the relevant code? If yes → true.

#### D3: `causal_chain`

**Question:** Does the guidance explain WHY the mechanism causes this specific problem?

- **true** = Provides a causal explanation: "X happens because Y, which triggers Z." The chain connects the root cause to the user's observed symptom.
- **false** = Names what's happening but not why. "This is a guard failure" without explaining what guard failed or why.

**Bright-line test:** Does the explanation have at least one "because" / "which causes" / "due to" connecting mechanism to symptom?

**Calibration rule:** Investigation methodology ("how to find the cause") does NOT count as causal chain. The explanation must state the actual cause, not how to discover it. "Run bisect to narrow down the commit" = methodology. "The regression was introduced in commit X because of Y" = causal chain.

#### D4: `consistent_with_resolution`

**Question:** (For resolved cases only) Is the diagnosis consistent with the actual fix/resolution?

- **true** = The diagnosed mechanism matches what actually fixed the problem.
- **false** = The diagnosis points to a different cause than what the resolution addressed.
- **N/A** = Issue is unresolved. **Set to true** (do not penalize unresolved cases).

**Bright-line test:** If you read only the diagnosis and then read the fix, do they address the same mechanism?

#### D5: `case_specific_diagnosis`

**Question:** Is the diagnostic reasoning tied to THIS case's details, or is it generic?

- **true** = References the user's specific error message, stack trace, model architecture, code pattern, or issue number.
- **false** = Generic diagnosis that could apply to any issue in the same subsystem.

**Bright-line test:** Could you swap this diagnosis onto a different issue in the same subsystem and it would still make sense? If yes → false.

**Calibration rule:** Referencing specific issue numbers or specific error messages = case_specific=true.

### Diagnosis Formula

```
count = sum(correct_subsystem, names_mechanism, causal_chain, case_specific_diagnosis)
# consistent_with_resolution acts as a cap, not a contributor

IF consistent_with_resolution == false:
    Diag = min(1, count)    # Cap at 1 if diagnosis contradicts actual fix
ELIF count >= 3:
    Diag = 3
ELIF count == 2:
    Diag = 2
ELIF count == 1:
    Diag = 1
ELSE:
    Diag = 0
```

**Design rationale:** The formula counts how many diagnostic features are present. `consistent_with_resolution` acts as a quality gate — if the diagnosis contradicts the actual fix, it can't score above 1 regardless of how many features it has. The count threshold (≥3 for Diag=3) means a diagnosis needs most features to earn the top score, but doesn't need all four.

### Track-Aware Diagnosis Rules

These rules from v2.9 still apply and interact with labels as follows:

**Track 2 (doc-restricted) — Unresolved issues:**
If the agent accurately identifies the documentation gap ("this is not covered in official docs"), score:
- `correct_subsystem` = true (accurate characterization of the gap)
- `names_mechanism` = true IF the agent names the specific topic/API not covered
- `case_specific_diagnosis` = true IF the gap identification is specific to this case
- Apply the formula normally. An accurate gap identification typically yields Diag=3.

**Track 1 (unrestricted):**
"Docs don't cover this" alone is insufficient — the agent had access to GitHub, source code, and forums. Label accordingly: `names_mechanism` = false if no specific mechanism named beyond "not documented."

**Resolved issues (both tracks):**
Always score against the actual fix. `consistent_with_resolution` = false if the diagnosis doesn't match the fix, regardless of track constraints.

---

## Dimension 2: Actionability (0-3) — Label-Based

**Question:** Can the user take the agent's guidance and solve (or meaningfully progress on) their problem?

### Labels

For each case, classify on **four binary labels** (true/false):

#### A1: `standalone_fix`

**Question:** Can a developer apply this guidance to fix or address their specific issue without additional research or external information?

- **true** = The guidance contains a complete, self-contained fix: specific API call, config setting, env var, version upgrade with specific version, or code change that the developer can copy and apply directly.
- **false** = The guidance points in a direction but the developer would need to look up specifics, consult other docs, or experiment to arrive at a working fix.

**Bright-line test:** If you gave ONLY this guidance to a competent PyTorch developer who has never seen the issue before, could they resolve it without opening any other resource?

**Calibration rules:**
- A version upgrade counts as standalone_fix=true IF the guidance names the specific version (e.g., "upgrade to PyTorch 2.2+"). Vague "try upgrading" = false.
- "Avoid feature X" counts as standalone_fix=true IF the guidance provides the specific avoidance action (e.g., "use `torch.compiler.disable()` on the checkpoint wrapper"). Vague "try avoiding the feature" = false.
- `standalone_fix` means "can the developer act without further research," NOT "does it fix the root cause." Workarounds that are immediately actionable count.

#### A2: `has_imperative`

**Question:** Does the guidance contain at least one specific imperative action step?

- **true** = Contains explicit instructions: "set X=Y", "add `config.foo = True`", "wrap the function with `@torch.compile`", "check GitHub issue #12345."
- **false** = Purely descriptive or diagnostic. Explains what's happening but doesn't tell the user what to DO.

**Bright-line test:** Does the guidance contain a verb in imperative mood directed at the developer? ("Set...", "Add...", "Change...", "Use...", "Remove...", "Check...", "Try...")

**Clarification:** Descriptive necessity statements are NOT imperatives. "Would need to consult...", "requires understanding...", "you would need to build..." are observations about the problem, not instructions. Only score true when the agent explicitly directs the user to take an action.

#### A3: `case_specific`

**Question:** Is the guidance's actionable content tied to the details of THIS specific issue?

- **true** = References the specific error message, stack trace, model architecture, or other details unique to this case. The actionable advice wouldn't apply verbatim to a different issue.
- **false** = Generic advice that could be copy-pasted to a different torch.compile issue without modification.

**Bright-line test:** Could you swap this guidance onto a different torch.compile issue from a different category and it would still make sense? If yes → false. If no → true.

#### A4: `is_template`

**Question:** Could this exact response (not just the advice, but the specific wording and structure) appear as the response to a different case unmodified?

- **true** = The response follows a generic template pattern — "docs don't cover X" followed by listing general doc topics, or boilerplate debugging advice that appears identically across cases.
- **false** = The response is customized to this case: quotes the user's error, references their specific setup, tailors the fix to their code.

**Bright-line test:** Would this exact Actionability section appear nearly verbatim in the agent's response to a *different* issue? If yes → true.

**Note:** `is_template` and `case_specific` are related but NOT inverses. A response can be case_specific=true (references user's error) AND is_template=true (but gives boilerplate advice around it). The formula uses `case_specific` for score derivation; `is_template` is recorded for analysis but does not enter the formula.

### Actionability Formula

```
IF standalone_fix == true:
    Act = 3
ELIF has_imperative == true AND case_specific == true:
    Act = 2
ELIF has_imperative == true AND case_specific == false:
    Act = 1
ELSE:
    Act = 0
```

**Priority:** `standalone_fix` takes absolute priority. If the fix works standalone, no other label can override it down. This encodes the v2.8 scope rule: the interchangeability test does NOT cap standalone fixes.

**Design rationale:** The formula captures the v2.0–v2.9 scoring rules in a deterministic structure:
- Act=3: User can apply directly → `standalone_fix`
- Act=2: User has case-specific next steps → imperative + specific
- Act=1: User has generic advice → imperative but not specific
- Act=0: User has nothing actionable → no imperative at all

### The Gap Acknowledgment Pattern

Under label-based scoring, this pattern is unambiguous:

| Label | Value | Why |
|-------|-------|-----|
| `standalone_fix` | false | "Not documented" isn't a fix |
| `has_imperative` | false | No action directed at user |
| `case_specific` | varies | May reference the specific gap |
| `is_template` | often true | Same template across gaps |
| **Derived Act** | **0** | Formula: no imperative → Act=0 |

Combined with Diagnosis labels (accurate gap ID → Diag=3), this cleanly decomposes the pattern that caused 20/21 large v1 disagreements.

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
- Deprecated but once-real API (note in rationale, but don't flag)
- General-knowledge claims like "graph breaks reduce performance" (not a verifiable technical claim)
- Hedged suggestions: "if such a config exists" (agent explicitly disclaims certainty)

### Fabrication Scoring Workflow (Detector-First)

1. Run `verify_claims.py` on the agent guidance BEFORE manual scoring begins.
2. Provide detector results to both manual scorers alongside the guidance.
3. Manual scorers **confirm** detector flags (mark fabrication=Yes for flagged cases) and **add** cases the detector cannot catch: semantic fabrication (wrong return values, wrong function signatures), fabricated issue references, fabricated pip packages.
4. Manual scorers do NOT independently search for name-based fabrication — the detector handles this.

**Why:** LLM scorers skip fabrication verification at scale (Raven flagged 0/28 real fabrications across 1,064 cases in v2.8). The detector-first process removes the "forgot to check" failure mode. See `analysis/track1_iaa_root_cause.md`.

### Fabrication and Overall Scoring

Fabrication does NOT override Diagnosis or Actionability scores. Fabrication is recorded as a separate flag. Downstream analysis can apply penalties (e.g., "cap effective score at 1 if Fabrication=Yes") but that is an analysis decision, not a scoring decision. Scorers report what they see; they do not apply caps.

---

## Scoring Process

For each test case:

1. **Read** the user's question and the agent's response.
2. **Score Diagnosis labels (D1–D5):** Assign true/false to each label using the bright-line test. Write a one-sentence rationale for each label.
3. **Compute Diagnosis score:** Apply the Diagnosis formula to derive Diag 0–3.
4. **Score Actionability labels (A1–A4):** Assign true/false to each label using the bright-line test. Write a one-sentence rationale for each label.
5. **Compute Actionability score:** Apply the Actionability formula to derive Act 0–3.
6. **Score Fabrication (Yes/No):** Check detector results first, then add any semantic fabrication the detector missed.
7. **Record** all labels, derived scores, and rationales.

**CRITICAL:** The scorer assigns labels only. The derived score is computed mechanically from the formula. If a scorer disagrees with the derived score, they should re-examine their labels — the formula is not overridable. If a label seems wrong given the derived score, adjust the label, not the score.

---

## Recording Format

For each case, record:

```json
{
  "id": "J7-15",
  "resolution": "unresolved",
  "correct_subsystem": true,
  "correct_subsystem_rationale": "Correctly identifies Dynamo as the source of the compilation issue",
  "names_mechanism": true,
  "names_mechanism_rationale": "Names guard failure on dynamic shapes — grep-able in PyTorch source",
  "causal_chain": true,
  "causal_chain_rationale": "'because each new sequence length triggers a new guard failure' — connects mechanism to symptom",
  "consistent_with_resolution": true,
  "consistent_with_resolution_rationale": "N/A — unresolved case, set to true",
  "case_specific_diagnosis": true,
  "case_specific_diagnosis_rationale": "References user's specific variable sequence lengths and batch processing setup",
  "derived_diag": 3,
  "standalone_fix": false,
  "standalone_fix_rationale": "Suggests investigating dynamic shapes but doesn't provide specific config change",
  "has_imperative": true,
  "has_imperative_rationale": "'Check your model's input shapes and consider using torch._dynamo.mark_dynamic()'",
  "case_specific": true,
  "case_specific_rationale": "References user's specific sequence length dimension",
  "is_template": false,
  "is_template_rationale": "Response tailored to this user's sequence length scenario",
  "derived_act": 2,
  "fabrication": false,
  "fabrication_detail": "n/a"
}
```

---

## Edge Cases

### Edge Case 1: Correct diagnosis but fabricated fix

- Diagnosis labels: correct_subsystem=true, names_mechanism=true, causal_chain=true, consistent=true, case_specific=true → **Diag=3**
- Act labels: standalone_fix=false (fix doesn't exist), has_imperative=true, case_specific=true → **Act=2** (or Act=0 if no real imperative)
- Fabrication: **Yes**

### Edge Case 2: Wrong diagnosis but accidentally useful advice

- Diagnosis labels: correct_subsystem=false, etc. → **Diag=0**
- Act labels: standalone_fix=true (the workaround works) → **Act=3**
- Fabrication: **No**

### Edge Case 3: Agent says "file a bug"

- Act labels: standalone_fix=false, has_imperative=true ("file a bug"), case_specific=false (generic advice) → **Act=1**
- If agent links to the specific existing issue: case_specific=true → **Act=2**

### Edge Case 4: Cookie-cutter template response

- Diagnosis labels: correct_subsystem=maybe, names_mechanism=false, causal_chain=false, case_specific=false → **Diag=0 or 1**
- Act labels: standalone_fix=false, has_imperative=true (generic "try X"), case_specific=false → **Act=1**
- If purely descriptive with no imperative → **Act=0**

### Edge Case 5: Doc-restricted gap acknowledgment

- Diagnosis labels: correct_subsystem=true, names_mechanism=true (names specific gap), case_specific=true → **Diag=3**
- Act labels: standalone_fix=false, has_imperative=false → **Act=0**
- Fabrication: **No**

### Edge Case 6: Standalone fix that's repetitive across cases

- Act labels: standalone_fix=true → **Act=3**
- Record `[repetitive-fix]` in standalone_fix_rationale for downstream analysis
- The label formula does not penalize repetitive fixes — the value to the user is the same

---

## Calibration Rules (Established)

These rules were established during pilot calibration and are binding for all future scoring:

### Actionability Calibration
1. **Version upgrade = standalone_fix** if the guidance names the specific version (e.g., "upgrade to PyTorch 2.2+"). Vague "try upgrading" = false.
2. **"Avoid feature X" = standalone_fix** if the guidance provides the specific avoidance action. Vague "try avoiding" = false.
3. **standalone_fix means actionable, not root-cause-fixing.** Workarounds that the developer can apply immediately without further research count as standalone_fix=true.

### Diagnosis Calibration
1. **Referencing specific issue numbers or error messages = case_specific_diagnosis=true.**
2. **Investigation methodology ≠ causal_chain.** "Run bisect to narrow down the commit" explains how to find the cause — it does not explain the cause itself. causal_chain requires stating the actual cause.

### Adding New Calibration Rules

During scoring, if both scorers encounter a case where the labels are ambiguous and the bright-line test doesn't resolve it:
1. Document the case and both scorers' reasoning.
2. Formulate a rule that resolves the ambiguity for this case AND future similar cases.
3. Add the rule to this section.
4. Re-score any prior cases affected by the new rule.

Calibration rules must be **reusable** — each rule applies to a class of cases, not a single case.

---

## Relationship to Prior Rubric Versions

This rubric replaces v2.9. The key evolution:

| Aspect | v2.0–v2.9 (Direct Scoring) | v3.0 (Label-Based) |
|--------|---------------------------|---------------------|
| Scorer task | Read guidance, assign 0–3 | Read guidance, assign true/false per label |
| Subjectivity | Per-case judgment on score boundaries | Per-case judgment on binary labels only |
| Synthesis | Implicit (scorer combines observations) | Explicit (formula combines labels) |
| Transparency | Opaque number + rationale | Per-label rationale + mechanical derivation |
| IAA (Act) | κ = 0.429 | κ = 1.000 (post-calibration) |
| IAA (Diag) | κ = 0.182 | κ = 1.000 (post-calibration) |

All v2.x scoring rules, edge cases, and track-aware logic are preserved in the label definitions and formula design. The content hasn't changed — only the method of arriving at the score.

**Migration:** Prior v2.x scores are NOT directly comparable to v3.0 label-derived scores. When label scoring reveals different scores than direct scoring, the label-derived score is more reliable (validated by IAA). Full re-scoring under v3.0 is required for the final dataset.

---

## Version History

*Rubric v3.0 — 2026-04-14. Replaces direct ordinal scoring with label-based decomposition for Diagnosis and Actionability. Diagnosis: 5 binary labels (correct_subsystem, names_mechanism, causal_chain, consistent_with_resolution, case_specific_diagnosis) + count-based formula. Actionability: 4 binary labels (standalone_fix, has_imperative, case_specific, is_template) + priority-based formula. Validated on 60 pilot cases: Act κ improved from 0.429 to 1.000 (40 cases), Diag κ improved from 0.182 to 1.000 (20 cases). See protocol/rubric_design_methodology.md for full methodology. Fabrication unchanged from v2.9 (detector-first workflow).*

*Prior versions (v2.0–v2.9): See rubric_v2_multidimensional.md for full changelog.*
