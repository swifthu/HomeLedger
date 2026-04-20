"""Migration script to add new fields to existing database."""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from db.database import engine

def migrate():
    """Add new columns to records table."""
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(records)"))
        existing_cols = [row[1] for row in result]

        migrations = []

        if "merchant" not in existing_cols:
            migrations.append("ALTER TABLE records ADD COLUMN merchant TEXT")

        if "tags" not in existing_cols:
            migrations.append("ALTER TABLE records ADD COLUMN tags TEXT")

        if "deleted_at" not in existing_cols:
            migrations.append("ALTER TABLE records ADD COLUMN deleted_at TEXT")

        if "year_month" not in existing_cols:
            migrations.append("ALTER TABLE records ADD COLUMN year_month TEXT NOT NULL DEFAULT ''")

        # Run migrations
        for m in migrations:
            print(f"Running: {m}")
            conn.execute(text(m))

        conn.commit()

        # Backfill year_month from created_at for existing records
        if "year_month" in existing_cols:
            result = conn.execute(text("SELECT COUNT(*) FROM records WHERE year_month = ''"))
            if result.scalar() > 0:
                print("Backfilling year_month...")
                conn.execute(text("UPDATE records SET year_month = substr(created_at, 1, 7) WHERE year_month = ''"))
                conn.commit()

        print("Migration complete.")

if __name__ == "__main__":
    migrate()