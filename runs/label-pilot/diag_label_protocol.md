# Label-Based Diagnosis Scoring — Protocol

**Version:** v3.0-pilot-diag
**Purpose:** Decompose Diagnosis into discrete labels to resolve the 2/3 boundary disagreement (48/160 cases on Track 1).

## Problem Statement

The Diag 2/3 boundary asks: "Does the guidance identify the specific mechanism or just the correct subsystem?" Scorers consistently disagree on what counts as "specific mechanism." In Track 1, 48/160 cases have Owl=2, Raven=3 — Raven treats subsystem identification as sufficient for Diag=3, Owl requires a named config/API/env var.

## Labels

For each case, classify on **five binary labels** (true/false):

### D1: `correct_subsystem`
**Question:** Does the guidance identify the correct area of PyTorch responsible for the issue (e.g., Dynamo, Inductor, AOTAutograd, SDPA, distributed)?

- **true** = Correctly names or describes the subsystem where the problem originates.
- **false** = Wrong subsystem, vague ("something in the compiler"), or no diagnosis at all.

**Bright-line test:** If you removed all other content and just kept the subsystem attribution, would an engineer know which team/component to assign the bug to?

### D2: `names_mechanism`
**Question:** Does the guidance name the specific technical mechanism causing the issue?

- **true** = Names a specific config option, API, env var, code path, or internal function. Examples: "cache_size_limit", "guard failure on tensor shape", "tl.dot codegen", "TORCHINDUCTOR_FX_GRAPH_CACHE".
- **false** = Stays at subsystem level: "this is a Dynamo issue", "related to the cache", "compilation overhead problem."

**Bright-line test:** Could a developer grep the PyTorch source code for the named mechanism and find the relevant code? If yes → true.

### D3: `causal_chain`
**Question:** Does the guidance explain WHY the mechanism causes this specific problem?

- **true** = Provides a causal explanation: "X happens because Y, which triggers Z." The chain connects the root cause to the user's observed symptom.
- **false** = Names what's happening but not why. "This is a guard failure" without explaining what guard failed or why.

**Bright-line test:** Does the explanation have at least one "because" / "which causes" / "due to" connecting mechanism to symptom?

### D4: `consistent_with_resolution`
**Question:** (For resolved cases only) Is the diagnosis consistent with the actual fix/resolution?

- **true** = The diagnosed mechanism matches what actually fixed the problem (from issue resolution).
- **false** = The diagnosis points to a different cause than what the resolution addressed.
- **N/A** = Issue is unresolved. Set to true (don't penalize unresolved cases).

**Bright-line test:** If you read only the diagnosis and then read the fix, do they address the same mechanism?

### D5: `case_specific_diagnosis`
**Question:** Is the diagnostic reasoning tied to THIS case's details, or is it generic?

- **true** = References the user's specific error message, stack trace, model architecture, or code pattern.
- **false** = Generic diagnosis that could apply to any issue in the same subsystem.

**Bright-line test:** Could you swap this diagnosis onto a different issue in the same subsystem and it would still make sense? If yes → false.

## Formula

Labels → Diagnosis score:

```
count = sum([correct_subsystem, names_mechanism, causal_chain, case_specific_diagnosis])
# consistent_with_resolution acts as a cap, not a contributor

IF consistent_with_resolution == false:
    Diag = min(1, count)  # Cap at 1 if diagnosis contradicts actual fix
ELIF count >= 3:
    Diag = 3
ELIF count == 2:
    Diag = 2
ELIF count == 1:
    Diag = 1
ELSE:
    Diag = 0
```

**Key design decision:** `names_mechanism` is required for Diag=3. If correct_subsystem=true, names_mechanism=false, causal_chain=true, case_specific=true → count=3 → Diag=3. BUT if the scorer correctly applies the bright-line test for names_mechanism (can you grep for it?), this forces the diagnosis to be specific enough for Diag=3.

## Output Format

```json
{
  "id": "J1-1",
  "correct_subsystem": true,
  "correct_subsystem_rationale": "...",
  "names_mechanism": true,
  "names_mechanism_rationale": "...",
  "causal_chain": true,
  "causal_chain_rationale": "...",
  "consistent_with_resolution": true,
  "consistent_with_resolution_rationale": "N/A — unresolved case",
  "case_specific_diagnosis": true,
  "case_specific_diagnosis_rationale": "...",
  "derived_diag": 3
}
```

## Validation Criteria

- **Label-level κ target:** ≥ 0.85 per label (binary Cohen's κ)
- **Derived-score κ target:** ≥ 0.80 (quadratic weighted κ)
- **Comparison:** derived-score κ vs. v2.8 direct-scoring κ (0.415)
