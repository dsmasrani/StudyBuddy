from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/query",
    tags=["query"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/initialize")
def initialize_dependencies():
    """"""

    return 
    
@router.post("/query_embeddings")
def query_embeddings():
    """"""
    
    return 
