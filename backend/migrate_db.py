from app import app
from models import db
from sqlalchemy import text

def alter_harvest_log():
    with app.app_context():
        try:
            db.session.execute(text("ALTER TABLE harvest_log ADD COLUMN source VARCHAR(80) NOT NULL DEFAULT 'all';"))
            db.session.commit()
            print("Successfully added 'source' column to 'harvest_log' table.")
        except Exception as e:
            print(f"Error adding column (it might already exist): {e}")
            db.session.rollback()

if __name__ == "__main__":
    alter_harvest_log()