from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config import get_settings

_settings = get_settings()
_connect_args = {}
if _settings.database_url.startswith("sqlite"):
  _connect_args["check_same_thread"] = False
engine = create_engine(_settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
