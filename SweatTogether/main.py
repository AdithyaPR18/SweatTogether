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
frame_width = 2560  # Adjust as needed
frame_height = 1920  # Adjust as needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

# Exercise selection
selected_exercise = input("Select an exercise (pushups/situps/jumpingjacks/bicep): ").lower()

# Variables for push-up detection and progress tracking
max_pushup_angle = 92  # Angle at which push-up is at its max
min_pushup_angle = 111  # Starting angle
pushup_start = False
pushup_progress = 0
rep_count = 0
rep_in_progress = False

# Variables for bicep curl detection and progress tracking (right arm)
max_curl_angle_right = 270  # Adjust this based on your own comfort
min_curl_angle_right = 90   # Adjust this based on your own comfort

# Variables for bicep curl detection and progress tracking (left arm)
max_curl_angle_left = 260    # Adjust this based on your own comfort
min_curl_angle_left = 80     # Adjust this based on your own comfort

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

        # Exercise selection handling
        if selected_exercise == "pushups":
            # Extract keypoints for right shoulder and right elbow
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]

            # Calculate angle using trigonometry for right elbow
            if right_shoulder and right_elbow:
                shoulder_angle_right = math.degrees(math.atan2(right_elbow.y - right_shoulder.y, right_elbow.x - right_shoulder.x))

                # Check for push-up start
                if shoulder_angle_right <= max_pushup_angle:
                    pushup_start = True
                    pushup_progress = 0
                    if rep_in_progress and pushup_progress >= 75:
                        rep_in_progress = False

                # Calculate push-up progress based on angle
                if pushup_start:
                    pushup_progress = int(((max_pushup_angle - shoulder_angle_right) / (max_pushup_angle - min_pushup_angle)) * 100)
                    pushup_progress = max(min(pushup_progress, 100), 0)

                    # Rep counting logic
                    if pushup_progress <= 15 and not rep_in_progress:
                        rep_in_progress = True
                    elif pushup_progress >= 75 and rep_in_progress:
                        rep_count += 1
                        rep_in_progress = False

                # Display push-up progress, elbow angle, and rep count
                cv2.putText(frame, f"Push-up Progress: {pushup_progress}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, f"Right Elbow Angle: {shoulder_angle_right:.2f} degrees", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, f"Rep Count: {rep_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        elif selected_exercise == "situps":
            cv2.putText(frame, "Situps: Feature being implemented", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif selected_exercise == "jumpingjacks":
            cv2.putText(frame, "Jumping Jacks: Feature being implemented", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif selected_exercise == "bicep":
            # Extract keypoints for right and left elbows
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]

            # Right bicep curl progress
            if right_shoulder and right_elbow and right_wrist:
                shoulder_angle_right = math.degrees(math.atan2(right_elbow.y - right_shoulder.y, right_elbow.x - right_shoulder.x))
                elbow_angle_right = math.degrees(math.atan2(right_wrist.y - right_elbow.y, right_wrist.x - right_elbow.x))

                if elbow_angle_right < 0 and shoulder_angle_right > 0:
                    elbow_angle_right += 360

                if elbow_angle_right >= min_curl_angle_right:
                    progress_right = int(((elbow_angle_right - min_curl_angle_right) / (max_curl_angle_right - min_curl_angle_right)) * 100)
                    progress_right = max(min(progress_right, 100), 0)
                else:
                    progress_right = 0

                cv2.putText(frame, f"Right Elbow Angle: {elbow_angle_right:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, f"Right Curl Progress: {progress_right}%", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            # Left bicep curl progress
            if left_shoulder and left_elbow and left_wrist:
                shoulder_angle_left = math.degrees(math.atan2(left_elbow.y - left_shoulder.y, left_elbow.x - left_shoulder.x))
                elbow_angle_left = math.degrees(math.atan2(left_wrist.y - left_elbow.y, left_wrist.x - left_elbow.x))

                if elbow_angle_left < 0 and shoulder_angle_left > 0:
                    elbow_angle_left += 360

                if 250 <= elbow_angle_left <= 350:
                    progress_left = int(((350 - elbow_angle_left) / (350 - 250)) * 100)
                    progress_left = max(min(progress_left, 100), 0)
                else:
                    progress_left = 0

                cv2.putText(frame, f"Left Elbow Angle: {elbow_angle_left:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, f"Left Curl Progress: {progress_left}%", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        else:
            cv2.putText(frame, "Select a valid exercise", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Draw pose landmarks on the frame
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display the frame
    cv2.imshow('Exercise Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()