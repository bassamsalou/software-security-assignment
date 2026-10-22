from flask import Flask, jsonify, request
import secrets
import requests

app = Flask(__name__)

RESOURCE_SERVICE_URL = "http://127.0.0.1:5001"
PROCESSING_SERVICE_URL = "http://127.0.0.1:5002"

# Seeded synthetic users
USERS = {
    "john": {
        "password": "john123",
        "role": "user"
    },
    "doe": {
        "password": "doe123",
        "role": "user"
    },
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}

# In-memory session for the assignment
SESSIONS = {}

def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1]
    return SESSIONS.get(token)


@app.get("/health")
def health():
    return jsonify({
        "service": "api-service",
        "status": "ok"
    })


@app.post("/login")
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
            }), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
            }), 400

    user = USERS.get(username.lower())

    if user is None or user["password"] != password:
        return jsonify({
            "error": "Invalid credentials"
            }), 401

    username = username.lower()

    token = secrets.token_urlsafe(32)

    SESSIONS[token] = {
        "username": username,
        "role": user["role"]
    }

    return jsonify({
        "message": "Login successful",
        "token": token,
        "username": username,
        "role": user["role"]
    })


@app.get("/me")
def me():
    user = get_current_user()


    if user is None:
        return jsonify({
            "error": "Authentication required"
            }), 401

    return jsonify(user)


@app.get("/bookings")
def get_my_bookings():
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
            }), 401

    try:
        response = requests.get(
            f"{RESOURCE_SERVICE_URL}/bookings",
            timeout=5
            )
        response.raise_for_status()

    except requests.RequestException:
        return jsonify({
            "error": "Resource service is unavailable"
            }), 503

    bookings = response.json()

    if user["role"] == "admin":
        visible_bookings = bookings
    else:
        visible_bookings = [
            booking 
            for booking in bookings 
            if booking["owner"] == user["username"]
        ]

    return jsonify(visible_bookings)


@app.get("/bookings/<int:booking_id>")
def get_booking(booking_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    try:
        response = requests.get(
            f"{RESOURCE_SERVICE_URL}/bookings/{booking_id}",
            headers={
                "X-User": user["username"],
                "X-Role": user["role"]
            },
            timeout=5
        )

    except requests.RequestException:
        return jsonify({
            "error": "Resource service is unavailable"
        }), 503

    return jsonify(response.json()), response.status_code


@app.patch("/bookings/<int:booking_id>/status")
def update_booking_status(booking_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    if user["role"] != "admin":
        return jsonify({
            "error": "Administrator access required"
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400

    try:
        response = requests.patch(
            f"{RESOURCE_SERVICE_URL}/bookings/{booking_id}/status",
            headers={
                "X-User": user["username"],
                "X-Role": user["role"]
            },
            json=data,
            timeout=5
        )

    except requests.RequestException:
        return jsonify({
            "error": "Resource service is unavailable"
        }), 503

    return jsonify(response.json()), response.status_code


@app.post("/bookings/<int:booking_id>/summary")
def create_booking_summary(booking_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    try:
        response = requests.post(
            f"{PROCESSING_SERVICE_URL}/process-summary",
            json={
                "booking_id": booking_id,
                "username": user["username"],
                "role": user["role"]
            },
            timeout=5
        )

    except requests.RequestException:
        return jsonify({
            "error": "Processing service is unavailable"
        }), 503

    return jsonify(response.json()), response.status_code



@app.get("/summaries/<int:summary_id>")
def get_summary(summary_id):
    user = get_current_user()

    if user is None:
        return jsonify({
            "error": "Authentication required"
        }), 401

    try:
        response = requests.get(
            f"{RESOURCE_SERVICE_URL}/summaries/{summary_id}",
            headers={
                "X-User": user["username"],
                "X-Role": user["role"]
            },
            timeout=5
        )

    except requests.RequestException:
        return jsonify({
            "error": "Resource service is unavailable"
        }), 503

    return jsonify(response.json()), response.status_code



if __name__ == "__main__":
    app.run(
        host="127.0.0.1", 
        port=5000,
        debug=False
        )