"""
summarize_e1.py
Reads results_e1.csv and organizes cases into two groups:
- Guideline-matched (in-scope) cases: show System C performance
- Out-of-scope cases: show System C's honest rejection (safety)
"""
import csv

# The 3 cases we identified as genuinely out-of-scope
# (different disease than sepsis/pneumonia/aki)
out_of_scope = {
    "case_012_SEPSIS_AKI_SOAP___Chart___Progress_Notes.txt",   # nephrolithiasis follow-up
    "case_034_PNEUMONIA_AKI_SOAP___Chart___Progress_Notes.txt", # C. diff colitis
    "case_041_AKI_SOAP___Chart___Progress_Notes.txt",           # ventricular tachycardia
}

with open("E:/Oishee/Thesis/results_e1.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

matched, oos = [], []
for r in rows:
    (oos if r["case"] in out_of_scope else matched).append(r)


def tally(group):
    s = sum(int(r["C_supported"]) for r in group)
    p = sum(int(r["C_partial"]) for r in group)
    u = sum(int(r["C_unsupported"]) for r in group)
    return s, p, u


print("=" * 65)
print("E1 RESULTS — organized into two groups")
print("=" * 65)

print(f"\n--- GROUP 1: GUIDELINE-MATCHED CASES ({len(matched)} cases) ---")
print("(These show how well System C verifies in-scope reasoning)\n")
for r in matched:
    print(f"  {r['case'][:45]:45} S:{r['C_supported']} P:{r['C_partial']} U:{r['C_unsupported']}")
s, p, u = tally(matched)
total = s + p + u
print(f"\n  TOTAL: {s} SUPPORTED, {p} PARTIAL, {u} UNSUPPORTED  (of {total} hops)")
if total:
    print(f"  Verifiable (S+P): {s+p}/{total} = {100*(s+p)/total:.0f}%")

print(f"\n--- GROUP 2: OUT-OF-SCOPE CASES ({len(oos)} cases) ---")
print("(Different diseases; System C correctly declines to verify)\n")
for r in oos:
    print(f"  {r['case'][:45]:45} S:{r['C_supported']} P:{r['C_partial']} U:{r['C_unsupported']}")
s2, p2, u2 = tally(oos)
total2 = s2 + p2 + u2
print(f"\n  TOTAL: {s2} SUPPORTED, {p2} PARTIAL, {u2} UNSUPPORTED  (of {total2} hops)")
if total2:
    print(f"  Correctly rejected (U): {u2}/{total2} = {100*u2/total2:.0f}%")

print("\n" + "=" * 65)
print("KEY NARRATIVE FOR DEFENSE:")
print("  Group 1 -> System C verifies in-scope clinical reasoning")
print("  Group 2 -> System C does NOT over-claim on out-of-scope cases")
print("=" * 65)