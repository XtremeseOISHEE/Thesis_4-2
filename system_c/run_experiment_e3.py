"""
run_experiment_e3.py
E3: Hop ablation. Compares 1-hop, 2-hop, and 3-hop reasoning on the same
cases to test whether decomposing reasoning into more hops produces more
guideline-verifiable output.
"""
import sys
import csv
import time
sys.path.append("E:/Oishee/Thesis/system_c")

from data_loader import DataLoader
from llm_connector import LLMConnector
from knowledge_base import KnowledgeBase
from constraint_checker import ConstraintChecker

# Three hop configurations
HOP_CONFIGS = {
    "1-hop": [
        "Based on this patient case, state the diagnosis AND the recommended "
        "management together in 3-4 sentences."
    ],
    "2-hop": [
        "Based on the patient's presentation, what is the most likely primary "
        "condition? State reasoning in 2-3 sentences.",
        "Based on the confirmed condition, what is the recommended initial "
        "management? Be specific in 2-3 sentences.",
    ],
    "3-hop": [
        "Based on the patient's symptoms and presentation, what is the most "
        "likely primary condition? State reasoning in 2-3 sentences.",
        "Based on the labs, vitals, and clinical findings, what diagnostic "
        "criteria support or confirm this condition? Reference specific values.",
        "Based on the confirmed condition, what is the recommended initial "
        "management? Be specific in 2-3 sentences.",
    ],
}


def guess_condition(text):
    t = text.lower()
    if "sepsis" in t or "septic" in t:
        return "sepsis"
    if "kidney" in t or "creatinine" in t or "renal" in t or "aki" in t:
        return "aki"
    if "pneumonia" in t or "consolidation" in t:
        return "pneumonia"
    return None


def run_config(case_text, instructions, llm, kb, checker):
    """Run one hop configuration, return verdict counts."""
    accumulated = f"PATIENT CASE:\n{case_text[:2000]}\n\n"
    counts = {"SUPPORTED": 0, "PARTIAL": 0, "UNSUPPORTED": 0}

    for instr in instructions:
        hop_output = llm.ask(accumulated + "\n" + instr,
                             system_prompt="You are a clinical reasoning assistant.")
        cond = guess_condition(hop_output)
        check = checker.check_hop(hop_output, condition=cond)
        v = check["verdict"].upper()
        if v in counts:
            counts[v] += 1
        accumulated += f"\nConclusion: {hop_output}\n"

    return counts


if __name__ == "__main__":
    print("=" * 65)
    print("E3: HOP ABLATION (1-hop vs 2-hop vs 3-hop)")
    print("=" * 65)

    loader = DataLoader()
    llm = LLMConnector()
    kb = KnowledgeBase()
    checker = ConstraintChecker(llm, kb)

    # Use the 6 guideline-matched cases (in-scope) for a fair test
    with open("E:/Oishee/Thesis/experiment_cases.txt", "r", encoding="utf-8") as f:
        all_cases = [line.strip() for line in f if line.strip()]
    # Exclude the 3 out-of-scope cases
    out_of_scope = {"case_012", "case_034", "case_041"}
    cases = [c for c in all_cases if not any(o in c for o in out_of_scope)]

    print(f"\nRunning on {len(cases)} in-scope cases...\n")

    rows = []
    totals = {"1-hop": {"S": 0, "P": 0, "U": 0},
              "2-hop": {"S": 0, "P": 0, "U": 0},
              "3-hop": {"S": 0, "P": 0, "U": 0}}

    for idx, path in enumerate(cases, 1):
        case = loader.load_case(path)
        fname = case["filename"]
        case_text = case["transcription"] if case["transcription"] else case["full_text"]
        print(f"[{idx}/{len(cases)}] {fname[:45]}")

        row = {"case": fname}
        for config_name, instructions in HOP_CONFIGS.items():
            counts = run_config(case_text, instructions, llm, kb, checker)
            row[f"{config_name}_S"] = counts["SUPPORTED"]
            row[f"{config_name}_P"] = counts["PARTIAL"]
            row[f"{config_name}_U"] = counts["UNSUPPORTED"]
            totals[config_name]["S"] += counts["SUPPORTED"]
            totals[config_name]["P"] += counts["PARTIAL"]
            totals[config_name]["U"] += counts["UNSUPPORTED"]
            print(f"    {config_name}: S:{counts['SUPPORTED']} P:{counts['PARTIAL']} U:{counts['UNSUPPORTED']}")
        rows.append(row)
        time.sleep(2)
        print()

    # Save CSV
    with open("E:/Oishee/Thesis/results_e3.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 65)
    print("E3 COMPLETE. Saved to results_e3.csv\n")
    print("TOTALS (across all in-scope cases):")
    for config_name in ["1-hop", "2-hop", "3-hop"]:
        t = totals[config_name]
        total_hops = t["S"] + t["P"] + t["U"]
        verifiable = t["S"] + t["P"]
        pct = 100 * verifiable / total_hops if total_hops else 0
        print(f"  {config_name}: {t['S']} SUPPORTED, {t['P']} PARTIAL, {t['U']} UNSUPPORTED"
              f"  -> verifiable {verifiable}/{total_hops} = {pct:.0f}%")
    print("=" * 65)