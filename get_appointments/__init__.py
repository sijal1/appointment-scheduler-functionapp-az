import azure.functions as func
import json
from db import get_connection

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        provider_name = req.params.get("provider_name")
        date = req.params.get("date")
        status_filter = req.params.get("status")  

        if not provider_name or not date:
            return func.HttpResponse(
                json.dumps({"message": "Missing 'provider_name' or 'date' query parameters"}),
                status_code=400,
                mimetype="application/json",
            )

        conn = get_connection()
        cursor = conn.cursor()

        if status_filter and status_filter.lower() != "all":
            cursor.execute(
                """
                SELECT id, client_name, time, status
                FROM Appointments
                WHERE provider_name=? AND date=? AND status=?
                ORDER BY time
                """,
                (provider_name, date, status_filter.capitalize()),
            )
        else:
            cursor.execute(
                """
                SELECT id, client_name, time, status
                FROM Appointments
                WHERE provider_name=? AND date=?
                ORDER BY time
                """,
                (provider_name, date),
            )

        rows = cursor.fetchall()
        if not rows:
            return func.HttpResponse(
                json.dumps({"message": "No appointments found"}),
                status_code=404,
                mimetype="application/json",
            )

        appointments = [
            {"id": r[0], "client_name": r[1], "time": str(r[2]), "status": r[3]}
            for r in rows
        ]

        return func.HttpResponse(
            json.dumps(appointments), mimetype="application/json", status_code=200
        )

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
