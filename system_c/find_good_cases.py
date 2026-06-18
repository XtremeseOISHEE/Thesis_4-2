import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from data_loader import DataLoader

loader = DataLoader()
cases = loader.list_cases()

# Strong indicator phrases for genuine cases
indicators = {
    "sepsis": ["sepsis", "septic shock", "lactate", "blood culture", "sofa"],
    "pneumonia": ["pneumonia", "consolidation", "infiltrate", "sputum", "chest x-ray"],
    "aki": ["acute kidney injury", "acute renal failure", "creatinine", "dialysis", "kdigo"],
}

print("Scanning cases for genuine condition content...\n")

good = {"sepsis": [], "pneumonia": [], "aki": []}

for path in cases:
    case = loader.load_case(path)
    text = case["transcription"].lower()
    for cond, words in indicators.items():
        score = sum(text.count(w) for w in words)
        if score >= 3:  # needs multiple mentions to count as genuine
            good[cond].append((score, case["filename"]))

for cond in good:
    good[cond].sort(reverse=True)
    print(f"=== Best {cond.upper()} cases ===")
    for score, fname in good[cond][:5]:
        print(f"  (score {score}) {fname}")
    print()