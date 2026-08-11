"""
summarize_e1.py
Stratified reporting of results_e1.csv:
  (a) OUT-OF-SCOPE rejection  -- safety metric (should be all-UNSUPPORTED)
  (b) IN-SCOPE end-to-end     -- honest realistic verifiable rate
  (c) IN-SCOPE | correct routing -- isolates the verification loop (contribution)
Splits are driven by columns in the CSV (labeled_condition / detected_condition),
NOT hardcoded filenames. No API calls.
"""
import csv

CSV_PATH = "E:/Oishee/Thesis/results_e1.csv"

with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    has_detected = "detected_condition" in (reader.fieldnames or [])

if not has_detected:
    print("WARNING: results_e1.csv has no 'detected_condition' column -- it predates "
          "the stratified E1 run. Metric (c) needs a rerun of run_experiment_e1.py.\n")


def spu(r):
    return int(r["C_supported"]), int(r["C_partial"]), int(r["C_unsupported"])

def errored(r):
    s, p, u = spu(r)
    return s < 0 or p < 0 or u < 0

def rate(group):
    """Return (S, P, U, verifiable, total, pct) over non-errored rows."""
    s = p = u = 0
    for r in group:
        if errored(r):
            continue
        rs, rp, ru = spu(r)
        s += rs; p += rp; u += ru
    total = s + p + u
    verifiable = s + p
    pct = 100 * verifiable / total if total else 0
    return s, p, u, verifiable, total, pct


oos = [r for r in rows if r["labeled_condition"].strip().upper() == "OUT_OF_SCOPE"]
in_scope = [r for r in rows if r["labeled_condition"].strip().upper() != "OUT_OF_SCOPE"]
n_err = sum(1 for r in rows if errored(r))

print("=" * 70)
print("E1 STRATIFIED RESULTS")
print("=" * 70)
if n_err:
    print(f"(note: {n_err} case(s) errored in System C and are excluded from hop tallies)")

# (a) OUT-OF-SCOPE REJECTION -----------------------------------------------
print(f"\n--- (a) OUT-OF-SCOPE REJECTION (safety)  [{len(oos)} cases] ---")
print("Each out-of-scope case SHOULD produce all-UNSUPPORTED (no over-claiming).\n")
all_u_cases = 0
for r in oos:
    if errored(r):
        print(f"  {r['case'][:48]:48} ERRORED")
        continue
    s, p, u = spu(r)
    all_u = (s == 0 and p == 0 and u > 0)
    all_u_cases += all_u
    print(f"  {r['case'][:48]:48} S:{s} P:{p} U:{u}  {'[all-UNSUPPORTED]' if all_u else ''}")
s, p, u, ver, tot, pct = rate(oos)
print(f"\n  Cases fully rejected: {all_u_cases}/{len([r for r in oos if not errored(r)])}")
if tot:
    print(f"  Hop-level rejection: U {u}/{tot} = {100*u/tot:.0f}%")

# (b) IN-SCOPE END-TO-END --------------------------------------------------
print(f"\n--- (b) IN-SCOPE END-TO-END (honest, detection errors propagate)"
      f"  [{len(in_scope)} cases] ---")
s, p, u, ver, tot, pct = rate(in_scope)
print(f"  {s} SUPPORTED, {p} PARTIAL, {u} UNSUPPORTED  (of {tot} hops)")
print(f"  Verifiable (S+P): {ver}/{tot} = {pct:.0f}%")

# (c) IN-SCOPE | CORRECT ROUTING -------------------------------------------
print(f"\n--- (c) IN-SCOPE | CORRECT ROUTING (isolates the verification loop) ---")
if not has_detected:
    print("  Unavailable: no 'detected_condition' column (rerun E1).")
else:
    correct, misrouted = [], []
    for r in in_scope:
        labeled_key = r["labeled_condition"].strip().lower()
        detected = (r.get("detected_condition") or "").strip().lower()
        (correct if detected == labeled_key else misrouted).append(r)

    n_ok = len([r for r in correct if not errored(r)])
    print(f"  Routing accuracy: {len(correct)}/{len(in_scope)} in-scope cases correctly routed")

    s, p, u, ver, tot, pct = rate(correct)
    print(f"\n  Correctly-routed subset ({n_ok} cases):")
    print(f"    {s} SUPPORTED, {p} PARTIAL, {u} UNSUPPORTED  (of {tot} hops)")
    print(f"    Verifiable (S+P): {ver}/{tot} = {pct:.0f}%   <-- verification-loop performance")

    s2, p2, u2, ver2, tot2, pct2 = rate(misrouted)
    if tot2:
        print(f"\n  (For contrast) mis-routed subset: verifiable {ver2}/{tot2} = {pct2:.0f}%")
        print("   -- low here is expected: correct reasoning vs the WRONG guideline.")

print("\n" + "=" * 70)
print("READING GUIDE:")
print("  (a) safety: out-of-scope reasoning is not rubber-stamped.")
print("  (b) end-to-end: realistic number; includes detection routing error.")
print("  (c) conditioned on correct routing: isolates the verification contribution,")
print("      with NO hand-correction -- the split is objective (detected vs labeled).")
print("=" * 70)
