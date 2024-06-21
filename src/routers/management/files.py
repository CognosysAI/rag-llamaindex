import uuid
import aiohttp
import io

from fastapi import Request, APIRouter, UploadFile, Query
from fastapi.responses import JSONResponse
from src.models.file import File
from src.controllers.files import FileHandler, UnsupportedFileExtensionError

files_router = r = APIRouter()


@r.get("")
def fetch_files(
    user_id: str,
    bucket_name: str = Query(..., description="GCS bucket name"),
    gcs_prefix: str = Query(..., description="GCS prefix/directory")
):
    return FileHandler.get_current_files(user_id, bucket_name, gcs_prefix)

@r.post("")
async def add_file(
    user_id: str,
    file_name: str,
    bucket_name: str = Query(..., description="GCS bucket name"),
    gcs_prefix: str = Query(..., description="GCS prefix/directory")
):
    res = await FileHandler.upload_file(user_id, bucket_name, gcs_prefix, file_name)
    if isinstance(res, FileNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "FileNotFoundError",
                "message": str(res),
            },
        )
    return res

@r.delete("/{file_name}")
def remove_file(
    user_id: str,
    file_name: str,
    bucket_name: str = Query(..., description="GCS bucket name"),
    gcs_prefix: str = Query(..., description="GCS prefix/directory")
):
    FileHandler.remove_file(user_id, bucket_name, gcs_prefix, file_name)
    return JSONResponse(
        status_code=200,
        content={"message": f"File {file_name} removed from index successfully."},
    )
