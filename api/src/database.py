import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
metadata_obj = sqlalchemy.MetaData()
files = sqlalchemy.Table("files", metadata_obj, autoload_with = engine)
user_keys = sqlalchemy.Table("user_keys", metadata_obj, autoload_with = engine)