import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

import app.models  # Register all SQLAlchemy models before creating tables.
from app.database.session import create_tables as initialize_tables


def create_tables() -> None:
    initialize_tables()
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()
