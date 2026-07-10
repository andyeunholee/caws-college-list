# -*- coding: utf-8 -*-
"""
intake_parser.py
================
Parses a pasted intake-form / email text (the "Student Name: ... " questionnaire
that families send in) and builds the `STUDENT` dict consumed by
generate_college_report.py.

Usage
-----
    from intake_parser import parse_intake, build_student
    student = build_student(parse_intake(email_text))

Or from the command line, save the email to a .txt file and run:
    python generate_college_report.py intake_sample.txt

NOTE
----
This parser fills only the STUDENT *profile block* (name, info table, footer,
cycle line, output filename). The tiered college lists in `college_data.json`
are calibrated separately per student and are NOT produced here.
"""

import datetime
import re

# ---------------------------------------------------------------------------
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}
_NAME_TO_CODE = {v.lower(): k for k, v in US_STATES.items()}


# ---------------------------------------------------------------------------
# Label matching:  first rule whose keywords all appear (in the normalized key)
# wins. Order matters — more specific rules come first.
# ---------------------------------------------------------------------------
_LABEL_RULES = [
    ("high_school",  ["high school"]),
    ("sat_english",  ["sat", "english"]),
    ("sat_english",  ["sat", "ebrw"]),
    ("sat_english",  ["sat", "reading"]),
    ("sat_english",  ["sat", "verbal"]),
    ("sat_math",     ["sat", "math"]),
    ("sat_total",    ["sat", "total"]),
    ("sat_total",    ["sat", "composite"]),
    ("uw_gpa",       ["unweighted"]),
    ("w_gpa",        ["weighted"]),
    ("advanced",     ["ap", "ib"]),      # "Total Number of AP/IB/DE Courses"
    ("advanced",     ["number", "course"]),
    ("advanced",     ["advanced course"]),
    ("advanced",     ["dual enroll"]),
    ("major",        ["major"]),
    ("major",        ["field of study"]),
    ("early",        ["early"]),
    ("class_rank",   ["rank"]),
    ("race",         ["race"]),
    ("race",         ["ethnic"]),
    ("citizen",      ["citizen"]),
    ("leadership",   ["leadership"]),
    ("awards",       ["award"]),
    ("awards",       ["honor"]),
    ("service",      ["service"]),
    ("talents",      ["talent"]),
    ("talents",      ["significant activit"]),
    ("essays",       ["essay"]),
    ("essays",       ["recommendation"]),
    ("residence",    ["residence"]),
    ("num_colleges", ["how many college"]),
    ("num_colleges", ["number of college"]),
    ("want_lac",     ["liberal arts"]),
    ("additional",   ["additional information"]),
    ("name",         ["name"]),          # generic "name" last (after high school)
]


def _norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()


def _match_label(key):
    nk = _norm(key)
    for field, keywords in _LABEL_RULES:
        if all(kw in nk for kw in keywords):
            return field
    return None


def parse_intake(text):
    """Turn raw intake text into a dict of {canonical_field: value}.
    Handles values that wrap onto a following line."""
    fields, current = {}, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key, sep, val = line.partition(":")
        field = _match_label(key) if sep else None
        if field:
            fields[field] = val.strip()
            current = field
        elif current:                       # continuation of the previous value
            fields[current] = (fields[current] + " " + line).strip()
    return fields


# ---------------------------------------------------------------------------
def _int(value):
    if value is None:
        return None
    m = re.search(r"-?\d+", value.replace(",", ""))
    return int(m.group()) if m else None


def _blank(value):
    return (value is None) or value.strip() == "" or \
        value.strip().upper() in ("N/A", "NA", "NONE", "N.A.")


def _fix_comma_spacing(value):
    return re.sub(r"\s*,\s*", ", ", value).strip() if value else value


def _derive_state_name(*locations):
    """Return the full state name found in the location strings (HS first)."""
    for loc in locations:
        if not loc:
            continue
        # trailing 2-letter code, e.g. "..., GA"
        m = re.search(r",\s*([A-Za-z]{2})\b\s*$", loc.strip())
        if m and m.group(1).upper() in US_STATES:
            return US_STATES[m.group(1).upper()]
        # any full state name mentioned
        for name in _NAME_TO_CODE:
            if name in loc.lower():
                return US_STATES[_NAME_TO_CODE[name]]
        # any standalone 2-letter code
        for tok in re.findall(r"\b([A-Za-z]{2})\b", loc):
            if tok.upper() in US_STATES:
                return US_STATES[tok.upper()]
    return ""


def _current_cycle(today):
    y = today.year
    return f"{y}–{y + 1}" if today.month >= 7 else f"{y - 1}–{y}"


def build_student(f, *, grade="12th Grade (Senior)", cycle_years=None, today=None,
                  lang="Eng"):
    """Build the STUDENT dict from parsed intake fields `f`.

    `lang` sets the filename prefix: "Eng" for an English report, "Kor" for Korean.
    """
    today = today or datetime.date.today()
    cycle_years = cycle_years or _current_cycle(today)
    name = (f.get("name") or "Student").strip()

    # --- SAT ---------------------------------------------------------------
    e, m = _int(f.get("sat_english")), _int(f.get("sat_math"))
    if e is not None and m is not None:
        sat = f"{e + m} (EBRW {e} / Math {m})"
    elif not _blank(f.get("sat_total")):
        sat = f["sat_total"].strip()
    else:
        sat = "N/A"

    # --- advanced courses --------------------------------------------------
    n_adv = _int(f.get("advanced"))
    if n_adv == 0:
        advanced = "0 (no AP / IB / DE coursework)"
    elif n_adv is not None:
        advanced = f"{n_adv} (AP / IB / DE)"
    else:
        advanced = f.get("advanced", "N/A") or "N/A"

    # --- leadership --------------------------------------------------------
    n_lead = _int(f.get("leadership"))
    if n_lead is not None:
        advanced_plural = "position" if n_lead == 1 else "positions"
        leadership = f"{n_lead} leadership {advanced_plural}"
    else:
        leadership = f.get("leadership", "N/A") or "N/A"

    # --- community service -------------------------------------------------
    n_serv = _int(f.get("service"))
    service = f"~{n_serv} hours" if n_serv is not None else (f.get("service") or "N/A")

    # --- citizenship -------------------------------------------------------
    cit = f.get("citizen", "")
    if "yes" in cit.lower() or "u.s" in cit.lower() or "citizen" in cit.lower():
        citizen = "U.S. Citizen"
    else:
        citizen = cit.strip() or "N/A"

    # --- misc text fields --------------------------------------------------
    early = f.get("early", "")
    early = "Undecided (ED / EA / REA)" if (_blank(early) or "undecid" in early.lower()) else early
    awards = "None reported" if _blank(f.get("awards")) else f["awards"].strip()
    essays = f.get("essays", "")
    essays = "N/A" if _blank(essays) else re.sub(r"\s-\s", " — ", essays).strip()
    _slash = lambda v: re.sub(r"\s*/\s*", " / ", v).strip()
    talents = _slash(f.get("talents", "")) or "N/A"
    major = _slash(f.get("major", "")) or "N/A"
    residence = _fix_comma_spacing(f.get("residence", "")) or "N/A"
    high_school = _fix_comma_spacing(f.get("high_school", "")) or "N/A"
    uw = f.get("uw_gpa", "").strip() or "N/A"
    w = f.get("w_gpa", "").strip() or "N/A"
    rank = f.get("class_rank", "").strip() or "N/A"

    home_state = _derive_state_name(f.get("high_school"), f.get("residence"))

    safe_name = re.sub(r'[\\/:*?"<>|]', "", name)
    return {
        "name": name,
        "cycle_line": f"{cycle_years} Application Cycle · {grade}",
        "home_state": home_state,
        "footer": f"{name}  ·  {cycle_years}  ·  CONFIDENTIAL  ·  ",
        "output_name": f"{lang}-{safe_name}_College_List_Est._Admit_Rate_{today:%m.%d.%Y}.docx",
        "info": [
            ("Name", name),
            ("High School", high_school),
            ("Residence", residence),
            ("Unweighted GPA", uw),
            ("Weighted GPA", w),
            ("Class Rank", rank),
            ("SAT", sat),
            ("Advanced Courses", advanced),
            ("Intended Major", major),
            ("Early Plan", early),
            ("Leadership", leadership),
            ("Community Service", service),
            ("Talents / Key Activities", talents),
            ("Awards & Honors", awards),
            ("Essays & Recs", essays),
            ("Citizenship", citizen),
        ],
        # extra parsed fields (not shown in the info table, kept for reference)
        "_extra": {
            "race": f.get("race", ""),
            "num_colleges": f.get("num_colleges", ""),
            "want_lac": f.get("want_lac", ""),
            "additional": f.get("additional", ""),
        },
    }


if __name__ == "__main__":
    import json
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "intake_sample.txt"
    with open(src, encoding="utf-8") as fh:
        student = build_student(parse_intake(fh.read()))
    print(json.dumps({k: v for k, v in student.items() if k != "info"},
                     ensure_ascii=False, indent=2))
    print("\nINFO TABLE:")
    for label, value in student["info"]:
        print(f"  {label:26} | {value}")
