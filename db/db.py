from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

DB_URL = "mysql+pymysql://reza:1234@localhost/tel_test2"


engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
