import sqlite3

# Delete old database and create new one with emotion column
connection = sqlite3.connect("attendance_data/attendance.db")
cursor = connection.cursor()

# Drop old table
cursor.execute("DROP TABLE IF EXISTS attendance")

# Create new table with emotion column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        time TEXT,
        emotion TEXT
    )
''')

connection.commit()
connection.close()

print("✅ Database updated with emotion column!")