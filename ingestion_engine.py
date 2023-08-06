import os
import textract

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from pdfminer.high_level import extract_text
from constants import OPENAPI_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME
import pinecone

textract_config = {
    '.pdf': {
        'pdftotext': None,
        'command': 'pdfminer.six',
    },
}

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

def main():
    data_directory = os.path.join(os.getcwd(), 'data')
    text_files_directory = convert_to_text_files(data_directory)

    loader = DirectoryLoader(text_files_directory)
    data = loader.load()
    
    print(f'You have {len(data)} document(s) in your data')
    print(f'There are {len(data[0].page_content)} characters in your document')
    print(data)
    embeddings  = OpenAIEmbeddings(openai_api_key=OPENAPI_KEY)
    pinecone.init(      
        api_key=PINECONE_API_KEY,      
        environment=PINECONE_ENVIRONMENT,      
    )      
    index = pinecone.Index(PINECONE_INDEX_NAME)
    index_name = PINECONE_INDEX_NAME

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)

    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)

    llm = OpenAI(temperature=0, openai_api_key=OPENAPI_KEY)

    chain = load_qa_chain(llm, chain_type="StudyBuddy")
    print("Input a query (type exit to exit)")
    query = input()
    while query.lower() != 'exit':
        docs = docsearch.similarity_search(query)
        print(chain.run(input_documents=docs, question=query))
        print("Input a query (type exit to exit)")
        query = input()

if __name__ == "__main__":
    main()
