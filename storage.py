"""
Student Result Verification System - Storage Layer
Lightweight, zero-database JSON file storage.
Stores student records reliably and persists across server restarts.
"""

import json
import os
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "results.json")

SAMPLE_STUDENTS = [
    {
        "roll_no": "IT2026-001",
        "name": "Aarav Sharma",
        "marks": {"sub1": 88.0, "sub2": 92.0, "sub3": 85.0, "sub4": 90.0, "sub5": 95.0},
        "total": 450.0,
        "max_total": 500.0,
        "percentage": 90.0,
        "status": "Pass",
        "grade": "A+",
        "timestamp": "2026-10-25 09:30:00"
    },
    {
        "roll_no": "IT2026-002",
        "name": "Priya Patel",
        "marks": {"sub1": 65.0, "sub2": 72.0, "sub3": 58.0, "sub4": 64.0, "sub5": 70.0},
        "total": 329.0,
        "max_total": 500.0,
        "percentage": 65.8,
        "status": "Pass",
        "grade": "B",
        "timestamp": "2026-10-25 10:15:00"
    },
    {
        "roll_no": "IT2026-003",
        "name": "Rohan Deshmukh",
        "marks": {"sub1": 78.0, "sub2": 82.0, "sub3": 32.0, "sub4": 75.0, "sub5": 80.0},
        "total": 347.0,
        "max_total": 500.0,
        "percentage": 69.4,
        "status": "Fail",
        "grade": "F",
        "timestamp": "2026-10-25 11:00:00"
    },
    {
        "roll_no": "IT2026-004",
        "name": "Sneha Kulkarni",
        "marks": {"sub1": 35.0, "sub2": 35.0, "sub3": 35.0, "sub4": 35.0, "sub5": 35.0},
        "total": 175.0,
        "max_total": 500.0,
        "percentage": 35.0,
        "status": "Pass",
        "grade": "D",
        "timestamp": "2026-10-25 11:45:00"
    }
]


def ensure_data_file() -> None:
    """Ensures data directory and initial JSON file exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(SAMPLE_STUDENTS, f, indent=2)


def get_all_results() -> List[Dict[str, Any]]:
    """Loads all student results from file."""
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def get_result_by_roll_no(roll_no: str) -> Optional[Dict[str, Any]]:
    """Finds a student result by roll number (case-insensitive)."""
    results = get_all_results()
    roll_normalized = str(roll_no).strip().upper()
    for item in results:
        if str(item.get("roll_no")).strip().upper() == roll_normalized:
            return item
    return None


def save_result(student_record: Dict[str, Any]) -> Tuple_Result:
    """
    Saves or updates a student result in the JSON storage.
    If roll_no already exists, updates the record. Otherwise, appends.
    """
    ensure_data_file()
    results = get_all_results()
    roll_normalized = str(student_record["roll_no"]).strip().upper()

    existing_index = -1
    for idx, item in enumerate(results):
        if str(item.get("roll_no")).strip().upper() == roll_normalized:
            existing_index = idx
            break

    if existing_index >= 0:
        results[existing_index] = student_record
        action = "updated"
    else:
        results.append(student_record)
        action = "added"

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return action, student_record


# Type helper
Tuple_Result = tuple


def delete_result(roll_no: str) -> bool:
    """Deletes a student record by roll number."""
    ensure_data_file()
    results = get_all_results()
    roll_normalized = str(roll_no).strip().upper()

    new_results = [r for r in results if str(r.get("roll_no")).strip().upper() != roll_normalized]
    if len(new_results) < len(results):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(new_results, f, indent=2)
        return True
    return False


def reset_sample_data() -> None:
    """Resets dataset to default initial sample students."""
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_STUDENTS, f, indent=2)


def get_summary_statistics() -> Dict[str, Any]:
    """
    Computes real-time statistics across all stored student results.
    """
    results = get_all_results()
    total_students = len(results)

    if total_students == 0:
        return {
            "total_students": 0,
            "passed_count": 0,
            "failed_count": 0,
            "pass_percentage": 0.0,
            "class_average": 0.0,
            "highest_score": None,
            "lowest_score": None,
        }

    passed_count = sum(1 for r in results if r.get("status") == "Pass")
    failed_count = total_students - passed_count
    pass_pct = round((passed_count / total_students) * 100.0, 1)

    all_percentages = [r.get("percentage", 0.0) for r in results]
    class_average = round(sum(all_percentages) / total_students, 1)

    # Topper
    highest_record = max(results, key=lambda r: r.get("percentage", 0.0))
    lowest_record = min(results, key=lambda r: r.get("percentage", 0.0))

    return {
        "total_students": total_students,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "pass_percentage": pass_pct,
        "class_average": class_average,
        "highest_score": {
            "name": highest_record.get("name"),
            "roll_no": highest_record.get("roll_no"),
            "percentage": highest_record.get("percentage"),
            "total": highest_record.get("total"),
        },
        "lowest_score": {
            "name": lowest_record.get("name"),
            "roll_no": lowest_record.get("roll_no"),
            "percentage": lowest_record.get("percentage"),
        },
    }
