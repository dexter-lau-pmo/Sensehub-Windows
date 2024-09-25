import cv2
import numpy as np

# Load the image
image = cv2.imread('shirts/orange_shirt.jpg')

# Convert to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define color ranges (for example, red)
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# Create a mask for red
mask = cv2.inRange(hsv_image, lower_red, upper_red)

# Find contours of the shirt area
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contours:
    largest_contour = max(contours, key=cv2.contourArea)
    # Calculate the mean color of the shirt
    mask_mean = cv2.mean(image, mask=mask)
    print("Detected color (BGR):", mask_mean[:3])  # Output the BGR values

# Display the image with the detected color
cv2.imshow('Detected Shirt Color', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
