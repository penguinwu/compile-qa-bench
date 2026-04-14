#!/usr/bin/env python3
"""
Build a held-out validation set for rubric generalization testing.

Selects 24 new cases (3 per journey × 8 journeys) from the issue corpus,
excluding all 160 cases in the existing test suite. Uses the same
classification logic as build_balanced_test_suite.py.

Usage:
    python scripts/build_holdout_set.py \
        --corpus ~/projects/pt2-github-issues/pytorch-issues-pt2.json \
        --existing suite/cases.json \
        --output suite/holdout_cases.json
"""

import argparse
import json
import random
import re
from collections import defaultdict


def extract_labels(issue):
    """Extract label names from label objects."""
    labels = issue.get("labels", [])
    if not labels:
        return set()
    if isinstance(labels[0], str):
        return set(labels)
    return {l["name"] for l in labels if isinstance(l, dict) and "name" in l}


def classify_issue(issue):
    """Classify an issue into a journey. Same logic as build_balanced_test_suite.py."""
    labels = extract_labels(issue)
    title = (issue.get("title") or "").lower()
    body = (issue.get("body") or "").lower()
    text = title + " " + body[:3000]

    if "module: graph breaks" in labels:
        return "J4"
    if "module: dynamic shapes" in labels:
        return "J6"
    if "module: correctness (silent)" in labels:
        return "J3"
    if "module: compile-time" in labels:
        return "J7"
    if "module: custom-operators" in labels or "module: higher order operators" in labels:
        return "J8"
    if "module: flex attention" in labels:
        return "J8"
    if "module: cuda graphs" in labels:
        return "J5"

    if re.search(r"graph.?break|fullgraph|graph_break|breaks_in_graph", text):
        return "J4"
    if re.search(r"dynamic.?shape|recompil|guard|shape.?guard|symbolic.?int|unbacked", text):
        if re.search(r"recompil.*slow|slow.*recompil|compilation.*time|compile.*time|cold.?start", text):
            return "J7"
        return "J6"
    if re.search(r"wrong.?result|incorrect.?result|numerical|accuracy|silent.*error|correctness|diverge|mismatch.*output|output.*mismatch|produces.*different", text):
        return "J3"
    if re.search(r"custom.?op|torch\.library|flex.?attention|while.?loop|scan|cond\b|higher.?order|wrap_with_set_grad|autograd\.function.*compile|vmap.*compile|functorch", text):
        return "J8"
    if re.search(r"compile.*time|compilation.*slow|cold.?start|compile.*slow|compilation.*time|too.*long.*compil|compil.*forever|compil.*minutes|compil.*hours", text):
        return "J7"
    if re.search(r"cache.*compil|compil.*cache|persistent.*cache|save.*cache|load.*cache", text):
        return "J7"
    if re.search(r"slower.*eager|eager.*faster|no.*speedup|regression.*perf|performance.*regression|torch\.compile.*slow(?!.*compil)|compiled.*slower|perf.*degradation", text):
        return "J2"
    if re.search(r"runtime.*overhead|overhead.*runtime|small.*graph.*overhead|overhead.*small", text):
        return "J2"
    if re.search(r"(?:slow|perf).*(?:inductor|compile|compiled)|(?:inductor|compile|compiled).*(?:slow|perf)(?!.*compil.*time)", text):
        if not re.search(r"compil(?:e|ation)\s+(?:time|speed|duration|overhead)", text):
            return "J2"

    if "module: performance" in labels:
        if re.search(r"slower.*eager|eager.*faster|no.*speedup|diagnos|regression", text):
            return "J2"
        return "J5"
    if re.search(r"max.?autotune|triton|kernel.*optim|fus(?:ion|e)|inductor.*perf|cudagraph|cuda.?graph|optimize|tun(?:e|ing)|throughput", text):
        return "J5"

    if re.search(r"how.?to|getting.?start|basic.*usage|migrat|tutorial|documentation|doc.*issue|beginner|first.*time|new.*to|learn|example|api.*doc|torch\.compile\b.*(?:not|doesn.t|can.t).*work", text):
        return "J1"

    if "module: inductor" in labels:
        if re.search(r"perf|speed|slow|fast|optim|throughput", text):
            return "J5"
        if re.search(r"error|crash|fail|bug|wrong|incorrect", text):
            return "J3"
        return "J5"
    if "module: dynamo" in labels:
        if re.search(r"error|crash|fail|bug", text):
            return "J4"
        return "J1"

    return None


def is_ci_or_bot_issue(issue):
    """Filter out CI/bot/infra issues."""
    title = issue.get("title", "")
    if title.startswith("DISABLED") or title.startswith("UNSTABLE") or title.startswith("[CI]"):
        return True
    if re.match(r"^\[.*\]\s*(DISABLED|UNSTABLE)", title):
        return True
    labels = extract_labels(issue)
    if "module: tests" in labels and "oncall: pt2" not in labels:
        return True
    return False


def is_export_issue(issue):
    """Filter out export/AOTInductor issues."""
    labels = extract_labels(issue)
    if "oncall: export" in labels:
        return True
    title = (issue.get("title") or "").lower()
    if "aotinductor" in title or "torch.export" in title:
        return True
    return False


def build_question(issue):
    """Build a natural language question from the issue."""
    title = issue.get("title", "")
    body = (issue.get("body") or "")[:1500]
    # Simple heuristic: use title as base question
    q = title.strip()
    if not q.endswith("?"):
        q = f"How do I resolve: {q}"
    return q


def main():
    parser = argparse.ArgumentParser(description="Build held-out validation set")
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--existing", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--per-journey", type=int, default=3, help="Cases per journey (default 3)")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    with open(args.corpus) as f:
        corpus = json.load(f)
    with open(args.existing) as f:
        existing = json.load(f)

    # Get existing issue numbers
    existing_nums = set()
    for c in existing:
        url = c.get("source_url", "")
        num = url.split("/")[-1]
        if num.isdigit():
            existing_nums.add(int(num))
    print(f"Existing cases: {len(existing_nums)} issue numbers")

    # Filter and classify
    candidates = defaultdict(lambda: {"resolved": [], "unresolved": []})
    skipped = {"ci": 0, "export": 0, "unclassified": 0, "existing": 0, "no_body": 0}

    for issue in corpus:
        num = issue["number"]
        if num in existing_nums:
            skipped["existing"] += 1
            continue
        if is_ci_or_bot_issue(issue):
            skipped["ci"] += 1
            continue
        if is_export_issue(issue):
            skipped["export"] += 1
            continue
        if not issue.get("body"):
            skipped["no_body"] += 1
            continue

        journey = classify_issue(issue)
        if not journey:
            skipped["unclassified"] += 1
            continue

        state = issue["state"]
        bucket = "resolved" if state == "CLOSED" else "unresolved"
        candidates[journey][bucket].append(issue)

    print(f"\nSkipped: {skipped}")
    print(f"\nCandidates by journey:")
    for j in sorted(candidates):
        r = len(candidates[j]["resolved"])
        u = len(candidates[j]["unresolved"])
        print(f"  {j}: {r} resolved, {u} unresolved")

    # Select cases: balance resolved/unresolved within each journey
    holdout = []
    target = args.per_journey

    for j in sorted(candidates):
        resolved = candidates[j]["resolved"]
        unresolved = candidates[j]["unresolved"]

        # Try to get a mix: ceil(target/2) resolved, rest unresolved
        n_resolved = min((target + 1) // 2, len(resolved))
        n_unresolved = min(target - n_resolved, len(unresolved))
        # If not enough unresolved, take more resolved
        if n_resolved + n_unresolved < target:
            n_resolved = min(target - n_unresolved, len(resolved))

        random.shuffle(resolved)
        random.shuffle(unresolved)

        selected_r = resolved[:n_resolved]
        selected_u = unresolved[:n_unresolved]

        for idx, issue in enumerate(selected_r + selected_u, 1):
            case_id = f"{j}-H{idx}"
            status = "resolved" if issue["state"] == "CLOSED" else "unresolved"
            holdout.append({
                "id": case_id,
                "journey": j,
                "source_issue": issue["number"],
                "source_url": f"https://github.com/pytorch/pytorch/issues/{issue['number']}",
                "user_question": build_question(issue),
                "resolution_status": status,
                "issue_context": (issue.get("body") or "")[:1500],
            })

    print(f"\nHeld-out set: {len(holdout)} cases")
    for j in sorted(set(c["journey"] for c in holdout)):
        jc = [c for c in holdout if c["journey"] == j]
        r = sum(1 for c in jc if c["resolution_status"] == "resolved")
        u = sum(1 for c in jc if c["resolution_status"] == "unresolved")
        print(f"  {j}: {r} resolved, {u} unresolved")

    with open(args.output, "w") as f:
        json.dump(holdout, f, indent=2)
    print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()
