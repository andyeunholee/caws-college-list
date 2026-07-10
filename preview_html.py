# -*- coding: utf-8 -*-
"""
preview_html.py
===============
Builds a self-contained HTML preview of the report (for st.components.v1.html).
Reuses the SAME narrative constants and college data that feed the .docx, so the
on-screen preview and the downloaded Word file stay in sync.
"""

import html as _h

from report_engine import NAVY, RED, GOLD, GREEN, TEXT, GRAY
import generate_college_report as gcr

HEX = lambda c: "#" + c
KIND = {RED: "red", GOLD: "gold", GREEN: "green", NAVY: "navy", GRAY: "gray"}


def _runs(run_list):
    out = []
    for text, bold, color, _size in run_list:
        t = _h.escape(text)
        if bold:
            out.append('<b style="color:%s">%s</b>' % (HEX(color), t))
        elif color != TEXT:
            out.append('<span style="color:%s">%s</span>' % (HEX(color), t))
        else:
            out.append(t)
    return "".join(out)


def _callout(kind, paras):
    inner = "".join('<span class="bullet">%s</span>' % _runs(rs) for rs, _after in paras)
    return '<div class="callout %s">%s</div>' % (kind, inner)


def _list_table(tier, rows):
    h = ['<div class="tblwrap"><table class="ltable %s"><tr>'
         '<th>No.</th><th class="l">College</th><th>State</th>'
         '<th>Est. Admit Probability</th></tr>' % tier]
    for i, (college, state, prob) in enumerate(rows, 1):
        h.append('<tr><td class="num">%d</td><td>%s</td><td class="c">%s</td>'
                 '<td class="prob">%s</td></tr>'
                 % (i, _h.escape(college), _h.escape(state), _h.escape(prob)))
    h.append("</table></div>")
    return "".join(h)


def _tiered(tiers, labels):
    out = []
    for key, label in zip(("reach", "match", "safety"), labels):
        out.append('<div class="tierbar %s">%s</div>' % (key, _h.escape(label)))
        out.append(_list_table(key, tiers[key]))
    return "".join(out)


CSS = """
*{box-sizing:border-box}
body{margin:0;background:#e9edf2;padding:20px;
     font-family:'Malgun Gothic','Segoe UI',system-ui,sans-serif}
.paper{background:#fff;color:#222;max-width:820px;margin:0 auto;padding:44px 52px;border-radius:6px;
     box-shadow:0 1px 3px rgba(0,0,0,.12),0 16px 44px rgba(0,0,0,.16)}
.eyebrow{font-weight:800;letter-spacing:.22em;color:#1F3864;font-size:15px}
.eyebrow-sub{font-weight:700;color:#666;font-size:12.5px;border-bottom:2px solid #B7791F;
     padding-bottom:8px;margin-bottom:22px}
h1{font-size:29px;line-height:1.15;color:#1F3864;margin:14px 0 6px}
.p-name{font-size:22px;font-weight:800;color:#7D2230;margin:0 0 4px}
.p-cycle{color:#666;font-size:13px;margin:0 0 20px}
h2{font-size:20px;color:#1F3864;border-bottom:2px solid #1F3864;padding-bottom:6px;margin:32px 0 14px}
p.body{font-size:13px;line-height:1.6;color:#222;margin:0 0 12px}
.itable{width:100%;border-collapse:collapse;border:1px solid #d5d5d5;margin:4px 0}
.itable td{border:1px solid #e5e5e5;padding:6px 10px;font-size:12px;vertical-align:middle}
.itable td.k{background:#e8ecf4;color:#1F3864;font-weight:700;width:33%}
.itable tr:nth-child(even) td.v{background:#f4f4f4}
.callout{border-left:5px solid #1F3864;padding:12px 16px;margin:14px 0;border-radius:0 4px 4px 0;
     font-size:12.5px;line-height:1.55}
.callout .bullet{display:block;margin:3px 0}
.callout.gold{border-color:#B7791F;background:#FBF1DD}
.callout.navy{border-color:#1F3864;background:#E8ECF4}
.callout.red{border-color:#7D2230;background:#F3E7E9}
.callout.green{border-color:#2F7D32;background:#E7F1E8}
.callout.gray{border-color:#666;background:#F2F2F2;color:#666}
.badges{display:grid;grid-template-columns:1fr 1fr 1fr;margin:14px 0}
.badge{padding:7px 12px;font-weight:700;font-size:12px}
.badge.reach{border-left:4px solid #7D2230;background:#F3E7E9;color:#7D2230}
.badge.match{border-left:4px solid #B7791F;background:#FBF1DD;color:#B7791F}
.badge.safety{border-left:4px solid #2F7D32;background:#E7F1E8;color:#2F7D32}
.tierbar{color:#fff;font-weight:700;font-size:15px;padding:8px 12px;margin:20px 0 0}
.tierbar.reach{background:#7D2230}.tierbar.match{background:#B7791F}.tierbar.safety{background:#2F7D32}
table.ltable{width:100%;border-collapse:collapse;border:1px solid #d5d5d5;font-size:12px}
table.ltable th{color:#fff;font-weight:700;padding:6px 8px;text-align:center}
table.ltable th.l{text-align:left}
table.ltable.reach th{background:#7D2230}table.ltable.match th{background:#B7791F}
table.ltable.safety th{background:#2F7D32}table.ltable.navy th{background:#1F3864}
table.ltable td{border:1px solid #e5e5e5;padding:5px 8px;vertical-align:middle}
table.ltable td.num,table.ltable td.c{text-align:center;font-variant-numeric:tabular-nums}
table.ltable td.prob{text-align:center;font-weight:700;font-variant-numeric:tabular-nums}
table.ltable.reach td.prob{color:#7D2230}table.ltable.match td.prob{color:#B7791F}
table.ltable.safety td.prob{color:#2F7D32}
table.ltable.reach tr:nth-child(even) td{background:#F3E7E9}
table.ltable.match tr:nth-child(even) td{background:#FBF1DD}
table.ltable.safety tr:nth-child(even) td{background:#E7F1E8}
table.ltable.navy tr:nth-child(even) td{background:#f4f4f4}
.tblwrap{overflow-x:auto;margin:0 0 4px}
.c{text-align:center}.prob-gray{color:#666;font-weight:700}.prob-green{color:#2F7D32;font-weight:700}
.prob-navy{color:#1F3864;font-weight:700}.rec{color:#7D2230;font-weight:700}
"""


def preview_html(student, data):
    h = ['<!doctype html><html><head><meta charset="utf-8"><style>', CSS,
         '</style></head><body><div class="paper">']
    h.append('<div class="eyebrow">ELITE PREP</div>')
    h.append('<div class="eyebrow-sub">College Admissions Strategy Report</div>')
    h.append('<h1>Comprehensive College Admissions Strategy Report</h1>')
    h.append('<div class="p-name">%s</div>' % _h.escape(student["name"]))
    h.append('<div class="p-cycle">%s</div>' % _h.escape(student["cycle_line"]))
    h.append('<table class="itable">')
    for k, v in student["info"]:
        h.append('<tr><td class="k">%s</td><td class="v">%s</td></tr>'
                 % (_h.escape(k), _h.escape(v)))
    h.append("</table>")
    h.append(_callout("gold", gcr.NOTE_BOX))

    h.append('<h2>1.&nbsp; Methodology · Evaluation Criteria</h2>')
    h.append('<p class="body">%s</p>' % _h.escape(gcr.METHODOLOGY_INTRO))
    h.append('<p class="body">%s</p>' % _runs(gcr.TIER_DEF))
    h.append('<div class="badges"><div class="badge reach">Reach · Est. ≤ 20%</div>'
             '<div class="badge match">Match · Est. 21–55%</div>'
             '<div class="badge safety">Safety · Est. ≥ 60%</div></div>')
    h.append(_callout("navy", gcr.TESTING_BOX))
    h.append(_callout("red", gcr.CORE_BOX))

    h.append('<h2>2.&nbsp; National University List</h2>')
    h.append('<p class="body">%s</p>' % _h.escape(gcr.NATIONAL_INTRO))
    h.append(_tiered(data["national"], ["REACH (Est. Admit Probability ≤ 20%)",
             "MATCH (Est. Admit Probability 21–55%)", "SAFETY (Est. Admit Probability ≥ 60%)"]))

    h.append('<h2>3.&nbsp; In-State Universities · Georgia</h2>')
    h.append('<p class="body">%s</p>' % _h.escape(gcr.INSTATE_INTRO))
    h.append(_tiered(data["instate_ga"], ["REACH", "MATCH", "SAFETY"]))

    h.append('<h2>4.&nbsp; Liberal Arts College (LAC) List</h2>')
    h.append('<p class="body">%s</p>' % _h.escape(gcr.LAC_INTRO))
    h.append(_tiered(data["lac"], ["REACH", "MATCH", "SAFETY"]))

    h.append('<h2>5.&nbsp; Early Decision (ED) Strategy · RD vs ED Comparison</h2>')
    h.append('<p class="body">%s</p>' % _runs(gcr.ED_INTRO))
    h.append('<div class="tblwrap"><table class="ltable navy"><tr><th class="l">College</th>'
             '<th>State</th><th>RD Prob.</th><th>ED Prob.</th><th>Recommendation</th></tr>')
    for college, state, rd, ed, rec in data["ed"]:
        h.append('<tr><td><b>%s</b></td><td class="c"><b>%s</b></td>'
                 '<td class="c prob-gray">%s</td><td class="c prob-green">%s</td>'
                 '<td class="c rec">%s</td></tr>'
                 % (_h.escape(college), _h.escape(state), _h.escape(rd),
                    _h.escape(ed), _h.escape(rec)))
    h.append("</table></div>")
    h.append(_callout("navy", gcr.ED_REC_BOX))

    h.append('<h2>6.&nbsp; Early Action (EA / REA) Strategy</h2>')
    h.append('<p class="body">%s</p>' % _runs(gcr.EA_INTRO))
    h.append('<div class="tblwrap"><table class="ltable navy"><tr><th class="l">College</th>'
             '<th>State</th><th>EA Prob.</th><th class="l">Notes (Policy / Caution)</th></tr>')
    for college, state, ea, notes in data["ea"]:
        h.append('<tr><td><b>%s</b></td><td class="c"><b>%s</b></td>'
                 '<td class="c prob-navy">%s</td><td class="prob-gray">%s</td></tr>'
                 % (_h.escape(college), _h.escape(state), _h.escape(ea), _h.escape(notes)))
    h.append("</table></div>")

    h.append('<h2>7.&nbsp; 12th-Grade Action Plan (From Now Through Application)</h2>')
    h.append('<p class="body">%s</p>' % _h.escape(gcr.ACTION_INTRO))
    for accent_tier, box in gcr.STEP_BOXES:
        h.append(_callout(KIND[gcr.BOX_ACCENT[accent_tier]], box))

    h.append('<h2>8.&nbsp; Abbreviations · Full Description</h2>')
    h.append('<p class="body">Full names and meanings of the abbreviations used in this '
             'report and its key notes.</p>')
    h.append('<div class="tblwrap"><table class="ltable navy"><tr>'
             '<th class="l">Abbreviation</th><th class="l">Full Description</th></tr>')
    for abbr, desc in gcr.ABBREVIATIONS:
        h.append('<tr><td><b style="color:#1F3864">%s</b></td><td><b>%s</b></td></tr>'
                 % (_h.escape(abbr), _h.escape(desc)))
    h.append("</table></div>")
    h.append(_callout("gray", gcr.DISCLAIMER_BOX))

    h.append("</div></body></html>")
    return "".join(h)
