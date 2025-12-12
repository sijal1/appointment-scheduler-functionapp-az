# Appointment Scheduler

**Summary:**  
Book and cancel appointments with providers.

**Table:**  
Appointments(id INT PK IDENTITY, client_name VARCHAR(100), provider_name VARCHAR(100), date DATE, time TIME, status VARCHAR(20)) 

**API: POST /book_appointment**  
Payload:  
{ "client_name":"Maya", "provider_name":"Dr. Roy", "date":"2025-11-02", "time":"10:30" }
- Flow: 
1. Ensure provider has no appointment at same date/time. 
2. Insert appointment with status 'Booked'. 
- Response: { "message":"Appointment booked", "appointment_id":1201 } 

**API: PUT /cancel_appointment**  
Payload: { "appointment_id":1201 } 
- Flow: Update status to 'Cancelled' and return confirmation. 

**API: GET /appointments/provider_name?date=YYYY-MM-DD**
- Response: Array of appointments for provider on that date.