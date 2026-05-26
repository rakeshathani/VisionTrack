import sqlite3

connection = sqlite3.connect("attendance_data/attendance.db")
cursor = connection.cursor()

cursor.execute("SELECT * FROM attendance")
records = cursor.fetchall()

print("---- Attendance Records ----")
for record in records:
    print(f"ID: {record[0]} | Name: {record[1]} | Date: {record[2]} | Time: {record[3]}")

connection.close()