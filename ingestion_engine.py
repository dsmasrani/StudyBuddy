#PDF -> Embeddings Libraries
#requires pip install pypdf and pip3 install langchain

from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

DEFAULT_GLOB = "**/*."
APPROVED_FILE_TYPES = 'pdf'

glob = DEFAULT_GLOB + APPROVED_FILE_TYPES


def main():
    filepath = os.getcwd() + '/data/'
    loader = DirectoryLoader(filepath, glob=glob)

    data = loader.load()

    print (f'You have {len(data)} document(s) in your data')
    print (f'There are {len(data[30].page_content)} characters in your document')



if __name__ == "__main__":
    main()


