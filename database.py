import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ImportantDate(Base):
    __tablename__ = 'ImportantDates'

    date_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    event_description = Column(String, nullable=False)
    notification_sent = Column(Boolean, default=False)

def create_tables():
    Base.metadata.create_all(bind=engine)