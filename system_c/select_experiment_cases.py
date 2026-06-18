"""
Selects content-verified cases (balanced across sepsis/pneumonia/aki)
for the E1 experiment. Removes duplicates. Saves the list to a file.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from data_loader import DataLoader

loader = DataLoader()
cases = loader.list_cases()

indicators = {
    "sepsis": ["sepsis", "septic", "lactate", "blood culture", "sofa", "vasopressor"],
    "pneumonia": ["pneumonia", "consolidation", "infiltrate", "sputum", "chest x-ray"],
    "aki": ["acute kidney injury", "acute renal failure", "creatinine", "dialysis", "kdigo", "nephro"],
}

scored = {"sepsis": [], "pneumonia": [], "aki": []}

for path in cases:
    case = loader.load_case(path)
    text = case["transcription"].lower()
    for cond, words in indicators.items():
        score = sum(text.count(w) for w in words)
        if score >= 2:  # softened from 3 to 2
            scored[cond].append((score, path))

# Build a balanced, DEDUPLICATED selection
selected = []
seen = set()  # track filenames already chosen

for cond in ["sepsis", "pneumonia", "aki"]:
    scored[cond].sort(reverse=True)
    print(f"\n=== {cond.upper()} candidates ===")
    count = 0
    for score, path in scored[cond]:
        fname = path.split("/")[-1].split("\\")[-1]
        if fname in seen:
            continue  # skip duplicates
        if count >= 4:
            break  # max 4 per condition
        print(f"  (score {score}) {fname}")
        selected.append(path)
        seen.add(fname)
        count += 1

with open("E:/Oishee/Thesis/experiment_cases.txt", "w", encoding="utf-8") as f:
    for path in selected:
        f.write(path + "\n")

print(f"\n\nTotal UNIQUE cases selected: {len(selected)}")
print("Saved list to: E:/Oishee/Thesis/experiment_cases.txt")