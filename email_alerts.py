import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ---- Your Gmail details ----
SENDER_EMAIL = "rakeshathani123@gmail.com"      # your gmail here
APP_PASSWORD = "yjdp olrb sbqk zoki"       # your 16 letter password here

# ---- Student email list ----
student_emails = {
    "Rakesh": "athanirakesh12@gmail.com",    # replace with real email
    "Bhima": "rakeshathani2003@gmail.com",      # replace with real email
}

# ---- Function to count attendance ----
def get_attendance_count(name):
    connection = sqlite3.connect("attendance_data/attendance.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE name=?", (name,))
    count = cursor.fetchone()[0]
    connection.close()
    return count

# ---- Function to send email ----
def send_email(to_email, student_name, count):
    subject = "⚠️ Low Attendance Alert - VisionTrack"
    body = f"""
Dear {student_name},

This is an automated alert from VisionTrack Attendance System.

Your current attendance count is: {count} days

Your attendance is below the required level. 
Please attend classes regularly to avoid problems.

Regards,
VisionTrack System
    """

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, message.as_string())
        server.quit()
        print(f"✅ Email sent to {student_name} at {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {student_name}: {e}")

# ---- Check all students ----
print("Checking attendance for all students...")
LOW_ATTENDANCE_LIMIT = 3

for name, email in student_emails.items():
    count = get_attendance_count(name)
    print(f"{name}: {count} days attended")

    if count < LOW_ATTENDANCE_LIMIT:
        print(f"⚠️ {name} has low attendance — sending alert!")
        send_email(email, name, count)
    else:
        print(f"✅ {name} attendance is fine")

print("\nDone checking attendance!")