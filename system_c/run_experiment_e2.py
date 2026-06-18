"""
run_experiment_e2.py
E2: Tests whether the constraint checker actually DISCRIMINATES between
correct and incorrect clinical claims (not just rubber-stamps everything).
Uses hand-crafted claims with known ground truth.
"""
import sys
import csv
sys.path.append("E:/Oishee/Thesis/system_c")

from llm_connector import LLMConnector
from knowledge_base import KnowledgeBase
from constraint_checker import ConstraintChecker

# Hand-crafted test claims with KNOWN ground truth.
# "correct" = guideline-aligned (should be SUPPORTED)
# "incorrect" = guideline-violating (should be UNSUPPORTED)
test_claims = [
    # --- SEPSIS ---
    {"condition": "sepsis", "truth": "correct",
     "claim": "A patient with qSOFA score of 2 (respiratory rate 24, confusion) is at higher risk for sepsis."},
    {"condition": "sepsis", "truth": "incorrect",
     "claim": "A fully alert patient with normal vitals and no infection meets criteria for septic shock."},
    {"condition": "sepsis", "truth": "correct",
     "claim": "Septic shock requires vasopressors to maintain MAP 65 and lactate above 2 despite fluids."},
    {"condition": "sepsis", "truth": "incorrect",
     "claim": "Sepsis is diagnosed solely by a single elevated temperature with no organ dysfunction."},

    # --- AKI ---
    {"condition": "aki", "truth": "correct",
     "claim": "A creatinine rise from 1.0 to 2.5 with low urine output indicates acute kidney injury."},
    {"condition": "aki", "truth": "incorrect",
     "claim": "A patient with normal creatinine and good urine output has Stage 3 AKI."},
    {"condition": "aki", "truth": "correct",
     "claim": "Management of AKI includes discontinuing nephrotoxic agents and optimizing volume status."},
    {"condition": "aki", "truth": "incorrect",
     "claim": "The first-line treatment for AKI is immediate antibiotics regardless of cause."},
]

if __name__ == "__main__":
    print("=" * 65)
    print("E2: CONSTRAINT CHECKER DISCRIMINATION TEST")
    print("=" * 65)

    llm = LLMConnector()
    kb = KnowledgeBase()
    checker = ConstraintChecker(llm, kb)

    rows = []
    correct_calls = 0

    for i, t in enumerate(test_claims, 1):
        result = checker.check_hop(t["claim"], condition=t["condition"])
        verdict = result["verdict"].upper()

        # Does the verdict match ground truth?
        # correct claim -> expect SUPPORTED (or PARTIAL)
        # incorrect claim -> expect UNSUPPORTED
        if t["truth"] == "correct":
            matched = verdict in ("SUPPORTED", "PARTIAL")
        else:
            matched = verdict == "UNSUPPORTED"

        if matched:
            correct_calls += 1

        mark = "OK" if matched else "MISS"
        print(f"\n[{i}] {t['condition'].upper()} | ground truth: {t['truth']}")
        print(f"    Claim: {t['claim'][:70]}...")
        print(f"    Verdict: {verdict}  [{mark}]")

        rows.append({
            "condition": t["condition"],
            "ground_truth": t["truth"],
            "verdict": verdict,
            "matched": matched,
        })

    # Save CSV
    with open("E:/Oishee/Thesis/results_e2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    accuracy = 100 * correct_calls / len(test_claims)
    print("\n" + "=" * 65)
    print(f"E2 COMPLETE. Saved to results_e2.csv")
    print(f"Discrimination accuracy: {correct_calls}/{len(test_claims)} = {accuracy:.0f}%")
    print("=" * 65)
    print("\nIf accuracy is high, the constraint checker genuinely")
    print("distinguishes valid reasoning from invalid -- it is not a rubber stamp.")