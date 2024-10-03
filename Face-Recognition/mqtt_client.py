import paho.mqtt.client as mqtt
import json
import os
import constants

camer_id_topic = "/1234/Camera001/attrs"

class MQTTClient:
    def __init__(self):
        self.connect()
        self.client.loop_start()
        self.update_trainer = False
        self.url = ""
        self.url_json = ""

    def on_publish(self, client, userdata, mid):
        print("Message published: ", mid)

    def on_message(self, client, userdata, message):
        print(f"Message received on topic {message.topic}: {message.payload.decode('utf-8')}")
        
        # Check if the topic is /download/trainer => Download file if yes
        if message.topic == "/download/trainer":
            try:
                # Attempt to parse the payload as JSON
                payload = json.loads(message.payload.decode('utf-8'))
                
                # Check if the 'trainer' key is in the payload
                if 'trainer' in payload:
                    self.update_trainer = True
                    self.url = payload['trainer']  # Set self.url to the value of the trainer parameter
                    self.url_json = payload['json']
                    print(f"Set download new file to True. Trainer URL: {self.url}")
                else:
                    print("Trainer parameter not found in the payload")
            except json.JSONDecodeError:
                print("Payload is not valid JSON")

    def publish(self, json_object):
        ret = self.client.publish(self.topic, json.dumps(json_object))
        print(json.dumps(json_object))
        print("Paho ret ", ret)

    def custom_topic_publish (self, json_object , custom_topic):
        ret = self.client.publish(custom_topic, json.dumps(json_object))
        print(json.dumps(json_object))
        print("Paho ret ", ret)

    def reconnect(self):
        self.client.disconnect()
        self.connect()

    def is_connection_active(self):
        return self.client.is_connected()

    def connect(self):
        # Specify the path to your JSON file
        #json_file_path = '/home/admin/Pi-Sensor-Hub-with-Facial-Recognition/SettingsPage/UserPrefs.json'
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #json_file_path = os.path.normpath(os.path.join(script_dir, '..', 'SettingsPage', 'UserPrefs.json'))
        json_file_path = constants.settings_page_file
        print(json_file_path)

        # Open the JSON file for reading
        with open(json_file_path, 'r') as file:
            # Load the JSON data from the file
            data = json.load(file)

        broker = data['mqttSettings']['broker']
        port = data['mqttSettings']['port']
        #self.topic = "/1234/Camera001/attrs"
        #Topic name is "/1234/Camera001/attrs"
        self.topic = camer_id_topic
        
        self.client = mqtt.Client()

        # Register event handlers
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message  # Add on_message callback

        # Connect to the broker
        self.client.connect(broker, port, 60)

        # Subscribe to the /download/trainer topic
        self.client.subscribe("/download/trainer")

