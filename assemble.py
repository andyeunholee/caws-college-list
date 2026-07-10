# -*- coding: utf-8 -*-
"""
assemble.py — build the .docx from dynamic (student, data, narrative), bilingual
"""

import io

from report_engine import ReportBuilder, NAVY, RED, GOLD, GREEN, TEXT, GRAY
from i18n import T

BOX_BG = {"reach": "F3E7E9", "match": "FBF1DD", "safety": "E7F1E8", "navy": "E8ECF4"}
BOX_ACCENT = {"reach": RED, "match": GOLD, "safety": GREEN, "navy": NAVY}


def _rows(triples):
    return [(i + 1, c, s, p) for i, (c, s, p) in enumerate(triples)]


def _tiered(b, tiers, labels, L):
    for i, (key, label) in enumerate(zip(("reach", "match", "safety"), labels)):
        if i > 0:
            b.spacer(after=60)
        b.tier_label(key, label)
        rows = tiers.get(key, [])
        if rows:
            b.list_table(key, _rows(rows), headers=L["th_list"])
        else:
            b.body([(L["none_tier"], False, GRAY, 18)], after=40)


def assemble_bytes(student, data, narr, lang="Eng"):
    L = T(lang)
    b = ReportBuilder()
    b.build_header(L["subtitle"])
    b.build_footer(student["footer"])

    b.title_block(student["name"], student["cycle_line"], subtitle=L["subtitle"], title=L["title"])
    info = [(L["info"].get(k, k), v) for k, v in student["info"]]
    b.info_table(info)
    b.spacer()
    b.box(narr["note"], bg=BOX_BG["match"], accent=GOLD)
    b.page_break()

    b.heading(L["sec"][1])
    b.body([(narr["methodology"], False, TEXT, 20)])
    b.body(narr["tier_def"], after=120, line=276)
    b.tier_badges(labels=L["badges"])
    b.spacer()
    b.box(narr["testing"], bg=BOX_BG["navy"], accent=NAVY)
    b.spacer()
    b.box(narr["core"], bg=BOX_BG["reach"], accent=RED)
    b.spacer()

    b.heading(L["sec"][2])
    b.body([(narr["national_intro"], False, TEXT, 20)])
    _tiered(b, data["national"], L["tier_long"], L)

    b.heading(L["sec"][3] % data["instate_state_name"])
    b.body([(narr["instate_intro"], False, TEXT, 20)])
    _tiered(b, data["instate"], L["tier_short"], L)

    b.heading(L["sec"][4])
    b.body([(narr["lac_intro"], False, TEXT, 20)])
    _tiered(b, data["lac"], L["tier_short"], L)

    b.heading(L["sec"][5])
    b.body(narr["ed_intro"], after=160)
    if data["ed"]:
        te = L["th_ed"]
        b._generic_table([3640, 720, 1320, 1320, 2360],
                         [(te[0], "left"), (te[1], "center"), (te[2], "center"),
                          (te[3], "center"), (te[4], "center")],
                         [[(r[0], "left", True, TEXT), (r[1], "center", True, TEXT),
                           (r[2], "center", True, GRAY), (r[3], "center", True, GREEN),
                           (r[4], "center", True, RED)] for r in data["ed"]])
    else:
        b.body([(L["ed_none"], False, GRAY, 18)])
    b.box(narr["ed_rec"], bg=BOX_BG["navy"], accent=NAVY)
    b.spacer()

    b.heading(L["sec"][6])
    b.body(narr["ea_intro"], after=160)
    if data["ea"]:
        ta = L["th_ea"]
        b._generic_table([3600, 720, 1320, 3720],
                         [(ta[0], "left"), (ta[1], "center"), (ta[2], "center"), (ta[3], "left")],
                         [[(r[0], "left", True, TEXT), (r[1], "center", True, TEXT),
                           (r[2], "center", True, NAVY), (r[3], "left", True, GRAY)] for r in data["ea"]])
    else:
        b.body([(L["ea_none"], False, GRAY, 18)])
    b.spacer()

    b.heading(L["sec"][7])
    b.body([(narr["action_intro"], False, TEXT, 20)])
    for accent_tier, box in narr["steps"]:
        b.box(box, bg=BOX_BG[accent_tier], accent=BOX_ACCENT[accent_tier])
    b.spacer()

    b.heading(L["sec"][8])
    b.body([(L["abbr_intro"], False, TEXT, 20)])
    ta = L["th_abbr"]
    b._generic_table([2400, 6960], [(ta[0], "left"), (ta[1], "left")],
                     [[(a, "left", True, NAVY), (d, "left", True, TEXT)] for a, d in narr["abbreviations"]])
    b.spacer()
    b.box(narr["disclaimer"], bg="F2F2F2", accent=GRAY)

    buf = io.BytesIO()
    b.save(buf)
    buf.seek(0)
    return buf.getvalue()
