# CompileQA-Bench

Benchmark for evaluating any system's torch.compile question-answering capability. SWE-bench analog — same case suite + rubric, plug in any answerer (docs, QA bot, skill-augmented LLM, agent). Doc evaluation is configuration #1 (Track 2).

> Renamed 2026-04-22 from "PT2 Documentation Audit" / "Project Sentinel" / "torch-compile-doc-eval" because the methodology generalizes beyond docs.

## Owner

Owl (Evaluation Methodologist). Rubric design, IAA validation, scoring analysis. Raven scores as second annotator. Rocky built the original framework (handed off 2026-04-14).

## Status

All scoring and IAA validation is **COMPLETE**. Final dataset: `analysis/final_dataset_320.json` (320 cases x 3 dimensions). See `analysis/v3_scoring_status.md` for full status.

| Dimension | Track 1 κ | Track 2 κ | Status |
|-----------|-----------|-----------|--------|
| Act       | 0.900     | 0.945     | PASS   |
| Diag      | 0.918     | 0.925     | PASS   |
| Fab       | 1.000     | n/a       | PASS   |

## Evaluation Modes

- **Mode A** — Coverage & Discoverability: does pytorch.org have relevant docs, and can search find them?
- **Mode B** — Resolution Quality: given a real torch.compile problem, can an agent produce correct guidance?
  - **Track 1**: unrestricted (agent can use any knowledge)
  - **Track 2**: doc-restricted (agent limited to pytorch.org docs)

## Key Files

| Path | What |
|------|------|
| `suite/cases.json` | 160 test cases (immutable). 8 journeys x 20 cases. |
| `protocol/rubric_v3_label_based.md` | Production rubric (v3.0, label-based). |
| `protocol/rubric_v2_multidimensional.md` | Prior rubric (v2.8, direct ordinal). Archived. |
| `protocol/methodology.md` | Full evaluation methodology. |
| `analysis/v3_scoring_status.md` | Comprehensive scoring and IAA status. |
| `analysis/final_dataset_320.json` | Final scored dataset (320 cases). |
| `analysis/documentation_gap_analysis.md` | Gap analysis report. |
| `analysis/cross_reference.md` | Mode A x Mode B cross-reference findings. |
| `decisions.md` | 8 key design decisions with rationale. |
| `runs/label-scoring/` | All v3.0 label-based scores (Owl + Raven, both tracks). |
| `scripts/compute_iaa_labels.py` | IAA computation for label-based scoring. |
| `scripts/calibrate_track2.py` | Track 2 calibration rules. |
| `skills/` | Agent skills: rubric-design, iaa-validation, eval-lessons. |

## Conventions

- **Rubric versions**: v2.x = direct ordinal scoring. v3.x = label-based decomposition. v3.0 is production.
- **Calibration rules**: Rules 1-5 from Track 2 Diag pilot, Rules 6-10 from full T1/T2 IAA. All encoded in the rubric.
- **Score files**: `{scorer}_{dimension}_labels_{track}_{n}.json` (e.g., `owl_act_labels_track1_160.json`). Calibrated versions end in `_calibrated.json`.
- **IAA threshold**: κ ≥ 0.80 (quadratic-weighted Cohen's kappa for ordinal dimensions).
- **Test suite is immutable** after finalization. Never modify `suite/cases.json`.
- **`names_mechanism` interpretation**: diagnostic tools (TORCH_LOGS, profiler) represent the ceiling of what a doc-restricted response can cite; nm=false signals a documentation gap, not scorer error.

## Open Design Risks (from decisions.md)

- **D1**: No human ground truth — κ≥0.80 between two LLMs doesn't guarantee human-aligned rubric.
- **D2**: No held-out validation set — rubric may be overfit to 160 cases.
- **D5**: Track 1 rubric rules untested by IAA until v3.0 (now resolved).
- **D6**: Rocky was both rubric designer and scorer — structural bias risk (Owl now owns rubric design, mitigating this).
