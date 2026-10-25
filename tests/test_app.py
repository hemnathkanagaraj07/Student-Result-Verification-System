"""
Integration and API Tests for Flask Student Result Verification System.
Tested using Flask test client.
"""

import json
import pytest
from app import app
import storage


@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Reset storage to known state before each test
    storage.reset_sample_data()
    with app.test_client() as client:
        yield client
    # Clean up / reset after test
    storage.reset_sample_data()


def test_home_page_status_and_content(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Student Result Verification" in html
    assert "Roll Number" in html
    assert "Software Engineering" in html


def test_testing_dashboard_page(client):
    response = client.get("/testing")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Software Testing Dashboard" in html
    assert "Boundary Value Analysis" in html


def test_api_get_results(client):
    response = client.get("/api/results")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_api_submit_valid_student(client):
    payload = {
        "name": "Kavita Rao",
        "roll_no": "TEST-2026-99",
        "marks": {
            "sub1": 85.0,
            "sub2": 90.0,
            "sub3": 78.0,
            "sub4": 82.0,
            "sub5": 88.0
        }
    }
    response = client.post(
        "/api/results",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code in (200, 201)
    data = json.loads(response.data)
    assert data["success"] is True
    record = data["data"]
    assert record["name"] == "Kavita Rao"
    assert record["roll_no"] == "TEST-2026-99"
    assert record["total"] == 423.0
    assert record["percentage"] == 84.6
    assert record["status"] == "Pass"
    assert record["grade"] == "A"


def test_api_submit_failing_student_single_subject(client):
    payload = {
        "name": "Manish Verma",
        "roll_no": "TEST-FAIL-01",
        "marks": {
            "sub1": 95.0,
            "sub2": 90.0,
            "sub3": 34.0,  # Below 35
            "sub4": 92.0,
            "sub5": 89.0
        }
    }
    response = client.post(
        "/api/results",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code in (200, 201)
    data = json.loads(response.data)
    record = data["data"]
    assert record["status"] == "Fail"
    assert record["grade"] == "F"


def test_api_submit_invalid_mark_out_of_bounds(client):
    payload = {
        "name": "Rahul Test",
        "roll_no": "TEST-ERR-01",
        "marks": {
            "sub1": 105.0,  # Exceeds 100
            "sub2": 80.0,
            "sub3": 70.0,
            "sub4": 60.0,
            "sub5": 50.0
        }
    }
    response = client.post(
        "/api/results",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert any("exceeds maximum" in err.lower() for err in data["errors"])


def test_api_submit_missing_name_and_roll(client):
    payload = {
        "name": "",
        "roll_no": "",
        "marks": {"sub1": 50, "sub2": 50, "sub3": 50, "sub4": 50, "sub5": 50}
    }
    response = client.post(
        "/api/results",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert any("Name is required" in err for err in data["errors"])
    assert any("Roll Number is required" in err for err in data["errors"])


def test_api_delete_student(client):
    # Sample has IT2026-001
    response = client.delete("/api/results/IT2026-001")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

    # Confirm deletion
    get_res = client.get("/api/results/IT2026-001")
    assert get_res.status_code == 404


def test_api_stats(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    stats = data["stats"]
    assert "total_students" in stats
    assert "passed_count" in stats
    assert "failed_count" in stats
    assert "class_average" in stats
