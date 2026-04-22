#!/usr/bin/env python3
"""
Build a balanced test suite for torch.compile documentation evaluation.

Target: 160 cases total = 8 journeys x (10 resolved + 10 unresolved)

Keeps all existing cases from expanded_test_suite.json, adds resolution_status,
renumbers IDs, and fills in missing cases from pt2_all_issues.json.
"""

import json
import re
import sys
from collections import defaultdict
from typing import Any

# Paths
ISSUES_PATH = "/home/pengwu/projects/oss-model-graph-break-corpus/data/pt2-issues/pt2_all_issues.json"
EXISTING_PATH = "/home/pengwu/projects/compile-qa-bench/data/expanded_test_suite.json"
OUTPUT_PATH = "/home/pengwu/projects/compile-qa-bench/data/balanced_test_suite.json"

# Journey definitions
JOURNEYS = {
    "J1": "J1: First Compile",
    "J2": "J2: Performance Diagnosis",
    "J3": "J3: Correctness & Debugging",
    "J4": "J4: Graph Breaks",
    "J5": "J5: Performance Optimization",
    "J6": "J6: Dynamic Shapes",
    "J7": "J7: Compile-Time Performance",
    "J8": "J8: Custom & Higher-Order Ops",
}

# --------------------------------------------------------------------------- #
# Classification logic
# --------------------------------------------------------------------------- #

def classify_issue(issue: dict) -> str | None:
    """Classify an issue into a journey based on labels and title/body keywords."""
    labels = set(issue.get("labels", []))
    title = (issue.get("title") or "").lower()
    body = (issue.get("body") or "").lower()
    text = title + " " + body[:3000]

    # Label-based classification (highest priority)
    if "module: graph breaks" in labels:
        return "J4"
    if "module: dynamic shapes" in labels:
        return "J6"
    if "module: correctness (silent)" in labels:
        return "J3"
    if "module: compile-time" in labels:
        return "J7"
    if "module: custom-operators" in labels or "module: higher order operators" in labels:
        return "J8"
    if "module: flex attention" in labels:
        return "J8"
    if "module: cuda graphs" in labels:
        return "J5"

    # Keyword-based classification
    # J4: Graph Breaks
    if re.search(r"graph.?break|fullgraph|graph_break|breaks_in_graph", text):
        return "J4"

    # J6: Dynamic Shapes
    if re.search(r"dynamic.?shape|recompil|guard|shape.?guard|symbolic.?int|unbacked", text):
        # Distinguish recompilation overhead (J7) from recompilation due to shapes (J6)
        if re.search(r"recompil.*slow|slow.*recompil|compilation.*time|compile.*time|cold.?start", text):
            return "J7"
        return "J6"

    # J3: Correctness & Debugging
    if re.search(r"wrong.?result|incorrect.?result|numerical|accuracy|silent.*error|correctness|diverge|mismatch.*output|output.*mismatch|produces.*different", text):
        return "J3"

    # J8: Custom & Higher-Order Ops
    if re.search(r"custom.?op|torch\.library|flex.?attention|while.?loop|scan|cond\b|higher.?order|wrap_with_set_grad|autograd\.function.*compile|vmap.*compile|functorch", text):
        return "J8"

    # J7: Compile-Time Performance
    if re.search(r"compile.*time|compilation.*slow|cold.?start|compile.*slow|compilation.*time|too.*long.*compil|compil.*forever|compil.*minutes|compil.*hours", text):
        return "J7"
    # Cache-related can be J7 (reducing compile overhead)
    if re.search(r"cache.*compil|compil.*cache|persistent.*cache|save.*cache|load.*cache", text):
        return "J7"

    # J2: Performance Diagnosis (slower than eager, runtime overhead, perf regression)
    if re.search(r"slower.*eager|eager.*faster|no.*speedup|regression.*perf|performance.*regression|torch\.compile.*slow(?!.*compil)|compiled.*slower|perf.*degradation", text):
        return "J2"
    if re.search(r"runtime.*overhead|overhead.*runtime|small.*graph.*overhead|overhead.*small", text):
        return "J2"
    if re.search(r"(?:slow|perf).*(?:inductor|compile|compiled)|(?:inductor|compile|compiled).*(?:slow|perf)(?!.*compil.*time)", text):
        # Performance issue with compiled code (not compilation time)
        if not re.search(r"compil(?:e|ation)\s+(?:time|speed|duration|overhead)", text):
            return "J2"

    # J5: Performance Optimization
    if "module: performance" in labels:
        # Could be J2 or J5 - check context
        if re.search(r"slower.*eager|eager.*faster|no.*speedup|diagnos|regression", text):
            return "J2"
        return "J5"
    if re.search(r"max.?autotune|triton|kernel.*optim|fus(?:ion|e)|inductor.*perf|cudagraph|cuda.?graph|optimize|tun(?:e|ing)|throughput", text):
        return "J5"

    # J1: First Compile (getting started, basic usage)
    if re.search(r"how.?to|getting.?start|basic.*usage|migrat|tutorial|documentation|doc.*issue|beginner|first.*time|new.*to|learn|example|api.*doc|torch\.compile\b.*(?:not|doesn.t|can.t).*work", text):
        return "J1"

    # Fallback: check module labels for broad classification
    if "module: inductor" in labels:
        if re.search(r"perf|speed|slow|fast|optim|throughput", text):
            return "J5"
        if re.search(r"error|crash|fail|bug|wrong|incorrect", text):
            return "J3"
        return "J5"
    if "module: dynamo" in labels:
        if re.search(r"error|crash|fail|bug", text):
            return "J4"  # Many dynamo errors are graph break related
        return "J1"

    return None


def is_ci_or_bot_issue(issue: dict) -> bool:
    """Filter out CI/bot/infra issues."""
    title = issue.get("title", "")
    if title.startswith("DISABLED") or title.startswith("UNSTABLE") or title.startswith("[CI]"):
        return True
    if re.match(r"^\[.*\]\s*(DISABLED|UNSTABLE)", title):
        return True
    # Filter out pure feature requests with no user problem
    labels = set(issue.get("labels", []))
    if "module: tests" in labels and "oncall: pt2" not in labels:
        return True
    return False


def assess_difficulty(issue: dict) -> str:
    """Assess issue difficulty."""
    labels = set(issue.get("labels", []))
    title = (issue.get("title") or "").lower()
    body = (issue.get("body") or "").lower()[:3000]
    text = title + " " + body

    # Advanced indicators
    if any(l in labels for l in ["module: higher order operators", "module: custom-operators",
                                   "module: cuda graphs", "module: flex attention",
                                   "module: aotdispatch", "module: pt2-dispatcher"]):
        return "advanced"
    if re.search(r"autograd\.function|custom.?op|triton.?kernel|cuda.?graph|vmap|functorch|aot|dispatch", text):
        return "advanced"

    # Beginner indicators
    if re.search(r"how.?to|getting.?start|basic|tutorial|beginner|first.*time|documentation|new.*to", text):
        return "beginner"
    if "module: docs" in labels or "module: compile ux" in labels:
        return "beginner"

    return "intermediate"


def extract_doc_topics(issue: dict, journey_key: str) -> list[str]:
    """Extract expected documentation topics from an issue."""
    labels = set(issue.get("labels", []))
    title = (issue.get("title") or "").lower()
    body = (issue.get("body") or "").lower()[:3000]
    text = title + " " + body
    topics = []

    # Journey-specific default topics
    journey_topics = {
        "J1": ["torch.compile basics", "getting started"],
        "J2": ["performance profiling", "torch.profiler"],
        "J3": ["correctness debugging", "accuracy"],
        "J4": ["graph breaks", "torch._dynamo"],
        "J5": ["performance optimization", "inductor"],
        "J6": ["dynamic shapes", "recompilation"],
        "J7": ["compilation time", "caching"],
        "J8": ["custom operators", "higher-order ops"],
    }
    topics.extend(journey_topics.get(journey_key, []))

    # Keyword-specific topics
    keyword_topic_map = {
        r"cache": "caching",
        r"backend": "backends",
        r"triton": "triton",
        r"cuda.?graph": "CUDA graphs",
        r"max.?autotune": "max-autotune",
        r"dynamic": "dynamic shapes",
        r"guard": "shape guards",
        r"recompil": "recompilation",
        r"graph.?break": "graph break resolution",
        r"fullgraph": "fullgraph mode",
        r"flex.?attention": "flex_attention",
        r"custom.?op": "custom operators",
        r"while.?loop": "while_loop",
        r"scan": "torch.scan",
        r"cond\b": "torch.cond",
        r"vmap": "vmap",
        r"autograd\.function": "autograd.Function",
        r"profil": "profiling",
        r"minif": "minifier",
        r"repro": "repro_level",
        r"accuracy|numerical": "numerical accuracy",
        r"export": "torch.export",
        r"onnx": "ONNX export",
        r"inductor": "inductor backend",
        r"fusion|fuse": "operator fusion",
        r"memory|oom": "memory optimization",
        r"distributed|ddp|fsdp": "distributed training",
        r"inference": "inference mode",
        r"quantiz": "quantization",
        r"error.*message|traceback|stack.?trace": "error messages",
        r"logging|log_level": "logging",
    }

    for pattern, topic in keyword_topic_map.items():
        if re.search(pattern, text) and topic not in topics:
            topics.append(topic)
            if len(topics) >= 5:
                break

    return topics[:5]


def write_user_question(issue: dict, journey_key: str) -> str:
    """Write a natural user question based on the issue.

    Strategy: Extract the core problem from the issue and rewrite it as something
    a frustrated user would actually type into a chat/search box.
    """
    title = issue.get("title", "")
    body = (issue.get("body") or "")[:3000]

    # Clean up the title - remove tags, cc mentions
    clean_title = re.sub(r"^\[.*?\]\s*", "", title)
    clean_title = re.sub(r"\s*cc\s+@.*$", "", clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r"\s*\(#\d+\)$", "", clean_title)
    clean_title = clean_title.strip()

    # First, check for hand-crafted questions for specific issues
    hand_crafted = _HAND_CRAFTED_QUESTIONS.get(issue["number"])
    if hand_crafted:
        return hand_crafted

    # If title is already a good question, clean it up and use it
    if "?" in clean_title and len(clean_title) > 20:
        q = clean_title
        if not q[0].isupper():
            q = q[0].upper() + q[1:]
        return q

    # If title starts with how/why/what/when/can/is/does, make it a question
    if re.match(r"(?i)^(how|why|what|when|can|is|does|should)\b", clean_title):
        q = clean_title
        if not q.endswith("?"):
            q += "?"
        if not q[0].isupper():
            q = q[0].upper() + q[1:]
        return q

    # Otherwise, synthesize a natural question from the issue content
    return _synthesize_question(issue, clean_title, body, journey_key)


# Hand-crafted natural questions for issues where auto-generation would be poor.
# These are written as a frustrated user would type them.
_HAND_CRAFTED_QUESTIONS = {
    # J1 unresolved
    155862: "I'm trying to export a HuggingFace model that uses StaticCache with torch.export but it fails. How do I handle static KV caches during export?",
    91439: "I'm trying to use torch.compile with a GRU model but it doesn't seem to be supported. Is there a workaround for compiling RNN-based models?",
    146152: "torch.export fails when I try to export TorchVision's FasterRCNN with MobileNetV3 backbone. How do I export detection models?",
    125984: "I get a RuntimeError when trying to torch.export code that uses torch.autograd.grad. Is autograd.grad supported in export?",
    92398: "Does torch.compile/inductor support complex-valued tensors? I'm getting errors with complex dtypes.",
    124245: "How do I set up the C++ compiler for torch.compile on Windows? The default builder doesn't seem to work.",
    151649: "Inductor's pattern matcher silently replaces reshape with view, which changes semantics when my tensor isn't contiguous. Is this a bug?",
    153410: "Can torch.export save/load support safetensors format or weights_only=True for security?",
    173369: "I need to export an ONNX model that includes Captum attribution heatmaps. How do I handle the Captum ops during export?",
    147170: "get_source_partitions() returns wrong results in the PT2E quantization flow. Am I using it correctly?",
    # J1 resolved (filling)
    97436: "torch.compile stops working when I enable gradient checkpointing. Are they compatible?",
    # J2 unresolved
    125718: "torch.compile produces extremely slow code for complex-valued tensors. Is complex number support optimized in inductor?",
    159769: "The inductor-generated backward kernel for float8 scaled_grouped_mm is much slower than eager. How do I get inductor to generate efficient float8 code?",
    151705: "Can inductor generate native tl.dot matmuls instead of going through aten? I think the extra indirection is hurting performance.",
    149857: "torch.compile's decomposition of SDPA is actually faster than the EFFICIENT_ATTENTION backend on tf32. Shouldn't the fused kernel be faster?",
    130015: "Inductor generates suboptimal kernels when a pointwise op feeds into a reduction. The fused kernel is slower than separate kernels. How do I fix this?",
    174496: "torch._foreach_copy_ on CUDA tensors is much slower than a simple for-loop of tensor.copy_(). Why isn't the foreach variant faster?",
    126644: "Is there a way to get torch.compile to report which ops are causing slowdowns? I need some kind of performance canary or diagnostic mode.",
    93531: "Where can I find benchmarks for TorchInductor CPU performance? I want to compare my results against known baselines.",
    114723: "How do I use torch.compile with an Intel GPU? Is XPU backend supported upstream?",
    # J2 resolved (filling)
    93757: "I'm seeing that some ops aren't supported by inductor. Where can I find a list of which ops are covered?",
    114495: "After updating PyTorch, my GNN model (EdgeConv) regressed in performance on CPU with inductor. How do I diagnose this?",
    # J3 unresolved
    94855: "torch.compile breaks reproducibility even with manual seeds set. The same code gives different results across runs when compiled.",
    95708: "torch.compile fails on macOS with 'omp.h file not found'. How do I fix OpenMP issues on Mac?",
    143130: "Inductor's epilogue fusion produces wrong results when mutations are involved. How do I debug silent correctness issues in fused kernels?",
    93743: "My model uses data-dependent control flow (e.g., early stopping based on values). torch.compile traces through it incorrectly. What are my options?",
    169253: "torch.compile silently drops mutations to class-level list attributes. My model's output is wrong because in-place list modifications are ignored.",
    103650: "AOT autograd incorrectly depends on tensor strides when regenerating gradients, causing wrong results with non-contiguous tensors.",
    177499: "test_conv_stride_constraints fails on ROCm with an AssertionError. Is this a known correctness issue with conv on AMD GPUs?",
    169082: "I'm getting NaN values when using reduce-overhead or max-autotune modes, but the model works fine in default mode. What causes this?",
    108798: "A meta kernel isn't raising an expected error, so torch.compile silently produces wrong results instead of failing early.",
    # J3 resolved (filling)
    93767: "How do I benchmark whether torch.compile actually improves accuracy and performance across different models?",
    138652: "Segformer accuracy regressed when using AOT eager mode in PyTorch 2.5. How do I check if this is a known regression?",
    # J4 unresolved
    104053: "torch.compile treats my optimizer as a training graph instead of inference, causing unnecessary graph breaks. How do I fix this?",
    109774: "I'm using DDP with Dynamo but AllReduce ops cause graph breaks. Is there a way to compile through DDP communication?",
    138226: "Dynamo doesn't generate guards for frozen dataclasses, so config changes don't trigger recompilation. Is this expected?",
    126566: "torch.compiler.allow_in_graph doesn't create a call_module node in the FX graph. How do I properly inline a module?",
    117394: "Is there a way to get Dynamo to capture a single-step graph instead of tracing through the entire forward pass?",
    141790: "AOTAutograd cache never hits even on a trivially simple program. Why does it always miss?",
    174457: "The PT2E quantization flow is completely broken on ARM/Graviton3 CPU with PyTorch 2.9.1. Is this a known issue?",
    91469: "torch.compile with aotautograd doesn't support double backwards (grad of grad). Is there a workaround?",
    164891: "I need better guardrails for combining distributed optimizations with non-fullgraph compile. The current behavior is confusing.",
    160886: "Dynamo doesn't support Parameter subclasses. My custom Parameter type causes a graph break.",
    # J5 unresolved
    163811: "I wrote a custom softmax Triton kernel and registered it with torch.library, but torch.compile throws an error when trying to use it.",
    150296: "How do I integrate a custom backend (like zentorch) into TorchInductor's compilation pipeline?",
    143412: "test_select_algorithm fails for convolution in inductor. Is there a bug in the algorithm selection for conv ops?",
    122840: "The inductor-generated log_softmax kernel gets much worse performance when padding is involved. How do I avoid this?",
    120184: "Inductor's welford reduction implementation makes LayerNorm slower than eager in several cases. Is there a way to override the codegen?",
    121968: "Should torch.compile use CUDA graphs by default? I enabled them manually and got a big speedup.",
    # J5 resolved (filling)
    124480: "Is there a fused linear + cross-entropy loss function? Computing them separately seems wasteful.",
    130174: "How do I make torch.compile work with vLLM? I keep getting errors when trying to compile OPT-125M.",
    90768: "torch.compile/inductor doesn't work on Windows at all. I get linker errors. Is Windows supported?",
    97361: "torch.compile'd optimizer.step() fails with 'too many arguments in call' error. How do I compile optimizers?",
    # J6 unresolved
    152954: "DTensor placement propagation is missing for as_strided, causing failures when I compile models using DTensor sharding.",
    159346: "AOTInductor has a severe performance regression with FP16 autocast on small batch sizes. Is dynamic shapes causing extra overhead?",
    121036: "I can't compile TorchVision's RPN with AOTInductor - it fails with an AssertionError related to dynamic output shapes.",
    113180: "My training loss is higher and eval metrics are worse when using torch.compile. Could shape-related recompilation be silently changing behavior?",
    127153: "pad_sequence() isn't exportable in ONNX because of dynamic-length sequences. How do I handle variable-length padding?",
    122129: "I get an obscure 'Expected a value of type List[int]' error that seems related to dynamic shapes. How do I debug this?",
    116766: "torch.compile with DeepSpeed throws InternalTorchDynamoError about NestedUserFunction. Is DeepSpeed + Dynamo supported?",
    147475: "Exporting with dynamic_shapes and then compiling with AOTInductor produces degraded output quality. Are dynamic shapes handled differently in AOTI?",
    111950: "Operators returning dynamic-shape outputs that require grad cause issues. How does torch.compile handle ops with data-dependent output shapes?",
    163759: "torch.combinations throws RuntimeError with dynamic shapes enabled. Is this op supported in dynamic mode?",
    # J7 unresolved
    101107: "Is there a way to serialize a torch.compile'd model so I can load it without recompiling?",
    113287: "I need ahead-of-time compilation and serialization for torch.compile'd models for deployment. What's the recommended approach?",
    125977: "AOT Autograd tracing takes an extremely long time for my model. Where is the compilation time being spent?",
    111317: "torch.compile with FSDP mixed precision on LLaMA causes errors. Is this combination supported?",
    109074: "torch.compile/Triton holds the GIL during compilation, blocking all other threads. Can compilation run in the background?",
    # J7 resolved (filling)
    138211: "tmp_path.rename in the inductor code cache fails on Windows. How does caching work on Windows?",
    136254: "I'm seeing a performance regression in torch.compile after updating PyTorch. How do I bisect which commit caused it?",
    115344: "Inductor autotuning crashes with an illegal memory access when some input tensors are None. How do I work around this?",
    147323: "My model takes extremely long to compile because it's very deep. Can compilation be broken into smaller pieces?",
    140091: "Compiled autograd fails when running nn.LayerNorm with torch.compile. Is compiled autograd production-ready?",
    119607: "I have a CUDA memory leak when using torch.compile in a training loop. Memory keeps growing even with del and gc.collect().",
    # J8 unresolved
    123177: "torch.compile + CUDA graphs fails with an assertion error in multithreaded inference. Is this combination supported for concurrent requests?",
    50688: "Is there a torch.scan equivalent to JAX's lax.scan? I need a functional scan for my RNN that works with torch.compile.",
    95408: "Does PyTorch support parallel associative scans? I need an efficient prefix-sum that torch.compile can optimize.",
    162859: "How do I use symmetric memory (for NVLink-based collectives) with torch.compile? It currently breaks compilation.",
    166093: "AOTInductor cross-compilation for Windows fails with undefined reference errors. How do I cross-compile for a different platform?",
    106614: "My custom min_sum/mul_sum reduction ops are much slower with the C++ inductor backend on CPU than with eager mode.",
    178554: "Flex Attention crashes with an LLVM error after the recent Triton pin update. Is this a known Triton compatibility issue?",
    158212: "Compiled flex_attention gives wrong gradients. The forward pass is correct but backward produces different values than eager.",
    # J8 resolved (filling)
    98161: "Compiling a function with complex-valued tensors fails. Does torch.compile support complex number operations?",
    145984: "Triton autotuning fails with 'invalid argument' CUDA error. How do I debug autotuning failures?",
}


def _synthesize_question(issue: dict, clean_title: str, body: str, journey_key: str) -> str:
    """Synthesize a natural question when we don't have a hand-crafted one."""
    title_lower = clean_title.lower()

    # Try to extract the core problem
    # Look for "Describe the bug" section
    bug_match = re.search(r"describe the bug\s*\n+(.+?)(?:\n\n|\n###|\n##)", body, re.IGNORECASE | re.DOTALL)
    core_problem = ""
    if bug_match:
        core_problem = bug_match.group(1).strip()
        # Take first sentence
        first_sent = re.split(r"[.\n]", core_problem)[0].strip()
        if len(first_sent) > 30:
            core_problem = first_sent

    # Build question based on journey
    if journey_key == "J1":
        if core_problem:
            return f"I'm trying to get torch.compile working: {core_problem}. What am I doing wrong?"
        return f"How do I handle this with torch.compile: {clean_title}?"
    elif journey_key == "J2":
        if core_problem:
            return f"My compiled model isn't performing as expected. {core_problem}. How do I diagnose this?"
        return f"torch.compile isn't giving me the speedup I expected. {clean_title} - how do I investigate?"
    elif journey_key == "J3":
        if core_problem:
            return f"torch.compile produces different results than eager: {core_problem}. How do I debug this?"
        return f"I'm seeing correctness issues with torch.compile: {clean_title}. What should I check?"
    elif journey_key == "J4":
        if core_problem:
            return f"I'm getting graph breaks: {core_problem}. How do I resolve this?"
        return f"My model hits graph breaks with torch.compile: {clean_title}. How do I fix this?"
    elif journey_key == "J5":
        if core_problem:
            return f"I want to optimize my compiled model: {core_problem}. What options do I have?"
        return f"How do I get better performance from torch.compile for: {clean_title}?"
    elif journey_key == "J6":
        if core_problem:
            return f"I'm having dynamic shape issues with torch.compile: {core_problem}. What's the right approach?"
        return f"torch.compile has issues with dynamic shapes in my case: {clean_title}. How do I handle this?"
    elif journey_key == "J7":
        if core_problem:
            return f"Compilation is taking too long: {core_problem}. How do I speed it up?"
        return f"torch.compile takes too long: {clean_title}. How do I reduce compilation time?"
    elif journey_key == "J8":
        if core_problem:
            return f"My custom op doesn't work with torch.compile: {core_problem}. What do I need to change?"
        return f"torch.compile fails with my custom operation: {clean_title}. How do I make it compatible?"
    else:
        return f"{clean_title}?"


def extract_issue_context(issue: dict) -> str:
    """Extract first 1500 chars of issue body, preserving error messages."""
    body = issue.get("body") or ""
    # Clean up but preserve code blocks and error messages
    context = body[:1500]
    if len(body) > 1500:
        # Try to break at a natural point
        for break_char in ["\n\n", "\n", ". ", " "]:
            idx = context.rfind(break_char)
            if idx > 1200:
                context = context[:idx]
                break
    return context.strip()


def main():
    print("Loading data...")
    with open(ISSUES_PATH) as f:
        all_issues = json.load(f)
    issue_map = {i["number"]: i for i in all_issues}
    print(f"  Loaded {len(all_issues)} issues ({sum(1 for i in all_issues if i['state']=='open')} open, {sum(1 for i in all_issues if i['state']=='closed')} closed)")

    with open(EXISTING_PATH) as f:
        existing_cases = json.load(f)
    print(f"  Loaded {len(existing_cases)} existing cases")

    # Track used issue numbers to avoid duplicates
    used_issues = set(c["source_issue"] for c in existing_cases)

    # Organize existing cases by journey and status
    journey_cases: dict[str, dict[str, list]] = defaultdict(lambda: {"resolved": [], "unresolved": []})

    for c in existing_cases:
        issue_num = c["source_issue"]
        state = issue_map[issue_num]["state"]
        status = "resolved" if state == "closed" else "unresolved"
        c["resolution_status"] = status
        # Update issue_context if missing or short
        if "issue_context" not in c or len(c.get("issue_context", "")) < 100:
            c["issue_context"] = extract_issue_context(issue_map[issue_num])
        jkey = c["journey"][:2]
        journey_cases[jkey][status].append(c)

    # Print current state
    print("\nCurrent state before balancing:")
    print(f"  {'Journey':<35s} {'Resolved':>10s} {'Unresolved':>10s}")
    print("  " + "-" * 57)
    for jkey in sorted(JOURNEYS.keys()):
        r = len(journey_cases[jkey]["resolved"])
        u = len(journey_cases[jkey]["unresolved"])
        print(f"  {JOURNEYS[jkey]:<35s} {r:>10d} {u:>10d}")

    # Pre-classify all issues for faster lookup
    print("\nClassifying all issues...")
    classified: dict[str, dict[str, list]] = defaultdict(lambda: {"open": [], "closed": []})
    skip_count = 0

    for issue in all_issues:
        if is_ci_or_bot_issue(issue):
            skip_count += 1
            continue
        if issue["number"] in used_issues:
            continue
        journey = classify_issue(issue)
        if journey:
            classified[journey][issue["state"]].append(issue)

    print(f"  Skipped {skip_count} CI/bot issues")
    for jkey in sorted(JOURNEYS.keys()):
        o = len(classified[jkey]["open"])
        c = len(classified[jkey]["closed"])
        print(f"  {JOURNEYS[jkey]}: {c} closed, {o} open candidates")

    # Sort candidates by quality (comments, reactions, recency)
    def issue_quality_score(issue: dict) -> float:
        """Higher is better - prioritize engaged, recent issues with substance."""
        comments = issue.get("comments", 0)
        reactions = issue.get("reactions", 0)
        body_len = len(issue.get("body") or "")
        # Prefer issues with meaningful body text
        body_score = min(body_len / 500, 3.0)
        # Prefer issues with engagement
        engagement = min(comments, 20) * 0.3 + min(reactions, 10) * 0.2
        # Prefer newer issues (higher number = newer)
        recency = issue["number"] / 200000
        return body_score + engagement + recency

    for jkey in classified:
        for state in ["open", "closed"]:
            classified[jkey][state].sort(key=issue_quality_score, reverse=True)

    # Now fill in missing cases
    print("\nFilling missing cases...")

    def create_case(issue: dict, journey_key: str, case_id: str, status: str) -> dict:
        return {
            "id": case_id,
            "journey": JOURNEYS[journey_key],
            "source_issue": issue["number"],
            "source_url": issue["html_url"],
            "resolution_status": status,
            "user_question": write_user_question(issue, journey_key),
            "issue_context": extract_issue_context(issue),
            "difficulty": assess_difficulty(issue),
            "expected_doc_topics": extract_doc_topics(issue, journey_key),
        }

    for jkey in sorted(JOURNEYS.keys()):
        resolved_list = journey_cases[jkey]["resolved"]
        unresolved_list = journey_cases[jkey]["unresolved"]

        # Fill resolved cases (need 10)
        need_resolved = 10 - len(resolved_list)
        if need_resolved > 0:
            candidates = [i for i in classified[jkey]["closed"] if i["number"] not in used_issues]
            added = 0
            for issue in candidates:
                if added >= need_resolved:
                    break
                # Basic quality check
                if len(issue.get("body") or "") < 50:
                    continue
                case_id = f"{jkey}-{len(resolved_list) + 1}"
                case = create_case(issue, jkey, case_id, "resolved")
                resolved_list.append(case)
                used_issues.add(issue["number"])
                added += 1
                print(f"  Added resolved {case_id}: #{issue['number']} - {issue['title'][:60]}")

            if added < need_resolved:
                print(f"  WARNING: Could only add {added}/{need_resolved} resolved cases for {JOURNEYS[jkey]}")

        # Fill unresolved cases (need 10)
        need_unresolved = 10 - len(unresolved_list)
        if need_unresolved > 0:
            candidates = [i for i in classified[jkey]["open"]
                         if i["number"] not in used_issues
                         and i.get("comments", 0) > 0  # Must have some engagement
                         and len(i.get("body") or "") >= 100]  # Must have substance
            added = 0
            for issue in candidates:
                if added >= need_unresolved:
                    break
                case_id = f"{jkey}-{10 + len(unresolved_list) + 1}"
                case = create_case(issue, jkey, case_id, "unresolved")
                unresolved_list.append(case)
                used_issues.add(issue["number"])
                added += 1
                print(f"  Added unresolved {case_id}: #{issue['number']} - {issue['title'][:60]}")

            if added < need_unresolved:
                # Relax constraints and try again
                relaxed_candidates = [i for i in classified[jkey]["open"]
                                     if i["number"] not in used_issues
                                     and len(i.get("body") or "") >= 30]
                for issue in relaxed_candidates:
                    if added >= need_unresolved:
                        break
                    case_id = f"{jkey}-{10 + len(unresolved_list) + 1}"
                    case = create_case(issue, jkey, case_id, "unresolved")
                    unresolved_list.append(case)
                    used_issues.add(issue["number"])
                    added += 1
                    print(f"  Added unresolved (relaxed) {case_id}: #{issue['number']} - {issue['title'][:60]}")

            if added < need_unresolved:
                print(f"  WARNING: Could only add {added}/{need_unresolved} unresolved cases for {JOURNEYS[jkey]}")

    # Now renumber all cases properly: J{n}-1..10 resolved, J{n}-11..20 unresolved
    print("\nRenumbering cases...")
    final_cases = []
    for jkey in sorted(JOURNEYS.keys()):
        resolved_list = journey_cases[jkey]["resolved"]
        unresolved_list = journey_cases[jkey]["unresolved"]

        for i, case in enumerate(resolved_list[:10], 1):
            case["id"] = f"{jkey}-{i}"
            final_cases.append(case)

        for i, case in enumerate(unresolved_list[:10], 11):
            case["id"] = f"{jkey}-{i}"
            final_cases.append(case)

    # Save output
    print(f"\nSaving {len(final_cases)} cases to {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(final_cases, f, indent=2, ensure_ascii=False)

    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    journey_summary = defaultdict(lambda: {"resolved": 0, "unresolved": 0})
    for case in final_cases:
        jkey = case["journey"][:2]
        journey_summary[jkey][case["resolution_status"]] += 1

    print(f"\n{'Journey':<35s} {'Resolved':>10s} {'Unresolved':>10s} {'Total':>8s} {'Status':>8s}")
    print("-" * 75)
    all_good = True
    for jkey in sorted(JOURNEYS.keys()):
        r = journey_summary[jkey]["resolved"]
        u = journey_summary[jkey]["unresolved"]
        t = r + u
        ok = "OK" if r == 10 and u == 10 else "FAIL"
        if ok == "FAIL":
            all_good = False
        print(f"{JOURNEYS[jkey]:<35s} {r:>10d} {u:>10d} {t:>8d} {ok:>8s}")

    total = len(final_cases)
    total_r = sum(v["resolved"] for v in journey_summary.values())
    total_u = sum(v["unresolved"] for v in journey_summary.values())
    print("-" * 75)
    print(f"{'TOTAL':<35s} {total_r:>10d} {total_u:>10d} {total:>8d}")

    # Check for duplicates
    issue_nums = [c["source_issue"] for c in final_cases]
    dups = [n for n in issue_nums if issue_nums.count(n) > 1]
    if dups:
        print(f"\nDUPLICATE ISSUES FOUND: {set(dups)}")
        all_good = False
    else:
        print(f"\nNo duplicate issues found.")

    print(f"\nFinal result: {'ALL CHECKS PASSED' if all_good else 'SOME CHECKS FAILED'}")
    print(f"Output saved to: {OUTPUT_PATH}")

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
