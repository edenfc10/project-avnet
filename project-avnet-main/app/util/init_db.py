import os
import time
from sqlalchemy.exc import OperationalError
from app.core.database import Base, engine
# Ensure all SQLAlchemy models are imported so they are registered in Base.metadata
import app.models.user  # noqa: F401
import app.models.mador  # noqa: F401
import app.models.meeting  # noqa: F401


def create_tables(retries=5, delay=3):
    # If RESET_DB is set, drop all existing tables and recreate them.
    if os.getenv("RESET_DB") in ("1", "true", "True"):
        print("RESET_DB enabled: dropping all tables")
        Base.metadata.drop_all(bind=engine)

    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully")
            return
        except OperationalError:
            print(f"Database not ready, retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database")