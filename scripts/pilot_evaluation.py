#!/usr/bin/env python3
"""
Pilot Evaluation Runner for torch.compile Documentation Quality

Simulates the Find→Understand→Apply evaluation funnel:
1. FIND: Can the user locate relevant documentation for their question?
2. UNDERSTAND: Does the doc content address the question?
3. APPLY: Does the doc provide actionable steps to resolve the issue?

Scores each test case using HACS (Human Attention Cost Score):
  L0 = Autonomous (doc directly answers, no human needed)
  L1 = Trivial (doc points to answer, minimal effort)
  L2 = Moderate (doc exists but requires significant interpretation)
  L3 = High (doc is missing/misleading, user must do deep research)
  L4 = Negative (doc gives wrong guidance, worse than no doc)

This script processes the pilot test suite and outputs evaluation results.
"""

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# PyTorch torch.compile documentation pages (from Sphinx sitemap)
# Manually curated list of the 35 known pages
TORCH_COMPILE_DOCS = {
    "torch.compiler": {
        "url": "https://pytorch.org/docs/stable/torch.compiler.html",
        "topics": ["torch.compile", "API reference", "modes", "backends", "options"],
    },
    "torch.compiler_get_started": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_get_started.html",
        "topics": ["getting started", "first compile", "basic usage", "tutorial"],
    },
    "torch.compiler_api": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_api.html",
        "topics": ["API reference", "torch.compile", "fullgraph", "dynamic", "backend"],
    },
    "torch.compiler_faq": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_faq.html",
        "topics": ["FAQ", "common questions", "troubleshooting"],
    },
    "torch.compiler_troubleshooting": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_troubleshooting.html",
        "topics": ["troubleshooting", "debugging", "errors", "graph breaks"],
    },
    "torch.compiler_transformations": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_transformations.html",
        "topics": ["transformations", "passes", "optimization"],
    },
    "torch.compiler_inductor_profiling": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_inductor_profiling.html",
        "topics": ["profiling", "inductor", "performance", "tracing"],
    },
    "torch.compiler_best_practices": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_best_practices.html",
        "topics": ["best practices", "performance", "optimization", "tips"],
    },
    "torch.compiler_dynamic_shapes": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_dynamic_shapes.html",
        "topics": ["dynamic shapes", "symbolic shapes", "guards", "recompilation", "mark_dynamic"],
    },
    "torch.compiler_custom_backends": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_custom_backends.html",
        "topics": ["custom backends", "backend registration", "compiler"],
    },
    "torch.compiler_cudagraph_trees": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_cudagraph_trees.html",
        "topics": ["CUDA graphs", "cudagraph trees", "reduce-overhead", "memory"],
    },
    "torch.compiler_fake_tensor": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_fake_tensor.html",
        "topics": ["fake tensor", "meta tensor", "shape inference"],
    },
    "torch.compiler_fine_grain_apis": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_fine_grain_apis.html",
        "topics": ["fine-grained APIs", "compilation control", "selective compile"],
    },
    "torch.compiler_graph_breaks": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_graph_breaks.html",
        "topics": ["graph breaks", "fullgraph", "unsupported", "dynamo"],
    },
    "torch.compiler_guards_overview": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_guards_overview.html",
        "topics": ["guards", "recompilation", "specialization", "dynamic shapes"],
    },
    "torch._dynamo": {
        "url": "https://pytorch.org/docs/stable/torch._dynamo.html",
        "topics": ["dynamo", "graph capture", "bytecode"],
    },
    "torch.compiler_aot_inductor": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_aot_inductor.html",
        "topics": ["AOT inductor", "ahead-of-time", "deployment", "export"],
    },
    "custom_ops": {
        "url": "https://pytorch.org/docs/stable/torch.library.html",
        "topics": ["custom ops", "torch.library", "operator registration"],
    },
    "higher_order_ops": {
        "url": "https://pytorch.org/docs/stable/higher_order_ops.html",
        "topics": ["higher-order ops", "flex_attention", "while_loop", "scan", "control flow"],
    },
    "compile_caching": {
        "url": "https://pytorch.org/docs/stable/torch.compiler_caching.html",
        "topics": ["compile cache", "persistent cache", "cold start", "TORCHINDUCTOR_FX_GRAPH_CACHE"],
    },
}


@dataclass
class FindResult:
    """Result of the FIND stage: can the user locate relevant docs?"""
    relevant_pages: list  # pages that might answer the question
    best_match: Optional[str]  # best matching page
    topic_coverage: float  # 0-1, how well docs cover the expected topics
    finding: str  # human-readable finding


@dataclass
class UnderstandResult:
    """Result of the UNDERSTAND stage: does the doc address the question?"""
    addresses_question: bool
    has_examples: bool
    has_actionable_steps: bool
    gaps: list  # what's missing
    finding: str


@dataclass
class ApplyResult:
    """Result of the APPLY stage: can the user resolve their issue?"""
    resolvable: bool
    steps_clear: bool
    additional_research_needed: str  # what else user needs to find
    finding: str


@dataclass
class EvalResult:
    """Complete evaluation of a single test case."""
    id: str
    journey: str
    question: str
    source_issue: int
    hacs_score: int  # 0-4
    hacs_label: str
    find: dict
    understand: dict
    apply: dict
    rationale: str


def find_relevant_docs(test_case: dict) -> FindResult:
    """
    Stage 1: FIND — Match user question against available documentation.

    Simulates a user searching for docs by matching expected topics
    against the known doc page topics.
    """
    expected_topics = test_case.get("expected_doc_topics", [])
    question = test_case["user_question"].lower()

    matches = []
    for page_id, page in TORCH_COMPILE_DOCS.items():
        page_topics = [t.lower() for t in page["topics"]]
        score = 0
        matched_topics = []

        # Check expected topic overlap
        for expected in expected_topics:
            expected_lower = expected.lower()
            for pt in page_topics:
                if expected_lower in pt or pt in expected_lower:
                    score += 2
                    matched_topics.append(expected)
                    break

        # Check question keyword overlap
        for pt in page_topics:
            if pt in question:
                score += 1

        if score > 0:
            matches.append((page_id, score, matched_topics))

    matches.sort(key=lambda x: -x[1])

    # Calculate topic coverage
    covered = set()
    for _, _, topics in matches:
        covered.update(topics)
    coverage = len(covered) / len(expected_topics) if expected_topics else 0

    relevant = [{"page": m[0], "score": m[1], "url": TORCH_COMPILE_DOCS[m[0]]["url"]}
                for m in matches[:5]]
    best = matches[0][0] if matches else None

    if not matches:
        finding = "NO relevant documentation pages found for this question"
    elif coverage < 0.5:
        finding = f"Partial coverage: {len(relevant)} pages found but only {coverage:.0%} of expected topics covered"
    else:
        finding = f"Good findability: {len(relevant)} relevant pages, {coverage:.0%} topic coverage"

    return FindResult(
        relevant_pages=relevant,
        best_match=best,
        topic_coverage=coverage,
        finding=finding,
    )


def evaluate_understanding(test_case: dict, find_result: FindResult) -> UnderstandResult:
    """
    Stage 2: UNDERSTAND — Assess whether found docs address the question.

    This is a heuristic evaluation based on topic coverage and doc structure.
    In a full evaluation, this would involve actually reading the doc content.
    """
    expected_topics = test_case.get("expected_doc_topics", [])
    difficulty = test_case.get("difficulty", "intermediate")

    # Heuristic: pages exist but do they cover the right topics?
    has_match = find_result.best_match is not None
    good_coverage = find_result.topic_coverage >= 0.7

    # Known documentation gaps based on Otter's analysis
    known_gaps = {
        "compile cache": "Compile caching docs exist but are thin on cold-start optimization",
        "custom ops": "Custom ops docs have lowest issue close rate (43%), unclear guidance",
        "dynamic shapes": "Dynamic shapes docs exist but don't explain guard mechanics well",
        "recompilation": "Recompilation docs lack diagnostic workflow",
        "profiling": "Profiling docs exist but don't show end-to-end diagnosis flow",
        "accuracy debugging": "Accuracy debugging workflow poorly documented",
        "minifier": "Minifier tool exists but tutorial is hard to find",
        "DDP": "DDP + compile integration guide is missing",
        "while_loop": "Higher-order ops docs are sparse on stateful modules",
        "flex_attention": "flex_attention has 132 issues but limited troubleshooting docs",
        "CUDA graphs": "CUDA graphs integration guide is missing (P3 priority)",
        "mode combinations": "No doc explains interaction between max-autotune and reduce-overhead",
        "backward pass": "Backward pass behavior under compile poorly documented",
        "regression": "No version-specific migration/changelog guide",
    }

    gaps = []
    for topic in expected_topics:
        for gap_key, gap_desc in known_gaps.items():
            if gap_key.lower() in topic.lower():
                gaps.append(gap_desc)

    # Remove duplicates
    gaps = list(set(gaps))

    # Determine if question is addressed
    addresses = has_match and good_coverage and len(gaps) < len(expected_topics)

    # Heuristic for examples and actionable steps
    has_examples = has_match and difficulty in ("beginner", "intermediate")
    has_steps = has_match and good_coverage and len(gaps) == 0

    if not has_match:
        finding = "No relevant documentation found — user would need to search GitHub/forums"
    elif not good_coverage:
        finding = f"Documentation exists but has gaps: {'; '.join(gaps[:3])}"
    elif gaps:
        finding = f"Partial understanding possible but gaps remain: {'; '.join(gaps[:3])}"
    else:
        finding = "Documentation adequately addresses this question"

    return UnderstandResult(
        addresses_question=addresses,
        has_examples=has_examples,
        has_actionable_steps=has_steps,
        gaps=gaps,
        finding=finding,
    )


def evaluate_applicability(test_case: dict, find_result: FindResult,
                           understand_result: UnderstandResult) -> ApplyResult:
    """
    Stage 3: APPLY — Can the user resolve their issue from the docs?
    """
    difficulty = test_case.get("difficulty", "intermediate")

    if not understand_result.addresses_question:
        return ApplyResult(
            resolvable=False,
            steps_clear=False,
            additional_research_needed="User must search GitHub issues, forums, or read source code",
            finding="Cannot resolve from documentation alone",
        )

    if understand_result.gaps:
        additional = f"Gaps in: {', '.join(understand_result.gaps[:2])}"
        return ApplyResult(
            resolvable=difficulty == "beginner",
            steps_clear=False,
            additional_research_needed=additional,
            finding=f"Partially resolvable — {additional}",
        )

    return ApplyResult(
        resolvable=True,
        steps_clear=understand_result.has_actionable_steps,
        additional_research_needed="None" if understand_result.has_actionable_steps else "Minor clarification needed",
        finding="Resolvable from documentation",
    )


def score_hacs(find: FindResult, understand: UnderstandResult, apply: ApplyResult) -> tuple:
    """
    Score using HACS (Human Attention Cost Score).

    L0 = Autonomous: Doc directly answers, user can self-serve
    L1 = Trivial: Doc points to answer, minimal human effort
    L2 = Moderate: Doc exists but requires significant interpretation
    L3 = High: Doc missing/inadequate, user must do deep research
    L4 = Negative: Doc gives wrong guidance (not scored in pilot)
    """
    if apply.resolvable and apply.steps_clear:
        return 0, "L0: Autonomous — documentation directly answers the question"
    elif apply.resolvable and not apply.steps_clear:
        return 1, "L1: Trivial — documentation points to answer but needs minor interpretation"
    elif find.best_match and not apply.resolvable:
        return 2, "L2: Moderate — relevant docs exist but don't fully address this use case"
    elif not find.best_match:
        return 3, "L3: High — no relevant documentation; user must search GitHub/forums/source"
    else:
        return 2, "L2: Moderate — documentation has gaps that require additional research"


def run_evaluation(test_suite_path: str, output_path: str):
    """Run the full pilot evaluation."""
    with open(test_suite_path) as f:
        test_cases = json.load(f)

    results = []
    journey_scores = {}

    for tc in test_cases:
        # Run 3-stage evaluation
        find = find_relevant_docs(tc)
        understand = evaluate_understanding(tc, find)
        apply = evaluate_applicability(tc, find, understand)
        hacs_score, hacs_label = score_hacs(find, understand, apply)

        result = EvalResult(
            id=tc["id"],
            journey=tc["journey"],
            question=tc["user_question"],
            source_issue=tc["source_issue"],
            hacs_score=hacs_score,
            hacs_label=hacs_label,
            find=asdict(find),
            understand=asdict(understand),
            apply=asdict(apply),
            rationale=f"FIND: {find.finding} | UNDERSTAND: {understand.finding} | APPLY: {apply.finding}",
        )
        results.append(result)

        # Track by journey
        journey = tc["journey"]
        if journey not in journey_scores:
            journey_scores[journey] = []
        journey_scores[journey].append(hacs_score)

    # Generate report
    report = generate_report(results, journey_scores)

    with open(output_path, "w") as f:
        f.write(report)

    # Also save raw results as JSON
    json_path = output_path.replace(".md", ".json")
    with open(json_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"Report: {output_path}")
    print(f"Raw data: {json_path}")
    print(f"\n{report}")


def generate_report(results: list, journey_scores: dict) -> str:
    """Generate the pilot evaluation report."""
    lines = []
    lines.append("# Pilot Evaluation Report: torch.compile Documentation Quality")
    lines.append(f"\n**Date:** 2026-04-11")
    lines.append(f"**Test cases:** {len(results)} (3 per journey, 8 journeys)")
    lines.append(f"**Method:** Find→Understand→Apply funnel with HACS scoring")
    lines.append(f"**Data source:** Real GitHub issues from pytorch/pytorch (oncall:pt2)")

    # Overall summary
    all_scores = [r.hacs_score for r in results]
    avg = sum(all_scores) / len(all_scores)
    dist = {i: all_scores.count(i) for i in range(5)}

    lines.append("\n---\n")
    lines.append("## Overall Results")
    lines.append(f"\n**Average HACS Score: {avg:.1f}** (0=best, 4=worst)")
    lines.append(f"\n| Score | Label | Count | % |")
    lines.append(f"|-------|-------|-------|---|")
    for i in range(5):
        labels = ["L0: Autonomous", "L1: Trivial", "L2: Moderate", "L3: High", "L4: Negative"]
        pct = dist.get(i, 0) / len(all_scores) * 100
        lines.append(f"| {i} | {labels[i]} | {dist.get(i, 0)} | {pct:.0f}% |")

    # Per-journey breakdown
    lines.append("\n---\n")
    lines.append("## Per-Journey Scores")
    lines.append(f"\n| Journey | Avg HACS | Scores | Assessment |")
    lines.append(f"|---------|----------|--------|------------|")

    for journey in sorted(journey_scores.keys()):
        scores = journey_scores[journey]
        j_avg = sum(scores) / len(scores)
        score_str = ", ".join(f"L{s}" for s in scores)
        if j_avg <= 1:
            assessment = "Well documented"
        elif j_avg <= 2:
            assessment = "Gaps exist"
        else:
            assessment = "Poorly documented"
        lines.append(f"| {journey} | {j_avg:.1f} | {score_str} | {assessment} |")

    # Detailed results
    lines.append("\n---\n")
    lines.append("## Detailed Results")

    current_journey = None
    for r in results:
        if r.journey != current_journey:
            current_journey = r.journey
            lines.append(f"\n### {r.journey}\n")

        lines.append(f"**{r.id}:** {r.question}")
        lines.append(f"- Source: pytorch/pytorch#{r.source_issue}")
        lines.append(f"- **HACS: {r.hacs_label}**")
        lines.append(f"- FIND: {r.find['finding']}")
        lines.append(f"- UNDERSTAND: {r.understand['finding']}")
        lines.append(f"- APPLY: {r.apply['finding']}")
        if r.understand.get('gaps'):
            lines.append(f"- Gaps: {'; '.join(r.understand['gaps'][:3])}")
        lines.append("")

    # Key findings
    lines.append("---\n")
    lines.append("## Key Findings")
    lines.append("")

    # Find the worst journeys
    worst = sorted(journey_scores.items(), key=lambda x: -sum(x[1])/len(x[1]))
    best = sorted(journey_scores.items(), key=lambda x: sum(x[1])/len(x[1]))

    lines.append("### Worst Documentation Coverage (highest HACS)")
    for journey, scores in worst[:3]:
        j_avg = sum(scores) / len(scores)
        lines.append(f"1. **{journey}** (avg {j_avg:.1f}) — users in this journey face the most friction")

    lines.append("\n### Best Documentation Coverage (lowest HACS)")
    for journey, scores in best[:3]:
        j_avg = sum(scores) / len(scores)
        lines.append(f"1. **{journey}** (avg {j_avg:.1f}) — documentation mostly serves these users")

    # Recommendations
    lines.append("\n### Recommendations for Prototype Phase 2")
    lines.append("")
    lines.append("1. **Validate with live doc reads** — This pilot used topic-matching heuristics. Phase 2 should actually fetch and read the doc pages to verify content quality.")
    lines.append("2. **Add agent-in-the-loop scoring** — Have an LLM attempt to answer each question using only the docs, then compare to the known resolution from the GitHub issue.")
    lines.append("3. **Expand test suite** — Move from 3 to 10 cases per journey, with difficulty stratification (beginner/intermediate/advanced).")
    lines.append("4. **A/B with improved docs** — For the highest-HACS journeys, draft improved documentation and re-run evaluation to measure HACS delta.")
    lines.append("")
    lines.append("---")
    lines.append(f"\n*Generated from {len(results)} test cases derived from real pytorch/pytorch GitHub issues.*")

    return "\n".join(lines)


if __name__ == "__main__":
    base = Path(__file__).parent
    test_suite = base / "pilot_test_suite.json"
    output = base / "pilot_evaluation_report.md"
    run_evaluation(str(test_suite), str(output))
