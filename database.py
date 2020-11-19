from sqlalchemy import Column, Integer, VARCHAR, BOOLEAN, FLOAT, MetaData, Table, JSON, DATETIME, create_engine
import databases
from env import from_env

user = from_env('DB_USER')
password = from_env('DB_PASSWORD')
host = from_env('DB_HOST')
port = from_env('DB_PORT')
database = from_env('DB_DATABASE')

DATABASE_CONNECTION_URI = f'postgresql://{user}:{password}@{host}:{port}/{database}'

database = databases.Database(DATABASE_CONNECTION_URI)

metadata = MetaData()

berths = Table(
    "berths",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", VARCHAR),
    Column("has_fiscalization", BOOLEAN),
    Column("depth", FLOAT),
)


cost_queue = Table(
    "cost_queue",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ship_details", JSON),
    Column("created_at", DATETIME),
)

engine = create_engine(
    DATABASE_CONNECTION_URI
)

#metadata.create_all(engine)