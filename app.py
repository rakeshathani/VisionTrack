from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# ---- Function to get all attendance records ----
def get_attendance():
    connection = sqlite3.connect("attendance_data/attendance.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    records = cursor.fetchall()
    connection.close()
    return records

# ---- Main page route ----
@app.route("/")
def home():
    records = get_attendance()
    total = len(records)
    return render_template("index.html", records=records, total=total)

if __name__ == "__main__":
    print("✅ VisionTrack Dashboard starting...")
    print("✅ Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True)