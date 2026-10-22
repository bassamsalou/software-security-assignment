from flask import Flask, jsonify, request
import requests

from booking_helper import generate_booking_summary

app = Flask(__name__)

RESOURCE_SERVICE_URL = "http://127.0.0.1:5001"


@app.get("/health")
def health():
    return jsonify({
        "service": "processing-service",
        "status": "ok"
    })


@app.post("/process-summary")
def process_summary():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400

    booking_id = data.get("booking_id")
    username = data.get("username")
    role = data.get("role")

    if booking_id is None or not username or not role:
        return jsonify({
            "error": "booking_id, username and role are required"
        }), 400

    try:
        response = requests.get(
            f"{RESOURCE_SERVICE_URL}/bookings/{booking_id}",
            headers={
                "X-User": username,
                "X-Role": role
            },
            timeout=5
        )

    except requests.RequestException:
        return jsonify({
            "error": "Resource service is unavailable"
        }), 503

    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    booking = response.json()

    summary = generate_booking_summary(booking)

    try:
        store_response = requests.post(
            f"{RESOURCE_SERVICE_URL}/summaries",
            headers={
                "X-User": username,
                "X-Role": role
            },
            json={
                "booking_id": booking_id,
                "owner": booking["owner"],
                "summary": summary
            },
            timeout=5
        )

    except requests.RequestException:
        return jsonify({
            "error": "Resource service is unavailable"
        }), 503

    if store_response.status_code != 201:
        return jsonify(
            store_response.json()
        ), store_response.status_code

    stored_summary = store_response.json()

    return jsonify({
        "booking_id": booking_id,
        "owner": booking["owner"],
        "summary_id": stored_summary["summary_id"],
        "summary": summary
    }), 201


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5002,
        debug=False
    )