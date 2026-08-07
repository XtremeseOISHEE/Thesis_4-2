import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from system_c import SystemC

system = SystemC()

# case_057 — got 3-hop U:3 (all unsupported), let's see why
case = system.loader.load_case("E:/Oishee/Thesis/cases/case_057_SEPSIS_AKI_Nephrology.txt")
print("CASE: case_057 (3-hop gave all UNSUPPORTED)\n")

result = system.analyze_case(case)
for step in result["trace"]:
    print(f"{step['hop_name']}: {step['verdict']}")
    print(f"  guidelines pulled: {step['guidelines_used']}")
    print(f"  reasoning: {step['reasoning'][:120]}")
    print(f"  why: {step['verification_reason'][:130]}")
    print()