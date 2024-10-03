from google.oauth2 import service_account
from google.cloud import storage
import json
import time
from mqtt_client import MQTTClient
import constants


class FTPUploader_generic:
    def upload_file(self, local_file_path, file_name):
        credential_json_path = constants.credential_json_path
        
        # Create credentials from the service account JSON file
        creds = service_account.Credentials.from_service_account_file(credential_json_path)

        # Initialize the storage client with the credentials
        storage_client = storage.Client(credentials=creds)

        # Get the bucket
        bucket = storage_client.get_bucket("ngsi-ld")
        #bucket = storage_client.get_bucket("sndgo_scd")

        # Create a blob object
        blob = bucket.blob(file_name)
        
        # Upload the file
        with open(local_file_path, 'rb') as f:
            blob.upload_from_file(f)
        
        print("Upload complete")
        url = blob.public_url
        print (url)
        #url = blob.generate_signed_url(expiration=3600, method='GET')

        return url

print("Uploading trained Model")

local_path = constants.trainer_file
destination_file_name = "trainer.yml"
json_path = constants.id_to_names_file
destination_json_name = "name_to_id.json"
custom_topic = "/download/trainer"

ftp_uploader = FTPUploader_generic()
url = ftp_uploader.upload_file(local_path , destination_file_name)
json_url = ftp_uploader.upload_file(json_path, destination_json_name)
print("Uploaded")
print("Sending MQTT message")

client = MQTTClient()
message ={
    "trainer": url,
    "json": json_url
}

client.client.subscribe("/download/response")
client.custom_topic_publish(message, custom_topic)

print("Mqtt msessage sent")
print("\n")
# Sleep for 8 seconds
time.sleep(40)

# Optionally stop the client loop (if needed)
client.client.loop_stop()