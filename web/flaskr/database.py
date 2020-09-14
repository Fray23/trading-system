import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

flaskr_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(flaskr_dir, 'db')

POSTGRES_URL="postgres:5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="1234postgres1234"
POSTGRES_DB="postgres"

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PASSWORD,url=POSTGRES_URL,db=POSTGRES_DB)
engine = create_engine(DB_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import web.flaskr.models
    Base.metadata.create_all(engine)
