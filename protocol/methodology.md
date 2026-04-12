# Evaluation Methodology: torch.compile Agent-Friendly Documentation

**Status:** Validated via experiment (2026-04-11)
**Owner:** Rocky (design & validation)

---

## Objective

Measure whether documentation improvements actually help agents resolve real user problems with torch.compile.

## Test Suite

**160 test cases**, 10 resolved + 10 unresolved per journey, derived from real pytorch/pytorch GitHub issues (oncall:pt2 label, 9,277 issue pool, filtered to 6,810 user-facing).

Each test case has:
- **Clean question** — natural language, what a user would type to an agent
- **Full context** — actual issue body with error messages, stack traces, code snippets (first 1500 chars)
- **Source issue** — GitHub issue number + URL for ground truth resolution
- **Resolution status** — resolved (closed with fix) or unresolved (still open)
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

### Dimension 1: Coverage (manual annotation, one-time)

Does pytorch.org have content that addresses the **compile-specific** aspect of this question — regardless of whether search finds it?

| Label | Criteria |
|-------|----------|
| **Full** | pytorch.org has a page that directly addresses the compile-specific question |
| **Partial** | pytorch.org has compile-related content in the same area but doesn't address the specific question |
| **None** | No relevant compile-specific pytorch.org content exists |

**Key calibration rule — compile concept vs. eager concept:**

The question is whether the *concept itself* belongs to the compile world:

- **Compile concepts** (graph breaks, dynamic shapes, AOTInductor, compile cache, recompilation, Dynamo tracing, inductor backends): A page about these topics is a coverage match — the concept inherently lives in the compile world.
- **Eager concepts** (symmetric memory, DTensor, GRU, dataclasses, OpenMP, cross-entropy loss): A page about these topics is NOT a match unless it specifically discusses compile behavior. These are general PyTorch features; their eager-mode docs don't answer compile questions.

Example: User asks "symmetric memory breaks under torch.compile." symmetric_memory.html covers the eager API but never mentions compile → Coverage = None. But if a user asks "how to fix graph breaks," landing on a graph breaks page is a hit even without the word "torch.compile" — because graph breaks ARE a compile concept.

**Validated baseline (15-case sample, April 2026):**

| Coverage | Count | % |
|----------|-------|---|
| Full | 6 | 40% |
| Partial | 5 | 33% |
| None | 4 | 27% |

### Dimension 2: Discoverability (automated, cheap) — PRIMARY METRIC

For each test question, run a web search and classify by **topic relevance** (not content quality):

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | **Direct** | Official pytorch.org page is about this topic |
| 2 | **Tangential** | Official pytorch.org page is tangentially related |
| 1 | **Community** | No official docs; only GitHub issues or forums match the topic |
| 0 | **Missing** | No results match the topic |

**Rubric philosophy:** Keep scoring simple — judge whether search surfaces the right *page*, not whether the page contains a good *answer*. "Is this page about dynamic shapes?" is unambiguous. "Would this page fix the user's problem?" adds annotator disagreement without improving the discoverability measurement. Content quality is a downstream problem: if the page is found but thin, we can improve it.

**Priority order:** Discoverability first (can search find the right page?), then coverage (does the page exist?), then content quality (is the page good?). Fixing discoverability unblocks everything else.

**Search tool:** Three Pai external web search (Meta internal). Must be pinned for reproducibility — same API, same parameters, documented date.

**Current baseline (80 resolved cases, April 2026):**

| Score | Count | % |
|-------|-------|---|
| Direct (3) | 10 | 12.5% |
| Tangential (2) | 28 | 35.0% |
| Community (1) | ~35 | ~44% |
| Missing (0) | ~7 | ~9% |

**Primary metric: % of queries with Score 3 (Direct).** Target: 50%+ after Phase 1.

### Coverage × Discoverability Matrix

The key insight from the validation experiment: these two dimensions create a 2×2 that drives different actions.

| | Search Finds Docs | Search Misses |
|--|---|---|
| **Docs Exist** | ✅ Working — no action | Fix SEO, cross-linking, page titles |
| **Docs Don't Exist** | N/A | Write new documentation |

**Validated distribution (15-case sample):**
- No gap (both exist + findable): 27%
- Discoverability gap (docs exist, search misses): 13%
- Coverage gap (docs don't exist): 27%
- Both (partial docs, poorly discoverable): 33%

### Dimension 3: Source Attribution (automated, cheap)

Track WHERE the answer comes from:

| Source | Reliability | Current Frequency |
|--------|-------------|-------------------|
| Official pytorch.org docs | High (authoritative, versioned) | ~48% of queries |
| GitHub issues | Medium (specific but fragile, may be stale) | ~38% of queries |
| discuss.pytorch.org forums | Unreliable (rolling discussion, never audited) | ~25% of queries |
| Medium/blogs | Low (may be outdated, wrong, SEO-optimized) | ~31% of queries |
| Other (NVIDIA, HuggingFace, etc.) | Varies | ~10% of queries |

**Goal:** Shift agent reliance from community/blog sources to official docs.

### Dimension 4: Resolution Quality (semi-automated, medium cost)

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

## Two Evaluation Modes

### Mode A: Clean Question (retrieval-focused)

**Input:** Clean question only (e.g., "How do I diagnose why torch.compile is slower than eager?")
**What it tests:** Can an agent FIND relevant documentation?
**Measures:** Discoverability — does the right page appear in search results?
**Scoring:** Retrieval Quality (0-3) + Source Attribution

This is the simpler, cheaper evaluation. Run web searches, classify results. Already baselined on 80 resolved cases.

### Mode B: Full Context (end-to-end resolution)

**Input:** Full issue body — error messages, stack traces, code snippets, version info (first 1500 chars)
**What it tests:** Can an agent USE documentation to resolve a real problem?
**Measures:** Resolution quality — does the agent produce a correct, helpful answer?

This is the harder evaluation. Requires judging agent output quality, not just retrieval.

#### Scoring for resolved issues (J{n}-1 through J{n}-10):

The ground truth is the actual resolution from the GitHub issue thread. Score the agent's response against it:

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | **Resolved** | Agent's answer matches the actual resolution (or is equally correct) |
| 2 | **Partial** | Agent gives relevant guidance but misses the specific fix |
| 1 | **Directional** | Agent points to the right area but answer is too vague to act on |
| 0 | **Unhelpful** | Agent's answer doesn't help or is wrong |

#### Scoring for unresolved issues (J{n}-11 through J{n}-20):

No ground truth exists. The test is whether the agent is HONEST about uncertainty:

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | **Honest + Helpful** | Agent acknowledges the issue is open/unsolved, suggests workarounds or points to the right issue tracker |
| 2 | **Honest + Limited** | Agent says "I don't know" or "this may be a bug" — correct but not actionable |
| 1 | **Overconfident** | Agent gives a plausible-sounding answer that doesn't actually apply |
| 0 | **Hallucination** | Agent fabricates a confident, specific answer that is wrong (HACS L4 — negative value) |

**Key principle:** For unresolved issues, the BEST outcome is honesty (Score 3), not a fabricated answer. An agent that says "this appears to be an open bug, here's the issue link" is more useful than one that confidently suggests a wrong fix.

## How to Run

### Baseline (Before)

**Mode A (Retrieval):**
1. Run web search for all 160 clean questions → score discoverability (0-3)
2. Record source attribution for each
3. Annotate coverage (Full/Partial/None) for each — one-time manual pass

**Mode B (Full Context):**
1. Give agent each full-context issue → collect agent response
2. For resolved cases: score against ground truth resolution (0-3)
3. For unresolved cases: score honesty vs. hallucination (0-3)

### After Improvement (Phase 1, 2, 3)
1. Re-run identical searches/prompts after doc changes are deployed and indexed
2. Compare scores before/after
3. Delta = improvement attributable to documentation changes

### Controls
- **Same queries**: use identical test suite, don't modify questions
- **Same search tool**: pin to specific API (Three Pai external web search) with documented parameters
- **Model-independent**: this evaluates doc quality, not model quality — keep model constant or measure retrieval only
- **Timestamp snapshots**: search results change over time — record exact results and dates
- **Resolved/unresolved balance**: 50/50 split prevents optimizing for one type of answer

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
| `data/balanced_test_suite.json` | **Primary**: 160 test cases (10 resolved + 10 unresolved × 8 journeys) |
| `data/expanded_test_suite.json` | Previous 80-case suite (mostly resolved), used for retrieval baseline |
| `analysis/coverage_vs_discoverability.md` | Validation experiment: separating coverage from discoverability (15 cases) |
| `analysis/retrieval_analysis_report.md` | Full retrieval analysis with per-journey breakdown (80 cases) |
| `analysis/journey_issues_analysis.md` | Initial 40-issue extraction with methodology |
| `scripts/build_balanced_test_suite.py` | Builds 160-case balanced suite from issue pool |
| `scripts/build_expanded_suite.py` | Builds 80-case expanded suite |
| `scripts/extract_journey_issues.py` | Issue extraction and journey classification script |

## Open Design Questions

1. **Coverage annotation at scale**: The 15-case experiment was done manually. For all 160 cases, should we use an LLM-as-annotator (checking pytorch.org pages) or keep it manual? Manual is gold-standard but expensive; LLM is scalable but may miss nuance.

2. **Full-context evaluation tooling**: Mode B requires running an agent end-to-end on each case and judging the output. Options:
   - Manual expert scoring (expensive, gold standard)
   - LLM-as-judge with ground truth from resolved issues (scalable, needs calibration)
   - Hybrid: LLM scores, human reviews disagreements

3. **Journey weighting**: Equal weight across all 8 journeys. Issue volume is a biased sample — J1 (First Compile) is massively underreported because users who can't get started don't file issues, but it's the gateway journey. Issue counts reflect who persists, not who needs help.

4. **Temporal stability**: Search results change. How often to re-baseline? Suggestion: snapshot quarterly, always record exact date.

---

*Methodology validated via coverage vs. discoverability experiment on 2026-04-11. Core finding: the 2×2 matrix (coverage × discoverability) produces actionable signal that simple retrieval scoring cannot.*
