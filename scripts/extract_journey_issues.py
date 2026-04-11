#!/usr/bin/env python3
"""
Extract representative GitHub issues mapped to 8 user journeys for torch.compile
documentation evaluation.

Reads pt2_all_issues.json (~9,277 issues) and selects the 5 best representative
issues per journey based on label matching, keyword heuristics, engagement,
and user-facing quality.
"""

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

INPUT_FILE = "/home/pengwu/projects/oss-model-graph-break-corpus/data/pt2-issues/pt2_all_issues.json"
OUTPUT_FILE = "/home/pengwu/.myclaw-rocky/spaces/AAQA_65oV7k/projects/corpus/journey_issues_analysis.md"

# ── Journey definitions ──────────────────────────────────────────────────────

JOURNEYS = {
    "J1": {
        "name": "First Compile (Getting Started)",
        "description": "Users trying torch.compile for the first time, basic setup, migration from eager mode.",
    },
    "J2": {
        "name": "Performance Diagnosis (Why Is It Slow?)",
        "description": "Users noticing compiled code is slower than eager, profiling, understanding overheads.",
    },
    "J3": {
        "name": "Correctness & Debugging (Wrong Results)",
        "description": "Compiled model produces different/wrong results vs eager mode, silent correctness issues.",
    },
    "J4": {
        "name": "Graph Breaks (Graph Break Errors)",
        "description": "Users encountering graph breaks that fragment compilation and hurt performance.",
    },
    "J5": {
        "name": "Performance Optimization (Making It Faster)",
        "description": "Users tuning compiled code for better performance, inductor options, kernel optimization.",
    },
    "J6": {
        "name": "Dynamic Shapes (Dynamic Shape Issues)",
        "description": "Issues with dynamic/variable input shapes causing recompilation or errors.",
    },
    "J7": {
        "name": "Compile-Time Performance (Compilation Too Slow)",
        "description": "Long compilation times, cold start, caching, recompilation exhaustion.",
    },
    "J8": {
        "name": "Custom & Higher-Order Ops",
        "description": "Issues with custom operators, higher-order operators (flex attention, scan, etc.).",
    },
}

# ── Internal / CI issue filters ──────────────────────────────────────────────

INTERNAL_TITLE_PREFIXES = [
    "DISABLED test_",
    "DISABLED Test",
    "FLAKY test_",
    "[FLAKY]",
]

INTERNAL_LABELS = {
    "module: flaky-tests",
    "skipped",
    "rocm-skipped-tests",
    "topic: not user facing",
    "topic: fuzzer",
    "internal ramp-up task",
    "better-engineering",
    "module: ci",
    "module: tests",
}

# Labels that strongly indicate CI/infra issues, not user reports
CI_TITLE_PATTERNS = [
    r"^DISABLED\s",
    r"^test_\w+\s",
    r"^\[CI\]",
    r"CI failure",
    r"CI flak",
    r"Merge conflict",
]


def is_internal_issue(issue: dict) -> bool:
    """Filter out internal dev/CI/infra issues that aren't real user questions."""
    title = issue["title"]

    # Title prefix checks
    for prefix in INTERNAL_TITLE_PREFIXES:
        if title.startswith(prefix):
            return True

    # Title regex checks
    for pattern in CI_TITLE_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True

    # Label checks
    labels = set(issue.get("labels", []))
    if labels & INTERNAL_LABELS:
        return True

    return False


# ── Journey classification ───────────────────────────────────────────────────

# Label-based mappings (strongest signals)
LABEL_TO_JOURNEY = {
    "module: graph breaks": ["J4"],
    "module: dynamic shapes": ["J6"],
    "module: custom-operators": ["J8"],
    "module: higher order operators": ["J8"],
    "module: flex attention": ["J8"],
    "module: correctness (silent)": ["J3"],
    "module: compile-time": ["J7"],
    "module: compile ux": ["J1"],
    "module: performance": ["J5"],
    "module: docs": ["J1"],
    "module: logging": ["J2"],
    "module: crash": ["J3"],
    "module: regression": ["J2"],
    "module: guards": ["J7"],
    "module: cuda graphs": ["J5"],
}

# Keyword patterns for title + body matching
# Each entry: (pattern, journeys, weight)
KEYWORD_RULES = [
    # J1: First Compile / Getting Started
    (r"\bhow\s+to\b.*\bcompile\b", ["J1"], 3),
    (r"\bgetting\s+started\b", ["J1"], 3),
    (r"\bfirst\s+time\b.*\bcompile\b", ["J1"], 3),
    (r"\bmigrat(e|ion|ing)\b.*\beager\b", ["J1"], 2),
    (r"\btorch\.compile\b.*\bnot\s+work(ing)?\b", ["J1"], 2),
    (r"\btorch\.compile\b.*\bfail(s|ing|ed)?\b", ["J1"], 1),
    (r"\bhow\s+(do|can)\s+I\b.*\bcompile\b", ["J1"], 3),
    (r"\bbasic\b.*\bcompile\b", ["J1"], 2),
    (r"\bsetup\b.*\bcompile\b", ["J1"], 2),
    (r"\bdoesn'?t\s+work\b.*\bcompile\b", ["J1"], 2),
    (r"\bcompile\b.*\bdoesn'?t\s+work\b", ["J1"], 2),
    (r"\bsupport(s|ed)?\b.*\bpython\s+3\.\d+\b", ["J1"], 2),
    (r"\btorch\.compile\b.*\berror\b", ["J1"], 1),

    # J2: Performance Diagnosis
    (r"\bslower\s+than\s+eager\b", ["J2"], 4),
    (r"\bcompil(e|ed)\b.*\bslower\b", ["J2"], 3),
    (r"\bslower\b.*\bcompil(e|ed)\b", ["J2"], 3),
    (r"\bno\s+speed\s*up\b", ["J2"], 3),
    (r"\bworse\s+performance\b", ["J2"], 3),
    (r"\bperformance\s+(regression|degradation)\b", ["J2"], 3),
    (r"\bslowdown\b", ["J2"], 2),
    (r"\bslower\s+than\b.*\b(pytorch|torch)\b", ["J2"], 2),
    (r"\btorch\s+2\.\d+\s+slower\b", ["J2"], 3),

    # J3: Correctness & Debugging
    (r"\bwrong\s+result\b", ["J3"], 4),
    (r"\bincorrect\s+(result|output)\b", ["J3"], 4),
    (r"\baccuracy\s+(issue|problem|difference|mismatch|regression)\b", ["J3"], 3),
    (r"\bsilent(ly)?\s+(wrong|incorrect|bad)\b", ["J3"], 3),
    (r"\bproduces?\s+(wrong|different|incorrect)\b", ["J3"], 3),
    (r"\bnumerical\s+(issue|difference|mismatch|error)\b", ["J3"], 3),
    (r"\bnan\b.*\bcompile\b", ["J3"], 2),
    (r"\bcompile\b.*\bnan\b", ["J3"], 2),
    (r"\bdifferent\s+results?\b", ["J3"], 2),
    (r"\bmismatch\b.*\b(eager|compiled)\b", ["J3"], 2),
    (r"\bcorrectness\b", ["J3"], 2),

    # J4: Graph Breaks
    (r"\bgraph\s*break\b", ["J4"], 4),
    (r"\bfullgraph\b", ["J4"], 3),
    (r"\bfull_?graph\s*=\s*True\b", ["J4"], 3),
    (r"\bunsupported\b.*\b(builtin|op|function|call)\b", ["J4"], 2),
    (r"\bBREAK\b", ["J4"], 1),
    (r"\bgraph\s+fragment\b", ["J4"], 2),

    # J5: Performance Optimization
    (r"\boptimiz(e|ation|ing)\b.*\bperformance\b", ["J5"], 3),
    (r"\bperformance\b.*\boptimiz(e|ation|ing)\b", ["J5"], 3),
    (r"\bfaster\b.*\bcompil(e|ed)\b", ["J5"], 2),
    (r"\bfus(e|ion|ed|ing)\b.*\b(kernel|op|operator)\b", ["J5"], 2),
    (r"\binductor\b.*\b(perf|performance|slow|faster|optimization)\b", ["J5"], 2),
    (r"\bkernel\s*(fusion|performance|optimization)\b", ["J5"], 2),
    (r"\bmax[-_]?autotune\b", ["J5"], 3),
    (r"\bautotuning\b", ["J5"], 2),
    (r"\btriton\s+kernel\b.*\b(slow|perf|fast)\b", ["J5"], 2),
    (r"\bcuda\s+graph\b", ["J5"], 2),

    # J6: Dynamic Shapes
    (r"\bdynamic\s+(shape|batch|size|input|dim)\b", ["J6"], 4),
    (r"\bmark_dynamic\b", ["J6"], 3),
    (r"\bsymbolic\s+(shape|int|size)\b", ["J6"], 3),
    (r"\bdynamic=True\b", ["J6"], 3),
    (r"\bvariable[\s-]*(length|size|shape|batch)\b", ["J6"], 2),
    (r"\bshape\s+(guard|specialization)\b", ["J6"], 2),
    (r"\bunbacked\s+symint\b", ["J6"], 2),

    # J7: Compile-Time Performance
    (r"\brecompil(e|ation|ing)\b", ["J7"], 3),
    (r"\bcompil(e|ation)\s+(time|slow|long|latency)\b", ["J7"], 4),
    (r"\bslow\s+compil(e|ation)\b", ["J7"], 4),
    (r"\bcold\s+start\b", ["J7"], 3),
    (r"\bcompil(e|ation)\s+cach(e|ing)\b", ["J7"], 3),
    (r"\btakes?\s+(too\s+)?long\s+to\s+compile\b", ["J7"], 4),
    (r"\bcompil(e|ation)\s+overhead\b", ["J7"], 3),
    (r"\brecompilation\s+exhaust\b", ["J7"], 3),
    (r"\bcache\s+(hit|miss)\b", ["J7"], 2),
    (r"\bpersistent\s+cach(e|ing)\b", ["J7"], 2),
    (r"\bslow.*first.*call\b", ["J7"], 2),

    # J8: Custom & Higher-Order Ops
    (r"\bcustom\s*(op|operator|kernel)\b", ["J8"], 4),
    (r"\bhigher[\s-]*order\s*(op|operator)\b", ["J8"], 4),
    (r"\bflex[\s_]*attention\b", ["J8"], 3),
    (r"\bassociative[\s_]*scan\b", ["J8"], 3),
    (r"\btorch\.scan\b", ["J8"], 3),
    (r"\bwhile_loop\b", ["J8"], 2),
    (r"\bcond\b.*\b(compile|dynamo|export)\b", ["J8"], 2),
    (r"\b@custom_op\b", ["J8"], 3),
    (r"\btorch\.library\b", ["J8"], 2),
    (r"\btriton\s+kernel\b.*\bcompile\b", ["J8"], 2),
    (r"\buser[\s_]?defined\s+(triton\s+)?kernel\b", ["J8"], 2),
]


@dataclass
class ScoredIssue:
    issue: dict
    journey: str
    score: float = 0.0
    match_reasons: list = field(default_factory=list)

    @property
    def engagement(self) -> int:
        return self.issue.get("comments", 0) + self.issue.get("reactions", 0) * 3


def classify_issue(issue: dict) -> dict[str, ScoredIssue]:
    """Classify a single issue into journeys with confidence scores."""
    labels = set(issue.get("labels", []))
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    # Use first 3000 chars of body for keyword matching (efficiency)
    body_excerpt = body[:3000]
    text = f"{title} {body_excerpt}"

    journey_scores: dict[str, ScoredIssue] = {}

    def add_score(journey: str, points: float, reason: str):
        if journey not in journey_scores:
            journey_scores[journey] = ScoredIssue(issue=issue, journey=journey)
        journey_scores[journey].score += points
        journey_scores[journey].match_reasons.append(reason)

    # Label-based matching (high confidence)
    for label, journeys in LABEL_TO_JOURNEY.items():
        if label in labels:
            for j in journeys:
                add_score(j, 5, f"label: {label}")

    # Keyword-based matching
    for pattern, journeys, weight in KEYWORD_RULES:
        # Check title first (stronger signal), then body
        title_match = re.search(pattern, title, re.IGNORECASE)
        body_match = re.search(pattern, text, re.IGNORECASE) if not title_match else None

        if title_match:
            for j in journeys:
                add_score(j, weight * 1.5, f"title keyword: {pattern}")
        elif body_match:
            for j in journeys:
                add_score(j, weight * 0.8, f"body keyword: {pattern}")

    # Inductor label heuristic: could be J2 or J5
    if "module: inductor" in labels:
        if any(j in journey_scores for j in ["J2", "J5"]):
            pass  # Already classified
        else:
            # Default inductor to J5 with low score
            add_score("J5", 2, "label: module: inductor (default)")

    # Dynamo label heuristic: could be J1 or J4
    if "module: dynamo" in labels:
        if any(j in journey_scores for j in ["J1", "J4"]):
            pass
        else:
            add_score("J4", 2, "label: module: dynamo (default)")

    return journey_scores


def compute_user_quality_score(issue: dict) -> float:
    """Score how likely this is a real user question (vs internal/CI report)."""
    score = 1.0
    title = issue["title"].lower()
    body = (issue.get("body", "") or "").lower()[:2000]

    # Positive signals: looks like a user question
    if "?" in issue["title"]:
        score += 2
    if any(w in title for w in ["how to", "how do", "how can", "is it possible", "why does", "why is"]):
        score += 3
    if "🐛 describe the bug" in body or "describe the bug" in body:
        score += 1.5  # GitHub issue template = real user
    if "steps to reproduce" in body or "minimal repro" in body or "reproducer" in body:
        score += 1
    if "torch.compile" in body or "torch.compile" in title:
        score += 1

    # Negative signals: looks internal
    if title.startswith("["):
        bracket_content = title[1:title.find("]")] if "]" in title else ""
        if any(x in bracket_content.lower() for x in ["rfc", "tracking", "tracker", "meta"]):
            score -= 1
    if "meta" in issue.get("user", "").lower():
        score -= 0.5
    if any(x in title.lower() for x in ["upstream", "rfc", "tracking issue", "tracker"]):
        score -= 1.5
    if issue.get("comments", 0) == 0 and issue.get("reactions", 0) == 0:
        score -= 1

    return max(score, 0)


def extract_user_question(issue: dict, journey: str) -> str:
    """Rewrite the issue as a user question someone would ask a doc/agent."""
    title = issue["title"]
    body = (issue.get("body", "") or "")[:1500]

    # Clean up title: remove common prefixes
    clean_title = re.sub(r"^\[.*?\]\s*", "", title).strip()
    clean_title = re.sub(r"^🐛\s*", "", clean_title).strip()
    clean_title = re.sub(r"^🚀\s*", "", clean_title).strip()

    # Journey-specific question templates
    templates = {
        "J1": "How do I {action} with torch.compile?",
        "J2": "Why is my compiled model {problem}?",
        "J3": "Why does torch.compile produce {problem}?",
        "J4": "How do I fix graph breaks caused by {cause}?",
        "J5": "How can I optimize {what} for better performance with torch.compile?",
        "J6": "How do I handle {problem} with dynamic shapes in torch.compile?",
        "J7": "Why does compilation {problem} and how can I speed it up?",
        "J8": "How do I use {what} with torch.compile?",
    }

    # Try to extract core question from title
    title_lower = clean_title.lower()

    if "?" in clean_title:
        # Already a question -- use as-is
        return clean_title

    # If title already starts with "how to" / "how do" / "why", make it a question
    if re.match(r"^(how\s+(to|do|can)|why\s+(does|is|do))", title_lower):
        return clean_title + "?"

    # Build contextual question based on journey and title content
    if journey == "J1":
        if "not work" in title_lower or "doesn't work" in title_lower or "fail" in title_lower:
            return f"Why doesn't torch.compile work? ({clean_title})"
        if "support" in title_lower:
            return f"Does torch.compile support this? ({clean_title})"
        return f"How do I get torch.compile working? ({clean_title})"

    elif journey == "J2":
        if "slow" in title_lower or "regression" in title_lower:
            return f"Why is torch.compile making my model slower? ({clean_title})"
        return f"Why is torch.compile slower than expected? ({clean_title})"

    elif journey == "J3":
        if "nan" in title_lower:
            return f"Why does torch.compile produce NaN values? ({clean_title})"
        if "wrong" in title_lower or "incorrect" in title_lower:
            return f"Why does torch.compile give wrong results? ({clean_title})"
        return f"Why does torch.compile produce different/incorrect results? ({clean_title})"

    elif journey == "J4":
        return f"How do I resolve this graph break? ({clean_title})"

    elif journey == "J5":
        return f"How can I optimize torch.compile performance? ({clean_title})"

    elif journey == "J6":
        return f"How do I handle dynamic shapes in torch.compile? ({clean_title})"

    elif journey == "J7":
        if "recompil" in title_lower:
            return f"Why does my model keep recompiling? ({clean_title})"
        if "cache" in title_lower:
            return f"How do I use compile caching? ({clean_title})"
        return f"Why is compilation so slow? ({clean_title})"

    elif journey == "J8":
        if "flex" in title_lower and "attention" in title_lower:
            return f"How do I use flex_attention with torch.compile? ({clean_title})"
        if "custom" in title_lower and "op" in title_lower:
            return f"How do I make my custom op work with torch.compile? ({clean_title})"
        return f"How do I use custom/higher-order ops with torch.compile? ({clean_title})"

    return clean_title


def select_best_issues(
    candidates: list[ScoredIssue], n: int = 5
) -> list[ScoredIssue]:
    """Select the N best representative issues from candidates."""
    # Compute composite score:
    # - classification confidence (how well it matches the journey)
    # - user quality (is it a real user question?)
    # - engagement (comments + reactions)

    for c in candidates:
        user_quality = compute_user_quality_score(c.issue)
        engagement = c.engagement
        # Composite: classification confidence + user quality + log(engagement)
        import math
        c.score = (
            c.score * 1.0            # classification confidence
            + user_quality * 2.0     # user quality bonus
            + math.log1p(engagement) * 1.5  # engagement (logarithmic)
        )

    # Sort by composite score
    candidates.sort(key=lambda x: x.score, reverse=True)

    # Deduplicate: avoid issues that are too similar
    selected = []
    seen_titles = set()
    for c in candidates:
        # Skip near-duplicate titles
        title_key = re.sub(r"\W+", " ", c.issue["title"].lower()).strip()
        if any(similar(title_key, t) for t in seen_titles):
            continue
        seen_titles.add(title_key)
        selected.append(c)
        if len(selected) >= n:
            break

    return selected


def similar(a: str, b: str) -> bool:
    """Quick similarity check between two strings."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return False
    overlap = len(words_a & words_b)
    return overlap / min(len(words_a), len(words_b)) > 0.7


def explain_representativeness(scored: ScoredIssue) -> str:
    """Generate explanation for why this issue is representative."""
    issue = scored.issue
    parts = []

    # Match reasons
    reasons = scored.match_reasons[:4]
    if reasons:
        parts.append(f"Matched via: {'; '.join(reasons)}")

    # Engagement
    comments = issue.get("comments", 0)
    reactions = issue.get("reactions", 0)
    if comments > 5 or reactions > 2:
        parts.append(f"High engagement ({comments} comments, {reactions} reactions)")

    # User quality indicators
    body = (issue.get("body", "") or "").lower()[:2000]
    if "?" in issue["title"]:
        parts.append("Phrased as a direct user question")
    if "describe the bug" in body:
        parts.append("User-filed bug report with structured template")
    if "torch.compile" in issue["title"].lower() or "torch.compile" in body[:500]:
        parts.append("Directly about torch.compile usage")

    # Labels
    labels = issue.get("labels", [])
    relevant = [l for l in labels if l not in ("oncall: pt2", "triaged", "skipped")]
    if relevant:
        parts.append(f"Labels: {', '.join(relevant[:4])}")

    return " | ".join(parts) if parts else "General match"


def main():
    print(f"Loading issues from {INPUT_FILE}...")
    with open(INPUT_FILE) as f:
        data = json.load(f)
    print(f"Loaded {len(data)} issues")

    # Step 1: Filter out internal/CI issues
    user_issues = [i for i in data if not is_internal_issue(i)]
    print(f"After filtering internal/CI issues: {len(user_issues)} remaining")

    # Step 2: Classify each issue into journeys
    journey_candidates: dict[str, list[ScoredIssue]] = defaultdict(list)

    for issue in user_issues:
        classifications = classify_issue(issue)
        for journey_id, scored in classifications.items():
            journey_candidates[journey_id].append(scored)

    print("\nJourney candidate counts:")
    for j_id in sorted(JOURNEYS.keys()):
        count = len(journey_candidates[j_id])
        print(f"  {j_id}: {count} candidates")

    # Step 3: Select best 5 per journey
    results: dict[str, list[ScoredIssue]] = {}
    for j_id in sorted(JOURNEYS.keys()):
        candidates = journey_candidates[j_id]
        if not candidates:
            print(f"  WARNING: No candidates for {j_id}")
            results[j_id] = []
            continue
        results[j_id] = select_best_issues(candidates, n=5)

    # Step 4: Generate report
    report_lines = []
    report_lines.append("# User Journey Issue Analysis")
    report_lines.append("")
    report_lines.append("Extracted from `pt2_all_issues.json` (9,277 PyTorch PT2 GitHub issues).")
    report_lines.append(f"Filtered to {len(user_issues)} user-facing issues (excluded CI/infra/test issues).")
    report_lines.append("")
    report_lines.append("Each journey shows the 5 most representative real-user issues, selected by:")
    report_lines.append("- Label and keyword classification confidence")
    report_lines.append("- User-facing quality (real questions vs internal reports)")
    report_lines.append("- Community engagement (comments + reactions)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    for j_id in sorted(JOURNEYS.keys()):
        journey = JOURNEYS[j_id]
        selected = results[j_id]

        report_lines.append(f"## {j_id}: {journey['name']}")
        report_lines.append("")
        report_lines.append(f"*{journey['description']}*")
        report_lines.append("")
        report_lines.append(f"**Candidate pool:** {len(journey_candidates[j_id])} issues")
        report_lines.append("")

        if not selected:
            report_lines.append("*No qualifying issues found.*")
            report_lines.append("")
            continue

        for i, scored in enumerate(selected, 1):
            issue = scored.issue
            user_question = extract_user_question(issue, j_id)
            explanation = explain_representativeness(scored)

            report_lines.append(f"### {i}. #{issue['number']}: {issue['title']}")
            report_lines.append("")
            report_lines.append(f"- **URL:** {issue['html_url']}")
            report_lines.append(f"- **Comments:** {issue.get('comments', 0)} | **Reactions:** {issue.get('reactions', 0)}")
            report_lines.append(f"- **State:** {issue['state']} | **Created:** {issue['created_at'][:10]}")
            report_lines.append(f"- **Labels:** {', '.join(issue.get('labels', [])[:6])}")
            report_lines.append(f"- **User Question:** \"{user_question}\"")
            report_lines.append(f"- **Why Representative:** {explanation}")
            report_lines.append("")

        report_lines.append("---")
        report_lines.append("")

    # Summary statistics
    report_lines.append("## Summary Statistics")
    report_lines.append("")
    report_lines.append("| Journey | Candidate Pool | Selected |")
    report_lines.append("|---------|---------------|----------|")
    for j_id in sorted(JOURNEYS.keys()):
        pool = len(journey_candidates[j_id])
        selected = len(results[j_id])
        report_lines.append(f"| {j_id}: {JOURNEYS[j_id]['name']} | {pool} | {selected} |")
    report_lines.append("")

    total_classified = sum(len(v) for v in journey_candidates.values())
    report_lines.append(f"**Total classifications:** {total_classified} (issues can appear in multiple journeys)")
    report_lines.append("")

    report = "\n".join(report_lines)

    with open(OUTPUT_FILE, "w") as f:
        f.write(report)

    print(f"\nReport written to {OUTPUT_FILE}")
    print(f"\n{'='*80}")
    print(report)


if __name__ == "__main__":
    main()
