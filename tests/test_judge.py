"""Tests for the Physics Judge engine."""

import json
import pytest
from app.services.judge import (
    judge, judge_numeric, judge_expression,
    judge_multiple_choice, judge_multi_part,
    _parse_number, _compare_numeric, _compare_expression,
    JudgeResult,
)


class TestParseNumber:
    def test_integer(self):
        assert _parse_number("42") == 42.0

    def test_float(self):
        assert _parse_number("3.14") == pytest.approx(3.14)

    def test_negative(self):
        assert _parse_number("-2.5") == -2.5

    def test_scientific_notation(self):
        assert _parse_number("3e8") == 3e8

    def test_custom_scientific(self):
        assert _parse_number("2.5×10^3") == 2500.0

    def test_fraction(self):
        assert _parse_number("3/4") == pytest.approx(0.75)

    def test_sympy_expression(self):
        result = _parse_number("sqrt(2)")
        assert result == pytest.approx(1.41421356, rel=1e-5)

    def test_invalid(self):
        assert _parse_number("hello") is None

    def test_spaces(self):
        assert _parse_number("  42  ") == 42.0


class TestCompareNumeric:
    def test_exact_match(self):
        is_correct, _ = _compare_numeric(3.14, 3.14, 0.01)
        assert is_correct

    def test_within_tolerance(self):
        is_correct, _ = _compare_numeric(3.15, 3.14, 0.01)
        assert is_correct

    def test_outside_tolerance(self):
        is_correct, _ = _compare_numeric(3.20, 3.14, 0.01)
        assert not is_correct

    def test_zero_correct_value(self):
        is_correct, _ = _compare_numeric(0.001, 0, 0.01)
        assert is_correct

    def test_zero_both(self):
        is_correct, _ = _compare_numeric(0, 0, 0.01)
        assert is_correct


class TestCompareExpression:
    def test_identical(self):
        assert _compare_expression("x**2", "x**2")

    def test_equivalent(self):
        assert _compare_expression("x**2 + 2*x + 1", "(x+1)**2")

    def test_different(self):
        assert not _compare_expression("x**2", "x**3")

    def test_trig_identity(self):
        assert _compare_expression("sin(x)**2 + cos(x)**2", "1")

    def test_with_constants(self):
        assert _compare_expression("2*pi", "2*pi")


class TestJudgeNumeric:
    def test_correct_answer(self):
        answer_data = {"value": 37.2, "unit": "°"}
        result = judge_numeric("37.2", answer_data, 0.02, 10.0)
        assert result.is_correct
        assert result.score == 10.0

    def test_within_tolerance(self):
        answer_data = {"value": 37.2, "unit": "°"}
        result = judge_numeric("37.5", answer_data, 0.02, 10.0)
        assert result.is_correct

    def test_wrong_answer(self):
        answer_data = {"value": 37.2, "unit": "°"}
        result = judge_numeric("40.0", answer_data, 0.02, 10.0)
        assert not result.is_correct
        assert result.score == 0.0

    def test_unparseable(self):
        answer_data = {"value": 37.2, "unit": "°"}
        result = judge_numeric("abc", answer_data, 0.02, 10.0)
        assert not result.is_correct


class TestJudgeExpression:
    def test_kepler_third_law(self):
        answer_data = {
            "expression": "2*pi*sqrt(r**3/(G*M))",
            "also_accept": ["2*pi*r**(3/2)/sqrt(G*M)"],
        }
        result = judge_expression("2*pi*sqrt(r**3/(G*M))", answer_data, 12.0)
        assert result.is_correct
        assert result.score == 12.0

    def test_alternative_form(self):
        answer_data = {
            "expression": "2*pi*sqrt(r**3/(G*M))",
            "also_accept": ["2*pi*r**(3/2)/sqrt(G*M)"],
        }
        result = judge_expression("2*pi*r**(3/2)/sqrt(G*M)", answer_data, 12.0)
        assert result.is_correct

    def test_wrong_expression(self):
        answer_data = {
            "expression": "2*pi*sqrt(r**3/(G*M))",
            "also_accept": [],
        }
        result = judge_expression("pi*sqrt(r**3/(G*M))", answer_data, 12.0)
        assert not result.is_correct


class TestJudgeMultipleChoice:
    def test_correct(self):
        result = judge_multiple_choice("A", {"correct": "A"}, 4.0)
        assert result.is_correct
        assert result.score == 4.0

    def test_case_insensitive(self):
        result = judge_multiple_choice("a", {"correct": "A"}, 4.0)
        assert result.is_correct

    def test_wrong(self):
        result = judge_multiple_choice("B", {"correct": "A"}, 4.0)
        assert not result.is_correct


class TestJudgeMultiPart:
    def test_all_correct(self):
        answer_data = {
            "parts": [
                {"id": "a", "type": "numeric", "value": 3.85, "points": 5.0},
                {"id": "b", "type": "numeric", "value": 1361, "points": 5.0},
            ]
        }
        user_answer = json.dumps({"a": "3.85", "b": "1361"})
        result = judge_multi_part(user_answer, answer_data, 0.03, 10.0)
        assert result.is_correct
        assert result.score == pytest.approx(10.0)

    def test_partial(self):
        answer_data = {
            "parts": [
                {"id": "a", "type": "numeric", "value": 3.85, "points": 5.0},
                {"id": "b", "type": "numeric", "value": 1361, "points": 5.0},
            ]
        }
        user_answer = json.dumps({"a": "3.85", "b": "999"})
        result = judge_multi_part(user_answer, answer_data, 0.03, 10.0)
        assert not result.is_correct
        assert result.score == pytest.approx(5.0)

    def test_invalid_json(self):
        answer_data = {"parts": []}
        result = judge_multi_part("not json", answer_data, 0.03, 10.0)
        assert not result.is_correct


class TestMainJudge:
    def test_numeric_via_main(self):
        result = judge("37.2", "numeric", json.dumps({"value": 37.2, "unit": "°"}), 0.02, 10.0)
        assert result.is_correct

    def test_multiple_choice_via_main(self):
        result = judge("A", "multiple_choice", json.dumps({"correct": "A"}), 0.0, 4.0)
        assert result.is_correct

    def test_unknown_type(self):
        result = judge("x", "unknown_type", "{}", 0.01, 10.0)
        assert not result.is_correct
        assert "알 수 없는" in result.feedback

    def test_invalid_json_answer_data(self):
        result = judge("x", "numeric", "not json", 0.01, 10.0)
        assert not result.is_correct
