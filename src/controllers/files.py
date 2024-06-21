import os
from src.tasks.indexing import index_all, reset_index
from src.models.file import File, FileStatus, SUPPORTED_FILE_EXTENSIONS

from src.controllers.gcs_storage import GCSStorage


class UnsupportedFileExtensionError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class FileHandler:

    @classmethod
    def get_current_files(cls, user_id: str, bucket_name: str, gcs_prefix: str):
        gcs = GCSStorage(bucket_name)
        return [
            File(user_id=user_id, name=file_name, status=FileStatus.UPLOADED)
            for file_name in gcs.list_files(prefix=f"{gcs_prefix}/{user_id}")
        ]

    @classmethod
    async def upload_file(cls, user_id: str, bucket_name: str, gcs_prefix: str, file_name: str):
        gcs = GCSStorage(bucket_name)
        full_path = f"{gcs_prefix}/{user_id}/{file_name}"
        
        # Check if the file exists in GCS
        if full_path not in gcs.list_files(prefix=f"{gcs_prefix}/{user_id}"):
            return FileNotFoundError(f"File {file_name} not found in GCS.")

        # We don't actually download the file here, just verify its existence
        return File(user_id=user_id, name=file_name, status=FileStatus.UPLOADED)

    @classmethod
    def remove_file(cls, user_id: str, bucket_name: str, gcs_prefix: str, file_name: str):
        # In this case, we're not actually removing the file from GCS
        # Just removing it from our index
        reset_index(user_id)
