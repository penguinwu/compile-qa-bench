# Evaluation Methodology: torch.compile Agent-Friendly Documentation

**Status:** Validated via prototype (2026-04-11)
**Owner:** Rocky (design), Otter (implementation)

---

## Objective

Measure whether documentation improvements actually help agents resolve real user problems with torch.compile.

## Test Suite

**80 test cases**, 10 per journey, derived from real pytorch/pytorch GitHub issues (oncall:pt2 label, 9,277 issue pool, filtered to 6,810 user-facing).

Each test case has:
- **Clean question** — natural language, what a user would type to an agent
- **Full context** — actual issue body with error messages, stack traces, code snippets (first 1500 chars)
- **Source issue** — GitHub issue number + URL for ground truth resolution
- **Difficulty** — beginner / intermediate / advanced
- **Expected doc topics** — what docs should cover to answer this

### The 8 Journeys

| Journey | Pool Size | Description |
|---------|-----------|-------------|
| J1: First Compile | 692 | Getting started, basic usage, setup |
| J2: Performance Diagnosis | 320 | "Why is compile slower than eager?" |
| J3: Correctness & Debugging | 418 | Wrong results, numerical divergence |
| J4: Graph Breaks | 2,053 | Graph break errors, fullgraph failures |
| J5: Performance Optimization | 1,805 | Tuning, max-autotune, CUDA graphs |
| J6: Dynamic Shapes | 976 | Variable shapes, recompilation, guards |
| J7: Compile-Time Performance | 366 | Compilation too slow, cold start |
| J8: Custom & Higher-Order Ops | 651 | Custom ops, flex_attention, control flow |

## Evaluation Dimensions

### Dimension 1: Retrieval Quality (automated, cheap)

For each test question, run a web search and classify results:

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | **Direct** | Official pytorch.org page directly addresses the question |
| 2 | **Tangential** | Official pytorch.org content appears but generic/partial |
| 1 | **Community** | No official docs, but GitHub issues or forums have relevant content |
| 0 | **Missing** | No helpful results from any source |

**Current baseline (April 2026):**

| Score | Count | % |
|-------|-------|---|
| Direct (3) | 10 | 12.5% |
| Tangential (2) | 28 | 35.0% |
| Community (1) | ~35 | ~44% |
| Missing (0) | ~7 | ~9% |

**Primary metric: % of queries with Score 3 (Direct).** Target: 50%+ after Phase 1.

### Dimension 2: Source Attribution (automated, cheap)

Track WHERE the answer comes from:

| Source | Reliability | Current Frequency |
|--------|-------------|-------------------|
| Official pytorch.org docs | High (authoritative, versioned) | ~48% of queries |
| GitHub issues | Medium (specific but fragile, may be stale) | ~38% of queries |
| discuss.pytorch.org forums | Medium (community, may be incomplete) | ~25% of queries |
| Medium/blogs | Low (may be outdated, wrong, SEO-optimized) | ~31% of queries |
| Other (NVIDIA, HuggingFace, etc.) | Varies | ~10% of queries |

**Goal:** Shift agent reliance from community/blog sources to official docs.

### Dimension 3: Resolution Relevance (semi-automated, medium cost)

For the "full context" version of each test case, score whether retrieved content could plausibly resolve the user's problem:

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | **Resolvable** | Retrieved content contains the answer or actionable fix |
| 2 | **Partial** | Content is relevant but user needs additional research |
| 1 | **Directional** | Content points to the right area but doesn't resolve |
| 0 | **Unhelpful** | Content doesn't help or misleads |

This is harder to automate. Options:
- **Manual scoring** (gold standard but expensive): domain expert rates each result
- **LLM-as-judge**: give an LLM the question + retrieved content, ask if it resolves the issue, compare against ground truth from the GitHub issue thread
- **Proxy metric**: use issue close status + resolution comments as ground truth

## How to Run

### Baseline (Before)
1. Run web search for all 80 clean questions → score retrieval quality
2. Run web search for all 80 full-context versions → score retrieval quality
3. Compare clean vs. full-context retrieval (does more context help or hurt search?)
4. Record source attribution for each

### After Improvement (Phase 1, 2, 3)
1. Re-run identical searches after doc changes are deployed and indexed
2. Compare retrieval quality scores before/after
3. Delta = improvement attributable to documentation changes

### Controls
- **Same queries**: use identical test suite, don't modify questions
- **Same search method**: use the same search API/tool
- **Model-independent**: this evaluates doc quality, not model quality — any model improvement is a confound, controlled by keeping the model constant or measuring retrieval only
- **Timestamp snapshots**: search results change over time — record exact results and dates

## Key Insights from Prototype

1. **J1 (First Compile) is the only well-served journey** — 30% direct hits. All other journeys are ≤20%.
2. **Three journeys have zero direct doc hits** — J2 (Performance Diagnosis), J3 (Correctness), J5 (Performance Optimization). These are the highest-impact improvement targets.
3. **The troubleshooting page is a catch-all that catches nothing** — it appears in ~15 queries but is too generic to resolve any specific question.
4. **GitHub issues are the de facto documentation** for advanced topics — for J5-J8, the most relevant search result is often the exact issue thread.
5. **65% of external users file one issue and never return** (from Otter's analysis) — first-contact doc quality is critical.
6. **473 issues mention "example" in their body** — users want worked examples, not API reference.

## Files

| File | Description |
|------|-------------|
| `expanded_test_suite.json` | 80 test cases with questions + issue context |
| `retrieval_analysis_report.md` | Full retrieval analysis with per-journey breakdown |
| `journey_issues_analysis.md` | Initial 40-issue extraction with methodology |
| `pilot_test_suite.json` | Original 24-case pilot (subset of expanded) |
| `pilot_evaluation_report.md` | Pilot heuristic evaluation (superseded by retrieval analysis) |
| `extract_journey_issues.py` | Issue extraction script |
| `build_expanded_suite.py` | Test suite expansion script |

---

*Methodology validated via prototype on 2026-04-11. Ready for integration into design doc.*
