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

## In Progress
- **Raven:** Full 160-case Track 1 label scoring (Act + Diag)
- **Owl:** Retroactive names_mechanism recalibration on Track 1 Diag labels (157/160 scored true — some may be diagnostic tools)

## Next Steps
1. Apply names_mechanism calibration rule retroactively to Track 1 Diag labels
2. Compute IAA on Raven's full 160-case scores vs Owl's (calibrated)
3. Calibrate any label disagreements
4. Full Track 2 scoring (160 cases, both scorers, both dimensions)
5. Compile final dataset with all three dimensions
