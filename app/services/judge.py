"""
Physics Judge - 물리학 답안 채점 엔진

채점 유형:
1. NUMERIC: 수치 답 비교 (상대/절대 오차 허용)
2. EXPRESSION: 수식 동치 비교 (SymPy 활용)
3. MULTIPLE_CHOICE: 객관식 정답 비교
4. MULTI_PART: 여러 소문항 각각 채점 후 합산
"""

import json
import math
import re
from typing import Any

from sympy import sympify, simplify, N
from sympy.parsing.latex import parse_latex


class JudgeResult:
    """채점 결과를 담는 객체"""

    def __init__(self, is_correct: bool, score: float, max_score: float,
                 feedback: str, details: dict | None = None):
        self.is_correct = is_correct
        self.score = score
        self.max_score = max_score
        self.feedback = feedback
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "is_correct": self.is_correct,
            "score": self.score,
            "max_score": self.max_score,
            "feedback": self.feedback,
            "details": self.details,
        }


def _parse_number(s: str) -> float | None:
    """문자열에서 숫자를 파싱. 과학적 표기법, 분수 등 지원."""
    s = s.strip().replace(" ", "")

    # 분수 처리: "3/4" -> 0.75
    if "/" in s and not any(c.isalpha() for c in s):
        parts = s.split("/")
        if len(parts) == 2:
            try:
                return float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                pass

    # 과학적 표기법 및 일반 숫자
    s = s.replace("×10^", "e").replace("x10^", "e").replace("*10^", "e")
    s = s.replace("×10**", "e").replace("x10**", "e").replace("*10**", "e")
    try:
        return float(s)
    except ValueError:
        pass

    # SymPy로 수식 평가
    try:
        expr = sympify(s)
        result = float(N(expr))
        if math.isfinite(result):
            return result
    except Exception:
        pass

    return None


def _compare_numeric(user_val: float, correct_val: float,
                     tolerance: float) -> tuple[bool, float]:
    """
    수치 비교. tolerance는 상대 오차 비율.
    Returns (is_correct, closeness_ratio)
    """
    if correct_val == 0:
        diff = abs(user_val)
        is_correct = diff <= tolerance
        closeness = 1.0 - min(diff, 1.0) if is_correct else 0.0
        return is_correct, closeness

    relative_error = abs(user_val - correct_val) / abs(correct_val)
    is_correct = relative_error <= tolerance
    closeness = max(0.0, 1.0 - relative_error / tolerance) if tolerance > 0 else (1.0 if is_correct else 0.0)
    return is_correct, closeness


def _compare_expression(user_str: str, correct_str: str) -> bool:
    """SymPy를 이용한 수식 동치 비교"""
    try:
        # LaTeX 파싱 시도
        try:
            user_expr = parse_latex(user_str)
        except Exception:
            user_expr = sympify(user_str)

        try:
            correct_expr = parse_latex(correct_str)
        except Exception:
            correct_expr = sympify(correct_str)

        diff = simplify(user_expr - correct_expr)
        if diff == 0:
            return True

        # 수치적으로 비교 (기호가 없는 경우)
        if not diff.free_symbols:
            return abs(float(N(diff))) < 1e-10

        # 기호 변수가 있으면 simplify 결과가 0인지 확인
        return simplify(diff).equals(0)
    except Exception:
        return False


def judge_numeric(user_answer: str, answer_data: dict,
                  tolerance: float, max_points: float) -> JudgeResult:
    """수치 답 채점"""
    correct_value = answer_data["value"]
    unit = answer_data.get("unit", "")

    user_num = _parse_number(user_answer)
    if user_num is None:
        return JudgeResult(
            is_correct=False, score=0.0, max_score=max_points,
            feedback=f"입력을 숫자로 파싱할 수 없습니다: '{user_answer}'"
        )

    correct_num = float(correct_value)
    is_correct, closeness = _compare_numeric(user_num, correct_num, tolerance)

    if is_correct:
        score = max_points
        feedback = "정답입니다!"
        if unit:
            feedback += f" (단위: {unit})"
    else:
        score = 0.0
        relative_error = abs(user_num - correct_num) / abs(correct_num) if correct_num != 0 else abs(user_num)
        feedback = f"오답입니다. 상대 오차: {relative_error:.2%} (허용: {tolerance:.2%})"

    return JudgeResult(
        is_correct=is_correct, score=score, max_score=max_points,
        feedback=feedback,
        details={"user_value": user_num, "relative_error": abs(user_num - correct_num) / abs(correct_num) if correct_num != 0 else None}
    )


def judge_expression(user_answer: str, answer_data: dict,
                     max_points: float) -> JudgeResult:
    """수식 답 채점"""
    correct_expr = answer_data["expression"]
    accept_list = answer_data.get("also_accept", [])

    all_correct = [correct_expr] + accept_list

    for expr in all_correct:
        if _compare_expression(user_answer, expr):
            return JudgeResult(
                is_correct=True, score=max_points, max_score=max_points,
                feedback="정답입니다!"
            )

    return JudgeResult(
        is_correct=False, score=0.0, max_score=max_points,
        feedback="수식이 정답과 일치하지 않습니다."
    )


def judge_multiple_choice(user_answer: str, answer_data: dict,
                          max_points: float) -> JudgeResult:
    """객관식 채점"""
    correct = str(answer_data["correct"]).strip().upper()
    user = user_answer.strip().upper()

    is_correct = user == correct
    score = max_points if is_correct else 0.0
    feedback = "정답입니다!" if is_correct else f"오답입니다."

    return JudgeResult(
        is_correct=is_correct, score=score, max_score=max_points,
        feedback=feedback
    )


def judge_multi_part(user_answer: str, answer_data: dict,
                     tolerance: float, max_points: float) -> JudgeResult:
    """여러 소문항 채점"""
    try:
        user_parts = json.loads(user_answer)
    except json.JSONDecodeError:
        return JudgeResult(
            is_correct=False, score=0.0, max_score=max_points,
            feedback="답안을 JSON 형식으로 파싱할 수 없습니다. 예: {\"a\": \"답1\", \"b\": \"답2\"}"
        )

    parts = answer_data["parts"]
    total_score = 0.0
    total_max = 0.0
    part_results = {}

    for part in parts:
        part_id = part["id"]
        part_type = part["type"]
        part_points = part.get("points", max_points / len(parts))
        total_max += part_points

        user_part_answer = user_parts.get(part_id, "")
        if not user_part_answer:
            part_results[part_id] = {"score": 0, "max": part_points, "feedback": "미응답"}
            continue

        if part_type == "numeric":
            result = judge_numeric(
                str(user_part_answer),
                {"value": part["value"], "unit": part.get("unit", "")},
                tolerance, part_points
            )
        elif part_type == "expression":
            result = judge_expression(
                str(user_part_answer),
                {"expression": part["expression"], "also_accept": part.get("also_accept", [])},
                part_points
            )
        elif part_type == "multiple_choice":
            result = judge_multiple_choice(
                str(user_part_answer),
                {"correct": part["correct"]},
                part_points
            )
        else:
            result = JudgeResult(False, 0, part_points, f"알 수 없는 유형: {part_type}")

        total_score += result.score
        part_results[part_id] = {
            "score": result.score,
            "max": part_points,
            "feedback": result.feedback,
        }

    is_correct = total_score >= total_max - 1e-9
    feedback_parts = [f"({pid}) {r['feedback']} [{r['score']}/{r['max']}점]"
                      for pid, r in part_results.items()]
    feedback = "\n".join(feedback_parts)

    return JudgeResult(
        is_correct=is_correct, score=total_score, max_score=total_max,
        feedback=feedback, details={"parts": part_results}
    )


def judge(user_answer: str, answer_type: str, answer_data_json: str,
          tolerance: float = 0.01, max_points: float = 10.0) -> JudgeResult:
    """
    메인 채점 함수.

    Args:
        user_answer: 사용자 제출 답안
        answer_type: "numeric", "expression", "multiple_choice", "multi_part"
        answer_data_json: 정답 데이터 (JSON 문자열)
        tolerance: 수치 오차 허용 비율
        max_points: 최대 점수

    Returns:
        JudgeResult
    """
    try:
        answer_data = json.loads(answer_data_json)
    except json.JSONDecodeError:
        return JudgeResult(
            is_correct=False, score=0.0, max_score=max_points,
            feedback="[시스템 오류] 정답 데이터 파싱 실패"
        )

    if answer_type == "numeric":
        return judge_numeric(user_answer, answer_data, tolerance, max_points)
    elif answer_type == "expression":
        return judge_expression(user_answer, answer_data, max_points)
    elif answer_type == "multiple_choice":
        return judge_multiple_choice(user_answer, answer_data, max_points)
    elif answer_type == "multi_part":
        return judge_multi_part(user_answer, answer_data, tolerance, max_points)
    else:
        return JudgeResult(
            is_correct=False, score=0.0, max_score=max_points,
            feedback=f"[시스템 오류] 알 수 없는 답안 유형: {answer_type}"
        )
