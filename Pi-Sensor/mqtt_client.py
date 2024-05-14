import paho.mqtt.client as mqtt
import json

class MQTTClient:
    def __init__(self):
        # Specify the path to your JSON file
        json_file_path = '/home/admin/Pi-Sensor-Hub-with-Facial-Recognition/SettingsPage/UserPrefs.json'

        # Open the JSON file for reading
        with open(json_file_path, 'r') as file:
            # Load the JSON data from the file
            data = json.load(file)
        
        self.broker = data['mqttSettings']['broker']
        self.port = data['mqttSettings']['port']
        self.topic = "/1234/EnvironmentalSensor001/attrs"

        self.client = mqtt.Client()
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect


    def on_publish(self, client, userdata, mid):
        print(f"Message published: {mid}")

    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def publish_json(self, json_object):
        self.client.publish(self.topic, json.dumps(json_object))
        
    def publish_message(self, message):
        self.client.publish(self.topic, message)
        print(message)
        
    def connect(self):
        self.client.connect(self.broker , self.port, 60)
        self.client.loop_start()
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            #added subscribe
            self.client.subscribe("/1234/Robot001/cmd")
            print("Subscribed to /1234/Robot001/cmd")

        else: 
            print("Failed to connect to MQTT broker")
