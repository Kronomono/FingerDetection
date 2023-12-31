import cv2
import mediapipe as mp

import math

def calculate_angle(finger_tip, finger_base, palm):
    # Calculate the vectors for finger_tip to finger_base and finger_tip to palm
    vec1 = [finger_tip.x - finger_base.x, finger_tip.y - finger_base.y]
    vec2 = [finger_tip.x - palm.x, finger_tip.y - palm.y]

    # Calculate the angle between the two vectors
    dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    magnitude_product = math.sqrt(vec1[0]**2 + vec1[1]**2) * math.sqrt(vec2[0]**2 + vec2[1]**2)
    angle_rad = math.acos(dot_product / magnitude_product)
    angle_deg = math.degrees(angle_rad)

    return angle_deg


def count_fingers(landmarks):
    # Indices of finger tip landmarks in the hand landmarks list
    tip_indices = [4, 8, 12, 16, 20]

    # Count the number of fingers that are "up"
    finger_count = 0

    # Check the angle between adjacent fingers
    for i in range(len(tip_indices)):
        finger_tip = landmarks.landmark[tip_indices[i]]

        if i == 0:  # thumb
            finger_base = landmarks.landmark[tip_indices[i] - 1]
            threshold_angle = 40  # Adjust this value for thumb if necessary
        else:
            finger_base = landmarks.landmark[tip_indices[i] - 2]
            threshold_angle = 90  # For other fingers

        palm = landmarks.landmark[0]  # Landmark for the center of the palm

        # Calculate the angle between the finger tip, finger base, and palm
        angle = calculate_angle(finger_tip, finger_base, palm)

        # Check the threshold angle to determine if the finger is raised or not
        if angle < threshold_angle:
            finger_count += 1

    return finger_count


def count_hands_fingers(landmarks_list):
    # This function will return a dictionary with separate counts for left and right hands
    finger_counts = {"Left": 0, "Right": 0}

    for hand_landmarks, hand_info in landmarks_list:
        # Get the finger count for this hand
        finger_count = count_fingers(hand_landmarks)

#inverse to get accurate hand
        if hand_info.classification[0].label == "Left":
            finger_counts["Right"] = finger_count
        else:
            finger_counts["Left"] = finger_count

    return finger_counts


def display_camera_with_finger_detection():
    # Load Mediapipe hand tracking module
    mp_hands = mp.solutions.hands

    # Open the default camera (usually the first camera in the system)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    # Initialize Mediapipe hand tracking
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Unable to capture frame.")
                break

            # Convert the frame from BGR to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame
            results = hands.process(rgb_frame)

            # Check if hand(s) are detected
            if results.multi_hand_landmarks and results.multi_handedness:
                # Zip the landmarks and hand info for easier access
                zipped_info = zip(results.multi_hand_landmarks, results.multi_handedness)

                # Get the counts for both hands
                finger_counts = count_hands_fingers(zipped_info)

                for hand_landmarks in results.multi_hand_landmarks:
                    for landmark in hand_landmarks.landmark:
                        x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Display the counts for both hands
                cv2.putText(frame, f"Left Hand Fingers: {finger_counts['Left']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0), 2)
                cv2.putText(frame, f"Right Hand Fingers: {finger_counts['Right']}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

            # Display the frame
            cv2.imshow("Camera Footage with Finger Detection", frame)

            # Wait for 1 millisecond and check if 'q' key is pressed to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    display_camera_with_finger_detection()