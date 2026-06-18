"""
find_clean_cases.py
Finds cases that GENUINELY match each guideline condition by requiring
multiple co-occurring clinical signals AND excluding confounders
(lupus, overdose, etc). Much stricter than the earlier keyword counter.
"""
import sys
sys.path.append("E:/Oishee/Thesis/system_c")
from data_loader import DataLoader

loader = DataLoader()
cases = loader.list_cases()

# A case must hit signals from MULTIPLE groups to count as genuine.
profiles = {
    "sepsis": {
        "must_have_groups": [
            ["sepsis", "septic", "bacteremia"],          # the condition
            ["lactate", "blood culture", "wbc", "fever", "infection"],  # supporting
            ["antibiotic", "vasopressor", "fluid", "resuscitation"],    # management
        ],
        "exclude": ["overdose", "lupus", "chemotherapy", "lymphoma"],
    },
    "pneumonia": {
        "must_have_groups": [
            ["pneumonia"],                               # the condition
            ["infiltrate", "consolidation", "chest x-ray", "sputum", "cough"],  # imaging/resp
            ["antibiotic", "levofloxacin", "azithromycin", "ceftriaxone"],      # management
        ],
        "exclude": ["lupus", "overdose", "pneumonitis", "interstitial", "chemotherapy"],
    },
    "aki": {
        "must_have_groups": [
            ["acute kidney injury", "acute renal failure", "aki"],  # the condition
            ["creatinine", "bun", "urine output", "gfr"],           # labs
            ["dialysis", "fluid", "nephrotoxic", "hydration", "electrolyte"],  # management
        ],
        "exclude": ["chemotherapy", "lymphoma"],
    },
}

results = {"sepsis": [], "pneumonia": [], "aki": []}

for path in cases:
    case = loader.load_case(path)
    text = case["transcription"].lower()

    for cond, prof in profiles.items():
        # Skip if any confounder word is present
        if any(bad in text for bad in prof["exclude"]):
            continue
        # Require at least one hit from EACH group
        groups_hit = 0
        for group in prof["must_have_groups"]:
            if any(word in text for word in group):
                groups_hit += 1
        # Must hit all groups to count as genuine
        if groups_hit == len(prof["must_have_groups"]):
            # score = total keyword density for ranking
            score = sum(text.count(w) for group in prof["must_have_groups"] for w in group)
            results[cond].append((score, case["filename"]))

print("GENUINE cases (hit ALL signal groups, no confounders):\n")
selected = []
for cond in ["sepsis", "pneumonia", "aki"]:
    results[cond].sort(reverse=True)
    print(f"=== {cond.upper()} ({len(results[cond])} found) ===")
    for score, fname in results[cond][:6]:
        print(f"  (score {score}) {fname}")
    print()