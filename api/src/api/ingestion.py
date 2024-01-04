from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.src.api import auth
import sqlalchemy
from api.src import database as db
import httpx
import os
import dotenv


router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(auth.get_api_key)],
)    


@router.get("/retrieve_files")
async def retrieve_embeddings():
    """"""
    dotenv.load_dotenv()
    key=str(os.environ.get("PROJECT_KEY"))
    url=str(os.environ.get("PROJECT_URL"))
    print(key)
    print(url)
    print(f"Bearer {key}")
    curl = f"{url}/storage/v1/object/list/files"
    print(curl)
    headers = {
        "authorization": f"Bearer {key}"
    }
    data = {
        "prefix": "", 
        "limit": 100  
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(curl, json=data, headers=headers)

    #if response.status_code != 200:
    #   raise HTTPException(status_code=response.status_code, detail="Error listing bucket files")

    file_list = response.json()
    print(file_list)

    return {"message": "Ingestion initialized successfully"}
    
    
@router.post("/upload_embeddings")
def upload_embeddings():
    """ """
  
    return 