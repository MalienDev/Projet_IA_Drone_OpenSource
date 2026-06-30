"""
Script to seed the database with initial data.
Creates a default admin operator if none exists.
Runs locally connecting to the PostgreSQL database.
"""

import sys
import os
import psycopg2
from psycopg2 import sql
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with initial data."""
    
    # Database connection parameters
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "drone_surveillance")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT username FROM operators WHERE username = %s", ("admin",))
        if cursor.fetchone():
            print("Admin user already exists. Skipping seed.")
            return
        
        # Create default admin user
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        password_hash = get_password_hash(default_password)
        
        insert_query = sql.SQL("""
            INSERT INTO operators (username, password_hash, role, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """)
        
        cursor.execute(insert_query, ("admin", password_hash, "admin"))
        
        print(f"✓ Admin user created successfully")
        print(f"  Username: admin")
        print(f"  Password: {default_password}")
        print(f"  ⚠️  IMPORTANT: Change this password after first login!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    seed_database()
