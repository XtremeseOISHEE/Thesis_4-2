"""
system_a.py
System A (Baseline): Single-shot LLM diagnosis.
No multi-hop reasoning, no guideline retrieval, no constraint checking.
This is the simplest baseline — just ask the LLM directly.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")

from data_loader import DataLoader
from llm_connector import LLMConnector


class SystemA:
    """Baseline: one LLM call, no guidelines, no hops, no verification."""

    def __init__(self):
        print("Initializing System A (baseline)...")
        self.loader = DataLoader()
        self.llm = LLMConnector()
        print("System A ready.\n")

    def analyze_case(self, case):
        case_text = case["transcription"] if case["transcription"] else case["full_text"]

        system_prompt = ("You are a clinical reasoning assistant. "
                         "Read the case and give a diagnosis and recommendation.")
        prompt = (
            f"PATIENT CASE:\n{case_text[:2000]}\n\n"
            f"Provide: (1) the most likely diagnosis, and "
            f"(2) the recommended initial management. Keep it concise."
        )

        answer = self.llm.ask(prompt, system_prompt=system_prompt, temperature=0.2)

        return {
            "filename": case["filename"],
            "labeled_condition": case["condition"],
            "system": "A",
            "output": answer,
            "trace": [],          # no hops
            "guidelines_used": [],  # no guidelines
            "verdicts": {},        # no verification
        }


# Quick test
if __name__ == "__main__":
    system = SystemA()
    case_path = "E:/Oishee/Thesis/cases/case_056_SEPSIS_AKI_Nephrology.txt"
    case = system.loader.load_case(case_path)

    print(f"Analyzing: {case['filename']}\n")
    result = system.analyze_case(case)

    print("=" * 65)
    print("SYSTEM A OUTPUT (single-shot, no guidelines, no verification):")
    print("=" * 65)
    print(result["output"])
    print("=" * 65)