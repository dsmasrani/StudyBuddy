import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import OPENAPI_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
from pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, OnlinePDFLoader
import tiktoken
from uuid import uuid4
from tqdm.auto import tqdm
import hashlib
from openai import OpenAI
from pinecone import ServerlessSpec
#from docx2pdf import convert

#Batch limit of upload size (can go upto 1000)
batch_limit = 100

#Helper function to calculae length of TOKENS not characters
def tiktoken_len(text):
    tiktoken.encoding_for_model('gpt-4o-mini')
    tokenizer = tiktoken.get_encoding('o200k_base')

    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

#Splits each chunk of text by token length to help ChatGPT
def text_splitter():
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter

#Compute Hash
def compute_md5(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

#Intializes the pinecone index and uploads the embeddings
##TODO: Split this function to improve readability
def initalize_embeddings(data, VERBOSE):
    texts = []
    metadatas = []
    model_name = 'text-embedding-3-small'
    openai_client = OpenAI(api_key=OPENAPI_KEY)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    # Validate index dimension matches embedding dimension
    try:
        desc = pc.describe_index(PINECONE_INDEX_NAME)
        index_dim = desc.get('dimension') if isinstance(desc, dict) else getattr(desc, 'dimension', None)
    except Exception:
        index_dim = None
    embedding_dim = 1024
    if index_dim is not None and index_dim != embedding_dim:
        raise RuntimeError(f"Pinecone index '{PINECONE_INDEX_NAME}' has dimension {index_dim}, but model '{model_name}' outputs {embedding_dim}. Recreate the index with dimension {embedding_dim} or change model.")
    
    print(index.describe_index_stats()) if VERBOSE else None
    txt_splitter = text_splitter()
    texts = []
    metadatas = []
    for i, document in enumerate(tqdm(data)): #For each page in the document
        metadata = {
            'source': document.metadata['source'],
            'page': document.metadata['page'] + 1,}
        record_texts = txt_splitter.split_text(document.page_content)
        record_metadatas = [{
            "chunk": j, "text": chunk, 'source': (document.metadata['source'].split('/')[-1] + ' Page: ' + str(document.metadata['page'])) 
        } for j, chunk in enumerate(record_texts)] #Each page will be associated with a metadata

        texts.extend(record_texts)
        metadatas.extend(record_metadatas)
    for i in tqdm(range(0, len(texts), batch_limit)):
        text_tmp = texts[i:i + batch_limit]
        metadata_tmp = metadatas[i:i + batch_limit]
        ids = [compute_md5(text_tmp[j]) for j in range(len(text_tmp))]

        # Create embeddings using OpenAI v2 client
        response = openai_client.embeddings.create(
            model=model_name,
            input=text_tmp
        )
        raw_embeds = [item.embedding for item in response.data]
        def to_target_dim(vec, target):
            if len(vec) == target:
                return vec
            if len(vec) > target:
                return vec[:target]
            return vec + [0.0] * (target - len(vec))
        embeds = [to_target_dim(e, embedding_dim) for e in raw_embeds]

        # Upsert using Pinecone v3 vectors format
        vectors = [
            {
                "id": ids[j],
                "values": embeds[j],
                "metadata": metadata_tmp[j]
            }
            for j in range(len(text_tmp))
        ]
        index.upsert(vectors=vectors)