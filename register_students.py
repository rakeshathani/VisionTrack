import face_recognition
import pickle
import os

# List of students — add name and photo file here
students = [
    {"name": "Rakesh", "photo": "student_photos/rakesh.jpg"},
    {"name": "Bhima",  "photo": "student_photos/bhima.jpg"},
]

known_encodings = []
known_names = []

print("Registering students...")

for student in students:
    name = student["name"]
    photo = student["photo"]

    # Check if photo exists
    if not os.path.exists(photo):
        print(f"❌ Photo not found for {name} — skipping")
        continue

    # Load photo and encode face
    image = face_recognition.load_image_file(photo)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        print(f"❌ No face found in {name}'s photo — skipping")
        continue

    known_encodings.append(encodings[0])
    known_names.append(name)
    print(f"✅ {name} registered successfully!")

# Save all encodings to a file
data = {"encodings": known_encodings, "names": known_names}
with open("models/encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print(f"\n✅ Total students registered: {len(known_names)}")
print("✅ Encodings saved to models/encodings.pkl")