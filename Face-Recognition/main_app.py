from mqtt_client import MQTTClient
from ftp_uploader import FTPUploader
from camera import Camera
from recognition_logic import FaceRecognitionLogic
import cv2
import json
from datetime import datetime
import os
import time
import constants

trainer_file = constants.trainer_file
id_to_names_file = constants.id_to_names_file

class MainApp:
    def __init__(self):
        # Specify the path to your JSON file
        #json_file_path = '/home/admin/Pi-Sensor-Hub-with-Facial-Recognition/SettingsPage/UserPrefs.json'
        
        # Construct the path relative to the script's directory, use absolute path if does not work     
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #json_file_path = os.path.normpath(os.path.join(script_dir, '..', 'SettingsPage', 'UserPrefs.json'))
        #print(json_file_path)
        
        json_file_path = constants.settings_page_file #'../SettingsPage/UserPrefs.json'  
        
        # Open the JSON file for reading
        with open(json_file_path, 'r') as file:
            # Load the JSON data from the file
            self.data = json.load(file)
            
        self.mqtt_client = MQTTClient()
        self.ftp_uploader = FTPUploader()
        self.camera = Camera()
        self.recognizer = FaceRecognitionLogic()
        self.frame_count = 0

    def run(self):
        while True:
            img, gray = self.camera.read_frame()

            #Error handling
            if img is None or gray is None:
                print("Invalid Frame")
                time.sleep(5)
                continue  # Skip iteration if no valid frame

            
            self.frame_count += 1
            
            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break
            
            # Regardless of how fast the frame rate is, only one frame will be sampled per second
            if self.frame_count % self.camera.cam.get(cv2.CAP_PROP_FPS) != 0: #Skip loop if not a full second
                continue
            
            minW, minH = self.camera.get_min_face_size()
            json_object = self.recognizer.identify_faces(gray, img, minW, minH)# Returns basic JSON message add find shirt color afterwards in seperate classifier, using img instead of gray
            
            #is_tenth_minute = ((self.frame_count/self.camera.cam.get(cv2.CAP_PROP_FPS))*5 == 300)
            
            # human is detected
            if json_object is not None:
                #Person detected
                file_name = json_object['filename']
                folder_path = self.data['filePaths']['snapshotFolder']
                local_img_path = folder_path + file_name
                thumbnail_path = file_name[:-3] + "jpg"
                local_thumbnail_path = self.data['filePaths']['snapshotFolder'] + thumbnail_path
                self.camera.record_video(1 , local_img_path, local_thumbnail_path , img) #Video length is further reduced # Added img to supply thumbnail image
                file_name = "alerts/" + file_name
                gcp_thumbnail_path = "alerts/" + thumbnail_path
               
                side_effect_url = self.ftp_uploader.upload_file(local_img_path, file_name)
                gcp_thumbnail_url = self.ftp_uploader.upload_file(local_thumbnail_path, gcp_thumbnail_path, False)
                json_object['mediaURL'] = side_effect_url
                json_object['imagepath'] = gcp_thumbnail_url
                self.mqtt_client.publish(json_object)
                time.sleep(1)
            
            #Recogniser update
            #Stop recognising to download new trainer if Flag is raised by MQTT
            if self.mqtt_client.update_trainer == True and self.mqtt_client.url != "":
                #File avaliable for download
                print("Start download of new trainer file")
                self.mqtt_client.custom_topic_publish("\n\n\nDownload started...\n\n\n", "/download/response")
                self.ftp_uploader.download_file(self.mqtt_client.url, trainer_file)
                print("Start download of new json file")
                self.ftp_uploader.download_file(self.mqtt_client.url_json, id_to_names_file)
                self.mqtt_client.update_trainer = False
                self.mqtt_client.custom_topic_publish("\n\n\nDownload successful\n\n\n", "/download/response")

        print("\n[INFO] Exiting Program and cleanup stuff")
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = MainApp()
    app.run()
