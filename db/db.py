from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

DB_URL = "mysql+mysqlconnector://telegram_user:secure_password@localhost/telegram_db"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
