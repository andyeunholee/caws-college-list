# -*- coding: utf-8 -*-
"""
narrative.py — dynamic, per-student report commentary (English + Korean)
========================================================================
build_narrative(profile, lists, lang) returns the `narr` dict of tailored prose.
lang="Eng" (default) or "Kor".
"""

from report_engine import NAVY, RED, GOLD, GREEN, TEXT, GRAY

TEST_REQUIRED_STATES = {"GA", "FL"}
TEST_BLIND_STATES = {"CA"}
STATE_SCHOLARSHIP = {
    "GA": "Georgia HOPE/Zell Miller", "FL": "Florida Bright Futures", "CA": "Cal Grant",
    "TN": "Tennessee HOPE (lottery) Scholarship", "SC": "SC LIFE Scholarship",
    "NM": "New Mexico Lottery Scholarship", "LA": "Louisiana TOPS",
    "WV": "West Virginia PROMISE", "AR": "Arkansas Challenge", "KY": "Kentucky KEES",
    "NV": "Nevada Millennium Scholarship",
}


def _test_level(profile):
    if not profile["has_test"]:
        return "none"
    s = profile["sat_equiv"]
    return "low" if s < 1100 else "mid" if s < 1300 else "strong" if s < 1420 else "elite"


def _gpa_level(profile):
    g = profile["gpa_used"]
    return "high" if g >= 3.85 else "solid" if g >= 3.5 else "moderate" if g >= 3.1 else "developing"


def build_narrative(profile, lists, lang="Eng"):
    return _kor(profile, lists) if lang == "Kor" else _eng(profile, lists)


# ======================================================================= ENG
def _eng(profile, lists):
    S = profile["name"].split()[0]
    home, home_name = profile["home_state"], profile["home_state_name"] or "the home state"
    tl, gl = _test_level(profile), _gpa_level(profile)
    major, test_disp = profile["major"], profile["test_display"]
    rigor, lead, serv = profile["rigor"], profile["leadership"], profile["service"]

    facts = []
    facts.append("an unweighted GPA of %.2f" % profile["uw_gpa"] if profile["uw_gpa"]
                 else ("a weighted GPA of %.2f" % profile["w_gpa"] if profile["w_gpa"] else "a developing GPA"))
    facts.append("%d AP/IB/DE course%s" % (rigor, "" if rigor == 1 else "s"))
    facts.append(("a test score of " + test_disp) if profile["has_test"] else "no test score on file yet")
    facts.append("%d leadership position%s" % (lead, "" if lead == 1 else "s"))
    facts.append("~%d community-service hours" % serv)
    facts_str = ", ".join(facts[:-1]) + ", and " + facts[-1]

    if tl in ("none", "low"):
        lever = ("The standardized test is the single biggest and most efficient variable to move — "
                 "raising it (or, where it helps, applying test-optional) reshapes the list the most.")
    elif gl in ("moderate", "developing"):
        lever = ("Grades and course rigor are the biggest levers — a strong, upward senior transcript and one "
                 "or two more rigorous courses lift competitiveness across the board.")
    elif rigor <= 2:
        lever = ("Adding course rigor (AP / Dual Enrollment) and sharpening the application narrative are the "
                 "most efficient remaining levers.")
    else:
        lever = ("The academic profile is strong; the highest-leverage move now is a sharp application narrative "
                 "plus a well-chosen Early Decision to convert a strong Match into an admit.")

    note = [([("All admission probabilities in this report are ", False, TEXT, 18),
             ("‘profile-adjusted estimated probabilities’ based on the student’s individual profile", True, NAVY, 18),
             (". They are not the colleges’ published overall acceptance rates; each school is re-calibrated into "
              "Reach/Match/Safety from %s’s GPA, test score, course rigor, extracurriculars, and "
              "essay/recommendation strength." % S, False, TEXT, 18)], 0)]

    methodology = ("%s presents %s across the profile — %s. The intended focus is %s. %s"
                   % (S, {"high": "a strong academic record", "solid": "a solid academic record",
                          "moderate": "a developing academic record", "developing": "an early-stage academic record"}[gl],
                      facts_str, major, lever))

    tier_def = [("Tier Definitions — ", True, NAVY, 19),
                ("Reach: estimated admit probability ~20% or below · Match: ~21–55% · Safety: ~60% or above. "
                 "‘<1%’ denotes a statistically extremely low case.", False, TEXT, 19)]

    testing = [([("2026–2027 Cycle: Testing Policy — What Matters for %s" % S, True, NAVY, 19)], 60)]
    if home in TEST_BLIND_STATES:
        testing.append(([("· ", True, NAVY, 18), ("%s’s public system (UC / CSU) is test-blind — scores are ignored "
            "entirely, so GPA, coursework, essays, and activities decide the in-state list." % home_name, False, TEXT, 18)], 40))
    elif home in TEST_REQUIRED_STATES:
        testing.append(([("· ", True, NAVY, 18), ("%s’s public universities require the SAT/ACT, so the test is counted "
            "on the in-state list; a higher score lifts every in-state probability." % home_name, False, TEXT, 18)], 40))
    else:
        testing.append(([("· ", True, NAVY, 18), ("Most public universities in %s are test-optional, but a strong score "
            "still helps at the flagship and honors programs." % home_name, False, TEXT, 18)], 40))
    if tl in ("none", "low"):
        testing.append(([("· ", True, NAVY, 18), ("With no strong score on file, applying test-optional at schools that allow "
            "it is usually the better play — a withheld score reads better than a clearly below-median one.", False, TEXT, 18)], 40))
    else:
        testing.append(([("· ", True, NAVY, 18), ("The current score is competitive at many targets; submit it where it sits at "
            "or above the school’s median, and consider withholding only where it falls below.", False, TEXT, 18)], 40))
    testing.append(([("· ", True, NAVY, 18), ("Because ~80% of applicants at selective privates now submit scores, a genuine "
        "score increase is the most durable fix rather than relying on test-optional permanently.", False, TEXT, 18)], 0))

    if tl in ("none", "low"):
        core_txt = ("Raising the test toward a mid-band score (and applying test-optional where it helps) reshapes the "
                    "list the most. Paired with one carefully chosen Early Decision or a broad set of non-binding Early "
                    "Action applications at well-matched schools, this converts several ‘Reach’ targets into realistic "
                    "‘Match’ ones while a solid Safety base secures the plan.")
    else:
        core_txt = ("With the academic profile already competitive, the highest-value move is a sharp, specific application "
                    "narrative plus a single Early Decision at a genuine first-choice Match~low-Reach — where the binding "
                    "boost roughly doubles the odds — rather than spending the ED card on an ultra-selective Reach.")
    core = [([("Core Strategy in One Line", True, RED, 19)], 60), ([(core_txt, False, TEXT, 20)], 0)]

    national_intro = ("Below are up to 150 national universities across the U.S., excluding %s-based schools and Liberal "
                      "Arts Colleges (LACs) — up to 50 per tier. Tiers reflect %s’s profile-adjusted probability, not each "
                      "school’s overall admit rate." % (home_name, S))
    instate_intro = "Universities in %s, %s’s state of residence and graduation (LACs excluded). " % (home_name, S)
    if home in TEST_BLIND_STATES:
        instate_intro += "Public campuses here are test-blind, so strong grades and activities translate directly. "
    elif home in TEST_REQUIRED_STATES:
        instate_intro += "Public campuses here require the SAT/ACT, so the test is factored in. "
    instate_intro += "In-state residency lowers cost and widens capacity"
    if home in STATE_SCHOLARSHIP:
        instate_intro += " and can unlock the %s" % STATE_SCHOLARSHIP[home]
    instate_intro += ", so these remain strategically valuable."
    lac_intro = ("LACs are small, undergraduate-focused colleges known for close faculty mentorship, small discussion "
                 "classes, and strong advising. Many remain test-optional, and their smaller cohorts can mean more "
                 "individual support. They are included here for reference regardless of the LAC preference on the intake "
                 "form, because the fit can genuinely help this profile.")

    ed_intro = [("ED is ", False, TEXT, 20), ("a binding early application that obligates enrollment upon admission", True, RED, 20),
                (", usable at only one school. Colleges treat ED applicants as ‘first-choice applicants’ and grant higher "
                 "admit rates; for %s’s profile, ED roughly " % S, False, TEXT, 20), ("1.7–2×", True, TEXT, 20),
                (" the estimated probability. In the table below, the ", False, TEXT, 20), ("★/★★ marked schools", True, NAVY, 20),
                (" are the best-fit candidates that ‘settle into the Match range with the ED boost.’", False, TEXT, 20)]
    strong_ed = [r[0] for r in lists["ed"] if r[4].startswith("★★")][:6] or [r[0] for r in lists["ed"] if r[4].startswith("★")][:6]
    ed_names = " · ".join(strong_ed) if strong_ed else "the best-matched ED-offering schools above"
    ed_rec = [([("ED Recommendation", True, NAVY, 19)], 60),
              ([("If %s decides to use ED, the strongest single-card targets are %s — where the binding boost lifts the "
                 "estimate into the strongest range shown. Spending the binding card on ultra-selective Reaches is inefficient, "
                 "since they stay in the low single digits even with ED. Because ED is binding, use it only for a school %s "
                 "would attend if admitted — and confirm the financial-aid fit first." % (S, ed_names, S), False, TEXT, 18)], 0)]

    ea_intro = [("EA is ", False, TEXT, 20), ("a non-binding early application", True, RED, 20),
                (" — no obligation to enroll if admitted — so %s can apply EA to several schools at once and collect early "
                 "decisions plus priority Honors/scholarship review. A few schools use " % S, False, TEXT, 20),
                ("REA/SCEA", True, NAVY, 20), (" (restrictive single-choice) that cannot be combined with other private "
                 "EA/ED. Applying early is strongly advised where deadlines allow.", False, TEXT, 20)]

    action_intro = ("%s is currently in 12th grade. The steps below are ordered by impact, highest first, to raise admit "
                    "odds from now through the application deadlines." % S)
    steps = []
    if tl in ("none", "low"):
        steps.append(("reach", [
            ([("STEP 1. ", True, RED, 18), ("Raise the test — the highest-impact move", True, NAVY, 18)], 60),
            ([("· ", True, RED, 18), ("Target a mid-band score; even a moderate gain moves several current Reach schools into "
              "Match and lifts every test-required in-state probability.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("Use the remaining fall test dates before EA/ED deadlines (many Nov 1); plan a focused "
              "study sprint on the weaker section with full-length timed practice.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("At test-optional schools, submit only once the score sits at or above their median; "
              "otherwise apply test-optional.", False, TEXT, 18)], 0)]))
    else:
        steps.append(("reach", [
            ([("STEP 1. ", True, RED, 18), ("Lock the Early strategy — the highest-impact move", True, NAVY, 18)], 60),
            ([("· ", True, RED, 18), ("Choose ONE Early Decision at a genuine first-choice Match~low-Reach; the binding boost "
              "roughly doubles the odds and is the most efficient single move.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("Layer non-binding Early Action broadly to bank early admits and priority scholarship "
              "review; mind any REA restriction.", False, TEXT, 18)], 0)]))
    steps.append(("match", [
        ([("STEP 2. ", True, GOLD, 18), ("Strengthen rigor and protect senior grades", True, NAVY, 18)], 60),
        ([("· ", True, GOLD, 18), ("Keep the hardest available courses and a strong, upward senior transcript — mid-year and "
          "final reports still reach colleges.", False, TEXT, 18)], 40),
        ([("· ", True, GOLD, 18), ("Where possible, add an AP or Dual-Enrollment course aligned with %s to signal readiness "
          "for the intended path." % major, False, TEXT, 18)], 0)]))
    steps.append(("safety", [
        ([("STEP 3. ", True, GREEN, 18), ("Build the story: essays, activities, service", True, NAVY, 18)], 60),
        ([("· ", True, GREEN, 18), ("Draft the Common App essay early and revise toward a specific, genuine narrative that "
          "connects the activities and the intended major.", False, TEXT, 18)], 40),
        ([("· ", True, GREEN, 18), ("Deepen one or two activities into documented, leadership-bearing commitments rather than "
          "adding many shallow ones.", False, TEXT, 18)], 0)]))
    steps.append(("navy", [
        ([("STEP 4. ", True, NAVY, 18), ("Recommendations, deadlines, and finances", True, NAVY, 18)], 60),
        ([("· ", True, NAVY, 18), ("Ask two teachers for recommendations in Aug–Sep with a short brag-sheet of specifics.", False, TEXT, 18)], 40),
        ([("· ", True, NAVY, 18), ("File the FAFSA (opens October) and any required CSS Profile on time"
          + ((", and confirm %s eligibility" % STATE_SCHOLARSHIP[home]) if home in STATE_SCHOLARSHIP else "") + ".", False, TEXT, 18)], 0)]))

    abbreviations = _abbr_eng(home)
    disclaimer = [([("Disclaimer", True, GRAY, 18),
        ("   All figures are ‘estimated admit probabilities’ based on %s’s profile, not official college acceptance rates. "
         "Each school’s policies, deadlines, and testing requirements change every cycle, so always confirm on each college’s "
         "official admissions page before applying." % S, True, GRAY, 18)], 0)]

    return _pack(note, methodology, tier_def, testing, core, national_intro, instate_intro,
                 profile, lac_intro, ed_intro, ed_rec, ea_intro, action_intro, steps, abbreviations, disclaimer)


# ======================================================================= KOR
def _kor(profile, lists):
    S = profile["name"].split()[0]
    stu = "%s 학생" % S
    home, home_name = profile["home_state"], profile["home_state_name"] or "거주 주"
    tl, gl = _test_level(profile), _gpa_level(profile)
    major = profile["major"]
    test_disp = profile["test_display"].replace("SAT eq.", "SAT 환산").replace(" / Math ", " / 수학 ")
    rigor, lead, serv = profile["rigor"], profile["leadership"], profile["service"]

    facts = []
    facts.append("비가중 GPA %.2f" % profile["uw_gpa"] if profile["uw_gpa"]
                 else ("가중 GPA %.2f" % profile["w_gpa"] if profile["w_gpa"] else "발전 중인 GPA"))
    facts.append("AP/IB/DE %d과목" % rigor)
    facts.append(("시험 점수 " + test_disp) if profile["has_test"] else "시험 점수 미제출")
    facts.append("리더십 %d개" % lead)
    facts.append("봉사 약 %d시간" % serv)
    facts_str = ", ".join(facts)

    if tl in ("none", "low"):
        lever = ("표준화 시험 점수가 가장 크고 효율적인 변수입니다 — 점수를 올리거나(도움이 되는 경우) test-optional로 "
                 "지원하는 것이 리스트를 가장 크게 바꿉니다.")
    elif gl in ("moderate", "developing"):
        lever = ("내신과 과목 난이도가 가장 큰 지렛대입니다 — 상승세의 탄탄한 12학년 성적과 심화 과목 1~2개가 전반적인 "
                 "경쟁력을 끌어올립니다.")
    elif rigor <= 2:
        lever = "과목 난이도(AP/DE) 추가와 지원서 내러티브를 다듬는 것이 남은 가장 효율적인 지렛대입니다."
    else:
        lever = ("학업 프로필이 강합니다. 지금 가장 효율적인 수는 날카로운 지원서 내러티브와, 강한 적정권 학교에 대한 "
                 "신중한 Early Decision 한 장으로 합격을 확보하는 것입니다.")

    note = [([("이 리포트의 모든 합격 확률은 ", False, TEXT, 18),
             ("학생 개인 프로필을 반영한 ‘프로필 조정 추정 확률’", True, NAVY, 18),
             ("입니다. 대학이 공개한 전체 합격률이 아니며, 각 학교는 %s의 GPA·시험 점수·과목 난이도·비교과 활동·"
              "에세이/추천서 강도를 기준으로 도전/적정/안정으로 재조정됩니다." % stu, False, TEXT, 18)], 0)]

    acad = {"high": "강한 학업 기록", "solid": "탄탄한 학업 기록", "moderate": "발전 중인 학업 기록",
            "developing": "초기 단계의 학업 기록"}[gl]
    methodology = "%s은 프로필 전반에서 %s을 보여줍니다 — %s. 희망 분야는 %s입니다. %s" % (stu, acad, facts_str, major, lever)

    tier_def = [("티어 정의 — ", True, NAVY, 19),
                ("도전(Reach): 추정 합격률 약 20% 이하 · 적정(Match): 약 21–55% · 안정(Safety): 약 60% 이상. "
                 "‘<1%’는 통계적으로 매우 낮은 경우를 뜻합니다.", False, TEXT, 19)]

    testing = [([("2026–2027 사이클: 시험 정책 — %s에게 중요한 점" % stu, True, NAVY, 19)], 60)]
    if home in TEST_BLIND_STATES:
        testing.append(([("· ", True, NAVY, 18), ("%s의 공립 시스템(UC/CSU)은 test-blind로, 점수를 전혀 반영하지 않습니다. "
            "따라서 주내 리스트는 GPA·과목·에세이·활동으로 결정됩니다." % home_name, False, TEXT, 18)], 40))
    elif home in TEST_REQUIRED_STATES:
        testing.append(([("· ", True, NAVY, 18), ("%s의 공립대학은 SAT/ACT를 필수로 요구하므로 주내 리스트에서는 시험 점수가 "
            "반영됩니다. 점수를 올리면 주내 모든 확률이 상승합니다." % home_name, False, TEXT, 18)], 40))
    else:
        testing.append(([("· ", True, NAVY, 18), ("%s의 공립대학은 대부분 test-optional이지만, 강한 점수는 주력 캠퍼스와 "
            "우등 프로그램에서 여전히 도움이 됩니다." % home_name, False, TEXT, 18)], 40))
    if tl in ("none", "low"):
        testing.append(([("· ", True, NAVY, 18), ("강한 점수가 없으면, 허용하는 학교에서는 test-optional 지원이 대체로 유리합니다 "
            "— 명백히 중앙값 이하인 점수를 내는 것보다 미제출이 더 낫게 읽힙니다.", False, TEXT, 18)], 40))
    else:
        testing.append(([("· ", True, NAVY, 18), ("현재 점수는 여러 목표교에서 경쟁력이 있습니다. 학교 중앙값 이상인 곳에는 제출하고, "
            "그 미만인 곳에서만 미제출을 고려하세요.", False, TEXT, 18)], 40))
    testing.append(([("· ", True, NAVY, 18), ("선발형 사립의 지원자 약 80%가 점수를 제출하는 만큼, test-optional에 계속 기대기보다 "
        "실제 점수를 올리는 것이 가장 지속적인 해법입니다.", False, TEXT, 18)], 0))

    if tl in ("none", "low"):
        core_txt = ("시험을 중간대 점수로 끌어올리고(도움이 되는 곳은 test-optional 활용) 리스트를 가장 크게 바꾸는 것이 핵심입니다. "
                    "여기에 신중히 고른 Early Decision 한 장 또는 잘 맞는 학교들에 대한 폭넓은 비구속 Early Action을 결합하면, "
                    "여러 ‘도전’ 목표가 현실적인 ‘적정’으로 바뀌고 탄탄한 ‘안정’ 기반이 계획을 지켜줍니다.")
    else:
        core_txt = ("학업 프로필이 이미 경쟁력이 있으므로, 가장 가치 있는 수는 날카롭고 구체적인 지원서 내러티브와, 진정한 1지망인 "
                    "적정~낮은 도전권 학교에 대한 Early Decision 한 장입니다 — 구속형 보정이 확률을 대략 두 배로 올리므로, "
                    "초선발 도전교에 ED 카드를 쓰는 것보다 효율적입니다.")
    core = [([("핵심 전략 한 줄 요약", True, RED, 19)], 60), ([(core_txt, False, TEXT, 20)], 0)]

    national_intro = ("아래는 미 전국 대학 최대 150개로, %s 소재 학교와 리버럴 아츠 칼리지(LAC)는 제외했으며 티어당 최대 50개입니다. "
                      "티어는 각 학교의 전체 합격률이 아니라 %s의 프로필 조정 확률을 반영합니다." % (home_name, stu))
    instate_intro = "%s(%s의 거주·졸업 주) 소재 대학입니다(LAC 제외). " % (home_name, stu)
    if home in TEST_BLIND_STATES:
        instate_intro += "이곳 공립 캠퍼스는 test-blind이므로 강한 내신과 활동이 곧바로 반영됩니다. "
    elif home in TEST_REQUIRED_STATES:
        instate_intro += "이곳 공립 캠퍼스는 SAT/ACT를 요구하므로 시험 점수가 반영됩니다. "
    instate_intro += "주내 거주는 학비를 낮추고 정원 여유를 넓혀줍니다"
    if home in STATE_SCHOLARSHIP:
        instate_intro += "며, %s 장학금 자격도 열릴 수 있습니다" % STATE_SCHOLARSHIP[home]
    instate_intro += ". 따라서 전략적으로 가치가 높습니다."
    lac_intro = ("LAC는 소규모 학부 중심 대학으로, 교수와의 긴밀한 멘토링, 토론식 소규모 수업, 강한 지도로 알려져 있습니다. "
                 "다수가 test-optional을 유지하며, 작은 규모 덕분에 개별 지원이 더 두터울 수 있습니다. 인테이크 폼의 LAC 선택 여부와 "
                 "무관하게, 이 프로필에 실질적으로 도움이 될 수 있어 참고용으로 포함했습니다.")

    ed_intro = [("ED는 ", False, TEXT, 20), ("합격 시 반드시 등록해야 하는 구속형 조기 지원", True, RED, 20),
                ("으로, 단 한 학교에만 사용할 수 있습니다. 대학은 ED 지원자를 ‘1지망 지원자’로 보아 더 높은 합격률을 부여하며, "
                 "%s의 프로필에서는 ED가 추정 확률을 대략 " % stu, False, TEXT, 20), ("1.7~2배", True, TEXT, 20),
                (" 높입니다. 아래 표에서 ", False, TEXT, 20), ("★/★★ 표시 학교", True, NAVY, 20),
                ("가 ‘ED 보정으로 적정권에 안착하는’ 최적 후보입니다.", False, TEXT, 20)]
    strong_ed = [r[0] for r in lists["ed"] if r[4].startswith("★★")][:6] or [r[0] for r in lists["ed"] if r[4].startswith("★")][:6]
    ed_names = " · ".join(strong_ed) if strong_ed else "위 표의 가장 잘 맞는 ED 제공 학교들"
    ed_rec = [([("ED 추천", True, NAVY, 19)], 60),
              ([("%s이 ED를 사용한다면, 가장 강력한 단일 카드 후보는 %s입니다 — 구속형 보정이 추정치를 표시된 가장 높은 구간으로 "
                 "끌어올리는 학교들입니다. 초선발 도전교에 구속 카드를 쓰는 것은 ED로도 한 자릿수에 머물기 때문에 비효율적입니다. "
                 "ED는 구속형이므로 합격 시 실제로 다닐 학교에만 사용하고, 재정 지원 적합성을 먼저 확인하세요." % (stu, ed_names), False, TEXT, 18)], 0)]

    ea_intro = [("EA는 ", False, TEXT, 20), ("합격해도 등록 의무가 없는 비구속형 조기 지원", True, RED, 20),
                ("입니다. 따라서 %s은 여러 학교에 동시에 EA로 지원해 조기 결과와 우선 우등/장학 심사를 받을 수 있습니다. 일부 학교는 "
                 % stu, False, TEXT, 20), ("REA/SCEA", True, NAVY, 20),
                ("(제한적 단일 선택)를 사용하며, 다른 사립 EA/ED와 병행할 수 없습니다. 마감이 허락하는 한 조기 지원을 강력히 권합니다.",
                 False, TEXT, 20)]

    action_intro = ("%s은 현재 12학년입니다. 아래 단계는 지금부터 지원 마감까지 합격 가능성을 높이기 위해 영향력이 큰 순서로 "
                    "정리했습니다." % stu)
    steps = []
    if tl in ("none", "low"):
        steps.append(("reach", [
            ([("STEP 1. ", True, RED, 18), ("시험 점수 올리기 — 영향력이 가장 큰 수", True, NAVY, 18)], 60),
            ([("· ", True, RED, 18), ("중간대 점수를 목표로 하세요. 적당한 상승만으로도 여러 도전 학교가 적정권으로 이동하고, 시험 필수 "
              "주내 확률이 모두 올라갑니다.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("EA/ED 마감(다수 11월 1일) 전 남은 가을 시험 일정을 활용하고, 약한 영역 집중 학습과 실전 모의고사로 "
              "단기 스퍼트를 계획하세요.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("test-optional 학교에는 점수가 중앙값 이상일 때만 제출하고, 그 미만이면 미제출로 지원하세요.", False, TEXT, 18)], 0)]))
    else:
        steps.append(("reach", [
            ([("STEP 1. ", True, RED, 18), ("조기 지원 전략 확정 — 영향력이 가장 큰 수", True, NAVY, 18)], 60),
            ([("· ", True, RED, 18), ("진정한 1지망인 적정~낮은 도전권 학교에 Early Decision 한 곳을 정하세요. 구속형 보정이 확률을 "
              "대략 두 배로 올리는 가장 효율적인 단일 수입니다.", False, TEXT, 18)], 40),
            ([("· ", True, RED, 18), ("비구속 Early Action을 폭넓게 걸어 조기 합격과 우선 장학 심사를 확보하되, REA 제한은 유의하세요.", False, TEXT, 18)], 0)]))
    steps.append(("match", [
        ([("STEP 2. ", True, GOLD, 18), ("과목 난이도 강화 및 12학년 성적 관리", True, NAVY, 18)], 60),
        ([("· ", True, GOLD, 18), ("가능한 가장 어려운 과목과 상승세의 12학년 성적을 유지하세요 — 중간·최종 성적표가 여전히 대학에 전달됩니다.", False, TEXT, 18)], 40),
        ([("· ", True, GOLD, 18), ("가능하면 %s에 맞는 AP 또는 Dual Enrollment 과목을 추가해 희망 진로에 대한 준비도를 보여주세요." % major, False, TEXT, 18)], 0)]))
    steps.append(("safety", [
        ([("STEP 3. ", True, GREEN, 18), ("스토리 구축: 에세이·활동·봉사", True, NAVY, 18)], 60),
        ([("· ", True, GREEN, 18), ("Common App 에세이를 일찍 초안 작성하고, 활동과 희망 전공을 연결하는 구체적이고 진솔한 내러티브로 다듬으세요.", False, TEXT, 18)], 40),
        ([("· ", True, GREEN, 18), ("얕은 활동을 여러 개 더하기보다, 한두 활동을 문서화된 리더십 있는 몰입으로 심화하세요.", False, TEXT, 18)], 0)]))
    steps.append(("navy", [
        ([("STEP 4. ", True, NAVY, 18), ("추천서 · 마감 · 재정", True, NAVY, 18)], 60),
        ([("· ", True, NAVY, 18), ("8~9월에 교사 두 분께 추천서를 부탁하고, 구체적 사례를 담은 짧은 자기소개 자료를 전달하세요.", False, TEXT, 18)], 40),
        ([("· ", True, NAVY, 18), ("FAFSA(10월 오픈)와 필요한 경우 CSS Profile을 기한 내 제출하세요"
          + ((". %s 자격도 확인하세요" % STATE_SCHOLARSHIP[home]) if home in STATE_SCHOLARSHIP else "") + ".", False, TEXT, 18)], 0)]))

    abbreviations = _abbr_kor(home)
    disclaimer = [([("면책 조항", True, GRAY, 18),
        ("   본 리포트의 모든 수치는 %s의 프로필에 기반한 ‘추정 합격 확률’이며, 대학의 공식 합격률이 아닙니다. 각 학교의 정책·마감·"
         "시험 요건은 매 사이클 바뀌므로, 지원 전 반드시 각 대학 공식 입학 페이지에서 최종 확인하세요." % stu, True, GRAY, 18)], 0)]

    return _pack(note, methodology, tier_def, testing, core, national_intro, instate_intro,
                 profile, lac_intro, ed_intro, ed_rec, ea_intro, action_intro, steps, abbreviations, disclaimer)


# ------------------------------------------------------------------ helpers
def _pack(note, methodology, tier_def, testing, core, national_intro, instate_intro,
          profile, lac_intro, ed_intro, ed_rec, ea_intro, action_intro, steps, abbreviations, disclaimer):
    return {"note": note, "methodology": methodology, "tier_def": tier_def, "testing": testing,
            "core": core, "national_intro": national_intro, "instate_intro": instate_intro,
            "instate_state_name": profile["home_state_name"] or "Home State", "lac_intro": lac_intro,
            "ed_intro": ed_intro, "ed_rec": ed_rec, "ea_intro": ea_intro, "action_intro": action_intro,
            "steps": steps, "abbreviations": abbreviations, "disclaimer": disclaimer}


def _abbr_eng(home):
    a = [("GPA", "Grade Point Average — academic performance average"),
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
         ("test-blind", "policy that ignores test scores entirely, even if submitted")]
    if home in STATE_SCHOLARSHIP:
        a.append((STATE_SCHOLARSHIP[home].split("(")[0].strip(), "state merit scholarship for eligible in-state students"))
    return a


def _abbr_kor(home):
    a = [("GPA", "Grade Point Average — 학업 성취 평균"),
         ("UW GPA", "비가중 GPA — 가중치 없는 평균(4.0 만점)"),
         ("W GPA", "가중 GPA — AP/Honors/DE 반영 가중 평균"),
         ("SAT", "Scholastic Assessment Test — 미국 대학입학 표준화 시험"),
         ("EBRW", "Evidence-Based Reading and Writing — SAT 언어(독해·작문) 영역"),
         ("ACT", "American College Testing — SAT 대체 표준화 시험(여기서는 SAT 환산치로 표기)"),
         ("AP", "Advanced Placement — 고교 내 대학 수준 심화 과목"),
         ("IB", "International Baccalaureate — 국제 디플로마 과정"),
         ("DE", "Dual Enrollment — 고교 재학 중 취득하는 대학 학점"),
         ("ED", "Early Decision — 구속형 조기 지원(합격 시 등록 의무)"),
         ("EA", "Early Action — 비구속형 조기 지원(등록 의무 없음)"),
         ("REA / SCEA", "제한적/단일 선택 Early Action — 제한적 단일 선택 조기 지원"),
         ("RD", "Regular Decision — 일반 정규 지원 라운드"),
         ("LAC", "Liberal Arts College — 학부 중심 리버럴 아츠 대학"),
         ("OOS", "Out-of-State — 타주(他州) 출신 지원자"),
         ("CDS", "Common Data Set — 대학 공식 통계 자료"),
         ("FAFSA", "Free Application for Federal Student Aid — 연방 학자금 지원 신청서"),
         ("CSS Profile", "College Scholarship Service Profile — 사립대 재정지원 신청서"),
         ("test-optional", "시험 점수 제출 여부를 지원자가 선택하는 정책"),
         ("test-required", "SAT/ACT 점수 제출을 필수로 요구하는 정책"),
         ("test-blind", "제출해도 시험 점수를 전혀 반영하지 않는 정책")]
    if home in STATE_SCHOLARSHIP:
        a.append((STATE_SCHOLARSHIP[home].split("(")[0].strip(), "자격을 갖춘 주내 학생 대상 주(州) 성적 장학금"))
    return a
