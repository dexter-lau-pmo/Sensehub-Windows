import cv2
import os
from urllib.parse import quote

# Get HaarCascade configurations
faceCascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
profileCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

# Replace 'your_password' with your actual password
password = '#Strongether1'

# Encode the password for URL
encoded_password = quote(password)

# RTSP stream URL with encoded password
rtsp_url = f'rtsp://admin:{encoded_password}@192.168.1.3:554'

# Open the RTSP stream
cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"H264"))

# Set the desired frame size (lower resolution for better performance)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Adjust to lower width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)  # Adjust to lower height

# Buffer size
cap.set(cv2.CAP_PROP_BUFFERSIZE, 30)

# For each person, enter one numeric face id
face_id = input('\n Enter user ID and press <Enter> ==>  ')
print("\n Initializing face capture. Look at the camera and wait ...")

# Initialize individual sampling face count
count = 0

# Set the frame interval to 0.5 seconds
frame_interval = 0.2  # Frame interval in seconds
last_time = cv2.getTickCount() / cv2.getTickFrequency()  # Get the current time in seconds

while True:
    ret, img = cap.read()  # Capture frame
    if not ret:
        print("Failed to grab frame.")
        break
    
    current_time = cv2.getTickCount() / cv2.getTickFrequency()  # Get the current time
    if (current_time - last_time) >= frame_interval:  # Check if enough time has passed
        last_time = current_time  # Update last_time
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect frontal faces
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)

        # Detect profile faces
        profile_faces = profileCascade.detectMultiScale(gray, 1.3, 5)

        # Combine the detected faces
        all_faces = list(faces) + list(profile_faces)

        for (x, y, w, h) in all_faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            count += 1
            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])

        # Show the processed frame
        cv2.imshow('image', img)

    # Check for exit
    k = cv2.waitKey(1) & 0xff  # Press 'ESC' for exiting video
    if k == 27:
        break

# Cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cap.release()
cv2.destroyAllWindows()
