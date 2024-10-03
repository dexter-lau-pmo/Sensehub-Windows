from google.oauth2 import service_account
from google.cloud import storage
import json
import requests
import constants

class FTPUploader:
    def upload_file(self, local_file_path, file_name, isVideo=True):
        credential_json_path = constants.credential_json_path #"../SettingsPage/GCS_credentials.json"
        
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
            if isVideo:
                blob.upload_from_file(f, content_type='video/mp4')
            else:
                blob.upload_from_file(f, content_type='image/jpeg')
            #blob.upload_from_file(f)
        
        print("Upload complete")
        url = blob.public_url
        print (url)
        #url = blob.generate_signed_url(expiration=3600, method='GET')

        return url

    def download_file(self, url, file_name=None):
        try:
            # Send a GET request to the URL
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Use the file name from the URL if not specified
            if file_name is None:
                file_name = url.split("/")[-1]

            # Write the file in binary mode
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"File downloaded successfully: {file_name}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to download file: {e}")
            return False