#!/usr/bin/env python3
"""Build expanded test suite: 10 cases per journey (80 total).
Keeps existing 24 pilot entries (adding issue_context), adds 7 new per journey."""

import json

DATA_PATH = "/home/pengwu/projects/oss-model-graph-break-corpus/data/pt2-issues/pt2_all_issues.json"
PILOT_PATH = "/home/pengwu/.myclaw-rocky/spaces/AAQA_65oV7k/projects/corpus/pilot_test_suite.json"
OUTPUT_PATH = "/home/pengwu/.myclaw-rocky/spaces/AAQA_65oV7k/projects/corpus/expanded_test_suite.json"

# Load data
with open(DATA_PATH) as f:
    all_issues = json.load(f)
issue_by_num = {i["number"]: i for i in all_issues}

with open(PILOT_PATH) as f:
    pilot = json.load(f)


def get_issue_context(issue_num, max_chars=1500):
    """Get first max_chars of issue body."""
    if issue_num not in issue_by_num:
        return ""
    body = issue_by_num[issue_num].get("body", "") or ""
    if len(body) > max_chars:
        body = body[:max_chars] + "..."
    return body


# Add issue_context to existing pilot entries
for entry in pilot:
    entry["issue_context"] = get_issue_context(entry["source_issue"])

# Define new entries: 7 per journey
new_entries = [
    # ===== J1: First Compile (7 new) =====
    {
        "id": "J1-4",
        "journey": "J1: First Compile",
        "source_issue": 111794,
        "source_url": "https://github.com/pytorch/pytorch/issues/111794",
        "user_question": "I'm trying to use torch.compile with DDP and AMP together but I'm getting a NotImplementedError about autocast. Is there a specific order I need to wrap my model?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["DDP integration", "AMP compatibility", "torch.compile ordering", "mixed precision"]
    },
    {
        "id": "J1-5",
        "journey": "J1: First Compile",
        "source_issue": 92745,
        "source_url": "https://github.com/pytorch/pytorch/issues/92745",
        "user_question": "torch.compile fails on both CPU and CUDA with my ResNet50 model. I'm using the nightly Docker image. Is there something wrong with my setup?",
        "difficulty": "beginner",
        "expected_doc_topics": ["installation", "torch.compile setup", "backend compatibility", "troubleshooting"]
    },
    {
        "id": "J1-6",
        "journey": "J1: First Compile",
        "source_issue": 91794,
        "source_url": "https://github.com/pytorch/pytorch/issues/91794",
        "user_question": "I tried torch.compile() on resnet18 but the model actually runs slower. Am I using it wrong? What should I expect on first call?",
        "difficulty": "beginner",
        "expected_doc_topics": ["warmup", "compilation overhead", "first call latency", "when to use compile"]
    },
    {
        "id": "J1-7",
        "journey": "J1: First Compile",
        "source_issue": 108840,
        "source_url": "https://github.com/pytorch/pytorch/issues/108840",
        "user_question": "How do I use torch.compile together with Tensor Parallel? It crashes when I try to compile a tensor-parallelized model.",
        "difficulty": "advanced",
        "expected_doc_topics": ["tensor parallel", "distributed", "torch.compile + TP", "DTensor"]
    },
    {
        "id": "J1-8",
        "journey": "J1: First Compile",
        "source_issue": 97280,
        "source_url": "https://github.com/pytorch/pytorch/issues/97280",
        "user_question": "torch.compile doesn't seem to respect torch.cuda.set_device(). My compiled function puts tensors on the wrong GPU. Is this a known issue?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["multi-GPU", "device placement", "torch.compile limitations", "CUDA device"]
    },
    {
        "id": "J1-9",
        "journey": "J1: First Compile",
        "source_issue": 119054,
        "source_url": "https://github.com/pytorch/pytorch/issues/119054",
        "user_question": "I'm getting BackendCompilerFailed with 'device kernel image is invalid' when using torch.compile with inductor. How do I fix this Triton/CUDA error?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["inductor backend", "Triton errors", "CUDA compatibility", "backend debugging"]
    },
    {
        "id": "J1-10",
        "journey": "J1: First Compile",
        "source_issue": 113933,
        "source_url": "https://github.com/pytorch/pytorch/issues/113933",
        "user_question": "How can I save and reuse torch.compile results across different Python processes? I don't want to recompile every time I start a new process.",
        "difficulty": "intermediate",
        "expected_doc_topics": ["compile cache", "cross-process caching", "persistent cache", "torch._inductor.config"]
    },

    # ===== J2: Performance Diagnosis (7 new) =====
    {
        "id": "J2-4",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 138386,
        "source_url": "https://github.com/pytorch/pytorch/issues/138386",
        "user_question": "After upgrading from torch 2.4 to 2.5, my Llama2 inference with torch.compile(reduce-overhead) is noticeably slower. What changed and how do I diagnose the regression?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["version regression", "reduce-overhead", "profiling", "performance comparison"]
    },
    {
        "id": "J2-5",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 156103,
        "source_url": "https://github.com/pytorch/pytorch/issues/156103",
        "user_question": "My fully compiled Qwen3 model with torchtune is 4x slower than eager mode. Why would a full model compile be slower than no compile at all?",
        "difficulty": "advanced",
        "expected_doc_topics": ["full model compile", "inductor overhead", "large model compilation", "profiling"]
    },
    {
        "id": "J2-6",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 96047,
        "source_url": "https://github.com/pytorch/pytorch/issues/96047",
        "user_question": "torch.compile doesn't give me any speedup and after training I get 'free(): invalid pointer' crash. What's going wrong?",
        "difficulty": "beginner",
        "expected_doc_topics": ["no speedup", "memory errors", "compile debugging", "expected speedup"]
    },
    {
        "id": "J2-7",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 93611,
        "source_url": "https://github.com/pytorch/pytorch/issues/93611",
        "user_question": "I wrote a simple multi-head attention model and torch.compile with the inductor backend shows zero speedup. Is there something I'm doing wrong?",
        "difficulty": "beginner",
        "expected_doc_topics": ["no speedup", "inductor backend", "model complexity", "compilation warmup"]
    },
    {
        "id": "J2-8",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 163061,
        "source_url": "https://github.com/pytorch/pytorch/issues/163061",
        "user_question": "The GIL isn't released when calling torch.compile kernels, which blocks my multithreaded inference pipeline. Is this expected behavior?",
        "difficulty": "advanced",
        "expected_doc_topics": ["GIL", "multithreading", "compiled kernels", "inference pipeline"]
    },
    {
        "id": "J2-9",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 142817,
        "source_url": "https://github.com/pytorch/pytorch/issues/142817",
        "user_question": "FlexAttention backward pass is 12x slower than the forward pass at 32K sequence length. Is there a way to profile and fix the backward scaling?",
        "difficulty": "advanced",
        "expected_doc_topics": ["flex_attention", "backward pass performance", "scaling", "profiling"]
    },
    {
        "id": "J2-10",
        "journey": "J2: Performance Diagnosis",
        "source_issue": 134913,
        "source_url": "https://github.com/pytorch/pytorch/issues/134913",
        "user_question": "I've been trying hard but torch.compile consistently makes my decoder model slower, not faster. What should I check to understand why compile isn't helping?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["compile slowdown", "profiling", "model architecture", "when compile helps"]
    },

    # ===== J3: Correctness & Debugging (7 new) =====
    {
        "id": "J3-4",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 150859,
        "source_url": "https://github.com/pytorch/pytorch/issues/150859",
        "user_question": "My RMS norm layer produces NaNs when I use torch.compile with float8 and rowwise scales. The same code works fine in eager mode. How do I debug this?",
        "difficulty": "advanced",
        "expected_doc_topics": ["NaN debugging", "float8", "RMS norm", "precision", "compile correctness"]
    },
    {
        "id": "J3-5",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 159855,
        "source_url": "https://github.com/pytorch/pytorch/issues/159855",
        "user_question": "torch.compile gives different results every time I run it, even with the same input and seed. The eager version is deterministic. How do I fix this reproducibility issue?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["reproducibility", "deterministic", "compile correctness", "random seed"]
    },
    {
        "id": "J3-6",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 136662,
        "source_url": "https://github.com/pytorch/pytorch/issues/136662",
        "user_question": "When I compose torch.compile with torch.func.grad, I silently get a wrong result. No error is raised. How do I detect and debug silent correctness issues?",
        "difficulty": "advanced",
        "expected_doc_topics": ["silent correctness", "torch.func.grad", "composition bugs", "debugging"]
    },
    {
        "id": "J3-7",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 93078,
        "source_url": "https://github.com/pytorch/pytorch/issues/93078",
        "user_question": "dstack followed by reciprocal gives wrong results under torch.compile but correct results in eager. Is this a known inductor bug?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["wrong results", "operator correctness", "inductor bugs", "minifier"]
    },
    {
        "id": "J3-8",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 159469,
        "source_url": "https://github.com/pytorch/pytorch/issues/159469",
        "user_question": "torch.compile produces NaN gradients in the backward pass when using GQA with SDPA. Eager mode works fine. The bug seems related to tensor shape/stride.",
        "difficulty": "advanced",
        "expected_doc_topics": ["NaN gradients", "GQA", "SDPA", "stride correctness", "backward pass"]
    },
    {
        "id": "J3-9",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 173921,
        "source_url": "https://github.com/pytorch/pytorch/issues/173921",
        "user_question": "I'm seeing a 4.7% relative error in Conv2d output on CPU when using torch.compile vs eager mode. Is this level of numerical divergence expected?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["numerical divergence", "CPU correctness", "Conv2d", "tolerance thresholds"]
    },
    {
        "id": "J3-10",
        "journey": "J3: Correctness & Debugging",
        "source_issue": 145213,
        "source_url": "https://github.com/pytorch/pytorch/issues/145213",
        "user_question": "torch.compile introduces significant precision errors in my model's output compared to eager. How do I figure out which operation is causing the precision loss?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["precision errors", "accuracy debugging", "operator isolation", "minifier"]
    },

    # ===== J4: Graph Breaks (7 new) =====
    {
        "id": "J4-4",
        "journey": "J4: Graph Breaks",
        "source_issue": 133571,
        "source_url": "https://github.com/pytorch/pytorch/issues/133571",
        "user_question": "After upgrading to PyTorch 2.4, my torch.compile code that worked before now throws errors. How do I migrate my code and fix the new graph breaks?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["migration", "version upgrade", "graph breaks", "breaking changes"]
    },
    {
        "id": "J4-5",
        "journey": "J4: Graph Breaks",
        "source_issue": 123771,
        "source_url": "https://github.com/pytorch/pytorch/issues/123771",
        "user_question": "I used torch.compiler.disable on a function but dynamo still traces into nested functions called from it. How do I properly disable compilation for a section of my code?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["torch.compiler.disable", "graph breaks", "skip tracing", "nested functions"]
    },
    {
        "id": "J4-6",
        "journey": "J4: Graph Breaks",
        "source_issue": 116264,
        "source_url": "https://github.com/pytorch/pytorch/issues/116264",
        "user_question": "Dynamo fails when my model uses Python dataclasses. I get graph breaks because it can't track the dataclass fields. What's the workaround?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["dataclass", "graph breaks", "Python constructs", "dynamo limitations"]
    },
    {
        "id": "J4-7",
        "journey": "J4: Graph Breaks",
        "source_issue": 110682,
        "source_url": "https://github.com/pytorch/pytorch/issues/110682",
        "user_question": "Dynamo recompiles every time because it's guarding on a global config variable that I change between calls. How do I prevent guards on global state?",
        "difficulty": "advanced",
        "expected_doc_topics": ["guards", "global variables", "recompilation", "dynamo config"]
    },
    {
        "id": "J4-8",
        "journey": "J4: Graph Breaks",
        "source_issue": 161889,
        "source_url": "https://github.com/pytorch/pytorch/issues/161889",
        "user_question": "torch.compile doesn't work properly with selective activation checkpointing (SAC). How do I combine compile with gradient checkpointing?",
        "difficulty": "advanced",
        "expected_doc_topics": ["activation checkpointing", "SAC", "graph breaks", "memory optimization"]
    },
    {
        "id": "J4-9",
        "journey": "J4: Graph Breaks",
        "source_issue": 164349,
        "source_url": "https://github.com/pytorch/pytorch/issues/164349",
        "user_question": "I'm getting a graph break when calling create_block_mask for flex_attention inside a compiled function. How do I avoid this?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["flex_attention", "create_block_mask", "graph breaks", "higher-order ops"]
    },
    {
        "id": "J4-10",
        "journey": "J4: Graph Breaks",
        "source_issue": 107076,
        "source_url": "https://github.com/pytorch/pytorch/issues/107076",
        "user_question": "Dynamo can't trace through AdamW when I use a learning rate scheduler. It fails with graph breaks. How do I compile my optimizer step with an LR scheduler?",
        "difficulty": "advanced",
        "expected_doc_topics": ["optimizer compilation", "LR scheduler", "graph breaks", "dynamo tracing"]
    },

    # ===== J5: Performance Optimization (7 new) =====
    {
        "id": "J5-4",
        "journey": "J5: Performance Optimization",
        "source_issue": 124369,
        "source_url": "https://github.com/pytorch/pytorch/issues/124369",
        "user_question": "FlexAttention (templated attention) performance is really bad when I combine a causal mask with an upper square mask. Each mask alone is fast. Why does the combination kill performance?",
        "difficulty": "advanced",
        "expected_doc_topics": ["flex_attention", "mask composition", "performance tuning", "attention optimization"]
    },
    {
        "id": "J5-5",
        "journey": "J5: Performance Optimization",
        "source_issue": 122380,
        "source_url": "https://github.com/pytorch/pytorch/issues/122380",
        "user_question": "I'm getting a KeyError: 'dim' from UnbindCatRemover when torch.compile tries to optimize my model. Is this an inductor optimization pass bug?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["inductor passes", "optimization errors", "split_cat optimization", "debugging"]
    },
    {
        "id": "J5-6",
        "journey": "J5: Performance Optimization",
        "source_issue": 147463,
        "source_url": "https://github.com/pytorch/pytorch/issues/147463",
        "user_question": "I noticed a significant performance regression on nanogpt speedrun between two consecutive nightly builds. How do I bisect and report a compile performance regression?",
        "difficulty": "advanced",
        "expected_doc_topics": ["performance regression", "bisection", "nightly builds", "regression reporting"]
    },
    {
        "id": "J5-7",
        "journey": "J5: Performance Optimization",
        "source_issue": 133254,
        "source_url": "https://github.com/pytorch/pytorch/issues/133254",
        "user_question": "I'm getting 'shared memory out of resource' error when using compiled flex_attention on my RTX 4090. How do I work around GPU shared memory limits with torch.compile?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["shared memory", "GPU resources", "flex_attention", "resource limits"]
    },
    {
        "id": "J5-8",
        "journey": "J5: Performance Optimization",
        "source_issue": 177655,
        "source_url": "https://github.com/pytorch/pytorch/issues/177655",
        "user_question": "standalone_compile adds significant runtime overhead compared to regular torch.compile. Is there a way to reduce this overhead for production inference?",
        "difficulty": "advanced",
        "expected_doc_topics": ["standalone_compile", "runtime overhead", "production inference", "vLLM"]
    },
    {
        "id": "J5-9",
        "journey": "J5: Performance Optimization",
        "source_issue": 120667,
        "source_url": "https://github.com/pytorch/pytorch/issues/120667",
        "user_question": "My Triton kernel gets 1.35x slower when I add more specialization to it. Shouldn't more specialization make it faster? What's going on?",
        "difficulty": "advanced",
        "expected_doc_topics": ["Triton kernels", "specialization", "performance paradox", "kernel optimization"]
    },
    {
        "id": "J5-10",
        "journey": "J5: Performance Optimization",
        "source_issue": 125437,
        "source_url": "https://github.com/pytorch/pytorch/issues/125437",
        "user_question": "I'm getting misaligned address errors when using max-autotune with torch.compile. The autotuner picks a template that causes illegal memory access.",
        "difficulty": "advanced",
        "expected_doc_topics": ["max-autotune", "memory alignment", "template selection", "autotuner bugs"]
    },

    # ===== J6: Dynamic Shapes (7 new) =====
    {
        "id": "J6-4",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 94640,
        "source_url": "https://github.com/pytorch/pytorch/issues/94640",
        "user_question": "torch.compile fails on my GNN model trained with neighbor sampling because the input sizes change every batch. How do I use torch.compile with variable-size graph data?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["dynamic shapes", "GNN", "variable batch size", "neighbor sampling"]
    },
    {
        "id": "J6-5",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 121504,
        "source_url": "https://github.com/pytorch/pytorch/issues/121504",
        "user_question": "My custom attention implementation recompiles on every forward pass because the sequence length keeps changing. How do I avoid constant recompilation with variable sequence lengths?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["recompilation", "sequence length", "dynamic shapes", "mark_dynamic"]
    },
    {
        "id": "J6-6",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 139474,
        "source_url": "https://github.com/pytorch/pytorch/issues/139474",
        "user_question": "torch.compile hits 'Recompilation exhausted' with 'size mismatch at index 2'. I'm already using dynamic=True. Why does it still fail on changing input sizes?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["recompilation limit", "size mismatch", "dynamic shapes", "guard failures"]
    },
    {
        "id": "J6-7",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 105279,
        "source_url": "https://github.com/pytorch/pytorch/issues/105279",
        "user_question": "I set dynamic=True in torch.compile but it still doesn't work with my varying input shapes. I get errors about symbolic shapes. What am I doing wrong?",
        "difficulty": "beginner",
        "expected_doc_topics": ["dynamic shapes", "symbolic shapes", "torch.compile dynamic", "basic usage"]
    },
    {
        "id": "J6-8",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 123592,
        "source_url": "https://github.com/pytorch/pytorch/issues/123592",
        "user_question": "I'm getting 'Dynamic slicing on data-dependent value is not supported' from dynamo. How do I handle data-dependent indexing with torch.compile?",
        "difficulty": "advanced",
        "expected_doc_topics": ["data-dependent shapes", "dynamic slicing", "unsupported operations", "workarounds"]
    },
    {
        "id": "J6-9",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 128134,
        "source_url": "https://github.com/pytorch/pytorch/issues/128134",
        "user_question": "AMP autocast causes recompilation with 'dtype mismatch: expected Half, actual Float'. Why does torch.compile recompile when I use automatic mixed precision?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["AMP", "dtype guards", "recompilation", "mixed precision"]
    },
    {
        "id": "J6-10",
        "journey": "J6: Dynamic Shapes",
        "source_issue": 91719,
        "source_url": "https://github.com/pytorch/pytorch/issues/91719",
        "user_question": "torch.compile crashes on my wav2vec2 speech model because the audio input length varies. How do I make torch.compile work with variable-length audio inputs?",
        "difficulty": "beginner",
        "expected_doc_topics": ["dynamic shapes", "audio models", "variable length", "wav2vec2"]
    },

    # ===== J7: Compile-Time Performance (7 new) =====
    {
        "id": "J7-4",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 108971,
        "source_url": "https://github.com/pytorch/pytorch/issues/108971",
        "user_question": "torch.compile takes 17-30 minutes to compile my model even with a warm cache, and it causes NCCL timeouts in distributed training. How do I speed up compilation?",
        "difficulty": "advanced",
        "expected_doc_topics": ["slow compilation", "distributed training", "NCCL timeout", "compile time reduction"]
    },
    {
        "id": "J7-5",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 111441,
        "source_url": "https://github.com/pytorch/pytorch/issues/111441",
        "user_question": "torch.compile takes 34 seconds to compile a simple for loop. Is there a way to make dynamo handle loops faster?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["loop compilation", "dynamo tracing", "compile time", "loop unrolling"]
    },
    {
        "id": "J7-6",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 110506,
        "source_url": "https://github.com/pytorch/pytorch/issues/110506",
        "user_question": "Compiling my optimizer (Adam with 200+ parameters) takes 70 seconds because dynamo traces through every iteration of the for loop. How do I speed this up?",
        "difficulty": "advanced",
        "expected_doc_topics": ["optimizer compilation", "for loop tracing", "compile time", "parameter count"]
    },
    {
        "id": "J7-7",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 133898,
        "source_url": "https://github.com/pytorch/pytorch/issues/133898",
        "user_question": "My compiled AdamW optimizer recompiles every step when I use OneCycleLR scheduler. The learning rate change triggers a new compilation. How do I prevent this?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["recompilation", "LR scheduler", "optimizer guards", "tensor wrapping"]
    },
    {
        "id": "J7-8",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 140970,
        "source_url": "https://github.com/pytorch/pytorch/issues/140970",
        "user_question": "On CPU, torch._inductor.cpu_vec_isa.pick_vec_isa takes 9 seconds just to detect the vector ISA. Why is this so slow and can I skip it?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["CPU compilation", "vector ISA detection", "compile overhead", "inductor config"]
    },
    {
        "id": "J7-9",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 174704,
        "source_url": "https://github.com/pytorch/pytorch/issues/174704",
        "user_question": "After upgrading to PyTorch 2.10, recompilation times with FSDP and dynamic shapes went from 30 minutes to several hours. What changed in 2.10 that made recompilation so much slower?",
        "difficulty": "advanced",
        "expected_doc_topics": ["recompilation time", "FSDP", "dynamic shapes", "version regression"]
    },
    {
        "id": "J7-10",
        "journey": "J7: Compile-Time Performance",
        "source_issue": 135430,
        "source_url": "https://github.com/pytorch/pytorch/issues/135430",
        "user_question": "Compilation is 2x faster when my input size is 1 versus any other size. The forward pass time stays the same. Why does input size affect compile time so much?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["compile time variance", "input size", "specialization", "graph complexity"]
    },

    # ===== J8: Custom & Higher-Order Ops (7 new) =====
    {
        "id": "J8-4",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 139628,
        "source_url": "https://github.com/pytorch/pytorch/issues/139628",
        "user_question": "My custom op defined with torch.library causes an illegal memory access when used with torch.compile. The same op works in eager. How do I debug this?",
        "difficulty": "advanced",
        "expected_doc_topics": ["custom ops", "torch.library", "illegal memory access", "compile debugging"]
    },
    {
        "id": "J8-5",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 143773,
        "source_url": "https://github.com/pytorch/pytorch/issues/143773",
        "user_question": "I saved a TorchScript module that uses @custom_op, but loading it with jit.load() gives 'Unknown builtin op'. How do I make custom ops work with TorchScript serialization?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["custom ops", "TorchScript", "serialization", "jit.load"]
    },
    {
        "id": "J8-6",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 147551,
        "source_url": "https://github.com/pytorch/pytorch/issues/147551",
        "user_question": "Compiled FlexAttention gives illegal memory access or device-side assert errors even though all my tensors are contiguous and on the right device. What's causing this?",
        "difficulty": "advanced",
        "expected_doc_topics": ["flex_attention", "illegal memory access", "device-side assert", "debugging"]
    },
    {
        "id": "J8-7",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 136196,
        "source_url": "https://github.com/pytorch/pytorch/issues/136196",
        "user_question": "I can't compile flex_attention with dynamic shapes when my BlockMask depends on the batch dimension. How do I use dynamic shapes with batch-dependent block masks?",
        "difficulty": "advanced",
        "expected_doc_topics": ["flex_attention", "dynamic shapes", "BlockMask", "batch-dependent masks"]
    },
    {
        "id": "J8-8",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 138556,
        "source_url": "https://github.com/pytorch/pytorch/issues/138556",
        "user_question": "FlexAttention output deviates significantly from SDPA when I use torch.compile() with torch.set_float32_matmul_precision('high'). Is this a precision bug?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["flex_attention", "precision", "float32_matmul_precision", "numerical accuracy"]
    },
    {
        "id": "J8-9",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 95791,
        "source_url": "https://github.com/pytorch/pytorch/issues/95791",
        "user_question": "torch._dynamo.optimize fails on my code that uses pytorch_cluster's radius function with 'tensor has non-zero number of elements but data is not allocated'. How do I use third-party custom ops with dynamo?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["third-party ops", "dynamo compatibility", "custom ops", "pytorch_cluster"]
    },
    {
        "id": "J8-10",
        "journey": "J8: Custom & Higher-Order Ops",
        "source_issue": 98844,
        "source_url": "https://github.com/pytorch/pytorch/issues/98844",
        "user_question": "I'm trying to use torch.cond (control flow) with torch.compile but I'm getting various errors. What are the limitations of cond with compile?",
        "difficulty": "intermediate",
        "expected_doc_topics": ["cond", "control flow", "higher-order ops", "compile limitations"]
    },
]

# Add issue_context to all new entries
for entry in new_entries:
    entry["issue_context"] = get_issue_context(entry["source_issue"])

# Combine: pilot first, then new entries
expanded = pilot + new_entries

# Verify
from collections import Counter
journey_counts = Counter()
for entry in expanded:
    jkey = entry["id"].split("-")[0]
    journey_counts[jkey] += 1

print(f"Total entries: {len(expanded)}")
print(f"Entries per journey:")
for j in sorted(journey_counts.keys()):
    print(f"  {j}: {journey_counts[j]}")

# Verify no duplicate source issues
seen_issues = set()
for entry in expanded:
    if entry["source_issue"] in seen_issues:
        print(f"DUPLICATE: {entry['id']} uses issue #{entry['source_issue']}")
    seen_issues.add(entry["source_issue"])

# Verify all entries have issue_context
for entry in expanded:
    if not entry.get("issue_context"):
        print(f"MISSING CONTEXT: {entry['id']} #{entry['source_issue']}")
    elif len(entry["issue_context"]) < 50:
        print(f"SHORT CONTEXT: {entry['id']} #{entry['source_issue']} ({len(entry['issue_context'])} chars)")

# Save
with open(OUTPUT_PATH, "w") as f:
    json.dump(expanded, f, indent=2)

print(f"\nSaved to {OUTPUT_PATH}")
print(f"File size: {len(json.dumps(expanded, indent=2))} bytes")
