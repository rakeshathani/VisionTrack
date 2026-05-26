from deepface import DeepFace
import cv2

print("Loading camera...")
camera = cv2.VideoCapture(0)

print("Camera ready! Press Q to stop.")

while True:
    success, frame = camera.read()

    try:
        # Detect emotion
        result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)

        # Get the dominant emotion
        emotion = result[0]["dominant_emotion"]

        # Show emotion on screen
        cv2.putText(frame, f"Emotion: {emotion}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        print(f"Emotion detected: {emotion}")

    except Exception as e:
        pass

    cv2.imshow("VisionTrack - Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
print("Camera stopped.")