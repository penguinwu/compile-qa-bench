# v3.0 Label-Based Scoring — Status

**Date:** 2026-04-14

## Completed

### Rubric
- v3.0 rubric finalized: `protocol/rubric_v3_label_based.md`
- Replaces v2.9 direct ordinal scoring with label-based decomposition
- Validated on 60 pilot cases: Act κ 0.429→1.000, Diag κ 0.182→1.000

### Track 1 — Owl Scoring (160 cases)
- **Act labels:** `runs/label-scoring/owl_act_labels_track1_160.json`
  - Distribution: Act=0: 1, Act=1: 2, Act=2: 78, Act=3: 79
  - standalone_fix=true in 79/160 (49%)
  - has_imperative=true in 159/160; case_specific=true in 158/160
- **Diag labels:** `runs/label-scoring/owl_diag_labels_track1_160.json`
  - Distribution: Diag=1: 1, Diag=2: 11, Diag=3: 148
  - correct_subsystem=true in 159/160; names_mechanism=true in 157/160
  - causal_chain is the key differentiator: true in 112/160 (70%)

### Track 2 — Diag Pilot (20 cases, both scorers)
- **Owl raw labels:** `runs/label-pilot/owl_labels_20_track2_diag.json`
  - Initial distribution: Diag=0: 1, Diag=1: 1, Diag=2: 9, Diag=3: 9
- **Owl calibrated labels:** `runs/label-pilot/owl_labels_20_track2_diag_calibrated.json`
  - Post-calibration distribution: Diag=1: 11, Diag=2: 5, Diag=3: 4
  - 14 names_mechanism labels flipped (diagnostic tools ≠ mechanism)
- **Raven labels:** `runs/label-pilot/raven_labels_20_track2_diag.json`
  - Distribution: Diag=1: 10, Diag=2: 6, Diag=3: 4
- **IAA:** Initial κ=0.241 → calibrated κ=0.741 → post-adjudication κ=0.960
  - Root cause of initial failure: names_mechanism boundary too permissive
  - 3 new calibration rules added to v3.0 rubric (Rules 3–5)

### Fabrication Adjudication
- `runs/label-scoring/fab_adjudication_15.json`
- All 15 disagreements confirmed as fabrication → projected κ=1.000
- 7 semantic (Owl caught), 8 detector-confirmed (Raven caught)
- Total fabrications: 28/160 (17.5%)

### Calibration Rules Added (from Track 2 Diag pilot)
- **Rule 3:** Diagnostic tools (TORCH_LOGS, profiler, etc.) ≠ names_mechanism
- **Rule 4:** Echoed user terms ≠ case_specific_diagnosis — requires original diagnostic reasoning
- **Rule 5:** Gap identification ("docs don't cover X") = correct_subsystem=true

### Track 1 names_mechanism Retroactive Check
- Reviewed all 157 names_mechanism=true Track 1 cases for diagnostic-tool-only rationales
- **Result: No recalibration needed.** All 157 cases cite actual mechanisms (code paths, config options, APIs), not just diagnostic tools
- Track 2's calibration issue was specific to doc-restricted responses, which often lack deeper technical content

### Track 2 — Owl Full Scoring (160 cases)
- **Act labels:** `runs/label-scoring/owl_act_labels_track2_160.json`
  - Distribution: Act=0: 123, Act=1: 24, Act=2: 6, Act=3: 7
  - standalone_fix=true in 7/160 (4%); has_imperative=true in 36/160 (23%)
  - 38/160 are exact template responses (6 template groups)
  - 138/160 have doc_sufficient=False
- **Diag labels:** `runs/label-scoring/owl_diag_labels_track2_160.json`
  - Distribution: Diag=1: 35, Diag=2: 95, Diag=3: 30
  - correct_subsystem=true in 158/160; names_mechanism=true in 123/160
  - causal_chain is rare: true in 5/160 (3%) — most responses don't explain why
  - Template responses score Diag=1 or 2 (never 3, since csd always false)

### Track 1 vs Track 2 Comparison
| Metric | Track 1 | Track 2 |
|--------|---------|---------|
| Act=3 (standalone fix) | 79 (49%) | 7 (4%) |
| Act=0 (no actionable content) | 1 (1%) | 123 (77%) |
| Diag=3 (full diagnosis) | 148 (93%) | 30 (19%) |
| Diag=1 (minimal) | 1 (1%) | 35 (22%) |
| Template responses | 0 | 38 (24%) |
| Doc sufficient | 160 (100%) | 22 (14%) |

### IAA Computation Script
- `scripts/compute_iaa_labels.py` — computes per-label and derived score IAA
- Tested on Track 2 Diag pilot data: correctly reproduces κ=0.960

### Track 1 — Full IAA (Owl vs Raven, 160 cases)
- **Act IAA:** κ = 0.661 → calibrated → **κ = 0.900 PASS**
  - Main calibration: `standalone_fix` (25 cases adjudicated — actionable workarounds count)
  - Remaining: 11 `case_specific` within-1 disagreements (systematic boundary)
  - Raw files: `runs/label-scoring/raven_act_labels_track1_160.json`
  - Calibrated: `runs/label-scoring/owl_act_labels_track1_160_calibrated.json`, `raven_act_labels_track1_160_calibrated.json`
- **Diag IAA:** κ = 0.438 → calibrated → **κ = 0.918 PASS**
  - Main calibration: `causal_chain` (22 cases — methodology ≠ causal chain) + `names_mechanism` (11 cases) + `case_specific_diagnosis` (7 adjudicated)
  - Pre-cal κ was low due to extreme score distribution skew (93% Diag=3), not poor agreement (89.4% exact)
  - Raw files: `runs/label-scoring/raven_diag_labels_track1_160.json`
  - Calibrated: `runs/label-scoring/owl_diag_labels_track1_160_calibrated.json`, `raven_diag_labels_track1_160_calibrated.json`
- Full IAA analysis: `analysis/track1_iaa_v3_results.json`

### Documentation Gap Analysis
- `analysis/documentation_gap_analysis.md` — full markdown report
- `analysis/documentation_gap_data.json` — structured data for downstream use
- `scripts/doc_gap_analysis.py` — analysis script
- GDrive: `1Swb85mm2icSfKQAoaQmPkF4vIR1hJ6Bk` (report), `1C0soZ8Q7mQ2A4awSa6S6CZTG8dXn3xm-` (data)
- Key findings:
  - 138/160 (86%) cases doc-insufficient
  - Mean Act drop: 2.18 points; Mean Diag drop: 0.96 points
  - J3 (Correctness) worst: 0/20 doc sufficient, 18/20 template responses
  - 36 mechanism gaps (names_mechanism T1=true, T2=false)
  - 83 standalone fix gaps; 38 template responses across 2 journeys

### Track 2 IAA (v3.0, post-calibration)
- **Act: κ=0.945 PASS** (95% exact, 99.4% within-1)
- **Diag: κ=0.925 PASS** (93.8% exact, 99.4% within-1)
- Pre-cal: Act κ=0.662, Diag κ=0.323
- Calibration rules 6-10 applied (extending rules 1-5):
  - Rule 6: Soft imperatives ("best approach is to [verb]") count as imperative
  - Rule 7: Topic naming without unique actionable content ≠ case_specific
  - Rule 8: Extends Rule 3 — config options, generic feature names ≠ mechanism
  - Rule 9: Hedged hypotheses ≠ causal chain (consistent with T1 calibration)
  - Rule 10: Topic identification ≠ case_specific_diagnosis
- Calibration script: `scripts/calibrate_track2.py`
- Calibrated files: `runs/label-scoring/*_track2_160_calibrated.json`
- Full IAA analysis: `analysis/track2_iaa_v3_results.json`
- Calibration log: `analysis/track2_calibration_log.json`

## Completed — All IAA PASS

| Dimension | Track 1 κ | Track 2 κ | Status |
|-----------|-----------|-----------|--------|
| Act       | 0.900     | 0.945     | PASS   |
| Diag      | 0.918     | 0.925     | PASS   |

## Next Steps
1. Compile final dataset: 320 cases (160 T1 + 160 T2) × 2 dimensions (Act, Diag)
2. Fabrication dimension (if needed)
