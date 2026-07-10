# -*- coding: utf-8 -*-
"""
streamlit_app.py — ELITE PREP College Report Studio (full automation)
=====================================================================
Paste ANY student's intake -> the app auto-computes college lists, tiers,
profile-adjusted admit probabilities, and tailored commentary, and lets you
download the formatted .docx. Deploy on Streamlit Community Cloud.
"""

import os

import streamlit as st
import streamlit.components.v1 as components

import auto_report

HERE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="ELITE PREP · College Report Studio",
                   page_icon="🎓", layout="wide")

# Expose the Anthropic key (set in Streamlit Secrets) to the SDK via env var.
# Streamlit Cloud also mirrors secrets into environment variables, so prefer that
# and only touch st.secrets when a secrets.toml actually exists (avoids a noisy
# "no secrets found" box locally / before the key is configured).
def _load_api_key():
    from pathlib import Path
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        return
    if not any(p.exists() for p in (Path.cwd() / ".streamlit" / "secrets.toml",
                                    Path.home() / ".streamlit" / "secrets.toml")):
        return
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            os.environ["ANTHROPIC_API_KEY"] = str(st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        pass


_load_api_key()
AI_READY = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


@st.cache_data
def load_sample():
    path = os.path.join(HERE, "intake_sample.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return ""


@st.cache_data(show_spinner=False)
def build(intake_text, lang, use_ai):
    bundle = auto_report.generate(intake_text, lang=lang, use_ai=use_ai)
    return bundle, auto_report.docx_bytes(bundle), auto_report.preview_html(bundle)


st.markdown("""
<style>
  .block-container{padding-top:1.4rem;padding-bottom:2rem;max-width:1500px}
  .ep-bar{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid #B7791F;
          padding-bottom:10px;margin-bottom:6px}
  .ep-logo{font-weight:800;letter-spacing:.22em;color:#1F3864;font-size:20px}
  .ep-sub{color:#6b7280;font-size:14px}
  .ep-file{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#1F3864;
           background:#e8ecf4;border-radius:6px;padding:4px 9px;display:inline-block;word-break:break-all}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ep-bar"><span class="ep-logo">ELITE PREP</span>'
            '<span class="ep-sub">College Report Studio · full automation</span></div>',
            unsafe_allow_html=True)

left, right = st.columns([1, 1.55], gap="large")

with left:
    st.markdown("#### Intake form / email")
    if "intake" not in st.session_state:
        st.session_state["intake"] = load_sample()
    c1, c2 = st.columns(2)
    if c1.button("Load sample", use_container_width=True):
        st.session_state["intake"] = load_sample()
    if c2.button("Clear", use_container_width=True):
        st.session_state["intake"] = ""
    intake_text = st.text_area("Paste the student's intake email (Key: Value lines)",
                               key="intake", height=240, label_visibility="collapsed")
    lc, rc = st.columns([1, 1])
    lang = lc.radio("Report language", ["Eng", "Kor"], horizontal=True,
                    help="Sets the report language and the filename prefix (Eng- / Kor-).")
    use_ai = rc.checkbox("AI-enhanced commentary", value=AI_READY, disabled=not AI_READY,
                         help=("Claude writes the section commentary (lists & probabilities stay "
                               "code-computed). Requires an ANTHROPIC_API_KEY in Streamlit Secrets."
                               if AI_READY else
                               "Add ANTHROPIC_API_KEY in Streamlit Secrets to enable AI commentary."))

    # ---- explicit RUN button: report is generated only when this is clicked ----
    run = st.button("▶  Generate Report", type="primary", use_container_width=True)
    if run:
        st.session_state["gen_sig"] = (intake_text or "", lang, use_ai)
    # show the loaded sample on first visit so the screen isn't empty
    if "gen_sig" not in st.session_state:
        st.session_state["gen_sig"] = (intake_text or "", lang, use_ai)

    sig = st.session_state.get("gen_sig")
    bundle = docx = prev = None
    if sig and sig[0].strip():
        spinner = "Writing AI commentary…" if sig[2] else "Generating…"
        try:
            with st.spinner(spinner):
                bundle, docx, prev = build(sig[0], sig[1], sig[2])
        except Exception as exc:                   # never crash the whole page
            st.error("Could not process this intake: %s" % exc)

    if bundle:
        student, data, profile = bundle["student"], bundle["data"], bundle["profile"]
        nc = data["national_counts"]
        mode = "🟢 AI commentary" if bundle.get("narr_source") == "ai" else "⚪ Template commentary"
        st.caption("Home state: **%s** · strength index **%d/100** · test **%s** · "
                   "Reach %d / Match %d / Safety %d · %s"
                   % (profile["home_state_name"] or "?", round(profile["S"]),
                      profile["test_display"], nc["reach"], nc["match"], nc["safety"], mode))
        st.markdown("#### Parsed profile")
        st.table({"Field": [k for k, _ in student["info"]],
                  "Value": [v for _, v in student["info"]]})
        st.markdown('<span class="ep-file">%s</span>' % student["output_name"], unsafe_allow_html=True)
        st.download_button("⬇  Download .docx", data=docx, file_name=student["output_name"],
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           use_container_width=True)
        st.caption("Every college list, probability, and section note is generated from this profile — "
                   "home-state schools are auto-excluded from the national list and become the in-state section.")
    else:
        st.info("Paste the student's intake above, choose the language, then click "
                "**▶ Generate Report**.")

with right:
    st.markdown("#### Live preview")
    if prev:
        components.html(prev, height=1500, scrolling=True)
    else:
        st.caption("The report preview will appear here after you click ▶ Generate Report.")
