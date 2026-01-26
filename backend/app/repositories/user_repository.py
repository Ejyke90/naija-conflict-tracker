"""
Repository pattern for User CRUD operations.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.auth import User
from app.services.password_service import hash_password


class UserRepository:
    """Repository for User model database operations."""
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        password: str,
        role: str = "viewer",
        full_name: Optional[str] = None
    ) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            email: User email (must be unique)
            password: Plain text password (will be hashed)
            role: User role (admin/analyst/viewer)
            full_name: Optional user's full name
            
        Returns:
            Created User instance
            
        Raises:
            IntegrityError: If email already exists
            
        Example:
            >>> user = await user_repo.create_user(
            ...     db, "analyst@nextier.org", "SecureP@ss123", 
            ...     role="analyst", full_name="John Doe"
            ... )
            >>> user.email
            'analyst@nextier.org'
        """
        hashed_password = hash_password(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
            full_name=full_name,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    def create_user_sync(
        db: Session,
        email: str,
        password: str,
        role: str = "viewer",
        full_name: Optional[str] = None
    ) -> User:
        """Synchronous version of create_user for scripts."""
        hashed_password = hash_password(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=role,
            full_name=full_name,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve user by email address.
        
        Args:
            db: Database session
            email: User email to search for
            
        Returns:
            User instance or None if not found
            
        Example:
            >>> user = await user_repo.get_by_email(db, "analyst@nextier.org")
            >>> user.role
            'analyst'
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def get_by_email_sync(db: Session, email: str) -> Optional[User]:
        """Synchronous version of get_by_email."""
        result = db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Retrieve user by UUID.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User instance or None if not found
            
        Example:
            >>> user = await user_repo.get_by_id(db, user_uuid)
            >>> user.full_name
            'John Doe'
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def get_by_id_sync(db: Session, user_id: UUID) -> Optional[User]:
        """Synchronous version of get_by_id."""
        result = db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user_id: UUID) -> User:
        """
        Update user's last_login timestamp.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Updated User instance
            
        Example:
            >>> user = await user_repo.update_last_login(db, user_uuid)
            >>> user.last_login  # Now shows current timestamp
        """
        user = await UserRepository.get_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
        return user
    
    @staticmethod
    def update_last_login_sync(db: Session, user_id: UUID) -> User:
        """Synchronous version of update_last_login."""
        user = UserRepository.get_by_id_sync(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    async def update_password(db: AsyncSession, user_id: UUID, new_password: str) -> User:
        """
        Update user's password (for password reset flow).
        
        Args:
            db: Database session
            user_id: User UUID
            new_password: New plain text password (will be hashed)
            
        Returns:
            Updated User instance
            
        Example:
            >>> user = await user_repo.update_password(db, user_uuid, "NewP@ss456")
        """
        user = await UserRepository.get_by_id(db, user_id)
        if user:
            user.hashed_password = hash_password(new_password)
            await db.commit()
            await db.refresh(user)
        return user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: UUID) -> User:
        """
        Deactivate a user account (soft delete).
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Updated User instance with is_active=False
            
        Example:
            >>> user = await user_repo.deactivate_user(db, user_uuid)
            >>> user.is_active
            False
        """
        user = await UserRepository.get_by_id(db, user_id)
        if user:
            user.is_active = False
            await db.commit()
            await db.refresh(user)
        return user
    
    @staticmethod
    async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> list[User]:
        """
        List users with optional role filter and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum records to return
            role: Optional role filter
            
        Returns:
            List of User instances
            
        Example:
            >>> analysts = await user_repo.list_users(db, role="analyst", limit=50)
            >>> len(analysts)
            12
        """
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


# Singleton instance
user_repo = UserRepository()
