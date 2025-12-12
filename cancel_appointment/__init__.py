import azure.functions as func
import json
from db import get_connection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        appointment_id = data.get("appointment_id")

        if not appointment_id:
            return func.HttpResponse(
                json.dumps({"message": "Missing 'appointment_id'"}),
                status_code=400,
                mimetype="application/json",
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM Appointments WHERE id=?", (appointment_id,))
        row = cursor.fetchone()
        if not row:
            return func.HttpResponse(
                json.dumps({"message": "Appointment not found"}), status_code=404
            )

        status = row[0]
        if status == "Cancelled":
            return func.HttpResponse(
                json.dumps({"message": "Appointment already cancelled"}), status_code=400
            )
        if status == "Completed":
            return func.HttpResponse(
                json.dumps({"message": "Completed appointments cannot be cancelled"}),
                status_code=400,
            )

        cursor.execute(
            "UPDATE Appointments SET status='Cancelled' WHERE id=?", (appointment_id,)
        )
        conn.commit()

        return func.HttpResponse(
            json.dumps({"message": "Appointment cancelled successfully"}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
