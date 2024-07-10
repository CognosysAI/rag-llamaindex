import os
from src.tasks.indexing import index_all, reset_index
from src.models.file import File, FileStatus, SUPPORTED_FILE_EXTENSIONS


class UnsupportedFileExtensionError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class FileHandler:

    @classmethod
    def get_current_files(cls, user_id: str):
        """
        Construct the list files by all the files in the data folder.
        """
        user_data_folder = f"data/{user_id}"
        if not os.path.exists(user_data_folder):
            return []
        # Get all files in the data folder
        file_names = os.listdir(user_data_folder)
        # Construct list[File]
        return [
            File(user_id=user_id, name=file_name, status=FileStatus.UPLOADED) 
            for file_name in file_names
        ]

    @classmethod
    async def upload_file(
        cls, user_id: str, file, file_name: str
    ) -> File | UnsupportedFileExtensionError:
        """
        Upload a file to the data folder.
        """
        # Check if the file extension is supported
        if file_name.split(".")[-1] not in SUPPORTED_FILE_EXTENSIONS:
            return UnsupportedFileExtensionError(
                f"File {file_name} with extension {file_name.split('.')[-1]} is not supported."
            )
        # Create data folder if it does not exist
        user_data_folder = f"data/{user_id}"
        if not os.path.exists(user_data_folder):
            os.makedirs(user_data_folder)

        file_content = file if isinstance(file, bytes) else await file.read()
        with open(f"{user_data_folder}/{file_name}", "wb") as f:
            f.write(file_content)
        # Index the data
        index_all(user_id)
        return File(user_id=user_id, name=file_name, status=FileStatus.UPLOADED)

    @classmethod
    def remove_file(cls, user_id: str, file_name: str) -> None:
        """
        Remove a file from the data folder.
        """
        user_data_folder = f"data/{user_id}"
        os.remove(f"{user_data_folder}/{file_name}")
        # Re-index the data
        # index_all(user_id)

        # reset the index for the given context
        reset_index(user_id)
