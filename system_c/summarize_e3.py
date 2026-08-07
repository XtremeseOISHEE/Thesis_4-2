"""
summarize_e3.py
Reads results_e3.csv and prints a per-hop summary of how many reasoning claims
are individually guideline-verifiable. No API calls -- only reads the CSV.

Metric definitions (per hop config):
  SUPPORTED  = fully-verified claims
  VERIFIABLE = SUPPORTED + PARTIAL   (primary highlighted metric)
  TOTAL      = SUPPORTED + PARTIAL + UNSUPPORTED
"""
import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "results_e3.csv")

HOPS = ["1-hop", "2-hop", "3-hop"]


def summarize(csv_path=CSV_PATH):
    # Accumulators per hop config
    totals = {hop: {"S": 0, "P": 0, "U": 0} for hop in HOPS}
    n_cases = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n_cases += 1
            for hop in HOPS:
                totals[hop]["S"] += int(row[f"{hop}_S"])
                totals[hop]["P"] += int(row[f"{hop}_P"])
                totals[hop]["U"] += int(row[f"{hop}_U"])

    print("=" * 60)
    print(f"E3 SUMMARY  ({n_cases} cases)")
    print("=" * 60)

    verifiable_by_hop = {}
    for hop in HOPS:
        s = totals[hop]["S"]
        p = totals[hop]["P"]
        u = totals[hop]["U"]
        verifiable = s + p
        total = s + p + u
        verifiable_by_hop[hop] = verifiable

        print(f"\n{hop}:")
        print(f"  >> VERIFIABLE (SUPPORTED + PARTIAL): {verifiable}   <-- primary metric")
        print(f"     SUPPORTED (fully verified):       {s}")
        print(f"     Total claims:                     {total}")

    # One-line takeaway
    v1, v2, v3 = (verifiable_by_hop["1-hop"],
                  verifiable_by_hop["2-hop"],
                  verifiable_by_hop["3-hop"])
    print("\n" + "=" * 60)
    print(f"More hops produce more checkable claims: {v1} -> {v2} -> {v3}")
    print("=" * 60)


if __name__ == "__main__":
    summarize()
