"""
run_experiment_e1.py
E1: Main comparison experiment. Runs Systems A, B, and C on the
selected cases and saves results to CSV for analysis.
"""
import sys
import csv
import time
sys.path.append("E:/Oishee/Thesis/system_c")

from system_a import SystemA
from system_b import SystemB
from system_c import SystemC


def load_case_list():
    with open("E:/Oishee/Thesis/experiment_cases.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


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
    print(f"\nRunning on {len(case_paths)} cases...\n")

    rows = []

    for idx, path in enumerate(case_paths, 1):
        case = sys_a.loader.load_case(path)
        fname = case["filename"]
        print(f"[{idx}/{len(case_paths)}] {fname}")

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