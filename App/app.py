"""
app.py -- Frontend for the Multi-Hop Guideline-Verifiable Clinical Reasoning System.

A Streamlit dashboard with two modes:
  1. Showcase  -- pick a pre-analyzed case from a dropdown; its cached trace loads
                  instantly. The patient's clinical note is shown too, so a viewer
                  can see exactly what the system read.
  2. Try your own -- paste any clinical note; System C analyzes it live.

PLACE THIS FILE IN:  E:/Oishee/Thesis/App/app.py
Run it FROM the thesis root so imports resolve, e.g.:
    cd E:/Oishee/Thesis
    streamlit run App/app.py
(app.py computes THESIS_ROOT as its PARENT folder, so system_c/, cases_v2/,
chroma_db, and the OpenRouter key are all found automatically.)
"""

import os
import sys
import json
import streamlit as st

# --------------------------------------------------------------------------- #
# Paths & imports
# --------------------------------------------------------------------------- #
# This file lives in  <THESIS_ROOT>/App/app.py  -> THESIS_ROOT is the PARENT dir.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_ROOT = os.path.dirname(APP_DIR)                      # one level up from App/
SYSTEM_C_DIR = os.path.join(THESIS_ROOT, "system_c")
CASES_DIR = os.path.join(THESIS_ROOT, "cases_v2")
CACHE_PATH = os.path.join(APP_DIR, "showcase_cache.json")   # cache lives beside app.py

if SYSTEM_C_DIR not in sys.path:
    sys.path.insert(0, SYSTEM_C_DIR)

# The six showcase cases (one per disease). These filenames must exist in cases_v2/.
SHOWCASE_CASES = {
    "Sepsis — case 4481": "case_4481_SEPSIS__Consult___History_and_Phy_.txt",
    "Acute Kidney Injury — case 4135": "case_4135_AKI__Consult___History_and_Phy_.txt",
    "Pneumonia — case 4831": "case_4831_PNEUMONIA__Cardiovascular___Pulmonary.txt",
    "Heart Failure — case 4859": "case_4859_HEART_FAILURE__Cardiovascular___Pulmonary.txt",
    "Atrial Fibrillation — case 4908": "case_4908_ATRIAL_FIB__Cardiovascular___Pulmonary.txt",
    "Coronary Artery Disease / MI — case 4915": "case_4915_CAD_MI__Cardiovascular___Pulmonary.txt",
}

# An example note pre-filled in the live tab so users see the expected input shape.
EXAMPLE_NOTE = (
    "A 68-year-old man presents with acute shortness of breath and fatigue over "
    "two days. History of hypertension and prior myocardial infarction. On exam: "
    "bilateral crackles, elevated JVP, and pitting edema. BNP is markedly elevated "
    "at 1850 pg/mL. Chest X-ray shows pulmonary vascular congestion. He is on "
    "furosemide at home but admits poor adherence."
)

# Plain-language, one-line explanation of what each hop is doing (for non-clinician
# viewers). Shown under each hop so a CSE-student rater understands the step.
HOP_PLAIN = {
    "Hop 1": "Step 1 — the system decides which condition the patient most likely has.",
    "Hop 2": "Step 2 — the system checks the evidence that confirms that condition.",
    "Hop 3": "Step 3 — the system proposes how to treat / manage the condition.",
}

# Plain-language meaning of each verdict (shown once, in the legend).
VERDICT_MEANING = {
    "SUPPORTED": "This step's reasoning matches the medical guideline.",
    "PARTIAL": "Mostly matches, but adds detail the guideline doesn't cover.",
    "UNSUPPORTED": "Does not match the guideline (wrong topic, or contradicts it).",
}

# Verdict hues are FIXED (they carry meaning) but chosen to read on light AND dark.
VERDICT_COLOR = {              # badge text -- sits on the solid pastel pill below
    "SUPPORTED": "#1B7F4B",
    "PARTIAL": "#9A6B00",      # darkened from #B8860B for pill contrast
    "UNSUPPORTED": "#A3303E",  # darkened from #B23A48 for pill contrast
}
VERDICT_BG = {                 # badge pill -- solid pastel: a light island readable on any bg
    "SUPPORTED": "#E6F4EC",
    "PARTIAL": "#FBF3DD",
    "UNSUPPORTED": "#F7E7E9",
}
VERDICT_ACCENT = {             # card border + "why" label -- mid hue, legible on light OR dark
    "SUPPORTED": "#2FA968",
    "PARTIAL": "#C79A2E",
    "UNSUPPORTED": "#D0596A",
}

# Theme-adaptive style tokens (no forced background; text follows the active theme).
TXT = "var(--text-color, inherit)"
SURFACE = "var(--secondary-background-color, rgba(128,128,128,0.08))"
INSET = "rgba(128,128,128,0.14)"     # nested box (why / note), distinct from the card
BORDER = "rgba(128,128,128,0.28)"
MUTED = "opacity:0.62;"
ACCENT_BLUE = "#3b82f6"              # detected-condition + conclusion accent (blue reads on both)


# --------------------------------------------------------------------------- #
# Lazy System C loader (only imported when actually needed -> fast startup)
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_system():
    """Import and initialize System C once, cached across reruns."""
    from system_c import SystemC
    return SystemC()


def read_case_note(filename):
    """Return the raw text of a case file (for display), or a fallback message."""
    path = os.path.join(CASES_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "(Could not read the case file.)"


def analyze_live(note_text):
    """Run System C on a raw clinical note and normalize the trace to a dict."""
    system = get_system()
    case = {
        "filename": "user_input.txt",
        "condition": "UNKNOWN",
        "description": "",
        "transcription": note_text,
        "full_text": note_text,
    }
    result = system.analyze_case(case)
    # analyze_case doesn't return the routed condition, so re-derive it with the
    # same deterministic detector and the same inputs it used internally.
    result["detected_condition"] = system.reasoner._guess_condition(
        case.get("description", ""), note_text
    )
    return normalize_result(result)


def normalize_result(result):
    """Reduce a System C result to the fields the UI needs (JSON-serializable)."""
    trace = []
    for step in result.get("trace", []):
        trace.append({
            "hop_name": step.get("hop_name", ""),
            "reasoning": step.get("reasoning", ""),
            "verdict": step.get("verdict", "").upper(),
            "why": step.get("verification_reason", ""),
            "guidelines": step.get("guidelines_used", []),
        })
    return {
        "detected_condition": result.get("detected_condition") or "none",
        "trace": trace,
        "conclusion": result.get("conclusion") or result.get("final_summary", ""),
    }


# --------------------------------------------------------------------------- #
# Showcase cache (pre-computed traces so the demo is instant & offline-safe)
# --------------------------------------------------------------------------- #
def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def analyze_showcase(label, filename, cache):
    """Return a cached trace if present, else run live and write it to cache."""
    if label in cache:
        return cache[label]
    system = get_system()
    case = system.loader.load_case(os.path.join(CASES_DIR, filename))
    case_text = case["transcription"] if case["transcription"] else case["full_text"]
    raw = system.analyze_case(case)
    # analyze_case doesn't return the routed condition; re-derive it the same way.
    raw["detected_condition"] = system.reasoner._guess_condition(
        case.get("description", ""), case_text
    )
    result = normalize_result(raw)
    cache[label] = result
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass
    return result


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def verdict_badge(verdict):
    color = VERDICT_COLOR.get(verdict, "#555")
    bg = VERDICT_BG.get(verdict, "#eee")
    return (
        f"<span style='background:{bg};color:{color};font-weight:700;"
        f"padding:3px 12px;border-radius:999px;font-size:0.8rem;"
        f"letter-spacing:0.03em;border:1px solid {color}33;'>{verdict}</span>"
    )


def render_note(note_text):
    """Show the raw clinical note the system read, in a collapsible box."""
    with st.expander("📄  View the patient's clinical note (what the system read)", expanded=False):
        st.markdown(
            f"<div style='background:{INSET};border:1px solid {BORDER};border-radius:8px;"
            f"padding:0.9rem 1.1rem;font-size:0.86rem;line-height:1.55;color:{TXT};"
            f"white-space:pre-wrap;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;'>"
            f"{note_text}</div>",
            unsafe_allow_html=True,
        )


def render_trace(result):
    # CSS: turn each bordered container that holds a .hopcard marker into a "card"
    # with a verdict-colored left border. :has() lets us color the OUTER container
    # from a marker rendered inside it. (Re-injected per call; harmless/idempotent.)
    card_css = (
        "<style>"
        "div[data-testid='stVerticalBlockBorderWrapper']:has(.hopcard)"
        f"{{border-radius:10px;background:{SURFACE};}}"
        + "".join(
            f"div[data-testid='stVerticalBlockBorderWrapper']:has(.hopcard-{v.lower()})"
            f"{{border-left:5px solid {c} !important;}}"
            for v, c in VERDICT_ACCENT.items()
        )
        # Reasoning markdown text: crisp, near-black & slightly bolder in light mode
        # (photographs clearly for screenshots); light in dark mode. Targets ONLY the
        # p/li/td/th the reasoning markdown produces -- the header, badge, "why" box,
        # and guideline line use div/span/b and keep their own colors.
        + "div[data-testid='stVerticalBlockBorderWrapper']:has(.hopcard) "
          "[data-testid='stMarkdownContainer'] :is(p,li,td,th)"
          "{color:#1a1a1a !important;font-weight:500;}"
        + "@media (prefers-color-scheme:dark){"
          "div[data-testid='stVerticalBlockBorderWrapper']:has(.hopcard) "
          "[data-testid='stMarkdownContainer'] :is(p,li,td,th)"
          "{color:rgba(250,250,250,0.96) !important;}}"
        + "</style>"
    )
    st.markdown(card_css, unsafe_allow_html=True)

    detected = result.get("detected_condition", "none")
    st.markdown(
        f"<div style='margin:0.5rem 0 1.25rem 0;'>"
        f"<span style='{MUTED}font-size:0.85rem;'>Detected condition (routing)</span><br>"
        f"<span style='font-size:1.15rem;font-weight:700;color:{ACCENT_BLUE};'>"
        f"{detected}</span></div>",
        unsafe_allow_html=True,
    )

    for step in result["trace"]:
        hop_key = step["hop_name"].split(":")[0].strip()
        verdict = step["verdict"]
        accent = VERDICT_ACCENT.get(verdict, "#888")

        with st.container(border=True):
            # marker (drives the :has left-border) + header row + plain-language line
            st.markdown(
                f"<span class='hopcard hopcard-{verdict.lower()}'></span>"
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;margin-bottom:0.35rem;'>"
                f"<span style='font-weight:700;font-size:1.02rem;color:{TXT};'>"
                f"{step['hop_name']}</span>{verdict_badge(verdict)}</div>"
                f"<div style='{MUTED}font-size:0.82rem;font-style:italic;"
                f"margin-bottom:0.15rem;'>{HOP_PLAIN.get(hop_key, '')}</div>",
                unsafe_allow_html=True,
            )
            # reasoning as REAL markdown so tables / bullets / bold render (no gap)
            st.markdown(step["reasoning"])
            # "why" box + guideline line
            st.markdown(
                f"<div style='background:{INSET};border-radius:8px;padding:0.6rem 0.8rem;"
                f"font-size:0.86rem;color:{TXT};margin-top:0.3rem;'>"
                f"<b style='color:{accent};'>Why this verdict:</b> {step['why']}</div>"
                f"<div style='margin-top:0.5rem;font-size:0.78rem;{MUTED}'>"
                f"Guideline checked: "
                f"{', '.join(step['guidelines']) if step['guidelines'] else '—'}"
                f"</div>",
                unsafe_allow_html=True,
            )

    if result.get("conclusion"):
        st.markdown(
            f"<div style='background:{SURFACE};border:1px solid {BORDER};"
            f"border-left:5px solid {ACCENT_BLUE};border-radius:10px;"
            f"padding:1rem 1.25rem;margin-top:0.5rem;'>"
            f"<div style='font-size:0.78rem;letter-spacing:0.08em;text-transform:"
            f"uppercase;{MUTED}margin-bottom:0.35rem;'>Final conclusion</div>"
            f"<div style='color:{TXT};font-size:0.95rem;line-height:1.5;'>{result['conclusion']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_legend():
    chips = ""
    for v, meaning in VERDICT_MEANING.items():
        color = VERDICT_COLOR[v]
        bg = VERDICT_BG[v]
        chips += (
            f"<div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;'>"
            f"<span style='background:{bg};color:{color};font-weight:700;padding:2px 10px;"
            f"border-radius:999px;font-size:0.72rem;border:1px solid {color}33;'>{v}</span>"
            f"<span style='font-size:0.8rem;color:{TXT};{MUTED}'>{meaning}</span></div>"
        )
    st.markdown(chips, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Page
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Guideline-Verifiable Clinical Reasoning",
    page_icon="🩺",
    layout="centered",
)

# Header
st.markdown(
    "<div style='margin-bottom:0.25rem;'>"
    "<span style='font-size:0.8rem;letter-spacing:0.12em;text-transform:uppercase;"
    "opacity:0.6;'>Multi-Hop &nbsp;·&nbsp; Guideline-Verifiable &nbsp;·&nbsp; Auditable</span>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='margin-top:0;font-size:1.9rem;line-height:1.2;color:var(--text-color,inherit);'>"
    "Clinical Reasoning You Can Check</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='opacity:0.85;font-size:0.98rem;line-height:1.55;max-width:38rem;'>"
    "This system reads a patient's clinical note and reasons toward a diagnosis in "
    "three steps. Crucially, <b>every step is checked against an established medical "
    "guideline</b> and given a verdict — so you can see exactly which parts of the "
    "AI's reasoning are backed by guidelines and which are not.</p>",
    unsafe_allow_html=True,
)

with st.expander("What do the verdicts mean?", expanded=False):
    render_legend()

st.divider()

tab_showcase, tab_live = st.tabs(["📁  Showcase cases", "✏️  Try your own note"])

# ---- Showcase tab --------------------------------------------------------- #
with tab_showcase:
    st.markdown(
        "<p style='opacity:0.62;font-size:0.9rem;'>Pick a real, pre-analyzed case "
        "(one per condition). You can view the original patient note, then the full "
        "verified reasoning trace below.</p>",
        unsafe_allow_html=True,
    )
    label = st.selectbox("Choose a case", list(SHOWCASE_CASES.keys()))

    # Always show the case note (so a viewer sees what the system read) --------
    render_note(read_case_note(SHOWCASE_CASES[label]))

    if st.button("Show reasoning trace", type="primary"):
        cache = load_cache()
        with st.spinner("Loading trace…"):
            try:
                result = analyze_showcase(label, SHOWCASE_CASES[label], cache)
                render_trace(result)
            except Exception as e:
                st.error(
                    "Couldn't load this case. Run the app from the thesis root "
                    f"(streamlit run App/app.py) so system_c/ and cases_v2/ resolve.\n\n{e}"
                )

# ---- Live tab ------------------------------------------------------------- #
with tab_live:
    st.markdown(
        "<p style='opacity:0.62;font-size:0.9rem;'>Paste any clinical note and the "
        "system analyzes it live (real API calls, a few seconds per step). For best "
        "results, include the patient's symptoms, key labs, and history — like the "
        "example below.</p>",
        unsafe_allow_html=True,
    )
    st.caption(
        "This is a research prototype. The six showcase cases give the clearest "
        "results; free-text notes may route less accurately, especially when a note "
        "leads with past history rather than the current problem."
    )
    note = st.text_area("Clinical note", value=EXAMPLE_NOTE, height=220)
    if st.button("Analyze note", type="primary"):
        if len(note.strip()) < 40:
            st.warning(
                "Please paste a fuller clinical note — at least a few sentences "
                "describing the patient's symptoms, labs, and history."
            )
        else:
            with st.spinner("Analyzing — running three verified reasoning steps…"):
                try:
                    result = analyze_live(note)
                    render_trace(result)
                except Exception as e:
                    st.error(
                        "Analysis failed. Run from the thesis root, check the "
                        f"OpenRouter key, and confirm the network is up.\n\n{e}"
                    )

# Footer
st.divider()
st.markdown(
    "<p style='opacity:0.5;font-size:0.78rem;text-align:center;'>"
    "System A gives an answer you cannot audit. System B reasons with guidelines but "
    "never checks itself. <b>System C — shown here — verifies every step.</b></p>",
    unsafe_allow_html=True,
)
