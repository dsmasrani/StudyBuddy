# StudyBuddy

This is a project by @dsmasrani and @rotih aiming to change how users access ChatGPT. The aim is to allow any user to upload a folder full of documents to ChatGPT (pdf files) and ask it questions based on the context provided.

Currently, the system can support `.pdf`, with the expectation to support more formats in the future.

This repository is split into two separate but related projects wrapped into one mono repo. Under `src`, you can find the direct model we have built for file ingestion. Under `api`, you can find the API version of the same project we have deployed for cloud deployment (using `Render` and `Supabase` for compute and storage respectively).

## Dependency Setup

- Get an OpenAI key with instructions found [here](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt). A credit card is required as you will have to pay for API usage.
- Setup your pinecone database to be optimized for chatGPT:
  - Create a pinecone account found [here](https://app.pinecone.io/?sessionType=signup).
  - Login to said pinecone account and navigate to `Indexes`.
  - Press `Create Index` and give it a name (This will be your **PINECONE_INDEX_NAME**).
  - For dimensions put in `1536` with Metric `cosine`.
  - Pick p1 for faster queries **Note: without any activity pinecone will auto-delete. Try to run a query at least once a week to avoid deletion**.
  - Press Create Index.
  - Click into your index and note down the name environment.
  - Navigate on the left to API Keys and press `Create API Key`.
  - Enter whatever key name you would like and copy the value it provides (You can only see this once so copy it and keep it safe for the future).

### If Deploying API Version

*Instructions for deploying the API version are not provided in the document snippet.*

### How to Install + Run (Terminal Version)

1. Clone this repository.
2. In the repository folder, run `pip3 install -r requirements.txt` to install all necessary requirements.
3. Navigate to `src/constants.py`.
4. Populate the constant keys with their values:
   - `OPENAPI_KEY` is the API Key starting with `sk-`. Instructions [here](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt).
   - `PINECONE_API_KEY` is the API Key for Pinecone. Instructions [here](https://docs.pinecone.io/docs/authentication).
   - `PINECONE_ENVIRONMENT` will be the label of your index on Pinecone's index page.
   - `PINECONE_INDEX_NAME` is the name of your index.
5. After filling the constants (do not commit them to GitHub to prevent expiration), run `python3 src/application.py`. This will open a GUI for key uploading and file ingestion.
6. Choose a folder, press 'upload files', and watch the files upload to your vectorized database. Note: The application might require multiple clicks to respond, so patience is advised.
7. After uploading, navigate to `query.py` and run it as `python3 query.py` for interaction. Ask questions in a single line format. For multi-line queries, use a converter like [this one](https://tools.knowledgewalls.com/online-multiline-to-single-line-converter).
8. To exit, press `ctrl + c` or type "exit". You can repeat the process for multiple sessions.

## How to Install + Run (API Version)

### Render 

1. Clone the repository to a new repository or deploy from the public repository.
2. Create an account on Render. Create a new web service and select the repository for deployment.
3. In the build command section, input `pip install --upgrade pip && pip install -r requirements.txt`.
4. Skip the pre-deploy command and enter `uvicorn api.src.api.server:app --host 0.0.0.0 --port $PORT` as the start command.
5. Optionally enable auto-deploy. Select the free instance and add environment variables as follows:
   - `API_KEY`: Create a unique and secure string.
   - `PYTHON_VERSION`: Set to 3.11.7.

*Further instructions on using Supabase and environment variable setups are included in the document.*

### Supabase

1. Create an account on Supabase.
2. Create a new project and navigate to the SQL editor in the left navbar.
3. Refer to our `schema.sql` and copy-paste that into the SQL editor and click run to set up all the tables.
4. Retrieve these values and note them down:
   - `OPENAPI_KEY` is the API Key beginning with `sk-`. Instructions found [here](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt).
   - `PINECONE_API_KEY` is the API Key for Pinecone. Instructions found [here](https://docs.pinecone.io/docs/authentication).
   - `PINECONE_ENVIRONMENT` will be the environment your index is labeled as on the index's page.
   - `PINECONE_INDEX_NAME` will be the name of the aforementioned index you made.
5. Navigate to the authentication section. In users, click add user and send an invite to your email.
6. After accepting the invite, copy the User UID and navigate back to the table editor.
7. Insert a new row into the `user_keys` table and input your keys and Pinecone environment and index name into the respective columns along with your User UID in the `user_id` column and the email you used for authentication in the `user_email` column.
8. Navigate to the storage section and create a folder with your User UID as the name. Note that once ingestion runs, the folder gets deleted and you may need to make it again.
9. Click on policies and create two new policies:
   - Delete access to anon.
   - Read access to everyone.
10. Navigate to project settings.
    - Under API, note down the Project URL public API key.
    - Under Database, note down the connection string, replacing `[YOUR_PASSWORD]` with your API_KEY made during the Render setup.
11. Go back to Render with your new Project URL public API key and connection string.
    - Add a new environment variable called `POSTGRES_URI` and paste the connection string in.
    - Add a new environment variable `PROJECT_KEY` and paste the public API key in.
    - Add a new environment variable called `PROJECT_URL` and paste the Project URL in.

### .env

1. Open VSCode or an IDE of your choice and open up the project.
2. Create a new file named `.env`.
3. Add your `API_KEY`, `POSTGRES_URI`, `PROJECT_KEY`, and `PROJECT_URL`.
### How to Interact with the API

1. Go to the respective API URL you defined (either the one provided by Render or `127.0.0.1`). This will list all the APIs, allowing you to interact with them once you press the unlock button in the top right corner and paste the API key you were given in the setup.
2. All of the APIs are defined below:
   - `/ingestion/retrieve_files`: Takes no parameters and lists all files waiting in the queue to be processed, ordered by upload timestamp.
   - `/ingestion/resolve_queue`: Takes no parameters and processes the entire queue of waiting files by uploading them into their respective accounts. This will continue until all files are processed (and subsequently deleted). Set up a cron job to hit this every 10 minutes for long-term use.
   - `/ingestion/process_file`: Takes three parameters (`file_url` - direct URL path to the .pdf file, `user_email` - the email account for which you want to ingest, `file_name` - what you want to name the file for future metadata processing). This skips the existing queue and processes only the file you specify (upload not required).
   - `/query/query`: Takes two parameters (`question` and `user_UUID`). The UUID can be found in the `public -> user_keys` table. The output is the answer and the respective sources.

