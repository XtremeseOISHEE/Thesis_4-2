# Frontend — Guideline-Verifiable Clinical Reasoning

A simple Streamlit dashboard for your thesis system. Two modes:

- **Showcase** — pick one of 6 pre-chosen cases (one per disease); its verified
  reasoning trace loads (cached after first run, so it's instant + offline-safe).
- **Try your own** — paste any clinical note; System C analyzes it live.

The colored verdict badges (green SUPPORTED / amber PARTIAL / red UNSUPPORTED)
are the visual heart of the demo — this is exactly the auditability your thesis
is about.

---

## How to run

1. Put `app.py` in your thesis root: `E:\Oishee\Thesis\app.py`
   (It must sit where it can import `system_c/` and reach `chroma_db` and the
   OpenRouter key — i.e. the same folder you run experiments from.)

2. From that folder:
   ```
   streamlit run app.py
   ```

3. A browser tab opens automatically (usually http://localhost:8501).

---

## IMPORTANT — check the field names first (5-minute step)

`app.py` reads System C's result using these field names (in `normalize_result`):

| The app expects | From each hop in `result["trace"]` |
|---|---|
| `step["hop_name"]`            | e.g. "Hop 1: Identification" |
| `step["reasoning"]`           | the hop's reasoning text |
| `step["verdict"]`             | "SUPPORTED" / "PARTIAL" / "UNSUPPORTED" |
| `step["verification_reason"]` | the "why" explanation |
| `step["guidelines_used"]`     | list of guideline chunk names |

and at the top level: `result["detected_condition"]`, `result["conclusion"]`.

**If your `analyze_case` uses different key names, the trace will render blank.**
Your experiment scripts (e.g. E5) already read System C's trace, so the real
key names are visible there. The quickest way to confirm:

```python
# scratch_check.py — run once from the thesis root
import sys; sys.path.insert(0, "system_c")
from system_c import SystemC
s = SystemC()
case = s.loader.load_case("cases_v2/case_4915_CAD_MI__Cardiovascular___Pulmonary.txt")
r = s.analyze_case(case)
print("TOP-LEVEL KEYS:", list(r.keys()))
print("FIRST HOP KEYS:", list(r["trace"][0].keys()))
print("SAMPLE HOP:", r["trace"][0])
```

Compare the printed keys to the table above. If any differ, edit the four lines
inside `normalize_result()` in `app.py` to match (e.g. if your key is
`"reason"` instead of `"verification_reason"`, change that one line). Ask Claude
Code to do this mapping for you if you'd rather — hand it the printed keys.

---

## Pre-computing the showcase (recommended before your defense)

The first time you open each showcase case it runs live (~30s) and caches the
result to `showcase_cache.json`. After that it's instant. To warm all six ahead
of time so your demo never waits on the network, just open each of the six once
from the Showcase tab, or delete `showcase_cache.json` to force a fresh run.

For screenshots for your evaluation form: open a case, let it render, and
screenshot the trace cards — the colored badges photograph well.

---

## Notes

- The live tab makes real API calls (uses your OpenRouter key + network). The
  network-retry you added means brief drops won't crash it.
- Detection uses the same deterministic keyword detector as the pipeline, so the
  "Detected condition" shown is exactly what the system routed on.
- `layout="centered"` keeps it readable for screenshots; change to `"wide"` in
  `st.set_page_config` if you prefer full width.
