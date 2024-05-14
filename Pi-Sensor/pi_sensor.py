from sense_hat import SenseHat
from mqtt_client import MQTTClient
from threading import Timer
import time
import json



class PiSensor:
    def __init__(self):
        self.sense = SenseHat()
        self.mqtt_client = MQTTClient()
        self.mqtt_client.client.on_message = self.on_message
        self.mqtt_client.client.subscribe("/1234/Robot001/cmd/x1")
        self.mqtt_client.connect()
        self.rising_edge = True #Flag so that alarm can only be triggered once every heart beat
        self.threshold = 45

        
    def run(self):
        self.start_heartbeat_data_routine()
        self.start_temperature_data_routine()
        
    def on_message(self, client, userdata, message):
        
        received_message = message.payload.decode()
        print(received_message)

        if "x1" in received_message:
            payload = {
                "temperature" : self.sense.get_temperature_from_humidity(),
                "humidity" : self.sense.get_humidity(),
                "bearing" : self.sense.get_compass(),
                "pressure" : self.sense.get_pressure(),
                "gyroscope" : self.sense.get_gyroscope(),
                "accelerometer" : self.sense.get_accelerometer()
            }
            # Publish MQTT
            self.mqtt_client.publish_json(payload)    
            print("Triggered message by backend")
            
            message_data = json.loads(received_message)
            x1_value = message_data["x1"]
            print("Value of x1:", x1_value)
            if x1_value.isnumeric():
                self.threshold = float(x1_value)
                print("threshold updated")

        
        

    def start_heartbeat_data_routine(self):
        Timer(300,self.start_heartbeat_data_routine,[]).start()
        
        payload = {
            "temperature" : self.sense.get_temperature_from_humidity(),
            "humidity" : self.sense.get_humidity(),
            "bearing" : self.sense.get_compass(),
            "pressure" : self.sense.get_pressure(),
            "gyroscope" : self.sense.get_gyroscope(),
            "accelerometer" : self.sense.get_accelerometer()
        }
        print(self.sense.get_gyroscope())
        # Publish MQTT
        self.mqtt_client.publish_json(payload)
        self.rising_edge = True #Reset, so can alarm again
  
        
    def start_temperature_data_routine(self):
        Timer(5,self.start_temperature_data_routine,[]).start()
        
        # Temperature Sensor
        temp_H = self.sense.get_temperature_from_humidity()
        temp_P = self.sense.get_temperature_from_pressure()
        
        if temp_H > self.threshold and self.rising_edge == True:
            payload = {
                "temperature" : self.sense.get_temperature_from_humidity()
            }
            # Publish MQTT
            self.mqtt_client.publish_json(payload)
            print("Threshold reached")
            self.rising_edge = False #set to false, so cannot re trigger again till next heartbeat
            
if __name__ == "__main__":
    app = PiSensor()
    app.run()
