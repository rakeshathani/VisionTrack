import cv2
import face_recognition

# Load your photo and learn your face
print("Loading known faces...")
rakesh_image = face_recognition.load_image_file("student_photos/rakesh.jpg")
rakesh_encoding = face_recognition.face_encodings(rakesh_image)[0]

# Save known faces and their names in a list
known_encodings = [rakesh_encoding]
known_names = ["Rakesh"]

print("Face loaded! Starting camera...")

# Open camera
camera = cv2.VideoCapture(0)

while True:
    # Read frame
    success, frame = camera.read()

    # Make frame smaller for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert to RGB (face_recognition needs RGB)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all faces in frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Check each face
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare with known faces
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            index = matches.index(True)
            name = known_names[index]

        # Scale back up (we made it smaller earlier)
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw box around face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Show name below the box
        cv2.rectangle(frame, (left, bottom), (right, bottom+35), (0, 255, 0), -1)
        cv2.putText(frame, name, (left+6, bottom+25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # Show frame
    cv2.imshow("VisionTrack - Face Recognition", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
print("Camera stopped.")