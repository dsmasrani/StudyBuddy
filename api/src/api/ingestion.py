from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.src.api import auth
import sqlalchemy
from api.src import database as db
import httpx
import os
import dotenv
import os
from supabase import create_client, Client

url: str = os.environ.get("PROJECT_URL")
key: str = os.environ.get("PROJECT_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(auth.get_api_key)],
)    


@router.get("/retrieve_files")
def retrieve_embeddings():
    """"""
    res = supabase.storage.from_('files').list()
    return res
    
    
@router.post("/upload_embeddings")
def upload_embeddings():
    """ """
  
    return 