from sense_hat import SenseHat
from mqtt_client import MQTTClient
from threading import Timer


class PiSensor:
    def __init__(self):
        self.sense = SenseHat()
        self.mqtt_client = MQTTClient()
        
    def run(self):
        self.start_heartbeat_data_routine()
        self.start_temperature_data_routine()
        

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
  
        
    def start_temperature_data_routine(self):
        Timer(5,self.start_temperature_data_routine,[]).start()
        
        # Temperature Sensor
        temp_H = self.sense.get_temperature_from_humidity()
        temp_P = self.sense.get_temperature_from_pressure()
        
        if temp_H > 30 or temp_P > 30:
        payload = {
            "temperature" : self.sense.get_temperature_from_humidity()
        }
        # Publish MQTT
        self.mqtt_client.publish_json(payload)
            
if __name__ == "__main__":
    app = PiSensor()
    app.run()
