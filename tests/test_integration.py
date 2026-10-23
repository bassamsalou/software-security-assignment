import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests


ROOT = Path(__file__).resolve().parents[1]
API_URL = "http://127.0.0.1:5000"


def wait_for_service(url, timeout=10):
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass

        time.sleep(0.5)

    raise RuntimeError(f"Service did not start: {url}")


@pytest.fixture(scope="session", autouse=True)
def start_services():
    processes = []

    try:
        resource_process = subprocess.Popen(
            [sys.executable, str(ROOT / "resource-service" / "app.py")],
            cwd=str(ROOT)
        )
        processes.append(resource_process)

        wait_for_service("http://127.0.0.1:5001/health")

        processing_process = subprocess.Popen(
            [sys.executable, str(ROOT / "processing-service" / "app.py")],
            cwd=str(ROOT)
        )
        processes.append(processing_process)

        wait_for_service("http://127.0.0.1:5002/health")

        api_process = subprocess.Popen(
            [sys.executable, str(ROOT / "api-service" / "app.py")],
            cwd=str(ROOT)
        )
        processes.append(api_process)

        wait_for_service("http://127.0.0.1:5000/health")

        yield

    finally:
        for process in reversed(processes):
            process.terminate()

        for process in reversed(processes):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def login(username, password):
    response = requests.post(
        f"{API_URL}/login",
        json={
            "username": username,
            "password": password
        },
        timeout=5
    )

    assert response.status_code == 200

    return response.json()["token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_john_can_access_own_booking():
    token = login("john", "john123")

    response = requests.get(
        f"{API_URL}/bookings/1",
        headers=auth_headers(token),
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["owner"] == "john"


def test_john_cannot_access_doe_booking():
    token = login("john", "john123")

    response = requests.get(
        f"{API_URL}/bookings/3",
        headers=auth_headers(token),
        timeout=5
    )

    assert response.status_code == 403


def test_admin_can_access_doe_booking():
    token = login("admin", "admin123")

    response = requests.get(
        f"{API_URL}/bookings/3",
        headers=auth_headers(token),
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["owner"] == "doe"


def test_user_cannot_manage_booking():
    token = login("john", "john123")

    response = requests.patch(
        f"{API_URL}/bookings/1/status",
        headers=auth_headers(token),
        json={
            "status": "confirmed"
        },
        timeout=5
    )

    assert response.status_code == 403


def test_admin_can_manage_booking():
    token = login("admin", "admin123")

    response = requests.patch(
        f"{API_URL}/bookings/1/status",
        headers=auth_headers(token),
        json={
            "status": "confirmed"
        },
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["booking"]["status"] == "confirmed"


def test_john_can_generate_and_retrieve_summary():
    token = login("john", "john123")

    response = requests.post(
        f"{API_URL}/bookings/1/summary",
        headers=auth_headers(token),
        timeout=5
    )

    assert response.status_code == 201

    data = response.json()

    assert data["owner"] == "john"
    assert "summary_id" in data

    summary_id = data["summary_id"]

    response = requests.get(
        f"{API_URL}/summaries/{summary_id}",
        headers=auth_headers(token),
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["owner"] == "john"


def test_john_cannot_generate_doe_summary():
    token = login("john", "john123")

    response = requests.post(
        f"{API_URL}/bookings/3/summary",
        headers=auth_headers(token),
        timeout=5
    )

    assert response.status_code == 403


def test_doe_cannot_read_john_summary():
    john_token = login("john", "john123")

    create_response = requests.post(
        f"{API_URL}/bookings/1/summary",
        headers=auth_headers(john_token),
        timeout=5
    )

    assert create_response.status_code == 201

    summary_id = create_response.json()["summary_id"]

    doe_token = login("doe", "doe123")

    response = requests.get(
        f"{API_URL}/summaries/{summary_id}",
        headers=auth_headers(doe_token),
        timeout=5
    )

    assert response.status_code == 403