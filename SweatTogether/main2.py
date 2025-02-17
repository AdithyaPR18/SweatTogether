import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Pose module
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# OpenCV setup
cap = cv2.VideoCapture(0)  # You can also specify a video file here

# Set the desired width and height for the frame
frame_width = 1920  # Adjust as needed
frame_height = 1440  # Adjust as needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

# Initialize variables for thumb distance and rep counting
thumb_distance = 0.0
thumb_apart = True
rep_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with PoseNet
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Extract landmarks for both thumbs
        right_thumb = landmarks[mp_pose.PoseLandmark.RIGHT_THUMB]
        left_thumb = landmarks[mp_pose.PoseLandmark.LEFT_THUMB]

        if right_thumb and left_thumb:
            # Calculate the distance between the thumbs
            thumb_distance = math.sqrt((right_thumb.x - left_thumb.x) ** 2 + (right_thumb.y - left_thumb.y) ** 2)

            # Display the distance on the frame
            cv2.putText(frame, f"Thumb Distance: {thumb_distance:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            # Rep counting logic
            if thumb_distance <= 0.1 and thumb_apart:
                rep_count += 1
                thumb_apart = False
            elif thumb_distance > 0.1:
                thumb_apart = True

            # Display the rep count
            cv2.putText(frame, f"Rep Count: {rep_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        # Draw only the pose landmarks and connections (no coordinates or indices)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display the frame
    cv2.imshow('Thumb Distance and Rep Counter', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()