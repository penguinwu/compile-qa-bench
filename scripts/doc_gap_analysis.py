#!/usr/bin/env python3
"""Documentation Gap Analysis — Cross-referencing Track 1 vs Track 2 scoring data.

Uses calibrated Track 1 scores and Owl's Track 2 scores to identify:
1. Per-journey documentation gap severity
2. Specific missing documentation topics (mechanism-level, actionable content)
3. Cases where doc-restriction causes the biggest quality drops
4. Template response patterns as indicators of missing pages

Output: Markdown report suitable for stakeholder review.

Usage:
    python3 scripts/doc_gap_analysis.py
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# --- File paths ---
CASES = BASE / "suite" / "cases.json"
T1_ACT = BASE / "runs/label-scoring/owl_act_labels_track1_160_calibrated.json"
T1_DIAG = BASE / "runs/label-scoring/owl_diag_labels_track1_160_calibrated.json"
T2_ACT = BASE / "runs/label-scoring/owl_act_labels_track2_160.json"
T2_DIAG = BASE / "runs/label-scoring/owl_diag_labels_track2_160.json"
T2_BASELINE = BASE / "runs/2026-04-12-baseline/mode_b_doc_restricted.json"
T1_BASELINE = BASE / "runs/2026-04-12-baseline/mode_b_results.json"

# Fallback to uncalibrated T1 if calibrated doesn't exist
if not T1_ACT.exists():
    T1_ACT = BASE / "runs/label-scoring/owl_act_labels_track1_160.json"
if not T1_DIAG.exists():
    T1_DIAG = BASE / "runs/label-scoring/owl_diag_labels_track1_160.json"


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("results", data.get("scores", []))
    return data


def by_id(records):
    return {r["id"]: r for r in records}


def compute_act_score(labels):
    if labels.get("standalone_fix", False):
        return 3
    if labels.get("has_imperative", False) and labels.get("case_specific", False):
        return 2
    if labels.get("has_imperative", False):
        return 1
    return 0


def compute_diag_score(labels):
    if not labels.get("consistent_with_resolution", True):
        return min(1, sum([
            labels.get("correct_subsystem", False),
            labels.get("names_mechanism", False),
            labels.get("causal_chain", False),
            labels.get("case_specific_diagnosis", False),
        ]))
    count = sum([
        labels.get("correct_subsystem", False),
        labels.get("names_mechanism", False),
        labels.get("causal_chain", False),
        labels.get("case_specific_diagnosis", False),
    ])
    if count >= 3:
        return 3
    return count


def get_derived(rec, dim):
    key = f"derived_{dim}"
    if key in rec:
        return rec[key]
    return compute_act_score(rec) if dim == "act" else compute_diag_score(rec)


def journey_id(case_id):
    """Extract journey prefix: J1-3 -> J1"""
    return case_id.split("-")[0]


JOURNEY_NAMES = {
    "J1": "First Compile (Getting Started)",
    "J2": "Performance Diagnosis (Why Is It Slow?)",
    "J3": "Correctness & Debugging (Wrong Results)",
    "J4": "Graph Breaks",
    "J5": "Performance Optimization (Making It Faster)",
    "J6": "Dynamic Shapes",
    "J7": "Compile-Time Performance (Compilation Too Slow)",
    "J8": "Custom & Higher-Order Ops",
}


def main():
    # Load all data
    cases = load_json(CASES)
    cases_by_id = by_id(cases)

    t1_act = by_id(load_json(T1_ACT))
    t1_diag = by_id(load_json(T1_DIAG))
    t2_act = by_id(load_json(T2_ACT))
    t2_diag = by_id(load_json(T2_DIAG))
    t2_baseline = by_id(load_json(T2_BASELINE))

    all_ids = sorted(t1_act.keys())
    assert set(all_ids) == set(t2_act.keys()), "ID mismatch between tracks"

    # --- Per-case gap computation ---
    case_gaps = []
    for cid in all_ids:
        t1a = get_derived(t1_act[cid], "act")
        t1d = get_derived(t1_diag[cid], "diag")
        t2a = get_derived(t2_act[cid], "act")
        t2d = get_derived(t2_diag[cid], "diag")

        doc_suf = t2_baseline[cid].get("doc_sufficient", None)
        is_template = t2_act[cid].get("is_template", False)

        # Label-level gaps
        t1_nm = t1_diag[cid].get("names_mechanism", False)
        t2_nm = t2_diag[cid].get("names_mechanism", False)
        t1_cc = t1_diag[cid].get("causal_chain", False)
        t2_cc = t2_diag[cid].get("causal_chain", False)
        t1_sf = t1_act[cid].get("standalone_fix", False)
        t2_sf = t2_act[cid].get("standalone_fix", False)
        t1_cs = t1_act[cid].get("case_specific", False)
        t2_cs = t2_act[cid].get("case_specific", False)
        t1_csd = t1_diag[cid].get("case_specific_diagnosis", False)
        t2_csd = t2_diag[cid].get("case_specific_diagnosis", False)

        jid = journey_id(cid)
        case_info = cases_by_id.get(cid, {})

        case_gaps.append({
            "id": cid,
            "journey": jid,
            "user_question": case_info.get("user_question", ""),
            "difficulty": case_info.get("difficulty", ""),
            "expected_doc_topics": case_info.get("expected_doc_topics", []),
            "resolution_status": case_info.get("resolution_status", ""),
            "t1_act": t1a, "t2_act": t2a, "act_drop": t1a - t2a,
            "t1_diag": t1d, "t2_diag": t2d, "diag_drop": t1d - t2d,
            "doc_sufficient": doc_suf,
            "is_template": is_template,
            # Label gaps (T1=true, T2=false = doc gap signal)
            "nm_gap": t1_nm and not t2_nm,  # mechanism doc missing
            "cc_gap": t1_cc and not t2_cc,  # causal chain doc missing
            "sf_gap": t1_sf and not t2_sf,  # fix doc missing
            "cs_gap": t1_cs and not t2_cs,  # case-specific content missing
            "csd_gap": t1_csd and not t2_csd,  # case-specific diagnosis missing
            # Raw labels for detailed analysis
            "t1_nm": t1_nm, "t2_nm": t2_nm,
            "t1_cc": t1_cc, "t2_cc": t2_cc,
            "t1_sf": t1_sf, "t2_sf": t2_sf,
            "t1_csd": t1_csd, "t2_csd": t2_csd,
        })

    # --- Journey-level aggregation ---
    journey_stats = defaultdict(lambda: {
        "cases": [],
        "t1_act_sum": 0, "t2_act_sum": 0,
        "t1_diag_sum": 0, "t2_diag_sum": 0,
        "doc_sufficient_count": 0,
        "template_count": 0,
        "nm_gap_count": 0,
        "cc_gap_count": 0,
        "sf_gap_count": 0,
        "csd_gap_count": 0,
        "act_drop_sum": 0,
        "diag_drop_sum": 0,
        "t2_act0_count": 0,
        "n": 0,
    })

    for g in case_gaps:
        j = journey_stats[g["journey"]]
        j["cases"].append(g)
        j["n"] += 1
        j["t1_act_sum"] += g["t1_act"]
        j["t2_act_sum"] += g["t2_act"]
        j["t1_diag_sum"] += g["t1_diag"]
        j["t2_diag_sum"] += g["t2_diag"]
        j["doc_sufficient_count"] += (1 if g["doc_sufficient"] else 0)
        j["template_count"] += (1 if g["is_template"] else 0)
        j["nm_gap_count"] += (1 if g["nm_gap"] else 0)
        j["cc_gap_count"] += (1 if g["cc_gap"] else 0)
        j["sf_gap_count"] += (1 if g["sf_gap"] else 0)
        j["csd_gap_count"] += (1 if g["csd_gap"] else 0)
        j["act_drop_sum"] += g["act_drop"]
        j["diag_drop_sum"] += g["diag_drop"]
        j["t2_act0_count"] += (1 if g["t2_act"] == 0 else 0)

    # --- Generate report ---
    lines = []
    def w(s=""):
        lines.append(s)

    w("# Documentation Gap Analysis — torch.compile User Journeys")
    w()
    w("**Date:** 2026-04-15")
    w("**Method:** Cross-referencing Track 1 (unrestricted) vs Track 2 (doc-restricted) label scores")
    w("**Data:** 160 cases scored on Actionability (Act 0-3) and Diagnostic Quality (Diag 0-3)")
    w("**Scorer:** Owl (calibrated Track 1, Rules 3-5 applied to Track 2)")
    w()

    # Executive summary
    w("## Executive Summary")
    w()
    total_doc_suf = sum(1 for g in case_gaps if g["doc_sufficient"])
    total_template = sum(1 for g in case_gaps if g["is_template"])
    total_nm_gap = sum(1 for g in case_gaps if g["nm_gap"])
    total_cc_gap = sum(1 for g in case_gaps if g["cc_gap"])
    total_sf_gap = sum(1 for g in case_gaps if g["sf_gap"])
    avg_act_drop = sum(g["act_drop"] for g in case_gaps) / len(case_gaps)
    avg_diag_drop = sum(g["diag_drop"] for g in case_gaps) / len(case_gaps)

    w(f"Of 160 torch.compile support cases, **{160 - total_doc_suf} ({100*(160-total_doc_suf)/160:.0f}%)** cannot be adequately addressed using official PyTorch documentation alone. Key findings:")
    w()
    w(f"- **Actionability collapse:** Mean Act score drops from {sum(g['t1_act'] for g in case_gaps)/160:.2f} (Track 1) to {sum(g['t2_act'] for g in case_gaps)/160:.2f} (Track 2) — a **{avg_act_drop:.2f}-point** average drop")
    w(f"- **Diagnostic depth loss:** Mean Diag score drops from {sum(g['t1_diag'] for g in case_gaps)/160:.2f} to {sum(g['t2_diag'] for g in case_gaps)/160:.2f} — a **{avg_diag_drop:.2f}-point** average drop")
    w(f"- **{total_template} cases ({100*total_template/160:.0f}%)** receive identical template responses (no case-specific content)")
    w(f"- **{total_nm_gap} cases ({100*total_nm_gap/160:.0f}%)** lose mechanism-level information when restricted to docs (names_mechanism gap)")
    w(f"- **{total_cc_gap} cases** lose causal chain explanations (why the issue occurs)")
    w(f"- **{total_sf_gap} cases ({100*total_sf_gap/160:.0f}%)** lose standalone fixes")
    w()
    w("The mechanism gap is particularly significant: for many topics, official docs provide only diagnostic tool references (e.g., TORCH_LOGS, profiler) without explaining the underlying mechanisms. This means doc-restricted agents can point users to debugging tools but cannot name what went wrong — the docs literally don't contain that information.")
    w()

    # Journey-level gap ranking
    w("## Journey-Level Gap Severity")
    w()
    w("Journeys ranked by combined documentation gap severity (Act + Diag drop):")
    w()
    w("| Journey | N | T1 Act | T2 Act | Act Δ | T1 Diag | T2 Diag | Diag Δ | Doc Suf | Templates | NM Gap |")
    w("|---------|---|--------|--------|-------|---------|---------|--------|---------|-----------|--------|")

    # Sort by combined drop (worst first)
    sorted_journeys = sorted(journey_stats.items(),
                              key=lambda x: (x[1]["act_drop_sum"] + x[1]["diag_drop_sum"]) / x[1]["n"],
                              reverse=True)

    for jid, js in sorted_journeys:
        n = js["n"]
        jname = JOURNEY_NAMES.get(jid, jid)
        t1a = js["t1_act_sum"] / n
        t2a = js["t2_act_sum"] / n
        t1d = js["t1_diag_sum"] / n
        t2d = js["t2_diag_sum"] / n
        act_d = t1a - t2a
        diag_d = t1d - t2d
        ds = js["doc_sufficient_count"]
        tmpl = js["template_count"]
        nm = js["nm_gap_count"]
        w(f"| {jid}: {jname} | {n} | {t1a:.1f} | {t2a:.1f} | **-{act_d:.1f}** | {t1d:.1f} | {t2d:.1f} | **-{diag_d:.1f}** | {ds}/{n} | {tmpl} | {nm} |")

    w()

    # --- Detailed per-journey analysis ---
    w("## Per-Journey Documentation Gap Details")
    w()

    for jid, js in sorted_journeys:
        n = js["n"]
        jname = JOURNEY_NAMES.get(jid, jid)
        w(f"### {jid}: {jname}")
        w()

        # Summary stats
        t1a = js["t1_act_sum"] / n
        t2a = js["t2_act_sum"] / n
        t1d = js["t1_diag_sum"] / n
        t2d = js["t2_diag_sum"] / n

        w(f"**{n} cases** | Doc sufficient: {js['doc_sufficient_count']}/{n} | Templates: {js['template_count']}/{n}")
        w(f"Act: {t1a:.1f} → {t2a:.1f} (Δ={t1a-t2a:.1f}) | Diag: {t1d:.1f} → {t2d:.1f} (Δ={t1d-t2d:.1f})")
        w()

        # What's missing - mechanism gaps
        nm_gap_cases = [c for c in js["cases"] if c["nm_gap"]]
        if nm_gap_cases:
            w(f"**Missing mechanism documentation ({len(nm_gap_cases)} cases):**")
            w("These cases have names_mechanism=true in Track 1 but false in Track 2 — the docs don't contain the mechanism-level information needed to explain what went wrong.")
            w()
            for c in nm_gap_cases:
                topics = ", ".join(c["expected_doc_topics"]) if c["expected_doc_topics"] else "N/A"
                w(f"- **{c['id']}**: {c['user_question'][:120]}...")
                w(f"  - Expected topics: {topics}")
                w(f"  - Act: {c['t1_act']}→{c['t2_act']} | Diag: {c['t1_diag']}→{c['t2_diag']}")
            w()

        # What's missing - standalone fix gaps
        sf_gap_cases = [c for c in js["cases"] if c["sf_gap"]]
        if sf_gap_cases:
            w(f"**Missing fix/workaround documentation ({len(sf_gap_cases)} cases):**")
            w("Track 1 provides standalone fixes; Track 2 cannot — the fix information isn't in official docs.")
            w()
            for c in sf_gap_cases:
                topics = ", ".join(c["expected_doc_topics"]) if c["expected_doc_topics"] else "N/A"
                w(f"- **{c['id']}**: {c['user_question'][:120]}...")
                w(f"  - Expected topics: {topics}")
            w()

        # Causal chain gaps
        cc_gap_cases = [c for c in js["cases"] if c["cc_gap"]]
        if cc_gap_cases:
            w(f"**Missing causal explanations ({len(cc_gap_cases)} cases):**")
            w("Track 1 explains why the issue occurs; Track 2 cannot connect mechanism to symptom.")
            w()
            for c in cc_gap_cases:
                w(f"- **{c['id']}**: {c['user_question'][:120]}...")
                w(f"  - Act: {c['t1_act']}→{c['t2_act']} | Diag: {c['t1_diag']}→{c['t2_diag']}")
            w()

        # Template responses (entire missing pages)
        template_cases = [c for c in js["cases"] if c["is_template"]]
        if template_cases:
            w(f"**Template responses ({len(template_cases)} cases) — likely missing documentation pages:**")
            w("These cases all received identical boilerplate responses, suggesting the docs have no relevant page at all.")
            w()
            for c in template_cases:
                topics = ", ".join(c["expected_doc_topics"]) if c["expected_doc_topics"] else "N/A"
                q = c["user_question"][:120]
                w(f"- **{c['id']}**: {q}...")
                w(f"  - Expected topics: {topics}")
            w()

        # Worst individual drops
        worst = sorted(js["cases"], key=lambda c: c["act_drop"] + c["diag_drop"], reverse=True)[:5]
        if worst and (worst[0]["act_drop"] + worst[0]["diag_drop"]) > 0:
            w(f"**Largest individual drops (top 5):**")
            w()
            w("| Case | Question (truncated) | T1 Act→T2 | T1 Diag→T2 | Doc Suf |")
            w("|------|---------------------|-----------|------------|---------|")
            for c in worst:
                if c["act_drop"] + c["diag_drop"] <= 0:
                    continue
                q = c["user_question"][:60]
                ds = "Yes" if c["doc_sufficient"] else "No"
                w(f"| {c['id']} | {q} | {c['t1_act']}→{c['t2_act']} | {c['t1_diag']}→{c['t2_diag']} | {ds} |")
            w()

        w("---")
        w()

    # --- Cross-cutting analysis ---
    w("## Cross-Cutting Analysis")
    w()

    # 1. Topic-level gap clustering
    w("### Missing Documentation Topics")
    w()
    w("Aggregating `expected_doc_topics` from cases with the largest gaps (Act drop ≥ 2 or Diag drop ≥ 2):")
    w()

    topic_counts = Counter()
    high_gap_cases = [g for g in case_gaps if g["act_drop"] >= 2 or g["diag_drop"] >= 2]
    for g in high_gap_cases:
        for t in g["expected_doc_topics"]:
            topic_counts[t] += 1

    w(f"**{len(high_gap_cases)} cases** with high documentation gaps (≥2 point drop):")
    w()
    for topic, count in topic_counts.most_common(30):
        w(f"- **{topic}** — {count} cases")
    w()

    # 2. Mechanism gap as doc signal
    w("### Mechanism Documentation Gaps (names_mechanism analysis)")
    w()
    w("Per Peng's insight: when Track 1 achieves names_mechanism=true but Track 2 achieves names_mechanism=false, this directly measures **missing mechanism-level documentation**. The doc-restricted agent can only cite diagnostic tools (TORCH_LOGS, profiler); the underlying mechanisms that explain root causes are not documented.")
    w()

    nm_gap_by_journey = defaultdict(list)
    for g in case_gaps:
        if g["nm_gap"]:
            nm_gap_by_journey[g["journey"]].append(g)

    w(f"**Total mechanism gaps: {total_nm_gap}/{160} cases ({100*total_nm_gap/160:.0f}%)**")
    w()
    if nm_gap_by_journey:
        w("| Journey | Cases with NM gap | Example topics needing mechanism docs |")
        w("|---------|-------------------|--------------------------------------|")
        for jid in sorted(nm_gap_by_journey.keys()):
            cases_list = nm_gap_by_journey[jid]
            # Collect unique topics from these cases
            topics = set()
            for c in cases_list:
                topics.update(c["expected_doc_topics"])
            topics_str = ", ".join(sorted(topics)[:5])
            w(f"| {jid}: {JOURNEY_NAMES.get(jid, jid)} | {len(cases_list)} | {topics_str} |")
        w()

    # 3. Template analysis — entirely missing pages
    w("### Template Response Analysis (Missing Documentation Pages)")
    w()
    w("Template responses indicate the agent found NO relevant documentation and fell back to generic boilerplate. These signal **entire missing pages**, not just missing details within existing pages.")
    w()

    template_by_journey = defaultdict(list)
    template_topics = Counter()
    for g in case_gaps:
        if g["is_template"]:
            template_by_journey[g["journey"]].append(g)
            for t in g["expected_doc_topics"]:
                template_topics[t] += 1

    w(f"**{total_template} template responses across {len(template_by_journey)} journeys**")
    w()
    if template_topics:
        w("Documentation pages that likely need to be **created** (topics from template cases):")
        w()
        for topic, count in template_topics.most_common(20):
            w(f"- **{topic}** — {count} template cases")
        w()

    # 4. Doc-sufficient vs doc-insufficient breakdown
    w("### Doc Sufficiency Breakdown")
    w()
    w("Cases where doc_sufficient=True maintained similar quality across tracks vs. cases where it didn't:")
    w()

    doc_suf_cases = [g for g in case_gaps if g["doc_sufficient"]]
    doc_insuf_cases = [g for g in case_gaps if not g["doc_sufficient"]]

    if doc_suf_cases:
        suf_act_drop = sum(g["act_drop"] for g in doc_suf_cases) / len(doc_suf_cases)
        suf_diag_drop = sum(g["diag_drop"] for g in doc_suf_cases) / len(doc_suf_cases)
    else:
        suf_act_drop = suf_diag_drop = 0

    if doc_insuf_cases:
        insuf_act_drop = sum(g["act_drop"] for g in doc_insuf_cases) / len(doc_insuf_cases)
        insuf_diag_drop = sum(g["diag_drop"] for g in doc_insuf_cases) / len(doc_insuf_cases)
    else:
        insuf_act_drop = insuf_diag_drop = 0

    w(f"| Group | N | Mean Act Drop | Mean Diag Drop |")
    w(f"|-------|---|---------------|----------------|")
    w(f"| Doc sufficient=True | {len(doc_suf_cases)} | {suf_act_drop:.2f} | {suf_diag_drop:.2f} |")
    w(f"| Doc sufficient=False | {len(doc_insuf_cases)} | {insuf_act_drop:.2f} | {insuf_diag_drop:.2f} |")
    w()

    # 5. Difficulty breakdown
    w("### Gap by Issue Difficulty")
    w()
    diff_stats = defaultdict(lambda: {"n": 0, "act_drop": 0, "diag_drop": 0, "doc_suf": 0})
    for g in case_gaps:
        d = g["difficulty"] or "unknown"
        diff_stats[d]["n"] += 1
        diff_stats[d]["act_drop"] += g["act_drop"]
        diff_stats[d]["diag_drop"] += g["diag_drop"]
        diff_stats[d]["doc_suf"] += (1 if g["doc_sufficient"] else 0)

    w("| Difficulty | N | Mean Act Drop | Mean Diag Drop | Doc Sufficient |")
    w("|-----------|---|---------------|----------------|----------------|")
    for d in ["beginner", "intermediate", "advanced"]:
        if d in diff_stats:
            ds = diff_stats[d]
            w(f"| {d} | {ds['n']} | {ds['act_drop']/ds['n']:.2f} | {ds['diag_drop']/ds['n']:.2f} | {ds['doc_suf']}/{ds['n']} ({100*ds['doc_suf']/ds['n']:.0f}%) |")
    w()

    # --- Recommendations ---
    w("## Recommendations: Priority Documentation Work")
    w()
    w("Based on the gap analysis, documentation improvements are prioritized by impact (number of cases affected × severity of quality drop):")
    w()

    # Compute impact scores per journey
    impacts = []
    for jid, js in journey_stats.items():
        n = js["n"]
        act_drop = js["act_drop_sum"] / n
        diag_drop = js["diag_drop_sum"] / n
        impact = n * (act_drop + diag_drop)
        jname = JOURNEY_NAMES.get(jid, jid)
        impacts.append((jid, jname, n, act_drop, diag_drop, impact, js))

    impacts.sort(key=lambda x: x[5], reverse=True)

    w("### Priority 1: High-Impact Gaps (entire pages or major sections needed)")
    w()
    for jid, jname, n, act_d, diag_d, impact, js in impacts[:3]:
        w(f"**{jid}: {jname}** (impact score: {impact:.0f})")
        # Collect all expected topics from high-gap cases in this journey
        hg = [c for c in js["cases"] if c["act_drop"] >= 2 or c["diag_drop"] >= 2]
        if hg:
            topics = Counter()
            for c in hg:
                for t in c["expected_doc_topics"]:
                    topics[t] += 1
            w(f"- {len(hg)}/{n} cases have ≥2-point quality drops")
            w(f"- Key missing topics: {', '.join(t for t, _ in topics.most_common(5))}")
            if js["template_count"] > 0:
                w(f"- {js['template_count']} template responses (no relevant page found)")
            if js["nm_gap_count"] > 0:
                w(f"- {js['nm_gap_count']} cases missing mechanism-level documentation")
        w()

    w("### Priority 2: Mechanism Documentation (explanations of how things work)")
    w()
    w("These topics have diagnostic tool references in the docs but lack explanations of the underlying mechanisms. Users can be told to \"check TORCH_LOGS\" but not told *what* the logs will reveal or *why* the issue occurs.")
    w()
    for jid in sorted(nm_gap_by_journey.keys()):
        cases_list = nm_gap_by_journey[jid]
        topics = set()
        for c in cases_list:
            topics.update(c["expected_doc_topics"])
        jname = JOURNEY_NAMES.get(jid, jid)
        w(f"- **{jid}: {jname}** — {len(cases_list)} cases need mechanism docs")
        for t in sorted(topics):
            w(f"  - {t}")
    w()

    w("### Priority 3: Workaround/Fix Documentation")
    w()
    w("Cases where Track 1 provides a standalone fix but Track 2 cannot — the workaround exists but isn't documented:")
    w()
    sf_gap_by_journey = defaultdict(list)
    for g in case_gaps:
        if g["sf_gap"]:
            sf_gap_by_journey[g["journey"]].append(g)

    for jid in sorted(sf_gap_by_journey.keys()):
        cases_list = sf_gap_by_journey[jid]
        jname = JOURNEY_NAMES.get(jid, jid)
        topics = set()
        for c in cases_list:
            topics.update(c["expected_doc_topics"])
        w(f"- **{jid}: {jname}** — {len(cases_list)} undocumented fixes")
        for t in sorted(topics):
            w(f"  - {t}")
    w()

    # --- Appendix: Full case-level data ---
    w("## Appendix: All Cases Sorted by Gap Severity")
    w()
    w("| Case | Journey | T1 Act | T2 Act | T1 Diag | T2 Diag | Total Drop | Doc Suf | Template | NM Gap |")
    w("|------|---------|--------|--------|---------|---------|------------|---------|----------|--------|")

    sorted_cases = sorted(case_gaps, key=lambda g: g["act_drop"] + g["diag_drop"], reverse=True)
    for g in sorted_cases:
        total_drop = g["act_drop"] + g["diag_drop"]
        ds = "Y" if g["doc_sufficient"] else "N"
        tmpl = "Y" if g["is_template"] else ""
        nm = "Y" if g["nm_gap"] else ""
        w(f"| {g['id']} | {g['journey']} | {g['t1_act']} | {g['t2_act']} | {g['t1_diag']} | {g['t2_diag']} | {total_drop} | {ds} | {tmpl} | {nm} |")

    w()
    w("---")
    w("*Analysis generated by `scripts/doc_gap_analysis.py` from Owl's calibrated scoring data.*")

    report = "\n".join(lines)
    out_path = BASE / "analysis" / "documentation_gap_analysis.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(report)

    print(f"Report written to {out_path}")
    print(f"  {len(case_gaps)} cases analyzed across {len(journey_stats)} journeys")
    print(f"  High-gap cases (≥2pt drop): {len(high_gap_cases)}")
    print(f"  Mechanism gaps: {total_nm_gap}")
    print(f"  Template responses: {total_template}")
    print(f"  Standalone fix gaps: {total_sf_gap}")

    # Also output JSON for downstream use
    json_out = BASE / "analysis" / "documentation_gap_data.json"
    with open(json_out, "w") as f:
        json.dump({
            "summary": {
                "total_cases": len(case_gaps),
                "doc_sufficient": total_doc_suf,
                "doc_insufficient": 160 - total_doc_suf,
                "template_responses": total_template,
                "mechanism_gaps": total_nm_gap,
                "causal_chain_gaps": total_cc_gap,
                "standalone_fix_gaps": total_sf_gap,
                "mean_act_drop": round(avg_act_drop, 3),
                "mean_diag_drop": round(avg_diag_drop, 3),
            },
            "journey_stats": {
                jid: {
                    "name": JOURNEY_NAMES.get(jid, jid),
                    "n": js["n"],
                    "mean_act_drop": round(js["act_drop_sum"] / js["n"], 3),
                    "mean_diag_drop": round(js["diag_drop_sum"] / js["n"], 3),
                    "doc_sufficient": js["doc_sufficient_count"],
                    "templates": js["template_count"],
                    "nm_gaps": js["nm_gap_count"],
                    "sf_gaps": js["sf_gap_count"],
                }
                for jid, js in sorted_journeys
            },
            "cases": case_gaps,
        }, f, indent=2, default=str)

    print(f"  JSON data written to {json_out}")


if __name__ == "__main__":
    main()
