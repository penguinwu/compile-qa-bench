# Scoring Workflow — End-to-End Guide

How to run a Mode B scoring round from start to finish. This document is the operational companion to the rubric (`rubric_v2_multidimensional.md`) and methodology (`methodology.md`).

## Prerequisites

1. **Read the rubric** — `protocol/rubric_v2_multidimensional.md` (v2.8, production-ready)
2. **Read eval lessons** — `skills/eval-lessons.md` (10 hard-won lessons; prevents repeat mistakes)
3. **Understand the test suite** — `suite/cases.json` (160 cases, 8 journeys × 20 each)
4. **Agent guidance to score** — JSON in `runs/2026-04-12-baseline/mode_b_doc_restricted.json` (or equivalent for the run being scored)

## Roles

| Role | Who | Rules |
|------|-----|-------|
| **Generator** | Dedicated agent (not a scorer) | Produces agent guidance. Does NOT score. |
| **Scorer 1** | Any agent with rubric access | Scores independently. Must not be the generator or the doc author. |
| **Scorer 2** | Different agent from Scorer 1 | Scores independently. Same restrictions. |

**Critical:** Self-scoring is invalid (+0.79 inflation bias). The generator cannot detect its own fabrications. See `decisions.md` D1 and D6.

## Step 1: Generate Agent Guidance

```bash
python scripts/run_mode_b.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/
```

This produces agent responses for all 160 cases. The generator agent sees:
- The user's question
- Full issue context (error messages, stack traces, code — first 1500 chars)
- System prompt instructing it to search web and provide guidance

**Track 2 (doc-restricted):** Generator can ONLY reference official pytorch.org documentation.
**Track 1 (unrestricted):** Generator searches freely (GitHub, forums, blogs, docs).

## Step 2: Run Fabrication Detection

```bash
python scripts/verify_claims.py --input runs/YYYY-MM-DD-name/mode_b_results.json \
    --torch-path /path/to/torch/source
```

This extracts verifiable claims (config flags, env vars, API names, imports) from each agent response and checks them against PyTorch source. Zero false positive rate.

Output: JSON with fabrication flags per case. Any case with fabrication is **capped** in scoring.

## Step 3: Score with Two Independent Scorers

Each scorer receives:
- The agent guidance (from Step 1)
- The rubric (`protocol/rubric_v2_multidimensional.md`)
- The test case metadata (question, context, resolution status)
- Fabrication detection results (from Step 2)

Each scorer produces a JSON file with this format:

```json
[
  {
    "id": "J1-1",
    "resolution_status": "resolved",
    "diagnosis": 3,
    "diagnosis_rationale": "Brief explanation of why this score.",
    "actionability": 3,
    "actionability_rationale": "Brief explanation of why this score.",
    "fabrication": false,
    "fabrication_detail": ""
  }
]
```

### Scoring Dimensions

| Dimension | Scale | Question |
|-----------|-------|----------|
| **Diagnosis** | 0-3 | Did the agent correctly identify the problem? |
| **Actionability** | 0-3 | Can the user act on the guidance to solve their problem? |
| **Fabrication** | Yes/No | Does the guidance contain fabricated technical claims? |

### Key Scoring Rules

- **Track-aware:** "Docs don't cover this" is Diag=3 in Track 2 (correct diagnosis of doc gap), but Diag=1 in Track 1 (agent should have found non-doc sources).
- **Fabrication cap:** Cases with fabrication are capped at Diag=1 regardless of diagnosis quality.
- **Template detection:** Generic "try X, check Y, consider Z" without case-specific reasoning → Actionability ≤ 1.
- **Interchangeability test:** If the guidance could apply to a different case without modification → Actionability ≤ 1.
- **Imperative verb test:** Actionable guidance contains specific imperative steps ("add this import", "set this flag"). Vague suggestions don't count.

See the full rubric for bright-line tests at each score boundary.

### Working with Raven (Current Second Scorer)

Raven is on devvm53995, GChat space `spaces/AAQAVvPoEqg`.

1. Upload the updated rubric to GDrive
2. Send Raven the GDrive file ID + summary of what changed (via GChat `--as-user`)
3. Raven scores all 160 cases (~2-3 minutes) and uploads results as JSON to GDrive
4. Download Raven's scores via `gdrive download <FILE_ID>`

**gdrive JSON bug workaround:** `gdrive download` fails on JSON files with "Unexpected JSON response." The content is in the error output:
```bash
gdrive download <FILE_ID> /tmp/output.json 2>&1 | \
  sed -n '/^Error: Unexpected JSON response.*got: /,$ p' | \
  sed '1s/^Error: Unexpected JSON response.*got: //' > /tmp/clean.json
```

## Step 4: Compute Inter-Annotator Agreement

```bash
python scripts/compute_iaa.py \
    --scorer1 runs/rocky_v2_8_160_scores.json \
    --scorer2 runs/raven_v2_8_full_160_scores.json \
    --multidim
```

This computes for each dimension:
- **Weighted κ** (quadratic weights, default) — the headline metric
- **Weighted κ** (linear weights) — for comparison
- **Binary κ** (0 vs ≥1) — coarse agreement check
- **Exact agreement** and **within ±1** percentages
- **Confusion matrix** — shows where disagreements cluster
- **Score distributions** — detects systematic scorer bias
- **Large disagreements** (|diff| ≥ 2) — cases to investigate

### Target Thresholds

| Dimension | Metric | Target | Current (v2.8) |
|-----------|--------|--------|----------------|
| Diagnosis | Quadratic κ | ≥ 0.80 | 0.863 |
| Actionability | Quadratic κ | ≥ 0.80 | 0.885 |
| Fabrication | Agreement % | ≥ 90% | 96.2% |

**Why quadratic weights:** Penalizes large disagreements more than small ones, appropriate for ordinal scales (Fleiss & Cohen, 1973). See `decisions.md` D4.

### If κ < 0.80

1. Examine the confusion matrix — where do disagreements cluster?
2. Read disagreement rationales from both scorers
3. Identify ambiguous rubric language causing divergent interpretations
4. Add bright-line tests to resolve the ambiguity
5. **Both scorers re-score all 160 cases** with the updated rubric (same version)
6. Recompute κ

See `analysis/iaa_v2_2_full_160.md` for the progression from v2.2 (κ=0.027) to v2.8 (κ=0.885) — 7 rubric iterations with detailed root cause analysis at each step.

## Step 5: Report Results

After IAA validation confirms κ ≥ 0.80:

1. Record final scores in `runs/` with descriptive filename
2. Update IAA analysis in `analysis/iaa_v2_2_full_160.md` if rubric version changed
3. Compute aggregate metrics:
   - Mean Diagnosis / Actionability per journey
   - Fabrication rate (% of cases)
   - Score distributions per dimension

## File Naming Conventions

| File | Format |
|------|--------|
| Scorer scores | `runs/{scorer}_{rubric_version}_{n_cases}_scores.json` |
| Agent guidance | `runs/YYYY-MM-DD-name/mode_b_{track}.json` |
| IAA analysis | `analysis/iaa_{rubric_version}_{n_cases}.md` |
| Fabrication results | `runs/YYYY-MM-DD-name/fabrication_check_{track}.json` |

## Common Mistakes

From `skills/eval-lessons.md`:

1. **Don't use keyword matching** — "correct" doesn't mean the answer IS correct
2. **Generic ≠ case-specific** — "try recompiling" matches every compile case but solves none
3. **Templates aren't actionable** — step-by-step boilerplate without case reasoning = low actionability
4. **Same rubric version for both scorers** — even a minor edit invalidates comparison
5. **Rubric iteration ≠ overfitting** — each change must pass: "Would a third scorer find this clearer?"

## Open Validation Items

These are known gaps in the current framework. See `decisions.md` for full rationale.

- **No held-out validation set** (D2) — κ may not generalize to new cases
- **No third scorer** (D1, D6) — κ validated between Rocky/Raven pair only
- **Track 1 IAA untested** (D5) — rubric includes Track 1 rules never empirically validated
- **Mode A × Mode B cross-reference not computed** (D7) — the data exists
