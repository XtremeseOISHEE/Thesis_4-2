"""
run_experiment_e1.py
E1: Main comparison experiment. Runs Systems A, B, and C on the
selected cases and saves results to CSV for analysis.
"""
import sys
import csv
import time
import glob
import os
sys.path.append("E:/Oishee/Thesis/system_c")

from system_a import SystemA
from system_b import SystemB
from system_c import SystemC


# In-scope cases live in cases_v2/, out-of-scope negative controls in cases_oos/.
IN_SCOPE_DIR = "E:/Oishee/Thesis/cases_v2"
OUT_OF_SCOPE_DIR = "E:/Oishee/Thesis/cases_oos"

# Smoke-test limit: set to a small int (e.g. 3) to run only the first N cases.
# Set to None or 0 to run ALL cases.
LIMIT = None


def load_case_list():
    """Scan both case folders and return (path, scope) tuples. The in_scope /
    out_of_scope label is determined solely by WHICH FOLDER the case is in --
    NOT by re-running condition detection (detection is what E1 evaluates)."""
    in_scope = sorted(glob.glob(os.path.join(IN_SCOPE_DIR, "*.txt")))
    out_of_scope = sorted(glob.glob(os.path.join(OUT_OF_SCOPE_DIR, "*.txt")))
    cases = [(p, "in_scope") for p in in_scope]
    cases += [(p, "out_of_scope") for p in out_of_scope]
    return cases


def count_words(text):
    return len(text.split()) if text else 0


if __name__ == "__main__":
    print("=" * 60)
    print("E1: MAIN COMPARISON EXPERIMENT (Systems A, B, C)")
    print("=" * 60)

    # Initialize all three systems
    sys_a = SystemA()
    sys_b = SystemB()
    sys_c = SystemC()

    case_paths = load_case_list()
    if LIMIT:
        case_paths = case_paths[:LIMIT]
        print(f"\n*** SMOKE TEST: LIMIT={LIMIT} -- running only the first {LIMIT} cases ***")
    print(f"\nRunning on {len(case_paths)} cases...\n")

    rows = []

    for idx, (path, scope) in enumerate(case_paths, 1):
        case = sys_a.loader.load_case(path)
        fname = case["filename"]
        print(f"[{idx}/{len(case_paths)}] [{scope}] {fname}")

        # Deterministic condition routing actually used by the pipeline (no API).
        # Recorded per case so the stratified summary reflects the real run.
        c_text = case["transcription"] if case["transcription"] else case["full_text"]
        detected = sys_c.reasoner._guess_condition(case.get("description", ""), c_text)

        # --- System A ---
        try:
            ra = sys_a.analyze_case(case)
            a_words = count_words(ra["output"])
            print(f"    System A done ({a_words} words)")
        except Exception as e:
            a_words = -1
            print(f"    System A ERROR: {e}")

        # --- System B ---
        try:
            rb = sys_b.analyze_case(case)
            b_hops = len(rb["trace"])
            b_guidelines = sum(len(h["guidelines_used"]) for h in rb["trace"])
            print(f"    System B done ({b_hops} hops, {b_guidelines} guideline refs)")
        except Exception as e:
            b_hops, b_guidelines = -1, -1
            print(f"    System B ERROR: {e}")

        # --- System C ---
        try:
            rc = sys_c.analyze_case(case)
            verdicts = sys_c.count_verdicts(rc["trace"])
            c_supported = verdicts.get("SUPPORTED", 0)
            c_partial = verdicts.get("PARTIAL", 0)
            c_unsupported = verdicts.get("UNSUPPORTED", 0)
            print(f"    System C done (S:{c_supported} P:{c_partial} U:{c_unsupported})")
        except Exception as e:
            c_supported = c_partial = c_unsupported = -1
            print(f"    System C ERROR: {e}")

        rows.append({
            "case": fname,
            "detected_condition": detected,
            "labeled_condition": case["condition"],
            "A_output_words": a_words,
            "B_hops": b_hops,
            "B_guideline_refs": b_guidelines,
            "C_supported": c_supported,
            "C_partial": c_partial,
            "C_unsupported": c_unsupported,
        })

        # Small pause to respect API rate limits
        time.sleep(2)
        print()

    # Save to CSV
    out_path = "E:/Oishee/Thesis/results_e1.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 60)
    print(f"E1 COMPLETE. Results saved to: {out_path}")
    print("=" * 60)
    print(f"\nProcessed {len(rows)} cases.")
    print("Summary of System C verdicts across all cases:")
    total_s = sum(r["C_supported"] for r in rows if r["C_supported"] >= 0)
    total_p = sum(r["C_partial"] for r in rows if r["C_partial"] >= 0)
    total_u = sum(r["C_unsupported"] for r in rows if r["C_unsupported"] >= 0)
    print(f"  SUPPORTED: {total_s}")
    print(f"  PARTIAL: {total_p}")
    print(f"  UNSUPPORTED: {total_u}")