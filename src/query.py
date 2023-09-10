import sys
from ingestion_engine.ingestion import *
from langchain.chains import RetrievalQAWithSourcesChain, ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.memory import ConversationBufferMemory
from tqdm.auto import tqdm
from constants import OPENAPI_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
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
    memory = ConversationBufferMemory(memory_key="chat_history", input_key='question', output_key='answer', return_messages=True)
    llm = ChatOpenAI(
    openai_api_key=OPENAPI_KEY,
    model_name='gpt-3.5-turbo',
    temperature=1
    )
    return (vectorstore, llm, memory)

#Performs the similarity search and inputs query into OPENAI, then is formatted and outputted
def query_embeddings(query, vectorstore, llm, memory):

    vectorstore.similarity_search(
        query=query,
        k=10,
    )

    #qa = RetrievalQA.from_chain_type(
    #llm=llm,
    #chain_type="stuff",
    #retriever=vectorstore.as_retriever()
    #)
    #print(qa.run(query))
    doc_chain = load_qa_with_sources_chain(llm, chain_type="stuff")

    qa_with_sources = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    print(memory)
    format_query(qa_with_sources(query))

#Formats the query and prints it to the terminal
def format_query(query):
    print('\n')
    print(str(query["answer"]))
    print('\n')
    print("Sources: " + str(query["sources"]))

#Allows looping of commands in Command Line Interface
def terminal_query(vectorstore, llm, memory):
    print("Input a query (type exit to exit)")
    query = input()
    while query.lower() != 'exit':
        query_embeddings(query, vectorstore, llm, memory)
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
        loader = DirectoryLoader(os.path.join(os.getcwd(), 'data'), glob="*.pdf", show_progress=True, loader_cls=PyPDFLoader)
        
        data = loader.load() #Data is an an array of Document objects with each object having a page_content and metadata
        #print(data)
        initalize_embeddings(data, VERBOSE)

    vectorstore, llm, memory = intialize_dependencies()

    terminal_query(vectorstore, llm, memory)

if __name__ == "__main__":
    argv = sys.argv
    main(argv)