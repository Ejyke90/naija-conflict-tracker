"""
Seed script to create the first admin user.

Run this once during initial deployment:
    python seed_admin.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.repositories.user_repository import user_repo
import getpass


def seed_admin():
    """Create the first admin user interactively."""
    print("=" * 50)
    print("Create Initial Admin User")
    print("=" * 50)
    
    # Get admin details
    email = input("Admin email: ").strip()
    full_name = input("Admin full name: ").strip()
    
    # Get password securely
    while True:
        password = getpass.getpass("Admin password (min 8 chars): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue
        
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Passwords don't match")
            continue
        
        break
    
    # Create user
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = user_repo.get_by_email_sync(db, email)
        if existing:
            print(f"\n❌ User with email {email} already exists")
            return
        
        # Create admin user
        admin = user_repo.create_user_sync(
            db=db,
            email=email,
            password=password,
            role="admin",
            full_name=full_name
        )
        
        print("\n" + "=" * 50)
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        print(f"Full Name: {admin.full_name}")
        print(f"User ID: {admin.id}")
        print("\nYou can now login with these credentials.")
        
    except Exception as e:
        print(f"\n❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()


def get_by_email_sync(db, email):
    """Synchronous version of get_by_email for seeding."""
    from sqlalchemy import select
    from app.models.auth import User
    
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


# Patch the repository to add sync method
user_repo.get_by_email_sync = staticmethod(get_by_email_sync)


if __name__ == "__main__":
    seed_admin()
