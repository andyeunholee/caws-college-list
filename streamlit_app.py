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


@st.cache_data
def load_sample():
    path = os.path.join(HERE, "intake_sample.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return ""


@st.cache_data(show_spinner=False)
def build(intake_text, lang):
    bundle = auto_report.generate(intake_text, lang=lang)
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
    lang = st.radio("Report language", ["Eng", "Kor"], horizontal=True,
                    help="Sets the filename prefix (Eng- / Kor-).")

    try:
        bundle, docx, prev = build(intake_text or "", lang)
    except Exception as exc:                       # never crash the whole page
        st.error("Could not process this intake: %s" % exc)
        st.stop()

    student, data, profile = bundle["student"], bundle["data"], bundle["profile"]

    nc = data["national_counts"]
    st.caption("Home state: **%s** · strength index **%d/100** · test **%s** · "
               "national pool tiered → Reach %d / Match %d / Safety %d"
               % (profile["home_state_name"] or "?", round(profile["S"]),
                  profile["test_display"], nc["reach"], nc["match"], nc["safety"]))

    st.markdown("#### Parsed profile")
    st.table({"Field": [k for k, _ in student["info"]],
              "Value": [v for _, v in student["info"]]})

    st.markdown('<span class="ep-file">%s</span>' % student["output_name"], unsafe_allow_html=True)
    st.download_button("⬇  Download .docx", data=docx, file_name=student["output_name"],
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       use_container_width=True, type="primary")
    st.caption("Every college list, probability, and section note is generated from this profile — "
               "home-state schools are auto-excluded from the national list and become the in-state section.")

with right:
    st.markdown("#### Live preview")
    components.html(prev, height=1500, scrolling=True)
