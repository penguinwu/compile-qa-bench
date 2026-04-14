# Doc Eval Project — Agent Handoff Guide

## Project Summary

This project evaluates how well an AI agent can diagnose and provide actionable guidance for PyTorch `torch.compile` issues, using only official documentation as context (Track 2, doc-restricted mode).

The evaluation framework consists of:
1. **160 test cases** — real GitHub issues covering 8 user journeys (J1-J8), each with 10 resolved + 10 unresolved issues
2. **A multi-dimensional scoring rubric** (v2.6) — scores Diagnosis (0-3), Actionability (0-3), and Fabrication (binary)
3. **An IAA validation methodology** — inter-annotator agreement using weighted kappa, target κ≥0.80

## Current State (2026-04-14)

| Dimension | κ | Status |
|---|---|---|
| Diagnosis | 0.863 | **Validated** (≥0.80) |
| Actionability (4-level) | 0.885 | **Validated** (≥0.80) |
| Act binary (0 vs ≥1) | 0.808 | **Validated** (≥0.80) |
| Fabrication | 96.2% agreement | **Validated** |

**All dimensions validated.** Within-1 agreement: 100% (160/160). Rubric v2.8 is production-ready.

## Directory Structure

```
torch-compile-doc-eval/
├── protocol/
│   └── rubric_v2_multidimensional.md    # The scoring rubric (v2.6)
├── suite/
│   └── cases.json                       # 160 test cases
├── runs/
│   ├── 2026-04-12-baseline/
│   │   └── mode_b_doc_restricted.json   # Agent responses being scored
│   ├── rocky_v2_6_160_scores.json       # Rocky's v2.6 scores
│   └── raven_v2_6_full_160_scores.json  # Raven's v2.6 scores
├── analysis/
│   └── iaa_v2_2_full_160.md             # IAA analysis with kappa progression
├── skills/
│   ├── rubric-design.md                 # How to design scoring rubrics
│   ├── iaa-validation.md                # The IAA validation workflow
│   ├── eval-lessons.md                  # Hard-won lessons (read first!)
│   └── HANDOFF.md                       # This file
└── scripts/
    └── verify_claims.py                 # Automated fabrication detector
```

## GDrive Artifacts

- Rubric v2.8: `1ZO_oQ0dDMdRomyvDxnLoM3HOv95Hf-aW`
- Rubric v2.7: `1pBTcE-MJOKOLhDRtewG1IOjyhx1DPbOO`
- Rubric v2.6: `1hV4IutvkjqEqN1f7i_w_DaPgtnXWgdD3`
- Raven v2.7 scores: `1TWu5ib8HjBPoaHoYYpZ75vr8B4Tmt5BH`
- Raven v2.6 scores: `1N6OfRWIvkGPbMdJwzYfw8vAFoRLb6rm2`
- Raven v2.5 scores: `1_MnCwIca3Zm5JDZjoQ0TxYRxUHQMQHBl`

## Before You Start

1. Read `skills/eval-lessons.md` — these are the mistakes we already made so you don't repeat them
2. Read the rubric (`protocol/rubric_v2_multidimensional.md`) end-to-end
3. Read the IAA analysis (`analysis/iaa_v2_2_full_160.md`) for kappa progression and disagreement patterns

## Working With Raven (Second Scorer)

Raven is on devvm53995, GChat space `spaces/AAQAVvPoEqg`. Communication via GChat `--as-user` messages. She scores quickly (~2-3 minutes for 160 cases).

After any rubric change:
1. Upload updated rubric to GDrive
2. Send Raven the GDrive file ID and a summary of what changed
3. She uploads results as JSON to GDrive, posts the file ID in her space
4. Download via `gdrive download <FILE_ID>` (JSON files produce an "Unexpected JSON response" error but the content is in the error output — pipe through sed to extract)

## The gdrive JSON Bug

`gdrive download` fails on JSON files with "Unexpected JSON response during file download." The full file content appears in the error output. Extract with:

```bash
gdrive download <FILE_ID> /tmp/output.json 2>&1 | \
  sed -n '/^Error: Unexpected JSON response.*got: /,$ p' | \
  sed '1s/^Error: Unexpected JSON response.*got: //' > /tmp/clean.json
```
