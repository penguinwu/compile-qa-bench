# Retrieval Analysis: 80 torch.compile Questions via Web Search

**Date:** 2026-04-11
**Method:** Unrestricted web search for each of 80 real user questions (10 per journey)
**Goal:** What sources surface when users/agents search for torch.compile help?

---

## Overall Results

For each query, classified the top results by whether **official pytorch.org documentation** surfaces with a relevant answer:

| Category | Count | % | Description |
|----------|-------|---|-------------|
| ✅ Direct hit | 10 | 12.5% | Official pytorch.org page directly addresses the question |
| ⚠️ Tangential | 28 | 35.0% | Some pytorch.org content appears but generic or only partially relevant |
| ❌ No docs | 42 | 52.5% | No helpful pytorch.org documentation in search results |

**Over half of real user questions return zero helpful official documentation.**

---

## Per-Journey Breakdown

| Journey | ✅ Direct | ⚠️ Tangential | ❌ Missing | Direct % | Any Coverage % |
|---------|-----------|---------------|-----------|----------|----------------|
| J1: First Compile | 3 | 4 | 3 | 30% | 70% |
| J2: Performance Diagnosis | 0 | 4 | 6 | **0%** | 40% |
| J3: Correctness & Debugging | 0 | 5 | 5 | **0%** | 50% |
| J4: Graph Breaks | 2 | 4 | 4 | 20% | 60% |
| J5: Performance Optimization | 0 | 2 | 8 | **0%** | **20%** |
| J6: Dynamic Shapes | 2 | 4 | 4 | 20% | 60% |
| J7: Compile-Time Performance | 2 | 3 | 5 | 20% | 50% |
| J8: Custom & Higher-Order Ops | 1 | 2 | 7 | **10%** | **30%** |

### Key Findings:
- **J1 (First Compile)** is the only journey with decent doc coverage (30% direct, 70% any)
- **J2, J3, J5 have ZERO direct doc hits** — users land on blogs, forums, or GitHub issues
- **J5 (Performance Optimization)** is the worst: only 20% have any pytorch.org coverage at all
- **J8 (Custom Ops)** is nearly as bad at 30% — confirming Otter's finding of 43% issue close rate

---

## Where Agents Actually Land (When Official Docs Fail)

| Source | Frequency | Quality | Reliability |
|--------|-----------|---------|-------------|
| **GitHub issues** | Very common (~30 queries) | Specific but messy | Varies — some solved, many open |
| **discuss.pytorch.org** | Common (~20 queries) | Community workarounds | Often incomplete |
| **Medium blogs** | Very common (~25 queries) | SEO-optimized, often generic | Low — may be outdated/wrong |
| **dev-discuss.pytorch.org** | Occasional (~5 queries) | High quality developer context | Niche, hard to find |
| **NVIDIA docs** | Occasional (~5 queries) | Good for GPU-specific | Narrow scope |
| **HuggingFace docs** | Occasional (~5 queries) | Good for HF models | Framework-specific |
| **runebook.dev** | Occasional (~3 queries) | Mirror of official docs | Oddly ranks higher than pytorch.org |

### The "Troubleshooting Catch-All" Pattern
The `torch.compiler_troubleshooting` page appeared in results for ~15 queries across J2-J8. But it's a **single generic page** covering graph breaks, performance, and errors — it's the "bathroom key" that every search leads to but rarely resolves the specific question.

### The "GitHub Issue = Documentation" Pattern
For advanced queries (J5-J8), the most relevant result is often the **exact GitHub issue** our test case came from. This means:
- The issue thread IS the de facto documentation for these problems
- If the issue is closed with a fix, agents can extract the answer
- If the issue is open (31.8% are >1 year old), agents find unresolved problems

---

## Specific Direct Hits (What Works)

The 10 queries that found official docs successfully:

| ID | Question Topic | Doc Page Found |
|----|---------------|----------------|
| J1-1 | Compile cache | Caching tutorial + config tutorial |
| J1-2 | Change backend | torch.compile API reference |
| J1-3 | Recompilation diagnostics | Caching tutorial |
| J4-3 | __self__ mismatch graph break | Troubleshooting page (directly relevant) |
| J4-9 | create_block_mask graph break | flex_attention API docs |
| J6-3 | dynamic shapes + sum | Dynamic shapes doc |
| J6-7 | dynamic=True symbolic errors | Dynamic shapes doc + troubleshooting |
| J7-1 | Cold start compile time | Regional compilation + caching tutorials |
| J7-2 | T5 compile timeout | Regional compilation + caching tutorials |
| J8-10 | torch.cond control flow | torch.cond API doc |

**Pattern:** Docs work when: (1) a dedicated tutorial exists for the exact topic, (2) the question maps cleanly to an API reference page, or (3) the troubleshooting page happens to cover the specific error.

---

## What This Means for the Evaluation Design

### 1. Retrieval Quality Score (cheap, automated)
For each test question, classify search results:
- **Score 3:** Official doc directly addresses question (✅)
- **Score 2:** Official doc appears but tangential (⚠️)
- **Score 1:** No official docs, but relevant GitHub/forum content (community fills gap)
- **Score 0:** No helpful results from any source (❌)

### 2. Source Attribution (what agents actually use)
Track where each answer comes from:
- Official docs → reliable, authoritative
- GitHub issues → specific but fragile (issue might get closed, moved, or outdated)
- Blogs/forums → unreliable, may hallucinate from pre-training instead

### 3. Baseline Metric
**Current baseline: 12.5% of questions get official doc answers.**
This is the number to move. Target: 50%+ after Phase 1 doc improvements.

### 4. The Improvement Lever
For the 42 queries with ❌ no docs:
- ~15 could be addressed by improving the troubleshooting page with specific scenarios
- ~10 need new dedicated pages (DDP+compile, performance tuning guide, custom ops)
- ~10 need better error messages that link to relevant docs
- ~7 are edge cases that may never warrant dedicated docs (specific bugs, regressions)

---

*Analysis based on 80 web searches using real GitHub issues from pytorch/pytorch (oncall:pt2 label).*
