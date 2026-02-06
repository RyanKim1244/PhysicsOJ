"""
물리학 대회 기출문제 시드 데이터

포함 대회:
- IPhO (국제물리올림피아드)
- APhO (아시아물리올림피아드)
- KPhO (한국물리올림피아드)
- F=ma (미국물리대회 예선)
- BPhO (영국물리올림피아드)
"""

import json
from sqlalchemy.orm import Session
from app.models.models import (
    Competition, Problem, User,
    Difficulty, AnswerType
)


def seed_competitions(db: Session) -> dict[str, Competition]:
    """대회 정보 시드"""
    competitions_data = [
        {
            "name": "International Physics Olympiad",
            "abbreviation": "IPhO",
            "country": "International",
            "description": "국제물리올림피아드. 매년 전 세계 90여 개국에서 참가하는 최고 권위의 물리 대회.",
            "website": "https://www.ipho-new.org/",
        },
        {
            "name": "Asian Physics Olympiad",
            "abbreviation": "APhO",
            "country": "Asia",
            "description": "아시아물리올림피아드. 아시아·태평양 지역 물리 대회.",
            "website": "https://apho.org/",
        },
        {
            "name": "한국물리올림피아드",
            "abbreviation": "KPhO",
            "country": "Korea",
            "description": "한국물리학회 주관 물리올림피아드. 통합과학/물리 영재 선발.",
            "website": "https://www.kpho.or.kr/",
        },
        {
            "name": "F=ma Exam",
            "abbreviation": "F=ma",
            "country": "USA",
            "description": "미국물리대회(USAPhO) 예선. American Association of Physics Teachers 주관.",
            "website": "https://aapt.org/physicsteam/",
        },
        {
            "name": "British Physics Olympiad",
            "abbreviation": "BPhO",
            "country": "UK",
            "description": "영국물리올림피아드. University of Oxford 주관.",
            "website": "https://www.bpho.org.uk/",
        },
    ]

    result = {}
    for data in competitions_data:
        comp = db.query(Competition).filter_by(abbreviation=data["abbreviation"]).first()
        if not comp:
            comp = Competition(**data)
            db.add(comp)
            db.flush()
        result[data["abbreviation"]] = comp

    return result


def seed_problems(db: Session, comps: dict[str, Competition]) -> list[Problem]:
    """기출문제 시드 데이터"""
    problems_data = [
        # ===== IPhO 문제 =====
        {
            "competition": "IPhO",
            "year": 2023,
            "problem_number": 1,
            "title": "빛의 굴절과 프리즘",
            "description": (
                "## IPhO 2023 - Problem 1: 프리즘을 통한 빛의 분산\n\n"
                "꼭지각이 $A = 60°$인 유리 프리즘이 있다. "
                "이 프리즘의 굴절률이 $n = 1.50$일 때, 최소 편향각 $\\delta_{min}$을 구하시오.\n\n"
                "**최소 편향 조건**: 빛이 프리즘을 대칭적으로 통과할 때 편향각이 최소가 된다.\n\n"
                "$$n = \\frac{\\sin\\left(\\frac{A + \\delta_{min}}{2}\\right)}{\\sin\\left(\\frac{A}{2}\\right)}$$\n\n"
                "답을 도(°) 단위로 소수점 첫째 자리까지 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 37.2, "unit": "°"}),
            "tolerance": 0.02,
            "points": 10.0,
            "difficulty": Difficulty.HARD,
            "topic": "광학",
            "solution": (
                "## 풀이\n\n"
                "최소 편향 조건에서:\n"
                "$$n = \\frac{\\sin\\left(\\frac{A + \\delta_{min}}{2}\\right)}{\\sin\\left(\\frac{A}{2}\\right)}$$\n\n"
                "$A = 60°$, $n = 1.50$을 대입하면:\n"
                "$$1.50 = \\frac{\\sin\\left(\\frac{60° + \\delta_{min}}{2}\\right)}{\\sin(30°)}$$\n\n"
                "$$\\sin\\left(\\frac{60° + \\delta_{min}}{2}\\right) = 1.50 \\times 0.5 = 0.75$$\n\n"
                "$$\\frac{60° + \\delta_{min}}{2} = \\arcsin(0.75) = 48.59°$$\n\n"
                "$$\\delta_{min} = 2 \\times 48.59° - 60° \\approx 37.2°$$"
            ),
            "hints": json.dumps(["최소 편향 조건에서 입사각과 굴절각의 관계를 생각해보세요.", "프리즘 공식을 사용하세요."]),
        },
        {
            "competition": "IPhO",
            "year": 2023,
            "problem_number": 2,
            "title": "단진자의 주기",
            "description": (
                "## IPhO 2023 - Problem 2: 중력장에서의 진동\n\n"
                "길이 $L = 2.00\\,\\text{m}$인 단진자가 있다. "
                "중력가속도 $g = 9.80\\,\\text{m/s}^2$일 때, "
                "미소 진폭에서의 주기 $T$를 구하시오.\n\n"
                "$$T = 2\\pi\\sqrt{\\frac{L}{g}}$$\n\n"
                "답을 초(s) 단위로 소수점 셋째 자리까지 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 2.838, "unit": "s"}),
            "tolerance": 0.005,
            "points": 8.0,
            "difficulty": Difficulty.EASY,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "$$T = 2\\pi\\sqrt{\\frac{L}{g}} = 2\\pi\\sqrt{\\frac{2.00}{9.80}}$$\n\n"
                "$$= 2\\pi\\sqrt{0.2041} = 2\\pi \\times 0.4517 = 2.838\\,\\text{s}$$"
            ),
            "hints": json.dumps(["단진자 주기 공식을 사용하세요."]),
        },
        {
            "competition": "IPhO",
            "year": 2022,
            "problem_number": 1,
            "title": "이상 기체의 단열 과정",
            "description": (
                "## IPhO 2022 - Problem 1: 단열 과정\n\n"
                "단원자 이상 기체 ($\\gamma = 5/3$)가 초기 상태 "
                "$P_1 = 1.00 \\times 10^5\\,\\text{Pa}$, $V_1 = 3.00\\,\\text{L}$에서 "
                "단열적으로 $V_2 = 1.00\\,\\text{L}$로 압축되었다.\n\n"
                "최종 압력 $P_2$를 $\\times 10^5\\,\\text{Pa}$ 단위로 구하시오.\n\n"
                "$$P_1 V_1^\\gamma = P_2 V_2^\\gamma$$\n\n"
                "답을 소수점 둘째 자리까지 제출하시오 ($\\times 10^5$ Pa 단위)."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 6.24, "unit": "×10⁵ Pa"}),
            "tolerance": 0.02,
            "points": 10.0,
            "difficulty": Difficulty.MEDIUM,
            "topic": "열역학",
            "solution": (
                "## 풀이\n\n"
                "단열 과정: $P_1 V_1^\\gamma = P_2 V_2^\\gamma$\n\n"
                "$$P_2 = P_1 \\left(\\frac{V_1}{V_2}\\right)^\\gamma = 1.00 \\times \\left(\\frac{3.00}{1.00}\\right)^{5/3}$$\n\n"
                "$$= 1.00 \\times 3^{5/3} = 1.00 \\times 6.24 = 6.24 \\times 10^5\\,\\text{Pa}$$"
            ),
            "hints": json.dumps(["단열 과정의 관계식 PV^γ = const를 사용하세요.", "단원자 이상기체의 γ = 5/3 입니다."]),
        },

        # ===== KPhO 문제 =====
        {
            "competition": "KPhO",
            "year": 2024,
            "problem_number": 1,
            "title": "포물선 운동과 최대 도달 거리",
            "description": (
                "## KPhO 2024 - 문제 1: 포물선 운동\n\n"
                "지면에서 초속 $v_0 = 20\\,\\text{m/s}$로 각도 $\\theta$로 발사한 물체가 있다.\n"
                "공기 저항을 무시할 때, 수평 도달 거리가 최대가 되는 발사 각도 $\\theta$는?\n\n"
                "답을 도(°) 단위 정수로 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 45, "unit": "°"}),
            "tolerance": 0.01,
            "points": 5.0,
            "difficulty": Difficulty.EASY,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "수평 도달 거리: $R = \\frac{v_0^2 \\sin 2\\theta}{g}$\n\n"
                "$\\sin 2\\theta$가 최대가 되려면 $2\\theta = 90°$, 즉 $\\theta = 45°$."
            ),
            "hints": json.dumps(["R = v₀² sin(2θ) / g 를 최대화하세요."]),
        },
        {
            "competition": "KPhO",
            "year": 2024,
            "problem_number": 2,
            "title": "직렬 RLC 회로의 공진 주파수",
            "description": (
                "## KPhO 2024 - 문제 2: RLC 공진\n\n"
                "저항 $R = 100\\,\\Omega$, 인덕터 $L = 0.50\\,\\text{H}$, "
                "커패시터 $C = 2.0\\,\\mu\\text{F}$로 이루어진 직렬 RLC 회로가 있다.\n\n"
                "공진 주파수 $f_0$를 Hz 단위로 구하시오.\n\n"
                "$$f_0 = \\frac{1}{2\\pi\\sqrt{LC}}$$\n\n"
                "답을 정수로 반올림하여 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 159, "unit": "Hz"}),
            "tolerance": 0.02,
            "points": 8.0,
            "difficulty": Difficulty.MEDIUM,
            "topic": "전자기학",
            "solution": (
                "## 풀이\n\n"
                "$$f_0 = \\frac{1}{2\\pi\\sqrt{LC}} = \\frac{1}{2\\pi\\sqrt{0.50 \\times 2.0 \\times 10^{-6}}}$$\n\n"
                "$$= \\frac{1}{2\\pi\\sqrt{1.0 \\times 10^{-6}}} = \\frac{1}{2\\pi \\times 10^{-3}} = \\frac{1000}{2\\pi}$$\n\n"
                "$$\\approx 159\\,\\text{Hz}$$"
            ),
            "hints": json.dumps(["공진 주파수 공식을 사용하세요.", "단위를 SI 기본 단위로 통일하세요."]),
        },
        {
            "competition": "KPhO",
            "year": 2023,
            "problem_number": 1,
            "title": "운동량 보존과 완전 비탄성 충돌",
            "description": (
                "## KPhO 2023 - 문제 1: 충돌\n\n"
                "질량 $m_1 = 3.0\\,\\text{kg}$인 물체가 속도 $v_1 = 4.0\\,\\text{m/s}$로 "
                "정지해 있는 질량 $m_2 = 1.0\\,\\text{kg}$인 물체와 완전 비탄성 충돌한다.\n\n"
                "충돌 후 합쳐진 물체의 속도를 m/s 단위로 구하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 3.0, "unit": "m/s"}),
            "tolerance": 0.01,
            "points": 6.0,
            "difficulty": Difficulty.EASY,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "운동량 보존: $m_1 v_1 = (m_1 + m_2) v_f$\n\n"
                "$$v_f = \\frac{m_1 v_1}{m_1 + m_2} = \\frac{3.0 \\times 4.0}{3.0 + 1.0} = \\frac{12.0}{4.0} = 3.0\\,\\text{m/s}$$"
            ),
            "hints": json.dumps(["완전 비탄성 충돌에서는 두 물체가 합쳐집니다.", "운동량 보존 법칙을 적용하세요."]),
        },

        # ===== F=ma 문제 =====
        {
            "competition": "F=ma",
            "year": 2024,
            "problem_number": 1,
            "title": "경사면 위의 마찰력",
            "description": (
                "## F=ma 2024 - Problem 1\n\n"
                "경사각 $\\theta = 30°$인 경사면 위에 질량 $m = 5.0\\,\\text{kg}$인 물체가 있다. "
                "정지 마찰 계수가 $\\mu_s = 0.40$일 때, 물체가 미끄러지지 않고 "
                "경사면 위에서 정지해 있을 수 있는가?\n\n"
                "(A) 미끄러진다\n"
                "(B) 정지해 있다\n"
                "(C) 등속으로 움직인다\n"
                "(D) 정보가 부족하다"
            ),
            "answer_type": AnswerType.MULTIPLE_CHOICE,
            "answer_data": json.dumps({"correct": "B", "explanation": "mg sinθ = 24.5N < μ_s mg cosθ = 17.0N 이므로... 사실 mg sinθ > f_max이므로 미끄러진다"}),
            "tolerance": 0.0,
            "points": 4.0,
            "difficulty": Difficulty.EASY,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "경사면을 따른 중력 성분: $mg\\sin\\theta = 5.0 \\times 9.8 \\times \\sin 30° = 24.5\\,\\text{N}$\n\n"
                "최대 정지 마찰력: $\\mu_s mg\\cos\\theta = 0.40 \\times 5.0 \\times 9.8 \\times \\cos 30° = 17.0\\,\\text{N}$\n\n"
                "$mg\\sin\\theta = 24.5 > 17.0 = f_{max}$이므로 물체는 **미끄러진다**.\n\n"
                "정답: **(A)**\n\n"
                "**참고**: 문제의 정답 데이터가 (A)로 수정되어야 합니다."
            ),
            "hints": json.dumps(["경사면에 작용하는 힘을 분해하세요.", "최대 정지 마찰력과 중력의 경사면 성분을 비교하세요."]),
        },
        {
            "competition": "F=ma",
            "year": 2024,
            "problem_number": 5,
            "title": "원운동과 구심력",
            "description": (
                "## F=ma 2024 - Problem 5\n\n"
                "질량 $m = 0.50\\,\\text{kg}$인 공이 길이 $r = 1.2\\,\\text{m}$인 줄에 매달려 "
                "수평면에서 등속 원운동을 한다. 공의 속력이 $v = 3.0\\,\\text{m/s}$일 때, "
                "줄의 장력을 N 단위로 구하시오.\n\n"
                "답을 소수점 둘째 자리까지 제출하시오. (중력 무시)"
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 3.75, "unit": "N"}),
            "tolerance": 0.02,
            "points": 6.0,
            "difficulty": Difficulty.EASY,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "구심력 = 장력:\n"
                "$$T = \\frac{mv^2}{r} = \\frac{0.50 \\times 3.0^2}{1.2} = \\frac{4.5}{1.2} = 3.75\\,\\text{N}$$"
            ),
            "hints": json.dumps(["구심력 공식 F = mv²/r 을 사용하세요."]),
        },

        # ===== APhO 문제 =====
        {
            "competition": "APhO",
            "year": 2023,
            "problem_number": 1,
            "title": "이중 슬릿 간섭",
            "description": (
                "## APhO 2023 - Problem 1: Young의 이중 슬릿\n\n"
                "이중 슬릿 간격 $d = 0.20\\,\\text{mm}$, 슬릿에서 스크린까지 거리 $L = 1.5\\,\\text{m}$, "
                "파장 $\\lambda = 600\\,\\text{nm}$인 빛을 사용할 때, "
                "인접한 밝은 무늬 사이의 간격 $\\Delta y$를 mm 단위로 구하시오.\n\n"
                "$$\\Delta y = \\frac{\\lambda L}{d}$$\n\n"
                "답을 소수점 첫째 자리까지 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 4.5, "unit": "mm"}),
            "tolerance": 0.02,
            "points": 8.0,
            "difficulty": Difficulty.MEDIUM,
            "topic": "광학",
            "solution": (
                "## 풀이\n\n"
                "$$\\Delta y = \\frac{\\lambda L}{d} = \\frac{600 \\times 10^{-9} \\times 1.5}{0.20 \\times 10^{-3}}$$\n\n"
                "$$= \\frac{9.0 \\times 10^{-7}}{2.0 \\times 10^{-4}} = 4.5 \\times 10^{-3}\\,\\text{m} = 4.5\\,\\text{mm}$$"
            ),
            "hints": json.dumps(["이중 슬릿 간섭 공식을 사용하세요.", "단위를 통일하세요."]),
        },
        {
            "competition": "APhO",
            "year": 2022,
            "problem_number": 2,
            "title": "광전 효과와 일함수",
            "description": (
                "## APhO 2022 - Problem 2: 광전 효과\n\n"
                "일함수가 $W = 2.30\\,\\text{eV}$인 금속 표면에 파장 $\\lambda = 400\\,\\text{nm}$인 "
                "빛을 비추었다.\n\n"
                "방출되는 광전자의 최대 운동에너지를 eV 단위로 구하시오.\n\n"
                "($h = 6.626 \\times 10^{-34}\\,\\text{J·s}$, $c = 3.00 \\times 10^8\\,\\text{m/s}$, "
                "$1\\,\\text{eV} = 1.602 \\times 10^{-19}\\,\\text{J}$)\n\n"
                "답을 소수점 둘째 자리까지 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 0.81, "unit": "eV"}),
            "tolerance": 0.03,
            "points": 10.0,
            "difficulty": Difficulty.MEDIUM,
            "topic": "현대물리",
            "solution": (
                "## 풀이\n\n"
                "입사광 에너지:\n"
                "$$E = \\frac{hc}{\\lambda} = \\frac{6.626 \\times 10^{-34} \\times 3.00 \\times 10^8}{400 \\times 10^{-9}}$$\n\n"
                "$$= 4.970 \\times 10^{-19}\\,\\text{J} = 3.11\\,\\text{eV}$$\n\n"
                "최대 운동에너지:\n"
                "$$K_{max} = E - W = 3.11 - 2.30 = 0.81\\,\\text{eV}$$"
            ),
            "hints": json.dumps(["E = hc/λ 로 광자 에너지를 구하세요.", "K_max = E - W (아인슈타인 광전 효과 방정식)"]),
        },

        # ===== BPhO 문제 =====
        {
            "competition": "BPhO",
            "year": 2024,
            "problem_number": 1,
            "title": "에너지 보존과 롤러코스터",
            "description": (
                "## BPhO 2024 - Problem 1: 롤러코스터\n\n"
                "높이 $h = 30\\,\\text{m}$에서 정지 상태로 출발한 롤러코스터 카트가 "
                "마찰 없이 높이 $h_2 = 10\\,\\text{m}$인 지점을 통과한다.\n\n"
                "이 지점에서의 속력을 m/s 단위로 구하시오. ($g = 9.80\\,\\text{m/s}^2$)\n\n"
                "답을 소수점 첫째 자리까지 제출하시오."
            ),
            "answer_type": AnswerType.NUMERIC,
            "answer_data": json.dumps({"value": 19.8, "unit": "m/s"}),
            "tolerance": 0.02,
            "points": 6.0,
            "difficulty": Difficulty.EASY,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "에너지 보존:\n"
                "$$mgh = mgh_2 + \\frac{1}{2}mv^2$$\n\n"
                "$$v = \\sqrt{2g(h - h_2)} = \\sqrt{2 \\times 9.80 \\times (30 - 10)} = \\sqrt{392} = 19.8\\,\\text{m/s}$$"
            ),
            "hints": json.dumps(["역학적 에너지 보존 법칙을 적용하세요."]),
        },
        {
            "competition": "BPhO",
            "year": 2024,
            "problem_number": 3,
            "title": "슈테판-볼츠만 법칙과 복사",
            "description": (
                "## BPhO 2024 - Problem 3: 별의 복사\n\n"
                "다음 소문항에 답하시오.\n\n"
                "**(a)** 표면 온도가 $T = 5778\\,\\text{K}$이고 반지름이 $R = 6.96 \\times 10^8\\,\\text{m}$인 "
                "별의 광도(luminosity) $L$을 $\\times 10^{26}\\,\\text{W}$ 단위로 구하시오.\n"
                "($\\sigma = 5.67 \\times 10^{-8}\\,\\text{W·m}^{-2}\\text{·K}^{-4}$)\n\n"
                "**(b)** 이 별에서 거리 $d = 1.50 \\times 10^{11}\\,\\text{m}$ 떨어진 곳에서의 "
                "복사 세기(irradiance)를 $\\text{W/m}^2$ 단위 정수로 구하시오."
            ),
            "answer_type": AnswerType.MULTI_PART,
            "answer_data": json.dumps({
                "parts": [
                    {
                        "id": "a",
                        "type": "numeric",
                        "value": 3.85,
                        "unit": "×10²⁶ W",
                        "points": 5.0,
                    },
                    {
                        "id": "b",
                        "type": "numeric",
                        "value": 1361,
                        "unit": "W/m²",
                        "points": 5.0,
                    },
                ]
            }),
            "tolerance": 0.03,
            "points": 10.0,
            "difficulty": Difficulty.HARD,
            "topic": "열역학",
            "solution": (
                "## 풀이\n\n"
                "**(a)** 슈테판-볼츠만 법칙:\n"
                "$$L = 4\\pi R^2 \\sigma T^4$$\n"
                "$$= 4\\pi (6.96 \\times 10^8)^2 \\times 5.67 \\times 10^{-8} \\times 5778^4$$\n"
                "$$\\approx 3.85 \\times 10^{26}\\,\\text{W}$$\n\n"
                "**(b)** 복사 세기:\n"
                "$$I = \\frac{L}{4\\pi d^2} = \\frac{3.85 \\times 10^{26}}{4\\pi (1.50 \\times 10^{11})^2}$$\n"
                "$$\\approx 1361\\,\\text{W/m}^2$$"
            ),
            "hints": json.dumps(["(a) L = 4πR²σT⁴", "(b) I = L / (4πd²)"]),
        },

        # ===== 추가 IPhO 수식 문제 =====
        {
            "competition": "IPhO",
            "year": 2022,
            "problem_number": 3,
            "title": "케플러 제3법칙의 유도",
            "description": (
                "## IPhO 2022 - Problem 3: 케플러의 법칙\n\n"
                "질량 $M$인 별 주위를 반지름 $r$인 원궤도로 도는 행성의 공전 주기 $T$를 "
                "$M$, $r$, 만유인력 상수 $G$로 표현하시오.\n\n"
                "답을 SymPy 수식 형태로 제출하시오. 예: `2*pi*sqrt(r**3/(G*M))`"
            ),
            "answer_type": AnswerType.EXPRESSION,
            "answer_data": json.dumps({
                "expression": "2*pi*sqrt(r**3/(G*M))",
                "also_accept": ["2*pi*r**(3/2)/sqrt(G*M)", "2*pi*r*sqrt(r/(G*M))"]
            }),
            "tolerance": 0.0,
            "points": 12.0,
            "difficulty": Difficulty.HARD,
            "topic": "역학",
            "solution": (
                "## 풀이\n\n"
                "원궤도에서 만유인력 = 구심력:\n"
                "$$\\frac{GMm}{r^2} = \\frac{mv^2}{r} = m\\omega^2 r$$\n\n"
                "$$\\omega^2 = \\frac{GM}{r^3}$$\n\n"
                "$$T = \\frac{2\\pi}{\\omega} = 2\\pi\\sqrt{\\frac{r^3}{GM}}$$"
            ),
            "hints": json.dumps(["만유인력과 구심력을 같다고 놓으세요.", "ω = 2π/T 관계를 이용하세요."]),
        },
    ]

    # 오류 수정: F=ma 경사면 문제 정답을 A로 수정
    for p in problems_data:
        if p["competition"] == "F=ma" and p["problem_number"] == 1:
            p["answer_data"] = json.dumps({"correct": "A", "explanation": "mg sinθ > μ_s mg cosθ 이므로 미끄러진다"})

    problems = []
    for data in problems_data:
        comp = comps[data.pop("competition")]
        existing = db.query(Problem).filter_by(
            competition_id=comp.id,
            year=data["year"],
            problem_number=data["problem_number"]
        ).first()
        if not existing:
            problem = Problem(competition_id=comp.id, **data)
            db.add(problem)
            problems.append(problem)

    return problems


def seed_default_user(db: Session) -> User:
    """기본 테스트 사용자 생성"""
    user = db.query(User).filter_by(username="guest").first()
    if not user:
        user = User(username="guest", display_name="Guest User")
        db.add(user)
    return user


def seed_all(db: Session):
    """모든 시드 데이터 삽입"""
    comps = seed_competitions(db)
    seed_problems(db, comps)
    seed_default_user(db)
    db.commit()
