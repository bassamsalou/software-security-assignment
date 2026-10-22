def generate_booking_summary(booking):
    booking_id = booking["id"]
    owner = booking["owner"]
    destination = booking["destination"]
    booking_date = booking["booking_date"]
    status = booking["status"]

    return (
        f"Booking {booking_id} for {owner}: "
        f"{destination} on {booking_date} "
        f"with status '{status}'."
    )