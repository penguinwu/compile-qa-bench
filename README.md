# CompileQA-Bench

A benchmark for evaluating any system's ability to answer real torch.compile user questions. The cases (320 real GitHub issues spanning 8 user journeys) are the invariant; the *answerer* varies — official docs today, QA bots / skill-augmented LLMs / internal agents tomorrow.

> Repo: `~/projects/compile-qa-bench/` (renamed from `torch-compile-doc-eval/` on 2026-04-22).

**Core question:** Given a real torch.compile problem, can system X (docs, agent, bot, model) produce correct, actionable, non-fabricated guidance?

Analogous to **SWE-bench** for code-fix evaluation — but for question-answering capability rather than code generation.

## Configurations (the answerer slot)

Each configuration plugs a different *answerer* into the same case suite + same rubric. Today:

- **Track 1 — Unrestricted:** Agent answers from full knowledge (LLM + open web). Ceiling for what's possible.
- **Track 2 — Doc-restricted:** Agent answers using only official pytorch.org docs. Measures doc quality directly.

Future configurations: PyTorch+Skills agents, internal QA bots, fine-tuned models. Same scoring, plug in any answerer.

## Three Scoring Dimensions (v3.0 rubric)

- **Actionability (0–3):** Can the user act on this answer to fix their problem?
- **Diagnostic Quality (0–3):** Does the answer correctly identify the cause?
- **Fabrication (binary):** Did the answer invent APIs, behaviors, or facts?

All three are validated with Cohen's quadratic weighted κ ≥ 0.90 across two independent scorers (Owl + Raven).

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
