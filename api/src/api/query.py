from fastapi import APIRouter, Depends, HTTPException
from api.src.api import auth
import sqlalchemy
from api.src import database as db
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
import logging
from supabase import create_client, Client

router = APIRouter(
    prefix="/query",
    tags=["query"],
    dependencies=[Depends(auth.get_api_key)],
)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@router.get("/list_bucket")
def list_bucket(url: str, key: str):
    """"""
    url: url
    key: key
    supabase: Client = create_client(url, key)
    res = supabase.storage.list_buckets()  
    # Handling the response
    print(res)
    #if res.error:
    #    print("Error:", res.error)
    #else:
    #    for bucket in res.data:
    #        print("Bucket ID:", bucket.id, "Bucket Name:", bucket.name)
 
    return res

@router.get("/query")
def query(question: str, user_email: str):
    """"""
    with db.engine.begin() as connection:
        user_keys_query = sqlalchemy.text("SELECT * FROM user_keys WHERE user_email = :user_email")

        user_keys_result = connection.execute(user_keys_query, {'user_email': user_email}).fetchone()
        #print(user_keys_result)

        if not user_keys_result:
            logging.error("Invalid Credentials. Please check your email and try again.")
            raise HTTPException(400, "Invalid Credentials. Please check your email and try again.")

        pinecone_key = user_keys_result.pinecone_key
        pinecone_env = user_keys_result.pinecone_env
        index_name = user_keys_result.index_name
        openai_key = user_keys_result.openai_key

        logging.debug("Credentials retrieved successfully")
        logging.debug("Pinecone Key: %s, Pinecone Env: %s, Index Name: %s, OpenAI Key: %s", pinecone_key, pinecone_env, index_name, openai_key)
        vectorstore, llm  = intialize_dependencies(pinecone_key, pinecone_env, index_name, openai_key)
        logging.debug("Dependencies initialized successfully")
        out = query_embeddings(question, vectorstore, llm)
    return out
    
@router.post("/query_embeddings")
def query_embeddings():
    """"""

    return 

## Intialize pinecone and ChatGPT objects which are accessed in the future
def intialize_dependencies(pinecone_key, pinecone_env, index_name, openai_key):
    model_name = 'text-embedding-ada-002'
    pinecone.init(
        api_key=pinecone_key,
        environment=pinecone_env,
    )

    embed = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=openai_key
    )

    index = pinecone.Index(index_name)
    vectorstore = Pinecone(index, embed.embed_query, "text")
    llm = ChatOpenAI(
    openai_api_key=openai_key,
    model_name='gpt-4',
    temperature=0.7
    )
    return (vectorstore, llm)

def query_embeddings(query, vectorstore, llm):

    vectorstore.similarity_search(
        query=query,
        k=20,
    )

    logging.debug("Querying OpenAI...")
    qa_with_sources = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
    )
    q = qa_with_sources(query)
    print(q)
    return format_query(q)

def format_query(query):
    out = {}
    out["answer"] = str(query["answer"])
    out["sources"] = str(query["sources"])
    return out