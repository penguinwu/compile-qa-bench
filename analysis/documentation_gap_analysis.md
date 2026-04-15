# Documentation Gap Analysis — torch.compile User Journeys

**Date:** 2026-04-15
**Method:** Cross-referencing Track 1 (unrestricted) vs Track 2 (doc-restricted) label scores
**Data:** 160 cases scored on Actionability (Act 0-3) and Diagnostic Quality (Diag 0-3)
**Scorer:** Owl (calibrated Track 1, Rules 3-5 applied to Track 2)

## Executive Summary

Of 160 torch.compile support cases, **138 (86%)** cannot be adequately addressed using official PyTorch documentation alone. Key findings:

- **Actionability collapse:** Mean Act score drops from 2.54 (Track 1) to 0.36 (Track 2) — a **2.18-point** average drop
- **Diagnostic depth loss:** Mean Diag score drops from 2.92 to 1.97 — a **0.96-point** average drop
- **38 cases (24%)** receive identical template responses (no case-specific content)
- **36 cases (22%)** lose mechanism-level information when restricted to docs (names_mechanism gap)
- **124 cases** lose causal chain explanations (why the issue occurs)
- **83 cases (52%)** lose standalone fixes

The mechanism gap is particularly significant: for many topics, official docs provide only diagnostic tool references (e.g., TORCH_LOGS, profiler) without explaining the underlying mechanisms. This means doc-restricted agents can point users to debugging tools but cannot name what went wrong — the docs literally don't contain that information.

## Journey-Level Gap Severity

Journeys ranked by combined documentation gap severity (Act + Diag drop):

| Journey | N | T1 Act | T2 Act | Act Δ | T1 Diag | T2 Diag | Diag Δ | Doc Suf | Templates | NM Gap |
|---------|---|--------|--------|-------|---------|---------|--------|---------|-----------|--------|
| J3: Correctness & Debugging (Wrong Results) | 20 | 2.3 | 0.1 | **-2.2** | 2.9 | 1.2 | **-1.7** | 0/20 | 18 | 16 |
| J5: Performance Optimization (Making It Faster) | 20 | 2.8 | 0.1 | **-2.7** | 2.9 | 1.8 | **-1.1** | 0/20 | 0 | 3 |
| J8: Custom & Higher-Order Ops | 20 | 2.6 | 0.0 | **-2.6** | 2.9 | 2.0 | **-0.9** | 0/20 | 0 | 3 |
| J7: Compile-Time Performance (Compilation Too Slow) | 20 | 2.6 | 0.0 | **-2.6** | 2.9 | 2.3 | **-0.6** | 2/20 | 0 | 2 |
| J6: Dynamic Shapes | 20 | 2.5 | 0.3 | **-2.2** | 3.0 | 2.1 | **-0.8** | 2/20 | 0 | 1 |
| J1: First Compile (Getting Started) | 20 | 2.6 | 0.8 | **-1.9** | 3.0 | 2.2 | **-0.8** | 5/20 | 0 | 5 |
| J4: Graph Breaks | 20 | 2.5 | 1.0 | **-1.5** | 3.0 | 1.9 | **-1.1** | 9/20 | 20 | 1 |
| J2: Performance Diagnosis (Why Is It Slow?) | 20 | 2.2 | 0.7 | **-1.6** | 2.9 | 2.1 | **-0.8** | 4/20 | 0 | 5 |

## Per-Journey Documentation Gap Details

### J3: Correctness & Debugging (Wrong Results)

**20 cases** | Doc sufficient: 0/20 | Templates: 18/20
Act: 2.3 → 0.1 (Δ=2.2) | Diag: 2.9 → 1.2 (Δ=1.7)

**Missing mechanism documentation (16 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J3-1**: torch.compile produces different numerical output compared to eager mode. How do I debug this?...
  - Expected topics: accuracy debugging, torch._dynamo.config.repro_level, minifier, numerical precision
  - Act: 2→0 | Diag: 3→1
- **J3-10**: Segformer accuracy regressed when using AOT eager mode in PyTorch 2.5. How do I check if this is a known regression?...
  - Expected topics: correctness debugging, accuracy, repro_level, numerical accuracy, torch.export
  - Act: 2→0 | Diag: 3→1
- **J3-11**: I'm seeing a 4.7% relative error in Conv2d output on CPU when using torch.compile vs eager mode. Is this level of numeri...
  - Expected topics: numerical divergence, CPU correctness, Conv2d, tolerance thresholds
  - Act: 2→1 | Diag: 3→1
- **J3-12**: torch.compile introduces significant precision errors in my model's output compared to eager. How do I figure out which ...
  - Expected topics: precision errors, accuracy debugging, operator isolation, minifier
  - Act: 3→0 | Diag: 3→1
- **J3-13**: torch.compile breaks reproducibility even with manual seeds set. The same code gives different results across runs when ...
  - Expected topics: correctness debugging, accuracy, caching, minifier, repro_level
  - Act: 2→0 | Diag: 3→1
- **J3-14**: torch.compile fails on macOS with 'omp.h file not found'. How do I fix OpenMP issues on Mac?...
  - Expected topics: correctness debugging, accuracy, backends, minifier, numerical accuracy
  - Act: 3→0 | Diag: 3→1
- **J3-15**: Inductor's epilogue fusion produces wrong results when mutations are involved. How do I debug silent correctness issues ...
  - Expected topics: correctness debugging, accuracy, CUDA graphs, max-autotune, inductor backend
  - Act: 2→0 | Diag: 3→1
- **J3-16**: My model uses data-dependent control flow (e.g., early stopping based on values). torch.compile traces through it incorr...
  - Expected topics: correctness debugging, accuracy, backends, operator fusion
  - Act: 2→0 | Diag: 3→1
- **J3-17**: torch.compile silently drops mutations to class-level list attributes. My model's output is wrong because in-place list ...
  - Expected topics: correctness debugging, accuracy, recompilation
  - Act: 3→0 | Diag: 3→1
- **J3-18**: AOT autograd incorrectly depends on tensor strides when regenerating gradients, causing wrong results with non-contiguou...
  - Expected topics: correctness debugging, accuracy, backends, numerical accuracy
  - Act: 2→0 | Diag: 3→1
- **J3-19**: test_conv_stride_constraints fails on ROCm with an AssertionError. Is this a known correctness issue with conv on AMD GP...
  - Expected topics: correctness debugging, accuracy, repro_level, inductor backend, memory optimization
  - Act: 2→0 | Diag: 3→1
- **J3-2**: My conv2d + interpolate model gives wrong gradients under torch.compile but correct ones in eager. How do I isolate the ...
  - Expected topics: backward correctness, minifier, repro_level, accuracy tolerance
  - Act: 2→0 | Diag: 3→1
- **J3-5**: torch.compile gives different results every time I run it, even with the same input and seed. The eager version is deter...
  - Expected topics: reproducibility, deterministic, compile correctness, random seed
  - Act: 3→0 | Diag: 2→1
- **J3-6**: When I compose torch.compile with torch.func.grad, I silently get a wrong result. No error is raised. How do I detect an...
  - Expected topics: silent correctness, torch.func.grad, composition bugs, debugging
  - Act: 2→0 | Diag: 3→1
- **J3-7**: dstack followed by reciprocal gives wrong results under torch.compile but correct results in eager. Is this a known indu...
  - Expected topics: wrong results, operator correctness, inductor bugs, minifier
  - Act: 3→0 | Diag: 3→1
- **J3-9**: How do I benchmark whether torch.compile actually improves accuracy and performance across different models?...
  - Expected topics: correctness debugging, accuracy, backends
  - Act: 1→0 | Diag: 2→1

**Missing fix/workaround documentation (7 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J3-12**: torch.compile introduces significant precision errors in my model's output compared to eager. How do I figure out which ...
  - Expected topics: precision errors, accuracy debugging, operator isolation, minifier
- **J3-14**: torch.compile fails on macOS with 'omp.h file not found'. How do I fix OpenMP issues on Mac?...
  - Expected topics: correctness debugging, accuracy, backends, minifier, numerical accuracy
- **J3-17**: torch.compile silently drops mutations to class-level list attributes. My model's output is wrong because in-place list ...
  - Expected topics: correctness debugging, accuracy, recompilation
- **J3-20**: I'm getting NaN values when using reduce-overhead or max-autotune modes, but the model works fine in default mode. What ...
  - Expected topics: correctness debugging, accuracy, backends, max-autotune, fullgraph mode
- **J3-5**: torch.compile gives different results every time I run it, even with the same input and seed. The eager version is deter...
  - Expected topics: reproducibility, deterministic, compile correctness, random seed
- **J3-7**: dstack followed by reciprocal gives wrong results under torch.compile but correct results in eager. Is this a known indu...
  - Expected topics: wrong results, operator correctness, inductor bugs, minifier
- **J3-8**: torch.compile produces NaN gradients in the backward pass when using GQA with SDPA. Eager mode works fine. The bug seems...
  - Expected topics: NaN gradients, GQA, SDPA, stride correctness, backward pass

**Missing causal explanations (16 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J3-1**: torch.compile produces different numerical output compared to eager mode. How do I debug this?...
  - Act: 2→0 | Diag: 3→1
- **J3-11**: I'm seeing a 4.7% relative error in Conv2d output on CPU when using torch.compile vs eager mode. Is this level of numeri...
  - Act: 2→1 | Diag: 3→1
- **J3-12**: torch.compile introduces significant precision errors in my model's output compared to eager. How do I figure out which ...
  - Act: 3→0 | Diag: 3→1
- **J3-13**: torch.compile breaks reproducibility even with manual seeds set. The same code gives different results across runs when ...
  - Act: 2→0 | Diag: 3→1
- **J3-14**: torch.compile fails on macOS with 'omp.h file not found'. How do I fix OpenMP issues on Mac?...
  - Act: 3→0 | Diag: 3→1
- **J3-15**: Inductor's epilogue fusion produces wrong results when mutations are involved. How do I debug silent correctness issues ...
  - Act: 2→0 | Diag: 3→1
- **J3-16**: My model uses data-dependent control flow (e.g., early stopping based on values). torch.compile traces through it incorr...
  - Act: 2→0 | Diag: 3→1
- **J3-17**: torch.compile silently drops mutations to class-level list attributes. My model's output is wrong because in-place list ...
  - Act: 3→0 | Diag: 3→1
- **J3-18**: AOT autograd incorrectly depends on tensor strides when regenerating gradients, causing wrong results with non-contiguou...
  - Act: 2→0 | Diag: 3→1
- **J3-2**: My conv2d + interpolate model gives wrong gradients under torch.compile but correct ones in eager. How do I isolate the ...
  - Act: 2→0 | Diag: 3→1
- **J3-20**: I'm getting NaN values when using reduce-overhead or max-autotune modes, but the model works fine in default mode. What ...
  - Act: 3→1 | Diag: 3→2
- **J3-3**: Compiled flex_attention gives significantly different accuracy compared to eager. Is this expected and how do I fix it?...
  - Act: 2→0 | Diag: 3→2
- **J3-4**: My RMS norm layer produces NaNs when I use torch.compile with float8 and rowwise scales. The same code works fine in eag...
  - Act: 2→0 | Diag: 3→2
- **J3-6**: When I compose torch.compile with torch.func.grad, I silently get a wrong result. No error is raised. How do I detect an...
  - Act: 2→0 | Diag: 3→1
- **J3-7**: dstack followed by reciprocal gives wrong results under torch.compile but correct results in eager. Is this a known indu...
  - Act: 3→0 | Diag: 3→1
- **J3-8**: torch.compile produces NaN gradients in the backward pass when using GQA with SDPA. Eager mode works fine. The bug seems...
  - Act: 3→0 | Diag: 3→2

**Template responses (18 cases) — likely missing documentation pages:**
These cases all received identical boilerplate responses, suggesting the docs have no relevant page at all.

- **J3-1**: torch.compile produces different numerical output compared to eager mode. How do I debug this?...
  - Expected topics: accuracy debugging, torch._dynamo.config.repro_level, minifier, numerical precision
- **J3-10**: Segformer accuracy regressed when using AOT eager mode in PyTorch 2.5. How do I check if this is a known regression?...
  - Expected topics: correctness debugging, accuracy, repro_level, numerical accuracy, torch.export
- **J3-11**: I'm seeing a 4.7% relative error in Conv2d output on CPU when using torch.compile vs eager mode. Is this level of numeri...
  - Expected topics: numerical divergence, CPU correctness, Conv2d, tolerance thresholds
- **J3-12**: torch.compile introduces significant precision errors in my model's output compared to eager. How do I figure out which ...
  - Expected topics: precision errors, accuracy debugging, operator isolation, minifier
- **J3-13**: torch.compile breaks reproducibility even with manual seeds set. The same code gives different results across runs when ...
  - Expected topics: correctness debugging, accuracy, caching, minifier, repro_level
- **J3-14**: torch.compile fails on macOS with 'omp.h file not found'. How do I fix OpenMP issues on Mac?...
  - Expected topics: correctness debugging, accuracy, backends, minifier, numerical accuracy
- **J3-15**: Inductor's epilogue fusion produces wrong results when mutations are involved. How do I debug silent correctness issues ...
  - Expected topics: correctness debugging, accuracy, CUDA graphs, max-autotune, inductor backend
- **J3-16**: My model uses data-dependent control flow (e.g., early stopping based on values). torch.compile traces through it incorr...
  - Expected topics: correctness debugging, accuracy, backends, operator fusion
- **J3-17**: torch.compile silently drops mutations to class-level list attributes. My model's output is wrong because in-place list ...
  - Expected topics: correctness debugging, accuracy, recompilation
- **J3-18**: AOT autograd incorrectly depends on tensor strides when regenerating gradients, causing wrong results with non-contiguou...
  - Expected topics: correctness debugging, accuracy, backends, numerical accuracy
- **J3-19**: test_conv_stride_constraints fails on ROCm with an AssertionError. Is this a known correctness issue with conv on AMD GP...
  - Expected topics: correctness debugging, accuracy, repro_level, inductor backend, memory optimization
- **J3-2**: My conv2d + interpolate model gives wrong gradients under torch.compile but correct ones in eager. How do I isolate the ...
  - Expected topics: backward correctness, minifier, repro_level, accuracy tolerance
- **J3-20**: I'm getting NaN values when using reduce-overhead or max-autotune modes, but the model works fine in default mode. What ...
  - Expected topics: correctness debugging, accuracy, backends, max-autotune, fullgraph mode
- **J3-4**: My RMS norm layer produces NaNs when I use torch.compile with float8 and rowwise scales. The same code works fine in eag...
  - Expected topics: NaN debugging, float8, RMS norm, precision, compile correctness
- **J3-6**: When I compose torch.compile with torch.func.grad, I silently get a wrong result. No error is raised. How do I detect an...
  - Expected topics: silent correctness, torch.func.grad, composition bugs, debugging
- **J3-7**: dstack followed by reciprocal gives wrong results under torch.compile but correct results in eager. Is this a known indu...
  - Expected topics: wrong results, operator correctness, inductor bugs, minifier
- **J3-8**: torch.compile produces NaN gradients in the backward pass when using GQA with SDPA. Eager mode works fine. The bug seems...
  - Expected topics: NaN gradients, GQA, SDPA, stride correctness, backward pass
- **J3-9**: How do I benchmark whether torch.compile actually improves accuracy and performance across different models?...
  - Expected topics: correctness debugging, accuracy, backends

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J3-12 | torch.compile introduces significant precision errors in my  | 3→0 | 3→1 | No |
| J3-14 | torch.compile fails on macOS with 'omp.h file not found'. Ho | 3→0 | 3→1 | No |
| J3-17 | torch.compile silently drops mutations to class-level list a | 3→0 | 3→1 | No |
| J3-7 | dstack followed by reciprocal gives wrong results under torc | 3→0 | 3→1 | No |
| J3-1 | torch.compile produces different numerical output compared t | 2→0 | 3→1 | No |

---

### J5: Performance Optimization (Making It Faster)

**20 cases** | Doc sufficient: 0/20 | Templates: 0/20
Act: 2.8 → 0.1 (Δ=2.7) | Diag: 2.9 → 1.8 (Δ=1.1)

**Missing mechanism documentation (3 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J5-4**: I'm getting a KeyError: 'dim' from UnbindCatRemover when torch.compile tries to optimize my model. Is this an inductor o...
  - Expected topics: inductor passes, optimization errors, split_cat optimization, debugging
  - Act: 3→0 | Diag: 3→1
- **J5-6**: I'm getting misaligned address errors when using max-autotune with torch.compile. The autotuner picks a template that ca...
  - Expected topics: max-autotune, memory alignment, template selection, autotuner bugs
  - Act: 3→0 | Diag: 3→1
- **J5-9**: torch.compile/inductor doesn't work on Windows at all. I get linker errors. Is Windows supported?...
  - Expected topics: performance optimization, inductor, error messages
  - Act: 3→0 | Diag: 3→1

**Missing fix/workaround documentation (16 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J5-1**: What does mode='max-autotune' actually do and why does it seem to lower precision? Is there a way to get the speed benef...
  - Expected topics: max-autotune, CUDA graphs, autotuning, precision tradeoffs
- **J5-10**: torch.compile'd optimizer.step() fails with 'too many arguments in call' error. How do I compile optimizers?...
  - Expected topics: performance optimization, inductor, inductor backend, operator fusion, quantization
- **J5-11**: Using max-autotune with reduce-overhead is much slower than default mode because of repeated CUDA graph instantiation. W...
  - Expected topics: max-autotune, reduce-overhead, CUDA graphs, mode combinations
- **J5-12**: I'm getting 'shared memory out of resource' error when using compiled flex_attention on my RTX 4090. How do I work aroun...
  - Expected topics: shared memory, GPU resources, flex_attention, resource limits
- **J5-13**: Inductor-generated code for nn.Embedding forward is slower than eager. Why doesn't inductor optimize embedding lookups?...
  - Expected topics: inductor, performance, embedding, kernel optimization
- **J5-14**: My Triton kernel gets 1.35x slower when I add more specialization to it. Shouldn't more specialization make it faster? W...
  - Expected topics: Triton kernels, specialization, performance paradox, kernel optimization
- **J5-15**: I wrote a custom softmax Triton kernel and registered it with torch.library, but torch.compile throws an error when tryi...
  - Expected topics: performance optimization, inductor, triton
- **J5-17**: test_select_algorithm fails for convolution in inductor. Is there a bug in the algorithm selection for conv ops?...
  - Expected topics: performance optimization, inductor, triton, inductor backend, error messages
- **J5-18**: The inductor-generated log_softmax kernel gets much worse performance when padding is involved. How do I avoid this?...
  - Expected topics: performance optimization, inductor, triton, minifier, repro_level
- **J5-19**: Inductor's welford reduction implementation makes LayerNorm slower than eager in several cases. Is there a way to overri...
  - Expected topics: performance optimization, inductor, triton, dynamic shapes, profiling
- **J5-2**: After upgrading from PyTorch 2.9 to 2.10, torch.compile with reduce-overhead mode is 7x slower. How do I diagnose this r...
  - Expected topics: reduce-overhead, CUDA graphs, cudagraph_trees, performance regression
- **J5-3**: FlexAttention (templated attention) performance is really bad when I combine a causal mask with an upper square mask. Ea...
  - Expected topics: flex_attention, mask composition, performance tuning, attention optimization
- **J5-4**: I'm getting a KeyError: 'dim' from UnbindCatRemover when torch.compile tries to optimize my model. Is this an inductor o...
  - Expected topics: inductor passes, optimization errors, split_cat optimization, debugging
- **J5-6**: I'm getting misaligned address errors when using max-autotune with torch.compile. The autotuner picks a template that ca...
  - Expected topics: max-autotune, memory alignment, template selection, autotuner bugs
- **J5-7**: Is there a fused linear + cross-entropy loss function? Computing them separately seems wasteful....
  - Expected topics: performance optimization, inductor, operator fusion
- **J5-9**: torch.compile/inductor doesn't work on Windows at all. I get linker errors. Is Windows supported?...
  - Expected topics: performance optimization, inductor, error messages

**Missing causal explanations (16 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J5-1**: What does mode='max-autotune' actually do and why does it seem to lower precision? Is there a way to get the speed benef...
  - Act: 3→0 | Diag: 3→2
- **J5-10**: torch.compile'd optimizer.step() fails with 'too many arguments in call' error. How do I compile optimizers?...
  - Act: 3→0 | Diag: 3→2
- **J5-11**: Using max-autotune with reduce-overhead is much slower than default mode because of repeated CUDA graph instantiation. W...
  - Act: 3→0 | Diag: 3→1
- **J5-12**: I'm getting 'shared memory out of resource' error when using compiled flex_attention on my RTX 4090. How do I work aroun...
  - Act: 3→0 | Diag: 3→2
- **J5-13**: Inductor-generated code for nn.Embedding forward is slower than eager. Why doesn't inductor optimize embedding lookups?...
  - Act: 3→0 | Diag: 3→2
- **J5-14**: My Triton kernel gets 1.35x slower when I add more specialization to it. Shouldn't more specialization make it faster? W...
  - Act: 3→0 | Diag: 3→2
- **J5-17**: test_select_algorithm fails for convolution in inductor. Is there a bug in the algorithm selection for conv ops?...
  - Act: 3→0 | Diag: 3→2
- **J5-18**: The inductor-generated log_softmax kernel gets much worse performance when padding is involved. How do I avoid this?...
  - Act: 3→0 | Diag: 3→2
- **J5-19**: Inductor's welford reduction implementation makes LayerNorm slower than eager in several cases. Is there a way to overri...
  - Act: 3→0 | Diag: 3→2
- **J5-2**: After upgrading from PyTorch 2.9 to 2.10, torch.compile with reduce-overhead mode is 7x slower. How do I diagnose this r...
  - Act: 3→0 | Diag: 3→2
- **J5-3**: FlexAttention (templated attention) performance is really bad when I combine a causal mask with an upper square mask. Ea...
  - Act: 3→0 | Diag: 3→2
- **J5-4**: I'm getting a KeyError: 'dim' from UnbindCatRemover when torch.compile tries to optimize my model. Is this an inductor o...
  - Act: 3→0 | Diag: 3→1
- **J5-6**: I'm getting misaligned address errors when using max-autotune with torch.compile. The autotuner picks a template that ca...
  - Act: 3→0 | Diag: 3→1
- **J5-7**: Is there a fused linear + cross-entropy loss function? Computing them separately seems wasteful....
  - Act: 3→0 | Diag: 3→2
- **J5-8**: How do I make torch.compile work with vLLM? I keep getting errors when trying to compile OPT-125M....
  - Act: 2→0 | Diag: 3→2
- **J5-9**: torch.compile/inductor doesn't work on Windows at all. I get linker errors. Is Windows supported?...
  - Act: 3→0 | Diag: 3→1

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J5-11 | Using max-autotune with reduce-overhead is much slower than  | 3→0 | 3→1 | No |
| J5-4 | I'm getting a KeyError: 'dim' from UnbindCatRemover when tor | 3→0 | 3→1 | No |
| J5-6 | I'm getting misaligned address errors when using max-autotun | 3→0 | 3→1 | No |
| J5-9 | torch.compile/inductor doesn't work on Windows at all. I get | 3→0 | 3→1 | No |
| J5-1 | What does mode='max-autotune' actually do and why does it se | 3→0 | 3→2 | No |

---

### J8: Custom & Higher-Order Ops

**20 cases** | Doc sufficient: 0/20 | Templates: 0/20
Act: 2.6 → 0.0 (Δ=2.6) | Diag: 2.9 → 2.0 (Δ=0.9)

**Missing mechanism documentation (3 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J8-15**: Does PyTorch support parallel associative scans? I need an efficient prefix-sum that torch.compile can optimize....
  - Expected topics: custom operators, higher-order ops, torch.scan
  - Act: 2→0 | Diag: 3→1
- **J8-7**: torch._dynamo.optimize fails on my code that uses pytorch_cluster's radius function with 'tensor has non-zero number of ...
  - Expected topics: third-party ops, dynamo compatibility, custom ops, pytorch_cluster
  - Act: 3→0 | Diag: 3→2
- **J8-9**: Compiling a function with complex-valued tensors fails. Does torch.compile support complex number operations?...
  - Expected topics: custom operators, higher-order ops, backends, inductor backend, error messages
  - Act: 3→0 | Diag: 3→2

**Missing fix/workaround documentation (12 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J8-1**: How do I create a custom op that works with torch.compile / dynamo / inductor? The docs are unclear....
  - Expected topics: custom ops, torch.library, dynamo custom op, inductor lowering
- **J8-10**: Triton autotuning fails with 'invalid argument' CUDA error. How do I debug autotuning failures?...
  - Expected topics: custom operators, higher-order ops, backends, triton, minifier
- **J8-13**: torch.compile + CUDA graphs fails with an assertion error in multithreaded inference. Is this combination supported for ...
  - Expected topics: custom operators, higher-order ops, caching, CUDA graphs, max-autotune
- **J8-17**: Custom ops registered with @torch.library.custom_op decorator are much slower than ops registered with torch.Library.def...
  - Expected topics: custom ops, torch.library, performance, custom_op decorator
- **J8-19**: Flex Attention crashes with an LLVM error after the recent Triton pin update. Is this a known Triton compatibility issue...
  - Expected topics: custom operators, higher-order ops, triton, flex_attention, repro_level
- **J8-2**: Compiled flex_attention segfaults during the backward pass. How do I debug this?...
  - Expected topics: flex_attention, backward pass, segfault debugging, higher-order ops
- **J8-3**: How do I use torch.nn.BatchNorm2d inside a while_loop higher-order op with torch.compile?...
  - Expected topics: while_loop, higher-order ops, stateful modules, control flow
- **J8-4**: I registered a custom C++ op with torch.library but torch.compile gives wrong results or errors. What's the correct way ...
  - Expected topics: custom ops, torch.library, torch.compile, inductor
- **J8-6**: FlexAttention output deviates significantly from SDPA when I use torch.compile() with torch.set_float32_matmul_precision...
  - Expected topics: flex_attention, precision, float32_matmul_precision, numerical accuracy
- **J8-7**: torch._dynamo.optimize fails on my code that uses pytorch_cluster's radius function with 'tensor has non-zero number of ...
  - Expected topics: third-party ops, dynamo compatibility, custom ops, pytorch_cluster
- **J8-8**: I'm trying to use torch.cond (control flow) with torch.compile but I'm getting various errors. What are the limitations ...
  - Expected topics: cond, control flow, higher-order ops, compile limitations
- **J8-9**: Compiling a function with complex-valued tensors fails. Does torch.compile support complex number operations?...
  - Expected topics: custom operators, higher-order ops, backends, inductor backend, error messages

**Missing causal explanations (15 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J8-10**: Triton autotuning fails with 'invalid argument' CUDA error. How do I debug autotuning failures?...
  - Act: 3→0 | Diag: 3→2
- **J8-11**: My custom op defined with torch.library causes an illegal memory access when used with torch.compile. The same op works ...
  - Act: 2→0 | Diag: 3→2
- **J8-12**: Compiled FlexAttention gives illegal memory access or device-side assert errors even though all my tensors are contiguou...
  - Act: 2→0 | Diag: 3→2
- **J8-13**: torch.compile + CUDA graphs fails with an assertion error in multithreaded inference. Is this combination supported for ...
  - Act: 3→0 | Diag: 3→2
- **J8-16**: How do I use symmetric memory (for NVLink-based collectives) with torch.compile? It currently breaks compilation....
  - Act: 2→0 | Diag: 3→2
- **J8-18**: My custom min_sum/mul_sum reduction ops are much slower with the C++ inductor backend on CPU than with eager mode....
  - Act: 2→0 | Diag: 3→2
- **J8-19**: Flex Attention crashes with an LLVM error after the recent Triton pin update. Is this a known Triton compatibility issue...
  - Act: 3→0 | Diag: 3→2
- **J8-2**: Compiled flex_attention segfaults during the backward pass. How do I debug this?...
  - Act: 3→0 | Diag: 3→2
- **J8-20**: Compiled flex_attention gives wrong gradients. The forward pass is correct but backward produces different values than e...
  - Act: 2→0 | Diag: 3→2
- **J8-3**: How do I use torch.nn.BatchNorm2d inside a while_loop higher-order op with torch.compile?...
  - Act: 3→0 | Diag: 3→2
- **J8-5**: I can't compile flex_attention with dynamic shapes when my BlockMask depends on the batch dimension. How do I use dynami...
  - Act: 2→0 | Diag: 3→3
- **J8-6**: FlexAttention output deviates significantly from SDPA when I use torch.compile() with torch.set_float32_matmul_precision...
  - Act: 3→0 | Diag: 3→3
- **J8-7**: torch._dynamo.optimize fails on my code that uses pytorch_cluster's radius function with 'tensor has non-zero number of ...
  - Act: 3→0 | Diag: 3→2
- **J8-8**: I'm trying to use torch.cond (control flow) with torch.compile but I'm getting various errors. What are the limitations ...
  - Act: 3→0 | Diag: 3→2
- **J8-9**: Compiling a function with complex-valued tensors fails. Does torch.compile support complex number operations?...
  - Act: 3→0 | Diag: 3→2

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J8-10 | Triton autotuning fails with 'invalid argument' CUDA error.  | 3→0 | 3→2 | No |
| J8-13 | torch.compile + CUDA graphs fails with an assertion error in | 3→0 | 3→2 | No |
| J8-15 | Does PyTorch support parallel associative scans? I need an e | 2→0 | 3→1 | No |
| J8-17 | Custom ops registered with @torch.library.custom_op decorato | 3→0 | 3→2 | No |
| J8-19 | Flex Attention crashes with an LLVM error after the recent T | 3→0 | 3→2 | No |

---

### J7: Compile-Time Performance (Compilation Too Slow)

**20 cases** | Doc sufficient: 2/20 | Templates: 0/20
Act: 2.6 → 0.0 (Δ=2.6) | Diag: 2.9 → 2.3 (Δ=0.6)

**Missing mechanism documentation (2 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J7-10**: Compiled autograd fails when running nn.LayerNorm with torch.compile. Is compiled autograd production-ready?...
  - Expected topics: compilation time, caching, recompilation, repro_level, error messages
  - Act: 3→0 | Diag: 3→2
- **J7-6**: tmp_path.rename in the inductor code cache fails on Windows. How does caching work on Windows?...
  - Expected topics: compilation time, caching, triton, max-autotune, profiling
  - Act: 3→0 | Diag: 3→2

**Missing fix/workaround documentation (13 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J7-1**: torch.compile takes so long on T5 inference that it times out. How do I reduce compilation time for large models?...
  - Expected topics: compilation time, large models, inline_inbuilt_nn_modules, guards
- **J7-10**: Compiled autograd fails when running nn.LayerNorm with torch.compile. Is compiled autograd production-ready?...
  - Expected topics: compilation time, caching, recompilation, repro_level, error messages
- **J7-13**: torch.compile takes 34 seconds to compile a simple for loop. Is there a way to make dynamo handle loops faster?...
  - Expected topics: loop compilation, dynamo tracing, compile time, loop unrolling
- **J7-14**: On CPU, torch._inductor.cpu_vec_isa.pick_vec_isa takes 9 seconds just to detect the vector ISA. Why is this so slow and ...
  - Expected topics: CPU compilation, vector ISA detection, compile overhead, inductor config
- **J7-16**: Is there a way to serialize a torch.compile'd model so I can load it without recompiling?...
  - Expected topics: compilation time, caching, minifier, repro_level, torch.export
- **J7-19**: torch.compile with FSDP mixed precision on LLaMA causes errors. Is this combination supported?...
  - Expected topics: compilation time, caching, distributed training, error messages
- **J7-2**: Compile time grows exponentially when I chain multiple logsumexp operations with gradients enabled. Is this expected?...
  - Expected topics: compile time, gradient tracing, graph complexity, AOTAutograd
- **J7-3**: Compiling my optimizer (Adam with 200+ parameters) takes 70 seconds because dynamo traces through every iteration of the...
  - Expected topics: optimizer compilation, for loop tracing, compile time, parameter count
- **J7-4**: My compiled AdamW optimizer recompiles every step when I use OneCycleLR scheduler. The learning rate change triggers a n...
  - Expected topics: recompilation, LR scheduler, optimizer guards, tensor wrapping
- **J7-5**: Compilation is 2x faster when my input size is 1 versus any other size. The forward pass time stays the same. Why does i...
  - Expected topics: compile time variance, input size, specialization, graph complexity
- **J7-6**: tmp_path.rename in the inductor code cache fails on Windows. How does caching work on Windows?...
  - Expected topics: compilation time, caching, triton, max-autotune, profiling
- **J7-8**: Inductor autotuning crashes with an illegal memory access when some input tensors are None. How do I work around this?...
  - Expected topics: compilation time, caching, triton, inductor backend, memory optimization
- **J7-9**: My model takes extremely long to compile because it's very deep. Can compilation be broken into smaller pieces?...
  - Expected topics: compilation time, caching, torch.export, inductor backend

**Missing causal explanations (15 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J7-1**: torch.compile takes so long on T5 inference that it times out. How do I reduce compilation time for large models?...
  - Act: 3→0 | Diag: 3→3
- **J7-10**: Compiled autograd fails when running nn.LayerNorm with torch.compile. Is compiled autograd production-ready?...
  - Act: 3→0 | Diag: 3→2
- **J7-11**: I enabled TORCHINDUCTOR_FX_GRAPH_CACHE=1 but compilation is still slow on cold start. What else can I do to reduce compi...
  - Act: 2→0 | Diag: 3→2
- **J7-13**: torch.compile takes 34 seconds to compile a simple for loop. Is there a way to make dynamo handle loops faster?...
  - Act: 3→0 | Diag: 3→2
- **J7-14**: On CPU, torch._inductor.cpu_vec_isa.pick_vec_isa takes 9 seconds just to detect the vector ISA. Why is this so slow and ...
  - Act: 3→0 | Diag: 3→2
- **J7-16**: Is there a way to serialize a torch.compile'd model so I can load it without recompiling?...
  - Act: 3→0 | Diag: 3→3
- **J7-17**: Inductor has persistent caching but Dynamo frontend doesn't. Can Dynamo cache its analysis to speed up cold compilation?...
  - Act: 2→0 | Diag: 3→2
- **J7-2**: Compile time grows exponentially when I chain multiple logsumexp operations with gradients enabled. Is this expected?...
  - Act: 3→0 | Diag: 3→2
- **J7-20**: torch.compile/Triton holds the GIL during compilation, blocking all other threads. Can compilation run in the background...
  - Act: 2→0 | Diag: 3→2
- **J7-3**: Compiling my optimizer (Adam with 200+ parameters) takes 70 seconds because dynamo traces through every iteration of the...
  - Act: 3→0 | Diag: 3→3
- **J7-4**: My compiled AdamW optimizer recompiles every step when I use OneCycleLR scheduler. The learning rate change triggers a n...
  - Act: 3→0 | Diag: 3→3
- **J7-5**: Compilation is 2x faster when my input size is 1 versus any other size. The forward pass time stays the same. Why does i...
  - Act: 3→0 | Diag: 3→2
- **J7-6**: tmp_path.rename in the inductor code cache fails on Windows. How does caching work on Windows?...
  - Act: 3→0 | Diag: 3→2
- **J7-8**: Inductor autotuning crashes with an illegal memory access when some input tensors are None. How do I work around this?...
  - Act: 3→0 | Diag: 3→3
- **J7-9**: My model takes extremely long to compile because it's very deep. Can compilation be broken into smaller pieces?...
  - Act: 3→0 | Diag: 3→3

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J7-10 | Compiled autograd fails when running nn.LayerNorm with torch | 3→0 | 3→2 | No |
| J7-13 | torch.compile takes 34 seconds to compile a simple for loop. | 3→0 | 3→2 | No |
| J7-14 | On CPU, torch._inductor.cpu_vec_isa.pick_vec_isa takes 9 sec | 3→0 | 3→2 | No |
| J7-19 | torch.compile with FSDP mixed precision on LLaMA causes erro | 3→0 | 3→2 | No |
| J7-2 | Compile time grows exponentially when I chain multiple logsu | 3→0 | 3→2 | No |

---

### J6: Dynamic Shapes

**20 cases** | Doc sufficient: 2/20 | Templates: 0/20
Act: 2.5 → 0.3 (Δ=2.2) | Diag: 3.0 → 2.1 (Δ=0.8)

**Missing mechanism documentation (1 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J6-8**: I'm getting 'Dynamic slicing on data-dependent value is not supported' from dynamo. How do I handle data-dependent index...
  - Expected topics: data-dependent shapes, dynamic slicing, unsupported operations, workarounds
  - Act: 3→0 | Diag: 3→1

**Missing fix/workaround documentation (9 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J6-10**: torch.compile crashes on my wav2vec2 speech model because the audio input length varies. How do I make torch.compile wor...
  - Expected topics: dynamic shapes, audio models, variable length, wav2vec2
- **J6-2**: I'm getting a division by zero error when using torch.compile with dynamic=True on an empty tensor. This worked in the p...
  - Expected topics: dynamic shapes, empty tensors, regression, guard specialization
- **J6-20**: torch.combinations throws RuntimeError with dynamic shapes enabled. Is this op supported in dynamic mode?...
  - Expected topics: dynamic shapes, recompilation, backends, inductor backend
- **J6-3**: torch.sum fails with a dynamo error when dynamic=True. How do I use dynamic shapes correctly with reduction operations?...
  - Expected topics: dynamic shapes, reduction ops, symbolic shapes, dynamo errors
- **J6-4**: torch.compile fails on my GNN model trained with neighbor sampling because the input sizes change every batch. How do I ...
  - Expected topics: dynamic shapes, GNN, variable batch size, neighbor sampling
- **J6-6**: torch.compile hits 'Recompilation exhausted' with 'size mismatch at index 2'. I'm already using dynamic=True. Why does i...
  - Expected topics: recompilation limit, size mismatch, dynamic shapes, guard failures
- **J6-7**: I set dynamic=True in torch.compile but it still doesn't work with my varying input shapes. I get errors about symbolic ...
  - Expected topics: dynamic shapes, symbolic shapes, torch.compile dynamic, basic usage
- **J6-8**: I'm getting 'Dynamic slicing on data-dependent value is not supported' from dynamo. How do I handle data-dependent index...
  - Expected topics: data-dependent shapes, dynamic slicing, unsupported operations, workarounds
- **J6-9**: AMP autocast causes recompilation with 'dtype mismatch: expected Half, actual Float'. Why does torch.compile recompile w...
  - Expected topics: AMP, dtype guards, recompilation, mixed precision

**Missing causal explanations (17 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J6-1**: torch.compile(dynamic=True) keeps specializing on the batch dimension during LayerNorm backward, causing recompiles. How...
  - Act: 3→3 | Diag: 3→3
- **J6-10**: torch.compile crashes on my wav2vec2 speech model because the audio input length varies. How do I make torch.compile wor...
  - Act: 3→0 | Diag: 3→2
- **J6-11**: DTensor placement propagation is missing for as_strided, causing failures when I compile models using DTensor sharding....
  - Act: 2→0 | Diag: 3→2
- **J6-12**: Dynamo recompiles when input shape is (1,1), and mark_dynamic on nn.Parameter has no effect. How do I prevent recompilat...
  - Act: 2→0 | Diag: 3→2
- **J6-15**: Automatic dynamic shapes generates hundreds of guards on a single symbolic variable. Is there a way to limit guard accum...
  - Act: 2→0 | Diag: 3→2
- **J6-16**: I get an obscure 'Expected a value of type List[int]' error that seems related to dynamic shapes. How do I debug this?...
  - Act: 2→0 | Diag: 3→3
- **J6-17**: torch.compile with DeepSpeed throws InternalTorchDynamoError about NestedUserFunction. Is DeepSpeed + Dynamo supported?...
  - Act: 2→0 | Diag: 3→2
- **J6-18**: My ChatTTS model triggers too many recompilations from dynamic shape guards. How do I diagnose and fix excessive guard f...
  - Act: 2→0 | Diag: 3→2
- **J6-19**: Operators returning dynamic-shape outputs that require grad cause issues. How does torch.compile handle ops with data-de...
  - Act: 2→0 | Diag: 3→2
- **J6-2**: I'm getting a division by zero error when using torch.compile with dynamic=True on an empty tensor. This worked in the p...
  - Act: 3→0 | Diag: 3→2
- **J6-20**: torch.combinations throws RuntimeError with dynamic shapes enabled. Is this op supported in dynamic mode?...
  - Act: 3→0 | Diag: 3→2
- **J6-4**: torch.compile fails on my GNN model trained with neighbor sampling because the input sizes change every batch. How do I ...
  - Act: 3→0 | Diag: 3→2
- **J6-5**: My custom attention implementation recompiles on every forward pass because the sequence length keeps changing. How do I...
  - Act: 3→3 | Diag: 3→3
- **J6-6**: torch.compile hits 'Recompilation exhausted' with 'size mismatch at index 2'. I'm already using dynamic=True. Why does i...
  - Act: 3→0 | Diag: 3→2
- **J6-7**: I set dynamic=True in torch.compile but it still doesn't work with my varying input shapes. I get errors about symbolic ...
  - Act: 3→0 | Diag: 3→2
- **J6-8**: I'm getting 'Dynamic slicing on data-dependent value is not supported' from dynamo. How do I handle data-dependent index...
  - Act: 3→0 | Diag: 3→1
- **J6-9**: AMP autocast causes recompilation with 'dtype mismatch: expected Half, actual Float'. Why does torch.compile recompile w...
  - Act: 3→0 | Diag: 3→2

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J6-8 | I'm getting 'Dynamic slicing on data-dependent value is not  | 3→0 | 3→1 | No |
| J6-10 | torch.compile crashes on my wav2vec2 speech model because th | 3→0 | 3→2 | No |
| J6-2 | I'm getting a division by zero error when using torch.compil | 3→0 | 3→2 | No |
| J6-20 | torch.combinations throws RuntimeError with dynamic shapes e | 3→0 | 3→2 | No |
| J6-4 | torch.compile fails on my GNN model trained with neighbor sa | 3→0 | 3→2 | No |

---

### J1: First Compile (Getting Started)

**20 cases** | Doc sufficient: 5/20 | Templates: 0/20
Act: 2.6 → 0.8 (Δ=1.9) | Diag: 3.0 → 2.2 (Δ=0.8)

**Missing mechanism documentation (5 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J1-13**: I'm trying to use torch.compile with a GRU model but it doesn't seem to be supported. Is there a workaround for compilin...
  - Expected topics: torch.compile basics, getting started, caching, error messages
  - Act: 2→0 | Diag: 3→1
- **J1-14**: torch.compile doesn't work inside a multiprocessing pool. I get 'daemonic processes are not allowed to have children'. H...
  - Expected topics: torch.compile, multiprocessing, inductor, error messages
  - Act: 3→0 | Diag: 3→1
- **J1-16**: Does torch.compile/inductor support complex-valued tensors? I'm getting errors with complex dtypes....
  - Expected topics: torch.compile basics, getting started, inductor backend, error messages
  - Act: 2→0 | Diag: 3→1
- **J1-20**: torch.compile raises JSONDecodeError when using compile cache with Ray and multiple GPUs. The cache seems corrupted. How...
  - Expected topics: torch.compile, compile cache, Ray, distributed, error messages
  - Act: 3→0 | Diag: 3→1
- **J1-8**: I'm getting BackendCompilerFailed with 'device kernel image is invalid' when using torch.compile with inductor. How do I...
  - Expected topics: inductor backend, Triton errors, CUDA compatibility, backend debugging
  - Act: 2→0 | Diag: 3→1

**Missing fix/workaround documentation (9 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J1-12**: Dynamo doesn't support tracing through torch.autograd.grad. I use it for computing per-sample gradients. How do I make t...
  - Expected topics: dynamo limitations, autograd.grad, graph breaks, torch.compile
- **J1-14**: torch.compile doesn't work inside a multiprocessing pool. I get 'daemonic processes are not allowed to have children'. H...
  - Expected topics: torch.compile, multiprocessing, inductor, error messages
- **J1-17**: How do I set up the C++ compiler for torch.compile on Windows? The default builder doesn't seem to work....
  - Expected topics: torch.compile basics, getting started, inductor backend
- **J1-19**: torch.compile fails with '/usr/bin/ld: cannot find -lcuda' even though CUDA is installed. How do I fix the linker error?...
  - Expected topics: torch.compile, setup, CUDA, linker, error messages
- **J1-20**: torch.compile raises JSONDecodeError when using compile cache with Ray and multiple GPUs. The cache seems corrupted. How...
  - Expected topics: torch.compile, compile cache, Ray, distributed, error messages
- **J1-3**: I'm trying to use torch.compile with DDP and AMP together but I'm getting a NotImplementedError about autocast. Is there...
  - Expected topics: DDP integration, AMP compatibility, torch.compile ordering, mixed precision
- **J1-4**: torch.compile fails on both CPU and CUDA with my ResNet50 model. I'm using the nightly Docker image. Is there something ...
  - Expected topics: installation, torch.compile setup, backend compatibility, troubleshooting
- **J1-6**: How do I use torch.compile together with Tensor Parallel? It crashes when I try to compile a tensor-parallelized model....
  - Expected topics: tensor parallel, distributed, torch.compile + TP, DTensor
- **J1-7**: torch.compile doesn't seem to respect torch.cuda.set_device(). My compiled function puts tensors on the wrong GPU. Is th...
  - Expected topics: multi-GPU, device placement, torch.compile limitations, CUDA device

**Missing causal explanations (15 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J1-1**: How do I use compile cache in torch.compile so I don't have to recompile every time I restart my script?...
  - Act: 3→3 | Diag: 3→3
- **J1-12**: Dynamo doesn't support tracing through torch.autograd.grad. I use it for computing per-sample gradients. How do I make t...
  - Act: 3→0 | Diag: 3→3
- **J1-13**: I'm trying to use torch.compile with a GRU model but it doesn't seem to be supported. Is there a workaround for compilin...
  - Act: 2→0 | Diag: 3→1
- **J1-14**: torch.compile doesn't work inside a multiprocessing pool. I get 'daemonic processes are not allowed to have children'. H...
  - Act: 3→0 | Diag: 3→1
- **J1-15**: torch.compile throws NotImplementedError 'make_reindexer NYI on DtypeView' when I use MXFP8 quantization. Is MXFP8 suppo...
  - Act: 2→0 | Diag: 3→2
- **J1-16**: Does torch.compile/inductor support complex-valued tensors? I'm getting errors with complex dtypes....
  - Act: 2→0 | Diag: 3→1
- **J1-17**: How do I set up the C++ compiler for torch.compile on Windows? The default builder doesn't seem to work....
  - Act: 3→0 | Diag: 3→2
- **J1-18**: Inductor's pattern matcher silently replaces reshape with view, which changes semantics when my tensor isn't contiguous....
  - Act: 2→0 | Diag: 3→2
- **J1-19**: torch.compile fails with '/usr/bin/ld: cannot find -lcuda' even though CUDA is installed. How do I fix the linker error?...
  - Act: 3→0 | Diag: 3→2
- **J1-2**: How do I change the backend compiler used by torch.compile? The docs mention 'inductor' but I want to use a different on...
  - Act: 3→3 | Diag: 3→3
- **J1-20**: torch.compile raises JSONDecodeError when using compile cache with Ray and multiple GPUs. The cache seems corrupted. How...
  - Act: 3→0 | Diag: 3→1
- **J1-3**: I'm trying to use torch.compile with DDP and AMP together but I'm getting a NotImplementedError about autocast. Is there...
  - Act: 3→2 | Diag: 3→3
- **J1-7**: torch.compile doesn't seem to respect torch.cuda.set_device(). My compiled function puts tensors on the wrong GPU. Is th...
  - Act: 3→0 | Diag: 3→2
- **J1-8**: I'm getting BackendCompilerFailed with 'device kernel image is invalid' when using torch.compile with inductor. How do I...
  - Act: 2→0 | Diag: 3→1
- **J1-9**: How can I save and reuse torch.compile results across different Python processes? I don't want to recompile every time I...
  - Act: 3→3 | Diag: 3→3

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J1-14 | torch.compile doesn't work inside a multiprocessing pool. I  | 3→0 | 3→1 | No |
| J1-20 | torch.compile raises JSONDecodeError when using compile cach | 3→0 | 3→1 | No |
| J1-13 | I'm trying to use torch.compile with a GRU model but it does | 2→0 | 3→1 | No |
| J1-16 | Does torch.compile/inductor support complex-valued tensors?  | 2→0 | 3→1 | No |
| J1-17 | How do I set up the C++ compiler for torch.compile on Window | 3→0 | 3→2 | No |

---

### J4: Graph Breaks

**20 cases** | Doc sufficient: 9/20 | Templates: 20/20
Act: 2.5 → 1.0 (Δ=1.5) | Diag: 3.0 → 1.9 (Δ=1.1)

**Missing mechanism documentation (1 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J4-7**: Dynamo recompiles every time because it's guarding on a global config variable that I change between calls. How do I pre...
  - Expected topics: guards, global variables, recompilation, dynamo config
  - Act: 3→1 | Diag: 3→1

**Missing fix/workaround documentation (13 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J4-1**: I'm getting a graph break in my flex_attention code when using fullgraph=True. How do I fix it?...
  - Expected topics: graph breaks, fullgraph mode, flex_attention, higher-order ops
- **J4-10**: Dynamo can't trace through AdamW when I use a learning rate scheduler. It fails with graph breaks. How do I compile my o...
  - Expected topics: optimizer compilation, LR scheduler, graph breaks, dynamo tracing
- **J4-17**: The PT2E quantization flow is completely broken on ARM/Graviton3 CPU with PyTorch 2.9.1. Is this a known issue?...
  - Expected topics: graph breaks, torch._dynamo, dynamic shapes, fullgraph mode, profiling
- **J4-18**: torch.compile with aotautograd doesn't support double backwards (grad of grad). Is there a workaround?...
  - Expected topics: graph breaks, torch._dynamo, backends, graph break resolution, torch.cond
- **J4-19**: I need better guardrails for combining distributed optimizations with non-fullgraph compile. The current behavior is con...
  - Expected topics: graph breaks, torch._dynamo, backends, CUDA graphs, dynamic shapes
- **J4-2**: torch.compile with DDP causes a graph break on _broadcast_coalesced. How do I use torch.compile with distributed trainin...
  - Expected topics: DDP, distributed, graph breaks, compile + DDP integration
- **J4-20**: Dynamo doesn't support Parameter subclasses. My custom Parameter type causes a graph break....
  - Expected topics: graph breaks, torch._dynamo, backends, fullgraph mode
- **J4-3**: I'm getting 'Unsupported: __self__ mismatch for bound method' graph break after upgrading PyTorch. What changed and how ...
  - Expected topics: graph breaks, bound methods, dynamo unsupported, migration
- **J4-5**: I used torch.compiler.disable on a function but dynamo still traces into nested functions called from it. How do I prope...
  - Expected topics: torch.compiler.disable, graph breaks, skip tracing, nested functions
- **J4-6**: Dynamo fails when my model uses Python dataclasses. I get graph breaks because it can't track the dataclass fields. What...
  - Expected topics: dataclass, graph breaks, Python constructs, dynamo limitations
- **J4-7**: Dynamo recompiles every time because it's guarding on a global config variable that I change between calls. How do I pre...
  - Expected topics: guards, global variables, recompilation, dynamo config
- **J4-8**: torch.compile doesn't work properly with selective activation checkpointing (SAC). How do I combine compile with gradien...
  - Expected topics: activation checkpointing, SAC, graph breaks, memory optimization
- **J4-9**: I'm getting a graph break when calling create_block_mask for flex_attention inside a compiled function. How do I avoid t...
  - Expected topics: flex_attention, create_block_mask, graph breaks, higher-order ops

**Missing causal explanations (18 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J4-1**: I'm getting a graph break in my flex_attention code when using fullgraph=True. How do I fix it?...
  - Act: 3→1 | Diag: 3→2
- **J4-10**: Dynamo can't trace through AdamW when I use a learning rate scheduler. It fails with graph breaks. How do I compile my o...
  - Act: 3→1 | Diag: 3→2
- **J4-11**: torch.compile treats my optimizer as a training graph instead of inference, causing unnecessary graph breaks. How do I f...
  - Act: 0→1 | Diag: 3→2
- **J4-12**: I'm using DDP with Dynamo but AllReduce ops cause graph breaks. Is there a way to compile through DDP communication?...
  - Act: 2→1 | Diag: 3→2
- **J4-13**: Dynamo doesn't generate guards for frozen dataclasses, so config changes don't trigger recompilation. Is this expected?...
  - Act: 2→1 | Diag: 3→2
- **J4-14**: torch.compiler.allow_in_graph doesn't create a call_module node in the FX graph. How do I properly inline a module?...
  - Act: 2→1 | Diag: 3→2
- **J4-15**: Is there a way to get Dynamo to capture a single-step graph instead of tracing through the entire forward pass?...
  - Act: 2→1 | Diag: 3→2
- **J4-18**: torch.compile with aotautograd doesn't support double backwards (grad of grad). Is there a workaround?...
  - Act: 3→1 | Diag: 3→2
- **J4-19**: I need better guardrails for combining distributed optimizations with non-fullgraph compile. The current behavior is con...
  - Act: 3→1 | Diag: 3→2
- **J4-2**: torch.compile with DDP causes a graph break on _broadcast_coalesced. How do I use torch.compile with distributed trainin...
  - Act: 3→1 | Diag: 3→2
- **J4-20**: Dynamo doesn't support Parameter subclasses. My custom Parameter type causes a graph break....
  - Act: 3→1 | Diag: 3→2
- **J4-3**: I'm getting 'Unsupported: __self__ mismatch for bound method' graph break after upgrading PyTorch. What changed and how ...
  - Act: 3→1 | Diag: 3→2
- **J4-4**: After upgrading to PyTorch 2.4, my torch.compile code that worked before now throws errors. How do I migrate my code and...
  - Act: 2→1 | Diag: 3→2
- **J4-5**: I used torch.compiler.disable on a function but dynamo still traces into nested functions called from it. How do I prope...
  - Act: 3→1 | Diag: 3→2
- **J4-6**: Dynamo fails when my model uses Python dataclasses. I get graph breaks because it can't track the dataclass fields. What...
  - Act: 3→1 | Diag: 3→2
- **J4-7**: Dynamo recompiles every time because it's guarding on a global config variable that I change between calls. How do I pre...
  - Act: 3→1 | Diag: 3→1
- **J4-8**: torch.compile doesn't work properly with selective activation checkpointing (SAC). How do I combine compile with gradien...
  - Act: 3→1 | Diag: 3→2
- **J4-9**: I'm getting a graph break when calling create_block_mask for flex_attention inside a compiled function. How do I avoid t...
  - Act: 3→1 | Diag: 3→2

**Template responses (20 cases) — likely missing documentation pages:**
These cases all received identical boilerplate responses, suggesting the docs have no relevant page at all.

- **J4-1**: I'm getting a graph break in my flex_attention code when using fullgraph=True. How do I fix it?...
  - Expected topics: graph breaks, fullgraph mode, flex_attention, higher-order ops
- **J4-10**: Dynamo can't trace through AdamW when I use a learning rate scheduler. It fails with graph breaks. How do I compile my o...
  - Expected topics: optimizer compilation, LR scheduler, graph breaks, dynamo tracing
- **J4-11**: torch.compile treats my optimizer as a training graph instead of inference, causing unnecessary graph breaks. How do I f...
  - Expected topics: graph breaks, torch._dynamo, graph break resolution, minifier, repro_level
- **J4-12**: I'm using DDP with Dynamo but AllReduce ops cause graph breaks. Is there a way to compile through DDP communication?...
  - Expected topics: graph breaks, torch._dynamo, backends, recompilation, graph break resolution
- **J4-13**: Dynamo doesn't generate guards for frozen dataclasses, so config changes don't trigger recompilation. Is this expected?...
  - Expected topics: graph breaks, torch._dynamo, shape guards, fullgraph mode
- **J4-14**: torch.compiler.allow_in_graph doesn't create a call_module node in the FX graph. How do I properly inline a module?...
  - Expected topics: graph breaks, torch._dynamo, backends
- **J4-15**: Is there a way to get Dynamo to capture a single-step graph instead of tracing through the entire forward pass?...
  - Expected topics: graph breaks, torch._dynamo, graph break resolution, operator fusion
- **J4-16**: AOTAutograd cache never hits even on a trivially simple program. Why does it always miss?...
  - Expected topics: graph breaks, torch._dynamo, caching, fullgraph mode, inductor backend
- **J4-17**: The PT2E quantization flow is completely broken on ARM/Graviton3 CPU with PyTorch 2.9.1. Is this a known issue?...
  - Expected topics: graph breaks, torch._dynamo, dynamic shapes, fullgraph mode, profiling
- **J4-18**: torch.compile with aotautograd doesn't support double backwards (grad of grad). Is there a workaround?...
  - Expected topics: graph breaks, torch._dynamo, backends, graph break resolution, torch.cond
- **J4-19**: I need better guardrails for combining distributed optimizations with non-fullgraph compile. The current behavior is con...
  - Expected topics: graph breaks, torch._dynamo, backends, CUDA graphs, dynamic shapes
- **J4-2**: torch.compile with DDP causes a graph break on _broadcast_coalesced. How do I use torch.compile with distributed trainin...
  - Expected topics: DDP, distributed, graph breaks, compile + DDP integration
- **J4-20**: Dynamo doesn't support Parameter subclasses. My custom Parameter type causes a graph break....
  - Expected topics: graph breaks, torch._dynamo, backends, fullgraph mode
- **J4-3**: I'm getting 'Unsupported: __self__ mismatch for bound method' graph break after upgrading PyTorch. What changed and how ...
  - Expected topics: graph breaks, bound methods, dynamo unsupported, migration
- **J4-4**: After upgrading to PyTorch 2.4, my torch.compile code that worked before now throws errors. How do I migrate my code and...
  - Expected topics: migration, version upgrade, graph breaks, breaking changes
- **J4-5**: I used torch.compiler.disable on a function but dynamo still traces into nested functions called from it. How do I prope...
  - Expected topics: torch.compiler.disable, graph breaks, skip tracing, nested functions
- **J4-6**: Dynamo fails when my model uses Python dataclasses. I get graph breaks because it can't track the dataclass fields. What...
  - Expected topics: dataclass, graph breaks, Python constructs, dynamo limitations
- **J4-7**: Dynamo recompiles every time because it's guarding on a global config variable that I change between calls. How do I pre...
  - Expected topics: guards, global variables, recompilation, dynamo config
- **J4-8**: torch.compile doesn't work properly with selective activation checkpointing (SAC). How do I combine compile with gradien...
  - Expected topics: activation checkpointing, SAC, graph breaks, memory optimization
- **J4-9**: I'm getting a graph break when calling create_block_mask for flex_attention inside a compiled function. How do I avoid t...
  - Expected topics: flex_attention, create_block_mask, graph breaks, higher-order ops

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J4-7 | Dynamo recompiles every time because it's guarding on a glob | 3→1 | 3→1 | No |
| J4-1 | I'm getting a graph break in my flex_attention code when usi | 3→1 | 3→2 | Yes |
| J4-10 | Dynamo can't trace through AdamW when I use a learning rate  | 3→1 | 3→2 | Yes |
| J4-17 | The PT2E quantization flow is completely broken on ARM/Gravi | 3→1 | 3→2 | No |
| J4-18 | torch.compile with aotautograd doesn't support double backwa | 3→1 | 3→2 | No |

---

### J2: Performance Diagnosis (Why Is It Slow?)

**20 cases** | Doc sufficient: 4/20 | Templates: 0/20
Act: 2.2 → 0.7 (Δ=1.6) | Diag: 2.9 → 2.1 (Δ=0.8)

**Missing mechanism documentation (5 cases):**
These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.

- **J2-10**: I'm seeing that some ops aren't supported by inductor. Where can I find a list of which ops are covered?...
  - Expected topics: performance profiling, torch.profiler, inductor backend, operator fusion
  - Act: 2→0 | Diag: 3→1
- **J2-12**: torch.compile produces extremely slow code for complex-valued tensors. Is complex number support optimized in inductor?...
  - Expected topics: performance profiling, torch.profiler, backends, inductor backend, error messages
  - Act: 2→0 | Diag: 3→1
- **J2-15**: torch.compile's decomposition of SDPA is actually faster than the EFFICIENT_ATTENTION backend on tf32. Shouldn't the fus...
  - Expected topics: performance profiling, torch.profiler, backends, memory optimization
  - Act: 2→0 | Diag: 3→1
- **J2-20**: How do I use torch.compile with an Intel GPU? Is XPU backend supported upstream?...
  - Expected topics: performance profiling, torch.profiler, backends
  - Act: 3→0 | Diag: 3→1
- **J2-7**: The GIL isn't released when calling torch.compile kernels, which blocks my multithreaded inference pipeline. Is this exp...
  - Expected topics: GIL, multithreading, compiled kernels, inference pipeline
  - Act: 2→0 | Diag: 3→1

**Missing fix/workaround documentation (4 cases):**
Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.

- **J2-1**: I wrapped my model with torch.compile but inference is actually slower than eager mode. How do I diagnose why?...
  - Expected topics: profiling, torch.profiler, compilation overhead, warmup
- **J2-20**: How do I use torch.compile with an Intel GPU? Is XPU backend supported upstream?...
  - Expected topics: performance profiling, torch.profiler, backends
- **J2-5**: torch.compile doesn't give me any speedup and after training I get 'free(): invalid pointer' crash. What's going wrong?...
  - Expected topics: no speedup, memory errors, compile debugging, expected speedup
- **J2-6**: I wrote a simple multi-head attention model and torch.compile with the inductor backend shows zero speedup. Is there som...
  - Expected topics: no speedup, inductor backend, model complexity, compilation warmup

**Missing causal explanations (12 cases):**
Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.

- **J2-1**: I wrapped my model with torch.compile but inference is actually slower than eager mode. How do I diagnose why?...
  - Act: 3→2 | Diag: 3→3
- **J2-10**: I'm seeing that some ops aren't supported by inductor. Where can I find a list of which ops are covered?...
  - Act: 2→0 | Diag: 3→1
- **J2-12**: torch.compile produces extremely slow code for complex-valued tensors. Is complex number support optimized in inductor?...
  - Act: 2→0 | Diag: 3→1
- **J2-13**: The inductor-generated backward kernel for float8 scaled_grouped_mm is much slower than eager. How do I get inductor to ...
  - Act: 2→0 | Diag: 3→2
- **J2-14**: Can inductor generate native tl.dot matmuls instead of going through aten? I think the extra indirection is hurting perf...
  - Act: 2→0 | Diag: 3→2
- **J2-15**: torch.compile's decomposition of SDPA is actually faster than the EFFICIENT_ATTENTION backend on tf32. Shouldn't the fus...
  - Act: 2→0 | Diag: 3→1
- **J2-16**: Inductor generates suboptimal kernels when a pointwise op feeds into a reduction. The fused kernel is slower than separa...
  - Act: 2→0 | Diag: 3→2
- **J2-17**: torch._foreach_copy_ on CUDA tensors is much slower than a simple for-loop of tensor.copy_(). Why isn't the foreach vari...
  - Act: 2→0 | Diag: 3→1
- **J2-2**: torch.compile makes my backward pass 100x slower for torch.cumprod. How do I figure out what's going wrong?...
  - Act: 2→2 | Diag: 3→3
- **J2-5**: torch.compile doesn't give me any speedup and after training I get 'free(): invalid pointer' crash. What's going wrong?...
  - Act: 3→2 | Diag: 3→3
- **J2-7**: The GIL isn't released when calling torch.compile kernels, which blocks my multithreaded inference pipeline. Is this exp...
  - Act: 2→0 | Diag: 3→1
- **J2-9**: I've been trying hard but torch.compile consistently makes my decoder model slower, not faster. What should I check to u...
  - Act: 2→2 | Diag: 3→3

**Largest individual drops (top 5):**

| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |
|------|---------------------|-----------|------------|---------|
| J2-20 | How do I use torch.compile with an Intel GPU? Is XPU backend | 3→0 | 3→1 | No |
| J2-10 | I'm seeing that some ops aren't supported by inductor. Where | 2→0 | 3→1 | No |
| J2-12 | torch.compile produces extremely slow code for complex-value | 2→0 | 3→1 | No |
| J2-15 | torch.compile's decomposition of SDPA is actually faster tha | 2→0 | 3→1 | No |
| J2-17 | torch._foreach_copy_ on CUDA tensors is much slower than a s | 2→0 | 3→1 | No |

---

## Cross-Cutting Analysis

### Missing Documentation Topics

Aggregating `expected_doc_topics` from cases with the largest gaps (Act drop ≥ 2 or Diag drop ≥ 2):

**138 cases** with high documentation gaps (≥2 point drop):

- **dynamic shapes** — 25 cases
- **inductor backend** — 24 cases
- **recompilation** — 16 cases
- **backends** — 15 cases
- **caching** — 14 cases
- **error messages** — 14 cases
- **inductor** — 14 cases
- **higher-order ops** — 14 cases
- **graph breaks** — 13 cases
- **triton** — 13 cases
- **repro_level** — 13 cases
- **flex_attention** — 12 cases
- **minifier** — 11 cases
- **compilation time** — 11 cases
- **performance profiling** — 10 cases
- **torch.profiler** — 10 cases
- **performance optimization** — 10 cases
- **custom operators** — 10 cases
- **CUDA graphs** — 9 cases
- **correctness debugging** — 9 cases
- **accuracy** — 9 cases
- **profiling** — 8 cases
- **memory optimization** — 7 cases
- **max-autotune** — 7 cases
- **torch.compile** — 6 cases
- **torch.export** — 6 cases
- **guards** — 6 cases
- **torch.compile basics** — 5 cases
- **getting started** — 5 cases
- **operator fusion** — 5 cases

### Mechanism Documentation Gaps (names_mechanism analysis)

Per Peng's insight: when Track 1 achieves names_mechanism=true but Track 2 achieves names_mechanism=false, this directly measures **missing mechanism-level documentation**. The doc-restricted agent can only cite diagnostic tools (TORCH_LOGS, profiler); the underlying mechanisms that explain root causes are not documented.

**Total mechanism gaps: 36/160 cases (22%)**

| Journey | Cases with NM gap | Example topics needing mechanism docs |
|---------|-------------------|--------------------------------------|
| J1: First Compile (Getting Started) | 5 | CUDA compatibility, Ray, Triton errors, backend debugging, caching |
| J2: Performance Diagnosis (Why Is It Slow?) | 5 | GIL, backends, compiled kernels, error messages, inductor backend |
| J3: Correctness & Debugging (Wrong Results) | 16 | CPU correctness, CUDA graphs, Conv2d, accuracy, accuracy debugging |
| J4: Graph Breaks | 1 | dynamo config, global variables, guards, recompilation |
| J5: Performance Optimization (Making It Faster) | 3 | autotuner bugs, debugging, error messages, inductor, inductor passes |
| J6: Dynamic Shapes | 1 | data-dependent shapes, dynamic slicing, unsupported operations, workarounds |
| J7: Compile-Time Performance (Compilation Too Slow) | 2 | caching, compilation time, error messages, max-autotune, profiling |
| J8: Custom & Higher-Order Ops | 3 | backends, custom operators, custom ops, dynamo compatibility, error messages |

### Template Response Analysis (Missing Documentation Pages)

Template responses indicate the agent found NO relevant documentation and fell back to generic boilerplate. These signal **entire missing pages**, not just missing details within existing pages.

**38 template responses across 2 journeys**

Documentation pages that likely need to be **created** (topics from template cases):

- **graph breaks** — 19 template cases
- **correctness debugging** — 10 template cases
- **accuracy** — 10 template cases
- **backends** — 10 template cases
- **torch._dynamo** — 10 template cases
- **minifier** — 7 template cases
- **fullgraph mode** — 6 template cases
- **repro_level** — 5 template cases
- **graph break resolution** — 4 template cases
- **numerical accuracy** — 3 template cases
- **inductor backend** — 3 template cases
- **recompilation** — 3 template cases
- **accuracy debugging** — 2 template cases
- **caching** — 2 template cases
- **CUDA graphs** — 2 template cases
- **max-autotune** — 2 template cases
- **operator fusion** — 2 template cases
- **memory optimization** — 2 template cases
- **flex_attention** — 2 template cases
- **higher-order ops** — 2 template cases

### Doc Sufficiency Breakdown

Cases where doc_sufficient=True maintained similar quality across tracks vs. cases where it didn't:

| Group | N | Mean Act Drop | Mean Diag Drop |
|-------|---|---------------|----------------|
| Doc sufficient=True | 22 | 1.23 | 0.41 |
| Doc sufficient=False | 138 | 2.33 | 1.04 |

### Gap by Issue Difficulty

| Difficulty | N | Mean Act Drop | Mean Diag Drop | Doc Sufficient |
|-----------|---|---------------|----------------|----------------|
| beginner | 15 | 1.67 | 0.53 | 5/15 (33%) |
| intermediate | 75 | 2.27 | 1.00 | 13/75 (17%) |
| advanced | 70 | 2.20 | 1.00 | 4/70 (6%) |

## Recommendations: Priority Documentation Work

Based on the gap analysis, documentation improvements are prioritized by impact (number of cases affected × severity of quality drop):

### Priority 1: High-Impact Gaps (entire pages or major sections needed)

**J3: Correctness & Debugging (Wrong Results)** (impact score: 78)
- 19/20 cases have ≥2-point quality drops
- Key missing topics: correctness debugging, accuracy, minifier, repro_level, backends
- 18 template responses (no relevant page found)
- 16 cases missing mechanism-level documentation

**J5: Performance Optimization (Making It Faster)** (impact score: 76)
- 19/20 cases have ≥2-point quality drops
- Key missing topics: inductor, performance optimization, CUDA graphs, inductor backend, triton
- 3 cases missing mechanism-level documentation

**J8: Custom & Higher-Order Ops** (impact score: 69)
- 20/20 cases have ≥2-point quality drops
- Key missing topics: higher-order ops, custom operators, flex_attention, custom ops, torch.library
- 3 cases missing mechanism-level documentation

### Priority 2: Mechanism Documentation (explanations of how things work)

These topics have diagnostic tool references in the docs but lack explanations of the underlying mechanisms. Users can be told to "check TORCH_LOGS" but not told *what* the logs will reveal or *why* the issue occurs.

- **J1: First Compile (Getting Started)** — 5 cases need mechanism docs
  - CUDA compatibility
  - Ray
  - Triton errors
  - backend debugging
  - caching
  - compile cache
  - distributed
  - error messages
  - getting started
  - inductor
  - inductor backend
  - multiprocessing
  - torch.compile
  - torch.compile basics
- **J2: Performance Diagnosis (Why Is It Slow?)** — 5 cases need mechanism docs
  - GIL
  - backends
  - compiled kernels
  - error messages
  - inductor backend
  - inference pipeline
  - memory optimization
  - multithreading
  - operator fusion
  - performance profiling
  - torch.profiler
- **J3: Correctness & Debugging (Wrong Results)** — 16 cases need mechanism docs
  - CPU correctness
  - CUDA graphs
  - Conv2d
  - accuracy
  - accuracy debugging
  - accuracy tolerance
  - backends
  - backward correctness
  - caching
  - compile correctness
  - composition bugs
  - correctness debugging
  - debugging
  - deterministic
  - inductor backend
  - inductor bugs
  - max-autotune
  - memory optimization
  - minifier
  - numerical accuracy
  - numerical divergence
  - numerical precision
  - operator correctness
  - operator fusion
  - operator isolation
  - precision errors
  - random seed
  - recompilation
  - repro_level
  - reproducibility
  - silent correctness
  - tolerance thresholds
  - torch._dynamo.config.repro_level
  - torch.export
  - torch.func.grad
  - wrong results
- **J4: Graph Breaks** — 1 cases need mechanism docs
  - dynamo config
  - global variables
  - guards
  - recompilation
- **J5: Performance Optimization (Making It Faster)** — 3 cases need mechanism docs
  - autotuner bugs
  - debugging
  - error messages
  - inductor
  - inductor passes
  - max-autotune
  - memory alignment
  - optimization errors
  - performance optimization
  - split_cat optimization
  - template selection
- **J6: Dynamic Shapes** — 1 cases need mechanism docs
  - data-dependent shapes
  - dynamic slicing
  - unsupported operations
  - workarounds
- **J7: Compile-Time Performance (Compilation Too Slow)** — 2 cases need mechanism docs
  - caching
  - compilation time
  - error messages
  - max-autotune
  - profiling
  - recompilation
  - repro_level
  - triton
- **J8: Custom & Higher-Order Ops** — 3 cases need mechanism docs
  - backends
  - custom operators
  - custom ops
  - dynamo compatibility
  - error messages
  - higher-order ops
  - inductor backend
  - pytorch_cluster
  - third-party ops
  - torch.scan

### Priority 3: Workaround/Fix Documentation

Cases where Track 1 provides a standalone fix but Track 2 cannot — the workaround exists but isn't documented:

- **J1: First Compile (Getting Started)** — 9 undocumented fixes
  - AMP compatibility
  - CUDA
  - CUDA device
  - DDP integration
  - DTensor
  - Ray
  - autograd.grad
  - backend compatibility
  - compile cache
  - device placement
  - distributed
  - dynamo limitations
  - error messages
  - getting started
  - graph breaks
  - inductor
  - inductor backend
  - installation
  - linker
  - mixed precision
  - multi-GPU
  - multiprocessing
  - setup
  - tensor parallel
  - torch.compile
  - torch.compile + TP
  - torch.compile basics
  - torch.compile limitations
  - torch.compile ordering
  - torch.compile setup
  - troubleshooting
- **J2: Performance Diagnosis (Why Is It Slow?)** — 4 undocumented fixes
  - backends
  - compilation overhead
  - compilation warmup
  - compile debugging
  - expected speedup
  - inductor backend
  - memory errors
  - model complexity
  - no speedup
  - performance profiling
  - profiling
  - torch.profiler
  - warmup
- **J3: Correctness & Debugging (Wrong Results)** — 7 undocumented fixes
  - GQA
  - NaN gradients
  - SDPA
  - accuracy
  - accuracy debugging
  - backends
  - backward pass
  - compile correctness
  - correctness debugging
  - deterministic
  - fullgraph mode
  - inductor bugs
  - max-autotune
  - minifier
  - numerical accuracy
  - operator correctness
  - operator isolation
  - precision errors
  - random seed
  - recompilation
  - reproducibility
  - stride correctness
  - wrong results
- **J4: Graph Breaks** — 13 undocumented fixes
  - CUDA graphs
  - DDP
  - LR scheduler
  - Python constructs
  - SAC
  - activation checkpointing
  - backends
  - bound methods
  - compile + DDP integration
  - create_block_mask
  - dataclass
  - distributed
  - dynamic shapes
  - dynamo config
  - dynamo limitations
  - dynamo tracing
  - dynamo unsupported
  - flex_attention
  - fullgraph mode
  - global variables
  - graph break resolution
  - graph breaks
  - guards
  - higher-order ops
  - memory optimization
  - migration
  - nested functions
  - optimizer compilation
  - profiling
  - recompilation
  - skip tracing
  - torch._dynamo
  - torch.compiler.disable
  - torch.cond
- **J5: Performance Optimization (Making It Faster)** — 16 undocumented fixes
  - CUDA graphs
  - GPU resources
  - Triton kernels
  - attention optimization
  - autotuner bugs
  - autotuning
  - cudagraph_trees
  - debugging
  - dynamic shapes
  - embedding
  - error messages
  - flex_attention
  - inductor
  - inductor backend
  - inductor passes
  - kernel optimization
  - mask composition
  - max-autotune
  - memory alignment
  - minifier
  - mode combinations
  - operator fusion
  - optimization errors
  - performance
  - performance optimization
  - performance paradox
  - performance regression
  - performance tuning
  - precision tradeoffs
  - profiling
  - quantization
  - reduce-overhead
  - repro_level
  - resource limits
  - shared memory
  - specialization
  - split_cat optimization
  - template selection
  - triton
- **J6: Dynamic Shapes** — 9 undocumented fixes
  - AMP
  - GNN
  - audio models
  - backends
  - basic usage
  - data-dependent shapes
  - dtype guards
  - dynamic shapes
  - dynamic slicing
  - dynamo errors
  - empty tensors
  - guard failures
  - guard specialization
  - inductor backend
  - mixed precision
  - neighbor sampling
  - recompilation
  - recompilation limit
  - reduction ops
  - regression
  - size mismatch
  - symbolic shapes
  - torch.compile dynamic
  - unsupported operations
  - variable batch size
  - variable length
  - wav2vec2
  - workarounds
- **J7: Compile-Time Performance (Compilation Too Slow)** — 13 undocumented fixes
  - AOTAutograd
  - CPU compilation
  - LR scheduler
  - caching
  - compilation time
  - compile overhead
  - compile time
  - compile time variance
  - distributed training
  - dynamo tracing
  - error messages
  - for loop tracing
  - gradient tracing
  - graph complexity
  - guards
  - inductor backend
  - inductor config
  - inline_inbuilt_nn_modules
  - input size
  - large models
  - loop compilation
  - loop unrolling
  - max-autotune
  - memory optimization
  - minifier
  - optimizer compilation
  - optimizer guards
  - parameter count
  - profiling
  - recompilation
  - repro_level
  - specialization
  - tensor wrapping
  - torch.export
  - triton
  - vector ISA detection
- **J8: Custom & Higher-Order Ops** — 12 undocumented fixes
  - CUDA graphs
  - backends
  - backward pass
  - caching
  - compile limitations
  - cond
  - control flow
  - custom operators
  - custom ops
  - custom_op decorator
  - dynamo compatibility
  - dynamo custom op
  - error messages
  - flex_attention
  - float32_matmul_precision
  - higher-order ops
  - inductor
  - inductor backend
  - inductor lowering
  - max-autotune
  - minifier
  - numerical accuracy
  - performance
  - precision
  - pytorch_cluster
  - repro_level
  - segfault debugging
  - stateful modules
  - third-party ops
  - torch.compile
  - torch.library
  - triton
  - while_loop

## Appendix: All Cases Sorted by Gap Severity

| Case | Journey | T1 Act | T2 Act | T1 Diag | T2 Diag | Total Drop | Doc Suf | Template | NM Gap |
|------|---------|--------|--------|---------|---------|------------|---------|----------|--------|
| J1-14 | J1 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J1-20 | J1 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J2-20 | J2 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J3-12 | J3 | 3 | 0 | 3 | 1 | 5 | N | Y | Y |
| J3-14 | J3 | 3 | 0 | 3 | 1 | 5 | N | Y | Y |
| J3-17 | J3 | 3 | 0 | 3 | 1 | 5 | N | Y | Y |
| J3-7 | J3 | 3 | 0 | 3 | 1 | 5 | N | Y | Y |
| J5-11 | J5 | 3 | 0 | 3 | 1 | 5 | N |  |  |
| J5-4 | J5 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J5-6 | J5 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J5-9 | J5 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J6-8 | J6 | 3 | 0 | 3 | 1 | 5 | N |  | Y |
| J1-13 | J1 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J1-16 | J1 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J1-17 | J1 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J1-19 | J1 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J1-7 | J1 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J1-8 | J1 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J2-10 | J2 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J2-12 | J2 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J2-15 | J2 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J2-17 | J2 | 2 | 0 | 3 | 1 | 4 | N |  |  |
| J2-7 | J2 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J3-1 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-10 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-13 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-15 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-16 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-18 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-19 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-2 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-5 | J3 | 3 | 0 | 2 | 1 | 4 | N |  | Y |
| J3-6 | J3 | 2 | 0 | 3 | 1 | 4 | N | Y | Y |
| J3-8 | J3 | 3 | 0 | 3 | 2 | 4 | N | Y |  |
| J4-7 | J4 | 3 | 1 | 3 | 1 | 4 | N | Y | Y |
| J5-1 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-10 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-12 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-13 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-14 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-17 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-18 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-19 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-2 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-3 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J5-7 | J5 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-10 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-2 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-20 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-4 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-6 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-7 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J6-9 | J6 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J7-10 | J7 | 3 | 0 | 3 | 2 | 4 | N |  | Y |
| J7-13 | J7 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J7-14 | J7 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J7-19 | J7 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J7-2 | J7 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J7-5 | J7 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J7-6 | J7 | 3 | 0 | 3 | 2 | 4 | N |  | Y |
| J8-10 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-13 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-15 | J8 | 2 | 0 | 3 | 1 | 4 | N |  | Y |
| J8-17 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-19 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-2 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-3 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-7 | J8 | 3 | 0 | 3 | 2 | 4 | N |  | Y |
| J8-8 | J8 | 3 | 0 | 3 | 2 | 4 | N |  |  |
| J8-9 | J8 | 3 | 0 | 3 | 2 | 4 | N |  | Y |
| J1-12 | J1 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J1-15 | J1 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J1-18 | J1 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J1-6 | J1 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J2-13 | J2 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J2-14 | J2 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J2-16 | J2 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J2-18 | J2 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J3-11 | J3 | 2 | 1 | 3 | 1 | 3 | N | Y | Y |
| J3-20 | J3 | 3 | 1 | 3 | 2 | 3 | N | Y |  |
| J3-3 | J3 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J3-4 | J3 | 2 | 0 | 3 | 2 | 3 | N | Y |  |
| J4-1 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-10 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-17 | J4 | 3 | 1 | 3 | 2 | 3 | N | Y |  |
| J4-18 | J4 | 3 | 1 | 3 | 2 | 3 | N | Y |  |
| J4-19 | J4 | 3 | 1 | 3 | 2 | 3 | N | Y |  |
| J4-2 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-20 | J4 | 3 | 1 | 3 | 2 | 3 | N | Y |  |
| J4-3 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-5 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-6 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-8 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J4-9 | J4 | 3 | 1 | 3 | 2 | 3 | Y | Y |  |
| J5-15 | J5 | 3 | 0 | 2 | 2 | 3 | N |  |  |
| J5-16 | J5 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J5-8 | J5 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-11 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-12 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-13 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-15 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-17 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-18 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-19 | J6 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J6-3 | J6 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J7-1 | J7 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J7-11 | J7 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J7-15 | J7 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J7-16 | J7 | 3 | 0 | 3 | 3 | 3 | Y |  |  |
| J7-17 | J7 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J7-20 | J7 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J7-3 | J7 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J7-4 | J7 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J7-7 | J7 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J7-8 | J7 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J7-9 | J7 | 3 | 0 | 3 | 3 | 3 | Y |  |  |
| J8-1 | J8 | 3 | 0 | 2 | 2 | 3 | N |  |  |
| J8-11 | J8 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J8-12 | J8 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J8-14 | J8 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J8-16 | J8 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J8-18 | J8 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J8-20 | J8 | 2 | 0 | 3 | 2 | 3 | N |  |  |
| J8-4 | J8 | 3 | 0 | 2 | 2 | 3 | N |  |  |
| J8-6 | J8 | 3 | 0 | 3 | 3 | 3 | N |  |  |
| J1-10 | J1 | 2 | 0 | 2 | 2 | 2 | N |  |  |
| J1-11 | J1 | 2 | 0 | 3 | 3 | 2 | Y |  |  |
| J1-4 | J1 | 3 | 1 | 3 | 3 | 2 | N |  |  |
| J2-11 | J2 | 2 | 0 | 3 | 3 | 2 | N |  |  |
| J2-19 | J2 | 2 | 0 | 1 | 1 | 2 | N |  |  |
| J2-4 | J2 | 2 | 0 | 3 | 3 | 2 | N |  |  |
| J2-8 | J2 | 2 | 0 | 3 | 3 | 2 | N |  |  |
| J3-9 | J3 | 1 | 0 | 2 | 1 | 2 | N | Y | Y |
| J4-12 | J4 | 2 | 1 | 3 | 2 | 2 | N | Y |  |
| J4-13 | J4 | 2 | 1 | 3 | 2 | 2 | N | Y |  |
| J4-14 | J4 | 2 | 1 | 3 | 2 | 2 | N | Y |  |
| J4-15 | J4 | 2 | 1 | 3 | 2 | 2 | N | Y |  |
| J4-16 | J4 | 2 | 1 | 3 | 2 | 2 | N | Y |  |
| J4-4 | J4 | 2 | 1 | 3 | 2 | 2 | Y | Y |  |
| J5-20 | J5 | 2 | 0 | 2 | 2 | 2 | N |  |  |
| J6-14 | J6 | 2 | 0 | 2 | 2 | 2 | N |  |  |
| J6-16 | J6 | 2 | 0 | 3 | 3 | 2 | N |  |  |
| J7-12 | J7 | 2 | 0 | 2 | 2 | 2 | N |  |  |
| J7-18 | J7 | 2 | 0 | 2 | 2 | 2 | N |  |  |
| J8-5 | J8 | 2 | 0 | 3 | 3 | 2 | N |  |  |
| J1-3 | J1 | 3 | 2 | 3 | 3 | 1 | N |  |  |
| J2-1 | J2 | 3 | 2 | 3 | 3 | 1 | Y |  |  |
| J2-5 | J2 | 3 | 2 | 3 | 3 | 1 | N |  |  |
| J2-6 | J2 | 3 | 2 | 3 | 3 | 1 | Y |  |  |
| J5-5 | J5 | 1 | 1 | 3 | 2 | 1 | N |  |  |
| J1-1 | J1 | 3 | 3 | 3 | 3 | 0 | Y |  |  |
| J1-2 | J1 | 3 | 3 | 3 | 3 | 0 | Y |  |  |
| J1-5 | J1 | 3 | 3 | 3 | 3 | 0 | Y |  |  |
| J1-9 | J1 | 3 | 3 | 3 | 3 | 0 | Y |  |  |
| J2-2 | J2 | 2 | 2 | 3 | 3 | 0 | N |  |  |
| J2-3 | J2 | 3 | 3 | 3 | 3 | 0 | Y |  |  |
| J2-9 | J2 | 2 | 2 | 3 | 3 | 0 | Y |  |  |
| J4-11 | J4 | 0 | 1 | 3 | 2 | 0 | N | Y |  |
| J6-1 | J6 | 3 | 3 | 3 | 3 | 0 | Y |  |  |
| J6-5 | J6 | 3 | 3 | 3 | 3 | 0 | Y |  |  |

---
*Analysis generated by `scripts/doc_gap_analysis.py` from Owl's calibrated scoring data.*