import sys
from ingestion_engine.ingestion import *
from langchain.chains import RetrievalQAWithSourcesChain, ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.memory import ConversationBufferMemory
from tqdm.auto import tqdm
from constants import OPENAPI_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME
from langchain.llms import OpenAI
from pinecone import Pinecone
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
import os
from openai import OpenAI as OpenAIClient
from langchain.schema import Document
 

## Intialize pinecone and ChatGPT objects which are accessed in the future
def intialize_dependencies():
    model_name = 'text-embedding-3-small'
    pc = Pinecone(api_key=PINECONE_API_KEY)

    class SimpleOpenAIEmbeddings:
        def __init__(self, api_key: str, model: str):
            self.client = OpenAIClient(api_key=api_key)
            self.model = model
            self.target_dim = 1024
        def embed_query(self, text: str):
            response = self.client.embeddings.create(model=self.model, input=text)
            vec = response.data[0].embedding
            if len(vec) > self.target_dim:
                return vec[:self.target_dim]
            if len(vec) < self.target_dim:
                return vec + [0.0] * (self.target_dim - len(vec))
            return vec
        def embed_documents(self, texts):
            response = self.client.embeddings.create(model=self.model, input=texts)
            out = []
            for d in response.data:
                vec = d.embedding
                if len(vec) > self.target_dim:
                    out.append(vec[:self.target_dim])
                elif len(vec) < self.target_dim:
                    out.append(vec + [0.0] * (self.target_dim - len(vec)))
                else:
                    out.append(vec)
            return out

    embed = SimpleOpenAIEmbeddings(api_key=OPENAPI_KEY, model=model_name)

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

    class SimplePineconeVectorStore:
        def __init__(self, index, embed_query_fn):
            self._index = index
            self._embed_query_fn = embed_query_fn
        def similarity_search(self, query: str, k: int = 4):
            query_vec = self._embed_query_fn(query)
            res = self._index.query(vector=query_vec, top_k=k, include_metadata=True)
            matches = getattr(res, 'matches', []) or res.get('matches', [])
            docs = []
            for m in matches:
                md = m.get('metadata') if isinstance(m, dict) else getattr(m, 'metadata', {})
                page_text = (md or {}).get('text', '')
                docs.append(Document(page_content=page_text, metadata=md or {}))
            return docs
        def as_retriever(self, k: int = 4):
            store = self
            class _Retriever:
                def get_relevant_documents(self, query: str):
                    return store.similarity_search(query, k=k)
            return _Retriever()

    vectorstore = SimplePineconeVectorStore(index, embed.embed_query)
    # Lazy import to avoid importing ChatOpenAI when only ingesting
    # Use OpenAI v2 client directly to avoid legacy openai.error in old LangChain wrappers
    llm_client = OpenAIClient(api_key=OPENAPI_KEY)
    return (vectorstore, llm_client)

#Performs the similarity search and inputs query into OPENAI, then is formatted and outputted
def query_embeddings(query, vectorstore, llm):
    docs = vectorstore.similarity_search(query=query, k=20)
    # Prepare context from retrieved docs
    context_chunks = []
    sources = []
    for d in docs:
        context_chunks.append(d.page_content)
        src = d.metadata.get('source') if isinstance(d.metadata, dict) else None
        if src:
            sources.append(str(src))
    context_text = "\n\n".join(context_chunks)

    # Call OpenAI chat completions directly
    completion = llm.chat.completions.create(
        model='gpt-4o-mini',
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer using only the provided context. If unsure, say you don't know."},
            {"role": "user", "content": f"Question:\n{query}\n\nContext:\n{context_text}"}
        ]
    )
    answer = completion.choices[0].message.content if completion and completion.choices else ""
    out = {"answer": answer, "sources": ", ".join(sources)}
    format_query(out)

#Formats the query and prints it to the terminal
def format_query(query):
    print('\n')
    print(str(query["answer"]))
    print('\n')
    print("Sources: " + str(query["sources"]))

#Allows looping of commands in Command Line Interface
def terminal_query(vectorstore, llm):
    print("Paste your question. Submit with an empty line. Type 'exit' on a single line to quit.")
    while True:
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                line = ''
            if line.strip().lower() == 'exit' and len(lines) == 0:
                return
            if line == '':
                break
            lines.append(line)
        query = "\n".join(lines).strip()
        if not query:
            continue
        query_embeddings(query, vectorstore, llm)

#ArgV Parser
def parse_argv(argv):
    VERBOSE = True  if "-v" in argv else False
    NEW_DATA = True if "-n" in argv else False

    return VERBOSE, NEW_DATA

#self explanatory
def main(argv):
    VERBOSE, NEW_DATA = parse_argv(argv)

    if NEW_DATA:
        #loader = DirectoryLoader(os.path.join(os.getcwd(), 'data'), show_progress=True, loader_cls=UnstructuredFileLoader, loader_kwargs={'mode': "single", 'post_processors': [clean_extra_whitespace]} )
        loader = DirectoryLoader(os.path.join(os.getcwd(), 'data'), glob="*.pdf", show_progress=True, loader_cls=PyPDFLoader)
        
        data = loader.load() #Data is an an array of Document objects with each object having a page_content and metadata
        #print(data)
        initalize_embeddings(data, VERBOSE)
        print("Ingestion complete.")
        return

    vectorstore, llm = intialize_dependencies()
    terminal_query(vectorstore, llm)

if __name__ == "__main__":
    argv = sys.argv
    main(argv)