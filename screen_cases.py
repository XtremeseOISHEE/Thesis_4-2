"""
screen_cases.py
Automated screening of MTSamples to find genuine, guideline-verifiable cases
for six conditions: sepsis, AKI, pneumonia, heart failure, atrial fibrillation,
and coronary artery disease / MI.

METHOD (semi-automated screening — standard for noisy clinical corpora):
  For each note we require, per condition:
    1. CONDITION signal  — the disease is actually named
    2. EVIDENCE signals  — at least MIN_EVIDENCE supporting findings/labs
    3. MANAGEMENT signal  — a treatment consistent with the condition
    4. NO CONFOUNDER      — exclusion terms that usually indicate a different
                            primary disease (overdose, lymphoma, cancer, etc.)
  A note passing all four is a CANDIDATE. We also score it (signal density)
  and rank candidates so the strongest rise to the top. The human then does a
  final read of the ranked list (the filenames/descriptions are printed) to
  confirm — because filename/keyword alone is unreliable in MTSamples.

Run:  python screen_cases.py
Output: screened_candidates.csv  (ranked, per condition)
"""
import pandas as pd
import re

CSV_PATH = "mtsamples.csv"          # PC: "E:/Oishee/Thesis/mtsamples.csv"
MIN_EVIDENCE = 2                     # how many evidence signals required
OUT = "screened_candidates.csv"

# Disease definitions. Word-boundary matching avoids false hits
# (e.g. ' pe ' won't match 'type').
PROFILES = {
    "sepsis": {
        "condition": [r"sepsis", r"septic shock", r"septicemia", r"bacteremia", r"urosepsis"],
        "evidence":  [r"lactate", r"blood culture", r"wbc", r"leukocytosis", r"fever",
                      r"temperature", r"hypotension", r"tachycardia", r"septic workup"],
        "mgmt":      [r"antibiotic", r"vasopressor", r"levophed", r"norepinephrine",
                      r"fluid resuscitation", r"broad-spectrum", r"cultures"],
        "exclude":   [r"overdose", r"lupus", r"chemotherapy", r"lymphoma"],
    },
    "aki": {
        "condition": [r"acute kidney injury", r"acute renal failure",
                      r"acute renal insufficiency", r"\baki\b", r"\barf\b"],
        "evidence":  [r"creatinine", r"\bbun\b", r"urine output", r"oliguria",
                      r"\bgfr\b", r"anuria", r"azotemia", r"dialysis"],
        "mgmt":      [r"dialysis", r"fluid", r"nephrotoxic", r"hydration",
                      r"electrolyte", r"renal replacement", r"hemodialysis"],
        "exclude":   [r"chemotherapy", r"lymphoma", r"overdose"],
    },
    "pneumonia": {
        "condition": [r"pneumonia"],
        "evidence":  [r"infiltrate", r"consolidation", r"chest x-ray", r"chest xray",
                      r"sputum", r"cough", r"crackles", r"rales", r"hypoxemia"],
        "mgmt":      [r"antibiotic", r"levofloxacin", r"azithromycin", r"ceftriaxone",
                      r"moxifloxacin", r"doxycycline"],
        "exclude":   [r"lupus", r"overdose", r"pneumonitis", r"interstitial",
                      r"aspiration", r"chemotherapy"],
    },
    "heart_failure": {
        "condition": [r"heart failure", r"\bchf\b", r"congestive heart",
                      r"cardiomyopathy"],
        "evidence":  [r"\bbnp\b", r"ejection fraction", r"edema", r"dyspnea",
                      r"echocardiogram", r"shortness of breath", r"orthopnea", r"nyha"],
        "mgmt":      [r"diuretic", r"lasix", r"furosemide", r"ace inhibitor",
                      r"beta-blocker", r"spironolactone", r"carvedilol", r"lisinopril"],
        "exclude":   [r"overdose", r"lymphoma"],
    },
    "atrial_fib": {
        "condition": [r"atrial fibrillation", r"\bafib\b", r"a-fib", r"atrial flutter"],
        "evidence":  [r"\bekg\b", r"\becg\b", r"palpitations", r"irregular",
                      r"ventricular response", r"rhythm", r"rapid rate"],
        "mgmt":      [r"warfarin", r"coumadin", r"diltiazem", r"metoprolol",
                      r"anticoagulation", r"cardioversion", r"amiodarone", r"ablation"],
        "exclude":   [r"overdose", r"lymphoma"],
    },
    "cad_mi": {
        "condition": [r"myocardial infarction", r"coronary artery disease",
                      r"acute coronary", r"\bangina\b", r"\bcad\b"],
        "evidence":  [r"troponin", r"\bekg\b", r"chest pain", r"st elevation",
                      r"cardiac enzyme", r"\bcpk\b", r"coronary angiogra"],
        "mgmt":      [r"aspirin", r"nitroglycerin", r"heparin", r"stent",
                      r"statin", r"clopidogrel", r"catheterization"],
        "exclude":   [r"overdose", r"lymphoma"],
    },
}

def count_hits(text, patterns):
    return sum(1 for p in patterns if re.search(p, text))

def has_any(text, patterns):
    return any(re.search(p, text) for p in patterns)

def main():
    df = pd.read_csv(CSV_PATH)
    df["text"] = (df["transcription"].fillna("") + " " +
                  df["keywords"].fillna("") + " " +
                  df["description"].fillna("")).str.lower()

    rows = []
    for cond, prof in PROFILES.items():
        seen_desc = set()
        cand = []
        for idx, row in df.iterrows():
            t = row["text"]
            if has_any(t, prof["exclude"]):
                continue
            if not has_any(t, prof["condition"]):
                continue
            n_ev = count_hits(t, prof["evidence"])
            if n_ev < MIN_EVIDENCE:
                continue
            if not has_any(t, prof["mgmt"]):
                continue
            # dedupe by description (MTSamples has repeated notes)
            key = str(row["description"])[:80].lower().strip()
            if key in seen_desc:
                continue
            seen_desc.add(key)
            # score = condition mentions + evidence breadth
            score = sum(len(re.findall(p, t)) for p in prof["condition"]) + n_ev
            cand.append((score, idx, str(row["description"]).strip()[:150]))
        cand.sort(reverse=True)
        for score, idx, desc in cand:
            rows.append({"condition": cond, "score": score,
                         "row_index": idx, "description": desc})

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print("Automated screening complete.\n")
    print(out["condition"].value_counts().reindex(PROFILES.keys()).to_string())
    print(f"\nTotal candidates (pre-human-review): {len(out)}")
    print(f"Saved ranked candidates to {OUT}")
    print("\nNext step: read the ranked list and keep the genuine ones.")

if __name__ == "__main__":
    main()
