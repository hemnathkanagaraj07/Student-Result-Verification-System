"""
Automated Unit Tests for Student Result Verification System.
Designed for BSc IT Software Testing Laboratory.

Test Techniques Demonstrated:
1. Equivalence Class Partitioning (ECP)
2. Boundary Value Analysis (BVA)
3. Negative / Robustness Testing
4. Calculation & Business Rule Verification
"""

import pytest
from calculator import (
    validate_mark,
    validate_student_input,
    calculate_total,
    calculate_percentage,
    calculate_status,
    calculate_grade,
    compute_student_result,
    PASSING_MARK,
    MAX_MARK,
    MIN_MARK,
)


class TestBoundaryValueAnalysis:
    """
    Boundary Value Analysis (BVA) on marks validation:
    Valid range is [0.0, 100.0]. Passing threshold is 35.0.
    Boundaries to test:
    - Below Min: -1, -0.01
    - Min Boundary: 0
    - Above Min: 0.01, 1
    - Below Passing: 34, 34.99
    - Passing Boundary: 35.0
    - Above Passing: 35.01, 36
    - Below Max: 99, 99.99
    - Max Boundary: 100.0
    - Above Max: 100.01, 101
    """

    def test_bva_minimum_valid_boundary_zero(self):
        is_valid, mark, err = validate_mark(0)
        assert is_valid is True
        assert mark == 0.0
        assert err is None

    def test_bva_just_below_minimum_negative(self):
        is_valid, mark, err = validate_mark(-0.01)
        assert is_valid is False
        assert mark is None
        assert "below minimum" in err.lower()

    def test_bva_just_above_minimum(self):
        is_valid, mark, err = validate_mark(0.01)
        assert is_valid is True
        assert mark == 0.01

    def test_bva_passing_boundary_exact_35(self):
        is_valid, mark, err = validate_mark(35)
        assert is_valid is True
        assert mark == 35.0

    def test_bva_just_below_passing_34(self):
        is_valid, mark, err = validate_mark(34.99)
        assert is_valid is True
        assert mark == 34.99

    def test_bva_maximum_valid_boundary_hundred(self):
        is_valid, mark, err = validate_mark(100)
        assert is_valid is True
        assert mark == 100.0
        assert err is None

    def test_bva_just_above_maximum(self):
        is_valid, mark, err = validate_mark(100.01)
        assert is_valid is False
        assert mark is None
        assert "exceeds maximum" in err.lower()

    def test_bva_far_above_maximum(self):
        is_valid, mark, err = validate_mark(150)
        assert is_valid is False
        assert "exceeds maximum" in err.lower()

    def test_bva_far_below_minimum(self):
        is_valid, mark, err = validate_mark(-50)
        assert is_valid is False
        assert "below minimum" in err.lower()


class TestEquivalencePartitioningAndValidation:
    """
    Equivalence Class Partitioning for mark inputs:
    Partition 1 (Valid): Real numbers in [0, 100] as int, float, or valid numeric string.
    Partition 2 (Invalid Range): Numbers < 0 or > 100.
    Partition 3 (Invalid Type/Format): Non-numeric string, None, empty string, symbols.
    """

    @pytest.mark.parametrize("valid_input, expected", [
        (75, 75.0),
        ("85.5", 85.5),
        ("90", 90.0),
        (50.25, 50.25),
        (" 42 ", 42.0),
    ])
    def test_valid_numeric_inputs(self, valid_input, expected):
        is_valid, mark, err = validate_mark(valid_input)
        assert is_valid is True
        assert mark == expected
        assert err is None

    @pytest.mark.parametrize("invalid_input", [
        "abc",
        "xyz99",
        "100%",
        "A+",
        "!@#$",
        "None",
    ])
    def test_invalid_non_numeric_strings(self, invalid_input):
        is_valid, mark, err = validate_mark(invalid_input)
        assert is_valid is False
        assert mark is None
        assert "valid number" in err.lower()

    @pytest.mark.parametrize("empty_input", [
        None,
        "",
        "   ",
        "\t",
    ])
    def test_empty_or_whitespace_marks(self, empty_input):
        is_valid, mark, err = validate_mark(empty_input)
        assert is_valid is False
        assert mark is None
        assert "cannot be empty" in err.lower()


class TestStudentInputPayloadValidation:
    """Tests comprehensive validation of student form data."""

    def test_valid_student_payload(self):
        payload = {
            "name": "Hemant Sharma",
            "roll_no": "IT-101",
            "marks": {
                "sub1": 70,
                "sub2": 80,
                "sub3": 85,
                "sub4": 90,
                "sub5": 65,
            }
        }
        is_valid, cleaned, errors = validate_student_input(payload)
        assert is_valid is True
        assert len(errors) == 0
        assert cleaned["name"] == "Hemant Sharma"
        assert cleaned["roll_no"] == "IT-101"
        assert cleaned["marks"]["sub1"] == 70.0

    def test_missing_student_name(self):
        payload = {
            "name": "",
            "roll_no": "IT-102",
            "marks": {"sub1": 50, "sub2": 50, "sub3": 50, "sub4": 50, "sub5": 50}
        }
        is_valid, _, errors = validate_student_input(payload)
        assert is_valid is False
        assert any("Name is required" in e for e in errors)

    def test_missing_roll_number(self):
        payload = {
            "name": "Aarav Patel",
            "roll_no": "   ",
            "marks": {"sub1": 50, "sub2": 50, "sub3": 50, "sub4": 50, "sub5": 50}
        }
        is_valid, _, errors = validate_student_input(payload)
        assert is_valid is False
        assert any("Roll Number is required" in e for e in errors)

    def test_missing_subject_marks(self):
        payload = {
            "name": "Priya",
            "roll_no": "IT-103",
            "marks": {"sub1": 50, "sub2": 60}  # sub3, sub4, sub5 missing
        }
        is_valid, _, errors = validate_student_input(payload)
        assert is_valid is False
        assert len(errors) >= 3

    def test_multiple_validation_errors_reported(self):
        payload = {
            "name": "",
            "roll_no": "",
            "marks": {"sub1": 150, "sub2": -5, "sub3": "abc", "sub4": "", "sub5": 50}
        }
        is_valid, _, errors = validate_student_input(payload)
        assert is_valid is False
        # Multiple errors caught simultaneously
        assert len(errors) >= 5


class TestTotalCalculation:
    """Verifies total marks calculation across 5 subjects."""

    def test_total_with_all_hundreds(self):
        marks = {"sub1": 100, "sub2": 100, "sub3": 100, "sub4": 100, "sub5": 100}
        assert calculate_total(marks) == 500.0

    def test_total_with_all_zeros(self):
        marks = [0, 0, 0, 0, 0]
        assert calculate_total(marks) == 0.0

    def test_total_with_decimal_marks(self):
        marks = [45.5, 62.5, 78.0, 81.5, 90.0]
        assert calculate_total(marks) == 357.5

    def test_total_with_passing_marks(self):
        marks = [35, 35, 35, 35, 35]
        assert calculate_total(marks) == 175.0


class TestPercentageCalculation:
    """Verifies percentage calculation formulas."""

    def test_percentage_all_full_marks(self):
        assert calculate_percentage(500.0, 5) == 100.0

    def test_percentage_all_zero(self):
        assert calculate_percentage(0.0, 5) == 0.0

    def test_percentage_exact_passing_total(self):
        # 175 out of 500 = 35%
        assert calculate_percentage(175.0, 5) == 35.0

    def test_percentage_rounding_precision(self):
        # 333 out of 500 = 66.6%
        assert calculate_percentage(333.0, 5) == 66.6

    def test_invalid_subject_count_raises_error(self):
        with pytest.raises(ValueError):
            calculate_percentage(200.0, 0)


class TestPassFailLogic:
    """
    CRITICAL RULE FOR SOFTWARE TESTING:
    Rule: A student passes only if marks in ALL 5 subjects >= 35.0.
    Even if the total score is very high (e.g., 434/500), if one subject < 35, student FAILS.
    """

    def test_student_passes_when_all_above_passing(self):
        marks = [70, 80, 85, 90, 65]
        assert calculate_status(marks, PASSING_MARK) == "Pass"

    def test_student_passes_when_all_exact_boundary_35(self):
        marks = [35.0, 35.0, 35.0, 35.0, 35.0]
        assert calculate_status(marks, PASSING_MARK) == "Pass"

    def test_student_fails_when_single_subject_below_35(self):
        # 4 distinctions, 1 fail mark of 34
        marks = [100.0, 100.0, 100.0, 100.0, 34.0]
        assert calculate_status(marks, PASSING_MARK) == "Fail"

    def test_student_fails_when_one_subject_zero(self):
        marks = [85, 90, 0, 75, 80]
        assert calculate_status(marks, PASSING_MARK) == "Fail"

    def test_student_fails_when_all_marks_below_35(self):
        marks = [30, 25, 20, 34, 15]
        assert calculate_status(marks, PASSING_MARK) == "Fail"


class TestGradingLogic:
    """Verifies academic grade assignments."""

    def test_failed_student_always_gets_f(self):
        # High percentage but failed due to 1 subject
        assert calculate_grade(85.0, "Fail") == "F"

    @pytest.mark.parametrize("pct, expected_grade", [
        (95.0, "A+"),
        (90.0, "A+"),
        (85.0, "A"),
        (80.0, "A"),
        (75.0, "B+"),
        (70.0, "B+"),
        (65.0, "B"),
        (60.0, "B"),
        (55.0, "C"),
        (50.0, "C"),
        (35.0, "D"),
        (34.9, "F"),
    ])
    def test_grade_boundaries_when_passed(self, pct, expected_grade):
        assert calculate_grade(pct, "Pass") == expected_grade


class TestCompleteResultWorkflow:
    """Verifies end-to-end result calculation."""

    def test_full_pipeline_topper(self):
        marks = {"sub1": 95, "sub2": 92, "sub3": 89, "sub4": 96, "sub5": 98}
        result = compute_student_result("Alice Cooper", "BSc-01", marks)
        assert result["total"] == 470.0
        assert result["percentage"] == 94.0
        assert result["status"] == "Pass"
        assert result["grade"] == "A+"

    def test_full_pipeline_marginal_pass(self):
        marks = {"sub1": 35, "sub2": 35, "sub3": 35, "sub4": 35, "sub5": 35}
        result = compute_student_result("Bob Minimal", "BSc-02", marks)
        assert result["total"] == 175.0
        assert result["percentage"] == 35.0
        assert result["status"] == "Pass"
        assert result["grade"] == "D"

    def test_full_pipeline_single_failure(self):
        marks = {"sub1": 80, "sub2": 90, "sub3": 85, "sub4": 34, "sub5": 88}
        result = compute_student_result("Charlie Edge", "BSc-03", marks)
        assert result["total"] == 377.0
        assert result["percentage"] == 75.4
        assert result["status"] == "Fail"
        assert result["grade"] == "F"
