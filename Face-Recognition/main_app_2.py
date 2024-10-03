from mqtt_client import MQTTClient
from ftp_uploader import FTPUploader
from camera import Camera
import cv2
import json
from datetime import datetime
import os
import constants

class MainApp2:
    def __init__(self):
        # Specify the path to your JSON file
        #json_file_path = '/home/admin/Pi-Sensor-Hub-with-Facial-Recognition/SettingsPage/UserPrefs.json'

        # Construct the path relative to the script's directory, use absolute path if does not work     
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #json_file_path = os.path.normpath(os.path.join(script_dir, '..', 'SettingsPage', 'UserPrefs.json'))
        json_file_path = constants.settings_page_file
        
        
        # Open the JSON file for reading
        with open(json_file_path, 'r') as file:
            # Load the JSON data from the file
            self.data = json.load(file)
            
        self.mqtt_client = MQTTClient()
        self.ftp_uploader = FTPUploader()
        self.camera = Camera()
        self.frame_count = 0

    def run(self):
        while True:
            img, gray = self.camera.read_frame()
            
            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break

            timestamp = datetime.timestamp(datetime.now())
            timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H_%M_%S')
            #file_name =  timestamp_str + ".avi"
            file_name =  timestamp_str + ".mp4"
            thumbnail_path = timestamp_str + ".jpg"
            local_img_path = self.data['filePaths']['snapshotFolder'] + file_name
            local_thumbnail_path = self.data['filePaths']['snapshotFolder'] + thumbnail_path
            
            self.camera.record_video(80, local_img_path, local_thumbnail_path)
            file_name = "snapshots/" + file_name
            gcp_thumbnail_path = "snapshots/" + thumbnail_path
            side_effect_url = self.ftp_uploader.upload_file(local_img_path, file_name)
            gcp_thumbnail_url = self.ftp_uploader.upload_file(local_thumbnail_path, gcp_thumbnail_path, False)
            print("Create JSON")
            message = {
                "timestamp": timestamp_str,
                "filename": file_name,
                "imagepath": gcp_thumbnail_url,
                "mediaURL": side_effect_url
            }
            self.mqtt_client.publish(message)
            print("MQTT msg publish called")
                
            

        print("\n[INFO] Exiting Program and cleanup stuff")
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = MainApp2()
    app.run()
