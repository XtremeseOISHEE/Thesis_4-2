"""
run_experiment_e4.py
E4: Showcase trace. Runs all three systems (A, B, C) on ONE strong case
and produces a clean side-by-side comparison for the defense presentation.
Saves a readable text report.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")

from system_a import SystemA
from system_b import SystemB
from system_c import SystemC

# The showcase case (CAD_MI, scored 3/0/0 = all SUPPORTED in E1)
SHOWCASE = "E:/Oishee/Thesis/cases_v2/case_4915_CAD_MI__Cardiovascular___Pulmonary.txt"


def section(title):
    return "\n" + "=" * 70 + f"\n  {title}\n" + "=" * 70


if __name__ == "__main__":
    print("=" * 70)
    print("E4: SHOWCASE TRACE (Systems A vs B vs C on one case)")
    print("=" * 70)

    sys_a = SystemA()
    sys_b = SystemB()
    sys_c = SystemC()

    case = sys_a.loader.load_case(SHOWCASE)

    report = []
    report.append("#" * 70)
    report.append(f"# E4 SHOWCASE: {case['filename']}")
    report.append(f"# Labeled condition: {case['condition']}")
    report.append("#" * 70)
    report.append("\nPATIENT CASE (excerpt):")
    report.append(case["transcription"][:500] + "...")

    # --- System A ---
    print("\nRunning System A...")
    ra = sys_a.analyze_case(case)
    report.append(section("SYSTEM A: Single-shot (no guidelines, no verification)"))
    report.append(ra["output"])

    # --- System B ---
    print("Running System B...")
    rb = sys_b.analyze_case(case)
    report.append(section("SYSTEM B: Multi-hop + guidelines (NO verification)"))
    for step in rb["trace"]:
        report.append(f"\n[{step['hop_name']}]")
        report.append(step["reasoning"])
        report.append(f"(guidelines retrieved: {step['guidelines_used']} -- but NOT verified)")

    # --- System C ---
    print("Running System C...")
    rc = sys_c.analyze_case(case)
    report.append(section("SYSTEM C: Multi-hop + guidelines + VERIFICATION (full system)"))
    for step in rc["trace"]:
        v = step["verdict"].upper()
        mark = {"SUPPORTED": "[OK]", "PARTIAL": "[~]", "UNSUPPORTED": "[X]"}.get(v, "[?]")
        report.append(f"\n[{step['hop_name']}]")
        report.append(step["reasoning"])
        report.append(f"  VERIFICATION {mark} {v}")
        report.append(f"  WHY: {step['verification_reason']}")
        report.append(f"  Guidelines checked: {step['guidelines_used']}")

    # Key takeaway
    report.append(section("KEY TAKEAWAY"))
    report.append("System A: gives an answer, but you cannot audit it against any guideline.")
    report.append("System B: uses guidelines to reason, but never checks if it stayed faithful.")
    report.append("System C: every hop is explicitly verified against a clinical guideline,")
    report.append("          making the entire reasoning chain auditable.")

    # Write to file
    full_report = "\n".join(report)
    out_path = "E:/Oishee/Thesis/E4_showcase_trace.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_report)

    print("\n" + "=" * 70)
    print(f"E4 COMPLETE. Full showcase trace saved to:\n  {out_path}")
    print("=" * 70)
    print("\nThis file is your defense centerpiece -- it shows all three")
    print("systems side-by-side on the same case.")