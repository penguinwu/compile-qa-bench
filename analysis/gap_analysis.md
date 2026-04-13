# Gap Analysis: torch.compile Documentation & Agent Capabilities

**Date:** 2026-04-13
**Owner:** Rocky
**Data sources:** Track 1 (unrestricted), Track 3 (source-grounded), 160 cases, independent scoring by Raven

---

## Executive Summary

Agents correctly identify the right subsystem in ~90% of cases but miss the specific fix in 72.5%. Three root causes:

1. **Documentation gaps** (27% of cases have zero coverage) — agents can't find what doesn't exist
2. **Fabrication** (13% of cases) — agents invent configs/APIs when they can't verify; source access cuts this by 57%
3. **Skill gaps** — agents misdiagnose or give generic advice even when docs exist

The highest-leverage improvement targets are J5 (Performance Optimization) and J7 (Compile-Time Performance).

---

## 1. Documentation Coverage Gaps

27% of cases (43/160) have **zero** pytorch.org coverage for the compile-specific question.

| Journey | Full | Partial | None | % None |
|---------|------|---------|------|--------|
| J1: First Compile | 5 | 10 | 5 | 25% |
| J2: Perf Diagnosis | 5 | 10 | 5 | 25% |
| J3: Correctness | 0 | 12 | 8 | **40%** |
| J4: Graph Breaks | 2 | 14 | 4 | 20% |
| J5: Perf Optimization | 3 | 9 | 8 | **40%** |
| J6: Dynamic Shapes | 4 | 13 | 3 | 15% |
| J7: Compile-Time | 1 | 14 | 5 | 25% |
| J8: Custom Ops | 5 | 10 | 5 | 25% |

**Worst coverage:** J3 (Correctness) and J5 (Performance Optimization) at 40% None. These are advanced topics where users need the most help but docs provide the least.

**Key insight:** Only 16% of cases have Full coverage. The majority (58%) have Partial — docs mention the topic but don't address the specific question. This is the "almost helpful" gap.

---

## 2. Agent Quality by Journey

| Journey | Mean | S0 | S1 | S2 | S3 | Low-score rate |
|---------|------|----|----|----|----|----|
| J5: Perf Optimization | **1.60** | 0 | 8 | 12 | 0 | **40%** |
| J7: Compile-Time | 1.80 | 0 | 5 | 14 | 1 | 25% |
| J2: Perf Diagnosis | 1.85 | 0 | 4 | 15 | 1 | 20% |
| J6: Dynamic Shapes | 1.90 | 0 | 2 | 18 | 0 | 10% |
| J8: Custom Ops | 1.90 | 2 | 0 | 16 | 2 | 10% |
| J3: Correctness | 1.95 | 0 | 3 | 15 | 2 | 15% |
| J4: Graph Breaks | 2.00 | 0 | 3 | 14 | 3 | 15% |
| J1: First Compile | **2.10** | 0 | 3 | 12 | 5 | 15% |

**J5 is the worst-performing journey** — 40% of cases score 0-1, zero score-3 cases. Performance optimization requires deep knowledge of inductor internals (config flags, autotuning, kernel fusion) that isn't documented and is heavily fabricated.

**J1 is the best-performing journey** — highest mean (2.10), most score-3 cases (5). First Compile has the best documentation coverage.

---

## 3. Coverage Predicts Quality

| Coverage | Mean Score | n | Low-score rate |
|----------|-----------|---|----------------|
| Full | 1.96 | 25 | 16% |
| Partial | 1.95 | 92 | 15% |
| **None** | **1.72** | 43 | **28%** |

Coverage=None cases are 1.8x more likely to get a low score. Closing documentation gaps directly improves agent quality.

---

## 4. Fabrication Analysis

### Track 1 vs Track 3 Comparison

| Metric | Track 1 (Unrestricted) | Track 3 (Source-Grounded) |
|--------|----------------------|--------------------------|
| Total claims | 210 | 237 |
| Verified | 188 (89.5%) | 227 (95.8%) |
| Fabricated | 22 (10.5%) | 10 (4.2%) |
| Cases w/ fabrication | 21/160 (13.1%) | 9/160 (5.6%) |

### Fabrication Hotspots by Journey

| Journey | T1 cases | T3 cases | Reduction |
|---------|----------|----------|-----------|
| J5: Perf Optimization | **7/20** | 2/20 | 71% |
| J1: First Compile | 3/20 | 0/20 | 100% |
| J4: Graph Breaks | 3/20 | 1/20 | 67% |
| J8: Custom Ops | 3/20 | 2/20 | 33% |

**J5 is the fabrication leader** — 35% of J5 cases have fabricated claims in Track 1. This is directly caused by the documentation gap: when agents can't find real configs for performance tuning, they invent plausible-sounding ones.

### What Gets Fabricated

**Track 1 fabrication types:** triton_subconfig (6), env_var (3), import_claim (3), dynamo_config (2), cpp_subconfig (2), config_assignment (2), decorator_claim (2), functorch_config (1), distributed_optim_api (1)

**Track 3 residual fabrication:** env_var (4), inductor_config (4) — concentrated in speculative flags where agents hedged but still included unverified claims.

---

## 5. Failure Pattern Taxonomy

30 cases scored 0-1 by Raven. They cluster into 4 failure types:

### A. Fabricated Configs/APIs (12 cases)

Agent invents plausible but non-existent configuration flags or API methods.

| Case | Fabricated Claim | What's Real |
|------|-----------------|-------------|
| J5-7 | `config.fuse_cross_entropy_linear` | No such config |
| J5-10 | `config.split_large_kernels` | No such config |
| J5-19 | `config.triton.use_welford_reduction` | No such subconfig |
| J7-14 | `config.cpp.vec_isa` | Real name is `cpp.vec_isa_ok` |
| J4-8 | `SAC_checkpoint` API | No such API |
| J5-3 | `torch.nn.attention.create_mask` | Uses `score_mod`/`block_mask` |

**Root cause:** Documentation gap — these configs don't exist in docs because they don't exist in source. Agents extrapolate from naming patterns.

### B. Wrong Diagnosis (8 cases)

Agent misidentifies the root cause, leading to irrelevant advice.

| Case | Agent Claims | Actually |
|------|-------------|----------|
| J1-12 | autograd.grad not supported in Dynamo | It IS registered and supported |
| J8-14 | No `torch.scan` exists | `torch._higher_order_ops.scan` is implemented |
| J8-15 | No built-in parallel scan | `associative_scan` exists |
| J1-16 | Complex dtypes missing from DTYPE_TO_CPP | They ARE all mapped |
| J7-1 | `inline_inbuilt_nn_modules=False` as fix | Deprecated, always True |

**Root cause:** Model knowledge gap — the model's training data predates these features. Source access (Track 3) eliminates most of these.

### C. Generic/Vague Advice (7 cases)

Agent gives standard debugging methodology without addressing the specific issue.

| Case | Pattern |
|------|---------|
| J2-8 | "Profile with torch.profiler" for FlexAttention backward — doesn't ID root cause |
| J3-3 | Generic precision debugging for a specific resolved bug |
| J5-5 | "Bisect your code" for a specific regression |
| J5-17 | "Check CUDA version" for a specific test failure |

**Root cause:** Skill gap — the agent doesn't have deep enough understanding of the subsystem to diagnose the specific issue.

### D. Deprecated/Stale Recommendations (3 cases)

Agent recommends approaches that were valid in older versions but are now deprecated.

| Case | Recommendation | Status |
|------|---------------|--------|
| J7-1 | `inline_inbuilt_nn_modules=False` | Deprecated, always True |
| J2-15 | `torch.nn.functional.sdp_kernel()` | Deprecated context manager |

**Root cause:** Model training data staleness + docs not clearly marking deprecations.

---

## 6. High-Priority Documentation Targets

12 cases have **both** Coverage=None and Score 0-1, representing the intersection of "no docs" and "agent fails":

| Case | Journey | Issue |
|------|---------|-------|
| J5-5 | Perf Optimization | Regression debugging — no doc guidance |
| J5-7 | Perf Optimization | cross_entropy fusion — fabricated config |
| J5-17 | Perf Optimization | Test failure debugging — no specific guidance |
| J5-19 | Perf Optimization | Welford reduction — fabricated config |
| J7-14 | Compile-Time | vec_isa config — wrong name |
| J8-14 | Custom Ops | torch.scan — agent doesn't know it exists |
| J8-15 | Custom Ops | associative_scan — agent doesn't know it exists |
| J6-9 | Dynamic Shapes | autocast tracing — wrong diagnosis |
| J2-7 | Perf Diagnosis | GIL/Triton interaction — speculative |
| J2-19 | Perf Diagnosis | CPU benchmarks — vague |
| J3-19 | Correctness | ROCm conv debugging — generic |
| J1-16 | First Compile | Complex dtype support — wrong diagnosis |

**Top 3 actionable doc improvements:**
1. **Higher-order ops documentation** — `torch.scan`, `associative_scan` exist but agents (and likely users) don't know about them
2. **Performance tuning config reference** — exhaustive list of real `config.triton.*` and `config.cpp.*` options with descriptions, preventing fabrication
3. **Deprecation notices** — clear "deprecated since X, use Y instead" for `inline_inbuilt_nn_modules`, `sdp_kernel`, etc.

---

## 7. Track 3 Implications

Source access reduces fabrication by 55% but doesn't improve diagnostic accuracy for cases where the issue is semantic understanding, not factual accuracy. This suggests two complementary strategies:

1. **For fabrication reduction:** Better documentation of configs and APIs (what exists, what doesn't)
2. **For diagnostic improvement:** Worked examples and troubleshooting decision trees in docs

The 4.2% residual fabrication rate in Track 3 represents an agent behavior issue (speculative guessing) rather than an information access issue — agents include unverified claims even when they could verify them.

---

## 8. Doc-Restricted Findings (Raven IAA)

This section incorporates Raven's independent doc-restricted scoring (160 cases) and compares it with Rocky's scores on the same cases to identify where documentation improvements would have the most impact. Raven applies a stricter rubric (user-actionability focus, no credit for gap acknowledgment), providing a conservative floor estimate of doc quality.

### 8.1 Per-Journey Breakdown

| Journey | Raven Mean | Rocky Mean | Delta (R-V) | Unrestricted Mean | Doc-Restriction Drop |
|---------|-----------|-----------|-------------|-------------------|---------------------|
| J3: Correctness | **1.00** | 1.50 | +0.50 | 2.75 | **-1.75** |
| J4: Graph Breaks | **1.00** | 1.95 | +0.95 | 2.90 | **-1.90** |
| J8: Custom Ops | 1.10 | 1.80 | +0.70 | 2.60 | -1.50 |
| J5: Perf Optimization | 1.15 | 1.15 | +0.00 | 2.50 | -1.35 |
| J7: Compile-Time | 1.15 | 1.85 | +0.70 | 2.45 | -1.30 |
| J1: First Compile | 1.30 | 1.90 | +0.60 | 2.95 | -1.65 |
| J6: Dynamic Shapes | 1.30 | 1.75 | +0.45 | 2.75 | -1.45 |
| J2: Perf Diagnosis | 1.35 | 1.90 | +0.55 | 2.50 | -1.15 |
| **Overall** | **1.17** | **1.73** | **+0.56** | **2.67** | **-1.51** |

**Raven score distribution:** S0=0 (0%), S1=135 (84%), S2=23 (14%), S3=2 (1%). Raven never assigns 0 and rarely assigns 3, concentrating on 1 ("gap identified, no actionable guidance").

**Key observations:**

- **J3 and J4 are complete doc failures** — Raven gives every single case in both journeys a score of 1. Zero cases in Correctness or Graph Breaks produce actionable guidance from docs alone. J3 responses are boilerplate templates; J4 responses are cookie-cutter graph break advice.
- **J5 is the only journey where Rocky and Raven agree** (both 1.15). Both scorers recognize performance optimization docs as inadequate. This is the ground truth: when the docs truly fail, even a lenient scorer can't find value.
- **The unrestricted-to-doc-restricted drop averages 1.51 points** (on a 0-3 scale). This means the agent loses more than half its resolution capability when restricted to official docs. J4 has the largest drop (1.90) — agents resolve graph breaks well with general knowledge but docs provide almost nothing.
- **J1 has the largest unrestricted score (2.95) but still drops to 1.30** when doc-restricted. First Compile is well-served by general LLM knowledge but poorly served by pytorch.org specifically.

### 8.2 Gap Type Classification

Each of the 160 cases is classified into one of four gap types based on the intersection of documentation coverage (Mode A), discoverability, and doc-restricted quality (Raven score):

| Gap Type | Count | % | Raven Mean | Unrestricted Mean | Drop | Definition |
|----------|------:|----:|-----------|-------------------|------|------------|
| Documentation gap | 48 | 30.0% | 1.00 | 2.69 | -1.69 | Docs mention the topic but lack the specific content needed to resolve the issue (Partial coverage, discoverable) |
| Coverage gap | 41 | 25.6% | 1.00 | 2.63 | -1.63 | Topic not covered at all on pytorch.org (None coverage) |
| Discoverability gap | 36 | 22.5% | 1.00 | 2.72 | -1.72 | Docs exist (Partial or Full coverage) but search cannot surface them (discoverability <= 1) |
| Skill gap | 10 | 6.2% | 1.00 | 2.60 | -1.60 | Docs have Full coverage and are discoverable, but agent gives boilerplate instead of engaging with content |
| Adequate | 25 | 15.6% | 2.08 | 2.68 | -0.60 | Agent produces actionable guidance from docs alone (Raven score >= 2) |

**Only 25 of 160 cases (15.6%) produce adequate doc-restricted responses.** The remaining 135 cases (84.4%) represent some form of documentation failure.

#### Gap type by journey:

| Journey | Coverage | Doc Gap | Discoverability | Skill | Adequate |
|---------|:--------:|:-------:|:---------------:|:-----:|:--------:|
| J1: First Compile | 5 | 5 | 4 | 1 | 5 |
| J2: Perf Diagnosis | 5 | 4 | 3 | 2 | 6 |
| J3: Correctness | 8 | **10** | 2 | 0 | **0** |
| J4: Graph Breaks | 4 | **10** | 4 | 2 | **0** |
| J5: Perf Optimization | **8** | 3 | 5 | 1 | 3 |
| J6: Dynamic Shapes | 3 | 6 | 3 | 2 | 6 |
| J7: Compile-Time | 5 | 6 | 5 | 1 | 3 |
| J8: Custom Ops | 3 | 4 | **10** | 1 | 2 |

**Pattern highlights:**
- **J3 and J4** have zero adequate cases and are dominated by documentation gaps (10 each) — the docs exist in partial form but never go deep enough to help.
- **J5** has the most coverage gaps (8) — performance optimization topics simply don't exist on pytorch.org.
- **J8** has the most discoverability gaps (10) — custom ops docs exist but agents/search can't find them. This is the easiest gap type to fix (improve SEO, cross-linking, and doc titles).

### 8.3 Coverage Predicts Doc-Restricted Quality

| Coverage Level | n | Raven Mean | % Score >= 2 | Unrestricted Mean |
|----------------|---|-----------|-------------|-------------------|
| Full | 25 | 1.52 | 44% | 2.68 |
| Partial | 92 | 1.13 | 13% | 2.72 |
| None | 43 | 1.05 | 5% | 2.63 |

Full coverage cases are **9x more likely** to score >= 2 than None-coverage cases (44% vs 5%). But even Full coverage only reaches 44% adequacy — meaning 56% of cases with Full coverage still fail in the doc-restricted evaluation, driven by skill gaps and template responses.

### 8.4 The "Documentation Depth" Problem

58 cases have Partial-or-Full coverage AND discoverability >= 2, yet Raven still scores them as 1. These are the **documentation depth gaps**: the docs exist, the agent can find them, but the content doesn't go deep enough to help with the specific issue.

Top patterns in these 58 cases:

| Pattern | Count | Journeys | Issue |
|---------|------:|----------|-------|
| Boilerplate template response | 22 | J3, J4 | Agent finds general docs but produces identical cookie-cutter responses for every case in the journey |
| "Gap identified, no guidance" | 18 | J1, J2, J6, J7 | Agent correctly reports the doc doesn't cover the specific question |
| Partial coverage insufficient | 12 | J5, J6, J7, J8 | Docs mention the topic area but not the specific config/API/interaction |
| Skill gap (full docs ignored) | 6 | J2, J4, J6, J8 | Full coverage exists but agent doesn't extract the relevant information |

**This is the highest-leverage doc improvement category.** These 58 cases already have docs and discoverability — they just need deeper, more specific content. Deepening existing docs is cheaper than writing new docs from scratch.

### 8.5 Priority Ranking: Doc Improvement Targets

Ranked by: (number of affected cases) x (severity of doc-restriction drop) x (feasibility of fix).

| Rank | Target | Cases | Gap Type | Drop | Action |
|------|--------|------:|----------|------|--------|
| **1** | **J3: Correctness debugging guide** | 20 | Documentation gap (10), Coverage gap (8), Discoverability (2) | -1.75 | Add compile-specific correctness debugging: minifier usage, repro_level, NaN tracing, numerical accuracy. Every J3 case gets boilerplate today. |
| **2** | **J4: Graph break resolution cookbook** | 20 | Documentation gap (10), Coverage gap (4), Discoverability (4), Skill (2) | -1.90 | Transform the existing graph break page from "how to detect" to "how to fix": specific patterns (data-dependent control flow, unsupported ops, third-party libraries) with worked solutions. |
| **3** | **J8: Custom ops/advanced features discoverability** | 18 | Discoverability gap (10), Documentation gap (4), Coverage gap (3), Skill (1) | -1.50 | Improve findability of torch.library, FlexAttention, control flow ops, higher-order ops. Fix titles, add cross-links, create a unified "Advanced Features" landing page. |
| **4** | **J5: Performance tuning config reference** | 17 | Coverage gap (8), Discoverability (5), Documentation gap (3), Skill (1) | -1.35 | Create exhaustive config reference for inductor (`config.triton.*`, `config.cpp.*`, mode combinations). This directly prevents fabrication (Section 4 shows J5 is the fabrication leader at 35%). |
| **5** | **J7: Compilation time troubleshooting** | 17 | Documentation gap (6), Coverage gap (5), Discoverability (5), Skill (1) | -1.30 | Add compilation time diagnosis: AOTAutograd costs, cache behavior, recompilation triggers, regional compilation guidance. |
| **6** | **J6: Dynamic shapes interaction guide** | 14 | Documentation gap (6), Coverage gap (3), Discoverability (3), Skill (2) | -1.45 | Deepen dynamic shapes docs: guard system internals, mark_dynamic edge cases, framework-specific patterns (DeepSpeed, PyG, speech models). |
| **7** | **J1: Getting started completeness** | 15 | Documentation gap (5), Coverage gap (5), Discoverability (4), Skill (1) | -1.65 | Fill setup gaps: C++ compiler requirements, Windows support, multiprocessing, checkpoint interaction, tensor parallel. |
| **8** | **J2: Performance diagnosis methodology** | 14 | Coverage gap (5), Documentation gap (4), Discoverability (3), Skill (2) | -1.15 | Add structured debugging methodology: version regression bisection, operator coverage status, flex_attention profiling, XPU support status. |

### 8.6 Key Finding: What Doc-Restricted vs Unrestricted Tells Us

The doc-restricted evaluation reveals a stark reality: **the unrestricted agent scores 2.67 mean; doc-restricted scores 1.17 mean — a 56% quality loss.** Of 160 cases, 134 (84%) are resolved when unrestricted (score >= 2) but fail when doc-restricted (score <= 1).

This 134-case gap breaks down by coverage:

| Coverage | Cases in Gap | Interpretation |
|----------|-------------|----------------|
| Partial | 80 (60%) | Docs *almost* help — they mention the topic but don't go deep enough. **This is the biggest opportunity.** Deepening 80 existing partial docs is more tractable than creating 40 new ones. |
| None | 40 (30%) | Topics not on pytorch.org at all. Agents succeed with general knowledge (GitHub, forums, training data) but docs have zero coverage. Requires new documentation. |
| Full | 14 (10%) | Docs fully cover the topic but the agent still can't extract actionable guidance. This is a skill/retrieval problem, not a doc problem. Improvements here require better doc structure (decision trees, worked examples) rather than more content. |

**The strategic conclusion:** Documentation improvement should focus on **deepening the 80 Partial-coverage cases** before creating new docs for Coverage=None cases. The ROI is higher because:

1. The doc infrastructure already exists (pages, URLs, search indexing)
2. The agent already finds these docs (discoverability is not the bottleneck)
3. The gap is depth, not breadth — adding specific configs, worked examples, and troubleshooting steps to existing pages
4. Partial-coverage cases have the largest unrestricted-to-restricted drop (-1.69 mean), meaning the information IS available elsewhere — it just needs to be added to official docs

**For Beaver's doc work, the priority order is:**

1. **Deepen J3/J4 existing docs** — 20 cases each, currently 100% boilerplate responses. Add correctness debugging guide and graph break resolution cookbook.
2. **Fix J8 discoverability** — 10 cases where docs exist but can't be found. Cheapest fix: better titles, cross-links, landing page.
3. **Create J5 config reference** — 8 coverage-gap cases where content doesn't exist. Prevents fabrication.
4. **Expand J7 compilation time docs** — 5 coverage + 6 documentation gaps. Add AOTAutograd costs, cache behavior, regional compilation.
5. **Fill J1 setup gaps** — 5 coverage gaps for first-time users. High visibility, moderate effort.
