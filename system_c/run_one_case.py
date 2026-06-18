"""
run_one_case.py
Runs System C on a single well-matched case and prints a clean,
defense-ready reasoning trace.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")

from system_c import SystemC


def print_trace(result):
    """Pretty-print the full reasoning trace."""
    print("\n" + "#" * 70)
    print(f"#  CASE: {result['filename']}")
    print(f"#  Labeled condition: {result['labeled_condition']}")
    print("#" * 70)

    for step in result["trace"]:
        verdict = step["verdict"].upper()
        # Visual marker for verdict
        mark = {"SUPPORTED": "[OK]", "PARTIAL": "[~]",
                "UNSUPPORTED": "[X]", "UNKNOWN": "[?]"}.get(verdict, "[?]")

        print("\n" + "=" * 70)
        print(f"  {step['hop_name']}")
        print("=" * 70)
        print(f"  REASONING:")
        print(f"    {step['reasoning']}")
        print(f"\n  VERIFICATION {mark} {verdict}")
        print(f"    {step['verification_reason']}")
        print(f"    Guidelines checked: {step['guidelines_used']}")

    print("\n" + "#" * 70)
    print("  FINAL CONCLUSION:")
    print(f"    {result['final_summary']}")
    print("#" * 70)


if __name__ == "__main__":
    system = SystemC()

    # Directly use a verified genuine case (sepsis + AKI together)
    case_path = "E:/Oishee/Thesis/cases/case_056_SEPSIS_AKI_Nephrology.txt"
    case = system.loader.load_case(case_path)

    print(f"Selected case: {case['filename']}")
    print("Running System C (this makes ~7 API calls, please wait)...\n")

    result = system.analyze_case(case)
    print_trace(result)