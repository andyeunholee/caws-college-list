# -*- coding: utf-8 -*-
"""
i18n.py — fixed UI strings for the report in English and Korean.
College names, state codes, and student-written fields stay in English.
"""

ENG = {
    "subtitle": "College Admissions Strategy Report",
    "title": "Comprehensive College Admissions Strategy Report",
    "cycle_suffix": "Application Cycle",
    "grade_senior": "12th Grade (Senior)",
    "confidential": "CONFIDENTIAL",
    "info": {
        "Name": "Name", "High School": "High School", "Residence": "Residence",
        "Unweighted GPA": "Unweighted GPA", "Weighted GPA": "Weighted GPA",
        "Class Rank": "Class Rank", "Test Score": "Test Score",
        "Advanced Courses": "Advanced Courses", "Intended Major": "Intended Major",
        "Early Plan": "Early Plan", "Leadership": "Leadership",
        "Community Service": "Community Service",
        "Talents / Key Activities": "Talents / Key Activities",
        "Awards & Honors": "Awards & Honors", "Essays & Recs": "Essays & Recs",
        "Citizenship": "Citizenship",
    },
    "sec": {
        1: "1.  Methodology · Evaluation Criteria",
        2: "2.  National University List",
        3: "3.  In-State Universities · %s",
        4: "4.  Liberal Arts College (LAC) List",
        5: "5.  Early Decision (ED) Strategy · RD vs ED Comparison",
        6: "6.  Early Action (EA / REA) Strategy",
        7: "7.  12th-Grade Action Plan (From Now Through Application)",
        8: "8.  Abbreviations · Full Description",
    },
    "tier_long": ("REACH (Est. Admit Probability ≤ 20%)",
                  "MATCH (Est. Admit Probability 21–55%)",
                  "SAFETY (Est. Admit Probability ≥ 60%)"),
    "tier_short": ("REACH", "MATCH", "SAFETY"),
    "badges": ("Reach  ·  Est. ≤ 20%", "Match  ·  Est. 21–55%", "Safety  ·  Est. ≥ 60%"),
    "th_list": ("No.", "College", "State", "Est. Admit Probability"),
    "th_ed": ("College", "State", "RD Prob.", "ED Prob.", "Recommendation"),
    "th_ea": ("College", "State", "EA Prob.", "Notes (Policy / Caution)"),
    "th_abbr": ("Abbreviation", "Full Description"),
    "abbr_intro": "Full names and meanings of the abbreviations used in this report and its key notes.",
    "none_tier": "— no schools fell in this tier for this profile —",
    "ed_none": "No Early-Decision schools matched this profile’s reach/match band.",
    "ea_none": "No Early-Action schools matched this profile.",
}

KOR = {
    "subtitle": "대학 입시 전략 리포트",
    "title": "종합 대학 입시 전략 리포트",
    "cycle_suffix": "지원 사이클",
    "grade_senior": "12학년 (졸업반)",
    "confidential": "대외비",
    "info": {
        "Name": "이름", "High School": "고등학교", "Residence": "거주지",
        "Unweighted GPA": "비가중 GPA", "Weighted GPA": "가중 GPA",
        "Class Rank": "석차", "Test Score": "시험 점수",
        "Advanced Courses": "심화 과목", "Intended Major": "희망 전공",
        "Early Plan": "조기 지원 계획", "Leadership": "리더십",
        "Community Service": "봉사활동 시간",
        "Talents / Key Activities": "특기 / 주요 활동",
        "Awards & Honors": "수상 경력", "Essays & Recs": "에세이 · 추천서",
        "Citizenship": "시민권",
    },
    "sec": {
        1: "1.  평가 방법론 · 산정 기준",
        2: "2.  전국 대학 리스트",
        3: "3.  거주 주(州) 내 대학 · %s",
        4: "4.  리버럴 아츠 칼리지(LAC) 리스트",
        5: "5.  Early Decision(ED) 전략 · RD와 ED 비교",
        6: "6.  Early Action(EA / REA) 전략",
        7: "7.  12학년 실행 계획 (지금부터 지원까지)",
        8: "8.  약어 · 전체 설명",
    },
    "tier_long": ("REACH · 도전 (추정 합격률 ≤ 20%)",
                  "MATCH · 적정 (추정 합격률 21–55%)",
                  "SAFETY · 안정 (추정 합격률 ≥ 60%)"),
    "tier_short": ("REACH · 도전", "MATCH · 적정", "SAFETY · 안정"),
    "badges": ("Reach · 도전  ·  ≤ 20%", "Match · 적정  ·  21–55%", "Safety · 안정  ·  ≥ 60%"),
    "th_list": ("번호", "대학", "주", "추정 합격 확률"),
    "th_ed": ("대학", "주", "RD 확률", "ED 확률", "추천"),
    "th_ea": ("대학", "주", "EA 확률", "비고 (정책 / 유의사항)"),
    "th_abbr": ("약어", "전체 설명"),
    "abbr_intro": "이 리포트와 핵심 노트에 사용된 약어의 전체 명칭과 의미입니다.",
    "none_tier": "— 이 프로필에서는 해당 티어에 속한 학교가 없습니다 —",
    "ed_none": "이 프로필의 도전~적정 구간에 맞는 Early Decision 학교가 없습니다.",
    "ea_none": "이 프로필에 맞는 Early Action 학교가 없습니다.",
}


def T(lang):
    return KOR if lang == "Kor" else ENG
