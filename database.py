from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

DATABASE_URL = 'mysql+pymysql://root:anuj1234@localhost:3306/ziptie'

engine = create_engine(DATABASE_URL)

if not database_exists(engine.url):
    create_database(engine.url)
else:
    # Connect the database if exists.
    engine.connect()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()