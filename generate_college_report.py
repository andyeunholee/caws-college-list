# -*- coding: utf-8 -*-
"""
generate_college_report.py
===========================
Generates a "Comprehensive College Admissions Strategy Report" .docx that is
formatted IDENTICALLY to the Elite Prep reference template
(Eng-Sydney Bang-La_College_List_Strategy_CE_06.30.2026.docx).

It is fully data-driven:
  * STUDENT   – the student's profile (edit this block per student)
  * NARRATIVE – the tailored prose for each section
  * college_data.json – the tiered college lists + ED/EA tables

Run:  python generate_college_report.py
Output: Eng-<Name>_College_List_Strategy_CE_<MM.DD.YYYY>.docx

Requires: python-docx   (pip install python-docx)
"""

import json
import os

from report_engine import ReportBuilder, NAVY, RED, GOLD, GREEN, TEXT, GRAY

HERE = os.path.dirname(os.path.abspath(__file__))


# ===========================================================================
#  1. STUDENT PROFILE  (edit per student)
# ===========================================================================
STUDENT = {
    "name": "Sumin Yoon",
    "cycle_line": "2026–2027 Application Cycle · 12th Grade (Senior)",
    "home_state": "Georgia",
    "footer": "Sumin Yoon  ·  2026–2027  ·  CONFIDENTIAL  ·  ",
    "output_name": "Eng-Sumin Yoon_College_List_Est._Admit_Rate_07.10.2026.docx",
    "info": [
        ("Name", "Sumin Yoon"),
        ("High School", "Mill Creek High School, Hoschton, GA"),
        ("Residence", "Auburn, GA"),
        ("Unweighted GPA", "N/A"),
        ("Weighted GPA", "3.5"),
        ("Class Rank", "N/A"),
        ("SAT", "980 (EBRW 500 / Math 480)"),
        ("Advanced Courses", "0 (no AP / IB / DE coursework)"),
        ("Intended Major", "Pre-Health / Pre-Med"),
        ("Early Plan", "Undecided (ED / EA / REA)"),
        ("Leadership", "0 leadership positions"),
        ("Community Service", "~50 hours"),
        ("Talents / Key Activities", "Music (instrumental / vocal)"),
        ("Awards & Honors", "None reported"),
        ("Essays & Recs", "Developing — improving writing and building recommender relationships"),
        ("Citizenship", "U.S. Citizen"),
    ],
}


# ===========================================================================
#  2. NARRATIVE  (tailored prose; run = (text, bold, color, size_half_pts))
# ===========================================================================
S = "Sumin"

NOTE_BOX = [
    ([("All admission probabilities in this report are ", False, TEXT, 18),
      ("‘profile-adjusted estimated probabilities’ based on the student’s individual profile",
       True, NAVY, 18),
      (". They are not the colleges’ published overall acceptance rates; each school is "
       "re-calibrated into Reach/Match/Safety from Sumin’s GPA, SAT, course rigor, "
       "extracurriculars, and essay/recommendation strength.", False, TEXT, 18)], 0),
]

METHODOLOGY_INTRO = (
    "Sumin’s application is at an early, developing stage across most dimensions — a "
    "weighted GPA of 3.5 with no AP/IB/DE coursework, an SAT of 980 (EBRW 500 / Math 480), no "
    "leadership roles yet, and roughly 50 community-service hours. She intends to pursue a "
    "Pre-Health / Pre-Med track, one of the most competitive intended pathways, which raises the "
    "bar further. The SAT score and the absence of course rigor are the two biggest variables in "
    "the current profile — and, fortunately, the two most efficient areas to strengthen "
    "before applications are filed."
)

TIER_DEF = [
    ("Tier Definitions — ", True, NAVY, 19),
    ("Reach: estimated admit probability ~20% or below · Match: ~21–55% · Safety: "
     "~60% or above. ‘<1%’ denotes a statistically extremely low case.", False, TEXT, 19),
]

TESTING_BOX = [
    ([("2026–2027 Cycle: Testing Policy — What Matters for Sumin", True, NAVY, 19)], 60),
    ([("· ", True, NAVY, 18),
      ("Georgia’s public universities (University System of Georgia — UGA, Georgia Tech, "
       "Georgia State, Kennesaw State, etc.) require the SAT/ACT. For these in-state schools the "
       "980 is counted and currently works against her, so raising it is the single highest-value "
       "move for the Georgia list.", False, TEXT, 18)], 40),
    ([("· ", True, NAVY, 18),
      ("Many national private universities are test-optional. With a 980 that sits below their "
       "published medians, withholding the score is usually the stronger play — an omitted "
       "score reads better than a clearly below-median one at these schools.", False, TEXT, 18)], 40),
    ([("· ", True, NAVY, 18),
      ("Several large public flagships (e.g., Florida and others) also require testing; confirm "
       "each school’s policy before deciding whether to submit.", False, TEXT, 18)], 40),
    ([("· ", True, NAVY, 18),
      ("Because ~80% of applicants at selective privates now submit scores, the most durable fix "
       "is to raise the score itself rather than rely on test-optional as a permanent shield.",
       False, TEXT, 18)], 0),
]

CORE_BOX = [
    ([("Core Strategy in One Line", True, RED, 19)], 60),
    ([("Raising the SAT from 980 toward 1100–1150+ (Math has the most room) and adding at "
       "least one rigorous course (AP or Georgia Dual Enrollment) reshapes the list the most. "
       "Paired with a single non-binding EA — or one carefully chosen ED — at a "
       "well-matched, test-optional Match school, this converts several ‘Reach’ schools "
       "into realistic ‘Match’ targets while a pre-health-friendly Safety base keeps the "
       "plan secure.", False, TEXT, 20)], 0),
]

NATIONAL_INTRO = (
    "Below are 150 national universities across the U.S., excluding Georgia-based schools and "
    "Liberal Arts Colleges (LACs) — 50 schools per tier. Tiers reflect Sumin’s "
    "profile-adjusted probability, not each school’s overall admit rate."
)

INSTATE_INTRO = (
    "Georgia universities in Sumin’s state of residence and graduation (LACs excluded). "
    "University System of Georgia campuses require SAT/ACT scores, so the 980 is factored in here; "
    "because Georgia residency lowers cost and widens capacity at these public schools — and "
    "unlocks the HOPE/Zell Miller scholarships — they remain strategically valuable, and a "
    "higher SAT would lift every probability in this section."
)

LAC_INTRO = (
    "LACs are small, undergraduate-focused colleges known for close faculty mentorship, small "
    "discussion classes, and strong writing and pre-health advising. Many remain test-optional, "
    "which suits Sumin’s current 980 well, and their smaller pre-med cohorts can mean more "
    "individual support. (Although ‘No’ was selected for LACs on the intake form, they are "
    "included here for reference because the test-optional fit and advising model can genuinely "
    "help this profile.)"
)

ED_INTRO = [
    ("ED is ", False, TEXT, 20),
    ("a binding early application that obligates enrollment upon admission", True, RED, 20),
    (", usable at only one school. Colleges treat ED applicants as ‘first-choice "
     "applicants’ and grant higher admit rates; for Sumin’s profile, ED roughly ", False, TEXT, 20),
    ("1.7–2×", True, TEXT, 20),
    (" the estimated probability. In the table below, the ", False, TEXT, 20),
    ("★/★★ marked schools", True, NAVY, 20),
    (" are the best-fit candidates that ‘settle into the Match range with the ED boost.’",
     False, TEXT, 20),
]

ED_REC_BOX = [
    ([("ED Recommendation", True, NAVY, 19)], 60),
    ([("If Sumin decides to use ED, the strongest single-card targets are the test-optional Match "
       "schools — American · University of Denver · Drexel · George Washington "
       "· Marquette · Dickinson — where the binding boost lifts her into roughly the "
       "~55–62% range. Spending the binding card on ultra-selective Reaches (Ivies, Duke, "
       "Northwestern) is inefficient, since they stay in the low single digits even with ED. "
       "Because ED is binding, use it only for a school she would attend if admitted — and "
       "confirm the financial-aid fit first.", False, TEXT, 18)], 0),
]

EA_INTRO = [
    ("EA is ", False, TEXT, 20),
    ("a non-binding early application", True, RED, 20),
    (" — no obligation to enroll if admitted — so Sumin can apply EA to several schools "
     "at once and collect early decisions plus priority Honors/scholarship review. A few schools "
     "use ", False, TEXT, 20),
    ("REA/SCEA", True, NAVY, 20),
    (" (restrictive single-choice) that cannot be combined with other private EA/ED. Several "
     "Georgia and Southern publics also read EA/priority applications on a rolling basis, so "
     "applying early is strongly advised.", False, TEXT, 20),
]

ACTION_INTRO = (
    "Sumin is currently in 12th grade. The steps below are ordered by impact, highest first, to "
    "raise admit odds from now through the application deadlines."
)

STEP_BOXES = [
    ("reach", [
        ([("STEP 1. ", True, RED, 18), ("Retake the SAT — the highest-impact move", True, NAVY, 18)], 60),
        ([("· ", True, RED, 18),
          ("Goal: 980 → 1100–1150+ (Math 480 has the most room to rise). Even a 100–150 "
           "point gain moves several current Reach schools into Match and lifts every Georgia-public "
           "probability.", False, TEXT, 18)], 40),
        ([("· ", True, RED, 18),
          ("Fall 2026 test dates: Aug 22 (recommended), Sep 12, Oct 3 — allowing 1–2 "
           "sittings before EA/ED and USG priority deadlines (many Nov 1).", False, TEXT, 18)], 40),
        ([("· ", True, RED, 18),
          ("Plan a focused 6–8 week sprint weighted toward Math, with 3–4 full-length timed "
           "practice tests (free official prep via Khan Academy / Bluebook).", False, TEXT, 18)], 40),
        ([("· ", True, RED, 18),
          ("At test-optional schools a 1100+ becomes worth submitting; below that, apply "
           "test-optional.", False, TEXT, 18)], 0),
    ]),
    ("match", [
        ([("STEP 2. ", True, GOLD, 18), ("Add course rigor and protect senior grades", True, NAVY, 18)], 60),
        ([("· ", True, GOLD, 18),
          ("With 0 AP/IB/DE on the transcript, enroll in one or two rigorous courses this year "
           "— AP, or Georgia Dual Enrollment (MOWR / eCore) at a nearby college — "
           "prioritizing science and math for the pre-med narrative.", False, TEXT, 18)], 40),
        ([("· ", True, GOLD, 18),
          ("Senior-year grades still reach colleges through mid-year and final reports; a strong, "
           "upward-trending semester directly improves the profile.", False, TEXT, 18)], 40),
        ([("· ", True, GOLD, 18),
          ("Even one college-level science course with a good grade signals readiness for a "
           "demanding pre-health path.", False, TEXT, 18)], 0),
    ]),
    ("safety", [
        ([("STEP 3. ", True, GREEN, 18), ("Build the story: essays, activities, service", True, NAVY, 18)], 60),
        ([("· ", True, GREEN, 18),
          ("Essays are ‘Developing’ — start the Common App main essay now and revise "
           "heavily toward a genuine, specific narrative (music as discipline and identity, why "
           "medicine).", False, TEXT, 18)], 40),
        ([("· ", True, GREEN, 18),
          ("Turn music (instrumental/vocal) into a documented commitment, and add a role that shows "
           "initiative — tutoring, a club officer position, or a health-related volunteer "
           "setting.", False, TEXT, 18)], 40),
        ([("· ", True, GREEN, 18),
          ("Grow the 50 service hours toward 100+, ideally in a clinical or community-health "
           "context that supports the pre-med direction.", False, TEXT, 18)], 0),
    ]),
    ("navy", [
        ([("STEP 4. ", True, NAVY, 18), ("Recommendations, early plan, and finances", True, NAVY, 18)], 60),
        ([("· ", True, NAVY, 18),
          ("Ask two teachers (ideally one in science/math) for recommendations in Aug–Sep and "
           "give them a short brag-sheet of specifics.", False, TEXT, 18)], 40),
        ([("· ", True, NAVY, 18),
          ("Decide the early plan: apply EA broadly (non-binding) and consider ONE ED only at a "
           "test-optional Match she loves and can afford.", False, TEXT, 18)], 40),
        ([("· ", True, NAVY, 18),
          ("File the FAFSA (opens October) and any required CSS Profile on time, and confirm "
           "Georgia HOPE/Zell Miller eligibility for the in-state options.", False, TEXT, 18)], 0),
    ]),
]

ABBREVIATIONS = [
    ("GPA", "Grade Point Average — academic performance average"),
    ("UW GPA", "Unweighted GPA — unweighted average (4.0 scale)"),
    ("W GPA", "Weighted GPA — weighted for AP/Honors/DE courses"),
    ("SAT", "Scholastic Assessment Test — U.S. college-entrance standardized test"),
    ("EBRW", "Evidence-Based Reading and Writing — SAT verbal (reading & writing) section"),
    ("ACT", "American College Testing — standardized test, SAT alternative"),
    ("AP", "Advanced Placement — college-level high school coursework"),
    ("IB", "International Baccalaureate — international diploma program"),
    ("DE", "Dual Enrollment — college credit earned during high school"),
    ("MOWR", "Move On When Ready — Georgia’s dual-enrollment program (college credit in HS)"),
    ("eCore", "Georgia’s online core-curriculum college courses (USG)"),
    ("ED", "Early Decision — binding early application (must enroll if admitted)"),
    ("EA", "Early Action — non-binding early application (no obligation to enroll)"),
    ("REA / SCEA", "Restrictive / Single-Choice Early Action — restricted single-choice early application"),
    ("RD", "Regular Decision — standard application round"),
    ("LAC", "Liberal Arts College — undergraduate-focused liberal arts institution"),
    ("USG", "University System of Georgia — Georgia public university system (test-required)"),
    ("OOS", "Out-of-State — applicant from another state"),
    ("Pre-Med / Pre-Health", "undergraduate track preparing for medical / health professional school"),
    ("CDS", "Common Data Set — official university statistics"),
    ("FAFSA", "Free Application for Federal Student Aid — federal financial-aid application"),
    ("CSS Profile", "College Scholarship Service Profile — private-school financial-aid application"),
    ("HOPE / Zell Miller", "Georgia merit scholarships for eligible in-state students"),
    ("test-optional", "policy letting the applicant choose whether to submit test scores"),
    ("test-required", "policy that requires SAT/ACT scores for admission review"),
]

DISCLAIMER_BOX = [
    ([("Disclaimer", True, GRAY, 18),
      ("   All figures are ‘estimated admit probabilities’ based on Sumin’s profile, "
       "not official college acceptance rates. Each school’s policies, deadlines, and testing "
       "requirements change every cycle, so always confirm finally on each college’s official "
       "admissions page before applying.", True, GRAY, 18)], 0),
]


# ===========================================================================
#  3. ASSEMBLY
# ===========================================================================
def _rows(triples):
    """[[college, state, prob], ...] -> [(no, college, state, prob), ...]"""
    return [(i + 1, c, s, p) for i, (c, s, p) in enumerate(triples)]


def build(student, data, out_path):
    b = ReportBuilder()
    b.build_header("College Admissions Strategy Report")
    b.build_footer(student["footer"])

    # --- cover / profile ---------------------------------------------------
    b.title_block(student["name"], student["cycle_line"])
    b.info_table(student["info"])
    b.spacer()
    b.box(NOTE_BOX, bg=GOLD_BOX_BG, accent=GOLD)
    b.page_break()

    # --- 1. Methodology ----------------------------------------------------
    b.heading("1.  Methodology · Evaluation Criteria")
    b.body([(METHODOLOGY_INTRO, False, TEXT, 20)])
    b.body(TIER_DEF, after=120, line=276)
    b.tier_badges()
    b.spacer()
    b.box(TESTING_BOX, bg=NAVY_BOX_BG, accent=NAVY)
    b.spacer()
    b.box(CORE_BOX, bg=RED_BOX_BG, accent=RED)
    b.spacer()

    # --- 2. National list --------------------------------------------------
    b.heading("2.  National University List")
    b.body([(NATIONAL_INTRO, False, TEXT, 20)])
    _tiered_lists(b, data["national"],
                  labels=("REACH (Est. Admit Probability ≤ 20%)",
                          "MATCH (Est. Admit Probability 21–55%)",
                          "SAFETY (Est. Admit Probability ≥ 60%)"))

    # --- 3. In-state (Georgia) --------------------------------------------
    b.heading("3.  In-State Universities · Georgia")
    b.body([(INSTATE_INTRO, False, TEXT, 20)])
    _tiered_lists(b, data["instate_ga"], labels=("REACH", "MATCH", "SAFETY"))

    # --- 4. Liberal Arts Colleges -----------------------------------------
    b.heading("4.  Liberal Arts College (LAC) List")
    b.body([(LAC_INTRO, False, TEXT, 20)])
    _tiered_lists(b, data["lac"], labels=("REACH", "MATCH", "SAFETY"))

    # --- 5. Early Decision -------------------------------------------------
    b.heading("5.  Early Decision (ED) Strategy · RD vs ED Comparison")
    b.body(ED_INTRO, after=160)
    _ed_table(b, data["ed"])
    b.box(ED_REC_BOX, bg=NAVY_BOX_BG, accent=NAVY)
    b.spacer()

    # --- 6. Early Action ---------------------------------------------------
    b.heading("6.  Early Action (EA / REA) Strategy")
    b.body(EA_INTRO, after=160)
    _ea_table(b, data["ea"])
    b.spacer()

    # --- 7. Action plan ----------------------------------------------------
    b.heading("7.  12th-Grade Action Plan (From Now Through Application)")
    b.body([(ACTION_INTRO, False, TEXT, 20)])
    for accent_tier, box in STEP_BOXES:
        b.box(box, bg=BOX_BG[accent_tier], accent=BOX_ACCENT[accent_tier])
    b.spacer()

    # --- 8. Abbreviations --------------------------------------------------
    b.heading("8.  Abbreviations · Full Description")
    b.body([("Full names and meanings of the abbreviations used in this report and its key notes.",
             False, TEXT, 20)])
    b._generic_table([2400, 6960],
                     [("Abbreviation", "left"), ("Full Description", "left")],
                     [[(a, "left", True, NAVY), (d, "left", True, TEXT)] for a, d in ABBREVIATIONS])
    b.spacer()
    b.box(DISCLAIMER_BOX, bg="F2F2F2", accent=GRAY)

    b.save(out_path)
    return out_path


def _tiered_lists(b, tiers, labels):
    for tier, label, first in (("reach", labels[0], True),
                               ("match", labels[1], False),
                               ("safety", labels[2], False)):
        if not first:
            b.spacer(after=60)
        b.tier_label(tier, label)
        b.list_table(tier, _rows(tiers[tier]))


def _ed_table(b, ed):
    header = [("College", "left"), ("State", "center"), ("RD Prob.", "center"),
              ("ED Prob.", "center"), ("Recommendation", "center")]
    rows = []
    for college, state, rd, ed_p, rec in ed:
        rows.append([(college, "left", True, TEXT), (state, "center", True, TEXT),
                     (rd, "center", True, GRAY), (ed_p, "center", True, GREEN),
                     (rec, "center", True, RED)])
    b._generic_table([3640, 720, 1320, 1320, 2360], header, rows)


def _ea_table(b, ea):
    header = [("College", "left"), ("State", "center"),
              ("EA Prob.", "center"), ("Notes (Policy / Caution)", "left")]
    rows = []
    for college, state, ea_p, notes in ea:
        rows.append([(college, "left", True, TEXT), (state, "center", True, TEXT),
                     (ea_p, "center", True, NAVY), (notes, "left", True, GRAY)])
    b._generic_table([3600, 720, 1320, 3720], header, rows)


# Box background/accent lookup (mirrors the reference template's colour pairs)
GOLD_BOX_BG = "FBF1DD"
NAVY_BOX_BG = "E8ECF4"
RED_BOX_BG  = "F3E7E9"
BOX_BG     = {"reach": "F3E7E9", "match": "FBF1DD", "safety": "E7F1E8", "navy": "E8ECF4"}
BOX_ACCENT = {"reach": RED, "match": GOLD, "safety": GREEN, "navy": NAVY}


if __name__ == "__main__":
    import sys

    with open(os.path.join(HERE, "college_data.json"), encoding="utf-8") as f:
        college_data = json.load(f)

    # If an intake file is given (CLI arg) or an `intake.txt` sits next to this
    # script, auto-fill the STUDENT block from it. Otherwise use the hardcoded
    # STUDENT above.
    intake_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "intake.txt")
    if os.path.exists(intake_path):
        from intake_parser import parse_intake, build_student
        with open(intake_path, encoding="utf-8") as fh:
            student = build_student(parse_intake(fh.read()))
        print("Parsed intake from:", intake_path)
    else:
        student = STUDENT

    out = os.path.join(HERE, student["output_name"])
    path = build(student, college_data, out)
    print("Report generated:", path)
