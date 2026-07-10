# -*- coding: utf-8 -*-
"""
preview_html.py — self-contained HTML preview of the report
============================================================
Driven by the SAME (student, data, narr) that build the .docx, so the on-screen
preview and the downloaded Word file always match.
"""

import html as _h
from report_engine import NAVY, RED, GOLD, GREEN, TEXT, GRAY
from i18n import T

HEX = lambda c: "#" + c
KIND = {RED: "red", GOLD: "gold", GREEN: "green", NAVY: "navy", GRAY: "gray",
        "reach": "red", "match": "gold", "safety": "green", "navy": "navy"}


def _runs(run_list):
    out = []
    for text, bold, color, _s in run_list:
        t = _h.escape(text)
        if bold:
            out.append('<b style="color:%s">%s</b>' % (HEX(color), t))
        elif color != TEXT:
            out.append('<span style="color:%s">%s</span>' % (HEX(color), t))
        else:
            out.append(t)
    return "".join(out)


def _callout(kind, paras):
    inner = "".join('<span class="bullet">%s</span>' % _runs(rs) for rs, _a in paras)
    return '<div class="callout %s">%s</div>' % (kind, inner)


def _ltable(tier, rows, th, none_txt):
    h = ['<div class="tblwrap"><table class="ltable %s"><tr>'
         '<th>%s</th><th class="l">%s</th><th>%s</th><th>%s</th></tr>'
         % (tier, _h.escape(th[0]), _h.escape(th[1]), _h.escape(th[2]), _h.escape(th[3]))]
    for i, (c, s, p) in enumerate(rows, 1):
        h.append('<tr><td class="num">%d</td><td>%s</td><td class="c">%s</td>'
                 '<td class="prob">%s</td></tr>' % (i, _h.escape(c), _h.escape(s), _h.escape(p)))
    if not rows:
        h.append('<tr><td colspan="4" style="color:#888">%s</td></tr>' % _h.escape(none_txt))
    h.append("</table></div>")
    return "".join(h)


def _tiered(tiers, labels, L):
    out = []
    for key, label in zip(("reach", "match", "safety"), labels):
        out.append('<div class="tierbar %s">%s</div>' % (key, _h.escape(label)))
        out.append(_ltable(key, tiers.get(key, []), L["th_list"], L["none_tier"]))
    return "".join(out)


CSS = """
*{box-sizing:border-box}
body{margin:0;background:#e9edf2;padding:20px;font-family:'Malgun Gothic','Segoe UI',system-ui,sans-serif}
.paper{background:#fff;color:#222;max-width:820px;margin:0 auto;padding:44px 52px;border-radius:6px;
     box-shadow:0 1px 3px rgba(0,0,0,.12),0 16px 44px rgba(0,0,0,.16)}
.eyebrow{font-weight:800;letter-spacing:.22em;color:#1F3864;font-size:15px}
.eyebrow-sub{font-weight:700;color:#666;font-size:12.5px;border-bottom:2px solid #B7791F;padding-bottom:8px;margin-bottom:22px}
h1{font-size:29px;line-height:1.15;color:#1F3864;margin:14px 0 6px}
.p-name{font-size:22px;font-weight:800;color:#7D2230;margin:0 0 4px}
.p-cycle{color:#666;font-size:13px;margin:0 0 20px}
h2{font-size:20px;color:#1F3864;border-bottom:2px solid #1F3864;padding-bottom:6px;margin:32px 0 14px}
p.body{font-size:13px;line-height:1.6;color:#222;margin:0 0 12px}
.itable{width:100%;border-collapse:collapse;border:1px solid #d5d5d5;margin:4px 0}
.itable td{border:1px solid #e5e5e5;padding:6px 10px;font-size:12px;vertical-align:middle}
.itable td.k{background:#e8ecf4;color:#1F3864;font-weight:700;width:33%}
.itable tr:nth-child(even) td.v{background:#f4f4f4}
.callout{border-left:5px solid #1F3864;padding:12px 16px;margin:14px 0;border-radius:0 4px 4px 0;font-size:12.5px;line-height:1.55}
.callout .bullet{display:block;margin:3px 0}
.callout.gold{border-color:#B7791F;background:#FBF1DD}.callout.navy{border-color:#1F3864;background:#E8ECF4}
.callout.red{border-color:#7D2230;background:#F3E7E9}.callout.green{border-color:#2F7D32;background:#E7F1E8}
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
table.ltable.reach td.prob{color:#7D2230}table.ltable.match td.prob{color:#B7791F}table.ltable.safety td.prob{color:#2F7D32}
table.ltable.reach tr:nth-child(even) td{background:#F3E7E9}
table.ltable.match tr:nth-child(even) td{background:#FBF1DD}
table.ltable.safety tr:nth-child(even) td{background:#E7F1E8}
table.ltable.navy tr:nth-child(even) td{background:#f4f4f4}
.tblwrap{overflow-x:auto;margin:0 0 4px}
.c{text-align:center}.prob-gray{color:#666;font-weight:700}.prob-green{color:#2F7D32;font-weight:700}
.prob-navy{color:#1F3864;font-weight:700}.rec{color:#7D2230;font-weight:700}
"""


def preview_html(student, data, narr, lang="Eng"):
    L = T(lang)
    h = ['<!doctype html><html><head><meta charset="utf-8"><style>', CSS,
         '</style></head><body><div class="paper">']
    h.append('<div class="eyebrow">ELITE PREP</div>')
    h.append('<div class="eyebrow-sub">%s</div>' % _h.escape(L["subtitle"]))
    h.append('<h1>%s</h1>' % _h.escape(L["title"]))
    h.append('<div class="p-name">%s</div>' % _h.escape(student["name"]))
    h.append('<div class="p-cycle">%s</div>' % _h.escape(student["cycle_line"]))
    h.append('<table class="itable">')
    for k, v in student["info"]:
        h.append('<tr><td class="k">%s</td><td class="v">%s</td></tr>'
                 % (_h.escape(L["info"].get(k, k)), _h.escape(v)))
    h.append("</table>")
    h.append(_callout("gold", narr["note"]))

    h.append('<h2>%s</h2>' % _h.escape(L["sec"][1]))
    h.append('<p class="body">%s</p>' % _h.escape(narr["methodology"]))
    h.append('<p class="body">%s</p>' % _runs(narr["tier_def"]))
    bd = L["badges"]
    h.append('<div class="badges"><div class="badge reach">%s</div>'
             '<div class="badge match">%s</div><div class="badge safety">%s</div></div>'
             % (_h.escape(bd[0]), _h.escape(bd[1]), _h.escape(bd[2])))
    h.append(_callout("navy", narr["testing"]))
    h.append(_callout("red", narr["core"]))

    h.append('<h2>%s</h2>' % _h.escape(L["sec"][2]))
    h.append('<p class="body">%s</p>' % _h.escape(narr["national_intro"]))
    h.append(_tiered(data["national"], L["tier_long"], L))

    h.append('<h2>%s</h2>' % _h.escape(L["sec"][3] % data["instate_state_name"]))
    h.append('<p class="body">%s</p>' % _h.escape(narr["instate_intro"]))
    h.append(_tiered(data["instate"], L["tier_short"], L))

    h.append('<h2>%s</h2>' % _h.escape(L["sec"][4]))
    h.append('<p class="body">%s</p>' % _h.escape(narr["lac_intro"]))
    h.append(_tiered(data["lac"], L["tier_short"], L))

    te = L["th_ed"]
    h.append('<h2>%s</h2>' % _h.escape(L["sec"][5]))
    h.append('<p class="body">%s</p>' % _runs(narr["ed_intro"]))
    h.append('<div class="tblwrap"><table class="ltable navy"><tr><th class="l">%s</th>'
             '<th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>'
             % tuple(_h.escape(x) for x in te))
    for r in data["ed"]:
        h.append('<tr><td><b>%s</b></td><td class="c"><b>%s</b></td><td class="c prob-gray">%s</td>'
                 '<td class="c prob-green">%s</td><td class="c rec">%s</td></tr>'
                 % tuple(_h.escape(x) for x in r))
    h.append("</table></div>")
    h.append(_callout("navy", narr["ed_rec"]))

    ta = L["th_ea"]
    h.append('<h2>%s</h2>' % _h.escape(L["sec"][6]))
    h.append('<p class="body">%s</p>' % _runs(narr["ea_intro"]))
    h.append('<div class="tblwrap"><table class="ltable navy"><tr><th class="l">%s</th>'
             '<th>%s</th><th>%s</th><th class="l">%s</th></tr>' % tuple(_h.escape(x) for x in ta))
    for r in data["ea"]:
        h.append('<tr><td><b>%s</b></td><td class="c"><b>%s</b></td><td class="c prob-navy">%s</td>'
                 '<td class="prob-gray">%s</td></tr>' % tuple(_h.escape(x) for x in r))
    h.append("</table></div>")

    h.append('<h2>%s</h2>' % _h.escape(L["sec"][7]))
    h.append('<p class="body">%s</p>' % _h.escape(narr["action_intro"]))
    for accent_tier, box in narr["steps"]:
        h.append(_callout(KIND[accent_tier], box))

    tb = L["th_abbr"]
    h.append('<h2>%s</h2>' % _h.escape(L["sec"][8]))
    h.append('<p class="body">%s</p>' % _h.escape(L["abbr_intro"]))
    h.append('<div class="tblwrap"><table class="ltable navy"><tr>'
             '<th class="l">%s</th><th class="l">%s</th></tr>'
             % (_h.escape(tb[0]), _h.escape(tb[1])))
    for abbr, desc in narr["abbreviations"]:
        h.append('<tr><td><b style="color:#1F3864">%s</b></td><td><b>%s</b></td></tr>'
                 % (_h.escape(abbr), _h.escape(desc)))
    h.append("</table></div>")
    h.append(_callout("gray", narr["disclaimer"]))

    h.append("</div></body></html>")
    return "".join(h)
