import sys
import os

# This adds the project root to Python's search path.
# Without this, Python cannot find the src module when
# we run this file directly from the terminal.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.db import engine, Base
from src.database import models  # noqa: F401 — imports all models so Base knows about them


def init_db():
    # create_all looks at every class that inherits from Base
    # and creates a corresponding table in the database if it doesn't exist.
    # It never deletes existing tables — safe to run multiple times.
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    print("Tables:", Base.metadata.tables.keys())


if __name__ == "__main__":
    init_db()