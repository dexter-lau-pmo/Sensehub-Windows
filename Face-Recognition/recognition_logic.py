import cv2
import json
import os
import logging
from datetime import datetime
from shatsu import Shatsu
import constants

# Set up logging
logging.basicConfig(level=logging.INFO)

id_to_names_file = constants.id_to_names_file
trainer_file = constants.trainer_file
haarcascade_file = constants.haarcascade_file
settings_page_file = constants.settings_page_file

class FaceRecognitionLogic:
    def __init__(self):
        json_file_path = settings_page_file
        logging.info(f"Loading preferences from {json_file_path}")

        # Open the JSON file for reading
        try:
            with open(json_file_path, 'r') as file:
                self.data = json.load(file)
        except Exception as e:
            logging.error(f"Failed to load JSON data: {e}")
            raise

        self.names = self.get_names_from_json(id_to_names_file)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        try:
            self.recognizer.read(trainer_file)
        except Exception as e:
            logging.error(f"Failed to load the recognizer model: {e}")
            raise

        self.faceCascade = cv2.CascadeClassifier(haarcascade_file)
        self.profileCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

    def identify_faces(self, gray_img, img, minW, minH):
        frontal_faces = []
        profile_faces = []
        # Detect frontal faces
        frontal_faces , rejectLevels, levelWeights = self.faceCascade.detectMultiScale3(
            gray_img,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
            outputRejectLevels = 1
        )
        if len(frontal_faces)>0:
            print("Fontal Face: ")
            print("Faces: ", frontal_faces)
            print("rejectLevels: ", rejectLevels)
            print("levelWeights: ", levelWeights)

        # Detect profile faces
        profile_faces, rejectLevels, levelWeights= self.profileCascade.detectMultiScale3(
            gray_img,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
            outputRejectLevels = 1
        )

        if len(profile_faces)>0:
            print("")
            print("Profile Face: ")
            print("Faces: ", profile_faces)
            print("rejectLevels: ", rejectLevels)
            print("levelWeights: ", levelWeights)

        all_faces = list(frontal_faces) + list(profile_faces)  # Combine both detections
        message = None

        shatsu_obj = Shatsu("")
        if len(all_faces) > 0:
            timestamp = datetime.timestamp(datetime.now())
            timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H_%M_%S')
            file_name = f"{timestamp_str}.mp4"
            file_path = os.path.join(self.data['filePaths']['snapshotFolder'], file_name)
            names = []
            distance = 10000 #Set high inital distance, to select face with lowest distance
           
            names.append("Unknown")
            for (x, y, w, h) in all_faces:
                #id, distance = self.recognizer.predict(gray_img[y:y+h, x:x+w])
                #names.append("Unknown") 
                curr_id, curr_distance = self.recognizer.predict(gray_img[y:y+h, x:x+w])

                print("Curr Id, distance : " , curr_id , "  ,  " , curr_distance)

                if curr_distance < distance: #If current face is the most accurate, use it as the face detected
                    id = curr_id
                    distance = curr_distance

            if distance < 75:  # Low distance means high confidence
                names[-1] = self.names[id] #Get name from JSON
            else: # if confidence is too low(?)
                names[-1] = "Unknown" 

            color = shatsu_obj.detect(img , x, y, w, h)

            logging.info(f"Identified {len(names)} faces: {names} with distances: {distance}")
            logging.info(f"Identified color: {color} ")

            # JSONify
            message = {
                "names": names[-1], #Insert last name
                "timestamp": timestamp_str,
                "filename": file_name,
                "imagepath": "/" + file_name,
                "confidence": "{0}%".format((1.0 - (distance / 250)) * 100),
                "color": color
            }

        return message

    def get_names_from_json(self, json_file):
        try:
            with open(json_file, 'r') as file:
                name_to_id = json.load(file)
        except Exception as e:
            logging.error(f"Failed to load name to ID mapping: {e}")
            raise
        
        max_id = max(name_to_id.values())  # Find the highest ID
        names = [None] * (max_id + 1)  # Create a list with enough space for all IDs
        
        names[0] = "Unknown"
        for name, id in name_to_id.items():
            names[id] = name  # Adjust index to zero-based
        return names
