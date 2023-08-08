import os
from uuid import uuid4
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
import textract
import pinecone
from pdfminer.high_level import extract_text
from langchain.embeddings.openai import OpenAIEmbeddings
from constants import OPENAPI_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain

textract_config = {
    '.pdf': {
        'pdftotext': None,
        'command': 'pdfminer.six',
    },
}

VERBOSE = True

def convert_to_text_files(data_directory):
    text_files_directory = os.path.join(data_directory, 'text_files')
    if not os.path.exists(text_files_directory):
        os.makedirs(text_files_directory)

    for filename in os.listdir(data_directory):
        input_file_path = os.path.join(data_directory, filename)
        if filename.endswith(".pdf") or filename.endswith(".docx") or filename.endswith(".pptx"):
            try:
                if filename.endswith(".pdf"):
                    text = extract_text(input_file_path)
                elif filename.endswith(".docx") or filename.endswith(".pptx"):
                    text = textract.process(input_file_path, config=textract_config).decode('utf-8')
                else:
                    continue

                output_file_path = os.path.join(text_files_directory, f"{filename}.txt")
                with open(output_file_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(text)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return text_files_directory

# create the length function
def tiktoken_len(text):
    tiktoken.encoding_for_model('gpt-3.5-turbo')
    tokenizer = tiktoken.get_encoding('cl100k_base')

    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

def text_splitter(data):
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter
    chunks = []
    for document in data:
        chunks.append(text_splitter.split_text(document.page_content))
    return chunks

def initalize_embeddings(data):
    texts = []
    metadatas = []
    model_name = 'text-embedding-ada-002'
    embed = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=OPENAPI_KEY,
    )

    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT,
    )

    index = pinecone.GRPCIndex(PINECONE_INDEX_NAME)

    print(index.describe_index_stats())
    txt_splitter = text_splitter(data)
    for i, document in enumerate(data):
        metadata = {
            'source': document.metadata['source']}
        record_texts = txt_splitter.split_text(document.page_content)

        record_metadatas = [{
            "chunk": j, "text": text, **metadata
        } for j, text in enumerate(record_texts)]

        texts.extend(record_texts)
        metadatas.extend(record_metadatas)

        if len(texts) >= 10:
            ids = [str(uuid4()) for _ in range(len(texts))]
            embeds = embed.embed_documents(texts)
            index.upsert(vectors=zip(ids, embeds, metadatas))
            texts = []
            metadatas = []

    if len(texts) > 0:
        ids = [str(uuid4()) for _ in range(len(texts))]
        embeds = embed.embed_documents(texts)
        index.upsert(vectors=zip(ids, embeds, metadatas))
        
def query_embeddings(query):
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
    text_field="text"
    vectorstore = Pinecone(index, embed.embed_query, text_field)

    vectorstore.similarity_search(
        query=query,
        k=10,
    )
    llm = ChatOpenAI(
    openai_api_key=OPENAPI_KEY,
    model_name='gpt-3.5-turbo',
    temperature=0.0
    )
    qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
    )
    qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    print(qa.run(query))
    print(qa_with_sources(query))
def main():
    #data_directory = os.path.join(os.getcwd(), 'data')
    #text_files_directory = convert_to_text_files(data_directory)
    #loader = DirectoryLoader(text_files_directory)
    #data = loader.load()
    #initalize_embeddings(data)
    #chunks = text_splitter(data)
    #initalize_embeddings(chunks)
    #print(data)
    query_embeddings("What is shashank's phone number?")
if __name__ == "__main__":
    main()
