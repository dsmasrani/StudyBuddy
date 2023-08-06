from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(openai_api_key='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')
docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name="studybuddy")