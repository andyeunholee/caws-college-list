# -*- coding: utf-8 -*-
"""
assemble.py — build the .docx from dynamic (student, data, narrative)
=====================================================================
Same section order and formatting as the reference template, but every list and
every paragraph is supplied at call time (no hardcoded student).
"""

import io

from report_engine import ReportBuilder, NAVY, RED, GOLD, GREEN, TEXT, GRAY

BOX_BG = {"reach": "F3E7E9", "match": "FBF1DD", "safety": "E7F1E8", "navy": "E8ECF4"}
BOX_ACCENT = {"reach": RED, "match": GOLD, "safety": GREEN, "navy": NAVY}


def _rows(triples):
    return [(i + 1, c, s, p) for i, (c, s, p) in enumerate(triples)]


def _tiered(b, tiers, labels):
    for i, (key, label) in enumerate(zip(("reach", "match", "safety"), labels)):
        if i > 0:
            b.spacer(after=60)
        b.tier_label(key, label)
        rows = tiers.get(key, [])
        if rows:
            b.list_table(key, _rows(rows))
        else:
            b.body([("— no schools fell in this tier for this profile —", False, GRAY, 18)], after=40)


def assemble_bytes(student, data, narr):
    b = ReportBuilder()
    b.build_header("College Admissions Strategy Report")
    b.build_footer(student["footer"])

    b.title_block(student["name"], student["cycle_line"])
    b.info_table(student["info"])
    b.spacer()
    b.box(narr["note"], bg=BOX_BG["match"], accent=GOLD)
    b.page_break()

    b.heading("1.  Methodology · Evaluation Criteria")
    b.body([(narr["methodology"], False, TEXT, 20)])
    b.body(narr["tier_def"], after=120, line=276)
    b.tier_badges()
    b.spacer()
    b.box(narr["testing"], bg=BOX_BG["navy"], accent=NAVY)
    b.spacer()
    b.box(narr["core"], bg=BOX_BG["reach"], accent=RED)
    b.spacer()

    b.heading("2.  National University List")
    b.body([(narr["national_intro"], False, TEXT, 20)])
    _tiered(b, data["national"], ("REACH (Est. Admit Probability ≤ 20%)",
            "MATCH (Est. Admit Probability 21–55%)", "SAFETY (Est. Admit Probability ≥ 60%)"))

    b.heading("3.  In-State Universities · %s" % data["instate_state_name"])
    b.body([(narr["instate_intro"], False, TEXT, 20)])
    _tiered(b, data["instate"], ("REACH", "MATCH", "SAFETY"))

    b.heading("4.  Liberal Arts College (LAC) List")
    b.body([(narr["lac_intro"], False, TEXT, 20)])
    _tiered(b, data["lac"], ("REACH", "MATCH", "SAFETY"))

    b.heading("5.  Early Decision (ED) Strategy · RD vs ED Comparison")
    b.body(narr["ed_intro"], after=160)
    if data["ed"]:
        b._generic_table([3640, 720, 1320, 1320, 2360],
                         [("College", "left"), ("State", "center"), ("RD Prob.", "center"),
                          ("ED Prob.", "center"), ("Recommendation", "center")],
                         [[(r[0], "left", True, TEXT), (r[1], "center", True, TEXT),
                           (r[2], "center", True, GRAY), (r[3], "center", True, GREEN),
                           (r[4], "center", True, RED)] for r in data["ed"]])
    else:
        b.body([("No Early-Decision schools matched this profile’s reach/match band.", False, GRAY, 18)])
    b.box(narr["ed_rec"], bg=BOX_BG["navy"], accent=NAVY)
    b.spacer()

    b.heading("6.  Early Action (EA / REA) Strategy")
    b.body(narr["ea_intro"], after=160)
    if data["ea"]:
        b._generic_table([3600, 720, 1320, 3720],
                         [("College", "left"), ("State", "center"), ("EA Prob.", "center"),
                          ("Notes (Policy / Caution)", "left")],
                         [[(r[0], "left", True, TEXT), (r[1], "center", True, TEXT),
                           (r[2], "center", True, NAVY), (r[3], "left", True, GRAY)] for r in data["ea"]])
    else:
        b.body([("No Early-Action schools matched this profile.", False, GRAY, 18)])
    b.spacer()

    b.heading("7.  12th-Grade Action Plan (From Now Through Application)")
    b.body([(narr["action_intro"], False, TEXT, 20)])
    for accent_tier, box in narr["steps"]:
        b.box(box, bg=BOX_BG[accent_tier], accent=BOX_ACCENT[accent_tier])
    b.spacer()

    b.heading("8.  Abbreviations · Full Description")
    b.body([("Full names and meanings of the abbreviations used in this report and its key notes.",
             False, TEXT, 20)])
    b._generic_table([2400, 6960], [("Abbreviation", "left"), ("Full Description", "left")],
                     [[(a, "left", True, NAVY), (d, "left", True, TEXT)] for a, d in narr["abbreviations"]])
    b.spacer()
    b.box(narr["disclaimer"], bg="F2F2F2", accent=GRAY)

    buf = io.BytesIO()
    b.save(buf)
    buf.seek(0)
    return buf.getvalue()
