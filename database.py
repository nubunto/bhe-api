import sqlalchemy
import databases
from env import from_env

user = from_env('DB_USER')
password = from_env('DB_PASSWORD')
host = from_env('DB_HOST')
port = from_env('DB_PORT')
database = from_env('DB_DATABASE')

DATABASE_CONNECTION_URI = f'postgresql://{user}:{password}@{host}:{port}/{database}'

database = databases.Database(DATABASE_CONNECTION_URI)

metadata = sqlalchemy.MetaData()

berths = sqlalchemy.Table(
    "berths",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.VARCHAR),
    sqlalchemy.Column("has_fiscalization", sqlalchemy.BOOLEAN),
    sqlalchemy.Column("depth", sqlalchemy.FLOAT),
)


cost_queue = sqlalchemy.Table(
    "cost_queue",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("ship_details", sqlalchemy.JSON),
    sqlalchemy.Column("created_at", sqlalchemy.DATETIME),
)

engine = sqlalchemy.create_engine(
    DATABASE_CONNECTION_URI
)
