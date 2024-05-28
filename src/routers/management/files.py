import uuid

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
from src.models.file import File
from src.controllers.files import FileHandler, UnsupportedFileExtensionError

files_router = r = APIRouter()


@r.get("")
def fetch_files(user_id: str) -> list[File]:
    """
    Get the current files.
    """
    return FileHandler.get_current_files(user_id)


@r.post("")
async def add_file(file: UploadFile, user_id: str | None = None):
    """
    Upload a new file.
    """
    # generate user id if it's not set
    if user_id is None:
        user_id = str(uuid.uuid4())
    res = await FileHandler.upload_file(user_id, file, str(file.filename))
    if isinstance(res, UnsupportedFileExtensionError):
        # Return 400 response with message if the file extension is not supported
        return JSONResponse(
            status_code=400,
            content={
                "error": "UnsupportedFileExtensionError",
                "message": str(res),
            },
        )
    return res


@r.delete("/{file_name}")
def remove_file(user_id: str, file_name: str):
    """
    Remove a file.
    """
    try:
        FileHandler.remove_file(user_id, file_name)
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": "FileNotFoundError",
                "message": f"File {file_name} not found.",
            },
        )
    return JSONResponse(
        status_code=200,
        content={"message": f"File {file_name} removed successfully."},
    )
