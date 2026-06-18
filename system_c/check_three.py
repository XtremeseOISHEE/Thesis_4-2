import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from system_c import SystemC

system = SystemC()

cases_to_check = [
    "case_012_SEPSIS_AKI_SOAP___Chart___Progress_Notes.txt",
    "case_034_PNEUMONIA_AKI_SOAP___Chart___Progress_Notes.txt",
    "case_041_AKI_SOAP___Chart___Progress_Notes.txt",
]

for fname in cases_to_check:
    case = system.loader.load_case(f"E:/Oishee/Thesis/cases/{fname}")
    print("\n" + "#"*65)
    print(f"# {fname}")
    print("#"*65)
    print("CONTENT (first 350 chars):")
    print(case["transcription"][:350])
    print("\nVERDICTS:")
    result = system.analyze_case(case)
    for step in result["trace"]:
        print(f"  {step['hop_name']}: {step['verdict']} | guidelines: {step['guidelines_used']}")
        print(f"     why: {step['verification_reason'][:150]}")