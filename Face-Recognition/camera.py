import cv2
import json
import time
from urllib.parse import quote
import constants

class Camera:
    def __init__(self):
        self.desired_width = 1280  # Increase width for higher resolution
        self.desired_height = int(self.desired_width * 9 / 16)  # Calculate height for 16:9 aspect ratio
        self.connect()
        
    # Designed to be a blocking function because app serves no purpose without an rtsp connection
    def connect(self):
        # Specify the path to your JSON file
        json_file_path = constants.settings_page_file

        while True:
            try:
                # Open the JSON file for reading
                with open(json_file_path, 'r') as file:
                    # Load the JSON data from the file
                    data = json.load(file)

                rtspAddress = data['rtspSettings']['address']
                user = data['rtspSettings']['user']
                password = data['rtspSettings']['password']
                # Encode the password for URL
                encoded_password = quote(password)
                # RTSP stream URL with encoded password
                rtsp_url = f'rtsp://{user}:{encoded_password}@{rtspAddress}'
                print(rtsp_url)
                self.cam = cv2.VideoCapture(rtsp_url)
                self.set_properties()
                print("RTSP Connection successful")
                break
            except Exception as e:
                print(f"RTSP Connection failed. Error: {e}")
                print("Attempting to reconnect in 5 seconds...")
                time.sleep(5)


    #Read in next frame from RTSP
    def read_frame(self):
        for attempt in range(3):  # Try reading up to 3 times before giving up
            ret, img = self.cam.read()
            if ret and img is not None:
                try:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    return img, gray
                except cv2.error as e:
                    print(f"Error processing frame: {e}")
                    continue  # Skip to the next iteration
            else:
                print("Failed to read frame from camera.")
        
        # If failed to read after retries
        print("Invalid Frame after multiple attempts")
        return None, None

        
    def release(self):
        self.cam.release()

    def record_video(self, duration, file_path, first_frame_path):
        if not (self.is_connection_active()):
            self.reconnect()
            return
        
        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')  
        out = cv2.VideoWriter(file_path, fourcc, 10.0, (self.desired_width, self.desired_height))
        
        # Get current time
        start_time = cv2.getTickCount()
        
        first_run = True #save first frame for thumbnail purposes
        
        while True:
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed_time >= duration:
                break
            # Read a frame from the camera/video file
            img_frame, gray_frame = self.read_frame()
            resize_frame = cv2.resize(img_frame,(self.desired_width, self.desired_height))
            
            # Write the frame to the video file
            out.write(resize_frame)
            
            if first_run:
                cv2.imwrite(first_frame_path, resize_frame)
                
            first_run = False
        
        out.release()
        
    def reconnect(self):
        self.release()
        self.connect()
        
    def is_connection_active(self):
        try:
            # Try to read a frame
            ret, _ = self.cam.read()
            return ret
        except Exception as e:
            print(f"Error checking RTSP connection: {e}")
            return False
            
    def set_properties(self):

        self.cam.set(cv2.CAP_PROP_FPS, 25)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.desired_width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.desired_height)
        self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 10)

        
    def get_min_face_size(self):
        # Define min window size to be recognized as a face
        minW = 0.1 * self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        minH = 0.1 * self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return minW, minH


