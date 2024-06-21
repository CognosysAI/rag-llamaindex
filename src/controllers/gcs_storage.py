from google.cloud import storage
from google.oauth2 import service_account
import os

class GCSStorage:
    def __init__(self, bucket_name, credentials_path=None):
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = storage.Client(credentials=credentials)
        else:
            self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def list_files(self, prefix=None):
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    def download_file(self, file_name, destination):
        blob = self.bucket.blob(file_name)
        blob.download_to_filename(destination)