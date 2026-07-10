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

HERE = os.path.dirname(os.path.abspath(__file__))
_DB = None


def load_db(path=None):
    global _DB
    if _DB is None:
        with open(path or os.path.join(HERE, "college_db.json"), encoding="utf-8") as f:
            _DB = json.load(f)
    return _DB


def _patch_info(student, profile):
    """Show the real test score (incl. ACT) on the profile table."""
    info = []
    for label, value in student["info"]:
        if label == "SAT":
            info.append(("Test Score", profile["test_display"]))
        else:
            info.append((label, value))
    student["info"] = info
    return student


def generate(intake_text, lang="Eng", db=None):
    db = db or load_db()
    fields = parse_intake(intake_text or "")
    profile = build_profile(fields, intake_text or "")
    student = build_student(fields, lang=lang)
    _patch_info(student, profile)

    lists = select_lists(profile, db)
    data = {
        "national": lists["national"], "instate": lists["instate"], "lac": lists["lac"],
        "ed": lists["ed"], "ea": lists["ea"],
        "instate_state_name": lists["instate_state_name"],
        "national_counts": lists["national_counts"],
    }
    narr = build_narrative(profile, lists)
    return {"student": student, "data": data, "narr": narr, "profile": profile}


def docx_bytes(bundle):
    return assemble_bytes(bundle["student"], bundle["data"], bundle["narr"])


def preview_html(bundle):
    return _preview(bundle["student"], bundle["data"], bundle["narr"])
