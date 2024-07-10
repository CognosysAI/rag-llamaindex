import os
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb.config import Settings


def get_vector_store(user_id: str):
    collection_name = f"{os.getenv('CHROMA_COLLECTION', 'default')}_{user_id}"
    chroma_path = os.getenv("CHROMA_PATH")

    chroma_settings = Settings(anonymized_telemetry=False, chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider", chroma_client_auth_credentials=os.getenv("CHROMA_AUTH_TOKEN"))

    # if CHROMA_PATH is set, use a local ChromaVectorStore from the path
    # otherwise, use a remote ChromaVectorStore (ChromaDB Cloud is not supported yet)
    if chroma_path:
        store = ChromaVectorStore.from_params(
            persist_dir=chroma_path, collection_name=collection_name
        )
    else:
        if not os.getenv("CHROMA_HOST") or not os.getenv("CHROMA_PORT"):
            raise ValueError(
                "Please provide either CHROMA_PATH or CHROMA_HOST and CHROMA_PORT"
            )
        chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=int(os.getenv("CHROMA_PORT")), settings=chroma_settings)
        chroma_collection = chroma_client.get_or_create_collection(collection_name)
        store = ChromaVectorStore(chroma_collection=chroma_collection)
    return store
