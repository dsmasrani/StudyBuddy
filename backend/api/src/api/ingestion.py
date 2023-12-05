from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(auth.get_api_key)],
)    


@router.get("/initialize_embeddings")
def initialize_embeddings():
    """"""
    return
    
    
@router.post("/upload_embeddings")
def upload_embeddings():
    """ """
  
    return 