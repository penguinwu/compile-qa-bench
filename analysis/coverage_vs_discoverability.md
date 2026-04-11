# Coverage vs. Discoverability Experiment

**Date:** 2026-04-11
**Purpose:** Validate that the evaluation methodology produces actionable signal by separating two distinct failure modes: documentation doesn't exist (coverage gap) vs. documentation exists but search doesn't find it (discoverability gap).

**Method:** For 15 sample cases across all 8 journeys (mix of search-hit and search-miss from baseline), manually checked whether pytorch.org has relevant content by browsing known doc pages directly — independent of web search ranking.

---

## Known pytorch.org Doc Pages Checked

| Page | URL |
|------|-----|
| torch.compile Tutorial | docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html |
| torch.compile End-to-End | docs.pytorch.org/tutorials/intermediate/torch_compile_full_example.html |
| Troubleshooting | docs.pytorch.org/docs/stable/torch.compiler_troubleshooting.html |
| Profiling torch.compile | docs.pytorch.org/docs/stable/torch.compiler_profiling_torch_compile.html |
| Caching Tutorial | docs.pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html |
| Caching Configuration | docs.pytorch.org/tutorials/recipes/torch_compile_caching_configuration_tutorial.html |
| Regional Compilation | docs.pytorch.org/tutorials/recipes/regional_compilation.html |
| Dynamic Shapes | docs.pytorch.org/docs/stable/torch.compiler_dynamic_shapes.html |
| Dynamic Shapes Core Concepts | docs.pytorch.org/docs/stable/user_guide/torch_compiler/compile/dynamic_shapes_core_concepts.html |
| Custom Backends | docs.pytorch.org/docs/stable/torch.compiler_custom_backends.html |
| torch.compiler API Reference | docs.pytorch.org/docs/stable/torch.compiler_api.html |
| torch.library | docs.pytorch.org/docs/stable/library.html |
| Custom Python Operators | docs.pytorch.org/tutorials/advanced/python_custom_ops.html |
| Performance Tuning Guide | docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html |
| Numerical Accuracy | docs.pytorch.org/docs/stable/notes/numerical_accuracy.html |
| DDP Notes | docs.pytorch.org/docs/stable/notes/ddp.html |
| Dynamo Overview | docs.pytorch.org/docs/stable/torch.compiler_dynamo_overview.html |

---

## Results

| Case | Question Summary | Coverage? | Search Found? | Gap Type |
|------|-----------------|-----------|---------------|----------|
| J1-2 | Change backend compiler | ✅ YES — Custom Backends page + API ref | ✅ YES | **None** |
| J1-8 | torch.compile + multi-GPU device placement | ❌ NO — no compile+device docs | ❌ NO | **Coverage** |
| J2-1 | Compiled model slower than eager, how to diagnose | ✅ YES — Profiling page exists | ❌ NO | **Discoverability** |
| J2-7 | Zero speedup on attention model | ⚠️ PARTIAL — Profiling page is generic | ⚠️ TANGENTIAL | **Both** |
| J3-1 | Different numerical output vs eager | ⚠️ PARTIAL — Troubleshooting mentions minifier; no compile-specific accuracy guide | ⚠️ TANGENTIAL | **Both** |
| J3-2 | Wrong gradients under compile | ⚠️ PARTIAL — Troubleshooting mentions minifier | ❌ NO | **Both (mostly discoverability)** |
| J4-2 | DDP + compile graph break | ❌ NO — no compile+DDP integration guide | ❌ NO | **Coverage** |
| J4-3 | __self__ mismatch graph break | ✅ YES — Troubleshooting page covers this | ✅ YES | **None** |
| J5-1 | What does max-autotune do, precision tradeoffs | ⚠️ PARTIAL — API ref lists modes briefly; no deep dive | ⚠️ TANGENTIAL | **Both** |
| J5-3 | max-autotune + reduce-overhead CUDA graph overhead | ❌ NO — no mode interaction docs | ❌ NO | **Coverage** |
| J6-2 | dynamic=True + empty tensor division by zero | ❌ NO — dynamic shapes docs don't cover edge cases | ❌ NO | **Coverage** |
| J6-7 | dynamic=True still fails with symbolic errors | ✅ YES — Dynamic Shapes + Core Concepts pages | ✅ YES | **None** |
| J7-1 | Cache enabled but cold start still slow | ✅ YES — Caching + Regional Compilation tutorials | ✅ YES | **None** |
| J7-5 | 34s compile time for simple for loop | ⚠️ PARTIAL — Troubleshooting mentions compile time; no loop-specific guidance | ❌ NO | **Both** |
| J8-1 | Create custom op for torch.compile | ✅ YES — torch.library + Custom Python Operators tutorial | ❌ NO | **Discoverability** |

---

## Summary

| Gap Type | Count | Cases | Fix |
|----------|-------|-------|-----|
| **None** (docs exist + search finds them) | 4 | J1-2, J4-3, J6-7, J7-1 | No action needed |
| **Discoverability** (docs exist, search misses) | 2 | J2-1, J8-1 | SEO, cross-linking, better page titles |
| **Coverage** (docs don't exist) | 4 | J1-8, J4-2, J5-3, J6-2 | Write new documentation |
| **Both** (partial docs, poorly discoverable) | 5 | J2-7, J3-1, J3-2, J5-1, J7-5 | Expand existing docs + improve discoverability |

### Distribution

```
No gap:          ████ 27%  (4/15)
Discoverability: ██   13%  (2/15)
Coverage:        ████ 27%  (4/15)
Both:            █████ 33% (5/15)
```

---

## Key Findings

### 1. The methodology produces real signal — coverage and discoverability are distinct problems

If we only measured "did search find official docs?" (our baseline retrieval score), cases J2-1 and J8-1 would look identical to J4-2 and J5-3 — all score 0 (no docs found). But the fix is completely different:

- **J2-1** (compile slower than eager): A profiling page *already exists* at pytorch.org — the problem is search doesn't surface it. Fix: better page title, cross-links from troubleshooting page.
- **J8-1** (custom ops with compile): torch.library docs + Custom Python Operators tutorial *already exist* — search just doesn't connect "custom op + torch.compile" to these pages. Fix: SEO, add "torch.compile" to page metadata.
- **J4-2** (DDP + compile): No documentation exists at all. Fix: write a DDP + compile integration guide.
- **J5-3** (mode interaction): No documentation exists. Fix: write a modes comparison / interaction guide.

**This distinction is the core validation.** Our methodology can differentiate between "write new docs" and "make existing docs findable" — two fundamentally different interventions with different costs and owners.

### 2. The "Both" category reveals the biggest improvement opportunity

5 of 15 cases (33%) have *partial* coverage that's *poorly discoverable*. These are pages that mention the topic briefly (e.g., troubleshooting page mentions the minifier) but don't go deep enough to resolve the specific question. These need:
- Expanded content on existing pages (cheaper than new pages)
- Better internal linking (e.g., troubleshooting → profiling page)
- More specific page titles and headers for search indexing

### 3. The troubleshooting page is confirmed as a "catch-all that catches nothing"

It appears as partial coverage for 4 of 5 "Both" cases (J2-7, J3-1, J3-2, J7-5). It mentions many topics superficially but resolves none deeply. This confirms the retrieval analysis finding — the troubleshooting page needs to be either:
- Split into topic-specific pages (graph breaks, accuracy, performance, compile time)
- Or expanded with deep sections that search can index individually

### 4. Baseline retrieval score correlates but doesn't conflate

| Retrieval Score | Coverage exists? | |
|----------------|-----------------|---|
| Score 3 (Direct) | Always YES | Search works when docs are good |
| Score 2 (Tangential) | Usually PARTIAL | Search finds the page but content is thin |
| Score 0 (Missing) | Mix of YES and NO | **This is the key ambiguity our experiment resolves** |

The experiment validates Raven's critique: Score 0 is ambiguous and needs the coverage annotation to be actionable.

---

## Implications for Methodology

### Must-do: Add coverage annotation to scoring

Each test case needs a manual (or thorough-agent) annotation:
- **Coverage: Full** — pytorch.org has a page that directly addresses this
- **Coverage: Partial** — pytorch.org mentions the topic but doesn't resolve the specific question
- **Coverage: None** — no relevant pytorch.org content exists

This creates a 2×2 matrix:

|  | Discoverable | Not Discoverable |
|--|-------------|-----------------|
| **Coverage exists** | Working (no action) | Fix search/SEO |
| **No coverage** | N/A | Write docs |

### Must-do: Pin the search tool

Per Raven's critique, "unrestricted web search" is underspecified. For reproducibility, we should pin to a specific search API (e.g., this experiment used Three Pai external web search). Document: API, parameters, date of search.

### Nice-to-have: Weight by journey volume

J4 (Graph Breaks, 2,053 issues) and J5 (Performance Optimization, 1,805 issues) have 3-6x more users than J2 (320) or J7 (366). Coverage gaps in high-volume journeys should be prioritized.

---

*Experiment run 2026-04-11. 15 cases sampled from 80-case expanded test suite. Search tool: Three Pai external web search (Meta internal). Manual coverage check against 17 known pytorch.org doc pages.*
