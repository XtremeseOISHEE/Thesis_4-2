"""
build_human_eval.py
Generates blind A-vs-C comparison material for human evaluation.
For each case, produces System A output and System C output, labeled
neutrally as "Output 1" and "Output 2" (randomized) so raters are blind.
Saves a ready-to-paste file for the Google Form.
"""
import sys
import random
random.seed(42) 
sys.path.append("E:/Oishee/Thesis/system_c")

from system_a import SystemA
from system_c import SystemC

CASES = [
    "case_049_SEPSIS_PNEUMONIA_AKI_Nephrology.txt",
    "case_051_AKI_Nephrology.txt",
    "case_056_SEPSIS_AKI_Nephrology.txt",
    "case_024_SEPSIS_SOAP___Chart___Progress_Notes.txt",
    "case_012_SEPSIS_AKI_SOAP___Chart___Progress_Notes.txt",
]


def format_c_trace(trace):
    """Format System C trace with its verifications, as readable text."""
    lines = []
    for step in trace:
        v = step["verdict"].upper()
        lines.append(f"  Step - {step['hop_name']}:")
        lines.append(f"    Reasoning: {step['reasoning']}")
        lines.append(f"    [Guideline check: {v}] {step['verification_reason']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys_a = SystemA()
    sys_c = SystemC()

    report = []
    answer_key = []  # secret: which output is A and which is C

    for i, fname in enumerate(CASES, 1):
        case = sys_a.loader.load_case(f"E:/Oishee/Thesis/cases/{fname}")
        print(f"Processing case {i}: {fname[:45]}")

        ra = sys_a.analyze_case(case)
        rc = sys_c.analyze_case(case)

        a_text = ra["output"]
        c_text = format_c_trace(rc["trace"])

        # Randomize which is shown first (blind)
        if random.random() < 0.5:
            out1, out2 = a_text, c_text
            key = "Output 1 = System A, Output 2 = System C"
        else:
            out1, out2 = c_text, a_text
            key = "Output 1 = System C, Output 2 = System A"

        report.append("#" * 70)
        report.append(f"CASE {i}")
        report.append("#" * 70)
        report.append("\nPATIENT SUMMARY:")
        report.append(case["description"][:300])
        report.append("\n" + "-" * 50)
        report.append("OUTPUT 1:")
        report.append("-" * 50)
        report.append(out1)
        report.append("\n" + "-" * 50)
        report.append("OUTPUT 2:")
        report.append("-" * 50)
        report.append(out2)
        report.append("\n")

        answer_key.append(f"CASE {i}: {key}")

    # Save the form content
    with open("E:/Oishee/Thesis/human_eval_content.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    # Save the SECRET answer key separately (do not share with raters)
    with open("E:/Oishee/Thesis/human_eval_ANSWER_KEY.txt", "w", encoding="utf-8") as f:
        f.write("SECRET ANSWER KEY - do NOT share with raters\n")
        f.write("=" * 50 + "\n")
        f.write("\n".join(answer_key))

    print("\n" + "=" * 60)
    print("DONE. Two files created:")
    print("  human_eval_content.txt    -> paste into Google Form")
    print("  human_eval_ANSWER_KEY.txt -> KEEP SECRET (for scoring)")
    print("=" * 60)