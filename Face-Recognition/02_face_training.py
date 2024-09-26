import cv2
import numpy as np
from PIL import Image
import os
import json

# Path for face image database
path = 'dataset'
json_output_path = 'name_to_id.json'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def getImagesAndLabels(path):
    # Get all image paths
    imagePaths = [os.path.normpath(os.path.join(path, f)) for f in os.listdir(path) if f.endswith('.jpg')]
    print(imagePaths)
    
    faceSamples = []
    ids = []
    
    # Map each person (name) to a unique ID
    name_to_id = {}
    current_id = 1
    
    # Load profile face detector
    profile_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

    for imagePath in imagePaths:
        # Extract the person's name from the filename
        filename = os.path.split(imagePath)[-1]
        name = filename.split(".")[1]
        
        # Assign a unique ID to each person and store it in a JSON
        if name not in name_to_id:
            name_to_id[name] = current_id
            current_id += 1
        
        id = name_to_id[name]
        
        # Load image and convert to grayscale
        PIL_img = Image.open(imagePath).convert('L')  # convert to grayscale
        img_numpy = np.array(PIL_img, 'uint8')
        
        # Detect faces (frontal)
        faces = detector.detectMultiScale(img_numpy)
        
        # Detect profile faces
        profile_faces = profile_detector.detectMultiScale(img_numpy)

        # Process detected faces
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y + h, x:x + w])
            ids.append(id)
        
        for (x, y, w, h) in profile_faces:
            faceSamples.append(img_numpy[y:y + h, x:x + w])
            ids.append(id)
    
    # Save the name-to-ID mapping in a JSON file
    with open(json_output_path, 'w') as json_file:
        json.dump(name_to_id, json_file, indent=4)
    
    return faceSamples, ids

print("Loading training data")
faces, ids = getImagesAndLabels(path)
print("\n[INFO] Training faces. It will take a few seconds. Wait ...")
recognizer.train(faces, np.array(ids))

# Save the model into trainer.yml
recognizer.write('./trainer/trainer.yml')

# Print the number of faces trained and end program
print("\n[INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
