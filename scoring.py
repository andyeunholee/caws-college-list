# -*- coding: utf-8 -*-
"""
scoring.py — profile-adjusted admit-probability engine
======================================================
Turns a parsed intake into a structured profile, then computes a
profile-adjusted estimated admit probability for every college in the master
database and selects the Reach / Match / Safety lists (national, in-state, LAC)
plus the ED and EA tables.

Pure Python, deterministic, no network — safe for Streamlit Cloud.
All probabilities are heuristic estimates (the report says so explicitly).
"""

import math
import re

# ---- 2-letter <-> state name ----
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}
_NAME_TO_CODE = {v.lower(): k for k, v in US_STATES.items()}

# ---- ACT -> SAT concordance (College Board / ACT official-ish) ----
ACT_TO_SAT = {36: 1590, 35: 1540, 34: 1500, 33: 1460, 32: 1430, 31: 1400, 30: 1370,
              29: 1340, 28: 1310, 27: 1280, 26: 1240, 25: 1210, 24: 1180, 23: 1140,
              22: 1110, 21: 1080, 20: 1040, 19: 1010, 18: 970, 17: 930, 16: 890,
              15: 850, 14: 800, 13: 760, 12: 710, 11: 670}

MAJOR_COMPETITIVE = ["pre-med", "premed", "pre med", "pre-health", "prehealth", "pre health",
                     "medicine", "medical", "nursing", "computer science", "cs",
                     "engineer", "business", "biology", "neuroscience", "biomedical",
                     "data science", "finance", "economics"]


def _f(v):
    if v is None:
        return None
    m = re.search(r"-?\d+(\.\d+)?", str(v).replace(",", ""))
    return float(m.group()) if m else None


def _i(v):
    f = _f(v)
    return int(f) if f is not None else None


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ---------------------------------------------------------------- ACT parsing
def extract_act(raw_text):
    """Find an ACT composite anywhere in the intake (incl. Additional Info).
    Matches the whole word 'act' only, so it is not fooled by 'Activities'."""
    if not raw_text:
        return None
    low = raw_text.lower()
    for m in re.finditer(r"\bact\b", low):
        window = low[m.start():m.start() + 90]
        mcomp = re.search(r"composite[^0-9]{0,6}(\d{1,2})", window)
        if mcomp:
            n = int(mcomp.group(1))
            return n if 10 <= n <= 36 else None
        nums = [int(x) for x in re.findall(r"\b(\d{1,2})\b", window) if 10 <= int(x) <= 36]
        if nums:
            return int(round(sum(nums) / len(nums)))
    return None


def _essay_level(text):
    t = (text or "").lower()
    if any(w in t for w in ["excellent", "exceptional", "outstanding", "strong writing", "very strong"]):
        return "high"
    if any(w in t for w in ["solid", "good", "above average", "competitive"]):
        return "med"
    if any(w in t for w in ["developing", "working", "improving", "weak", "needs"]):
        return "low"
    return "med"


# ---------------------------------------------------------------- profile
def build_profile(fields, raw_text):
    name = (fields.get("name") or "Student").strip()
    home = ""
    for src in (fields.get("residence"), fields.get("high_school")):
        if not src:
            continue
        m = re.search(r",\s*([A-Za-z]{2})\b\s*$", src.strip())
        if m and m.group(1).upper() in US_STATES:
            home = m.group(1).upper(); break
        low = src.lower()
        for nm, code in _NAME_TO_CODE.items():
            if nm in low:
                home = code; break
        if home:
            break

    uw = _f(fields.get("uw_gpa"))
    w = _f(fields.get("w_gpa"))
    if uw is not None:
        gpa_used = uw
    elif w is not None:
        gpa_used = w if w <= 4.0 else clamp(3.6 + (w - 4.0) * 0.13, 3.0, 4.0)
    else:
        gpa_used = 3.3          # unknown -> neutral-ish

    e = _i(fields.get("sat_english"))
    m = _i(fields.get("sat_math"))
    sat_total = _i(fields.get("sat_total"))
    sat = None
    if e is not None and m is not None:
        sat = e + m
    elif sat_total is not None and sat_total > 400:
        sat = sat_total
    act = extract_act(raw_text)
    sat_equiv = sat
    native = "SAT"
    if sat_equiv is None and act is not None:
        sat_equiv = ACT_TO_SAT.get(act, 780 + int((act - 11) / 25.0 * 810))
        native = "ACT"
    has_test = sat_equiv is not None

    if sat is not None:
        test_display = "%d (EBRW %s / Math %s)" % (sat, e if e is not None else "?", m if m is not None else "?") \
            if (e is not None and m is not None) else "%d" % sat
    elif act is not None:
        test_display = "ACT %d (SAT eq. ~%d)" % (act, sat_equiv)
    else:
        test_display = "N/A"

    rigor = _i(fields.get("advanced"))
    rigor = rigor if rigor is not None else 0
    lead = _i(fields.get("leadership")); lead = lead if lead is not None else 0
    serv = _i(fields.get("service")); serv = serv if serv is not None else 0
    awards_raw = (fields.get("awards") or "").strip()
    awards_present = bool(awards_raw) and awards_raw.upper() not in ("N/A", "NA", "NONE")
    essays = _essay_level(fields.get("essays"))
    major = (fields.get("major") or "").strip()
    major_comp = any(k in major.lower() for k in MAJOR_COMPETITIVE)

    # ---- component scores (0-100) ----
    gpa_c = clamp((gpa_used - 2.5) / 1.5 * 100, 0, 100)
    test_c = clamp((sat_equiv - 780) / (1560 - 780) * 100, 0, 100) if has_test else None
    rigor_c = clamp(min(rigor, 12) / 12.0 * 100, 0, 100)
    soft_c = clamp(min(lead, 5) / 5.0 * 40
                   + min(serv, 200) / 200.0 * 20
                   + (20 if awards_present else 0)
                   + {"high": 20, "med": 10, "low": 0}[essays], 0, 100)

    # strength WITH test and WITHOUT test (for test-blind schools)
    if test_c is not None:
        S = 0.34 * gpa_c + 0.30 * test_c + 0.16 * rigor_c + 0.20 * soft_c
    else:
        S = 0.50 * gpa_c + 0.26 * rigor_c + 0.24 * soft_c
    S_no_test = 0.50 * gpa_c + 0.26 * rigor_c + 0.24 * soft_c

    return {
        "name": name, "home_state": home, "home_state_name": US_STATES.get(home, ""),
        "residence": fields.get("residence", ""), "high_school": fields.get("high_school", ""),
        "uw_gpa": uw, "w_gpa": w, "gpa_used": gpa_used,
        "sat": sat, "act": act, "sat_equiv": sat_equiv, "native": native,
        "has_test": has_test, "test_display": test_display,
        "rigor": rigor, "leadership": lead, "service": serv,
        "awards_present": awards_present, "essays": essays,
        "major": major or "Undecided", "major_competitive": major_comp,
        "citizen": fields.get("citizen", ""), "early": fields.get("early", ""),
        "S": S, "S_no_test": S_no_test,
        "gpa_c": gpa_c, "test_c": test_c, "rigor_c": rigor_c, "soft_c": soft_c,
    }


# ---------------------------------------------------------------- probability
def _logistic(x):
    return 1.0 / (1.0 + math.exp(-x))


def _expected(admit):
    """Approx. strength level (0-100) of a school's typical admitted student."""
    return clamp(96 - 0.85 * admit, 18, 96)


def _median_sat(admit):
    return 780 + _expected(admit) / 100.0 * 780


def prob_for(school, profile, instate=False, ed=False):
    admit = float(school["admit"])
    frac = admit / 100.0
    test = school.get("test", "optional")
    blind = test == "blind"
    S = profile["S_no_test"] if blind else profile["S"]
    fit = S - _expected(admit)

    # bounded model: floor for well-below applicants, ceiling that stays low for
    # ultra-selective schools (a lottery even for strong students).
    base = _logistic(0.11 * (fit + 4))
    lo = frac * 0.10
    hi = clamp(frac * 2.2 + 0.03, 0.06, 0.92)
    p = lo + (hi - lo) * base

    if not blind:
        if test == "optional":
            p *= 1.08
        elif test == "required" and not profile["has_test"]:
            p *= 0.75
        elif test == "required" and profile["has_test"] and profile["sat_equiv"] < _median_sat(admit):
            p *= 0.88
    if profile["major_competitive"]:
        p *= 0.92
    if instate and admit >= 25:          # in-state break mostly helps at publics
        p *= 1.25
    if ed:
        p *= 1.85
    return clamp(p, 0.003, 0.92)


# ---------------------------------------------------------------- display bucket
def bucket(p):
    pct = p * 100
    if pct < 1:
        return "<1%"
    if pct < 20:
        return "~%d%%" % int(round(pct))
    return "~%d%%" % int(round(pct / 5.0) * 5)


def tier_of(p):
    if p <= 0.20:
        return "reach"
    if p >= 0.60:
        return "safety"
    return "match"


# ---------------------------------------------------------------- selection
def _rows(entries):
    """entries: list of (prob, name, state) -> [[name,state,bucket],...] asc by prob."""
    entries = sorted(entries, key=lambda x: x[0])
    return [[n, s, bucket(p)] for p, n, s in entries]


def select_lists(profile, db):
    home = profile["home_state"]
    national = db["national"]
    lac = db["lac"]

    def tiered(pool, instate=False, per_tier=None):
        buckets = {"reach": [], "match": [], "safety": []}
        for sch in pool:
            p = prob_for(sch, profile, instate=instate)
            buckets[tier_of(p)].append((p, sch["name"], sch["state"]))
        out = {}
        for k in ("reach", "match", "safety"):
            rows = _rows(buckets[k])
            out[k] = rows[:per_tier] if per_tier else rows
        return out, {k: len(v) for k, v in buckets.items()}

    nat_pool = [s for s in national if s["state"] != home]
    national_lists, national_counts = tiered(nat_pool, per_tier=50)

    instate_pool = [s for s in national if s["state"] == home]
    instate_lists, _ = tiered(instate_pool, instate=True)

    lac_lists, _ = tiered(lac, per_tier=25)

    # ED table: ED-offering schools that land reach..match, sorted by RD prob
    ed_rows = []
    for sch in national + lac:
        if not sch.get("ed"):
            continue
        p = prob_for(sch, profile)
        if p > 0.58:
            continue
        ped = prob_for(sch, profile, ed=True)
        rec = ""
        if 0.30 <= ped <= 0.62 and p <= 0.55:
            rec = "★★ Strongly Recommend"
        elif 0.20 <= ped < 0.30:
            rec = "★ Recommend"
        ed_rows.append((p, [sch["name"], sch["state"], bucket(p), bucket(ped), rec]))
    ed_rows = [r for _p, r in sorted(ed_rows, key=lambda x: x[0])][:26]

    # EA table: EA/REA schools, mix, sorted by prob
    ea_rows = []
    for sch in national + lac:
        ea = sch.get("ea")
        if ea not in ("EA", "REA"):
            continue
        p = prob_for(sch, profile)
        note = ("Restrictive REA — no other private EA/ED" if ea == "REA" else "Unrestricted EA")
        if sch.get("test") == "required":
            note += " · SAT/ACT required"
        ea_rows.append((p, [sch["name"], sch["state"], bucket(p), note]))
    ea_rows = [r for _p, r in sorted(ea_rows, key=lambda x: x[0])][:38]

    return {
        "national": national_lists, "instate": instate_lists, "lac": lac_lists,
        "ed": ed_rows, "ea": ea_rows,
        "national_counts": national_counts,
        "instate_state_name": profile["home_state_name"] or "Home State",
    }
