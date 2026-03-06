from app import app, db
from models.user import User
from models.profile import Profile
from models.job import Job
from models.company import Company
from models.company_question import CompanyQuestion

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    with app.app_context():
        logger.info("Dropping all tables...")
        # Add CASCADE to drop tables if there are dependencies in PostgreSQL
        db.reflect()
        db.drop_all()
        
        logger.info("Creating fresh tables based on current schema...")
        db.create_all()
        
        logger.info("✅ Database reset complete! The schema is now fully updated.")

if __name__ == '__main__':
    # WARNING: This will delete ALL data in the database.
    confirm = input("⚠️ WARNING: This will DELETE all data in the database. Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Cancelled.")
