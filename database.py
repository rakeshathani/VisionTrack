import sqlite3

connection = sqlite3.connect("attendance_data/attendance.db")
cursor = connection.cursor()

# Drop old tables completely
cursor.execute("DROP TABLE IF EXISTS attendance")
cursor.execute("DROP TABLE IF EXISTS class_students")
cursor.execute("DROP TABLE IF EXISTS classes")
cursor.execute("DROP TABLE IF EXISTS students")

print("✅ Old tables cleared!")

# Table 1 - Users (Admin and Teachers) — keep existing users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Table 2 - Students
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        photo_path TEXT
    )
''')

# Table 3 - Classes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        teacher_id INTEGER,
        FOREIGN KEY (teacher_id) REFERENCES users(id)
    )
''')

# Table 4 - Which student is in which class
cursor.execute('''
    CREATE TABLE IF NOT EXISTS class_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        student_id INTEGER,
        FOREIGN KEY (class_id) REFERENCES classes(id),
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
''')

# Table 5 - Attendance
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        date TEXT,
        time TEXT,
        emotion TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (class_id) REFERENCES classes(id)
    )
''')

connection.commit()
connection.close()

print("✅ All 5 tables recreated successfully!")