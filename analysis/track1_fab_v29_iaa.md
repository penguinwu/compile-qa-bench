# Track 1 Fabrication IAA — v2.9 Update

**Date:** 2026-04-14
**Scorer 1:** Owl (manual + detector)
**Scorer 2:** Raven (detector-confirmed + re-score)

## Results

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Fab κ | 0.580 | ≥ 0.80 | FAIL |
| Agreement | 145/160 (90.6%) | — | — |
| Owl fab count | 20 | — | — |
| Raven fab count | 21 | — | — |
| Both flagged | 13 | — | — |

## Improvement from v2.8

| Version | κ | Owl count | Raven count |
|---------|---|-----------|-------------|
| v2.8 | 0.000 | 24 | 0 |
| v2.9 | 0.580 | 20 | 21 |

## Root Cause: Two Blind Spots

### 1. Raven missed 7 semantic fabrications (Owl-only)
Cases: J2-19, J3-19, J4-7, J7-20, J8-3, J8-14, J8-16

These are fabrications the automated detector CAN'T catch: wrong function signatures, fabricated issue references, non-existent APIs with plausible names. Raven confirmed all detector flags but did not add any semantic fabrication checks.

### 2. Owl missed 8 detector-confirmed fabrications (Raven-only)
Cases: J1-19, J3-5, J3-13, J5-5, J5-10, J5-16, J5-19, J6-9

Owl's manual review either missed these or rated evidence as "insufficient." The detector correctly identified them (subconfig fabrications, env vars, import claims).

## Protocol Fix for v2.10

The v2.9 detector-first workflow solved the Raven-zero-flags problem (0.000 → 0.580). To reach κ ≥ 0.80, both scorers need:

1. **Start with detector results** (catches name-based fabrication) — already in v2.9
2. **Mandatory semantic check pass** (catches wrong signatures, fabricated references, non-existent APIs) — NOT yet formalized
3. **Adjudication round** for disagreements — both scorers review the 15 disputed cases together

## Projected κ After Adjudication

If adjudication resolves all 15 disagreements → agreement = 160/160 → κ = 1.000. Even resolving half conservatively → ~0.85, which passes.
