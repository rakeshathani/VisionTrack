# VisionTrack - Intelligent Classroom Attendance System

## What is VisionTrack?
VisionTrack is an AI-powered attendance system that uses face recognition to automatically mark student attendance in real time using a webcam.

## Features
- Live face recognition using webcam
- Automatic attendance marking with date and time
- Emotion detection for each student
- Anti-proxy protection (no duplicate entries)
- Web dashboard for faculty to view attendance
- Automatic email alerts for low attendance

## Technologies Used
- Python 3.11
- OpenCV
- face_recognition
- DeepFace (Emotion Detection)
- Flask (Web Dashboard)
- SQLite (Database)
- smtplib (Email Alerts)

## Project Structure
- attendance.py — Main attendance marking script
- app.py — Web dashboard
- register_students.py — Register new students
- email_alerts.py — Send low attendance alerts
- database.py — Database setup
- student_photos/ — Student face photos
- attendance_data/ — Attendance database
- models/ — Saved face encodings
- templates/ — Web dashboard HTML

## How to Run

### Step 1 - Activate virtual environment
venv\Scripts\activate

### Step 2 - Register students
python register_students.py

### Step 3 - Start attendance system
python attendance.py

### Step 4 - View dashboard
python app.py
Then open browser at http://127.0.0.1:5000

## Developer
Rakesh — VisionTrack Internship Project 2026