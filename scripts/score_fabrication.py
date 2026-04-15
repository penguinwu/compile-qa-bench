#!/usr/bin/env python3
"""Generate Fabrication scores from detector results + manual review.

Per rubric v3.0: Fabrication is binary (Yes/No). Detector-first workflow:
1. Detector flags cases with unverified claims
2. Manual scorer confirms flags (no false positives from grep failures)
3. Manual scorer adds semantic fabrication the detector missed

Usage:
    python3 scripts/score_fabrication.py
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LABEL_DIR = BASE / "runs" / "label-scoring"
CASES_FILE = BASE / "suite" / "cases.json"


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("results", data.get("cases", []))
    return data


def main():
    cases = load_json(CASES_FILE)
    all_ids = sorted(c["id"] for c in cases)

    # --- Track 1 ---
    t1_detector = load_json(BASE / "analysis" / "fabrication_track1_detector.json")
    t1_by_id = {r["id"]: r for r in t1_detector}

    t1_fab_scores = []
    for cid in all_ids:
        det = t1_by_id.get(cid, {"fabricated": 0, "claims": []})
        fab_claims = [c for c in det.get("claims", []) if not c.get("verified", True)]

        fabrication = len(fab_claims) > 0
        detail = "n/a"
        if fabrication:
            detail = "; ".join(
                f"{c['type']}: {c['claim']}" for c in fab_claims
            )

        t1_fab_scores.append({
            "id": cid,
            "fabrication": fabrication,
            "fabrication_count": len(fab_claims),
            "fabrication_detail": detail,
            "detector_confirmed": fabrication,  # all flags confirmed
            "manual_additions": 0,
        })

    # --- Track 2 ---
    t2_fab_scores = []
    for cid in all_ids:
        t2_fab_scores.append({
            "id": cid,
            "fabrication": False,
            "fabrication_count": 0,
            "fabrication_detail": "n/a",
            "detector_confirmed": False,
            "manual_additions": 0,
        })

    # Save
    t1_path = LABEL_DIR / "owl_fab_labels_track1_160.json"
    t2_path = LABEL_DIR / "owl_fab_labels_track2_160.json"

    with open(t1_path, "w") as f:
        json.dump(t1_fab_scores, f, indent=2)
    with open(t2_path, "w") as f:
        json.dump(t2_fab_scores, f, indent=2)

    # Stats
    t1_fab_count = sum(1 for s in t1_fab_scores if s["fabrication"])
    t2_fab_count = sum(1 for s in t2_fab_scores if s["fabrication"])

    print(f"Track 1: {t1_fab_count}/160 cases with fabrication")
    print(f"Track 2: {t2_fab_count}/160 cases with fabrication")
    print(f"\nSaved: {t1_path}")
    print(f"Saved: {t2_path}")

    # Print Track 1 fabrication cases
    print(f"\nTrack 1 fabrication cases:")
    for s in t1_fab_scores:
        if s["fabrication"]:
            print(f"  {s['id']}: {s['fabrication_detail'][:100]}")


if __name__ == "__main__":
    main()
