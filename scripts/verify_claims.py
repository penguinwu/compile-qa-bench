#!/usr/bin/env python3
"""
Automated fabrication detector for Mode B agent guidance.

Extracts claimed config flags, env vars, API methods, import paths, and
sub-config options from agent guidance, then verifies each against the
PyTorch source code.

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


# Patterns to extract claims from agent guidance.
# More specific patterns come first to avoid redundant matches.
CLAIM_PATTERNS = [
    # --- Inductor sub-configs (triton.X, cpp.X) — check BEFORE top-level ---
    (r'(?:torch\._inductor\.)?config\.triton\.(\w+)', 'triton_subconfig'),
    (r'(?:torch\._inductor\.)?config\.cpp\.(\w+)', 'cpp_subconfig'),

    # --- Top-level inductor/dynamo config ---
    (r'torch\._inductor\.config\.(\w+)', 'inductor_config'),
    (r'torch\._dynamo\.config\.(\w+)', 'dynamo_config'),
    (r'config\.(\w+)\s*=', 'config_assignment'),

    # --- Functorch config ---
    (r'torch\._functorch\.config\.(\w+)', 'functorch_config'),

    # --- Environment variables ---
    (r'(TORCHINDUCTOR_\w+)', 'env_var'),
    (r'(TORCHDYNAMO_\w+)', 'env_var'),
    (r'(TORCH_COMPILE_\w+)', 'env_var'),

    # --- Compiler / higher-order ops API ---
    (r'torch\.compiler\.(\w+)', 'compiler_api'),
    (r'torch\._higher_order_ops\.(\w+)', 'higher_order_ops'),

    # --- Import path claims: from torch.X.Y import Z, W ---
    # Captures first imported name; comma-separated names handled in extract.
    (r'from\s+(torch(?:\.\w+)+)\s+import\s+(\w+(?:\s*,\s*\w+)*)', 'import_claim'),

    # --- Decorator claims ---
    (r'@(\w+)\.register_decomposition', 'decorator_claim'),

    # --- Specific module APIs that are commonly fabricated ---
    (r'torch\.utils\.checkpoint\.(\w+)', 'checkpoint_api'),
    (r'torch\.nn\.attention\.(\w+)', 'attention_api'),
    (r'torch\.distributed\.optim\.(\w+)', 'distributed_optim_api'),
]

# Known valid references (not worth checking — too generic or namespace names)
SKIP_CLAIMS = {
    'inductor_config': {'True', 'False', 'None', 'default', 'triton', 'cpp'},
    'dynamo_config': {'True', 'False', 'None', 'default'},
    'config_assignment': {'True', 'False', 'None', 'triton', 'cpp'},
    'triton_subconfig': {'True', 'False', 'None'},
    'cpp_subconfig': {'True', 'False', 'None'},
    'functorch_config': {'True', 'False', 'None', 'default'},
    'env_var': set(),
    'compiler_api': set(),
    'higher_order_ops': set(),
    'import_claim': set(),
    'decorator_claim': set(),
    'checkpoint_api': set(),
    'attention_api': set(),
    'distributed_optim_api': set(),
}


def extract_claims(guidance: str) -> list[dict]:
    """Extract verifiable claims from agent guidance text.

    Deduplicates claims by (type, value, module_path) to avoid redundant
    verification.
    """
    claims = []
    seen = set()
    for pattern, claim_type in CLAIM_PATTERNS:
        for match in re.finditer(pattern, guidance):
            context = guidance[max(0, match.start()-30):match.end()+30]
            full_claim = match.group(0)

            if claim_type == 'import_claim':
                # Handle comma-separated imports: "from X import A, B, C"
                module_path = match.group(1)
                names_str = match.group(2)
                import_names = [n.strip() for n in names_str.split(',')]
                for name in import_names:
                    if not name or name in SKIP_CLAIMS.get('import_claim',
                                                           set()):
                        continue
                    dedup_key = ('import_claim', name, module_path)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    claims.append({
                        'claim': full_claim,
                        'value': name,
                        'type': 'import_claim',
                        'module_path': module_path,
                        'context': context,
                    })
                continue

            value = match.group(1) if match.lastindex else match.group(0)
            module_path = None

            if value in SKIP_CLAIMS.get(claim_type, set()):
                continue

            dedup_key = (claim_type, value, module_path)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            claim = {
                'claim': full_claim,
                'value': value,
                'type': claim_type,
                'context': context,
            }
            if module_path:
                claim['module_path'] = module_path
            claims.append(claim)
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

    elif claim_type == 'triton_subconfig':
        # Verify attribute defined in inductor config (e.g. class triton:)
        search_file = os.path.join(torch_dir, '_inductor/config.py')
        result = subprocess.run(
            ['grep', '-nP', rf'^\s+{re.escape(value)}\s*[=:]', search_file],
            capture_output=True, text=True
        )
        found = result.returncode == 0

    elif claim_type == 'cpp_subconfig':
        search_file = os.path.join(torch_dir, '_inductor/config.py')
        result = subprocess.run(
            ['grep', '-nP', rf'^\s+{re.escape(value)}\s*[=:]', search_file],
            capture_output=True, text=True
        )
        found = result.returncode == 0

    elif claim_type == 'functorch_config':
        search_file = os.path.join(torch_dir, '_functorch/config.py')
        if os.path.exists(search_file):
            # Use \s* (not \s+) — functorch config uses module-level vars
            result = subprocess.run(
                ['grep', '-nP', rf'^\s*{re.escape(value)}\s*[=:]',
                 search_file],
                capture_output=True, text=True
            )
            found = result.returncode == 0
        else:
            result = subprocess.CompletedProcess(
                args=[], returncode=1, stdout='', stderr=''
            )
            found = False

    elif claim_type == 'decorator_claim':
        # Check if @X.register_decomposition is valid — it must be a method
        # on an op/module object. Search for the pattern in torch source.
        result = subprocess.run(
            ['grep', '-rn', r'register_decomposition', torch_dir,
             '--include=*.py'],
            capture_output=True, text=True, timeout=10
        )
        # register_decomposition exists as a standalone function, but
        # @op.register_decomposition (as a method on an op object) does not.
        # Check if the specific object pattern exists.
        if result.returncode == 0:
            obj_name = value  # The object before .register_decomposition
            obj_pattern = rf'\.register_decomposition'
            result2 = subprocess.run(
                ['grep', '-rnP', rf'{re.escape(obj_name)}\.register_decomposition',
                 torch_dir, '--include=*.py'],
                capture_output=True, text=True, timeout=10
            )
            found = result2.returncode == 0
            result = result2
        else:
            found = False

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

    elif claim_type == 'import_claim':
        module_path = claim.get('module_path', '')
        parts = module_path.split('.')
        if parts[0] == 'torch' and len(parts) > 1:
            sub_path = os.path.join(*parts[1:])
            search_path = os.path.join(torch_dir, sub_path)
            if os.path.isdir(search_path):
                result = subprocess.run(
                    ['grep', '-rnw', value, search_path, '--include=*.py'],
                    capture_output=True, text=True, timeout=10
                )
            elif os.path.isfile(search_path + '.py'):
                result = subprocess.run(
                    ['grep', '-nw', value, search_path + '.py'],
                    capture_output=True, text=True, timeout=10
                )
            else:
                result = subprocess.CompletedProcess(
                    args=[], returncode=1, stdout='', stderr=''
                )
            found = result.returncode == 0
        else:
            # Non-torch import, skip verification
            result = subprocess.CompletedProcess(
                args=[], returncode=0, stdout='skipped', stderr=''
            )
            found = True

    elif claim_type in ('checkpoint_api', 'attention_api',
                        'distributed_optim_api'):
        module_paths = {
            'checkpoint_api': 'utils/checkpoint.py',
            'attention_api': 'nn/attention',
            'distributed_optim_api': 'distributed/optim',
        }
        rel_path = module_paths[claim_type]
        search_path = os.path.join(torch_dir, rel_path)
        if os.path.isdir(search_path):
            result = subprocess.run(
                ['grep', '-rnw', value, search_path, '--include=*.py'],
                capture_output=True, text=True, timeout=10
            )
        elif os.path.isfile(search_path):
            result = subprocess.run(
                ['grep', '-nw', value, search_path],
                capture_output=True, text=True
            )
        else:
            result = subprocess.CompletedProcess(
                args=[], returncode=1, stdout='', stderr=''
            )
        found = result.returncode == 0

    else:
        # Fallback: broad search
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
    parser = argparse.ArgumentParser(
        description='Verify claims in Mode B guidance'
    )
    parser.add_argument('--results', required=True, help='Mode B results JSON')
    parser.add_argument('--torch-dir', required=True,
                        help='PyTorch source directory')
    parser.add_argument('--output', help='Output JSON path')
    args = parser.parse_args()

    with open(args.results) as f:
        data = json.load(f)

    results = data.get('results', data) if isinstance(data, dict) else data

    all_verifications = []
    fabrication_summary = Counter()
    fabrication_types = Counter()

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
                fabrication_types[verified['type']] += 1

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
    if total_claims > 0:
        print(f"Verified in source:     {total_verified}"
              f" ({total_verified/total_claims*100:.1f}%)")
        print(f"NOT found (fabricated): {total_fabricated}"
              f" ({total_fabricated/total_claims*100:.1f}%)")
    else:
        print(f"Verified in source:     0")
        print(f"NOT found (fabricated): 0")
    print(f"Cases with fabrication: {cases_with_fab}/{len(all_verifications)}")
    print()

    if fabrication_types:
        print("Fabrications by type:")
        for ftype, count in fabrication_types.most_common():
            print(f"  {ftype}: {count}")
        print()

    if fabrication_summary:
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
                'fabrication_by_type': dict(fabrication_types),
            },
            'results': all_verifications,
        }
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nSaved to {args.output}")


if __name__ == '__main__':
    main()
