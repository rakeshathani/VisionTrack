import sys
import cv2
import face_recognition
import sqlite3
import os
from datetime import datetime
from deepface import DeepFace

class_id = int(sys.argv[1])
DB = "attendance_data/attendance.db"

def get_db():
    return sqlite3.connect(DB)

# Load students from this class
db = get_db()
cursor = db.cursor()
cursor.execute("""
    SELECT students.id, students.name, students.photo_path
    FROM students
    JOIN class_students ON students.id = class_students.student_id
    WHERE class_students.class_id = ?
""", (class_id,))
students = cursor.fetchall()
db.close()

# Load face encodings
known_encodings = []
known_names = []
known_ids = []

for student in students:
    student_id = student[0]
    name = student[1]
    photo_path = student[2]

    if photo_path and os.path.exists(photo_path):
        image = face_recognition.load_image_file(photo_path)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(name)
            known_ids.append(student_id)
            print(f"✅ Loaded face: {name}")

if len(known_encodings) == 0:
    print("❌ No student photos found!")
    input("Press Enter to close...")
    sys.exit()

total_students = len(known_names)
print(f"✅ Loaded {total_students} students")
print("Starting camera... Camera will stop when all students are marked.")
print("Press Q anytime to stop manually.")

# Track who is already marked
marked_ids = set()

# Check who is already marked today
today = datetime.now().strftime("%Y-%m-%d")
db = get_db()
cursor = db.cursor()
cursor.execute("""
    SELECT student_id FROM attendance
    WHERE class_id=? AND date=?
""", (class_id, today))
already_marked = cursor.fetchall()
db.close()

for row in already_marked:
    marked_ids.add(row[0])

print(f"✅ Already marked today: {len(marked_ids)}/{total_students}")

# Start camera
camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()
    if not success:
        continue

    # Check if all students are marked — stop camera automatically
    if len(marked_ids) >= total_students:
        print("✅ All students marked! Camera closing automatically.")
        cv2.putText(frame, "All students marked! Closing...",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
        cv2.imshow("VisionTrack - Taking Attendance", frame)
        cv2.waitKey(2000)
        break

    # Detect emotion
    emotion = "unknown"
    try:
        result = DeepFace.analyze(frame, actions=["emotion"],
                                  enforce_detection=False)
        emotion = result[0]["dominant_emotion"]
    except:
        pass

    # Face recognition
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings):

        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"
        student_id = None

        if True in matches:
            index = matches.index(True)
            name = known_names[index]
            student_id = known_ids[index]

            # Only mark if not already marked
            if student_id not in marked_ids:
                current_time = datetime.now().strftime("%H:%M:%S")

                db = get_db()
                cursor = db.cursor()
                cursor.execute("""
                    INSERT INTO attendance
                    (student_id, class_id, date, time, emotion)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, class_id, today, current_time, emotion))
                db.commit()
                db.close()

                marked_ids.add(student_id)
                print(f"✅ {name} marked present at {current_time} | Emotion: {emotion}")
                print(f"✅ Progress: {len(marked_ids)}/{total_students} students marked")
            else:
                print(f"⚠️ {name} already marked today")

        # Draw box
        top *= 4; right *= 4; bottom *= 4; left *= 4
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom), (right, bottom+55), color, -1)
        cv2.putText(frame, name, (left+6, bottom+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(frame, emotion, (left+6, bottom+50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

    # Show progress on screen
    progress = f"Marked: {len(marked_ids)}/{total_students}"
    cv2.putText(frame, progress, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("VisionTrack - Taking Attendance", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Camera stopped manually.")
        break

camera.release()
cv2.destroyAllWindows()
print("✅ Camera closed.")