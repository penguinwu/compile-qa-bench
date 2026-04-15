# Label-Based Actionability Scoring — Pilot Protocol

**Version:** v3.0-pilot
**Purpose:** Test whether decomposing Actionability into discrete binary labels + deterministic formula improves inter-rater reliability over direct ordinal scoring.

## Hypothesis

Scoring disagreements are primarily **synthesis problems** — scorers agree on observable features but combine them differently into a score. If we separate classification (label assignment) from synthesis (score derivation), label-level κ should exceed score-level κ from v2.8/v2.9.

## Labels

For each case, classify the agent guidance on **four binary labels** (true/false):

### L1: `standalone_fix`
**Question:** Can a developer apply this guidance to fix or address their specific issue without additional research or external information?

- **true** = The guidance contains a complete, self-contained fix: specific API call, config setting, env var, or code change that the developer can copy and apply directly.
- **false** = The guidance points in a direction but the developer would need to look up specifics, consult other docs, or experiment to arrive at a working fix.

**Bright-line test:** If you gave ONLY this guidance to a competent PyTorch developer who has never seen the issue before, could they resolve it without opening any other resource?

### L2: `has_imperative`
**Question:** Does the guidance contain at least one specific imperative action step?

- **true** = Contains explicit instructions like "set X=Y", "add `torch._dynamo.config.foo = True`", "wrap the function with `@torch.compile`", etc.
- **false** = Purely descriptive or diagnostic. Explains what's happening but doesn't tell the user what to DO.

**Bright-line test:** Does the guidance contain a verb in imperative mood directed at the developer? ("Set...", "Add...", "Change...", "Use...", "Remove...")

### L3: `case_specific`
**Question:** Is the guidance's reasoning tied to the details of THIS specific issue?

- **true** = References the specific error message, stack trace, model architecture, or other details unique to this case. The reasoning wouldn't apply verbatim to a different issue.
- **false** = Generic advice that could be copy-pasted to a different torch.compile issue without modification.

**Bright-line test:** Could you swap this guidance onto a different torch.compile issue from a different category and it would still make sense? If yes → false. If no → true.

### L4: `is_template`
**Question:** Could this exact response (not just the advice, but the specific wording and structure) apply to a different case unmodified?

- **true** = The response uses generic language: "try reducing graph breaks", "check your config settings", "update to the latest version". No case-specific details embedded.
- **false** = The response is customized to this case: quotes the user's error, references their specific setup, tailors the fix to their code.

**Note:** `is_template` and `case_specific` are related but NOT inverses. A response can be case_specific=true (references user's error) AND is_template=false (customized wording), but it can also be case_specific=true AND is_template=true if it references the error but gives boilerplate advice.

## Formula

Labels → Actionability score:

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

**Priority:** `standalone_fix` takes absolute priority. If the fix works standalone, no other label can override it down.

## Output Format

For each case, produce:

```json
{
  "id": "J1-5",
  "standalone_fix": true,
  "standalone_fix_rationale": "Provides exact env var TORCHINDUCTOR_FX_GRAPH_CACHE=1 that fixes the caching issue",
  "has_imperative": true,
  "has_imperative_rationale": "Says 'Set TORCHINDUCTOR_FX_GRAPH_CACHE=1 before running your script'",
  "case_specific": true,
  "case_specific_rationale": "References user's specific error about cache invalidation on restart",
  "is_template": false,
  "is_template_rationale": "Response is tailored to this user's caching scenario, not generic advice",
  "derived_act": 3
}
```

`derived_act` is computed from the formula — do NOT set it manually. The scorer only assigns labels.

## Validation Criteria

- **Label-level κ target:** ≥ 0.85 per label (binary Cohen's κ)
- **Derived-score κ target:** ≥ 0.80 (quadratic weighted κ)
- **Comparison:** derived-score κ vs. v2.8/v2.9 direct-scoring κ (0.642)

## Cases

20 cases from Track 1: 10 selected from prior Act disagreements, 10 from prior Act agreements. Case guidance is in `pilot_cases_20.json` (same directory).
