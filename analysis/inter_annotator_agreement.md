# Inter-Annotator Agreement Analysis

**Date:** 2026-04-11
**Annotators:** Rocky (search-only), Raven (search + doc source tree verification)
**Sample:** 20 test cases (2-3 per journey, mix of resolved/unresolved)
**Rubric:** Topic relevance (0-3), simplified rubric

---

## Results

| ID | Rocky | Raven | Diff | Match |
|--------|-------|-------|------|-------|
| J1-2 | 3 | 3 | 0 | Exact |
| J1-13 | 2 | 0 | 2 | ❌ |
| J2-1 | 0 | 2 | 2 | ❌ |
| J2-15 | 2 | 0 | 2 | ❌ |
| J3-1 | 2 | 3 | 1 | ≈ |
| J3-16 | 2 | 3 | 1 | ≈ |
| J4-3 | 3 | 0 | 3 | ❌ |
| J4-12 | 2 | 3 | 1 | ≈ |
| J4-19 | 0 | 1 | 1 | ≈ |
| J5-1 | 2 | 2 | 0 | Exact |
| J5-15 | 3 | 2 | 1 | ≈ |
| J6-7 | 3 | 3 | 0 | Exact |
| J6-16 | 3 | 2 | 1 | ≈ |
| J7-1 | 3 | 2 | 1 | ≈ |
| J7-17 | 3 | 3 | 0 | Exact |
| J8-1 | 0 | 3 | 3 | ❌ |
| J8-12 | 0 | 1 | 1 | ≈ |
| J8-18 | 2 | 0 | 2 | ❌ |

(J2-7 and J5-3 excluded — different questions in Rocky's source vs. balanced suite)

### Agreement Metrics

| Metric | Count | % |
|--------|-------|---|
| Exact match | 4/18 | 22% |
| Within ±1 | 12/18 | 67% |
| Off by 2+ | 6/18 | 33% |

---

## Root Cause Analysis

The 22% exact agreement is unacceptable. But the disagreement is **systematic, not random** — it reveals a fundamental methodological issue.

### The problem: Rocky scored DISCOVERABILITY, Raven scored COVERAGE

| Pattern | Cases | Explanation |
|---------|-------|-------------|
| Rocky=0, Raven=3 | J8-1, J2-1 | Docs exist but Rocky's search missed them. Rocky measured discoverability; Raven verified coverage. |
| Rocky=3, Raven=0 | J4-3 | Rocky's search returned the troubleshooting page, but Raven verified the specific error isn't actually mentioned there. Rocky scored the search hit; Raven scored the content. |
| Rocky=2, Raven=0 | J1-13, J2-15, J8-18 | Rocky counted tangential/blog results as score 2. Raven verified no pytorch.org docs exist for the specific topic. Rocky was too generous with tangential scoring. |

### Systematic biases

**Rocky's search-only method:**
- False negatives (scores 0 when docs exist): J8-1, J2-1 — search tool didn't surface relevant pages
- False positives (scores 2-3 for tangential content): J4-3, J1-13 — scored search results as relevant when the actual page doesn't address the specific topic

**Raven's search + verification method:**
- More accurate: verified against doc source tree, not just search result titles
- Stricter on tangential: only scored 2 when the page genuinely discusses a related aspect
- No false negatives for direct matches: found J8-1 (custom ops), J4-12 (DDP), J3-16 (data-dependent control flow)

---

## Key Finding

**The disagreement proves we need TWO scores per case, not one:**

1. **Coverage score** (does the page exist and discuss this topic?) — requires doc source tree verification (Raven's method)
2. **Discoverability score** (does search surface this page?) — requires running actual searches (Rocky's method)

A single score conflates these. That's why agreement is low — we were measuring different things with the same number.

This aligns with the coverage vs. discoverability experiment: the 2×2 matrix is not just theoretically cleaner, it's **necessary for reproducibility**.

---

## Recommendations

1. **Use Raven's method for coverage annotation** — search + verify against doc source tree. This is the gold standard.
2. **Use search-only for discoverability scoring** — this IS the measurement (did search find it or not?).
3. **Record both scores per case** — Coverage (Full/Partial/None) + Discoverability (3/2/1/0).
4. **Tighten the "tangential" (score 2) criteria** — biggest disagreement zone. Proposal: score 2 requires the page to have a section or paragraph about the topic, not just mention a keyword. Blog posts and API docs that tangentially touch the topic → score 1, not 2.

---

*Agreement analysis run 2026-04-11. 18 comparable cases. Systematic disagreement traced to methodological difference (search-only vs. search+verify).*
