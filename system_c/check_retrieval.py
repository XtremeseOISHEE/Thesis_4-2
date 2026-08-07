import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from system_c import SystemC

system = SystemC()

# case_051 (strong AKI) — should pull AKI guidelines, let's see what happens
case = system.loader.load_case("E:/Oishee/Thesis/cases/case_051_AKI_Nephrology.txt")
print("CASE: case_051 (strong AKI)\n")

result = system.analyze_case(case)
for step in result["trace"]:
    print(f"{step['hop_name']}: {step['verdict']}")
    print(f"  reasoning mentions: {step['reasoning'][:80]}")
    print(f"  guidelines pulled: {step['guidelines_used']}")
    print()