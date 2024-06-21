import os
import logging
from llama_parse import LlamaParse
from pydantic import BaseModel, validator
from src.controllers.gcs_storage import GCSStorage

logger = logging.getLogger(__name__)


class FileLoaderConfig(BaseModel):
    data_dir: str = "data"
    use_llama_parse: bool = False
    gcs_prefix: str

    @validator("data_dir")
    def data_dir_must_exist(cls, v):
        if not os.path.isdir(v):
            raise ValueError(f"Directory '{v}' does not exist")
        return v


def llama_parse_parser():
    if os.getenv("LLAMA_CLOUD_API_KEY") is None:
        raise ValueError(
            "LLAMA_CLOUD_API_KEY environment variable is not set. "
            "Please set it in .env file or in your shell environment then run again!"
        )
    parser = LlamaParse(result_type="markdown", verbose=True, language="en")
    return parser


def get_file_documents(user_id: str, config: FileLoaderConfig):
    from llama_index.core.readers import SimpleDirectoryReader
    
    gcs = GCSStorage(config.bucket_name)
    temp_dir = f"/tmp/{user_id}"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        files = gcs.list_files(prefix=f"{config.gcs_prefix}/{user_id}")
        for file in files:
            gcs.download_file(file, f"{temp_dir}/{os.path.basename(file)}")

        reader = SimpleDirectoryReader(
            temp_dir,
            recursive=True,
            filename_as_id=True,
        )
        if config.use_llama_parse:
            parser = llama_parse_parser()
            reader.file_extractor = {".pdf": parser}
        
        documents = reader.load_data()

        # Clean up temporary files
        for file in os.listdir(temp_dir):
            os.remove(f"{temp_dir}/{file}")
        os.rmdir(temp_dir)

        return documents
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
        return []
