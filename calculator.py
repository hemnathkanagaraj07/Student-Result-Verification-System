"""
Student Result Verification System - Core Calculation and Validation Engine
Designed for BSc IT Software Testing Laboratory.
"""

from typing import Dict, List, Tuple, Union, Any

# Subject definitions for BSc IT
SUBJECT_KEYS = ["sub1", "sub2", "sub3", "sub4", "sub5"]
SUBJECT_NAMES = {
    "sub1": "Software Engineering",
    "sub2": "Python Programming",
    "sub3": "Database Management",
    "sub4": "Web Technologies",
    "sub5": "Software Testing & QA",
}

PASSING_MARK = 35.0
MAX_MARK = 100.0
MIN_MARK = 0.0
TOTAL_SUBJECTS = 5
MAX_TOTAL = MAX_MARK * TOTAL_SUBJECTS


def validate_mark(value: Any) -> Tuple[bool, Union[float, None], Union[str, None]]:
    """
    Validates a single subject mark against boundary and type criteria.
    Criteria:
    - Must not be empty or None
    - Must be numeric (int or float)
    - Must satisfy 0.0 <= mark <= 100.0 (Boundary Value Analysis: 0, 35, 100)
    """
    if value is None:
        return False, None, "Mark cannot be empty."

    # Handle string values
    if isinstance(value, str):
        val_str = value.strip()
        if val_str == "":
            return False, None, "Mark cannot be empty."
        try:
            num = float(val_str)
        except ValueError:
            return False, None, f"Mark '{value}' must be a valid number."
    elif isinstance(value, (int, float)):
        num = float(value)
    else:
        return False, None, "Invalid mark format."

    # Boundary checks
    if num < MIN_MARK:
        return False, None, f"Mark {num} is below minimum allowed value ({MIN_MARK})."
    if num > MAX_MARK:
        return False, None, f"Mark {num} exceeds maximum allowed value ({MAX_MARK})."

    # Return valid rounded float
    return True, round(num, 2), None


def validate_student_input(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validates complete student submission payload.
    Validates name, roll number, and marks for all 5 subjects.
    Returns: (is_valid, cleaned_data, list_of_errors)
    """
    errors: List[str] = []
    cleaned: Dict[str, Any] = {}

    if not isinstance(data, dict):
        return False, {}, ["Input payload must be a JSON dictionary."]

    # 1. Validate Student Name
    name = data.get("name")
    if name is None or str(name).strip() == "":
        errors.append("Student Name is required.")
    else:
        name_str = str(name).strip()
        if len(name_str) < 2:
            errors.append("Student Name must be at least 2 characters long.")
        elif len(name_str) > 60:
            errors.append("Student Name must not exceed 60 characters.")
        else:
            cleaned["name"] = name_str

    # 2. Validate Roll Number
    roll_no = data.get("roll_no")
    if roll_no is None or str(roll_no).strip() == "":
        errors.append("Roll Number is required.")
    else:
        roll_str = str(roll_no).strip().upper()
        if len(roll_str) < 1 or len(roll_str) > 20:
            errors.append("Roll Number must be between 1 and 20 characters.")
        else:
            cleaned["roll_no"] = roll_str

    # 3. Validate Marks for 5 subjects
    cleaned_marks: Dict[str, float] = {}
    marks_input = data.get("marks", {})
    if not isinstance(marks_input, dict):
        errors.append("Marks must be provided as an object containing all 5 subjects.")
        return False, {}, errors

    for key in SUBJECT_KEYS:
        subj_display = SUBJECT_NAMES[key]
        val = marks_input.get(key)
        is_valid, parsed_mark, err = validate_mark(val)
        if not is_valid:
            errors.append(f"{subj_display} ({key}): {err}")
        else:
            cleaned_marks[key] = parsed_mark

    cleaned["marks"] = cleaned_marks

    is_valid = len(errors) == 0
    return is_valid, cleaned, errors


def calculate_total(marks: Union[Dict[str, float], List[float]]) -> float:
    """
    Calculates total marks scored across all 5 subjects.
    """
    if isinstance(marks, dict):
        values = list(marks.values())
    elif isinstance(marks, (list, tuple)):
        values = list(marks)
    else:
        raise ValueError("Marks must be a dictionary or list of numbers.")

    total = sum(float(m) for m in values)
    return round(total, 2)


def calculate_percentage(total: float, subject_count: int = TOTAL_SUBJECTS) -> float:
    """
    Calculates percentage based on total marks and subject count.
    Max per subject is 100.
    """
    if subject_count <= 0:
        raise ValueError("Subject count must be greater than zero.")
    max_score = subject_count * MAX_MARK
    pct = (total / max_score) * 100.0
    return round(pct, 2)


def calculate_status(marks: Union[Dict[str, float], List[float]], passing_threshold: float = PASSING_MARK) -> str:
    """
    Evaluates student pass/fail status.
    Rule: A student PASSES only if EVERY subject mark >= passing_threshold (35.0).
    If any single subject < passing_threshold, status is "Fail".
    """
    if isinstance(marks, dict):
        values = list(marks.values())
    elif isinstance(marks, (list, tuple)):
        values = list(marks)
    else:
        raise ValueError("Marks must be a dictionary or list of numbers.")

    for m in values:
        if float(m) < passing_threshold:
            return "Fail"
    return "Pass"


def calculate_grade(percentage: float, status: str) -> str:
    """
    Assigns academic grade based on percentage and pass/fail status.
    If student has failed in any subject, grade is strictly 'F'.
    """
    if status == "Fail":
        return "F"
    if percentage >= 90.0:
        return "A+"
    if percentage >= 80.0:
        return "A"
    if percentage >= 70.0:
        return "B+"
    if percentage >= 60.0:
        return "B"
    if percentage >= 50.0:
        return "C"
    if percentage >= PASSING_MARK:
        return "D"
    return "F"


def compute_student_result(name: str, roll_no: str, marks: Dict[str, float]) -> Dict[str, Any]:
    """
    Processes a verified student submission into a complete result record.
    """
    total = calculate_total(marks)
    percentage = calculate_percentage(total, len(marks))
    status = calculate_status(marks, PASSING_MARK)
    grade = calculate_grade(percentage, status)

    return {
        "roll_no": roll_no,
        "name": name,
        "marks": marks,
        "total": total,
        "max_total": len(marks) * MAX_MARK,
        "percentage": percentage,
        "status": status,
        "grade": grade,
    }
