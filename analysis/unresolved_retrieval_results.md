# Retrieval Baseline: Unresolved Cases (80)

**Date:** 2026-04-11
**Search tool:** Three Pai external web search (Meta internal)
**Scoring:** Topic relevance only (3=Direct, 2=Tangential, 1=Community, 0=Missing)

---

## Overall Distribution

| Score | Count | % |
|-------|-------|---|
| Direct (3) | 7 | 8.8% |
| Tangential (2) | 22 | 27.5% |
| Community (1) | 36 | 45.0% |
| Missing (0) | 15 | 18.8% |

## Per-Journey Breakdown

| Journey | Direct | Tangential | Community | Missing | Avg Score |
|---------|--------|-----------|-----------|---------|-----------|
| J1: First Compile | 1 | 4 | 3 | 2 | 1.4 |
| J2: Performance Diagnosis | 1 | 2 | 2 | 5 | 0.9 |
| J3: Correctness & Debugging | 0 | 3 | 6 | 1 | 1.2 |
| J4: Graph Breaks | 0 | 5 | 3 | 2 | 1.3 |
| J5: Performance Optimization | 1 | 1 | 8 | 0 | 1.3 |
| J6: Dynamic Shapes | 1 | 3 | 4 | 2 | 1.3 |
| J7: Compile-Time Performance | 3 | 3 | 4 | 0 | 1.9 |
| J8: Custom & Higher-Order Ops | 0 | 1 | 6 | 3 | 0.8 |

## Comparison: Resolved vs. Unresolved

| Metric | Resolved (80) | Unresolved (80) | Combined (160) |
|--------|---------------|-----------------|----------------|
| Direct (3) | 12.5% | 8.8% | 10.6% |
| Tangential (2) | 35.0% | 27.5% | 31.3% |
| Community (1) | ~44% | 45.0% | ~44% |
| Missing (0) | ~9% | 18.8% | ~14% |

### Key Observations

1. **Unresolved cases have WORSE discoverability** — 8.8% direct vs. 12.5% for resolved. This makes sense: unresolved issues tend to be harder, more edge-case, and less likely to have docs written about them.

2. **Missing rate doubles** — 18.8% vs. ~9%. Unresolved issues ask about things that simply aren't documented anywhere (e.g., inductor-level CPU benchmarks, custom op fusion edge cases).

3. **J7 remains the best-served journey** even for unresolved cases (3 direct hits, avg 1.9). Caching and compile-time docs are the most mature.

4. **J8 is the worst** (avg 0.8, zero direct hits, 3 missing). Custom/higher-order ops have the weakest doc coverage of any journey.

5. **J2 has the highest missing rate** (5/10 = 50% missing). Performance diagnosis for edge cases has virtually no doc coverage.

6. **Community sources dominate** — 45% of unresolved queries only find answers in GitHub issues. This confirms that GitHub issues are the de facto documentation for advanced/unsolved problems.

---

*80 unresolved cases from balanced_test_suite.json (J{n}-11 through J{n}-20). Scored 2026-04-11.*
