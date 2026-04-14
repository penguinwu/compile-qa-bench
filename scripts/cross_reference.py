#!/usr/bin/env python3
"""
Mode A × Mode B Cross-Reference Analysis

Computes whether discoverability (Mode A) predicts resolution quality (Mode B).
This is the key question: does finding the right docs lead to better agent answers?

Usage:
    python scripts/cross_reference.py \
        --mode-a runs/2026-04-12-baseline/mode_a_scores.json \
        --mode-b-scorer1 runs/rocky_v2_8_160_scores.json \
        --mode-b-scorer2 runs/raven_v2_8_full_160_scores.json \
        [--output analysis/cross_reference.md]
"""

import argparse
import json
import sys
from collections import defaultdict


def load_mode_a(path):
    with open(path) as f:
        data = json.load(f)
    return {s["id"]: s for s in data["scores"]}


def load_mode_b(path):
    with open(path) as f:
        data = json.load(f)
    return {s["id"]: s for s in data}


def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def stdev(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5


def spearman_rank_correlation(x_vals, y_vals):
    """Compute Spearman's rank correlation coefficient."""
    n = len(x_vals)
    if n < 3:
        return float("nan")

    def rank(vals):
        sorted_indices = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and vals[sorted_indices[j]] == vals[sorted_indices[i]]:
                j += 1
            avg_rank = (i + j - 1) / 2.0 + 1
            for k in range(i, j):
                ranks[sorted_indices[k]] = avg_rank
            i = j
        return ranks

    rx = rank(x_vals)
    ry = rank(y_vals)
    d_sq = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - (6 * d_sq) / (n * (n**2 - 1))


def journey(case_id):
    return case_id.split("-")[0]


def main():
    parser = argparse.ArgumentParser(description="Mode A × B cross-reference")
    parser.add_argument("--mode-a", required=True)
    parser.add_argument("--mode-b-scorer1", required=True)
    parser.add_argument("--mode-b-scorer2", required=True)
    parser.add_argument("--output", default=None, help="Output markdown file")
    args = parser.parse_args()

    ma = load_mode_a(args.mode_a)
    mb1 = load_mode_b(args.mode_b_scorer1)
    mb2 = load_mode_b(args.mode_b_scorer2)

    case_ids = sorted(set(ma.keys()) & set(mb1.keys()) & set(mb2.keys()))
    print(f"Cross-referencing {len(case_ids)} cases")

    lines = []
    lines.append("# Mode A × Mode B Cross-Reference Analysis")
    lines.append("")
    lines.append(f"**Cases:** {len(case_ids)}")
    lines.append(f"**Mode A:** Coverage + Discoverability (0-3)")
    lines.append(f"**Mode B:** Diagnosis (0-3) + Actionability (0-3) + Fabrication (binary)")
    lines.append(f"**Scorers:** Average of Scorer 1 and Scorer 2 for Mode B dimensions")
    lines.append("")

    # Build merged records
    records = []
    for cid in case_ids:
        a = ma[cid]
        b1 = mb1[cid]
        b2 = mb2[cid]
        rec = {
            "id": cid,
            "journey": journey(cid),
            "coverage": a["coverage"],
            "discoverability": a["discoverability"],
            "diag_avg": (b1["diagnosis"] + b2["diagnosis"]) / 2,
            "act_avg": (b1["actionability"] + b2["actionability"]) / 2,
            "fab_either": b1.get("fabrication", False) or b2.get("fabrication", False),
            "diag_1": b1["diagnosis"],
            "diag_2": b2["diagnosis"],
            "act_1": b1["actionability"],
            "act_2": b2["actionability"],
        }
        records.append(rec)

    # === 1. Discoverability → Diagnosis/Actionability ===
    lines.append("## 1. Discoverability → Resolution Quality")
    lines.append("")
    lines.append("Does finding the right docs (Mode A discoverability) predict better agent answers (Mode B)?")
    lines.append("")

    disc_labels = {3: "Direct (3)", 2: "Tangential (2)", 1: "Community (1)", 0: "Missing (0)"}
    lines.append("| Discoverability | n | Mean Diag | Mean Act | Fab Rate | Mean Diag (S1) | Mean Diag (S2) |")
    lines.append("|---|---|---|---|---|---|---|")
    for d in [3, 2, 1, 0]:
        group = [r for r in records if r["discoverability"] == d]
        if not group:
            continue
        n = len(group)
        md = mean([r["diag_avg"] for r in group])
        ma_val = mean([r["act_avg"] for r in group])
        fab = sum(1 for r in group if r["fab_either"]) / n * 100
        md1 = mean([r["diag_1"] for r in group])
        md2 = mean([r["diag_2"] for r in group])
        lines.append(f"| {disc_labels[d]} | {n} | {md:.2f} | {ma_val:.2f} | {fab:.1f}% | {md1:.2f} | {md2:.2f} |")

    # Correlation
    disc_vals = [r["discoverability"] for r in records]
    diag_vals = [r["diag_avg"] for r in records]
    act_vals = [r["act_avg"] for r in records]
    rho_diag = spearman_rank_correlation(disc_vals, diag_vals)
    rho_act = spearman_rank_correlation(disc_vals, act_vals)

    lines.append("")
    lines.append(f"**Spearman's ρ:** Discoverability↔Diagnosis = {rho_diag:.3f}, Discoverability↔Actionability = {rho_act:.3f}")
    lines.append("")

    # === 2. Coverage → Resolution Quality ===
    lines.append("## 2. Coverage → Resolution Quality")
    lines.append("")
    lines.append("Does doc existence (Mode A coverage) predict agent quality?")
    lines.append("")

    lines.append("| Coverage | n | Mean Diag | Mean Act | Fab Rate |")
    lines.append("|---|---|---|---|---|")
    for cov in ["Full", "Partial", "None"]:
        group = [r for r in records if r["coverage"] == cov]
        if not group:
            continue
        n = len(group)
        md = mean([r["diag_avg"] for r in group])
        ma_val = mean([r["act_avg"] for r in group])
        fab = sum(1 for r in group if r["fab_either"]) / n * 100
        lines.append(f"| {cov} | {n} | {md:.2f} | {ma_val:.2f} | {fab:.1f}% |")

    lines.append("")

    # === 3. Coverage × Discoverability Matrix ===
    lines.append("## 3. Coverage × Discoverability → Diagnosis (Mean)")
    lines.append("")
    lines.append("The 2D matrix showing how both dimensions interact.")
    lines.append("")

    lines.append("| Coverage \\ Disc. | Direct (3) | Tangential (2) | Community (1) | Missing (0) |")
    lines.append("|---|---|---|---|---|")
    for cov in ["Full", "Partial", "None"]:
        row = f"| {cov} |"
        for d in [3, 2, 1, 0]:
            group = [r for r in records if r["coverage"] == cov and r["discoverability"] == d]
            if group:
                md = mean([r["diag_avg"] for r in group])
                row += f" {md:.2f} (n={len(group)}) |"
            else:
                row += " — |"
        lines.append(row)

    lines.append("")
    lines.append("### Same matrix for Actionability")
    lines.append("")
    lines.append("| Coverage \\ Disc. | Direct (3) | Tangential (2) | Community (1) | Missing (0) |")
    lines.append("|---|---|---|---|---|")
    for cov in ["Full", "Partial", "None"]:
        row = f"| {cov} |"
        for d in [3, 2, 1, 0]:
            group = [r for r in records if r["coverage"] == cov and r["discoverability"] == d]
            if group:
                ma_val = mean([r["act_avg"] for r in group])
                row += f" {ma_val:.2f} (n={len(group)}) |"
            else:
                row += " — |"
        lines.append(row)

    lines.append("")

    # === 4. Per-Journey Breakdown ===
    lines.append("## 4. Per-Journey Analysis")
    lines.append("")
    lines.append("| Journey | n | Mean Disc | Mean Diag | Mean Act | Fab Rate | Coverage: Full | None |")
    lines.append("|---|---|---|---|---|---|---|---|")

    journeys = sorted(set(r["journey"] for r in records))
    for j in journeys:
        group = [r for r in records if r["journey"] == j]
        n = len(group)
        md_disc = mean([r["discoverability"] for r in group])
        md_diag = mean([r["diag_avg"] for r in group])
        md_act = mean([r["act_avg"] for r in group])
        fab = sum(1 for r in group if r["fab_either"]) / n * 100
        full = sum(1 for r in group if r["coverage"] == "Full")
        none = sum(1 for r in group if r["coverage"] == "None")
        lines.append(f"| {j} | {n} | {md_disc:.2f} | {md_diag:.2f} | {md_act:.2f} | {fab:.1f}% | {full} | {none} |")

    lines.append("")

    # === 5. Fabrication by Discoverability ===
    lines.append("## 5. Fabrication Distribution")
    lines.append("")
    lines.append("Where does fabrication concentrate?")
    lines.append("")

    fab_cases = [r for r in records if r["fab_either"]]
    lines.append(f"**Total fabrication cases:** {len(fab_cases)}/{len(records)} ({len(fab_cases)/len(records)*100:.1f}%)")
    lines.append("")

    lines.append("| Discoverability | Total | Fabricated | Rate |")
    lines.append("|---|---|---|---|")
    for d in [3, 2, 1, 0]:
        total = [r for r in records if r["discoverability"] == d]
        fab = [r for r in total if r["fab_either"]]
        if total:
            lines.append(f"| {disc_labels[d]} | {len(total)} | {len(fab)} | {len(fab)/len(total)*100:.1f}% |")

    lines.append("")
    lines.append("| Coverage | Total | Fabricated | Rate |")
    lines.append("|---|---|---|---|")
    for cov in ["Full", "Partial", "None"]:
        total = [r for r in records if r["coverage"] == cov]
        fab = [r for r in total if r["fab_either"]]
        if total:
            lines.append(f"| {cov} | {len(total)} | {len(fab)} | {len(fab)/len(total)*100:.1f}% |")

    lines.append("")

    # === 6. Key Findings ===
    lines.append("## 6. Key Findings")
    lines.append("")

    # Compute the key deltas
    disc3 = [r for r in records if r["discoverability"] == 3]
    disc0 = [r for r in records if r["discoverability"] == 0]
    cov_full = [r for r in records if r["coverage"] == "Full"]
    cov_none = [r for r in records if r["coverage"] == "None"]

    if disc3 and disc0:
        delta_diag = mean([r["diag_avg"] for r in disc3]) - mean([r["diag_avg"] for r in disc0])
        delta_act = mean([r["act_avg"] for r in disc3]) - mean([r["act_avg"] for r in disc0])
        lines.append(f"1. **Discoverability gap (Direct vs Missing):** Diagnosis Δ={delta_diag:+.2f}, Actionability Δ={delta_act:+.2f}")

    if cov_full and cov_none:
        delta_diag = mean([r["diag_avg"] for r in cov_full]) - mean([r["diag_avg"] for r in cov_none])
        delta_act = mean([r["act_avg"] for r in cov_full]) - mean([r["act_avg"] for r in cov_none])
        lines.append(f"2. **Coverage gap (Full vs None):** Diagnosis Δ={delta_diag:+.2f}, Actionability Δ={delta_act:+.2f}")

    lines.append(f"3. **Spearman correlations:** Disc↔Diag ρ={rho_diag:.3f}, Disc↔Act ρ={rho_act:.3f}")

    if abs(rho_diag) < 0.2 and abs(rho_act) < 0.2:
        lines.append("")
        lines.append("**⚠️ Weak correlations suggest discoverability alone does not strongly predict resolution quality.** "
                      "This could mean: (a) agents compensate via non-doc sources even in doc-restricted mode, "
                      "(b) doc quality (not just existence) is the bottleneck, or "
                      "(c) the discoverability rubric captures page-topic match but not content depth.")
    elif abs(rho_diag) > 0.4 or abs(rho_act) > 0.4:
        lines.append("")
        lines.append("**Strong correlations confirm: better discoverability → better agent answers.** "
                      "Improving search ranking and doc discoverability is a high-leverage intervention.")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by `scripts/cross_reference.py`*")

    output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
