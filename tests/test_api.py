import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_APP_PATH = PROJECT_ROOT / "api-service" / "app.py"

spec = importlib.util.spec_from_file_location(
    "api_service_app",
    API_APP_PATH
)

api_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_app)


def setup_function():
    api_app.SESSIONS.clear()


def test_health():
    client = api_app.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_valid_john_login():
    client = api_app.app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "john",
            "password": "john123"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["username"] == "john"
    assert data["role"] == "user"
    assert "token" in data


def test_invalid_password_is_rejected():
    client = api_app.app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "john",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid credentials"


def test_unknown_user_is_rejected():
    client = api_app.app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "unknown",
            "password": "password"
        }
    )

    assert response.status_code == 401


def test_missing_credentials_are_rejected():
    client = api_app.app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "john"
        }
    )

    assert response.status_code == 400


def test_bookings_require_authentication():
    client = api_app.app.test_client()

    response = client.get("/bookings")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


def test_summary_requires_authentication():
    client = api_app.app.test_client()

    response = client.post("/bookings/1/summary")

    assert response.status_code == 401