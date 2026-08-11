"""
constraint_checker.py
The core contribution: verifies each reasoning hop against clinical guidelines.
Makes every hop AUDITABLE / GUIDELINE-VERIFIABLE.
"""


class ConstraintChecker:
    def __init__(self, llm, knowledge_base):
        self.llm = llm
        self.kb = knowledge_base

    def check_hop(self, hop_claim, condition=None):
        """
        Verify a single reasoning hop against retrieved guidelines.
        Returns a verdict: SUPPORTED, PARTIAL, or UNSUPPORTED, with reasoning.
        """
        # Step 1: Retrieve the most relevant guideline for this claim
        chunks = self.kb.retrieve(hop_claim, n_results=2, condition=condition)
        guideline_text = self.kb.format_for_prompt(chunks)

        # Step 2: Ask the LLM to verify the claim ONLY against the guideline
        system_prompt = (
            "You are a clinical guideline auditor. Your ONLY job is to check whether "
            "a clinical claim is supported by the provided guideline text. "
            "Do NOT use outside knowledge beyond the guideline given. "
            "\n\n"
            "Judge the claim at the level of its clinical PRINCIPLE, not its wording. "
            "You are checking whether the claim's underlying clinical principle matches a "
            "principle in the guideline -- NOT whether the same words, drug names, or exact "
            "lab values appear verbatim. A claim can be fully supported even if it uses "
            "different terminology than the guideline.\n\n"
            "Treat a specific drug name, dose, or exact lab value in the claim as a valid "
            "INSTANTIATION (a concrete example) of a general principle in the guideline. If "
            "the guideline endorses the general category, then a specific example that falls "
            "within that category counts as SUPPORTED. For instance, if the guideline says to "
            "'monitor electrolytes and acid-base balance,' a claim about 'potassium repletion "
            "and bicarbonate replacement' is SUPPORTED because it instantiates that principle; "
            "if the guideline says to 'discontinue nephrotoxic agents,' a claim that names a "
            "specific nephrotoxic medication to stop or adjust is SUPPORTED.\n\n"
            "This applies to specific diagnoses and sub-types too. If the claim names a "
            "specific diagnosis or sub-type that clinically falls UNDER the general category "
            "the guideline covers, treat the guideline's general principle as applying to it "
            "-> SUPPORTED. For example, a specific form of acute kidney injury (such as "
            "crescentic glomerulonephritis) is still covered by general AKI staging and "
            "management guidelines, so the general principle applies to it. A specific lab "
            "value, drug, or sub-diagnosis that is a valid instance of the guideline's general "
            "category counts as SUPPORTED, not UNSUPPORTED.\n\n"
            "The following clinically related entities belong to the SAME guideline family, "
            "so a claim naming any member is covered when the retrieved guideline is for that "
            "family: atrial fibrillation and atrial flutter are both covered by the AFib "
            "guideline; sepsis, septic shock, bacteremia, and urosepsis are all covered by the "
            "sepsis guideline; CHF, HFrEF, HFpEF, cardiomyopathy, and decompensated heart "
            "failure are all covered by the heart_failure guideline; CAD, ACS, STEMI, NSTEMI, "
            "unstable angina, and MI are all covered by the cad_mi guideline; AKI, acute renal "
            "failure, and acute tubular necrosis (ATN) are all covered by the AKI guideline. If "
            "the reasoning names a specific entity within one of these families and the "
            "retrieved guideline is for that family, treat it as SUPPORTED (not UNSUPPORTED), "
            "provided the underlying claim still aligns with the guideline's principles.\n\n"
            "CONTRADICTION OVERRIDES FAMILY MATCH. Family membership only bridges terminology; "
            "it NEVER rescues a claim whose clinical content conflicts with the guideline. If a "
            "claim names an entity in the correct disease family but RECOMMENDS something the "
            "guideline advises against, or ASSERTS something the guideline explicitly rules out, "
            "that is a CONTRADICTION and the verdict is UNSUPPORTED -- even though the disease "
            "family matches. Decision rule: same family AND aligns with the principle -> "
            "SUPPORTED; same family BUT contradicts the principle -> UNSUPPORTED; a different "
            "disease entirely -> UNSUPPORTED.\n\n"
            "Use the three verdicts as follows:\n"
            "- SUPPORTED: the claim's clinical principle matches a principle in the guideline, "
            "even if expressed with different words, instantiated with specific examples, or "
            "naming a specific sub-type that falls under the guideline's general category.\n"
            "- PARTIAL: the claim is mostly aligned with the guideline, but it ALSO adds a "
            "specific assertion that the guideline neither supports nor contradicts.\n"
            "- UNSUPPORTED: use this in EITHER of two cases -- (1) the claim's core condition is "
            "genuinely a DIFFERENT disease category the guideline does not cover at all (e.g. a "
            "cardiac arrhythmia or drug overdose checked against an AKI or sepsis guideline); OR "
            "(2) the claim CONTRADICTS the guideline -- recommending something it advises against, "
            "or asserting something it explicitly rules out -- EVEN IF the condition is within the "
            "correct disease family. A same-family sub-type that ALIGNS with the guideline's "
            "principle is NOT UNSUPPORTED; a same-family claim that CONTRADICTS the principle IS "
            "UNSUPPORTED.\n\n"
            "Do not penalize a claim merely for being more specific than the guideline."
        )

        prompt = f"""GUIDELINE TEXT:
{guideline_text}

CLINICAL CLAIM TO VERIFY:
"{hop_claim}"

When deciding, ask: does the claim's clinical PRINCIPLE match a principle in the
guideline above? Specific drug names, doses, or exact lab values are valid concrete
examples of a general guideline principle, and a specific diagnosis or sub-type that
falls UNDER the guideline's general category is covered by that category -- in all these
cases the verdict is SUPPORTED. Use PARTIAL when the claim is mostly aligned but adds a
specific assertion the guideline neither supports nor contradicts. Use UNSUPPORTED ONLY
when the claim's core condition is a genuinely DIFFERENT disease category not covered by
the guideline (e.g. a cardiac arrhythmia vs. an AKI/sepsis guideline), OR when the claim
CONTRADICTS the guideline (recommends what it advises against, or asserts what it rules out)
even if the disease family matches.

Respond in EXACTLY this format:
VERDICT: [SUPPORTED / PARTIAL / UNSUPPORTED]
REASON: [one sentence explaining why, citing the guideline]"""

        response = self.llm.ask(prompt, system_prompt=system_prompt, temperature=0.1)

        # Step 3: Parse the verdict
        verdict = "UNKNOWN"
        reason = ""
        for line in response.split("\n"):
            if line.strip().startswith("VERDICT:"):
                verdict = line.replace("VERDICT:", "").strip()
            if line.strip().startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()

        return {
            "claim": hop_claim,
            "verdict": verdict,
            "reason": reason,
            "guidelines_used": [f"{c['condition']}/{c['hop']}" for c in chunks],
            "raw_response": response,
        }


# Quick test when run directly
if __name__ == "__main__":
    import sys
    sys.path.append("E:/Oishee/Thesis/system_c")
    from llm_connector import LLMConnector
    from knowledge_base import KnowledgeBase

    llm = LLMConnector()
    kb = KnowledgeBase()
    checker = ConstraintChecker(llm, kb)

    print("Testing constraint checker...\n")

    # Test 1: A claim that SHOULD be supported
    print("=" * 60)
    print("TEST 1: A correct claim")
    result = checker.check_hop(
        "A patient with qSOFA score of 2 (RR 24, confusion) is at high risk for sepsis.",
        condition="sepsis"
    )
    print(f"  Claim: {result['claim']}")
    print(f"  VERDICT: {result['verdict']}")
    print(f"  REASON: {result['reason']}")
    print(f"  Guidelines used: {result['guidelines_used']}")

    # Test 2: A claim that should be UNSUPPORTED / wrong
    print("\n" + "=" * 60)
    print("TEST 2: A WRONG claim (should be caught)")
    result = checker.check_hop(
        "A patient with a normal creatinine and good urine output has Stage 3 AKI.",
        condition="aki"
    )
    print(f"  Claim: {result['claim']}")
    print(f"  VERDICT: {result['verdict']}")
    print(f"  REASON: {result['reason']}")
    print(f"  Guidelines used: {result['guidelines_used']}")