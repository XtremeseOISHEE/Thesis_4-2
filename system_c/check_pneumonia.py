import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from system_c import SystemC

system = SystemC()
case = system.loader.load_case("E:/Oishee/Thesis/cases/case_007_PNEUMONIA_SOAP___Chart___Progress_Notes.txt")

print("CASE CONTENT (first 400 chars):")
print(case["transcription"][:400])
print("\n" + "="*60)

result = system.analyze_case(case)
for step in result["trace"]:
    print(f"\n{step['hop_name']}: {step['verdict']}")
    print(f"  Guidelines pulled: {step['guidelines_used']}")