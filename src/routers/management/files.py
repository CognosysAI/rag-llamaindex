import uuid
import aiohttp
import io

from fastapi import Request, APIRouter, UploadFile
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
async def add_file(request: Request, file: UploadFile | None = None, user_id: str | None = None):
    """
    Upload a new file.
    """
    # generate user id if it's not set
    if user_id is None:
        user_id = str(uuid.uuid4())
    
    body = await request.json()
    url = body.get("url")
    fileName = body.get("fileName")

    if file is not None and url is not None:
        return JSONResponse(
            status_code=400,
            content={
                "error": "InvalidRequest",
                "message": "Only one of 'file' or 'url' can be provided.",
            },
        )
    elif file is not None:
        # File upload via form data
        res = await FileHandler.upload_file(user_id, file, str(file.filename))
    elif url is not None:
        # File upload via GCP signed URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Read the file content
                    file_content = await response.read()
                    res = await FileHandler.upload_file(user_id, file_content, fileName)
                        
                else:
                    return JSONResponse(
                        status_code=response.status,
                        content={
                            "error": "FileDownloadError",
                            "message": "Failed to download the file from the provided URL.",
                        },
                    )
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
