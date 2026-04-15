#!/usr/bin/env python3
"""Compute inter-annotator agreement (IAA) for v3.0 label-based scoring.

Compares Owl and Raven label scores, computing:
- Per-label agreement rate and Cohen's kappa (binary labels)
- Derived score quadratic weighted kappa (ordinal 0-3)
- Disagreement breakdown for calibration

Usage:
    python3 scripts/compute_iaa_labels.py OWL_FILE RAVEN_FILE --dimension act|diag

Examples:
    python3 scripts/compute_iaa_labels.py \
        runs/label-scoring/owl_act_labels_track1_160.json \
        runs/label-scoring/raven_act_labels_track1_160.json \
        --dimension act

    python3 scripts/compute_iaa_labels.py \
        runs/label-scoring/owl_diag_labels_track1_160.json \
        runs/label-scoring/raven_diag_labels_track1_160.json \
        --dimension diag
"""

import argparse
import json
import sys
from collections import Counter


def cohens_kappa_binary(labels1, labels2):
    """Cohen's kappa for binary labels."""
    n = len(labels1)
    assert n == len(labels2), f"Length mismatch: {n} vs {len(labels2)}"

    agree = sum(1 for a, b in zip(labels1, labels2) if a == b)
    p_o = agree / n

    # Expected agreement by chance
    p1_true = sum(labels1) / n
    p2_true = sum(labels2) / n
    p_e = p1_true * p2_true + (1 - p1_true) * (1 - p2_true)

    if p_e == 1.0:
        return 1.0  # Perfect agreement when both always agree
    return (p_o - p_e) / (1 - p_e)


def quadratic_weighted_kappa(scores1, scores2, min_val=0, max_val=3):
    """Cohen's quadratic weighted kappa for ordinal scores."""
    n = len(scores1)
    assert n == len(scores2)

    num_categories = max_val - min_val + 1

    # Build observed confusion matrix
    observed = [[0] * num_categories for _ in range(num_categories)]
    for s1, s2 in zip(scores1, scores2):
        observed[s1 - min_val][s2 - min_val] += 1

    # Build expected confusion matrix
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(num_categories)) for j in range(num_categories)]
    expected = [[row_totals[i] * col_totals[j] / n for j in range(num_categories)] for i in range(num_categories)]

    # Build weight matrix (quadratic)
    weights = [[0.0] * num_categories for _ in range(num_categories)]
    for i in range(num_categories):
        for j in range(num_categories):
            weights[i][j] = (i - j) ** 2 / (num_categories - 1) ** 2

    # Compute kappa
    num = sum(weights[i][j] * observed[i][j] for i in range(num_categories) for j in range(num_categories))
    den = sum(weights[i][j] * expected[i][j] for i in range(num_categories) for j in range(num_categories))

    if den == 0:
        return 1.0
    return 1 - num / den


ACT_LABELS = ['standalone_fix', 'has_imperative', 'case_specific', 'is_template']
DIAG_LABELS = ['correct_subsystem', 'names_mechanism', 'causal_chain', 'consistent_with_resolution', 'case_specific_diagnosis']


def load_scores(filepath):
    """Load label scores from JSON file. Returns list of dicts, sorted by id."""
    with open(filepath) as f:
        data = json.load(f)

    # Handle both list and dict-with-scores-key formats
    if isinstance(data, dict):
        scores = data.get('scores', data.get('results', []))
    else:
        scores = data

    return sorted(scores, key=lambda x: x['id'])


def compute_iaa(owl_file, raven_file, dimension):
    """Compute IAA between Owl and Raven for a given dimension."""
    owl = load_scores(owl_file)
    raven = load_scores(raven_file)

    # Verify same case IDs
    owl_ids = [s['id'] for s in owl]
    raven_ids = [s['id'] for s in raven]
    if owl_ids != raven_ids:
        missing_from_raven = set(owl_ids) - set(raven_ids)
        missing_from_owl = set(raven_ids) - set(owl_ids)
        print(f"ERROR: Case ID mismatch!")
        if missing_from_raven:
            print(f"  In Owl but not Raven: {sorted(missing_from_raven)}")
        if missing_from_owl:
            print(f"  In Raven but not Owl: {sorted(missing_from_owl)}")
        sys.exit(1)

    n = len(owl)
    labels = ACT_LABELS if dimension == 'act' else DIAG_LABELS
    derived_key = 'derived_act' if dimension == 'act' else 'derived_diag'

    print(f"={'=' * 60}")
    print(f"IAA Report: {dimension.upper()} dimension ({n} cases)")
    print(f"={'=' * 60}")
    print(f"Owl:   {owl_file}")
    print(f"Raven: {raven_file}")
    print()

    # Per-label agreement
    print("## Per-Label Agreement")
    print(f"{'Label':<30} {'Agree':>5} {'κ':>8} {'Owl T':>6} {'Rav T':>6} {'Both T':>6}")
    print("-" * 70)

    disagreement_cases = {}
    for label in labels:
        owl_vals = [s[label] for s in owl]
        raven_vals = [s[label] for s in raven]

        agree = sum(1 for a, b in zip(owl_vals, raven_vals) if a == b)
        kappa = cohens_kappa_binary(
            [int(v) for v in owl_vals],
            [int(v) for v in raven_vals]
        )
        owl_true = sum(owl_vals)
        raven_true = sum(raven_vals)
        both_true = sum(1 for a, b in zip(owl_vals, raven_vals) if a and b)

        # Track disagreements
        disagree_ids = [owl[i]['id'] for i in range(n) if owl_vals[i] != raven_vals[i]]
        if disagree_ids:
            disagreement_cases[label] = {
                'owl_true_raven_false': [owl[i]['id'] for i in range(n) if owl_vals[i] and not raven_vals[i]],
                'owl_false_raven_true': [owl[i]['id'] for i in range(n) if not owl_vals[i] and raven_vals[i]],
            }

        status = "PASS" if kappa >= 0.80 else "WARN" if kappa >= 0.60 else "FAIL"
        print(f"{label:<30} {agree:>3}/{n:<2} {kappa:>7.3f}  {owl_true:>5}  {raven_true:>5}  {both_true:>5}  {status}")

    # Derived score agreement
    print()
    print("## Derived Score Agreement")

    # Get derived scores — try the key, or compute from labels
    owl_derived = []
    raven_derived = []
    for s in owl:
        if derived_key in s:
            owl_derived.append(s[derived_key])
        elif dimension == 'act':
            owl_derived.append(compute_act_score(s))
        else:
            owl_derived.append(compute_diag_score(s))

    for s in raven:
        if derived_key in s:
            raven_derived.append(s[derived_key])
        elif dimension == 'act':
            raven_derived.append(compute_act_score(s))
        else:
            raven_derived.append(compute_diag_score(s))

    qwk = quadratic_weighted_kappa(owl_derived, raven_derived,
                                    min_val=0 if dimension == 'act' else 0,
                                    max_val=3)

    exact_agree = sum(1 for a, b in zip(owl_derived, raven_derived) if a == b)
    within1 = sum(1 for a, b in zip(owl_derived, raven_derived) if abs(a - b) <= 1)

    print(f"Quadratic weighted κ: {qwk:.3f} {'PASS' if qwk >= 0.80 else 'WARN' if qwk >= 0.60 else 'FAIL'}")
    print(f"Exact agreement:      {exact_agree}/{n} ({100*exact_agree/n:.1f}%)")
    print(f"Within-1 agreement:   {within1}/{n} ({100*within1/n:.1f}%)")
    print()

    # Score distributions
    print("## Score Distributions")
    owl_dist = Counter(owl_derived)
    raven_dist = Counter(raven_derived)
    print(f"{'Score':<8} {'Owl':>6} {'Raven':>6}")
    for score in range(4):
        print(f"  {score:<6} {owl_dist.get(score, 0):>6} {raven_dist.get(score, 0):>6}")
    print()

    # Disagreement details
    if disagreement_cases:
        print("## Disagreement Details")
        for label, cases in disagreement_cases.items():
            if cases['owl_true_raven_false'] or cases['owl_false_raven_true']:
                print(f"\n### {label}")
                if cases['owl_true_raven_false']:
                    print(f"  Owl=true, Raven=false ({len(cases['owl_true_raven_false'])}): {', '.join(cases['owl_true_raven_false'])}")
                if cases['owl_false_raven_true']:
                    print(f"  Owl=false, Raven=true ({len(cases['owl_false_raven_true'])}): {', '.join(cases['owl_false_raven_true'])}")

    # Cases with derived score disagreement
    derived_disagree = [(owl[i]['id'], owl_derived[i], raven_derived[i])
                        for i in range(n) if owl_derived[i] != raven_derived[i]]
    if derived_disagree:
        print(f"\n### Derived Score Disagreements ({len(derived_disagree)} cases)")
        for case_id, o, r in sorted(derived_disagree, key=lambda x: abs(x[1]-x[2]), reverse=True):
            print(f"  {case_id}: Owl={o}, Raven={r} (diff={abs(o-r)})")

    return qwk


def compute_act_score(labels):
    """Compute derived Act score from labels."""
    if labels.get('standalone_fix', False):
        return 3
    if labels.get('has_imperative', False) and labels.get('case_specific', False):
        return 2
    if labels.get('has_imperative', False):
        return 1
    return 0


def compute_diag_score(labels):
    """Compute derived Diag score from labels."""
    if not labels.get('consistent_with_resolution', True):
        return min(1, sum([
            labels.get('correct_subsystem', False),
            labels.get('names_mechanism', False),
            labels.get('causal_chain', False),
            labels.get('case_specific_diagnosis', False),
        ]))

    count = sum([
        labels.get('correct_subsystem', False),
        labels.get('names_mechanism', False),
        labels.get('causal_chain', False),
        labels.get('case_specific_diagnosis', False),
    ])

    if count >= 3:
        return 3
    elif count == 2:
        return 2
    elif count == 1:
        return 1
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute IAA for v3.0 label-based scoring')
    parser.add_argument('owl_file', help='Path to Owl label scores JSON')
    parser.add_argument('raven_file', help='Path to Raven label scores JSON')
    parser.add_argument('--dimension', required=True, choices=['act', 'diag'],
                        help='Scoring dimension (act or diag)')
    args = parser.parse_args()

    compute_iaa(args.owl_file, args.raven_file, args.dimension)
