import os
from datetime import date

from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("SQLite_DATABASE_URL", "sqlite:///myproject.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Urls(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(Date, default=date.today)


class UrlCheck(Base):
    __tablename__ = "url_checks"

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, nullable=False)
    status_code = Column(Integer)
    h1 = Column(String)
    title = Column(String)
    description = Column(String)
    created_at = Column(Date, default=date.today)


Base.metadata.create_all(bind=engine)


def get_db():
    return SessionLocal()