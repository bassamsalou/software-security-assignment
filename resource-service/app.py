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
    connection = get_connection()

    bookings = connection.execute(
        "SELECT * FROM bookings"
        ).fetchall()
    
    connection.close()

    return jsonify([dict(booking) for booking in bookings])

@app.get("/bookings/<int:booking_id>")
def get_booking(booking_id):
    username = request.headers.get("X-User")
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

if __name__ == "__main__":
    app.run(
        host="127.0.0.1", 
        port=5001, 
        debug=False
        )