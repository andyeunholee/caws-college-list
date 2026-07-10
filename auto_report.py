# -*- coding: utf-8 -*-
"""
auto_report.py — full-automation pipeline
=========================================
intake text  ->  parsed fields  ->  structured profile  ->  computed college
lists + probabilities  ->  tailored narrative  ->  (.docx bytes | HTML preview).

Any student, any home state: the college lists, tiers, probabilities, and the
section commentary are all generated from the pasted profile.
"""

import json
import os

from intake_parser import parse_intake, build_student
from scoring import build_profile, select_lists
from narrative import build_narrative
from assemble import assemble_bytes
from preview_html import preview_html as _preview
import llm_narrative

HERE = os.path.dirname(os.path.abspath(__file__))
_DB = None


def load_db(path=None):
    global _DB
    if _DB is None:
        with open(path or os.path.join(HERE, "college_db.json"), encoding="utf-8") as f:
            _DB = json.load(f)
    return _DB


def _patch_info(student, profile, lang):
    """Show the real test score (incl. ACT) on the profile table."""
    disp = profile["test_display"]
    if lang == "Kor":
        disp = disp.replace("SAT eq.", "SAT 환산").replace(" / Math ", " / 수학 ")
    info = []
    for label, value in student["info"]:
        info.append(("Test Score", disp) if label == "SAT" else (label, value))
    student["info"] = info
    return student


def generate(intake_text, lang="Eng", db=None, use_ai=True):
    db = db or load_db()
    fields = parse_intake(intake_text or "")
    profile = build_profile(fields, intake_text or "")
    student = build_student(fields, lang=lang)
    _patch_info(student, profile, lang)

    lists = select_lists(profile, db)
    data = {
        "national": lists["national"], "instate": lists["instate"], "lac": lists["lac"],
        "ed": lists["ed"], "ea": lists["ea"],
        "instate_state_name": lists["instate_state_name"],
        "national_counts": lists["national_counts"],
    }
    narr = build_narrative(profile, lists, lang)          # deterministic template baseline
    source = "template"
    if use_ai and llm_narrative.available():
        try:
            narr = llm_narrative.enhance(profile, lists, narr, lang)   # Claude-written prose
            source = "ai"
        except Exception:
            source = "template"                            # safe fallback on any error
    return {"student": student, "data": data, "narr": narr, "profile": profile,
            "lang": lang, "narr_source": source}


def docx_bytes(bundle):
    return assemble_bytes(bundle["student"], bundle["data"], bundle["narr"], bundle.get("lang", "Eng"))


def preview_html(bundle):
    return _preview(bundle["student"], bundle["data"], bundle["narr"], bundle.get("lang", "Eng"))
