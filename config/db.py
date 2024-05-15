from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from dotenv import load_dotenv
import os

load_dotenv()

DRIVER_NAME = os.getenv('DRIVER_NAME')
USERNAME = os.getenv('DB_USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE_NAME = os.getenv('DATABASE_NAME')

connection_string = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}?driver={DRIVER_NAME}'

engine = create_engine(connection_string)
metadata = MetaData()

user_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(length=100), nullable=False, unique=True),
    Column('password', String, nullable=False)
)

recipe_table = Table(
    'recipes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('ingredients', String, nullable=False),
    Column('directions', String, nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
)

metadata.create_all(engine)
