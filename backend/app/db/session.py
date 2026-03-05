import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv(
  "DATABASE_URL",
  "postgresql+psycopg2://postgres:postgres@localhost:5432/auditsentinel"
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


