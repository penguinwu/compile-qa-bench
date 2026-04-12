# Test Suite Sampling Methodology

## Source Corpus
- **9,277 GitHub issues** with the `oncall:pt2` label from pytorch/pytorch
- Corpus snapshot: `/home/pengwu/projects/pt2-knowledge-mining/pt2-issues/pt2_all_issues.json`

## Exclusions
- **oncall:export issues removed**: 786 issues with `oncall:export` label excluded. AOTInductor/export is a separate stack (torch.export → AOTInductor) from torch.compile (JIT compilation). Different entry points, different deployment paths.
- 13 cases in the original suite had export/AOTInductor content and were replaced with non-export oncall:pt2 issues.

## Sampling Strategy
- **8 user journeys** (J1-J8), defined in the project design doc
- **20 cases per journey**: 10 resolved + 10 unresolved
- **Total: 160 cases**
- Issues sampled to cover diverse difficulty levels (beginner, intermediate, advanced) and problem types within each journey

## Balance Verification
Each journey has exactly 10 resolved and 10 unresolved cases. All 8 journeys weighted equally — issue volume in the corpus is biased toward certain journeys, but the test suite normalizes this.

## Replacement Cases (2026-04-11)
13 export/AOTInductor cases removed and replaced:
- Removed IDs: J1-12, J1-14, J1-15, J1-19, J1-20, J5-13, J6-12, J6-13, J6-15, J6-18, J7-17, J8-4, J8-17
- Replacements sourced from non-export oncall:pt2 issues, maintaining resolved/unresolved balance per journey

*Version 1.1 — 2026-04-11. Updated to exclude export/AOTInductor cases.*
