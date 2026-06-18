"""
system_b.py
System B (Ablation baseline): Multi-hop reasoning WITH guideline retrieval,
but WITHOUT constraint checking / verification.
This isolates the contribution of the constraint checker (the only thing
System C adds on top of System B).
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")

from data_loader import DataLoader
from llm_connector import LLMConnector
from knowledge_base import KnowledgeBase


class SystemB:
    """Multi-hop + guidelines, but NO verification of each hop."""

    def __init__(self):
        print("Initializing System B (guidelines, no verification)...")
        self.loader = DataLoader()
        self.llm = LLMConnector()
        self.kb = KnowledgeBase()
        print("System B ready.\n")

        self.hops = [
            {
                "name": "Hop 1: Identification",
                "instruction": "Based on the patient's symptoms and presentation, "
                               "what is the most likely primary condition? "
                               "State your reasoning in 2-3 sentences."
            },
            {
                "name": "Hop 2: Diagnostic Confirmation",
                "instruction": "Based on the labs, vitals, and clinical findings, "
                               "what diagnostic criteria support or confirm this condition? "
                               "Reference specific values in 2-3 sentences."
            },
            {
                "name": "Hop 3: Management",
                "instruction": "Based on the confirmed condition, what is the recommended "
                               "initial management or treatment approach? Be specific in 2-3 sentences."
            },
        ]

    def _guess_condition(self, text):
        text_low = text.lower()
        if "sepsis" in text_low or "septic" in text_low:
            return "sepsis"
        if "pneumonia" in text_low or "consolidation" in text_low:
            return "pneumonia"
        if "kidney" in text_low or "creatinine" in text_low or "renal" in text_low or "aki" in text_low:
            return "aki"
        return None

    def analyze_case(self, case):
        case_text = case["transcription"] if case["transcription"] else case["full_text"]
        trace = []
        accumulated = f"PATIENT CASE:\n{case_text[:2000]}\n\n"

        for hop in self.hops:
            # Retrieve guideline to ENRICH the prompt (but no verification after)
            condition_hint = self._guess_condition(case_text)
            chunks = self.kb.retrieve(hop["instruction"], n_results=2, condition=condition_hint)
            guideline_text = self.kb.format_for_prompt(chunks)

            prompt = (accumulated +
                      f"\nRelevant clinical guidelines:\n{guideline_text}\n\n"
                      f"{hop['instruction']}")
            system_prompt = ("You are a clinical reasoning assistant working step by step. "
                             "Use the provided guidelines to inform your reasoning.")
            hop_output = self.llm.ask(prompt, system_prompt=system_prompt)

            # NOTE: No constraint check here — that's what makes this System B
            trace.append({
                "hop_name": hop["name"],
                "reasoning": hop_output,
                "guidelines_used": [f"{c['condition']}/{c['hop']}" for c in chunks],
                # no verdict, no verification_reason
            })

            accumulated += f"\n{hop['name']} conclusion: {hop_output}\n"

        return {
            "filename": case["filename"],
            "labeled_condition": case["condition"],
            "system": "B",
            "trace": trace,
        }


# Quick test
if __name__ == "__main__":
    system = SystemB()
    case_path = "E:/Oishee/Thesis/cases/case_056_SEPSIS_AKI_Nephrology.txt"
    case = system.loader.load_case(case_path)

    print(f"Analyzing: {case['filename']}\n")
    result = system.analyze_case(case)

    for step in result["trace"]:
        print("=" * 65)
        print(f"  {step['hop_name']}")
        print("=" * 65)
        print(f"  REASONING: {step['reasoning']}")
        print(f"  Guidelines used: {step['guidelines_used']}")
        print(f"  (NO verification — this is System B)\n")