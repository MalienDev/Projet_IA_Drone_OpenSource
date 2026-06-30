"""
Script to seed the database with initial data.
Creates a default admin operator if none exists.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.operator import Operator
from app.auth.security import get_password_hash


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(Operator).filter(Operator.username == "admin").first()
        
        if admin_user:
            print("Admin user already exists. Skipping seed.")
            return
        
        # Create default admin user
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        admin_operator = Operator(
            username="admin",
            password_hash=get_password_hash(default_password),
            role="admin"
        )
        
        db.add(admin_operator)
        db.commit()
        
        print(f"✓ Admin user created successfully")
        print(f"  Username: admin")
        print(f"  Password: {default_password}")
        print(f"  ⚠️  IMPORTANT: Change this password after first login!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
