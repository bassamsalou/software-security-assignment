import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCE_SERVICE_PATH = PROJECT_ROOT / "resource-service"
RESOURCE_APP_PATH = RESOURCE_SERVICE_PATH / "app.py"

# Required because resource-service/app.py imports database.py
sys.path.insert(0, str(RESOURCE_SERVICE_PATH))

# Load resource-service/app.py with a unique module name.
# This prevents it from colliding with api-service/app.py during pytest.
spec = importlib.util.spec_from_file_location(
    "resource_service_app",
    RESOURCE_APP_PATH
)

resource_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resource_app)


def test_health():
    client = resource_app.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_booking_requires_authorization_information():
    client = resource_app.app.test_client()

    response = client.get("/bookings/1")

    assert response.status_code == 401


def test_john_can_access_own_booking():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/1",
        headers={
            "X-Username": "john",
            "X-Role": "user"
        }
    )

    assert response.status_code == 200

    booking = response.get_json()

    assert booking["id"] == 1
    assert booking["owner"] == "john"


def test_john_cannot_access_doe_booking():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/3",
        headers={
            "X-Username": "john",
            "X-Role": "user"
        }
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Access denied"


def test_doe_cannot_access_john_booking():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/1",
        headers={
            "X-Username": "doe",
            "X-Role": "user"
        }
    )

    assert response.status_code == 403


def test_admin_can_access_john_booking():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/1",
        headers={
            "X-Username": "admin",
            "X-Role": "admin"
        }
    )

    assert response.status_code == 200


def test_admin_can_access_doe_booking():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/3",
        headers={
            "X-Username": "admin",
            "X-Role": "admin"
        }
    )

    assert response.status_code == 200


def test_user_cannot_manage_booking():
    client = resource_app.app.test_client()

    response = client.patch(
        "/bookings/1/status",
        headers={
            "X-Username": "john",
            "X-Role": "user"
        },
        json={
            "status": "confirmed"
        }
    )

    assert response.status_code == 403


def test_admin_can_manage_booking():
    client = resource_app.app.test_client()

    response = client.patch(
        "/bookings/1/status",
        headers={
            "X-Username": "admin",
            "X-Role": "admin"
        },
        json={
            "status": "confirmed"
        }
    )

    assert response.status_code == 200

    booking = response.get_json()["booking"]

    assert booking["status"] == "confirmed"


def test_cwe20_invalid_booking_status_is_rejected():
    client = resource_app.app.test_client()

    response = client.patch(
        "/bookings/1/status",
        headers={
            "X-Username": "admin",
            "X-Role": "admin"
        },
        json={
            "status": "totally-invalid-status"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid booking status"


def test_cwe862_bookings_require_authorization():
    client = resource_app.app.test_client()

    response = client.get("/bookings")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authorization information required"


def test_cwe89_sql_injection_is_blocked():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/search",
        query_string={
            "destination": "' OR 1=1 --"
        },
        headers={
            "X-Username": "john",
            "X-Role": "user"
        }
    )

    assert response.status_code == 200

    bookings = response.get_json()

    assert bookings == []


def test_booking_search_works_with_normal_destination():
    client = resource_app.app.test_client()

    response = client.get(
        "/bookings/search",
        query_string={
            "destination": "Copenhagen"
        },
        headers={
            "X-Username": "john",
            "X-Role": "user"
        }
    )

    assert response.status_code == 200

    bookings = response.get_json()

    assert len(bookings) == 1
    assert bookings[0]["owner"] == "john"
    assert bookings[0]["destination"] == "Copenhagen"