import sqlite3
from werkzeug.security import generate_password_hash

# Admin details — change these to your own
ADMIN_NAME = "Rakesh"
ADMIN_EMAIL = "rakeshathani123@gmail.com"
ADMIN_PASSWORD = "admin123"

connection = sqlite3.connect("attendance_data/attendance.db")
cursor = connection.cursor()

# Check if admin already exists
cursor.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,))
existing = cursor.fetchone()

if existing:
    print("⚠️ Admin already exists!")
else:
    # Hash the password for security
    hashed_password = generate_password_hash(ADMIN_PASSWORD)

    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   (ADMIN_NAME, ADMIN_EMAIL, hashed_password, "admin"))
    connection.commit()
    print("✅ Admin account created successfully!")
    print(f"✅ Email: {ADMIN_EMAIL}")
    print(f"✅ Password: {ADMIN_PASSWORD}")
    print("✅ Role: admin")

connection.close()