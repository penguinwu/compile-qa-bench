#!/usr/bin/env python3
"""
Compute Inter-Annotator Agreement (IAA) between two scorers.

Supports:
- Mode A: single-score format (coverage + discoverability)
- Mode B v1: single-score format (guidance quality 0-3)
- Mode B v2: multi-dimensional format (diagnosis 0-3, actionability 0-3, fabrication bool)

Computes: weighted Cohen's kappa (quadratic weights by default, matching
the project's reported kappa values; linear weights available via --weights),
simple Cohen's kappa (for binary), agreement percentages, confusion matrix,
and score distributions.

Note: The project's headline kappa values (Diag=0.863, Act=0.885 on v2.8)
use quadratic weights. The iaa-validation.md skill shows a linear formula,
but the ad-hoc computation that produced reported values used quadratic.
Quadratic weighting penalizes large disagreements more than small ones,
which is standard for ordinal scales (Fleiss & Cohen, 1973).

Usage:
    # Single-score (legacy or Mode A)
    python compute_iaa.py --scorer1 rocky.json --scorer2 raven.json

    # Multi-dimensional (v2)
    python compute_iaa.py --scorer1 rocky_v2_8.json --scorer2 raven_v2_8.json --multidim

    # Specific dimension only
    python compute_iaa.py --scorer1 rocky.json --scorer2 raven.json --multidim --dimension diagnosis
"""

import argparse
import json
import sys
from collections import Counter


# ---------------------------------------------------------------------------
# Kappa computation
# ---------------------------------------------------------------------------

def weighted_kappa(scores_a, scores_b, num_categories, weights="linear"):
    """
    Compute Cohen's weighted kappa for ordinal scales.

    Args:
        scores_a: list of int scores from scorer A
        scores_b: list of int scores from scorer B
        num_categories: number of score levels (e.g., 4 for 0-3)
        weights: "linear" or "quadratic"

    Returns:
        float: weighted kappa coefficient
    """
    n = len(scores_a)
    assert n == len(scores_b), "Score lists must have equal length"
    assert n > 0, "Score lists must not be empty"

    # Build confusion matrix
    cm = [[0] * num_categories for _ in range(num_categories)]
    for a, b in zip(scores_a, scores_b):
        cm[a][b] += 1

    # Marginals
    row_m = [sum(cm[i]) for i in range(num_categories)]
    col_m = [sum(cm[i][j] for i in range(num_categories)) for j in range(num_categories)]

    # Weight function
    if weights == "linear":
        w = lambda i, j: abs(i - j) / (num_categories - 1) if num_categories > 1 else 0
    elif weights == "quadratic":
        w = lambda i, j: (i - j) ** 2 / (num_categories - 1) ** 2 if num_categories > 1 else 0
    else:
        raise ValueError(f"Unknown weight type: {weights}")

    # Observed disagreement
    observed = sum(
        w(i, j) * cm[i][j] / n
        for i in range(num_categories)
        for j in range(num_categories)
    )

    # Expected disagreement (by chance)
    chance = sum(
        w(i, j) * row_m[i] * col_m[j] / n ** 2
        for i in range(num_categories)
        for j in range(num_categories)
    )

    if chance == 0:
        return 1.0

    return 1.0 - observed / chance


def simple_kappa(scores_a, scores_b):
    """
    Compute Cohen's (unweighted) kappa for nominal/binary scales.
    """
    n = len(scores_a)
    assert n == len(scores_b)
    assert n > 0

    observed_agreement = sum(1 for a, b in zip(scores_a, scores_b) if a == b) / n

    labels = sorted(set(scores_a) | set(scores_b))
    chance_agreement = sum(
        (scores_a.count(l) / n) * (scores_b.count(l) / n)
        for l in labels
    )

    if chance_agreement == 1.0:
        return 1.0

    return (observed_agreement - chance_agreement) / (1.0 - chance_agreement)


def interpret_kappa(k):
    """Landis & Koch interpretation."""
    if k < 0:
        return "Poor"
    elif k <= 0.20:
        return "Slight"
    elif k <= 0.40:
        return "Fair"
    elif k <= 0.60:
        return "Moderate"
    elif k <= 0.80:
        return "Substantial"
    else:
        return "Near-perfect"


# ---------------------------------------------------------------------------
# Score loading
# ---------------------------------------------------------------------------

def load_scores_single(path):
    """Load single-score format. Returns {case_id: score}."""
    with open(path) as f:
        data = json.load(f)

    scores = {}
    if isinstance(data, dict) and "scores" in data:
        for item in data["scores"]:
            scores[item["id"]] = item["score"]
    elif isinstance(data, dict) and "results" in data:
        for item in data["results"]:
            key = "rocky_score" if "rocky_score" in item else "score"
            if item.get(key) is not None:
                scores[item["id"]] = item[key]
    elif isinstance(data, list):
        for item in data:
            key = "score" if "score" in item else "rocky_score"
            if key in item:
                scores[item["id"]] = item[key]
    else:
        raise ValueError(f"Unknown format in {path}")

    return scores


def load_scores_multidim(path):
    """
    Load multi-dimensional score format.
    Returns {case_id: {"diagnosis": int, "actionability": int, "fabrication": bool}}
    """
    with open(path) as f:
        data = json.load(f)

    scores = {}
    items = data if isinstance(data, list) else data.get("scores", data.get("results", []))

    for item in items:
        cid = item.get("id")
        if cid and "diagnosis" in item:
            scores[cid] = {
                "diagnosis": item["diagnosis"],
                "actionability": item["actionability"],
                "fabrication": item.get("fabrication", False),
            }

    return scores


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_confusion_matrix(scores_a, scores_b, label, num_categories):
    """Print a confusion matrix (scorer A rows x scorer B cols)."""
    cm = [[0] * num_categories for _ in range(num_categories)]
    for a, b in zip(scores_a, scores_b):
        cm[a][b] += 1

    print(f"\nConfusion Matrix — {label} (Scorer1 rows × Scorer2 cols)")
    header = "        " + "".join(f"  S2={j}" for j in range(num_categories))
    print(header)
    for i in range(num_categories):
        row = f"  S1={i}:  " + "".join(f"{cm[i][j]:>5}" for j in range(num_categories))
        print(row)


def print_disagreements(common_ids, scores1, scores2, label, threshold=2):
    """Print cases with large disagreements."""
    large = [(cid, scores1[cid], scores2[cid])
             for cid in common_ids
             if abs(scores1[cid] - scores2[cid]) >= threshold]

    if not large:
        print(f"\nNo disagreements ≥{threshold} on {label}.")
        return

    print(f"\nLarge disagreements (|diff|≥{threshold}) — {label}:")
    print(f"  {'Case':<10} {'S1':>4} {'S2':>4} {'Delta':>6}")
    print(f"  {'-'*26}")
    for cid, s1, s2 in sorted(large, key=lambda x: -abs(x[1] - x[2])):
        print(f"  {cid:<10} {s1:>4} {s2:>4} {s1-s2:>+6}")


def report_dimension(name, scores_a, scores_b, common_ids, num_categories, weights="quadratic"):
    """Full report for one ordinal dimension."""
    a = [scores_a[c] for c in common_ids]
    b = [scores_b[c] for c in common_ids]
    n = len(a)

    exact = sum(1 for x, y in zip(a, b) if x == y)
    within1 = sum(1 for x, y in zip(a, b) if abs(x - y) <= 1)
    mean_a = sum(a) / n
    mean_b = sum(b) / n

    kw = weighted_kappa(a, b, num_categories, weights=weights)

    # Also compute binary kappa (0 vs ≥1) if useful
    a_bin = [0 if x == 0 else 1 for x in a]
    b_bin = [0 if x == 0 else 1 for x in b]
    k_bin = simple_kappa(a_bin, b_bin) if len(set(a_bin) | set(b_bin)) > 1 else 1.0

    dist_a = [a.count(i) for i in range(num_categories)]
    dist_b = [b.count(i) for i in range(num_categories)]

    kw_alt = weighted_kappa(a, b, num_categories,
                            weights="linear" if weights == "quadratic" else "quadratic")

    print(f"\n{'='*50}")
    print(f"  {name} (n={n}, {num_categories}-level ordinal)")
    print(f"{'='*50}")
    print(f"  Weighted κ ({weights}):  {kw:.3f}  ({interpret_kappa(kw)})")
    print(f"  Weighted κ ({'linear' if weights == 'quadratic' else 'quadratic'}):  {kw_alt:.3f}  ({interpret_kappa(kw_alt)})")
    print(f"  Binary κ (0 vs ≥1):   {k_bin:.3f}  ({interpret_kappa(k_bin)})")
    print(f"  Exact agreement:      {exact}/{n} ({exact/n*100:.1f}%)")
    print(f"  Within ±1:            {within1}/{n} ({within1/n*100:.1f}%)")
    print(f"  Scorer 1 mean:        {mean_a:.2f}  dist={dist_a}")
    print(f"  Scorer 2 mean:        {mean_b:.2f}  dist={dist_b}")
    print(f"  Bias (S1 − S2):       {mean_a - mean_b:+.2f}")

    print_confusion_matrix(a, b, name, num_categories)
    print_disagreements(common_ids, scores_a, scores_b, name)


def report_binary(name, scores_a, scores_b, common_ids):
    """Report for a binary dimension (e.g., fabrication)."""
    a = [int(scores_a[c]) for c in common_ids]
    b = [int(scores_b[c]) for c in common_ids]
    n = len(a)

    exact = sum(1 for x, y in zip(a, b) if x == y)
    k = simple_kappa(a, b) if len(set(a) | set(b)) > 1 else 1.0

    print(f"\n{'='*50}")
    print(f"  {name} (n={n}, binary)")
    print(f"{'='*50}")
    print(f"  Cohen's κ:            {k:.3f}  ({interpret_kappa(k)})")
    print(f"  Agreement:            {exact}/{n} ({exact/n*100:.1f}%)")
    print(f"  Scorer 1 flagged:     {sum(a)}")
    print(f"  Scorer 2 flagged:     {sum(b)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compute IAA between two scorers (agreement + weighted kappa)"
    )
    parser.add_argument("--scorer1", required=True, help="First scorer's JSON file")
    parser.add_argument("--scorer2", required=True, help="Second scorer's JSON file")
    parser.add_argument("--multidim", action="store_true",
                        help="Multi-dimensional v2 format (diagnosis, actionability, fabrication)")
    parser.add_argument("--dimension", choices=["diagnosis", "actionability", "fabrication"],
                        help="Report only one dimension (requires --multidim)")
    parser.add_argument("--weights", choices=["linear", "quadratic"], default="quadratic",
                        help="Kappa weight type (default: quadratic, matching reported values)")
    args = parser.parse_args()

    print(f"Scorer 1: {args.scorer1}")
    print(f"Scorer 2: {args.scorer2}")

    if args.multidim:
        s1 = load_scores_multidim(args.scorer1)
        s2 = load_scores_multidim(args.scorer2)
        common = sorted(set(s1.keys()) & set(s2.keys()))
        print(f"Common cases: {len(common)}")

        if not common:
            print("No overlapping case IDs!")
            sys.exit(1)

        dims = [args.dimension] if args.dimension else ["diagnosis", "actionability", "fabrication"]

        for dim in dims:
            if dim in ("diagnosis", "actionability"):
                dim_s1 = {c: s1[c][dim] for c in common}
                dim_s2 = {c: s2[c][dim] for c in common}
                report_dimension(dim.capitalize(), dim_s1, dim_s2, common,
                                 num_categories=4, weights=args.weights)
            elif dim == "fabrication":
                fab_s1 = {c: s1[c]["fabrication"] for c in common}
                fab_s2 = {c: s2[c]["fabrication"] for c in common}
                report_binary("Fabrication", fab_s1, fab_s2, common)
    else:
        # Legacy single-score format
        s1 = load_scores_single(args.scorer1)
        s2 = load_scores_single(args.scorer2)
        common = sorted(set(s1.keys()) & set(s2.keys()))
        print(f"Common cases: {len(common)}")

        if not common:
            print("No overlapping case IDs!")
            sys.exit(1)

        # Detect scale
        all_scores = [s1[c] for c in common] + [s2[c] for c in common]
        num_cat = max(all_scores) + 1

        report_dimension("Score", s1, s2, common, num_categories=num_cat,
                         weights=args.weights)


if __name__ == "__main__":
    main()
