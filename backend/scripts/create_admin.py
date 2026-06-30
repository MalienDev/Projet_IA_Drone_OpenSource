"""
Create admin user directly in the database.
This script should be run inside the backend container.
"""

import sys
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.operator import Operator
from app.auth.security import get_password_hash


def create_admin_user():
    """Create admin user in the database."""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(Operator).filter(Operator.username == "admin").first()
        
        if admin_user:
            print("Admin user already exists. Skipping creation.")
            return
        
        # Create default admin user
        default_password = "admin123"
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
        print(f"Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
