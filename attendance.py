import cv2
import face_recognition
import sqlite3
import pickle
from datetime import datetime
from deepface import DeepFace

# ---- Load all registered students ----
print("Loading registered students...")
with open("models/encodings.pkl", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

print(f"✅ Loaded {len(known_names)} students: {known_names}")

# ---- Function to mark attendance with emotion ----
def mark_attendance(name, emotion):
    connection = sqlite3.connect("attendance_data/attendance.db")
    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, today))
    record = cursor.fetchone()

    if record is None:
        cursor.execute("INSERT INTO attendance (name, date, time, emotion) VALUES (?, ?, ?, ?)", (name, today, current_time, emotion))
        connection.commit()
        print(f"✅ Attendance marked for {name} at {current_time} | Emotion: {emotion}")
    else:
        print(f"⚠️ {name} already marked today")

    connection.close()

# ---- Start camera ----
print("Starting camera... Press Q to stop.")
camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    # ---- Detect emotion ----
    emotion = "unknown"
    try:
        result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
        emotion = result[0]["dominant_emotion"]
    except:
        pass

    # ---- Detect and recognise faces ----
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            index = matches.index(True)
            name = known_names[index]
            mark_attendance(name, emotion)

        # Scale back up
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw box
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom), (right, bottom+55), color, -1)
        cv2.putText(frame, name, (left+6, bottom+25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(frame, emotion, (left+6, bottom+50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

    cv2.imshow("VisionTrack - Attendance + Emotion", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
print("Camera stopped.")