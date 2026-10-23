from flask import Flask, jsonify, request
from database import get_connection, init_db

app = Flask(__name__)
init_db()

@app.get("/health")
def health():
    return jsonify({
        "service": "resource-service",
        "status": "ok"
    })

@app.get("/bookings")
def get_bookings():
    username = request.headers.get("X-Username")
    role = request.headers.get("X-Role")

    if not username or not role:
        return jsonify({
            "error": "Authorization information required"
        }), 401

    connection = get_connection()

    if role == "admin":
        bookings = connection.execute(
            "SELECT * FROM bookings"
        ).fetchall()

    elif role == "user":
        bookings = connection.execute(
            "SELECT * FROM bookings WHERE owner = ?",
            (username,)
        ).fetchall()

    else:
        connection.close()

        return jsonify({
            "error": "Access denied"
        }), 403

    connection.close()

    return jsonify([dict(booking) for booking in bookings])


@app.get("/bookings/search")
def search_bookings():
    username = request.headers.get("X-Username")
    role = request.headers.get("X-Role")

    if not username or not role:
        return jsonify({
            "error": "Authorization information required"
        }), 401

    destination = request.args.get("destination")

    if not destination:
        return jsonify({
            "error": "Destination is required"
        }), 400

    connection = get_connection()

    if role == "admin":
        bookings = connection.execute(
            "SELECT * FROM bookings WHERE destination = ?",
            (destination,)
        ).fetchall()

    elif role == "user":
        bookings = connection.execute(
            """
            SELECT * FROM bookings
            WHERE owner = ? AND destination = ?
            """,
            (username, destination)
        ).fetchall()

    else:
        connection.close()

        return jsonify({
            "error": "Access denied"
        }), 403

    connection.close()

    return jsonify([dict(booking) for booking in bookings])


@app.get("/bookings/<int:booking_id>")
def get_booking(booking_id):
    username = request.headers.get("X-Username")
    role = request.headers.get("X-Role")

    if not username or not role:
        return jsonify({
            "error": "Authorization information required"
        }), 401

    connection = get_connection()

    booking = connection.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    ).fetchone()

    connection.close()

    if booking is None:
        return jsonify({
            "error": "Booking not found"
        }), 404

    # Administrator may access any booking.
    if role == "admin":
        return jsonify(dict(booking))

    # Ordinary users may only access their own booking.
    if role == "user" and booking["owner"] == username:
        return jsonify(dict(booking))

    return jsonify({
        "error": "Access denied"
    }), 403


@app.patch("/bookings/<int:booking_id>/status")
def update_booking_status(booking_id):
    username = request.headers.get("X-Username")
    role = request.headers.get("X-Role")

    if not username or not role:
        return jsonify({
            "error": "Authorization information required"
        }), 401

    # Only administrators may manage bookings.
    if role != "admin":
        return jsonify({
            "error": "Administrator access required"
        }), 403

    data = request.get_json(silent=True)

    if not data or "status" not in data:
        return jsonify({
            "error": "Status is required"
        }), 400

    new_status = data["status"]

    allowed_statuses = [
        "pending",
        "confirmed",
        "cancelled"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid booking status"
        }), 400

    connection = get_connection()

    booking = connection.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    ).fetchone()

    if booking is None:
        connection.close()

        return jsonify({
            "error": "Booking not found"
        }), 404

    connection.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        (new_status, booking_id)
    )

    connection.commit()

    updated_booking = connection.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    ).fetchone()

    connection.close()

    return jsonify({
        "message": "Booking status updated",
        "booking": dict(updated_booking)
    })


@app.post("/summaries")
def store_summary():
    username = request.headers.get("X-Username")
    role = request.headers.get("X-Role")

    if not username or not role:
        return jsonify({
            "error": "Authorization information required"
        }), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400

    booking_id = data.get("booking_id")
    owner = data.get("owner")
    summary = data.get("summary")

    if booking_id is None or not owner or not summary:
        return jsonify({
            "error": "booking_id, owner and summary are required"
        }), 400

    # VULNERABILITY:
    # The Resource Service trusts the authorization context supplied
    # by the Processing Service instead of re-checking the current
    # ownership of the booking.
    #
    # If ownership changes after Processing originally accessed the
    # booking, this stale authorization decision may still be accepted.
    if role == "user" and owner != username:
        return jsonify({
            "error": "Access denied"
        }), 403

    if role not in ["user", "admin"]:
        return jsonify({
            "error": "Access denied"
        }), 403

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO summaries (booking_id, owner, summary)
        VALUES (?, ?, ?)
        """,
        (booking_id, owner, summary)
    )

    connection.commit()

    summary_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Summary stored",
        "summary_id": summary_id
    }), 201



@app.get("/summaries/<int:summary_id>")
def get_summary(summary_id):
    username = request.headers.get("X-Username")
    role = request.headers.get("X-Role")

    if not username or not role:
        return jsonify({
            "error": "Authorization information required"
        }), 401

    connection = get_connection()

    summary = connection.execute(
        "SELECT * FROM summaries WHERE id = ?",
        (summary_id,)
    ).fetchone()

    connection.close()

    if summary is None:
        return jsonify({
            "error": "Summary not found"
        }), 404

    if role == "admin":
        return jsonify(dict(summary))

    if role == "user" and summary["owner"] == username:
        return jsonify(dict(summary))

    return jsonify({
        "error": "Access denied"
    }), 403



if __name__ == "__main__":
    app.run(
        host="127.0.0.1", 
        port=5001, 
        debug=False
        )