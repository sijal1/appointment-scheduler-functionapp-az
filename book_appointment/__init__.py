import azure.functions as func
import json
from datetime import datetime, time as time_cls, timedelta
from db import get_connection
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        client = data.get("client_name", "").strip()
        provider = data.get("provider_name", "").strip()
        date_str = data.get("date")
        time_str = data.get("time")

        if not all([client, provider, date_str, time_str]):
            return func.HttpResponse(
                json.dumps({"message": "Missing required fields"}),
                status_code=400,
            )

        name_pattern = re.compile(r"^[A-Za-z\s\.\-]+$")
        if not name_pattern.match(client):
            return func.HttpResponse(
                json.dumps(
                    {"message": "Invalid client name. Only letters and spaces allowed."}
                ),
                status_code=400,
            )

        if not name_pattern.match(provider):
            return func.HttpResponse(
                json.dumps(
                    {"message": "Invalid provider name. Only letters and spaces allowed."}
                ),
                status_code=400,
            )

        try:
            appt_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return func.HttpResponse(
                json.dumps({"message": "Invalid date or time format"}),
                status_code=400,
            )

        try:
            appt_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return func.HttpResponse(
                json.dumps({"message": "Invalid date or time format"}),
                status_code=400,
            )

        if appt_datetime < datetime.utcnow():
            return func.HttpResponse(
                json.dumps({"message": "Cannot book an appointment in the past"}),
                status_code=400,
            )

        start_time, end_time = time_cls(9, 0), time_cls(17, 0)
        if not (start_time <= appt_datetime.time() <= end_time):
            return func.HttpResponse(
                json.dumps({"message": "Bookings allowed only between 09:00 and 17:00"}),
                status_code=400,
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM Appointments
            WHERE provider_name=? AND date=?
              AND status='Booked'
              AND ABS(DATEDIFF(MINUTE, time, ?)) < 10
            """,
            (provider, date_str, time_str),
        )
        if cursor.fetchone()[0] > 0:
            return func.HttpResponse(
                json.dumps(
                    {"message": "Provider not available within 10 minutes of this slot"}
                ),
                status_code=400,
            )

        cursor.execute(
            """
            SELECT COUNT(*) FROM Appointments
            WHERE client_name=? AND provider_name=? AND date=? AND time=? AND status='Booked'
            """,
            (client, provider, date_str, time_str),
        )
        if cursor.fetchone()[0] > 0:
            return func.HttpResponse(
                json.dumps({"message": "Client already has an appointment at this time"}),
                status_code=400,
            )

        cursor.execute(
            """
            INSERT INTO Appointments (client_name, provider_name, date, time, status)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, 'Booked')
            """,
            (client, provider, date_str, time_str),
        )
        appointment_id = cursor.fetchone()[0]
        conn.commit()

        return func.HttpResponse(
            json.dumps(
                {"message": "Appointment booked successfully", "appointment_id": appointment_id}
            ),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
