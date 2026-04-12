#!/usr/bin/env python3
"""
Mode B Evaluation: Full-Context Resolution Quality

For each case in the test suite:
1. Construct agent prompt with user question + issue context
2. Agent searches web and produces guidance
3. Score guidance quality (0-3)

Usage:
    python run_mode_b.py --suite ../suite/cases.json --output-dir ../runs/YYYY-MM-DD-baseline/
    python run_mode_b.py --suite ../suite/cases.json --output-dir ../runs/YYYY-MM-DD-baseline/ --cases J1-1,J1-2
"""

import argparse
import json
import os
from datetime import datetime


AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant specializing in PyTorch torch.compile.
A user is asking for help with a torch.compile problem. Search the web for relevant
PyTorch documentation and provide actionable guidance.

Be specific and accurate. If you're unsure about something, say so rather than guessing.
If the issue appears to be a known bug or limitation, identify it as such and suggest
workarounds if they exist."""


def build_agent_prompt(case: dict) -> str:
    """Build the prompt an agent would receive for this case."""
    parts = [
        f"User question: {case['user_question']}",
        "",
        f"Context from their GitHub issue:",
        case.get("issue_context", "(no additional context)"),
    ]
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Run Mode B evaluation")
    parser.add_argument("--suite", required=True, help="Path to test suite JSON")
    parser.add_argument("--output-dir", required=True, help="Output directory for this run")
    parser.add_argument("--cases", help="Comma-separated case IDs to evaluate (default: all)")
    args = parser.parse_args()

    with open(args.suite) as f:
        cases = json.load(f)

    if args.cases:
        case_ids = set(args.cases.split(","))
        cases = [c for c in cases if c["id"] in case_ids]

    print(f"Mode B evaluation: {len(cases)} cases")
    print(f"Output: {args.output_dir}")
    print(f"Agent system prompt: {len(AGENT_SYSTEM_PROMPT)} chars")

    scores_path = os.path.join(args.output_dir, "mode_b_scores.json")

    results = {
        "metadata": {
            "evaluator": "agent",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "search_tool": "three_pai_external_web_search",
            "rubric_version": "Mode B v1.0",
        },
        "results": [],
    }

    for case in cases:
        print(f"\n--- {case['id']} ({case['resolution_status']}) ---")
        prompt = build_agent_prompt(case)
        print(f"Prompt: {prompt[:200]}...")

        # In automated mode, call the agent here:
        # response = call_agent(AGENT_SYSTEM_PROMPT, prompt)
        # Then score the response (LLM-as-judge or manual)

        results["results"].append({
            "id": case["id"],
            "resolution_status": case["resolution_status"],
            "agent_prompt": prompt,
            "agent_guidance": "",  # Fill after agent run
            "score": None,  # Fill after scoring
            "justification": "",
        })

    os.makedirs(args.output_dir, exist_ok=True)
    with open(scores_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved template to {scores_path}")


if __name__ == "__main__":
    main()
