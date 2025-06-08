import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("MEMBER_DB_USER")
DB_PASS = os.getenv("MEMBER_DB_PASS")
DB_HOST = os.getenv("MEMBER_DB_HOST", "member_db")
DB_PORT = os.getenv("MEMBER_DB_PORT", "5432")
DB_NAME = os.getenv("MEMBER_DB_NAME")

if not all([DB_USER, DB_PASS, DB_NAME]):
    raise RuntimeError("MEMBER_DB_USER, MEMBER_DB_PASS, and MEMBER_DB_NAME must be set")

DATABASE_URL = os.getenv(
    "MEMBER_DATABASE_URL",
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

RETRY_ATTEMPTS = int(os.getenv("DB_CONNECT_RETRY_ATTEMPTS", 5))
RETRY_DELAY = int(os.getenv("DB_CONNECT_RETRY_DELAY", 2))

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def connect_with_retry(attempts=RETRY_ATTEMPTS, delay=RETRY_DELAY):
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            with engine.connect():
                print(f"[db] Connected on attempt {i}")
                return
        except OperationalError as e:
            last_exc = e
            print(f"[db] Attempt {i} failed: {e}, retrying in {delay}s...")
            time.sleep(delay)
    raise last_exc


connect_with_retry()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
