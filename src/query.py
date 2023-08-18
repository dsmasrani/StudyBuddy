import sys
from ingestion_engine.ingestion import *
from langchain.chains import RetrievalQAWithSourcesChain
from tqdm.auto import tqdm
from constants import OPENAPI_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
import pinecone
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
import os
 

## Intialize pinecone and ChatGPT objects which are accessed in the future
def intialize_dependencies():
    model_name = 'text-embedding-ada-002'
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT,
    )

    embed = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=OPENAPI_KEY
    )

    index = pinecone.Index(PINECONE_INDEX_NAME)
    vectorstore = Pinecone(index, embed.embed_query, "text")

    llm = ChatOpenAI(
    openai_api_key=OPENAPI_KEY,
    model_name='gpt-3.5-turbo',
    temperature=0.7
    )
    return (vectorstore, llm)

#Performs the similarity search and inputs query into OPENAI, then is formatted and outputted
def query_embeddings(query, vectorstore, llm):

    vectorstore.similarity_search(
        query=query,
        k=20,
    )

    #qa = RetrievalQA.from_chain_type(
    #llm=llm,
    #chain_type="stuff",
    #retriever=vectorstore.as_retriever()
    #)
    #print(qa.run(query))
    qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    format_query(qa_with_sources(query))

#Formats the query and prints it to the terminal
def format_query(query):
    print('\n')
    print(str(query["answer"]))
    print('\n')
    print("Sources: " + str(query["sources"]))

#Allows looping of commands in Command Line Interface
def terminal_query(vectorstore, llm):
    print("Input a query (type exit to exit)")
    query = input()
    while query.lower() != 'exit':
        query_embeddings(query, vectorstore, llm)
        print("Input a query (type exit to exit)")
        query = input()

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
        loader = DirectoryLoader(os.path.join(os.getcwd(), 'data'), show_progress=True, loader_cls=PyPDFLoader)
        
        data = loader.load() #Data is an an array of Document objects with each object having a page_content and metadata
        #print(data)
        initalize_embeddings(data, VERBOSE)

    vectorstore, llm = intialize_dependencies()

    terminal_query(vectorstore, llm)

if __name__ == "__main__":
    argv = sys.argv
    main(argv)