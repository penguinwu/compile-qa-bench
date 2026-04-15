# torch.compile Documentation: Where to Invest First

**Date:** 2026-04-15
**Source:** 160 support cases scored with/without docs (Track 1 unrestricted vs Track 2 doc-restricted)
**Bottom line:** 86% of real user questions cannot be adequately answered using official PyTorch documentation alone. This document identifies the highest-impact areas to fix.

---

## Top 5 Documentation Priorities

These are ranked by how many users they'd help and how severe the current gap is. Each priority includes what to create, why it matters, and a rough scope estimate.

### Priority 1: Correctness & Debugging Guide

**Impact:** Fixes the worst gap in the entire doc set. 20 cases, nearly total failure.

**The problem:** When users get wrong results from `torch.compile` (silent correctness bugs, NaN gradients, numerical divergence), the docs offer essentially nothing. 18 out of 20 cases produced identical template responses — the agent couldn't find any relevant page. Users asking "my compiled model gives different results than eager" get zero help from docs today.

**What to create:**
- A new page: **"Debugging Correctness Issues with torch.compile"**
- Content needed:
  - How to use `torch._dynamo.config.repro_level` and the minifier to isolate which operator produces wrong results
  - Common causes of numerical divergence (operator fusion changing precision, stride-dependent gradients, mutation semantics)
  - Step-by-step: "My compiled model gives wrong results — what do I do?"
  - Known correctness gotchas: class-level list mutations silently dropped, data-dependent control flow traced incorrectly, float8/mixed-precision interactions

**Why this is #1:** This journey has the highest combined quality drop (Act: 2.3→0.1, Diag: 2.9→1.2) and the most template responses (18/20). Users hitting correctness bugs are in the most urgent situation — wrong results with no error message — and the docs leave them completely stranded.

**Estimated scope:** 1 new page, ~2000-3000 words. Most of the content exists scattered across GitHub issues and internal knowledge — it needs to be consolidated and structured.

---

### Priority 2: Performance Optimization Cookbook

**Impact:** 20 cases, largest actionability drop (2.7 points). Users know what they want but can't find how to do it.

**The problem:** Users trying to make `torch.compile` faster (not just "does it work?") hit a wall. The docs describe what `max-autotune` and `reduce-overhead` are, but not how to actually tune performance — what to try when compilation is slow, when the generated code is slow, or when mode combinations interact badly. All 20 cases are doc-insufficient, and 16 lose their standalone fixes.

**What to create:**
- A new page: **"Optimizing Performance with torch.compile"**
- Content needed:
  - Decision tree: which mode to use when (`default` vs `reduce-overhead` vs `max-autotune`)
  - Common performance traps: mode combination pitfalls (max-autotune + reduce-overhead causing repeated CUDA graph instantiation), embedding lookup not optimized by inductor, padding degrading kernel performance
  - How inductor's kernel generation works at a high level (so users can understand profiler output)
  - Triton kernel tuning basics: what specialization does, when it helps/hurts
  - Workarounds for known slow paths (welford reduction for LayerNorm, log_softmax with padding)

**Why this is #2:** Every single case drops from Act 3 (standalone fix) to Act 0 (no actionable guidance). The fixes exist in the ecosystem — they're just not documented. This is pure ROI: write them down, and 20 cases go from useless to actionable.

**Estimated scope:** 1 new page, ~2500-3000 words. Heavy on code snippets and configuration examples.

---

### Priority 3: Custom Ops & Higher-Order Ops Guide (expand existing)

**Impact:** 20 cases, all doc-insufficient. Users building advanced integrations have no path forward.

**The problem:** Users writing custom operators (via `torch.library`), using higher-order ops (`torch.cond`, `while_loop`), or integrating FlexAttention all hit undocumented territory. The existing custom ops page covers the happy path but not error recovery, performance comparison between registration methods, or composition with CUDA graphs. 12 cases lose standalone fixes; 15 lose causal explanations.

**What to create:**
- Expand the existing custom ops page OR create a companion troubleshooting page
- Content needed:
  - `@torch.library.custom_op` vs `torch.Library.def` — performance differences and when to use each
  - FlexAttention: backward pass issues, dynamic shapes with BlockMask, precision interaction with `float32_matmul_precision`
  - `torch.cond` and `while_loop` limitations and workarounds (stateful modules, BatchNorm inside loops)
  - Debugging segfaults and illegal memory access in compiled custom ops
  - Third-party op compatibility (pytorch_cluster, complex tensors)

**Why this is #3:** This is the advanced user journey where people are doing real integration work. They're committed to `torch.compile` and hitting walls that have solutions — the solutions just aren't written down. These users are the most likely to file issues or abandon the tool.

**Estimated scope:** Expand 1 existing page + 1 new troubleshooting page, ~2000 words total.

---

### Priority 4: Compilation Time & Caching Guide (expand existing)

**Impact:** 20 cases, all but 2 doc-insufficient. Users can't reduce compile time without tribal knowledge.

**The problem:** Users whose models take 30-70+ seconds to compile can't find guidance on reducing compilation time. The docs mention compile caching exists but don't explain strategies: serializing compiled models, breaking deep models into pieces, understanding why loops explode compile time, or why optimizer compilation is slow. 13 cases lose standalone fixes.

**What to create:**
- Expand the existing compile caching page with a troubleshooting section
- Content needed:
  - "Compilation is too slow" decision tree: model too deep → chunk it; optimizer → reduce parameter count per trace; loops → restructure
  - Compile cache: how to serialize and reload, cross-process cache sharing (Ray, multiprocessing), cache invalidation
  - Why specific patterns cause slow compilation (loop unrolling, exponential graph growth with chained ops + gradients)
  - CPU-specific: vector ISA detection overhead, Windows caching issues

**Why this is #4:** Compilation time is often the first-contact frustration — users try `torch.compile`, it takes forever, and they give up. Diagnostic quality is actually decent (Diag drops only 0.6 points — docs explain *what* caching is), but actionability collapses (Act: 2.6→0.0) because users can't find *how to fix it*.

**Estimated scope:** Expand 1 existing page, add ~1500 words of troubleshooting content.

---

### Priority 5: Graph Breaks Troubleshooting Guide (expand existing)

**Impact:** 20 cases, mixed. Some docs exist (9/20 sufficient), but all 20 cases got template responses — suggesting the agent can find concept pages but not solutions.

**The problem:** This is an unusual pattern. The graph breaks concept is partially documented (highest doc-sufficiency rate at 45%), yet every single Track 2 response was a template. This means the docs explain *what* graph breaks are but don't help users *fix their specific graph break*. Users asking "how do I fix this graph break with DDP/dataclasses/flex_attention/SAC" get concept pages, not solutions. 13 cases lose standalone fixes.

**What to create:**
- A troubleshooting companion to the existing graph breaks page
- Content needed:
  - "I have a graph break — now what?" flowchart
  - Common graph break causes with specific fixes: DDP `_broadcast_coalesced`, dataclass fields, bound methods after PyTorch upgrade, Parameter subclasses
  - `torch.compiler.disable` gotchas (doesn't propagate to nested functions)
  - Graph break interaction with distributed (DDP, FSDP), optimizers (AdamW + LR scheduler), and activation checkpointing
  - `fullgraph=True` vs allowing graph breaks: when each is appropriate

**Why this is #5:** Graph breaks are the most-documented topic already (45% sufficient), so the marginal improvement per word written is lower than priorities 1-4. But the template response rate (100%) shows the existing docs aren't solving the actual user problems — they explain the concept without resolving specific cases.

**Estimated scope:** 1 new troubleshooting page, ~2000 words. Many fixes are one-liner workarounds that just need to be catalogued.

---

## Remaining Gaps (Lower Priority)

These journeys also have documentation gaps but are either less severe or partially covered:

| Journey | Cases | Doc Sufficient | Key Gap |
|---------|-------|---------------|---------|
| J6: Dynamic Shapes | 20 | 2/20 (10%) | Workarounds for data-dependent shapes, recompilation debugging, AMP interaction |
| J1: First Compile | 20 | 5/20 (25%) | Setup troubleshooting (Windows, multi-GPU, multiprocessing), integration patterns (DDP+AMP, Tensor Parallel) |
| J2: Performance Diagnosis | 20 | 4/20 (20%) | "Why is my compiled model not faster?" diagnostic guide, op support coverage |

These could be addressed after Priorities 1-5 or folded into the priority pages where they overlap (e.g., dynamic shapes troubleshooting could be a section within the Performance Optimization page).

---

## What Kind of Documentation Is Missing?

The gaps fall into three distinct types, each requiring different effort:

### Type A: Entire pages that don't exist (create new)
The agent found nothing relevant and returned boilerplate. This signals a topic the docs simply don't cover.
- **38 cases** across 2 journeys (J3 Correctness, J4 Graph Breaks) produced template responses
- **Fix:** Create new pages (Priorities 1, 2, 5 above)

### Type B: Mechanism explanations missing from existing pages (add depth)
The docs mention tools and concepts but don't explain *how things work internally*. The agent can say "use TORCH_LOGS" but not "what TORCH_LOGS will show you is that inductor's fusion pass merged your matmul with the subsequent add, changing the precision of the intermediate result."
- **36 cases** (22%) have mechanism-level gaps — Track 1 explains the mechanism, Track 2 can only point to diagnostic tools
- **Fix:** Add "how it works" sections to existing pages (Priorities 3, 4 above)

### Type C: Workarounds that exist but aren't documented (extract from issues)
The fix exists in GitHub issues, Stack Overflow, or internal knowledge. Track 1 (which has access to these) provides standalone fixes; Track 2 (docs only) cannot.
- **83 cases** (52%) lose standalone fixes when restricted to docs
- **Fix:** Systematically extract workarounds from GitHub issues into doc pages (all priorities above)

### A note on mechanism gaps

Some mechanism gaps are inherent to how torch.compile works. Many internal mechanisms (inductor fusion decisions, AOT autograd decompositions, Dynamo guard generation) are implementation details that change between releases. Documenting them at full depth would create maintenance burden and might mislead users into depending on internals.

**Recommended approach:** Document mechanisms at the *user-actionable* level. Users don't need to know every inductor pass, but they do need to know "if you see X symptom, the likely cause is Y, and the fix is Z." The correctness debugging guide (Priority 1) is the right level — symptom → cause → fix, without requiring users to understand compiler internals.

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Total cases evaluated | 160 |
| Cases where docs are insufficient | 138 (86%) |
| Mean actionability drop (T1→T2) | 2.18 points (0-3 scale) |
| Mean diagnostic quality drop | 0.96 points (0-3 scale) |
| Cases receiving template responses | 38 (24%) |
| Cases losing mechanism explanations | 36 (22%) |
| Cases losing standalone fixes | 83 (52%) |
| Fabrication in unrestricted responses | 21/160 (13%) |

---

## Appendix A: Journey-Level Data

### Score Distributions by Journey

| Journey | N | T1 Act | T2 Act | Act Drop | T1 Diag | T2 Diag | Diag Drop | Doc Suf | Templates | NM Gaps |
|---------|---|--------|--------|----------|---------|---------|-----------|---------|-----------|---------|
| J3: Correctness/Debugging | 20 | 2.3 | 0.1 | 2.2 | 2.9 | 1.2 | 1.7 | 0/20 | 18 | 16 |
| J5: Performance Optimization | 20 | 2.8 | 0.1 | 2.7 | 2.9 | 1.8 | 1.1 | 0/20 | 0 | 3 |
| J8: Custom/Higher-Order Ops | 20 | 2.6 | 0.0 | 2.6 | 2.9 | 2.0 | 0.9 | 0/20 | 0 | 3 |
| J7: Compile-Time Performance | 20 | 2.6 | 0.0 | 2.6 | 2.9 | 2.3 | 0.6 | 2/20 | 0 | 2 |
| J6: Dynamic Shapes | 20 | 2.5 | 0.3 | 2.2 | 3.0 | 2.1 | 0.8 | 2/20 | 0 | 1 |
| J1: First Compile | 20 | 2.6 | 0.8 | 1.9 | 3.0 | 2.2 | 0.8 | 5/20 | 0 | 5 |
| J4: Graph Breaks | 20 | 2.5 | 1.0 | 1.5 | 3.0 | 1.9 | 1.1 | 9/20 | 20 | 1 |
| J2: Performance Diagnosis | 20 | 2.2 | 0.7 | 1.6 | 2.9 | 2.1 | 0.8 | 4/20 | 0 | 5 |

### Column Definitions

- **T1/T2 Act:** Mean Actionability score (0-3). Track 1 = unrestricted, Track 2 = docs-only.
- **T1/T2 Diag:** Mean Diagnostic Quality score (0-3).
- **Doc Suf:** Cases where documentation was sufficient to produce comparable quality.
- **Templates:** Cases where the doc-restricted agent returned identical boilerplate (no relevant page found).
- **NM Gaps:** Cases where Track 1 names the mechanism but Track 2 cannot (docs lack mechanism-level info).

## Appendix B: Cross-Cutting Topic Frequency

Topics most frequently associated with high-gap cases (Act or Diag drop >= 2 points):

| Topic | Cases | Topic | Cases |
|-------|-------|-------|-------|
| dynamic shapes | 25 | flex_attention | 12 |
| inductor backend | 24 | minifier | 11 |
| recompilation | 16 | compilation time | 11 |
| backends | 15 | performance profiling | 10 |
| caching | 14 | custom operators | 10 |
| error messages | 14 | CUDA graphs | 9 |
| inductor | 14 | correctness debugging | 9 |
| higher-order ops | 14 | max-autotune | 7 |
| graph breaks | 13 | memory optimization | 7 |
| triton | 13 | operator fusion | 5 |

## Appendix C: Methodology

### Scoring Framework

Each of 160 cases was scored independently by two raters (Owl, Raven) on two tracks:
- **Track 1 (unrestricted):** Agent has access to all sources (docs, GitHub issues, source code, community knowledge)
- **Track 2 (doc-restricted):** Agent can only use official PyTorch documentation

Three dimensions were scored:
- **Actionability (Act, 0-3):** Can the user act on the response? (0=no guidance, 1=generic direction, 2=specific steps, 3=standalone fix)
- **Diagnostic Quality (Diag, 0-3):** Does the response explain what's wrong? (0=no diagnosis, 1=correct subsystem, 2=names mechanism, 3=full causal chain)
- **Fabrication (binary):** Does the response contain invented information?

### Inter-Rater Agreement

Scores were calibrated using 10 rules developed through systematic disagreement analysis. Post-calibration agreement (Cohen's quadratic weighted kappa):

| Dimension | Track 1 | Track 2 |
|-----------|---------|---------|
| Actionability | 0.900 | 0.945 |
| Diagnostic Quality | 0.918 | 0.925 |

All dimensions exceed the 0.80 threshold for "almost perfect" agreement.

### Key Interpretation Rule

For Track 2, `names_mechanism=false` signals a **documentation gap**, not a response quality failure. When the official docs only provide diagnostic tool references (e.g., "use TORCH_LOGS") without explaining the underlying mechanism, the doc-restricted agent literally cannot name what went wrong — the information doesn't exist in the docs. This is by design: the gap analysis measures what's *missing from docs*, not what the agent did wrong.

### Doc Sufficiency Assessment

A case is "doc-sufficient" when Track 2 scores are within 1 point of Track 1 on both Act and Diag. This indicates the docs contain enough information to produce a comparable response, even if not identical.

## Appendix D: Detailed Per-Journey Case Lists

### J3: Correctness & Debugging — All 20 Cases

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Template | NM Gap |
|------|---------------------|-----------|------------|----------|--------|
| J3-1 | torch.compile produces different numerical output | 2→0 | 3→1 | Yes | Yes |
| J3-2 | conv2d + interpolate wrong gradients under compile | 2→0 | 3→1 | No | Yes |
| J3-3 | Compiled flex_attention different accuracy vs eager | 2→0 | 3→2 | No | No |
| J3-4 | RMS norm NaNs with float8 and rowwise scales | 2→0 | 3→2 | Yes | No |
| J3-5 | Different results every run, even with same seed | 3→0 | 2→1 | No | Yes |
| J3-6 | compose compile with torch.func.grad, silent wrong result | 2→0 | 3→1 | Yes | Yes |
| J3-7 | dstack+reciprocal wrong results under compile | 3→0 | 3→1 | Yes | Yes |
| J3-8 | NaN gradients with GQA + SDPA backward pass | 3→0 | 3→2 | Yes | No |
| J3-9 | How to benchmark compile accuracy across models | 1→0 | 2→1 | Yes | Yes |
| J3-10 | Segformer accuracy regressed with AOT eager in 2.5 | 2→0 | 3→1 | Yes | Yes |
| J3-11 | 4.7% relative error in Conv2d on CPU | 2→1 | 3→1 | Yes | Yes |
| J3-12 | Significant precision errors, isolate which op | 3→0 | 3→1 | Yes | Yes |
| J3-13 | Breaks reproducibility even with manual seeds | 2→0 | 3→1 | Yes | Yes |
| J3-14 | Fails on macOS with 'omp.h file not found' | 3→0 | 3→1 | Yes | Yes |
| J3-15 | Inductor epilogue fusion wrong results with mutations | 2→0 | 3→1 | Yes | Yes |
| J3-16 | Data-dependent control flow traced incorrectly | 2→0 | 3→1 | Yes | Yes |
| J3-17 | Silently drops mutations to class-level list attrs | 3→0 | 3→1 | Yes | Yes |
| J3-18 | AOT autograd stride-dependent gradient regeneration | 2→0 | 3→1 | Yes | Yes |
| J3-19 | conv_stride_constraints fails on ROCm | 2→0 | 3→1 | Yes | Yes |
| J3-20 | NaN values with reduce-overhead/max-autotune modes | 3→1 | 3→2 | Yes | No |

### J5: Performance Optimization — All 20 Cases

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | NM Gap |
|------|---------------------|-----------|------------|--------|
| J5-1 | max-autotune lowers precision? | 3→0 | 3→2 | No |
| J5-2 | reduce-overhead mode 7x slower after upgrade | 3→0 | 3→2 | No |
| J5-3 | FlexAttention bad perf with causal+upper mask | 3→0 | 3→2 | No |
| J5-4 | KeyError 'dim' from UnbindCatRemover | 3→0 | 3→1 | Yes |
| J5-5 | torch.compile breaks multi-GPU DistributedDataLoader | 2→0 | 2→2 | No |
| J5-6 | Misaligned address errors with max-autotune | 3→0 | 3→1 | Yes |
| J5-7 | Fused linear + cross-entropy loss? | 3→0 | 3→2 | No |
| J5-8 | Make torch.compile work with vLLM | 2→0 | 3→2 | No |
| J5-9 | Inductor doesn't work on Windows | 3→0 | 3→1 | Yes |
| J5-10 | Compile optimizer.step() fails 'too many arguments' | 3→0 | 3→2 | No |
| J5-11 | max-autotune+reduce-overhead slower than default | 3→0 | 3→1 | No |
| J5-12 | Shared memory error with flex_attention on RTX 4090 | 3→0 | 3→2 | No |
| J5-13 | nn.Embedding forward slower than eager | 3→0 | 3→2 | No |
| J5-14 | Triton kernel slower with more specialization | 3→0 | 3→2 | No |
| J5-15 | Custom softmax Triton kernel errors with compile | 3→0 | 3→2 | No |
| J5-16 | Why is max-autotune so much slower for small models? | 2→0 | 2→2 | No |
| J5-17 | test_select_algorithm fails for conv in inductor | 3→0 | 3→2 | No |
| J5-18 | log_softmax kernel worse with padding | 3→0 | 3→2 | No |
| J5-19 | welford reduction makes LayerNorm slower | 3→0 | 3→2 | No |
| J5-20 | What profiling tools to understand inductor output? | 2→0 | 3→2 | No |

### J8: Custom & Higher-Order Ops — All 20 Cases

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | NM Gap |
|------|---------------------|-----------|------------|--------|
| J8-1 | Create custom op for compile/dynamo/inductor | 3→0 | 3→2 | No |
| J8-2 | Compiled flex_attention segfaults backward pass | 3→0 | 3→2 | No |
| J8-3 | BatchNorm2d inside while_loop with compile | 3→0 | 3→2 | No |
| J8-4 | Custom C++ op with torch.library wrong results | 3→0 | 3→2 | No |
| J8-5 | flex_attention dynamic shapes with BlockMask | 2→0 | 3→3 | No |
| J8-6 | FlexAttention deviates from SDPA with float32_matmul | 3→0 | 3→3 | No |
| J8-7 | pytorch_cluster radius function fails with dynamo | 3→0 | 3→2 | Yes |
| J8-8 | torch.cond errors and limitations | 3→0 | 3→2 | No |
| J8-9 | Complex-valued tensors fail with compile | 3→0 | 3→2 | Yes |
| J8-10 | Triton autotuning 'invalid argument' CUDA error | 3→0 | 3→2 | No |
| J8-11 | Custom op illegal memory access with compile | 2→0 | 3→2 | No |
| J8-12 | FlexAttention illegal memory access | 2→0 | 3→2 | No |
| J8-13 | compile + CUDA graphs fails multithreaded inference | 3→0 | 3→2 | No |
| J8-14 | Export model uses torch.library custom op | 2→0 | 2→2 | No |
| J8-15 | Parallel associative scans support? | 2→0 | 3→1 | Yes |
| J8-16 | Symmetric memory (NVLink) breaks compilation | 2→0 | 3→2 | No |
| J8-17 | @custom_op slower than Library.def registration | 3→0 | 3→2 | No |
| J8-18 | Custom reduction ops slower with C++ inductor on CPU | 2→0 | 3→2 | No |
| J8-19 | Flex Attention crashes LLVM error after Triton pin | 3→0 | 3→2 | No |
| J8-20 | Flex_attention wrong gradients in backward | 2→0 | 3→2 | No |
