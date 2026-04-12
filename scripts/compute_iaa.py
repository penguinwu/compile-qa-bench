#!/usr/bin/env python3
"""
Compute Inter-Annotator Agreement (IAA) between two scorers.

Supports both Mode A (coverage + discoverability) and Mode B (guidance quality).

Usage:
    python compute_iaa.py --scorer1 rocky_scores.json --scorer2 raven_scores.json
    python compute_iaa.py --scorer1 rocky_scores.json --scorer2 raven_scores.json --mode b
"""

import argparse
import json
from collections import Counter


def load_scores(path: str, mode: str) -> dict:
    """Load scores from a JSON file. Handles both Mode A and Mode B formats."""
    with open(path) as f:
        data = json.load(f)

    scores = {}
    if isinstance(data, dict) and "scores" in data:
        # Raven format: {"scores": [{"id": ..., "score": ...}]}
        for item in data["scores"]:
            scores[item["id"]] = item["score"]
    elif isinstance(data, dict) and "results" in data:
        # Rocky Mode B format: {"results": [{"id": ..., "rocky_score": ...}]}
        for item in data["results"]:
            key = "rocky_score" if "rocky_score" in item else "score"
            if item.get(key) is not None:
                scores[item["id"]] = item[key]
    elif isinstance(data, list):
        # Simple list format
        for item in data:
            key = "score" if "score" in item else "rocky_score"
            scores[item["id"]] = item[key]
    else:
        raise ValueError(f"Unknown format in {path}")

    return scores


def compute_agreement(scores1: dict, scores2: dict, label: str = "Score"):
    """Compute and print agreement metrics."""
    common_ids = sorted(set(scores1.keys()) & set(scores2.keys()))
    if not common_ids:
        print("No overlapping case IDs found!")
        return

    n = len(common_ids)
    exact = sum(1 for c in common_ids if scores1[c] == scores2[c])
    within1 = sum(1 for c in common_ids if abs(scores1[c] - scores2[c]) <= 1)
    off2plus = sum(1 for c in common_ids if abs(scores1[c] - scores2[c]) >= 2)

    mean1 = sum(scores1[c] for c in common_ids) / n
    mean2 = sum(scores2[c] for c in common_ids) / n

    print(f"\n=== {label} Agreement (n={n}) ===")
    print(f"{'Metric':<25} {'Value':>10}")
    print("-" * 37)
    print(f"{'Exact agreement':<25} {exact}/{n} ({exact/n*100:.0f}%)")
    print(f"{'Within ±1':<25} {within1}/{n} ({within1/n*100:.0f}%)")
    print(f"{'Off by 2+':<25} {off2plus}/{n} ({off2plus/n*100:.0f}%)")
    print(f"{'Scorer 1 mean':<25} {mean1:.2f}")
    print(f"{'Scorer 2 mean':<25} {mean2:.2f}")
    print(f"{'Bias (S1 - S2)':<25} {mean1 - mean2:+.2f}")

    # Distribution comparison
    dist1 = Counter(scores1[c] for c in common_ids)
    dist2 = Counter(scores2[c] for c in common_ids)
    print(f"\n{'Score':<8} {'Scorer1':>8} {'Scorer2':>8}")
    print("-" * 26)
    all_scores = sorted(set(list(dist1.keys()) + list(dist2.keys())), reverse=True)
    for s in all_scores:
        print(f"{s:<8} {dist1.get(s,0):>8} {dist2.get(s,0):>8}")

    # Per-case comparison
    print(f"\n{'ID':<10} {'S1':>4} {'S2':>4} {'Delta':>6}")
    print("-" * 26)
    for c in common_ids:
        d = scores1[c] - scores2[c]
        marker = " ←" if abs(d) >= 2 else ""
        print(f"{c:<10} {scores1[c]:>4} {scores2[c]:>4} {d:>+6}{marker}")


def main():
    parser = argparse.ArgumentParser(description="Compute IAA between two scorers")
    parser.add_argument("--scorer1", required=True, help="First scorer's JSON file")
    parser.add_argument("--scorer2", required=True, help="Second scorer's JSON file")
    parser.add_argument("--mode", choices=["a", "b"], default="b", help="Evaluation mode")
    args = parser.parse_args()

    scores1 = load_scores(args.scorer1, args.mode)
    scores2 = load_scores(args.scorer2, args.mode)

    print(f"Scorer 1: {args.scorer1} ({len(scores1)} scores)")
    print(f"Scorer 2: {args.scorer2} ({len(scores2)} scores)")

    compute_agreement(scores1, scores2, label=f"Mode {args.mode.upper()}")


if __name__ == "__main__":
    main()
