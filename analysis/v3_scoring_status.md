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

### Track 2 — Diag Pilot (20 cases)
- **Owl labels:** `runs/label-pilot/owl_labels_20_track2_diag.json`
  - Distribution: Diag=0: 1, Diag=1: 1, Diag=2: 9, Diag=3: 9
  - More varied than Track 1 — labels differentiate well on doc-restricted data

### Fabrication Adjudication
- `runs/label-scoring/fab_adjudication_15.json`
- All 15 disagreements confirmed as fabrication → projected κ=1.000
- 7 semantic (Owl caught), 8 detector-confirmed (Raven caught)
- Total fabrications: 28/160 (17.5%)

## In Progress
- **Raven:** Full 160-case Track 1 label scoring (Act + Diag) + 20-case Track 2 Diag pilot

## Next Steps
1. Compute IAA on Raven's full scores vs Owl's
2. Calibrate any label disagreements
3. Full Track 2 scoring (160 cases, both scorers)
4. Compile final dataset with all three dimensions
