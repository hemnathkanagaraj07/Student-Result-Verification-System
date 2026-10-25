"""
Student Result Verification System - Flask Web Application
Developed for BSc IT Software Testing Laboratory.
"""

from datetime import datetime
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

from calculator import (
    SUBJECT_KEYS,
    SUBJECT_NAMES,
    PASSING_MARK,
    MAX_MARK,
    validate_student_input,
    compute_student_result,
)
import storage

app = Flask(__name__)
app.secret_key = "bsc-it-software-testing-lab-secret-key-2026"


@app.context_processor
def inject_common():
    return {
        "subject_keys": SUBJECT_KEYS,
        "subject_names": SUBJECT_NAMES,
        "passing_mark": PASSING_MARK,
        "max_mark": MAX_MARK,
    }


# ==========================================
# PAGE ROUTES
# ==========================================

@app.route("/")
def index():
    """Main student result dashboard."""
    results = storage.get_all_results()
    stats = storage.get_summary_statistics()
    return render_template(
        "index.html",
        results=results,
        stats=stats,
        page_title="Student Result Dashboard"
    )


@app.route("/testing")
def testing_dashboard():
    """Software Testing Laboratory Dashboard."""
    return render_template(
        "testing.html",
        page_title="Software Testing Dashboard"
    )


# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route("/api/results", methods=["GET"])
def api_get_results():
    """Retrieve all student results."""
    results = storage.get_all_results()
    return jsonify({
        "success": True,
        "count": len(results),
        "data": results,
    })


@app.route("/api/results/<roll_no>", methods=["GET"])
def api_get_result_by_roll(roll_no):
    """Retrieve single student result by roll number."""
    record = storage.get_result_by_roll_no(roll_no)
    if record:
        return jsonify({"success": True, "data": record})
    return jsonify({"success": False, "message": f"Roll number '{roll_no}' not found."}), 404


@app.route("/api/results", methods=["POST"])
def api_add_result():
    """
    Validates and stores a new student result.
    Supports both JSON payloads and traditional form submissions.
    """
    if request.is_json:
        payload = request.get_json()
    else:
        # Parse standard form post
        name = request.form.get("name", "")
        roll_no = request.form.get("roll_no", "")
        marks_dict = {}
        for k in SUBJECT_KEYS:
            marks_dict[k] = request.form.get(k)
        payload = {
            "name": name,
            "roll_no": roll_no,
            "marks": marks_dict
        }

    is_valid, cleaned, errors = validate_student_input(payload)
    if not is_valid:
        if request.is_json:
            return jsonify({
                "success": False,
                "message": "Validation failed.",
                "errors": errors
            }), 400
        else:
            for err in errors:
                flash(err, "error")
            return redirect(url_for("index"))

    # Compute total, percentage, pass/fail status and grade
    result_record = compute_student_result(
        name=cleaned["name"],
        roll_no=cleaned["roll_no"],
        marks=cleaned["marks"]
    )
    result_record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    action, saved_record = storage.save_result(result_record)

    msg = f"Result for student {saved_record['name']} ({saved_record['roll_no']}) successfully {action}!"

    if request.is_json:
        return jsonify({
            "success": True,
            "message": msg,
            "action": action,
            "data": saved_record,
            "stats": storage.get_summary_statistics()
        }), 201 if action == "added" else 200
    else:
        flash(msg, "success")
        return redirect(url_for("index"))


@app.route("/api/results/<roll_no>", methods=["DELETE"])
def api_delete_result(roll_no):
    """Deletes a student result by roll number."""
    success = storage.delete_result(roll_no)
    if success:
        return jsonify({
            "success": True,
            "message": f"Student record with roll number '{roll_no}' deleted.",
            "stats": storage.get_summary_statistics()
        })
    return jsonify({"success": False, "message": f"Record with roll number '{roll_no}' not found."}), 404


@app.route("/api/results/reset", methods=["POST"])
def api_reset_sample():
    """Resets dataset to default initial student samples."""
    storage.reset_sample_data()
    return jsonify({
        "success": True,
        "message": "Student records reset to default sample dataset.",
        "stats": storage.get_summary_statistics(),
        "data": storage.get_all_results()
    })


@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    """Returns real-time summary statistics."""
    stats = storage.get_summary_statistics()
    return jsonify({"success": True, "stats": stats})


def parse_pytest_execution(stdout: str, stderr: str, xml_path: str, returncode: int, elapsed_seconds: float) -> dict:
    """
    Accurately parses pytest execution results from JUnit XML and terminal output.
    Does NOT fabricate results. Extracts exact total, passed, failed, skipped, and durations.
    """
    tests = []
    total = 0
    passed_count = 0
    failed_count = 0
    skipped_count = 0
    error_count = 0
    summary_text = ""
    xml_parsed = False

    # 1. Primary: Parse structured JUnit XML if available
    if os.path.exists(xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            suite = root.find("testsuite") if root.tag == "testsuites" else root
            if suite is not None:
                for idx, tc in enumerate(suite.findall("testcase")):
                    name = tc.attrib.get("name", "unknown_test")
                    classname = tc.attrib.get("classname", "")
                    tc_time = float(tc.attrib.get("time", 0.0))

                    # Determine status
                    failure_node = tc.find("failure")
                    error_node = tc.find("error")
                    skipped_node = tc.find("skipped")

                    message = ""
                    if failure_node is not None:
                        status = "FAILED"
                        message = failure_node.text or failure_node.attrib.get("message", "")
                        failed_count += 1
                    elif error_node is not None:
                        status = "ERROR"
                        message = error_node.text or error_node.attrib.get("message", "")
                        error_count += 1
                    elif skipped_node is not None:
                        status = "SKIPPED"
                        message = skipped_node.text or skipped_node.attrib.get("message", "")
                        skipped_count += 1
                    else:
                        status = "PASSED"
                        passed_count += 1

                    # File and class formatting
                    parts = classname.split(".")
                    file_name = parts[1] + ".py" if len(parts) > 1 else classname
                    class_name = parts[2] if len(parts) > 2 else ""

                    tests.append({
                        "id": idx + 1,
                        "file": file_name,
                        "class_name": class_name,
                        "name": name,
                        "status": status,
                        "duration": round(tc_time, 3),
                        "message": message.strip()
                    })

                total = len(tests)
                xml_parsed = True
        except Exception as xml_err:
            print(f"Notice: XML parsing error: {xml_err}")

    # 2. Extract summary line from terminal stdout
    full_output = stdout + "\n" + stderr
    for line in full_output.splitlines():
        line_str = line.strip()
        if ("passed in" in line_str or "failed in" in line_str or "error in" in line_str) and "==" in line_str:
            summary_text = line_str.strip("= ")
            break

    # 3. Fallback to stdout line-by-line parsing if XML was not available
    if not xml_parsed or len(tests) == 0:
        test_pattern = re.compile(r'^(tests[\\/][^:]+)::(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\b', re.IGNORECASE)
        test_id = 1
        tests = []
        passed_count = 0
        failed_count = 0
        skipped_count = 0
        error_count = 0

        for line in full_output.splitlines():
            line_str = line.strip()
            m = test_pattern.search(line_str)
            if m:
                file_path = m.group(1).replace("\\", "/")
                test_spec = m.group(2).strip()
                status = m.group(3).upper()

                if "::" in test_spec:
                    class_name, test_name = test_spec.rsplit("::", 1)
                else:
                    class_name = ""
                    test_name = test_spec

                if status == "PASSED":
                    passed_count += 1
                elif status == "FAILED":
                    failed_count += 1
                elif status in ("ERROR", "XPASS"):
                    error_count += 1
                elif status in ("SKIPPED", "XFAIL"):
                    skipped_count += 1

                tests.append({
                    "id": test_id,
                    "file": file_path.split("/")[-1],
                    "class_name": class_name,
                    "name": test_name,
                    "status": status,
                    "duration": 0.0,
                    "message": ""
                })
                test_id += 1

        total = len(tests)

    # 4. Parse execution time from summary text if available
    time_match = re.search(r'in\s+([\d\.]+)\s*s', summary_text)
    if time_match:
        reported_time = float(time_match.group(1))
    else:
        reported_time = round(elapsed_seconds, 2)

    all_passed = (returncode == 0 and failed_count == 0 and error_count == 0)

    result_payload = {
        "success": True,
        "returncode": returncode,
        "passed": all_passed,
        "summary": summary_text or f"{passed_count} passed in {reported_time}s",
        "total": total,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "elapsed_seconds": reported_time,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests": tests,
        "raw_output": full_output
    }

    # Cache latest test results
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "latest_test_results.json")
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result_payload, f, indent=2)
    except Exception as save_err:
        print(f"Notice: Failed to cache test results: {save_err}")

    return result_payload


@app.route("/api/test-results", methods=["GET"])
def api_get_test_results():
    """
    Returns the latest actual pytest execution results.
    Loads from cache or parses XML report if available.
    """
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "latest_test_results.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return jsonify({"success": True, "has_results": True, "data": data})
        except Exception:
            pass

    # If cache not found, check XML
    xml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_results.xml")
    if os.path.exists(xml_path):
        parsed = parse_pytest_execution("", "", xml_path, 0, 0.0)
        return jsonify({"success": True, "has_results": True, "data": parsed})

    return jsonify({"success": True, "has_results": False})


@app.route("/api/run-tests", methods=["POST"])
def api_run_tests():
    """
    Executes real automated pytest unit tests on the server and returns genuine test results.
    Does NOT fabricate results.
    Runs complete test suite (including Selenium) by default.
    """
    req_data = request.get_json(silent=True) or {}
    suite = req_data.get("suite", "all").lower()

    # Determine test targets based on requested suite
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(base_dir, "data", "test_results.xml")
    os.makedirs(os.path.dirname(xml_path), exist_ok=True)

    if suite == "unit":
        # Fast unit & integration tests only (68 tests)
        targets = ["tests/test_calculator.py", "tests/test_app.py"]
    elif suite == "selenium":
        # Selenium end-to-end browser test only (1 test)
        targets = ["tests/test_selenium.py"]
    else:
        # Complete suite (All 69 tests including Selenium)
        targets = ["tests/test_calculator.py", "tests/test_app.py", "tests/test_selenium.py"]

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--tb=short",
        f"--junitxml={xml_path}"
    ] + targets

    try:
        start_time = datetime.now()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=base_dir,
            timeout=300  # 5 minutes for full browser automation
        )
        elapsed_seconds = (datetime.now() - start_time).total_seconds()

        payload = parse_pytest_execution(
            stdout=result.stdout,
            stderr=result.stderr,
            xml_path=xml_path,
            returncode=result.returncode,
            elapsed_seconds=elapsed_seconds
        )
        payload["suite"] = suite

        return jsonify(payload)

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "message": "Test execution timed out after 300 seconds."
        }), 504
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Test execution error: {str(e)}"
        }), 500


if __name__ == "__main__":
    storage.ensure_data_file()
    print("=" * 60)
    print(" Student Result Verification System (Flask)")
    print(" Software Testing Laboratory Project")
    print(" Server running on: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
