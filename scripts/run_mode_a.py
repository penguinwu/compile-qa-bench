#!/usr/bin/env python3
"""
Mode A Evaluation: Coverage & Discoverability Scoring

For each case in the test suite:
1. Run a canonical web search (pinned query)
2. Save search result URLs as artifacts
3. Score Coverage (Full/Partial/None) and Discoverability (0-3)

Search artifacts are saved so both annotators score from the same URL set,
eliminating search tool variation as a confound.

Usage:
    python run_mode_a.py --suite ../suite/cases.json --output-dir ../runs/YYYY-MM-DD-baseline/
    python run_mode_a.py --suite ../suite/cases.json --output-dir ../runs/YYYY-MM-DD-baseline/ --cases J1-1,J1-2
    python run_mode_a.py --search-only  # Only run searches, don't score
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


def search_web(query: str) -> list[dict]:
    """Run a web search via Three Pai and return results."""
    # This calls the MCP tool via CLI - adapt to your environment
    # For now, returns empty list as placeholder
    # In practice, use the Three Pai external web search tool
    print(f"  Searching: {query}")
    return []


def build_search_query(case: dict) -> str:
    """Build a canonical search query from a test case."""
    # Use the user question directly, prefixed with pytorch context
    question = case["user_question"]
    # Add pytorch.org focus for discoverability
    return f"pytorch torch.compile {question}"


def load_existing_artifacts(output_dir: str) -> dict:
    """Load any existing search artifacts to support incremental runs."""
    artifacts_dir = os.path.join(output_dir, "search_artifacts")
    artifacts = {}
    if os.path.exists(artifacts_dir):
        for f in os.listdir(artifacts_dir):
            if f.endswith(".json"):
                case_id = f.replace(".json", "")
                with open(os.path.join(artifacts_dir, f)) as fh:
                    artifacts[case_id] = json.load(fh)
    return artifacts


def save_search_artifact(output_dir: str, case_id: str, artifact: dict):
    """Save search results for a single case."""
    artifacts_dir = os.path.join(output_dir, "search_artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    path = os.path.join(artifacts_dir, f"{case_id}.json")
    with open(path, "w") as f:
        json.dump(artifact, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Run Mode A evaluation")
    parser.add_argument("--suite", required=True, help="Path to test suite JSON")
    parser.add_argument("--output-dir", required=True, help="Output directory for this run")
    parser.add_argument("--cases", help="Comma-separated case IDs to evaluate (default: all)")
    parser.add_argument("--search-only", action="store_true", help="Only run searches, don't score")
    args = parser.parse_args()

    # Load test suite
    with open(args.suite) as f:
        cases = json.load(f)

    # Filter cases if specified
    if args.cases:
        case_ids = set(args.cases.split(","))
        cases = [c for c in cases if c["id"] in case_ids]
        print(f"Evaluating {len(cases)} specified cases")
    else:
        print(f"Evaluating all {len(cases)} cases")

    # Load existing artifacts for incremental runs
    existing = load_existing_artifacts(args.output_dir)
    print(f"Found {len(existing)} existing search artifacts")

    # Run searches
    for case in cases:
        case_id = case["id"]
        if case_id in existing:
            print(f"[{case_id}] Skipping search (artifact exists)")
            continue

        query = build_search_query(case)
        results = search_web(query)

        artifact = {
            "case_id": case_id,
            "search_query": query,
            "search_tool": "three_pai_external_web_search",
            "search_timestamp": datetime.utcnow().isoformat(),
            "results": results,
        }
        save_search_artifact(args.output_dir, case_id, artifact)
        print(f"[{case_id}] Saved {len(results)} search results")

    if args.search_only:
        print("\nSearch-only mode complete. Run again without --search-only to score.")
        return

    # Scoring phase - load all artifacts and score
    print("\n=== SCORING ===")
    print("Score each case using the search artifacts (not your own searches).")
    print("Coverage: Full / Partial / None")
    print("Discoverability: 0-3")
    print("See protocol/annotation_guide.md for rubric details.\n")

    scores_path = os.path.join(args.output_dir, "mode_a_scores.json")
    scores = []
    if os.path.exists(scores_path):
        with open(scores_path) as f:
            scores = json.load(f)
        print(f"Loaded {len(scores)} existing scores")

    scored_ids = {s["id"] for s in scores}
    for case in cases:
        if case["id"] in scored_ids:
            continue
        print(f"\n--- {case['id']} ({case['journey']}) ---")
        print(f"Question: {case['user_question']}")
        print(f"Status: {case['resolution_status']}")
        # In automated mode, an LLM scorer would be called here
        # For manual scoring, print and wait for input

    print(f"\nTotal scored: {len(scores)}/{len(cases)}")
    if scores:
        with open(scores_path, "w") as f:
            json.dump(scores, f, indent=2)
        print(f"Saved to {scores_path}")


if __name__ == "__main__":
    main()
