# User Journey Issue Analysis

Extracted from `pt2_all_issues.json` (9,277 PyTorch PT2 GitHub issues).
Filtered to 6810 user-facing issues (excluded CI/infra/test issues).

Each journey shows the 5 most representative real-user issues, selected by:
- Label and keyword classification confidence
- User-facing quality (real questions vs internal reports)
- Community engagement (comments + reactions)

---

## J1: First Compile (Getting Started)

*Users trying torch.compile for the first time, basic setup, migration from eager mode.*

**Candidate pool:** 692 issues

### 1. #156797: How to use compile cache?

- **URL:** https://github.com/pytorch/pytorch/issues/156797
- **Comments:** 5 | **Reactions:** 0
- **State:** closed | **Created:** 2025-06-25
- **Labels:** module: docs, oncall: pt2
- **User Question:** "How to use compile cache?"
- **Why Representative:** Matched via: label: module: docs; title keyword: \bhow\s+to\b.*\bcompile\b | Phrased as a direct user question | Directly about torch.compile usage | Labels: module: docs

### 2. #131313: How to create a custom op which can be compile by dynamo inductor?

- **URL:** https://github.com/pytorch/pytorch/issues/131313
- **Comments:** 3 | **Reactions:** 0
- **State:** closed | **Created:** 2024-07-22
- **Labels:** module: docs, triaged, module: custom-operators, oncall: pt2
- **User Question:** "How to create a custom op which can be compile by dynamo inductor?"
- **Why Representative:** Matched via: label: module: docs; title keyword: \bhow\s+to\b.*\bcompile\b | Phrased as a direct user question | Labels: module: docs, module: custom-operators

### 3. #91537: Unclear how to change compiler used by `torch.compile`

- **URL:** https://github.com/pytorch/pytorch/issues/91537
- **Comments:** 3 | **Reactions:** 0
- **State:** closed | **Created:** 2022-12-30
- **Labels:** module: docs, triaged, oncall: pt2, module: dynamo
- **User Question:** "How do I get torch.compile working? (Unclear how to change compiler used by `torch.compile`)"
- **Why Representative:** Matched via: label: module: docs; title keyword: \bhow\s+to\b.*\bcompile\b | Directly about torch.compile usage | Labels: module: docs, module: dynamo

### 4. #149094: How to skip backward specific steps in torch.compile

- **URL:** https://github.com/pytorch/pytorch/issues/149094
- **Comments:** 3 | **Reactions:** 0
- **State:** open | **Created:** 2025-03-13
- **Labels:** triaged, oncall: pt2
- **User Question:** "How to skip backward specific steps in torch.compile?"
- **Why Representative:** Matched via: title keyword: \bhow\s+to\b.*\bcompile\b | User-filed bug report with structured template | Directly about torch.compile usage

### 5. #149096: How to determine which part of torch.compile undergoes recompiling after caching

- **URL:** https://github.com/pytorch/pytorch/issues/149096
- **Comments:** 2 | **Reactions:** 0
- **State:** open | **Created:** 2025-03-13
- **Labels:** triaged, oncall: pt2
- **User Question:** "How to determine which part of torch.compile undergoes recompiling after caching?"
- **Why Representative:** Matched via: title keyword: \bhow\s+to\b.*\bcompile\b | User-filed bug report with structured template | Directly about torch.compile usage

---

## J2: Performance Diagnosis (Why Is It Slow?)

*Users noticing compiled code is slower than eager, profiling, understanding overheads.*

**Candidate pool:** 320 issues

### 1. #110666: Eval torch compile slower than eager for Torch 2.1.0

- **URL:** https://github.com/pytorch/pytorch/issues/110666
- **Comments:** 8 | **Reactions:** 0
- **State:** closed | **Created:** 2023-10-06
- **Labels:** high priority, module: regression, oncall: pt2
- **User Question:** "Why is torch.compile making my model slower? (Eval torch compile slower than eager for Torch 2.1.0)"
- **Why Representative:** Matched via: label: module: regression; title keyword: \bslower\s+than\s+eager\b; title keyword: \bcompil(e|ed)\b.*\bslower\b; title keyword: \bslower\s+than\b.*\b(pytorch|torch)\b | High engagement (8 comments, 0 reactions) | User-filed bug report with structured template | Labels: high priority, module: regression

### 2. #136263: torch.compile 100x slower than eager mode for torch.cumprod backward pass

- **URL:** https://github.com/pytorch/pytorch/issues/136263
- **Comments:** 5 | **Reactions:** 0
- **State:** closed | **Created:** 2024-09-18
- **Labels:** module: autograd, triaged, actionable, oncall: pt2, module: inductor, module: pt2-dispatcher
- **User Question:** "Why is torch.compile making my model slower? (torch.compile 100x slower than eager mode for torch.cumprod backward pass)"
- **Why Representative:** Matched via: title keyword: \bslower\s+than\s+eager\b; title keyword: \bcompil(e|ed)\b.*\bslower\b; body keyword: \bperformance\s+(regression|degradation)\b; title keyword: \bslower\s+than\b.*\b(pytorch|torch)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: autograd, actionable, module: inductor, module: pt2-dispatcher

### 3. #128354: torch.compile() function calling is slower than @torch.compile decorator.

- **URL:** https://github.com/pytorch/pytorch/issues/128354
- **Comments:** 6 | **Reactions:** 0
- **State:** closed | **Created:** 2024-06-10
- **Labels:** needs reproduction, triaged, oncall: pt2
- **User Question:** "Why is torch.compile making my model slower? (torch.compile() function calling is slower than @torch.compile decorator.)"
- **Why Representative:** Matched via: title keyword: \bcompil(e|ed)\b.*\bslower\b; title keyword: \bslower\b.*\bcompil(e|ed)\b; title keyword: \bslower\s+than\b.*\b(pytorch|torch)\b | High engagement (6 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: needs reproduction

### 4. #113933: How to  re-use torch.compile results in different python processes?

- **URL:** https://github.com/pytorch/pytorch/issues/113933
- **Comments:** 16 | **Reactions:** 0
- **State:** closed | **Created:** 2023-11-17
- **Labels:** high priority, feature, triaged, months, oncall: pt2, module: dynamic shapes
- **User Question:** "How to  re-use torch.compile results in different python processes?"
- **Why Representative:** Matched via: body keyword: \bcompil(e|ed)\b.*\bslower\b | High engagement (16 comments, 0 reactions) | Phrased as a direct user question | Directly about torch.compile usage | Labels: high priority, feature, months, module: dynamic shapes

### 5. #119611: torch.compile slower than eager on simple MLP

- **URL:** https://github.com/pytorch/pytorch/issues/119611
- **Comments:** 6 | **Reactions:** 0
- **State:** closed | **Created:** 2024-02-10
- **Labels:** module: performance, triaged, enhancement, oncall: pt2, module: inductor
- **User Question:** "Why is torch.compile making my model slower? (torch.compile slower than eager on simple MLP)"
- **Why Representative:** Matched via: title keyword: \bslower\s+than\s+eager\b; title keyword: \bcompil(e|ed)\b.*\bslower\b | High engagement (6 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: performance, enhancement, module: inductor

---

## J3: Correctness & Debugging (Wrong Results)

*Compiled model produces different/wrong results vs eager mode, silent correctness issues.*

**Candidate pool:** 418 issues

### 1. #178871: Incorrect output for non-power-of-2-sized fusion of scalar broadcast and scatter-add

- **URL:** https://github.com/pytorch/pytorch/issues/178871
- **Comments:** 2 | **Reactions:** 0
- **State:** open | **Created:** 2026-03-31
- **Labels:** triage review, module: correctness (silent), module: scatter & gather ops, oncall: pt2, module: inductor, bot-triaged
- **User Question:** "Why does torch.compile give wrong results? (Incorrect output for non-power-of-2-sized fusion of scalar broadcast and scatter-add)"
- **Why Representative:** Matched via: label: module: correctness (silent); body keyword: \bwrong\s+result\b; title keyword: \bincorrect\s+(result|output)\b; body keyword: \bsilent(ly)?\s+(wrong|incorrect|bad)\b | User-filed bug report with structured template | Labels: triage review, module: correctness (silent), module: scatter & gather ops, module: inductor

### 2. #155690: torch.compile produces incorrect output

- **URL:** https://github.com/pytorch/pytorch/issues/155690
- **Comments:** 2 | **Reactions:** 2
- **State:** closed | **Created:** 2025-06-11
- **Labels:** high priority, triaged, module: correctness (silent), oncall: pt2, module: inductor, pt2: ubn
- **User Question:** "Why does torch.compile give wrong results? (torch.compile produces incorrect output)"
- **Why Representative:** Matched via: label: module: correctness (silent); title keyword: \bincorrect\s+(result|output)\b; title keyword: \bproduces?\s+(wrong|different|incorrect)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: high priority, module: correctness (silent), module: inductor, pt2: ubn

### 3. #100794: `torch.compile`  produce wrong result in backward ad with  `conv2d + interpolate` when  interpolate`mode=nearest/bilinear/bicubic`

- **URL:** https://github.com/pytorch/pytorch/issues/100794
- **Comments:** 3 | **Reactions:** 1
- **State:** closed | **Created:** 2023-05-06
- **Labels:** high priority, triaged, module: correctness (silent), oncall: pt2
- **User Question:** "Why does torch.compile give wrong results? (`torch.compile`  produce wrong result in backward ad with  `conv2d + interpolate` when  interpolate`mode=nearest/bilinear/bicubic`)"
- **Why Representative:** Matched via: label: module: correctness (silent); title keyword: \bwrong\s+result\b; title keyword: \bproduces?\s+(wrong|different|incorrect)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: high priority, module: correctness (silent)

### 4. #168965: max_autotuned BMM produces wrong result when multiple threads are used

- **URL:** https://github.com/pytorch/pytorch/issues/168965
- **Comments:** 6 | **Reactions:** 0
- **State:** open | **Created:** 2025-11-24
- **Labels:** triaged, module: correctness (silent), oncall: pt2, oncall: export, oncall: cpu inductor, module: aotinductor
- **User Question:** "Why does torch.compile give wrong results? (max_autotuned BMM produces wrong result when multiple threads are used)"
- **Why Representative:** Matched via: label: module: correctness (silent); title keyword: \bwrong\s+result\b; title keyword: \bproduces?\s+(wrong|different|incorrect)\b | High engagement (6 comments, 0 reactions) | User-filed bug report with structured template | Labels: module: correctness (silent), oncall: export, oncall: cpu inductor, module: aotinductor

### 5. #109105: Inductor-Compiled Modules Produce  Incorrect Result When Handling Distributive Property of Multiplication

- **URL:** https://github.com/pytorch/pytorch/issues/109105
- **Comments:** 6 | **Reactions:** 0
- **State:** closed | **Created:** 2023-09-12
- **Labels:** triaged, oncall: pt2, module: inductor
- **User Question:** "Why does torch.compile give wrong results? (Inductor-Compiled Modules Produce  Incorrect Result When Handling Distributive Property of Multiplication)"
- **Why Representative:** Matched via: body keyword: \bwrong\s+result\b; title keyword: \bincorrect\s+(result|output)\b; title keyword: \bproduces?\s+(wrong|different|incorrect)\b; body keyword: \bdifferent\s+results?\b | High engagement (6 comments, 0 reactions) | User-filed bug report with structured template | Labels: module: inductor

---

## J4: Graph Breaks (Graph Break Errors)

*Users encountering graph breaks that fragment compilation and hurt performance.*

**Candidate pool:** 2053 issues

### 1. #164247: Dynamo graph break on flex attention code

- **URL:** https://github.com/pytorch/pytorch/issues/164247
- **Comments:** 7 | **Reactions:** 1
- **State:** closed | **Created:** 2025-09-30
- **Labels:** high priority, triaged, oncall: pt2, module: dynamo, module: graph breaks, module: higher order operators
- **User Question:** "How do I resolve this graph break? (Dynamo graph break on flex attention code)"
- **Why Representative:** Matched via: label: module: graph breaks; title keyword: \bgraph\s*break\b; body keyword: \bfullgraph\b; body keyword: \bfull_?graph\s*=\s*True\b | High engagement (7 comments, 1 reactions) | User-filed bug report with structured template | Labels: high priority, module: dynamo, module: graph breaks, module: higher order operators

### 2. #137476: torch.compile graph break: torch._dynamo.exc.Unsupported: __self__ mismatch for bound method

- **URL:** https://github.com/pytorch/pytorch/issues/137476
- **Comments:** 5 | **Reactions:** 0
- **State:** closed | **Created:** 2024-10-08
- **Labels:** high priority, triaged, module: regression, oncall: pt2, module: dynamo, module: graph breaks
- **User Question:** "How do I resolve this graph break? (torch.compile graph break: torch._dynamo.exc.Unsupported: __self__ mismatch for bound method)"
- **Why Representative:** Matched via: label: module: graph breaks; title keyword: \bgraph\s*break\b; body keyword: \bfullgraph\b; body keyword: \bfull_?graph\s*=\s*True\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: high priority, module: regression, module: dynamo, module: graph breaks

### 3. #139440: Graph break due to unsupported builtin torch._C._distributed_c10d.PyCapsule._broadcast_coalesced

- **URL:** https://github.com/pytorch/pytorch/issues/139440
- **Comments:** 9 | **Reactions:** 0
- **State:** closed | **Created:** 2024-10-31
- **Labels:** oncall: distributed, triaged, module: ddp, oncall: pt2, module: dynamo, module: graph breaks
- **User Question:** "How do I resolve this graph break? (Graph break due to unsupported builtin torch._C._distributed_c10d.PyCapsule._broadcast_coalesced)"
- **Why Representative:** Matched via: label: module: graph breaks; title keyword: \bgraph\s*break\b; title keyword: \bunsupported\b.*\b(builtin|op|function|call)\b; title keyword: \bBREAK\b | High engagement (9 comments, 0 reactions) | User-filed bug report with structured template | Labels: oncall: distributed, module: ddp, module: dynamo, module: graph breaks

### 4. #169112: `torch.compile(fullgraph=True, dynamic=True)` on CUDA fails when using `torch.utils.dlpack.to_dlpack` / `from_dlpack` (`torch._C._to_dlpack` skipped by Dynamo)

- **URL:** https://github.com/pytorch/pytorch/issues/169112
- **Comments:** 3 | **Reactions:** 0
- **State:** closed | **Created:** 2025-11-26
- **Labels:** triaged, module: dlpack, oncall: pt2, module: dynamo
- **User Question:** "How do I resolve this graph break? (`torch.compile(fullgraph=True, dynamic=True)` on CUDA fails when using `torch.utils.dlpack.to_dlpack` / `from_dlpack` (`torch._C._to_dlpack` skipped by Dynamo))"
- **Why Representative:** Matched via: body keyword: \bgraph\s*break\b; title keyword: \bfullgraph\b; title keyword: \bfull_?graph\s*=\s*True\b; body keyword: \bunsupported\b.*\b(builtin|op|function|call)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: dlpack, module: dynamo

### 5. #171865: torch.compile(fullgraph=True) fails with Unsupported error on torch.sparse_csr_tensor

- **URL:** https://github.com/pytorch/pytorch/issues/171865
- **Comments:** 2 | **Reactions:** 0
- **State:** closed | **Created:** 2026-01-07
- **Labels:** module: sparse, triaged, needs research, oncall: pt2, module: dynamo, module: graph breaks
- **User Question:** "How do I resolve this graph break? (torch.compile(fullgraph=True) fails with Unsupported error on torch.sparse_csr_tensor)"
- **Why Representative:** Matched via: label: module: graph breaks; title keyword: \bfullgraph\b; title keyword: \bfull_?graph\s*=\s*True\b; body keyword: \bunsupported\b.*\b(builtin|op|function|call)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: sparse, needs research, module: dynamo, module: graph breaks

---

## J5: Performance Optimization (Making It Faster)

*Users tuning compiled code for better performance, inductor options, kernel optimization.*

**Candidate pool:** 1805 issues

### 1. #161060: [Question] How to robustly prevent operator fusion in Inductor to workaround a compilation bug?

- **URL:** https://github.com/pytorch/pytorch/issues/161060
- **Comments:** 3 | **Reactions:** 0
- **State:** closed | **Created:** 2025-08-20
- **Labels:** oncall: pt2
- **User Question:** "How to robustly prevent operator fusion in Inductor to workaround a compilation bug?"
- **Why Representative:** Matched via: body keyword: \bfus(e|ion|ed|ing)\b.*\b(kernel|op|operator)\b; body keyword: \bmax[-_]?autotune\b | Phrased as a direct user question | User-filed bug report with structured template | Directly about torch.compile usage

### 2. #171672: torch.compile max-autotune and reduce-overhead much slower than default due to repeated CUDA graph instantiation

- **URL:** https://github.com/pytorch/pytorch/issues/171672
- **Comments:** 7 | **Reactions:** 0
- **State:** open | **Created:** 2026-01-04
- **Labels:** needs reproduction, triaged, module: cuda graphs, oncall: pt2, PT2-Bug-Bash
- **User Question:** "How can I optimize torch.compile performance? (torch.compile max-autotune and reduce-overhead much slower than default due to repeated CUDA graph instantiation)"
- **Why Representative:** Matched via: label: module: cuda graphs; body keyword: \binductor\b.*\b(perf|performance|slow|faster|optimization)\b; title keyword: \bmax[-_]?autotune\b; title keyword: \bcuda\s+graph\b | High engagement (7 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: needs reproduction, module: cuda graphs, PT2-Bug-Bash

### 3. #117602: If I use torch.compile to compile the whole graph，in the my own compiler, how to manage the memory in my own compiler? 

- **URL:** https://github.com/pytorch/pytorch/issues/117602
- **Comments:** 15 | **Reactions:** 0
- **State:** closed | **Created:** 2024-01-17
- **Labels:** oncall: pt2
- **User Question:** "If I use torch.compile to compile the whole graph，in the my own compiler, how to manage the memory in my own compiler?"
- **Why Representative:** Matched via: body keyword: \bfus(e|ion|ed|ing)\b.*\b(kernel|op|operator)\b | High engagement (15 comments, 0 reactions) | Phrased as a direct user question | User-filed bug report with structured template | Directly about torch.compile usage

### 4. #96693: torch.compile mode="max-autotune" precision appears to be lower

- **URL:** https://github.com/pytorch/pytorch/issues/96693
- **Comments:** 48 | **Reactions:** 3
- **State:** closed | **Created:** 2023-03-13
- **Labels:** high priority, needs reproduction, triaged, module: cuda graphs, oncall: pt2, module: inductor
- **User Question:** "How can I optimize torch.compile performance? (torch.compile mode="max-autotune" precision appears to be lower)"
- **Why Representative:** Matched via: label: module: cuda graphs; title keyword: \bmax[-_]?autotune\b | High engagement (48 comments, 3 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: high priority, needs reproduction, module: cuda graphs, module: inductor

### 5. #174575: torch.compile mode='reduce-overhead' regression: 7x slower cudaGraphLaunch and new cudagraph_trees.py overhead in PyTorch 2.10 vs 2.9

- **URL:** https://github.com/pytorch/pytorch/issues/174575
- **Comments:** 7 | **Reactions:** 0
- **State:** closed | **Created:** 2026-02-08
- **Labels:** module: performance, triaged, module: regression, module: cuda graphs, oncall: pt2, bot-triaged
- **User Question:** "How can I optimize torch.compile performance? (torch.compile mode='reduce-overhead' regression: 7x slower cudaGraphLaunch and new cudagraph_trees.py overhead in PyTorch 2.10 vs 2.9)"
- **Why Representative:** Matched via: label: module: performance; label: module: cuda graphs; body keyword: \bcuda\s+graph\b | High engagement (7 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: performance, module: regression, module: cuda graphs, bot-triaged

---

## J6: Dynamic Shapes (Dynamic Shape Issues)

*Issues with dynamic/variable input shapes causing recompilation or errors.*

**Candidate pool:** 976 issues

### 1. #113875: [dynamo/guards] Symbolic shape guard does not fail, thus failing to recompile when shape changes

- **URL:** https://github.com/pytorch/pytorch/issues/113875
- **Comments:** 4 | **Reactions:** 0
- **State:** closed | **Created:** 2023-11-16
- **Labels:** triaged, oncall: pt2, module: dynamic shapes
- **User Question:** "How do I handle dynamic shapes in torch.compile? (Symbolic shape guard does not fail, thus failing to recompile when shape changes)"
- **Why Representative:** Matched via: label: module: dynamic shapes; body keyword: \bdynamic\s+(shape|batch|size|input|dim)\b; title keyword: \bsymbolic\s+(shape|int|size)\b; body keyword: \bdynamic=True\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: dynamic shapes

### 2. #178530: Pytorch 2.11 regression: Division by zero exception on empty tensor with torch.compile and dynamic size

- **URL:** https://github.com/pytorch/pytorch/issues/178530
- **Comments:** 12 | **Reactions:** 2
- **State:** closed | **Created:** 2026-03-26
- **Labels:** module: crash, module: windows, triaged, module: regression, oncall: pt2, module: dynamic shapes
- **User Question:** "How do I handle dynamic shapes in torch.compile? (Pytorch 2.11 regression: Division by zero exception on empty tensor with torch.compile and dynamic size)"
- **Why Representative:** Matched via: label: module: dynamic shapes; title keyword: \bdynamic\s+(shape|batch|size|input|dim)\b; body keyword: \bdynamic=True\b; body keyword: \bunbacked\s+symint\b | High engagement (12 comments, 2 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: crash, module: windows, module: regression, module: dynamic shapes

### 3. #100055: pre_autograd `make_fx` broken with simple F.linear with symbolic shape

- **URL:** https://github.com/pytorch/pytorch/issues/100055
- **Comments:** 21 | **Reactions:** 0
- **State:** closed | **Created:** 2023-04-26
- **Labels:** triaged, oncall: pt2, module: dynamic shapes
- **User Question:** "How do I handle dynamic shapes in torch.compile? (pre_autograd `make_fx` broken with simple F.linear with symbolic shape)"
- **Why Representative:** Matched via: label: module: dynamic shapes; body keyword: \bdynamic\s+(shape|batch|size|input|dim)\b; title keyword: \bsymbolic\s+(shape|int|size)\b; body keyword: \bdynamic=True\b | High engagement (21 comments, 0 reactions) | User-filed bug report with structured template | Labels: module: dynamic shapes

### 4. #172822: torch.compile(dynamic=True) specializes batch dimension for LayerNorm backward, causing recompiles

- **URL:** https://github.com/pytorch/pytorch/issues/172822
- **Comments:** 6 | **Reactions:** 0
- **State:** closed | **Created:** 2026-01-20
- **Labels:** triaged, oncall: pt2, module: dynamic shapes
- **User Question:** "How do I handle dynamic shapes in torch.compile? (torch.compile(dynamic=True) specializes batch dimension for LayerNorm backward, causing recompiles)"
- **Why Representative:** Matched via: label: module: dynamic shapes; body keyword: \bdynamic\s+(shape|batch|size|input|dim)\b; title keyword: \bdynamic=True\b | High engagement (6 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: dynamic shapes

### 5. #111198: [Regression][PT2.1] sum operator fails with dynamo error when dynamic shape is True

- **URL:** https://github.com/pytorch/pytorch/issues/111198
- **Comments:** 8 | **Reactions:** 0
- **State:** closed | **Created:** 2023-10-13
- **Labels:** triaged, oncall: pt2, module: dynamic shapes
- **User Question:** "How do I handle dynamic shapes in torch.compile? ([PT2.1] sum operator fails with dynamo error when dynamic shape is True)"
- **Why Representative:** Matched via: label: module: dynamic shapes; title keyword: \bdynamic\s+(shape|batch|size|input|dim)\b; body keyword: \bdynamic=True\b | High engagement (8 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: dynamic shapes

---

## J7: Compile-Time Performance (Compilation Too Slow)

*Long compilation times, cold start, caching, recompilation exhaustion.*

**Candidate pool:** 366 issues

### 1. #146663: Exponentially slow compile time with repeated logsumexp when gradient is enabled

- **URL:** https://github.com/pytorch/pytorch/issues/146663
- **Comments:** 3 | **Reactions:** 0
- **State:** closed | **Created:** 2025-02-07
- **Labels:** oncall: pt2, module: compile-time
- **User Question:** "Why is compilation so slow? (Exponentially slow compile time with repeated logsumexp when gradient is enabled)"
- **Why Representative:** Matched via: label: module: compile-time; title keyword: \bcompil(e|ation)\s+(time|slow|long|latency)\b; title keyword: \bslow\s+compil(e|ation)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: compile-time

### 2. #121989: [inline_inbuilt_nn_modules] Long compilation time for hf_T5_generate inference cause timeout

- **URL:** https://github.com/pytorch/pytorch/issues/121989
- **Comments:** 9 | **Reactions:** 0
- **State:** closed | **Created:** 2024-03-15
- **Labels:** high priority, triaged, oncall: pt2, module: dynamo, module: guards, module: compile-time
- **User Question:** "Why is compilation so slow? (Long compilation time for hf_T5_generate inference cause timeout)"
- **Why Representative:** Matched via: label: module: compile-time; label: module: guards; title keyword: \bcompil(e|ation)\s+(time|slow|long|latency)\b; body keyword: \btakes?\s+(too\s+)?long\s+to\s+compile\b | High engagement (9 comments, 0 reactions) | User-filed bug report with structured template | Labels: high priority, module: dynamo, module: guards, module: compile-time

### 3. #128153: torch.compile Jamba: long compilation time with backend="eager"

- **URL:** https://github.com/pytorch/pytorch/issues/128153
- **Comments:** 3 | **Reactions:** 0
- **State:** open | **Created:** 2024-06-06
- **Labels:** triaged, oncall: pt2, module: dynamo, module: guards, module: compile-time
- **User Question:** "Why is compilation so slow? (torch.compile Jamba: long compilation time with backend="eager")"
- **Why Representative:** Matched via: label: module: compile-time; label: module: guards; title keyword: \bcompil(e|ation)\s+(time|slow|long|latency)\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: dynamo, module: guards, module: compile-time

### 4. #156797: How to use compile cache?

- **URL:** https://github.com/pytorch/pytorch/issues/156797
- **Comments:** 5 | **Reactions:** 0
- **State:** closed | **Created:** 2025-06-25
- **Labels:** module: docs, oncall: pt2
- **User Question:** "How to use compile cache?"
- **Why Representative:** Matched via: body keyword: \bcompil(e|ation)\s+(time|slow|long|latency)\b; title keyword: \bcompil(e|ation)\s+cach(e|ing)\b | Phrased as a direct user question | Directly about torch.compile usage | Labels: module: docs

### 5. #114206: [PT2] Compile Cold Start (Persistent Cacheing) - AOTAutograd may be bottleneck when `TORCHINDUCTOR_FX_GRAPH_CACHE=1`

- **URL:** https://github.com/pytorch/pytorch/issues/114206
- **Comments:** 19 | **Reactions:** 0
- **State:** open | **Created:** 2023-11-21
- **Labels:** needs reproduction, module: performance, triaged, topic: performance, oncall: pt2, module: aotdispatch
- **User Question:** "How do I use compile caching? (Compile Cold Start (Persistent Cacheing) - AOTAutograd may be bottleneck when `TORCHINDUCTOR_FX_GRAPH_CACHE=1`)"
- **Why Representative:** Matched via: label: module: compile-time; body keyword: \brecompil(e|ation|ing)\b; title keyword: \bcold\s+start\b; body keyword: \bcompil(e|ation)\s+overhead\b | High engagement (19 comments, 0 reactions) | Labels: needs reproduction, module: performance, topic: performance, module: aotdispatch

---

## J8: Custom & Higher-Order Ops

*Issues with custom operators, higher-order operators (flex attention, scan, etc.).*

**Candidate pool:** 651 issues

### 1. #134625: Compiled flex_attention backwards segfaults/crashes

- **URL:** https://github.com/pytorch/pytorch/issues/134625
- **Comments:** 14 | **Reactions:** 0
- **State:** closed | **Created:** 2024-08-27
- **Labels:** high priority, triaged, oncall: pt2, module: higher order operators, module: pt2-dispatcher, compile-cache
- **User Question:** "How do I use flex_attention with torch.compile? (Compiled flex_attention backwards segfaults/crashes)"
- **Why Representative:** Matched via: label: module: higher order operators; label: module: flex attention; body keyword: \bhigher[\s-]*order\s*(op|operator)\b; title keyword: \bflex[\s_]*attention\b | High engagement (14 comments, 0 reactions) | User-filed bug report with structured template | Labels: high priority, module: higher order operators, module: pt2-dispatcher, compile-cache

### 2. #154556: torch.compiled flex_attention + NJT raises `RuntimeError: Attempting to use FunctionalTensor on its own.`

- **URL:** https://github.com/pytorch/pytorch/issues/154556
- **Comments:** 9 | **Reactions:** 0
- **State:** closed | **Created:** 2025-05-28
- **Labels:** triaged, oncall: pt2, module: higher order operators, module: pt2-dispatcher, module: flex attention
- **User Question:** "How do I use flex_attention with torch.compile? (torch.compiled flex_attention + NJT raises `RuntimeError: Attempting to use FunctionalTensor on its own.`)"
- **Why Representative:** Matched via: label: module: higher order operators; label: module: flex attention; title keyword: \bflex[\s_]*attention\b | High engagement (9 comments, 0 reactions) | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: higher order operators, module: pt2-dispatcher, module: flex attention

### 3. #147267: flex_attention with N<128 tokens throws `CUDA error: device-side assert triggered`

- **URL:** https://github.com/pytorch/pytorch/issues/147267
- **Comments:** 4 | **Reactions:** 1
- **State:** closed | **Created:** 2025-02-15
- **Labels:** triaged, oncall: pt2, module: higher order operators, module: pt2-dispatcher, module: flex attention
- **User Question:** "How do I use flex_attention with torch.compile? (flex_attention with N<128 tokens throws `CUDA error: device-side assert triggered`)"
- **Why Representative:** Matched via: label: module: higher order operators; label: module: flex attention; title keyword: \bflex[\s_]*attention\b | User-filed bug report with structured template | Directly about torch.compile usage | Labels: module: higher order operators, module: pt2-dispatcher, module: flex attention

### 4. #135161: Significant Accuracy Difference between Compiled and Eager Flex Attention

- **URL:** https://github.com/pytorch/pytorch/issues/135161
- **Comments:** 25 | **Reactions:** 1
- **State:** closed | **Created:** 2024-09-04
- **Labels:** high priority, module: numerical-stability, triaged, oncall: pt2, module: higher order operators, module: pt2-dispatcher
- **User Question:** "How do I use flex_attention with torch.compile? (Significant Accuracy Difference between Compiled and Eager Flex Attention)"
- **Why Representative:** Matched via: label: module: higher order operators; label: module: flex attention; title keyword: \bflex[\s_]*attention\b | High engagement (25 comments, 1 reactions) | User-filed bug report with structured template | Labels: high priority, module: numerical-stability, module: higher order operators, module: pt2-dispatcher

### 5. #127320: [While_loop] How to use layer like `torch.nn.BatchNorm2d` with while_loop?

- **URL:** https://github.com/pytorch/pytorch/issues/127320
- **Comments:** 8 | **Reactions:** 0
- **State:** closed | **Created:** 2024-05-28
- **Labels:** triaged, module: xla, oncall: pt2, module: higher order operators, module: pt2-dispatcher
- **User Question:** "How to use layer like `torch.nn.BatchNorm2d` with while_loop?"
- **Why Representative:** Matched via: label: module: higher order operators; title keyword: \bwhile_loop\b | High engagement (8 comments, 0 reactions) | Phrased as a direct user question | User-filed bug report with structured template | Labels: module: xla, module: higher order operators, module: pt2-dispatcher

---

## Summary Statistics

| Journey | Candidate Pool | Selected |
|---------|---------------|----------|
| J1: First Compile (Getting Started) | 692 | 5 |
| J2: Performance Diagnosis (Why Is It Slow?) | 320 | 5 |
| J3: Correctness & Debugging (Wrong Results) | 418 | 5 |
| J4: Graph Breaks (Graph Break Errors) | 2053 | 5 |
| J5: Performance Optimization (Making It Faster) | 1805 | 5 |
| J6: Dynamic Shapes (Dynamic Shape Issues) | 976 | 5 |
| J7: Compile-Time Performance (Compilation Too Slow) | 366 | 5 |
| J8: Custom & Higher-Order Ops | 651 | 5 |

**Total classifications:** 7281 (issues can appear in multiple journeys)
