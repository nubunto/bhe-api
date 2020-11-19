import sqlalchemy
import os
import databases

user = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
host = os.environ['DB_HOST']
port = os.environ['DB_PORT']
database = os.environ['DB_DATABASE']

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

#metadata.create_all(engine)