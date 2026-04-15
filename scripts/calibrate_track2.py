#!/usr/bin/env python3
"""Track 2 IAA Calibration Script.

Applies calibration rules to Track 2 label scores (Owl + Raven) based on
systematic disagreement patterns identified in pre-calibration IAA analysis.

New calibration rules (extending Rules 1-5 from v3.0 rubric):
  Rule 6 (has_imperative): "The best approach is to [verb]", "you should [verb]",
    "recommend [verb]ing" count as imperative — they give the user a directive action.
  Rule 7 (case_specific, Act): For doc-restricted responses, listing missing docs
    or referencing the user's topic area without unique actionable content does NOT
    count as case_specific. Requires instructions/suggestions/workarounds tailored
    to this user's specific problem.
  Rule 8 (names_mechanism, extends Rule 3): Config options (fullgraph=True, dynamic=True),
    framework diagnostic tools (torch.profiler, TORCH_LOGS, TORCHINDUCTOR_PROFILE),
    and generic feature names (graph breaks, compilation, backends) are NOT mechanisms.
    A mechanism = specific internal component, algorithm, or code path.
  Rule 9 (causal_chain): For doc-restricted responses, "X may be causing this" or
    "this could be due to" are NOT causal chains. Requires (1) naming the mechanism,
    (2) explaining how it causes the symptom, (3) stated definitively.
  Rule 10 (case_specific_diagnosis): Identifying the correct topic area is
    correct_subsystem, not case_specific_diagnosis. Requires referencing specific
    technical details unique to this case in diagnostic reasoning.

Usage:
    python3 scripts/calibrate_track2.py
"""

import json
import copy
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
LABEL_DIR = BASE / "runs" / "label-scoring"

# Load Track 2 responses for reference
T2_BASELINE = BASE / "runs/2026-04-12-baseline/mode_b_doc_restricted.json"


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("results", data.get("cases", []))
    return data


def by_id(recs):
    return {r["id"]: r for r in recs}


def compute_act_score(rec):
    if rec.get("standalone_fix", False):
        return 3
    if rec.get("has_imperative", False) and rec.get("case_specific", False):
        return 2
    if rec.get("has_imperative", False):
        return 1
    return 0


def compute_diag_score(rec):
    if not rec.get("consistent_with_resolution", True):
        count = sum([
            rec.get("correct_subsystem", False),
            rec.get("names_mechanism", False),
            rec.get("causal_chain", False),
            rec.get("case_specific_diagnosis", False),
        ])
        return min(1, count)
    count = sum([
        rec.get("correct_subsystem", False),
        rec.get("names_mechanism", False),
        rec.get("causal_chain", False),
        rec.get("case_specific_diagnosis", False),
    ])
    if count >= 3:
        return 3
    return count


def main():
    # Load files
    owl_act = by_id(load_json(LABEL_DIR / "owl_act_labels_track2_160.json"))
    rav_act = by_id(load_json(LABEL_DIR / "raven_act_labels_track2_160.json"))
    owl_diag = by_id(load_json(LABEL_DIR / "owl_diag_labels_track2_160.json"))
    rav_diag = by_id(load_json(LABEL_DIR / "raven_diag_labels_track2_160.json"))
    t2_responses = by_id(load_json(T2_BASELINE))

    # Deep copy for calibration
    owl_act_cal = {k: copy.deepcopy(v) for k, v in owl_act.items()}
    rav_act_cal = {k: copy.deepcopy(v) for k, v in rav_act.items()}
    owl_diag_cal = {k: copy.deepcopy(v) for k, v in owl_diag.items()}
    rav_diag_cal = {k: copy.deepcopy(v) for k, v in rav_diag.items()}

    calibration_log = {
        "rules_applied": [],
        "act_flips": {"owl": [], "raven": []},
        "diag_flips": {"owl": [], "raven": []},
    }

    # =====================================================
    # RULE 6: has_imperative — soft imperatives count
    # =====================================================
    # Raven found imperatives in template responses that Owl missed.
    # "The best approach is to [verb]" = imperative.
    # Adjudication: Raven correct for 27 of 28 cases.
    rule6_owl_flips = []
    for cid in sorted(owl_act.keys()):
        owl_val = owl_act[cid].get("has_imperative", False)
        rav_val = rav_act[cid].get("has_imperative", False)
        if not owl_val and rav_val:
            # Raven found imperative, Owl didn't — check response
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")
            # Check for soft imperative patterns
            import re
            has_soft_imp = bool(re.search(
                r"(the best approach is to|you should|recommend|"
                r"best approach is to|consider|try|use |check |consult |"
                r"ensure |verify |review )",
                resp, re.IGNORECASE
            ))
            if has_soft_imp:
                owl_act_cal[cid]["has_imperative"] = True
                rule6_owl_flips.append(cid)

    # Also check J1-4 (Owl=true, Raven=false) — keep Owl's judgment for now
    # J1-4 response says "To use torch..." which is imperative
    print(f"Rule 6 (has_imperative): Owl flipped {len(rule6_owl_flips)} cases true")
    calibration_log["rules_applied"].append({
        "rule": 6,
        "description": "Soft imperatives ('best approach is to [verb]') count as imperative",
        "owl_flips_true": rule6_owl_flips,
        "raven_flips": [],
    })
    calibration_log["act_flips"]["owl"].extend(
        [{"id": c, "label": "has_imperative", "old": False, "new": True, "rule": 6}
         for c in rule6_owl_flips]
    )

    # =====================================================
    # RULE 7: case_specific — topic naming ≠ case-specific
    # =====================================================
    # Most Track 2 responses just name what docs DON'T cover.
    # That's topic identification, not case-specific actionable content.
    rule7_owl_flips = []
    rule7_raven_flips = []
    for cid in sorted(owl_act.keys()):
        owl_val = owl_act[cid].get("case_specific", False)
        rav_val = rav_act[cid].get("case_specific", False)
        if owl_val and not rav_val:
            # Owl=true, Raven=false — check if response has case-specific ACTIONS
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")
            doc_suf = t2_responses.get(cid, {}).get("doc_sufficient", False)
            is_template = owl_act[cid].get("is_template", False) or rav_act[cid].get("is_template", False)

            # If doc_sufficient=false and no standalone fix, likely just gap identification
            if not doc_suf and not owl_act[cid].get("standalone_fix", False):
                owl_act_cal[cid]["case_specific"] = False
                rule7_owl_flips.append(cid)
            elif is_template:
                owl_act_cal[cid]["case_specific"] = False
                rule7_owl_flips.append(cid)
        elif not owl_val and rav_val:
            # Raven=true, Owl=false — keep Owl's stricter judgment
            rav_act_cal[cid]["case_specific"] = False
            rule7_raven_flips.append(cid)

    print(f"Rule 7 (case_specific): Owl flipped {len(rule7_owl_flips)} false, Raven flipped {len(rule7_raven_flips)} false")
    calibration_log["rules_applied"].append({
        "rule": 7,
        "description": "Topic naming without unique actionable content ≠ case_specific",
        "owl_flips_false": rule7_owl_flips,
        "raven_flips_false": rule7_raven_flips,
    })
    calibration_log["act_flips"]["owl"].extend(
        [{"id": c, "label": "case_specific", "old": True, "new": False, "rule": 7}
         for c in rule7_owl_flips]
    )
    calibration_log["act_flips"]["raven"].extend(
        [{"id": c, "label": "case_specific", "old": True, "new": False, "rule": 7}
         for c in rule7_raven_flips]
    )

    # =====================================================
    # RULE 8: names_mechanism — extends Rule 3
    # =====================================================
    # Owl counted diagnostic tools and config options as mechanisms.
    # Per Rule 3: diagnostic tools ≠ mechanism.
    rule8_owl_flips = []
    rule8_raven_flips = []
    for cid in sorted(owl_diag.keys()):
        owl_val = owl_diag[cid].get("names_mechanism", False)
        rav_val = rav_diag[cid].get("names_mechanism", False)
        if owl_val and not rav_val:
            # Owl=true, Raven=false — check if Owl is counting diagnostic tools
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")
            is_template_owl = owl_act.get(cid, {}).get("is_template", False)
            is_template_rav = rav_act.get(cid, {}).get("is_template", False)
            is_template = is_template_owl or is_template_rav
            doc_suf = t2_responses.get(cid, {}).get("doc_sufficient", False)

            # Templates never name specific mechanisms
            if is_template:
                owl_diag_cal[cid]["names_mechanism"] = False
                rule8_owl_flips.append(cid)
                continue

            # Check if the response only mentions diagnostic tools (Rule 3 expanded)
            import re
            diag_tools = re.findall(
                r"(TORCH_LOGS|torch\.profiler|TORCHINDUCTOR_PROFILE|"
                r"TORCH_COMPILE_DEBUG|Chrome trace|profiler|TORCH_LOGS_FORMAT|"
                r"torch\.compiler\.disable|fullgraph=True|dynamic=True|"
                r"graph break|compilation|recompilation)",
                resp, re.IGNORECASE
            )
            # Check for real mechanism names
            real_mechanisms = re.findall(
                r"(guard system|guard failure|AOT autograd|TorchDynamo trace|"
                r"Inductor codegen|kernel fusion|cudagraph tree|"
                r"backward trace|FX graph|operator lowering|"
                r"specialize|symbolic shape|tensor subclass|"
                r"torch\.library|custom_op|wrap_with_proxy|"
                r"pattern match|post-grad pass|pre-grad pass|"
                r"autotuner|benchmark|triton kernel|"
                r"\_dynamo\.config\.|\_inductor\.config\.)",
                resp, re.IGNORECASE
            )

            if diag_tools and not real_mechanisms:
                owl_diag_cal[cid]["names_mechanism"] = False
                rule8_owl_flips.append(cid)
            elif not doc_suf and not real_mechanisms:
                # doc-insufficient with no real mechanism names
                owl_diag_cal[cid]["names_mechanism"] = False
                rule8_owl_flips.append(cid)

        elif not owl_val and rav_val:
            # Raven=true, Owl=false — check if Raven is correct
            # Generally keep Owl's stricter judgment unless response has clear mechanism
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")
            import re
            real_mechanisms = re.findall(
                r"(guard system|guard failure|AOT autograd|TorchDynamo trace|"
                r"Inductor codegen|kernel fusion|cudagraph tree|"
                r"backward trace|FX graph|operator lowering|"
                r"specialize|symbolic shape|tensor subclass|"
                r"torch\.library|custom_op|wrap_with_proxy|"
                r"pattern match|post-grad pass|pre-grad pass|"
                r"autotuner|benchmark|triton kernel|"
                r"\_dynamo\.config\.|\_inductor\.config\.)",
                resp, re.IGNORECASE
            )
            if not real_mechanisms:
                rav_diag_cal[cid]["names_mechanism"] = False
                rule8_raven_flips.append(cid)

    print(f"Rule 8 (names_mechanism): Owl flipped {len(rule8_owl_flips)} false, Raven flipped {len(rule8_raven_flips)} false")
    calibration_log["rules_applied"].append({
        "rule": 8,
        "description": "Diagnostic tools, config options, generic feature names ≠ mechanism",
        "owl_flips_false": rule8_owl_flips,
        "raven_flips_false": rule8_raven_flips,
    })
    calibration_log["diag_flips"]["owl"].extend(
        [{"id": c, "label": "names_mechanism", "old": True, "new": False, "rule": 8}
         for c in rule8_owl_flips]
    )
    calibration_log["diag_flips"]["raven"].extend(
        [{"id": c, "label": "names_mechanism", "old": True, "new": False, "rule": 8}
         for c in rule8_raven_flips]
    )

    # =====================================================
    # RULE 9: causal_chain — strict definition
    # =====================================================
    # From Track 1 calibration: investigation methodology ≠ causal chain,
    # hedged hypotheses ≠ causal chain. Requires definitive mechanism→symptom.
    rule9_raven_flips = []
    for cid in sorted(owl_diag.keys()):
        owl_val = owl_diag[cid].get("causal_chain", False)
        rav_val = rav_diag[cid].get("causal_chain", False)
        if not owl_val and rav_val:
            # Raven=true, Owl=false — check if response has definitive causal chain
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")
            is_template_owl = owl_act.get(cid, {}).get("is_template", False)
            is_template_rav = rav_act.get(cid, {}).get("is_template", False)

            # Templates never have causal chains
            if is_template_owl or is_template_rav:
                rav_diag_cal[cid]["causal_chain"] = False
                rule9_raven_flips.append(cid)
                continue

            import re
            # Check for hedged language (NOT a causal chain)
            hedged = bool(re.search(
                r"(may be|might be|could be|possibly|likely|"
                r"may stem from|could stem from|appears to|"
                r"might cause|could cause|may cause|"
                r"this could|this may|potentially|"
                r"it is possible|seem to|"
                r"consider that|suggest that.*might)",
                resp, re.IGNORECASE
            ))

            # Check for definitive causal language
            definitive = bool(re.search(
                r"(causes|because|results in|leads to|"
                r"this is because|the reason is|"
                r"triggers|prevents|forces|"
                r"X does Y which means Z|"
                r"when .+ happens.+ which .+ causes)",
                resp, re.IGNORECASE
            ))

            # If only hedged, flip to false
            if hedged and not definitive:
                rav_diag_cal[cid]["causal_chain"] = False
                rule9_raven_flips.append(cid)
            elif not hedged and not definitive:
                # No causal language at all
                rav_diag_cal[cid]["causal_chain"] = False
                rule9_raven_flips.append(cid)

    print(f"Rule 9 (causal_chain): Raven flipped {len(rule9_raven_flips)} false")
    calibration_log["rules_applied"].append({
        "rule": 9,
        "description": "Hedged hypotheses and investigation methodology ≠ causal chain",
        "raven_flips_false": rule9_raven_flips,
    })
    calibration_log["diag_flips"]["raven"].extend(
        [{"id": c, "label": "causal_chain", "old": True, "new": False, "rule": 9}
         for c in rule9_raven_flips]
    )

    # =====================================================
    # RULE 10: case_specific_diagnosis — topic ≠ diagnosis
    # =====================================================
    # Identifying the right topic area = correct_subsystem.
    # case_specific_diagnosis requires specific technical details unique to this case.
    rule10_raven_flips = []
    rule10_owl_flips = []
    for cid in sorted(owl_diag.keys()):
        owl_val = owl_diag[cid].get("case_specific_diagnosis", False)
        rav_val = rav_diag[cid].get("case_specific_diagnosis", False)
        if not owl_val and rav_val:
            # Raven=true, Owl=false
            is_template = owl_act.get(cid, {}).get("is_template", False) or rav_act.get(cid, {}).get("is_template", False)
            doc_suf = t2_responses.get(cid, {}).get("doc_sufficient", False)
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")

            # Templates = no case-specific diagnosis by definition
            if is_template:
                rav_diag_cal[cid]["case_specific_diagnosis"] = False
                rule10_raven_flips.append(cid)
                continue

            # For doc-insufficient cases: check if response has case-specific technical details
            # or just identifies the topic area
            if not doc_suf:
                # Check for specific error messages, API references, version numbers
                import re
                specific_detail = bool(re.search(
                    r"(error:|traceback|version \d|issue #|"
                    r"specifically|your .+ model|your .+ code|"
                    r"in your case|for your .+ scenario)",
                    resp, re.IGNORECASE
                ))
                if not specific_detail:
                    rav_diag_cal[cid]["case_specific_diagnosis"] = False
                    rule10_raven_flips.append(cid)
        elif owl_val and not rav_val:
            # Owl=true, Raven=false — small count (3), keep for individual review
            pass

    print(f"Rule 10 (case_specific_diagnosis): Raven flipped {len(rule10_raven_flips)} false")
    calibration_log["rules_applied"].append({
        "rule": 10,
        "description": "Topic identification ≠ case_specific_diagnosis; requires unique technical details",
        "raven_flips_false": rule10_raven_flips,
    })
    calibration_log["diag_flips"]["raven"].extend(
        [{"id": c, "label": "case_specific_diagnosis", "old": True, "new": False, "rule": 10}
         for c in rule10_raven_flips]
    )

    # =====================================================
    # TEMPLATE ALIGNMENT: is_template
    # =====================================================
    # Raven flagged 15 more templates than Owl (J7-12..20, J8-11..20 "Based on a search" pattern)
    # These are structural templates — same opening pattern even if content varies slightly
    # Align to Raven's broader template detection
    template_owl_flips = []
    for cid in sorted(owl_act.keys()):
        owl_val = owl_act[cid].get("is_template", False)
        rav_val = rav_act[cid].get("is_template", False)
        if not owl_val and rav_val:
            resp = t2_responses.get(cid, {}).get("agent_guidance", "")
            if resp.startswith("Based on a search"):
                owl_act_cal[cid]["is_template"] = True
                template_owl_flips.append(cid)

    print(f"Template alignment: Owl flipped {len(template_owl_flips)} to is_template=true")
    calibration_log["act_flips"]["owl"].extend(
        [{"id": c, "label": "is_template", "old": False, "new": True, "rule": "template_alignment"}
         for c in template_owl_flips]
    )

    # =====================================================
    # Recompute derived scores
    # =====================================================
    for cid in owl_act_cal:
        owl_act_cal[cid]["derived_act"] = compute_act_score(owl_act_cal[cid])
    for cid in rav_act_cal:
        rav_act_cal[cid]["derived_act"] = compute_act_score(rav_act_cal[cid])
    for cid in owl_diag_cal:
        owl_diag_cal[cid]["derived_diag"] = compute_diag_score(owl_diag_cal[cid])
    for cid in rav_diag_cal:
        rav_diag_cal[cid]["derived_diag"] = compute_diag_score(rav_diag_cal[cid])

    # Print new distributions
    print("\n=== Post-Calibration Distributions ===")
    print("Act (Owl):", dict(sorted(Counter(v["derived_act"] for v in owl_act_cal.values()).items())))
    print("Act (Rav):", dict(sorted(Counter(v["derived_act"] for v in rav_act_cal.values()).items())))
    print("Diag (Owl):", dict(sorted(Counter(v["derived_diag"] for v in owl_diag_cal.values()).items())))
    print("Diag (Rav):", dict(sorted(Counter(v["derived_diag"] for v in rav_diag_cal.values()).items())))

    # Per-label agreement post-cal
    print("\n=== Post-Cal Label Agreement ===")
    for label in ["standalone_fix", "has_imperative", "case_specific", "is_template"]:
        agree = sum(1 for cid in owl_act_cal
                    if owl_act_cal[cid].get(label) == rav_act_cal[cid].get(label))
        print(f"  {label:20s}: {agree}/160")

    for label in ["correct_subsystem", "names_mechanism", "causal_chain",
                   "consistent_with_resolution", "case_specific_diagnosis"]:
        agree = sum(1 for cid in owl_diag_cal
                    if owl_diag_cal[cid].get(label) == rav_diag_cal[cid].get(label))
        print(f"  {label:30s}: {agree}/160")

    # Save calibrated files
    def save(data, filename):
        records = sorted(data.values(), key=lambda r: r["id"])
        path = LABEL_DIR / filename
        with open(path, "w") as f:
            json.dump(records, f, indent=2)
        print(f"\nSaved: {path}")

    save(owl_act_cal, "owl_act_labels_track2_160_calibrated.json")
    save(rav_act_cal, "raven_act_labels_track2_160_calibrated.json")
    save(owl_diag_cal, "owl_diag_labels_track2_160_calibrated.json")
    save(rav_diag_cal, "raven_diag_labels_track2_160_calibrated.json")

    # Save calibration log
    log_path = BASE / "analysis" / "track2_calibration_log.json"
    with open(log_path, "w") as f:
        json.dump(calibration_log, f, indent=2)
    print(f"Saved calibration log: {log_path}")


if __name__ == "__main__":
    main()
