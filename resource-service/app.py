from flask import Flask, jsonify
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

    return jsonify(dict(booking))

if __name__ == "__main__":
    app.run(
        host="127.0.0.1", 
        port=5001, 
        debug=False
        )