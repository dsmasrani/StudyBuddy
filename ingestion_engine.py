from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

import pinecone
import os

def main():
    filepath = os.getcwd() + '/data/'
    loader = DirectoryLoader(filepath)

    data = loader.load()
    
    print (f'You have {len(data)} document(s) in your data')
    print (f'There are {len(data[0].page_content)} characters in your document')

    embeddings = OpenAIEmbeddings(openai_api_key='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')
    pinecone.init(
        api_key='116be029-cfab-4c8b-84d7-d9d95aa035dd', 
        environment='us-west4-gcp-free' 
    )
    index_name = "studybuddy"

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)

    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
    #query = "How many accidents has the car gotten into?"
    #docs = docsearch.similarity_search(query)

    #print(docs[0].page_content[:450])


    llm = OpenAI(temperature=0, openai_api_key='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')
    chain = load_qa_chain(llm, chain_type="stuff")
    query = "How many times has the bmw had its oil changed?"
    docs = docsearch.similarity_search(query)
    print(chain.run(input_documents=docs, question=query))

if __name__ == "__main__":
    main()


