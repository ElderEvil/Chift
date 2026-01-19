from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for User database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        query = select(User).where(User.username == username)
        return self.db.scalar(query)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        query = select(User).where(User.email == email)
        return self.db.scalar(query)

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID"""
        return self.db.get(User, user_id)

    def create(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, update_data: dict) -> User:
        """Update an existing user"""
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete a user"""
        self.db.delete(user)
        self.db.commit()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        query = select(User).offset(skip).limit(limit)
        return list(self.db.scalars(query).all())

    def count(self) -> int:
        """Count total users"""
        query = select(User)
        return len(list(self.db.scalars(query).all()))
