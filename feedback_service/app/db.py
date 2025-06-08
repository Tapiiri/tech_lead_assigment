import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# fundamental pieces
DB_USER = os.getenv("FEEDBACK_DB_USER")
DB_PASS = os.getenv("FEEDBACK_DB_PASS")
DB_HOST = os.getenv("FEEDBACK_DB_HOST", "feedback_db")
DB_NAME = os.getenv("FEEDBACK_DB_NAME")
DB_PORT = os.getenv("FEEDBACK_DB_PORT", 5432)

if not all([DB_USER, DB_PASS, DB_NAME]):
    raise RuntimeError("FEEDBACK_DB_USER, FEEDBACK_DB_PASS and FEEDBACK_DB_NAME must be set")

# build full URL if it isn't explicitly provided
DATABASE_URL = os.getenv(
    "FEEDBACK_DATABASE_URL",
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# retry settings
RETRY_ATTEMPTS = int(os.getenv("DB_CONNECT_RETRY_ATTEMPTS", 5))
RETRY_DELAY = int(os.getenv("DB_CONNECT_RETRY_DELAY", 2))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def connect_with_retry(attempts=RETRY_ATTEMPTS, delay=RETRY_DELAY):
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            with engine.connect():
                print(f"[db] Connected on attempt {i}")
                return
        except OperationalError as e:
            last_exc = e
            print(f"[db] Attempt {i} failed: {e!r}, retrying in {delay}s…")
            time.sleep(delay)
    print(f"[db] All {attempts} attempts failed, giving up.")
    raise last_exc

# run it at import/startup
connect_with_retry()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()