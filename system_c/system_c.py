"""
system_c.py
System C: The full multi-hop, constraint-guided clinical reasoning system.
This is the complete pipeline that ties all components together.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")

from data_loader import DataLoader
from llm_connector import LLMConnector
from knowledge_base import KnowledgeBase
from constraint_checker import ConstraintChecker
from multihop_reasoner import MultiHopReasoner


class SystemC:
    """Full system: multi-hop reasoning + per-hop guideline verification."""

    def __init__(self):
        print("Initializing System C...")
        self.loader = DataLoader()
        self.llm = LLMConnector()
        self.kb = KnowledgeBase()
        self.checker = ConstraintChecker(self.llm, self.kb)
        self.reasoner = MultiHopReasoner(self.llm, self.kb, self.checker)
        print("System C ready.\n")

    def analyze_case(self, case):
        """Run full reasoning on a single loaded case dict."""
        case_text = case["transcription"] if case["transcription"] else case["full_text"]
        trace = self.reasoner.reason(case_text)

        # Build a final summary diagnosis from the trace
        final_summary = self._summarize(trace)

        return {
            "filename": case["filename"],
            "labeled_condition": case["condition"],
            "trace": trace,
            "final_summary": final_summary,
        }

    def _summarize(self, trace):
        """Ask the LLM for a final concise conclusion from the full trace."""
        chain = "\n".join(
            f"{step['hop_name']}: {step['reasoning']}" for step in trace
        )
        prompt = (
            f"Based on this clinical reasoning chain, give a ONE-sentence final "
            f"diagnosis and primary recommendation:\n\n{chain}"
        )
        return self.llm.ask(prompt, temperature=0.1)

    def count_verdicts(self, trace):
        """Helper: tally verdicts for quick metrics."""
        counts = {"SUPPORTED": 0, "PARTIAL": 0, "UNSUPPORTED": 0, "UNKNOWN": 0}
        for step in trace:
            v = step["verdict"].upper()
            counts[v] = counts.get(v, 0) + 1
        return counts


# Quick test when run directly
if __name__ == "__main__":
    system = SystemC()

    # Load the first case from the dataset
    cases = system.loader.list_cases()
    case = system.loader.load_case(cases[0])

    print(f"Analyzing: {case['filename']}")
    print(f"Labeled condition: {case['condition']}\n")

    result = system.analyze_case(case)

    print("FINAL SUMMARY:")
    print(f"  {result['final_summary']}\n")
    print("VERDICT COUNTS:")
    print(f"  {system.count_verdicts(result['trace'])}")