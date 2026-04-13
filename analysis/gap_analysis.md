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
