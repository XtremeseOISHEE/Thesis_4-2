"""
inspect_verdicts.py
Diagnostic: shows WHY System C gives its verdicts on a few cases,
so we can decide how to tune the verifier.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from system_c import SystemC

system = SystemC()

# Look at 3 representative cases: one pneumonia, one sepsis+aki, one strong aki
inspect = [
    "E:/Oishee/Thesis/cases/case_005_PNEUMONIA_SOAP___Chart___Progress_Notes.txt",  # all UNSUPPORTED
    "E:/Oishee/Thesis/cases/case_056_SEPSIS_AKI_Nephrology.txt",                    # mixed
    "E:/Oishee/Thesis/cases/case_051_AKI_Nephrology.txt",                          # strong AKI
]

for path in inspect:
    case = system.loader.load_case(path)
    print("\n" + "#" * 70)
    print(f"# CASE: {case['filename']}")
    print(f"# Labeled: {case['condition']}")
    print("#" * 70)

    result = system.analyze_case(case)
    for step in result["trace"]:
        print(f"\n--- {step['hop_name']} ---")
        print(f"VERDICT: {step['verdict']}")
        print(f"GUIDELINES PULLED: {step['guidelines_used']}")
        print(f"WHY: {step['verification_reason']}")
        # Show first 200 chars of what the hop actually claimed
        print(f"CLAIM (start): {step['reasoning'][:200]}...")