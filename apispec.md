Initialize and Upload Embeddings to Pinecone:
/ingestion/initialize-embeddings GET
### Returns 

/ingestion/upload-embeddings POST
Request Body: `[{ "text": "string", "source": "string", "page": "integer" }]`
Response: `{ "uploadStatus": "string", "failedRecords": "array" }`


QUERY
Initialize Dependencies:
/query/initialize GET
Response: `{ "status": "Initialized", "message": "Dependencies are set up." }`

Query Embeddings:
/query/query-embeddings POST
Request Body: `{ "query": "string", "user_id":  }`
Response: `{ "answer": "string", "sources": "array" }`

Load New Data and Initialize Embeddings:
/query/load-data POST
Request Body: `{ "directoryPath": "string", "globPattern": "string" }`
Response: `{ "loadStatus": "string", "numDocuments": "integer" }`