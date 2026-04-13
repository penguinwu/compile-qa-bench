#!/usr/bin/env python3
"""
Automated fabrication detector for Mode B agent guidance.

Extracts claimed config flags, env vars, and API methods from agent guidance,
then verifies each against the PyTorch source code.

Usage:
    python verify_claims.py --results ../runs/2026-04-12-baseline/mode_b_results.json \
                            --torch-dir /home/pengwu/fbsource/fbcode/caffe2/torch
"""

import argparse
import json
import os
import re
import subprocess
from collections import Counter


# Patterns to extract claims from agent guidance
CLAIM_PATTERNS = [
    # Config flags: torch._inductor.config.X, torch._dynamo.config.X
    (r'torch\._inductor\.config\.(\w+)', 'inductor_config'),
    (r'torch\._dynamo\.config\.(\w+)', 'dynamo_config'),
    (r'config\.(\w+)\s*=', 'config_assignment'),
    # Env vars: TORCHINDUCTOR_X, TORCHDYNAMO_X, TORCH_X
    (r'(TORCHINDUCTOR_\w+)', 'env_var'),
    (r'(TORCHDYNAMO_\w+)', 'env_var'),
    (r'(TORCH_COMPILE_\w+)', 'env_var'),
    # API methods: torch.compiler.X, torch._dynamo.X
    (r'torch\.compiler\.(\w+)', 'compiler_api'),
    (r'torch\._higher_order_ops\.(\w+)', 'higher_order_ops'),
]

# Known valid references (not worth checking — too generic)
SKIP_CLAIMS = {
    'inductor_config': {'True', 'False', 'None', 'default'},
    'dynamo_config': {'True', 'False', 'None', 'default'},
    'config_assignment': {'True', 'False', 'None'},
    'env_var': set(),
    'compiler_api': set(),
    'higher_order_ops': set(),
}


def extract_claims(guidance: str) -> list[dict]:
    """Extract verifiable claims from agent guidance text."""
    claims = []
    for pattern, claim_type in CLAIM_PATTERNS:
        for match in re.finditer(pattern, guidance):
            value = match.group(1) if match.lastindex else match.group(0)
            if value not in SKIP_CLAIMS.get(claim_type, set()):
                claims.append({
                    'claim': match.group(0),
                    'value': value,
                    'type': claim_type,
                    'context': guidance[max(0, match.start()-30):match.end()+30],
                })
    return claims


def verify_claim(claim: dict, torch_dir: str) -> dict:
    """Verify a single claim against PyTorch source."""
    value = claim['value']
    claim_type = claim['type']

    if claim_type == 'inductor_config':
        search_file = os.path.join(torch_dir, '_inductor/config.py')
        result = subprocess.run(
            ['grep', '-n', value, search_file],
            capture_output=True, text=True
        )
        found = result.returncode == 0

    elif claim_type == 'dynamo_config':
        search_file = os.path.join(torch_dir, '_dynamo/config.py')
        result = subprocess.run(
            ['grep', '-n', value, search_file],
            capture_output=True, text=True
        )
        found = result.returncode == 0

    elif claim_type == 'env_var':
        result = subprocess.run(
            ['grep', '-rn', value, torch_dir],
            capture_output=True, text=True
        )
        found = result.returncode == 0

    elif claim_type == 'higher_order_ops':
        search_dir = os.path.join(torch_dir, '_higher_order_ops')
        result = subprocess.run(
            ['grep', '-rn', value, search_dir],
            capture_output=True, text=True
        )
        found = result.returncode == 0

    else:
        result = subprocess.run(
            ['grep', '-rn', value, torch_dir, '--include=*.py'],
            capture_output=True, text=True, timeout=10
        )
        found = result.returncode == 0

    return {
        **claim,
        'verified': found,
        'grep_output': result.stdout[:200] if found else '',
    }


def main():
    parser = argparse.ArgumentParser(description='Verify claims in Mode B guidance')
    parser.add_argument('--results', required=True, help='Mode B results JSON')
    parser.add_argument('--torch-dir', required=True, help='PyTorch source directory')
    parser.add_argument('--output', help='Output JSON path')
    args = parser.parse_args()

    with open(args.results) as f:
        data = json.load(f)

    results = data.get('results', data) if isinstance(data, dict) else data

    all_verifications = []
    fabrication_summary = Counter()

    for r in results:
        case_id = r['id']
        guidance = r.get('agent_guidance', '')
        claims = extract_claims(guidance)

        case_result = {
            'id': case_id,
            'total_claims': len(claims),
            'verified': 0,
            'fabricated': 0,
            'claims': [],
        }

        for claim in claims:
            verified = verify_claim(claim, args.torch_dir)
            case_result['claims'].append(verified)
            if verified['verified']:
                case_result['verified'] += 1
            else:
                case_result['fabricated'] += 1
                fabrication_summary[case_id] += 1

        all_verifications.append(case_result)

    # Summary
    total_claims = sum(v['total_claims'] for v in all_verifications)
    total_verified = sum(v['verified'] for v in all_verifications)
    total_fabricated = sum(v['fabricated'] for v in all_verifications)
    cases_with_fab = sum(1 for v in all_verifications if v['fabricated'] > 0)

    print(f"{'='*60}")
    print(f"AUTOMATED FABRICATION DETECTION")
    print(f"{'='*60}")
    print(f"Total claims extracted: {total_claims}")
    print(f"Verified in source:     {total_verified} ({total_verified/total_claims*100:.1f}%)")
    print(f"NOT found (fabricated): {total_fabricated} ({total_fabricated/total_claims*100:.1f}%)")
    print(f"Cases with fabrication: {cases_with_fab}/{len(all_verifications)}")
    print()
    print("Cases with fabricated claims:")
    for case_id, count in fabrication_summary.most_common():
        print(f"  {case_id}: {count} fabricated claim(s)")

    if args.output:
        output = {
            'metadata': {
                'torch_dir': args.torch_dir,
                'total_claims': total_claims,
                'verified': total_verified,
                'fabricated': total_fabricated,
                'cases_with_fabrication': cases_with_fab,
            },
            'results': all_verifications,
        }
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nSaved to {args.output}")


if __name__ == '__main__':
    main()
