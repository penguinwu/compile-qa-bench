# torch-compile-doc-eval

Evaluation framework for measuring whether torch.compile documentation helps AI agents resolve real user problems.

**Core question:** When a user asks an AI agent for help with torch.compile, can the agent find and use official documentation to produce correct guidance?

## Two Evaluation Modes

**Mode A — Coverage & Discoverability:** Does pytorch.org have relevant docs (Coverage), and can web search find them (Discoverability)?

**Mode B — Resolution Quality:** Given a real torch.compile problem with full context, can an agent produce correct, actionable guidance?

Results are cross-referenced: Mode A scores explain *why* Mode B succeeds or fails.

## Structure

```
├── suite/                        # FIXED INPUT (immutable after finalization)
│   ├── cases.json                # 160 balanced test cases
│   ├── sampling.md               # How cases were selected
│   └── expanded_test_suite.json  # Earlier 80-case version (archived)
│
├── protocol/                     # VERSIONED RULES
│   ├── annotation_guide.md       # Scoring rubrics (Mode A + B)
│   ├── methodology.md            # Full evaluation methodology
│   ├── rubric_v2_multidimensional.md  # Mode B rubric v2.8 (production)
│   └── scoring_workflow.md       # End-to-end scoring guide
│
├── runs/                         # EVALUATION OUTPUTS (grows over time)
│   ├── YYYY-MM-DD-baseline/      # Pre-fix baseline
│   │   ├── mode_a_scores.json
│   │   ├── mode_b_scores.json
│   │   └── search_artifacts/     # Pinned URLs per case
│   └── iaa/                      # Inter-annotator agreement validation
│       ├── round4/
│       └── mode_b_pilot/
│
├── scripts/                      # EVALUATION CODE
│   ├── run_mode_a.py             # Run Mode A (search + score)
│   ├── run_mode_b.py             # Run Mode B (agent + score)
│   ├── compute_iaa.py            # Compare annotator scores (weighted κ)
│   ├── verify_claims.py          # Automated fabrication detector
│   ├── build_balanced_test_suite.py
│   ├── build_expanded_suite.py
│   └── extract_journey_issues.py
│
├── analysis/                     # CROSS-RUN ANALYSIS
│   ├── inter_annotator_agreement.md
│   └── iaa_v2_2_full_160.md     # Kappa progression v2.2→v2.8
│
└── decisions.md                  # Design rationale (8 key decisions)
```

## Test Suite

**160 cases** from 9,277 pytorch/pytorch issues with `oncall:pt2` label:
- 8 user journeys × 20 cases each (10 resolved + 10 unresolved)
- Export/AOTInductor cases excluded (separate stack)
- Equal journey weighting (normalizes for issue volume bias)

See `suite/sampling.md` for full methodology.

## Scoring Rubrics

### Mode A

| Coverage | Criteria |
|----------|----------|
| Full | pytorch.org page directly answers the specific question |
| Partial | Page covers the concept area but misses the specific failure mode |
| None | No relevant compile-specific content exists |

| Discoverability | Criteria |
|-----------------|----------|
| 3 | Top result directly relevant |
| 2 | Relevant result on first page |
| 1 | Relevant result exists but buried |
| 0 | No relevant official docs in results |

### Mode B — Multi-Dimensional Rubric (v2.8, validated)

Mode B scores agent guidance on three independent dimensions:

| Dimension | Scale | Question |
|-----------|-------|----------|
| **Diagnosis** | 0-3 | Did the agent correctly identify the problem? |
| **Actionability** | 0-3 | Can the user act on the guidance to solve their problem? |
| **Fabrication** | Yes/No | Does the guidance contain fabricated technical claims? |

**IAA validation (v2.8, n=160):**

| Dimension | Weighted κ | Interpretation |
|-----------|-----------|----------------|
| Diagnosis | 0.863 | Near-perfect |
| Actionability | 0.885 | Near-perfect |
| Fabrication | 96.2% agreement | Near-perfect |

See `protocol/rubric_v2_multidimensional.md` for the full rubric with scoring rules, worked examples, and edge cases. See `analysis/iaa_v2_2_full_160.md` for the complete kappa progression from v2.2 to v2.8.

## How to Run

```bash
# 1. Run Mode A searches (pin results)
python scripts/run_mode_a.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/ --search-only

# 2. Score Mode A (from pinned search artifacts)
python scripts/run_mode_a.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/

# 3. Run Mode B (agent end-to-end)
python scripts/run_mode_b.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/

# 4. Compare annotators (computes weighted kappa + agreement + confusion matrix)
python scripts/compute_iaa.py --scorer1 runs/rocky_v2_8_160_scores.json --scorer2 runs/raven_v2_8_full_160_scores.json --multidim
```

## IAA Validation

Mode B rubric validated through 7 iterations (v2.2→v2.8), achieving κ≥0.80 on all dimensions. Key techniques: dimension separation, bright-line boundary tests, priority rules for conflicting tests. See `analysis/iaa_v2_2_full_160.md` for full progression and `decisions.md` for design rationale.

Mode A validated through 4 IAA rounds. See `runs/iaa/` and `analysis/inter_annotator_agreement.md`.

## Data Source

All test cases derived from public GitHub issues at [pytorch/pytorch](https://github.com/pytorch/pytorch), originally collected for the [OSS Model Graph Break Corpus](https://github.com/penguinwu/oss-model-graph-break-corpus).

## Related

- [torch.compile Agent Documentation & Skills — Design Doc](https://docs.google.com/document/d/1bDfcdb3rt7bzqHkD_RZxvJONHM6ZYi_JAv__fzBEgIo)
