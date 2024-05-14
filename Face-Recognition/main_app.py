from mqtt_client import MQTTClient
from ftp_uploader import FTPUploader
from camera import Camera
from recognition_logic import FaceRecognitionLogic
import cv2
import json
from datetime import datetime

class MainApp:
    def __init__(self):
        # Specify the path to your JSON file
        json_file_path = '/home/admin/Pi-Sensor-Hub-with-Facial-Recognition/SettingsPage/UserPrefs.json'

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
            
            self.frame_count += 1
            
            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break
            
            # Regardless of how fast the frame rate is, only one frame will be sampled per second
            if self.frame_count % self.camera.cam.get(cv2.CAP_PROP_FPS) != 0:
                continue
            
            minW, minH = self.camera.get_min_face_size()
            json_object = self.recognizer.identify_faces(gray, minW, minH)
            is_tenth_minute = ((self.frame_count/self.camera.cam.get(cv2.CAP_PROP_FPS))*5 == 300)
            
            # human is detected
            if json_object is not None:
                #Person detected
                file_name = json_object['filename']
                folder_path = self.data['filePaths']['snapshotFolder']
                local_img_path = folder_path + file_name
                thumbnail_path = file_name[:-3] + "jpg"
                local_thumbnail_path = self.data['filePaths']['snapshotFolder'] + thumbnail_path
                self.camera.record_video(3, local_img_path, local_thumbnail_path) #Video length is reduced
                file_name = "alerts/" + file_name
                gcp_thumbnail_path = "alerts/" + thumbnail_path
               
                side_effect_url = self.ftp_uploader.upload_file(local_img_path, file_name)
                gcp_thumbnail_url = self.ftp_uploader.upload_file(local_thumbnail_path, gcp_thumbnail_path, False)
                json_object['mediaURL'] = side_effect_url
                json_object['imagepath'] = gcp_thumbnail_url
                self.mqtt_client.publish(json_object)
            
            #mandatory 10 minutes rec
            #elif is_tenth_minute:
             #   print("5 min rec")
              #  self.frame_count = 0
               # timestamp = datetime.timestamp(datetime.now())
               # timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H_%M_%S')
                #file_name = timestamp_str + ".avi"
                #folder_path = self.data['filePaths']['alertsFolder']
                #local_img_path = folder_path + file_name
                #self.camera.record_video(10, local_img_path)
                
            

        print("\n[INFO] Exiting Program and cleanup stuff")
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = MainApp()
    app.run()
