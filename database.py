# database.py

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./app_data.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

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

if __name__ == "__main__":
    # You can run this file directly once to create the database table.
    print("Creating database tables...")
    create_tables()
    print("Tables created successfully.")