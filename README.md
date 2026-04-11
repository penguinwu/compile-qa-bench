# torch-compile-doc-eval

Evaluation framework for measuring torch.compile documentation quality from an agent's perspective.

**Question:** When a user asks an AI agent for help with torch.compile, can the agent find and use official documentation to resolve the problem?

## What This Is

80 test cases derived from real [pytorch/pytorch](https://github.com/pytorch/pytorch) GitHub issues (label: `oncall:pt2`), organized by 8 user journeys. Each test case includes the original user question, issue context (error messages, stack traces), and expected documentation topics.

We use these test cases to measure **retrieval quality** — whether web search surfaces official PyTorch documentation for real user problems — as the primary metric for documentation effectiveness.

## Key Finding (April 2026 Baseline)

**52.5% of real user questions return zero helpful official documentation via web search.**

| Retrieval Quality | Count | % |
|-------------------|-------|---|
| ✅ Official doc directly answers | 10 | 12.5% |
| ⚠️ Official doc appears but tangential | 28 | 35.0% |
| ❌ No helpful official documentation | 42 | 52.5% |

The worst-served journeys (0% direct doc hits): Performance Diagnosis, Correctness & Debugging, Performance Optimization.

## Structure

```
├── README.md                          # This file
├── evaluation_methodology.md          # Full methodology specification
├── data/
│   └── expanded_test_suite.json       # 80 test cases (10 per journey)
├── analysis/
│   ├── retrieval_analysis_report.md   # Web search retrieval analysis
│   └── journey_issues_analysis.md     # Issue-to-journey mapping analysis
└── scripts/
    ├── extract_journey_issues.py      # Extract issues from pt2_all_issues.json
    ├── build_expanded_suite.py        # Build 80-case test suite
    └── pilot_evaluation.py            # Heuristic evaluation runner
```

## Test Suite Format

Each test case in `data/expanded_test_suite.json`:

```json
{
  "id": "J4-2",
  "journey": "J4: Graph Breaks",
  "source_issue": 139440,
  "source_url": "https://github.com/pytorch/pytorch/issues/139440",
  "user_question": "torch.compile with DDP causes a graph break on _broadcast_coalesced. How do I use torch.compile with distributed training?",
  "issue_context": "### 🐛 Describe the bug\n\nCompiling a whole ddp wrapped model I got this graph break\n\n### Error logs\n\n```python\n..._broadcast_coalesced...\n```",
  "difficulty": "advanced",
  "expected_doc_topics": ["DDP", "distributed", "graph breaks", "compile + DDP integration"]
}
```

## The 8 User Journeys

| Journey | Test Cases | Issue Pool | Baseline Direct Hit % |
|---------|-----------|------------|----------------------|
| J1: First Compile | 10 | 692 | 30% |
| J2: Performance Diagnosis | 10 | 320 | **0%** |
| J3: Correctness & Debugging | 10 | 418 | **0%** |
| J4: Graph Breaks | 10 | 2,053 | 20% |
| J5: Performance Optimization | 10 | 1,805 | **0%** |
| J6: Dynamic Shapes | 10 | 976 | 20% |
| J7: Compile-Time Performance | 10 | 366 | 20% |
| J8: Custom & Higher-Order Ops | 10 | 651 | 10% |

## Source Reliability Hierarchy

When official docs fail, agents fall back to these sources (in decreasing reliability):

| Source | Reliability | Why |
|--------|-------------|-----|
| **Official pytorch.org docs** | Authoritative | Versioned, reviewed, maintained |
| **GitHub issues** | Specific but fragile | Tied to individual bugs, may be stale or unresolved |
| **discuss.pytorch.org forums** | Unreliable | Rolling discussions, never audited, never corrected after posting |
| **Medium/blogs** | Unreliable | SEO-optimized, may be outdated, often paraphrased from other sources |

## How to Reproduce

### Prerequisites

- Python 3.10+
- The PT2 issues dataset: `pt2_all_issues.json` (9,277 issues, ~25MB)
  - Source: GitHub API, all issues from pytorch/pytorch with label `oncall: pt2`
  - Fetched with `scripts/extract_journey_issues.py` (requires GitHub token)

### Steps

1. **Extract journey-mapped issues:**
   ```bash
   # Requires pt2_all_issues.json in the same directory or adjust path in script
   python scripts/extract_journey_issues.py
   ```

2. **Build expanded test suite (80 cases):**
   ```bash
   python scripts/build_expanded_suite.py
   ```

3. **Run retrieval evaluation:**
   For each question in `data/expanded_test_suite.json`, run a web search and classify results using the scoring rubric in `evaluation_methodology.md`.

4. **Compare before/after:**
   After documentation improvements, re-run step 3 with the same queries and compare scores.

## Methodology

See [`evaluation_methodology.md`](evaluation_methodology.md) for the full specification including:
- Three evaluation dimensions (retrieval quality, source attribution, resolution relevance)
- Scoring rubrics
- Control methodology for before/after comparison
- Key insights from the prototype

## Data Source

All test cases are derived from public GitHub issues at [pytorch/pytorch](https://github.com/pytorch/pytorch). The issues dataset was originally collected for the [OSS Model Graph Break Corpus](https://github.com/penguinwu/oss-model-graph-break-corpus) project.

## Related

- [torch.compile Agent Documentation & Skills — Design Doc](https://docs.google.com/document/d/1bDfcdb3rt7bzqHkD_RZxvJONHM6ZYi_JAv__fzBEgIo)
- [OSS Model Graph Break Corpus](https://github.com/penguinwu/oss-model-graph-break-corpus)
