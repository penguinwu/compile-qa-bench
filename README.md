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
│   └── methodology.md            # Full evaluation methodology
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
│   ├── compute_iaa.py            # Compare annotator scores
│   ├── build_balanced_test_suite.py
│   ├── build_expanded_suite.py
│   └── extract_journey_issues.py
│
└── analysis/                     # CROSS-RUN ANALYSIS
    ├── inter_annotator_agreement.md
    └── ...
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

### Mode B — Quality of Guidance (0-3)

**Resolved issues:** 3=correct fix, 2=right diagnosis/partial solution, 1=wrong diagnosis, 0=hallucinated fix

**Unresolved issues:** 3=correctly identifies limitation+workaround, 2=partially helpful, 1=vague/irrelevant, 0=confidently wrong

See `protocol/annotation_guide.md` for full rubric with calibration examples.

## How to Run

```bash
# 1. Run Mode A searches (pin results)
python scripts/run_mode_a.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/ --search-only

# 2. Score Mode A (from pinned search artifacts)
python scripts/run_mode_a.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/

# 3. Run Mode B (agent end-to-end)
python scripts/run_mode_b.py --suite suite/cases.json --output-dir runs/YYYY-MM-DD-name/

# 4. Compare annotators
python scripts/compute_iaa.py --scorer1 rocky_scores.json --scorer2 raven_scores.json
```

## IAA Validation

Four rounds of inter-annotator agreement for Mode A, one pilot for Mode B. See `runs/iaa/` and `analysis/inter_annotator_agreement.md`.

## Data Source

All test cases derived from public GitHub issues at [pytorch/pytorch](https://github.com/pytorch/pytorch), originally collected for the [OSS Model Graph Break Corpus](https://github.com/penguinwu/oss-model-graph-break-corpus).

## Related

- [torch.compile Agent Documentation & Skills — Design Doc](https://docs.google.com/document/d/1bDfcdb3rt7bzqHkD_RZxvJONHM6ZYi_JAv__fzBEgIo)
