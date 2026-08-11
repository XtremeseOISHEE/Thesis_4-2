"""
build_case_files.py
Reads genuine_cases_53.csv, pulls each row from mtsamples.csv, and writes one
case file per genuine case into the cases folder — same format your existing
pipeline expects (filename encodes condition, body is the transcription).

Run AFTER find_53_genuine.py has produced genuine_cases_53.csv.
"""
import pandas as pd
import os

MTSAMPLES = "E:/Oishee/Thesis/mtsamples.csv"          # on PC: "E:/Oishee/Thesis/mtsamples.csv"
GENUINE_LIST = "genuine_cases_53.csv"
OUT_DIR = "E:/Oishee/Thesis/cases_v2"                  # on PC: "E:/Oishee/Thesis/cases_v2"

def safe(s):
    # make a filesystem-safe fragment
    return "".join(c if c.isalnum() else "_" for c in str(s))[:40]

def main():
    df = pd.read_csv(MTSAMPLES)
    genuine = pd.read_csv(GENUINE_LIST)
    os.makedirs(OUT_DIR, exist_ok=True)

    written = 0
    listing = []
    for _, g in genuine.iterrows():
        idx = int(g["row_index"])
        cond = str(g["condition"]).upper()
        row = df.loc[idx]
        transcription = str(row["transcription"]).strip()
        description = str(row["description"]).strip()

        fname = f"case_{idx:04d}_{cond}_{safe(row['medical_specialty'])}.txt"
        path = os.path.join(OUT_DIR, fname)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"CONDITION: {cond}\n")
            f.write(f"SPECIALTY: {str(row['medical_specialty']).strip()}\n")
            f.write(f"DESCRIPTION: {description}\n")
            f.write("=" * 60 + "\n")
            f.write(transcription + "\n")

        listing.append(f"{OUT_DIR}/{fname}")
        written += 1

    # Save a plain list of all case file paths (for experiment_cases.txt)
    with open("experiment_cases_v2.txt", "w", encoding="utf-8") as f:
        for p in listing:
            f.write(p + "\n")

    print(f"Wrote {written} case files to '{OUT_DIR}/'")
    print(f"Case list saved to experiment_cases_v2.txt")

if __name__ == "__main__":
    main()
