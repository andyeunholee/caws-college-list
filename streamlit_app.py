# -*- coding: utf-8 -*-
"""
streamlit_app.py — ELITE PREP College Report Studio (Streamlit Cloud entry point)
=================================================================================
Deploy on Streamlit Community Cloud for a public https://<name>.streamlit.app URL.

Reuses the real Python generator (report_engine + intake_parser +
generate_college_report), so the downloaded .docx is identical to the CLI output.
"""

import io
import json
import os

import streamlit as st
import streamlit.components.v1 as components

from intake_parser import parse_intake, build_student
import generate_college_report as gcr
from preview_html import preview_html

HERE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="ELITE PREP · College Report Studio",
                   page_icon="🎓", layout="wide")


@st.cache_data
def load_data():
    with open(os.path.join(HERE, "college_data.json"), encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_sample():
    path = os.path.join(HERE, "intake_sample.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return ""


def make_docx_bytes(student, data):
    buf = io.BytesIO()
    gcr.build(student, data, buf)
    buf.seek(0)
    return buf.getvalue()


# ---------- styling ----------
st.markdown("""
<style>
  .block-container{padding-top:1.4rem;padding-bottom:2rem;max-width:1500px}
  .ep-bar{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid #B7791F;
          padding-bottom:10px;margin-bottom:6px}
  .ep-logo{font-weight:800;letter-spacing:.22em;color:#1F3864;font-size:20px}
  .ep-sub{color:#6b7280;font-size:14px}
  .ep-file{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#1F3864;
           background:#e8ecf4;border-radius:6px;padding:4px 9px;display:inline-block}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ep-bar"><span class="ep-logo">ELITE PREP</span>'
            '<span class="ep-sub">College Report Studio</span></div>',
            unsafe_allow_html=True)

data = load_data()
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

    student = build_student(parse_intake(intake_text or ""), lang=lang)

    st.markdown("#### Parsed profile")
    st.table({"Field": [k for k, _ in student["info"]],
              "Value": [v for _, v in student["info"]]})

    st.markdown('<span class="ep-file">%s</span>' % student["output_name"],
                unsafe_allow_html=True)
    st.download_button("⬇  Download .docx",
                       data=make_docx_bytes(student, data),
                       file_name=student["output_name"],
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       use_container_width=True, type="primary")
    st.caption("College lists, probabilities, and section commentary come from the loaded "
               "dataset for this student. Editing the intake updates the profile block, cover, "
               "footer, and filename.")

with right:
    st.markdown("#### Live preview")
    components.html(preview_html(student, data), height=1500, scrolling=True)
