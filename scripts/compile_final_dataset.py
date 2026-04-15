#!/usr/bin/env python3
"""Compile final evaluation dataset: 320 cases × 3 dimensions.

Merges calibrated scores from both tracks (T1 unrestricted, T2 doc-restricted)
across all three dimensions (Actionability, Diagnosis, Fabrication).

Uses calibrated files where available (post-IAA calibration).

Output: Single JSON file with all scores, plus a summary CSV.

Usage:
    python3 scripts/compile_final_dataset.py
"""

import json
import csv
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
LABEL_DIR = BASE / "runs" / "label-scoring"
CASES_FILE = BASE / "suite" / "cases.json"


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("results", data.get("cases", []))
    return data


def by_id(recs):
    return {r["id"]: r for r in recs}


def compute_act_score(rec):
    if rec.get("standalone_fix", False):
        return 3
    if rec.get("has_imperative", False) and rec.get("case_specific", False):
        return 2
    if rec.get("has_imperative", False):
        return 1
    return 0


def compute_diag_score(rec):
    if not rec.get("consistent_with_resolution", True):
        count = sum([
            rec.get("correct_subsystem", False),
            rec.get("names_mechanism", False),
            rec.get("causal_chain", False),
            rec.get("case_specific_diagnosis", False),
        ])
        return min(1, count)
    count = sum([
        rec.get("correct_subsystem", False),
        rec.get("names_mechanism", False),
        rec.get("causal_chain", False),
        rec.get("case_specific_diagnosis", False),
    ])
    if count >= 3:
        return 3
    return count


def load_best(track, dim, scorer):
    """Load calibrated file if available, else uncalibrated."""
    cal_name = f"{scorer}_{dim}_labels_track{track}_160_calibrated.json"
    raw_name = f"{scorer}_{dim}_labels_track{track}_160.json"
    cal_path = LABEL_DIR / cal_name
    raw_path = LABEL_DIR / raw_name
    if cal_path.exists():
        return load_json(cal_path), "calibrated"
    elif raw_path.exists():
        return load_json(raw_path), "raw"
    else:
        return None, "missing"


def main():
    cases = load_json(CASES_FILE)
    cases_by_id = by_id(cases)

    dataset = []
    missing_files = []

    for track in [1, 2]:
        # Load Act scores (prefer calibrated)
        owl_act_data, owl_act_src = load_best(track, "act", "owl")
        rav_act_data, rav_act_src = load_best(track, "act", "raven")

        # Load Diag scores
        owl_diag_data, owl_diag_src = load_best(track, "diag", "owl")
        rav_diag_data, rav_diag_src = load_best(track, "diag", "raven")

        # Load Fab scores
        owl_fab_data, owl_fab_src = load_best(track, "fab", "owl")
        rav_fab_data, rav_fab_src = load_best(track, "fab", "raven")

        print(f"\n=== Track {track} ===")
        print(f"  Owl Act: {owl_act_src}, Raven Act: {rav_act_src}")
        print(f"  Owl Diag: {owl_diag_src}, Raven Diag: {rav_diag_src}")
        print(f"  Owl Fab: {owl_fab_src}, Raven Fab: {rav_fab_src}")

        if not owl_act_data:
            missing_files.append(f"Track {track} Owl Act")
        if not owl_diag_data:
            missing_files.append(f"Track {track} Owl Diag")

        owl_act = by_id(owl_act_data) if owl_act_data else {}
        rav_act = by_id(rav_act_data) if rav_act_data else {}
        owl_diag = by_id(owl_diag_data) if owl_diag_data else {}
        rav_diag = by_id(rav_diag_data) if rav_diag_data else {}
        owl_fab = by_id(owl_fab_data) if owl_fab_data else {}
        rav_fab = by_id(rav_fab_data) if rav_fab_data else {}

        all_ids = sorted(owl_act.keys()) if owl_act else sorted(cases_by_id.keys())

        for cid in all_ids:
            case_info = cases_by_id.get(cid, {})

            # Act scores
            owl_act_rec = owl_act.get(cid, {})
            rav_act_rec = rav_act.get(cid, {})
            owl_act_score = owl_act_rec.get("derived_act", compute_act_score(owl_act_rec))
            rav_act_score = rav_act_rec.get("derived_act", compute_act_score(rav_act_rec)) if rav_act_rec else None

            # Diag scores
            owl_diag_rec = owl_diag.get(cid, {})
            rav_diag_rec = rav_diag.get(cid, {})
            owl_diag_score = owl_diag_rec.get("derived_diag", compute_diag_score(owl_diag_rec))
            rav_diag_score = rav_diag_rec.get("derived_diag", compute_diag_score(rav_diag_rec)) if rav_diag_rec else None

            # Fab scores
            owl_fab_rec = owl_fab.get(cid, {})
            rav_fab_rec = rav_fab.get(cid, {})
            owl_fab_val = owl_fab_rec.get("fabrication", False)
            rav_fab_val = rav_fab_rec.get("fabrication", False) if rav_fab_rec else None

            # Consensus: use Owl's score as primary (adjudicator)
            # For Fab: either scorer flags it = fabrication (conservative)
            fab_consensus = owl_fab_val
            if rav_fab_val is not None:
                fab_consensus = owl_fab_val or rav_fab_val

            entry = {
                "id": cid,
                "track": track,
                "journey": case_info.get("journey", ""),
                "difficulty": case_info.get("difficulty", ""),
                "resolution_status": case_info.get("resolution_status", ""),
                "user_question": case_info.get("user_question", ""),
                # Act
                "act_owl": owl_act_score,
                "act_raven": rav_act_score,
                "act_consensus": owl_act_score,  # Owl is adjudicator
                # Act labels (Owl calibrated)
                "standalone_fix": owl_act_rec.get("standalone_fix", False),
                "has_imperative": owl_act_rec.get("has_imperative", False),
                "case_specific": owl_act_rec.get("case_specific", False),
                "is_template": owl_act_rec.get("is_template", False),
                # Diag
                "diag_owl": owl_diag_score,
                "diag_raven": rav_diag_score,
                "diag_consensus": owl_diag_score,
                # Diag labels (Owl calibrated)
                "correct_subsystem": owl_diag_rec.get("correct_subsystem", False),
                "names_mechanism": owl_diag_rec.get("names_mechanism", False),
                "causal_chain": owl_diag_rec.get("causal_chain", False),
                "consistent_with_resolution": owl_diag_rec.get("consistent_with_resolution", True),
                "case_specific_diagnosis": owl_diag_rec.get("case_specific_diagnosis", False),
                # Fab
                "fabrication": fab_consensus,
                "fabrication_owl": owl_fab_val,
                "fabrication_raven": rav_fab_val,
                "fabrication_detail": owl_fab_rec.get("fabrication_detail", "n/a"),
            }
            dataset.append(entry)

    if missing_files:
        print(f"\n⚠ Missing files: {', '.join(missing_files)}")

    # Save full dataset
    out_json = BASE / "analysis" / "final_dataset_320.json"
    with open(out_json, "w") as f:
        json.dump(dataset, f, indent=2, default=str)
    print(f"\nSaved: {out_json} ({len(dataset)} cases)")

    # Save summary CSV
    out_csv = BASE / "analysis" / "final_dataset_320.csv"
    if dataset:
        fields = ["id", "track", "journey", "difficulty", "resolution_status",
                   "act_consensus", "diag_consensus", "fabrication",
                   "act_owl", "act_raven", "diag_owl", "diag_raven",
                   "standalone_fix", "has_imperative", "case_specific", "is_template",
                   "correct_subsystem", "names_mechanism", "causal_chain",
                   "consistent_with_resolution", "case_specific_diagnosis",
                   "fabrication_owl", "fabrication_raven", "fabrication_detail"]
        with open(out_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(dataset)
        print(f"Saved: {out_csv}")

    # Print summary stats
    print(f"\n{'='*60}")
    print(f"FINAL DATASET SUMMARY")
    print(f"{'='*60}")
    for track in [1, 2]:
        t_data = [d for d in dataset if d["track"] == track]
        act_dist = Counter(d["act_consensus"] for d in t_data)
        diag_dist = Counter(d["diag_consensus"] for d in t_data)
        fab_count = sum(1 for d in t_data if d["fabrication"])
        print(f"\nTrack {track} ({len(t_data)} cases):")
        print(f"  Act: {dict(sorted(act_dist.items()))}")
        print(f"  Diag: {dict(sorted(diag_dist.items()))}")
        print(f"  Fabrication: {fab_count}/{len(t_data)}")


if __name__ == "__main__":
    main()
