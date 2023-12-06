from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.api.src.api import auth
import sqlalchemy
from backend.api.src import database as db


router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(auth.get_api_key)],
)    


@router.get("/initialize_embeddings")
def initialize_embeddings(file_id: int, user_id: str):
    """"""
    with db.engine.begin() as connection:
        user_keys_query = sqlalchemy.text("SELECT * FROM user_keys WHERE user_id = :user_id")
        file_info_query = sqlalchemy.text("SELECT * FROM files WHERE id = :file_id")

        user_keys_result = connection.execute(user_keys_query, {'user_id': user_id}).fetchone()
        file_info_result = connection.execute(file_info_query, {'file_id': file_id}).fetchone()
        print(user_keys_result)
        print(file_info_result)

        if not user_keys_result or not file_info_result:
            return "User keys or file not found"

        pinecone_key = user_keys_result.pinecone_key
        openai_key = user_keys_result.openai_key

        # run_ingestion(file_info, pinecone_key, openai_key)

    return {"message": "Ingestion initialized successfully"}
    
    
@router.post("/upload_embeddings")
def upload_embeddings():
    """ """
  
    return 