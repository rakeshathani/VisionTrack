from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import csv
import os
import subprocess
import sys

app = Flask(__name__)
app.secret_key = "visiontrack2026"

DB = "attendance_data/attendance.db"

def get_db():
    return sqlite3.connect(DB)

# ---- HOME ----
@app.route("/")
def home():
    return redirect("/login")

# ---- LOGIN ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user[3], password):
            session["id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[4]
            if user[4] == "admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/teacher/dashboard")
        else:
            return render_template("login.html", error="Wrong email or password!")

    return render_template("login.html", error=None)

# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ====================
# ADMIN ROUTES
# ====================

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, name, email FROM users WHERE role='teacher'")
    teachers = cursor.fetchall()

    cursor.execute("SELECT id, name, email FROM students")
    students = cursor.fetchall()

    cursor.execute("""
        SELECT classes.id, classes.class_name, classes.subject, users.name
        FROM classes
        LEFT JOIN users ON classes.teacher_id = users.id
    """)
    classes = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    db.close()

    return render_template("admin/dashboard.html",
        teachers=teachers,
        students=students,
        classes=classes,
        total_teachers=len(teachers),
        total_students=len(students),
        total_classes=len(classes),
        total_attendance=total_attendance,
        message=request.args.get("message")
    )

# ---- Add Teacher ----
@app.route("/admin/add_teacher", methods=["POST"])
def add_teacher():
    if session.get("role") != "admin":
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                   (name, email, password, "teacher"))
    db.commit()
    db.close()

    return redirect("/admin/dashboard?message=Teacher added successfully!")

# ---- Delete Teacher ----
@app.route("/admin/delete_teacher/<int:id>")
def delete_teacher(id):
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=? AND role='teacher'", (id,))
    db.commit()
    db.close()

    return redirect("/admin/dashboard?message=Teacher removed!")

# ---- Add Student ----
@app.route("/admin/add_student", methods=["POST"])
def add_student():
    if session.get("role") != "admin":
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO students (name, email) VALUES (?, ?)", (name, email))
    db.commit()
    db.close()

    return redirect("/admin/dashboard?message=Student added successfully!")

# ---- Delete Student ----
@app.route("/admin/delete_student/<int:id>")
def delete_student(id):
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()

    return redirect("/admin/dashboard?message=Student removed!")

# ---- Add Class ----
@app.route("/admin/add_class", methods=["POST"])
def add_class():
    if session.get("role") != "admin":
        return redirect("/login")

    class_name = request.form["class_name"]
    subject = request.form["subject"]
    teacher_id = request.form["teacher_id"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO classes (class_name, subject, teacher_id) VALUES (?, ?, ?)",
                   (class_name, subject, teacher_id))
    db.commit()
    db.close()

    return redirect("/admin/dashboard?message=Class created successfully!")

# ---- Delete Class ----
@app.route("/admin/delete_class/<int:id>")
def delete_class(id):
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM classes WHERE id=?", (id,))
    db.commit()
    db.close()

    return redirect("/admin/dashboard?message=Class removed!")

# ---- Assign Student to Class ----
@app.route("/admin/assign_student", methods=["POST"])
def assign_student():
    if session.get("role") != "admin":
        return redirect("/login")

    class_id = request.form["class_id"]
    student_id = request.form["student_id"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM class_students
        WHERE class_id=? AND student_id=?
    """, (class_id, student_id))
    existing = cursor.fetchone()

    if not existing:
        cursor.execute("""
            INSERT INTO class_students (class_id, student_id)
            VALUES (?, ?)
        """, (class_id, student_id))
        db.commit()

    db.close()
    return redirect("/admin/dashboard?message=Student assigned to class!")

# ---- Upload Student Photo ----
@app.route("/admin/upload_photo/<int:student_id>", methods=["POST"])
def upload_photo(student_id):
    if session.get("role") != "admin":
        return redirect("/login")

    photo = request.files["photo"]
    if photo:
        filename = f"student_photos/student_{student_id}.jpg"
        photo.save(filename)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE students SET photo_path=? WHERE id=?",
                       (filename, student_id))
        db.commit()
        db.close()

    return redirect("/admin/dashboard?message=Photo uploaded successfully!")

# ====================
# TEACHER ROUTES
# ====================

@app.route("/teacher/dashboard")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT classes.id, classes.class_name, classes.subject,
               COUNT(class_students.student_id)
        FROM classes
        LEFT JOIN class_students ON classes.id = class_students.class_id
        WHERE classes.teacher_id = ?
        GROUP BY classes.id
    """, (session["id"],))
    classes = cursor.fetchall()

    cursor.execute("""
        SELECT students.name, classes.class_name,
               attendance.date, attendance.time, attendance.emotion
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        JOIN classes ON attendance.class_id = classes.id
        WHERE classes.teacher_id = ?
        ORDER BY attendance.date DESC, attendance.time DESC
        LIMIT 20
    """, (session["id"],))
    attendance = cursor.fetchall()

    db.close()

    return render_template("teacher/dashboard.html",
        classes=classes,
        attendance=attendance,
        message=request.args.get("message")
    )

# ---- Take Attendance Page ----
@app.route("/teacher/take_attendance/<int:class_id>")
def take_attendance(class_id):
    if session.get("role") != "teacher":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT class_name, subject FROM classes WHERE id=?", (class_id,))
    cls = cursor.fetchone()

    cursor.execute("""
        SELECT students.id, students.name, students.email
        FROM students
        JOIN class_students ON students.id = class_students.student_id
        WHERE class_students.class_id = ?
    """, (class_id,))
    students = cursor.fetchall()

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT student_id FROM attendance
        WHERE class_id=? AND date=?
    """, (class_id, today))
    present_ids = [row[0] for row in cursor.fetchall()]

    db.close()

    return render_template("teacher/take_attendance.html",
        class_id=class_id,
        class_name=cls[0],
        subject=cls[1],
        students=students,
        present_ids=present_ids,
        message=request.args.get("message")
    )

# ---- Start Camera ----
@app.route("/teacher/start_camera/<int:class_id>")
def start_camera(class_id):
    if session.get("role") != "teacher":
        return redirect("/login")

    subprocess.Popen([sys.executable, "run_camera.py", str(class_id)])

    return redirect(f"/teacher/take_attendance/{class_id}?message=Camera started! Press Q on camera window to stop.")

# ---- Export CSV ----
@app.route("/teacher/export/<int:class_id>")
def export_csv(class_id):
    if session.get("role") != "teacher":
        return redirect("/login")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT students.name, classes.class_name,
               attendance.date, attendance.time, attendance.emotion
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        JOIN classes ON attendance.class_id = classes.id
        WHERE attendance.class_id = ?
    """, (class_id,))
    records = cursor.fetchall()
    db.close()

    filepath = f"attendance_data/attendance_class_{class_id}.csv"
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student", "Class", "Date", "Time", "Emotion"])
        writer.writerows(records)

    return redirect(f"/teacher/dashboard?message=CSV exported to {filepath}")

if __name__ == "__main__":
    print("✅ VisionTrack starting...")
    print("✅ Open browser at: http://127.0.0.1:5000")
    app.run(debug=True)