# Annotation Guide: torch.compile Documentation Evaluation

**Purpose:** This guide tells you exactly how to score each test case. Follow it precisely to ensure consistency across annotators.

---

## What You're Scoring

Each test case is a real user question about torch.compile, extracted from a GitHub issue. You score it on **two independent dimensions**: Coverage and Discoverability.

---

## Dimension 1: Coverage

**Question:** Does pytorch.org have content that addresses the compile-specific aspect of this question?

**Method:** Browse pytorch.org doc pages and/or the doc source tree (fbsource/fbcode/caffe2/docs/source/). Do NOT rely on web search — check directly.

### Scores

| Score | Label | Criteria |
|-------|-------|----------|
| **Full** | Direct match | pytorch.org has a page with a section that a user reading it would recognize as **directly answering their specific question** — not just covering the same topic area. The page must address the specific failure mode, use case, or mechanism asked about. |
| **Partial** | Related compile content | pytorch.org has compile-related content about the **same concept area**, but doesn't address the specific failure mode, use case, or mechanism asked about. The user would find it *related but insufficient*. |
| **None** | No match | No relevant compile-specific content exists on pytorch.org |

### The Compile Concept Rule

Before scoring, classify the *concept* in the question:

**Compile concepts** — topics that inherently belong to the compile world:
- Graph breaks, Dynamo tracing, fullgraph mode
- Dynamic shapes, symbolic shapes, guards
- AOTInductor, inductor backends, inductor codegen
- Compile cache, recompilation, cold start
- torch.compile modes (max-autotune, reduce-overhead)
- Custom backends, torch.compiler API
- Compiled autograd

→ A page about a compile concept IS a coverage match, even if it doesn't literally say "torch.compile."

**Eager concepts** — general PyTorch features that exist independently of compile:
- Symmetric memory, DTensor, DDP, FSDP
- GRU, LSTM, Conv2d, attention
- Dataclasses, Python control flow
- OpenMP, C++ compilers, platform setup
- TorchScript, ONNX export
- Loss functions, optimizers

→ A page about an eager concept is NOT a match unless it specifically discusses compile behavior. Eager-mode API docs do not answer compile questions.

### Examples

| Question | Concept type | Page found | Score |
|----------|-------------|------------|-------|
| "How to fix graph breaks with bound methods?" | Compile | Troubleshooting page has graph break section | Full |
| "torch.compile + DDP causes AllReduce graph break" | Eager (DDP) | DDP page exists but no compile section | None |
| "torch.compile + DDP causes AllReduce graph break" | Eager (DDP) | DDP page has "TorchDynamo DDPOptimizer" section | Full |
| "Dynamic shapes fails on my GNN" | Compile (dynamic shapes) | Dynamic shapes page exists, mentions varying sizes | Partial (covers dynamic shapes but not GNN-specific) |
| "Symmetric memory breaks under compile" | Eager (symmetric memory) | symmetric_memory.html exists, no compile mention | None |
| "Compile cache doesn't persist across restarts" | Compile (cache) | Caching tutorial covers persistence | Full |

### Full vs. Partial Boundary (Calibration)

The hardest scoring call. Use these worked examples:

| Question | Page found | Why NOT Full | Score |
|----------|-----------|-------------|-------|
| "Deep model takes too long to compile, can it be broken into pieces?" | troubleshooting.html + where_to_apply_compile.html | Pages cover slow compilation and sub-module wrapping, but never prescribe "split deep model into chunks" as a strategy | **Partial** |
| "AOTAutograd cache never hits on trivial program" | caching_tutorial.html | Tutorial covers compile cache (inductor cache), but AOTAutograd cache is a different subsystem — different cache tier | **Partial** |
| "torch.sum fails with dynamo error when dynamic=True" | dynamic_shapes.html | Extensive dynamic shapes docs but no mention of torch.sum + dynamic=True as a failure scenario | **Partial** |
| "Can compile report which ops cause slowdowns?" | profiling_torch_compile.html | Profiling docs exist and TORCH_LOGS=perf_hints is close, but no single "which ops are bottlenecks" diagnostic | **Partial** |
| "Dynamic slicing on data-dependent value not supported" | dynamic_shapes_troubleshooting.html | Page covers unbacked SymInts with exact example of slice on .item(), concrete fix | **Full** |
| "Serialize compiled model to load without recompiling" | aot_inductor.html | Dedicated page: export → compile → package → load, no recompilation | **Full** |

**Rule of thumb:** Full means a user could ctrl+F the page and find a section that answers their question. Partial means they'd find related content and think "this is the right area, but my specific thing isn't here."

---

## Dimension 2: Discoverability

**Question:** When you web-search this question, does search return relevant official docs?

**Method:** Run a web search using the question text as the query. Use Three Pai external web search (or the pinned search tool). Score what comes back.

### Scores

| Score | Label | Criteria |
|-------|-------|----------|
| **3** | Direct | Official pytorch.org page about this topic appears in results |
| **2** | Tangential | Official pytorch.org page tangentially related appears in results |
| **1** | Community | No official docs; only GitHub issues, forums, or blogs match the topic |
| **0** | Missing | No results match the topic at all |

### Scoring Rules

- Score **topic relevance** only — "is the page about the right subject?" NOT "would it fix the user's problem?"
- The same compile-concept vs. eager-concept rule applies: an eager-mode API page appearing in results for a compile question scores 1 (community-level relevance), not 2.
- Blog posts on pytorch.org/blog count as official but are typically tangential (score 2 unless directly about the topic).
- discuss.pytorch.org forum posts are community (score 1), not official.
- GitHub issues are community (score 1).
- If multiple results appear, score based on the BEST result.

### Examples

| Question | Search result | Score |
|----------|--------------|-------|
| "How to change torch.compile backend" | torch.compiler_custom_backends.html appears | 3 (Direct) |
| "torch.compile slower than eager" | torch.compiler_faq.html appears ("Why no speedup?") | 2 (Tangential — related but not exact) |
| "GRU not supported in torch.compile" | Only GitHub issue #12345 appears | 1 (Community) |
| "torch.export + safetensors format" | Only HuggingFace docs appear | 0 (Missing — wrong project) |

---

## Independence

Score Coverage and Discoverability **independently**. A case can be:

| Coverage | Discoverability | Meaning |
|----------|----------------|---------|
| Full | 3 | Docs exist and search finds them — working |
| Full | 0 | Docs exist but search misses them — fix SEO/linking |
| None | 1 | No docs exist; only community content — write docs |
| None | 0 | No docs, no community content — highest priority gap |

---

## Process

For each test case:

1. Read the question and classify the concept (compile vs. eager)
2. **Coverage:** Check pytorch.org directly — does compile-specific content exist? Score Full/Partial/None
3. **Discoverability:** Run web search with the question — what comes back? Score 0-3
4. Record both scores, best URL found, and a brief rationale

---

## Common Pitfalls

- **Don't inflate Partial.** If the page is about the general topic in eager mode and doesn't touch compile → None, not Partial.
- **Don't conflate the two dimensions.** Coverage is about what EXISTS. Discoverability is about what SEARCH FINDS. They're different measurements.
- **Don't score resolution quality.** We're not judging whether the page would fix the user's problem — only whether it's about the right topic.
- **Don't let search results influence coverage scoring.** Check docs directly for coverage, regardless of what search returned.
- **Don't be generous with Full.** If the page covers the concept area but not the specific question, that's Partial. Full requires the page to address the specific failure mode, use case, or mechanism. A caching tutorial ≠ Full for an AOTAutograd cache question.

---

*Version 1.1 — 2026-04-11. Updated Full/Partial boundary with calibration examples from Round 3 IAA (45% exact → target 65%+ with tighter definition).*
