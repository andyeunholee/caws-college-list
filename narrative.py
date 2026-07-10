# -*- coding: utf-8 -*-
"""
narrative.py — dynamic, per-student report commentary
=====================================================
Generates the tailored prose for every section from the structured profile
(scoring.build_profile) and the selected lists (scoring.select_lists), returning
a `narr` dict consumed by assemble.py and preview_html.py.
"""

from report_engine import NAVY, RED, GOLD, GREEN, TEXT, GRAY

# states whose PUBLIC universities require test scores (best-effort)
TEST_REQUIRED_STATES = {"GA", "FL"}
TEST_BLIND_STATES = {"CA"}
STATE_SCHOLARSHIP = {
    "GA": "Georgia HOPE/Zell Miller", "FL": "Florida Bright Futures",
    "CA": "Cal Grant", "TN": "Tennessee HOPE (lottery) Scholarship",
    "SC": "SC LIFE Scholarship", "NM": "New Mexico Lottery Scholarship",
    "LA": "Louisiana TOPS", "WV": "West Virginia PROMISE", "AR": "Arkansas Challenge",
    "KY": "Kentucky KEES", "NV": "Nevada Millennium Scholarship",
}


def _test_level(profile):
    if not profile["has_test"]:
        return "none"
    s = profile["sat_equiv"]
    if s < 1100:
        return "low"
    if s < 1300:
        return "mid"
    if s < 1420:
        return "strong"
    return "elite"


def _gpa_level(profile):
    g = profile["gpa_used"]
    if g >= 3.85:
        return "high"
    if g >= 3.5:
        return "solid"
    if g >= 3.1:
        return "moderate"
    return "developing"


def build_narrative(profile, lists):
    S = profile["name"].split()[0]  # first name
    home = profile["home_state"]
    home_name = profile["home_state_name"] or "the home state"
    tl = _test_level(profile)
    gl = _gpa_level(profile)
    major = profile["major"]
    test_disp = profile["test_display"]
    rigor = profile["rigor"]
    lead = profile["leadership"]
    serv = profile["service"]

    # ---- headline facts sentence ----
    facts = []
    facts.append("an unweighted GPA of %.2f" % profile["uw_gpa"] if profile["uw_gpa"]
                 else ("a weighted GPA of %.2f" % profile["w_gpa"] if profile["w_gpa"] else "a developing GPA"))
    facts.append("%d AP/IB/DE course%s" % (rigor, "" if rigor == 1 else "s"))
    facts.append(("a test score of " + test_disp) if profile["has_test"] else "no test score on file yet")
    facts.append("%d leadership position%s" % (lead, "" if lead == 1 else "s"))
    facts.append("~%d community-service hours" % serv)
    facts_str = ", ".join(facts[:-1]) + ", and " + facts[-1]

    # ---- biggest lever ----
    if tl in ("none", "low"):
        lever = ("The standardized test is the single biggest and most efficient variable to move — "
                 "raising it (or, where it helps, applying test-optional) reshapes the list the most.")
    elif gl in ("moderate", "developing"):
        lever = ("Grades and course rigor are the biggest levers — a strong, upward senior transcript "
                 "and one or two more rigorous courses lift competitiveness across the board.")
    elif rigor <= 2:
        lever = ("Adding course rigor (AP / Dual Enrollment) and sharpening the application narrative are "
                 "the most efficient remaining levers.")
    else:
        lever = ("The academic profile is strong; the highest-leverage move now is a sharp application "
                 "narrative plus a well-chosen Early Decision to convert a strong Match into an admit.")

    note = [([("All admission probabilities in this report are ", False, TEXT, 18),
             ("‘profile-adjusted estimated probabilities’ based on the student’s individual profile",
              True, NAVY, 18),
             (". They are not the colleges’ published overall acceptance rates; each school is "
              "re-calibrated into Reach/Match/Safety from %s’s GPA, test score, course rigor, "
              "extracurriculars, and essay/recommendation strength." % S, False, TEXT, 18)], 0)]

    methodology = ("%s presents %s across the profile — %s. The intended focus is %s. %s"
                   % (S, {"high": "a strong academic record", "solid": "a solid academic record",
                          "moderate": "a developing academic record",
                          "developing": "an early-stage academic record"}[gl],
                      facts_str, major, lever))

    tier_def = [("Tier Definitions — ", True, NAVY, 19),
                ("Reach: estimated admit probability ~20% or below · Match: ~21–55% · "
                 "Safety: ~60% or above. ‘<1%’ denotes a statistically extremely low case.",
                 False, TEXT, 19)]

    # ---- testing box (state-aware) ----
    testing = [([("2026–2027 Cycle: Testing Policy — What Matters for %s" % S, True, NAVY, 19)], 60)]
    if home in TEST_BLIND_STATES:
        testing.append(([("· ", True, NAVY, 18),
            ("%s’s public system (UC / CSU) is test-blind — scores are ignored entirely, so GPA, "
             "coursework, essays, and activities decide the in-state list." % home_name, False, TEXT, 18)], 40))
    elif home in TEST_REQUIRED_STATES:
        testing.append(([("· ", True, NAVY, 18),
            ("%s’s public universities require the SAT/ACT, so the test is counted on the in-state list; "
             "a higher score lifts every in-state probability." % home_name, False, TEXT, 18)], 40))
    else:
        testing.append(([("· ", True, NAVY, 18),
            ("Most public universities in %s are test-optional, but a strong score still helps at the "
             "flagship and honors programs." % home_name, False, TEXT, 18)], 40))
    if tl in ("none", "low"):
        testing.append(([("· ", True, NAVY, 18),
            ("With no strong score on file, applying test-optional at schools that allow it is usually the "
             "better play — a withheld score reads better than a clearly below-median one.", False, TEXT, 18)], 40))
    else:
        testing.append(([("· ", True, NAVY, 18),
            ("The current score is competitive at many targets; submit it where it sits at or above the "
             "school’s median, and consider withholding only where it falls below.", False, TEXT, 18)], 40))
    testing.append(([("· ", True, NAVY, 18),
        ("Because ~80% of applicants at selective privates now submit scores, a genuine score increase is "
         "the most durable fix rather than relying on test-optional permanently.", False, TEXT, 18)], 0))

    # ---- core strategy ----
    if tl in ("none", "low"):
        core_txt = ("Raising the test toward a mid-band score (and applying test-optional where it helps) "
                    "reshapes the list the most. Paired with one carefully chosen Early Decision or a broad "
                    "set of non-binding Early Action applications at well-matched schools, this converts "
                    "several ‘Reach’ targets into realistic ‘Match’ ones while a solid Safety base secures the plan.")
    else:
        core_txt = ("With the academic profile already competitive, the highest-value move is a sharp, "
                    "specific application narrative plus a single Early Decision at a genuine first-choice "
                    "Match~low-Reach — where the binding boost roughly doubles the odds — rather than spending "
                    "the ED card on an ultra-selective Reach.")
    core = [([("Core Strategy in One Line", True, RED, 19)], 60),
            ([(core_txt, False, TEXT, 20)], 0)]

    national_intro = ("Below are up to 150 national universities across the U.S., excluding %s-based schools "
                      "and Liberal Arts Colleges (LACs) — up to 50 per tier. Tiers reflect %s’s "
                      "profile-adjusted probability, not each school’s overall admit rate." % (home_name, S))

    instate_intro = ("Universities in %s, %s’s state of residence and graduation (LACs excluded). "
                     % (home_name, S))
    if home in TEST_BLIND_STATES:
        instate_intro += "Public campuses here are test-blind, so strong grades and activities translate directly. "
    elif home in TEST_REQUIRED_STATES:
        instate_intro += "Public campuses here require the SAT/ACT, so the test is factored in. "
    instate_intro += "In-state residency lowers cost and widens capacity"
    if home in STATE_SCHOLARSHIP:
        instate_intro += " and can unlock the %s" % STATE_SCHOLARSHIP[home]
    instate_intro += ", so these remain strategically valuable."

    lac_intro = ("LACs are small, undergraduate-focused colleges known for close faculty mentorship, small "
                 "discussion classes, and strong advising. Many remain test-optional, and their smaller "
                 "cohorts can mean more individual support. They are included here for reference regardless of "
                 "the LAC preference on the intake form, because the fit can genuinely help this profile.")

    ed_intro = [("ED is ", False, TEXT, 20),
                ("a binding early application that obligates enrollment upon admission", True, RED, 20),
                (", usable at only one school. Colleges treat ED applicants as ‘first-choice applicants’ and "
                 "grant higher admit rates; for %s’s profile, ED roughly " % S, False, TEXT, 20),
                ("1.7–2×", True, TEXT, 20), (" the estimated probability. In the table below, the ", False, TEXT, 20),
                ("★/★★ marked schools", True, NAVY, 20),
                (" are the best-fit candidates that ‘settle into the Match range with the ED boost.’",
                 False, TEXT, 20)]

    strong_ed = [r[0] for r in lists["ed"] if r[4].startswith("★★")][:6]
    if not strong_ed:
        strong_ed = [r[0] for r in lists["ed"] if r[4].startswith("★")][:6]
    ed_names = " · ".join(strong_ed) if strong_ed else "the best-matched ED-offering schools above"
    ed_rec = [([("ED Recommendation", True, NAVY, 19)], 60),
              ([("If %s decides to use ED, the strongest single-card targets are %s — where the binding "
                 "boost lifts the estimate into the strongest range shown. Spending the binding card on "
                 "ultra-selective Reaches is inefficient, since they stay in the low single digits even with "
                 "ED. Because ED is binding, use it only for a school %s would attend if admitted — and "
                 "confirm the financial-aid fit first." % (S, ed_names, S), False, TEXT, 18)], 0)]

    ea_intro = [("EA is ", False, TEXT, 20), ("a non-binding early application", True, RED, 20),
                (" — no obligation to enroll if admitted — so %s can apply EA to several schools at once and "
                 "collect early decisions plus priority Honors/scholarship review. A few schools use " % S,
                 False, TEXT, 20),
                ("REA/SCEA", True, NAVY, 20),
                (" (restrictive single-choice) that cannot be combined with other private EA/ED. Applying "
                 "early is strongly advised where deadlines allow.", False, TEXT, 20)]

    action_intro = ("%s is currently in 12th grade. The steps below are ordered by impact, highest first, to "
                    "raise admit odds from now through the application deadlines." % S)

    # ---- action steps (prioritized by profile) ----
    steps = []
    if tl in ("none", "low"):
        steps.append(("reach", [
            ([("STEP 1. ", True, RED, 18), ("Raise the test — the highest-impact move", True, NAVY, 18)], 60),
            ([("· ", True, RED, 18), ("Target a mid-band score; even a moderate gain moves several current "
              "Reach schools into Match and lifts every test-required in-state probability.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("Use the remaining fall test dates before EA/ED deadlines (many Nov 1); "
              "plan a focused study sprint on the weaker section with full-length timed practice.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("At test-optional schools, submit only once the score sits at or above "
              "their median; otherwise apply test-optional.", False, TEXT, 18)], 0)]))
    else:
        steps.append(("reach", [
            ([("STEP 1. ", True, RED, 18), ("Lock the Early strategy — the highest-impact move", True, NAVY, 18)], 60),
            ([("· ", True, RED, 18), ("Choose ONE Early Decision at a genuine first-choice Match~low-Reach; the "
              "binding boost roughly doubles the odds and is the most efficient single move.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("Layer non-binding Early Action broadly to bank early admits and priority "
              "scholarship review; mind any REA restriction.", False, TEXT, 18)], 0)]))
    steps.append(("match", [
        ([("STEP 2. ", True, GOLD, 18), ("Strengthen rigor and protect senior grades", True, NAVY, 18)], 60),
        ([("· ", True, GOLD, 18), ("Keep the hardest available courses and a strong, upward senior transcript — "
          "mid-year and final reports still reach colleges.", False, TEXT, 18)]
         + ([] if rigor >= 5 else []), 40),
        ([("· ", True, GOLD, 18), ("Where possible, add an AP or Dual-Enrollment course aligned with %s to signal "
          "readiness for the intended path." % major, False, TEXT, 18)], 0)]))
    steps.append(("safety", [
        ([("STEP 3. ", True, GREEN, 18), ("Build the story: essays, activities, service", True, NAVY, 18)], 60),
        ([("· ", True, GREEN, 18), ("Draft the Common App essay early and revise toward a specific, genuine "
          "narrative that connects the activities and the intended major.", False, TEXT, 18)], 40),
        ([("· ", True, GREEN, 18), ("Deepen one or two activities into documented, leadership-bearing "
          "commitments rather than adding many shallow ones.", False, TEXT, 18)], 0)]))
    steps.append(("navy", [
        ([("STEP 4. ", True, NAVY, 18), ("Recommendations, deadlines, and finances", True, NAVY, 18)], 60),
        ([("· ", True, NAVY, 18), ("Ask two teachers for recommendations in Aug–Sep with a short brag-sheet of "
          "specifics.", False, TEXT, 18)], 40),
        ([("· ", True, NAVY, 18), ("File the FAFSA (opens October) and any required CSS Profile on time"
          + ((", and confirm %s eligibility" % STATE_SCHOLARSHIP[home]) if home in STATE_SCHOLARSHIP else "")
          + ".", False, TEXT, 18)], 0)]))

    abbreviations = [
        ("GPA", "Grade Point Average — academic performance average"),
        ("UW GPA", "Unweighted GPA — unweighted average (4.0 scale)"),
        ("W GPA", "Weighted GPA — weighted for AP/Honors/DE courses"),
        ("SAT", "Scholastic Assessment Test — U.S. college-entrance standardized test"),
        ("EBRW", "Evidence-Based Reading and Writing — SAT verbal section"),
        ("ACT", "American College Testing — standardized test, SAT alternative (concorded to an SAT-equivalent here)"),
        ("AP", "Advanced Placement — college-level high school coursework"),
        ("IB", "International Baccalaureate — international diploma program"),
        ("DE", "Dual Enrollment — college credit earned during high school"),
        ("ED", "Early Decision — binding early application (must enroll if admitted)"),
        ("EA", "Early Action — non-binding early application (no obligation to enroll)"),
        ("REA / SCEA", "Restrictive / Single-Choice Early Action — restricted single-choice early application"),
        ("RD", "Regular Decision — standard application round"),
        ("LAC", "Liberal Arts College — undergraduate-focused liberal arts institution"),
        ("OOS", "Out-of-State — applicant from another state"),
        ("CDS", "Common Data Set — official university statistics"),
        ("FAFSA", "Free Application for Federal Student Aid — federal financial-aid application"),
        ("CSS Profile", "College Scholarship Service Profile — private-school financial-aid application"),
        ("test-optional", "policy letting the applicant choose whether to submit test scores"),
        ("test-required", "policy that requires SAT/ACT scores for admission review"),
        ("test-blind", "policy that ignores test scores entirely, even if submitted"),
    ]
    if home in STATE_SCHOLARSHIP:
        abbreviations.append((STATE_SCHOLARSHIP[home].split("(")[0].strip(),
                              "state merit scholarship for eligible in-state students"))

    disclaimer = [([("Disclaimer", True, GRAY, 18),
        ("   All figures are ‘estimated admit probabilities’ based on %s’s profile, not official college "
         "acceptance rates. Each school’s policies, deadlines, and testing requirements change every cycle, so "
         "always confirm on each college’s official admissions page before applying." % S, True, GRAY, 18)], 0)]

    return {
        "note": note, "methodology": methodology, "tier_def": tier_def, "testing": testing,
        "core": core, "national_intro": national_intro, "instate_intro": instate_intro,
        "instate_state_name": profile["home_state_name"] or "Home State", "lac_intro": lac_intro,
        "ed_intro": ed_intro, "ed_rec": ed_rec, "ea_intro": ea_intro, "action_intro": action_intro,
        "steps": steps, "abbreviations": abbreviations, "disclaimer": disclaimer,
    }
