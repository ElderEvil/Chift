#!/usr/bin/env python3
"""
Create an admin user for the Chift application.

Usage:
    python -m scripts.create_admin
    # Or with uv:
    uv run python -m scripts.create_admin
"""

from getpass import getpass
import sys

from app.core.auth import get_password_hash
from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository


def create_admin():
    """Create an admin user interactively."""
    print("=== Chift Admin User Creation ===\n")

    # Get user input
    username = input("Username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        sys.exit(1)

    email = input("Email: ").strip()
    if not email:
        print("Error: Email cannot be empty")
        sys.exit(1)

    password = getpass("Password: ")
    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match")
        sys.exit(1)

    # Create user in database
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)

        # Check if user already exists
        if user_repo.get_by_username(username):
            print(f"Error: User '{username}' already exists")
            sys.exit(1)

        if user_repo.get_by_email(email):
            print(f"Error: Email '{email}' is already registered")
            sys.exit(1)

        # Create user
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": get_password_hash(password),
            "disabled": False,
        }

        user = user_repo.create(user_data)
        print("\n✅ Admin user created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   User ID: {user.id}")

    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
