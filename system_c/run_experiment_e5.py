"""
run_experiment_e5.py
E5: Error analysis. Categorizes WHERE and WHY System C produces
non-SUPPORTED verdicts, by re-running the in-scope cases and classifying
each hop's verdict + reason into error categories.
"""
import sys
import csv
import time
sys.path.append("E:/Oishee/Thesis/system_c")

from system_c import SystemC

# In-scope cases (genuine sepsis/aki) and out-of-scope cases
IN_SCOPE = [
    "case_057_SEPSIS_AKI_Nephrology.txt",
    "case_024_SEPSIS_SOAP___Chart___Progress_Notes.txt",
    "case_051_AKI_Nephrology.txt",
    "case_056_SEPSIS_AKI_Nephrology.txt",
    "case_049_SEPSIS_PNEUMONIA_AKI_Nephrology.txt",
    "case_035_AKI_SOAP___Chart___Progress_Notes.txt",
]
OUT_OF_SCOPE = [
    "case_012_SEPSIS_AKI_SOAP___Chart___Progress_Notes.txt",
    "case_034_PNEUMONIA_AKI_SOAP___Chart___Progress_Notes.txt",
    "case_041_AKI_SOAP___Chart___Progress_Notes.txt",
]


def categorize(verdict, reason):
    """Classify a non-supported verdict into an error category."""
    r = reason.lower()
    if verdict == "SUPPORTED":
        return "verified_ok"
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

    all_cases = [(c, "in_scope") for c in IN_SCOPE] + \
                [(c, "out_of_scope") for c in OUT_OF_SCOPE]

    for fname, scope in all_cases:
        case = system.loader.load_case(f"E:/Oishee/Thesis/cases/{fname}")
        print(f"\nAnalyzing [{scope}]: {fname[:45]}")
        result = system.analyze_case(case)

        for step in result["trace"]:
            verdict = step["verdict"].upper()
            hop_key = step["hop_name"].split(":")[0]  # "Hop 1"

            # Tally by hop position
            short = {"SUPPORTED": "S", "PARTIAL": "P", "UNSUPPORTED": "U"}.get(verdict, "U")
            if hop_key in hop_errors:
                hop_errors[hop_key][short] += 1

            # Categorize
            cat = categorize(verdict, step["verification_reason"])
            categories[cat] = categories.get(cat, 0) + 1

            print(f"    {hop_key}: {verdict} -> {cat}")

            rows.append({
                "case": fname,
                "scope": scope,
                "hop": hop_key,
                "verdict": verdict,
                "category": cat,
            })

        # Pause between cases to stay under Groq's tokens-per-minute rate limit
        time.sleep(15)

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