"""
run_experiment_e5.py
E5: Error analysis. Categorizes WHERE and WHY System C produces
non-SUPPORTED verdicts, by re-running the in-scope cases and classifying
each hop's verdict + reason into error categories.
"""
import sys
import csv
import time
import glob
import os
sys.path.append("E:/Oishee/Thesis/system_c")

from system_c import SystemC

# Same 56 cases as E1: in-scope in cases_v2/, out-of-scope controls in cases_oos/.
IN_SCOPE_DIR = "E:/Oishee/Thesis/cases_v2"
OUT_OF_SCOPE_DIR = "E:/Oishee/Thesis/cases_oos"

# Smoke-test limit: set to a small int (e.g. 3) to run only the first N cases.
# Set to None or 0 to run ALL cases.
LIMIT = None


def categorize(verdict, reason, routing_error=False):
    """Classify a non-supported verdict into an error category."""
    if verdict == "SUPPORTED":
        return "verified_ok"
    # Detection-aware: a mis-routed in-scope case had its reasoning checked
    # against the WRONG guideline family, so an UNSUPPORTED verdict here is a
    # routing error, not a genuine reasoning/guideline mismatch.
    if routing_error and verdict == "UNSUPPORTED":
        return "routing_error"
    r = reason.lower()
    # Out-of-scope: the reason says the condition/principle is absent/different
    if "absent" in r or "not mentioned" in r or "not addressed" in r or "different" in r:
        return "out_of_scope_disease"
    # Over-specific: claim adds detail beyond guideline
    if "specific" in r or "additional" in r or "also asserts" in r or "not covered" in r:
        return "claim_more_specific_than_guideline"
    # Otherwise: partial alignment
    return "partial_alignment"


if __name__ == "__main__":
    print("=" * 65)
    print("E5: ERROR ANALYSIS")
    print("=" * 65)

    system = SystemC()

    # Track errors by hop position and by category
    hop_errors = {"Hop 1": {"S": 0, "P": 0, "U": 0},
                  "Hop 2": {"S": 0, "P": 0, "U": 0},
                  "Hop 3": {"S": 0, "P": 0, "U": 0}}
    categories = {}
    rows = []

    # Scope is determined by WHICH FOLDER the case is in (same as E1) --
    # NOT by re-detecting the condition.
    in_scope = sorted(glob.glob(os.path.join(IN_SCOPE_DIR, "*.txt")))
    out_of_scope = sorted(glob.glob(os.path.join(OUT_OF_SCOPE_DIR, "*.txt")))
    all_cases = [(p, "in_scope") for p in in_scope] + \
                [(p, "out_of_scope") for p in out_of_scope]
    if LIMIT:
        all_cases = all_cases[:LIMIT]
        print(f"*** SMOKE TEST: LIMIT={LIMIT} -- running only the first {LIMIT} cases ***")

    for path, scope in all_cases:
        case = system.loader.load_case(path)
        fname = case["filename"]
        case_text = case["transcription"] if case["transcription"] else case["full_text"]
        # Detection-aware routing check: an in-scope case whose detected condition
        # differs from its labeled condition was routed to the WRONG guideline family.
        detected = system.reasoner._guess_condition(case.get("description", ""), case_text)
        labeled_key = case["condition"].strip().lower()
        routing_error = (scope == "in_scope") and (detected != labeled_key)
        print(f"\nAnalyzing [{scope}]: {fname[:45]}  (detected={detected}, labeled={labeled_key})")
        result = system.analyze_case(case)

        for step in result["trace"]:
            verdict = step["verdict"].upper()
            hop_key = step["hop_name"].split(":")[0]  # "Hop 1"

            # Tally by hop position
            short = {"SUPPORTED": "S", "PARTIAL": "P", "UNSUPPORTED": "U"}.get(verdict, "U")
            if hop_key in hop_errors:
                hop_errors[hop_key][short] += 1

            # Categorize (detection-aware)
            cat = categorize(verdict, step["verification_reason"], routing_error=routing_error)
            categories[cat] = categories.get(cat, 0) + 1

            print(f"    {hop_key}: {verdict} -> {cat}")

            rows.append({
                "case": fname,
                "scope": scope,
                "hop": hop_key,
                "verdict": verdict,
                "category": cat,
            })

        # Small pause between cases (network retry in llm_connector handles blips).
        time.sleep(2)

    # Save CSV
    with open("E:/Oishee/Thesis/results_e5.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Report
    print("\n" + "=" * 65)
    print("E5 RESULTS")
    print("=" * 65)

    print("\n--- Verdicts by HOP POSITION ---")
    for hop, c in hop_errors.items():
        print(f"  {hop}: S:{c['S']} P:{c['P']} U:{c['U']}")

    print("\n--- ERROR / VERDICT CATEGORIES ---")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {count:2d}  {cat}")

    print("\n" + "=" * 65)
    print("Saved to results_e5.csv")
    print("=" * 65)