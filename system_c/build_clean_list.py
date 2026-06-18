"""
build_clean_list.py
Builds the final deduplicated experiment case list (sepsis + AKI only).
Saves to experiment_cases.txt for E1.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from data_loader import DataLoader

loader = DataLoader()
cases = loader.list_cases()

profiles = {
    "sepsis": {
        "must_have_groups": [
            ["sepsis", "septic", "bacteremia"],
            ["lactate", "blood culture", "wbc", "fever", "infection"],
            ["antibiotic", "vasopressor", "fluid", "resuscitation"],
        ],
        "exclude": ["overdose", "lupus", "chemotherapy", "lymphoma"],
    },
    "aki": {
        "must_have_groups": [
            ["acute kidney injury", "acute renal failure", "aki"],
            ["creatinine", "bun", "urine output", "gfr"],
            ["dialysis", "fluid", "nephrotoxic", "hydration", "electrolyte"],
        ],
        "exclude": ["chemotherapy", "lymphoma"],
    },
}

results = {"sepsis": [], "aki": []}

for path in cases:
    case = loader.load_case(path)
    text = case["transcription"].lower()
    for cond, prof in profiles.items():
        if any(bad in text for bad in prof["exclude"]):
            continue
        groups_hit = sum(
            1 for group in prof["must_have_groups"]
            if any(word in text for word in group)
        )
        if groups_hit == len(prof["must_have_groups"]):
            score = sum(text.count(w) for group in prof["must_have_groups"] for w in group)
            results[cond].append((score, path))

# Build deduplicated final list
selected = []
seen = set()

for cond in ["sepsis", "aki"]:
    results[cond].sort(reverse=True)
    print(f"=== {cond.upper()} ===")
    count = 0
    for score, path in results[cond]:
        fname = path.split("/")[-1].split("\\")[-1]
        if fname in seen:
            continue
        if count >= 6:  # up to 6 per condition
            break
        print(f"  (score {score}) {fname}")
        selected.append(path)
        seen.add(fname)
        count += 1
    print()

with open("E:/Oishee/Thesis/experiment_cases.txt", "w", encoding="utf-8") as f:
    for path in selected:
        f.write(path + "\n")

print(f"Total UNIQUE cases: {len(selected)}")
print("Saved to: E:/Oishee/Thesis/experiment_cases.txt")