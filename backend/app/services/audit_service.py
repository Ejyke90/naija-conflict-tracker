"""
Audit logging service for security-critical actions.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.auth import AuditLog


class AuditService:
    """Service for logging security events to the audit_log table."""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: Optional[UUID],
        action: str,
        resource: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> AuditLog:
        """
        Create an audit log entry for a security-critical action.
        
        Args:
            db: Database session
            user_id: UUID of user performing the action (None for anonymous actions like failed login)
            action: Action type (e.g., "LOGIN", "LOGOUT", "CREATE_USER", "DELETE_RESOURCE")
            resource: Resource affected (e.g., "user:123", "conflict:456")
            ip_address: Client IP address
            user_agent: Client User-Agent header
            details: Additional JSON data (e.g., {"email": "...", "reason": "..."})
            success: Whether the action succeeded
            
        Returns:
            Created AuditLog instance
            
        Example:
            >>> await audit_service.log_action(
            ...     db=db,
            ...     user_id=user.id,
            ...     action="LOGIN",
            ...     resource=f"user:{user.id}",
            ...     ip_address=request.client.host,
            ...     user_agent=request.headers.get("user-agent"),
            ...     details={"email": user.email},
            ...     success=True
            ... )
        """
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            success=success,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        
        return audit_entry
    
    @staticmethod
    async def get_user_audit_trail(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 100
    ) -> list[AuditLog]:
        """
        Retrieve audit trail for a specific user.
        
        Args:
            db: Database session
            user_id: User UUID
            limit: Maximum number of records to return
            
        Returns:
            List of AuditLog entries, newest first
            
        Example:
            >>> logs = await audit_service.get_user_audit_trail(db, user_id, limit=50)
            >>> logs[0].action
            'LOGIN'
        """
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_failed_login_attempts(
        db: AsyncSession,
        email: str,
        since: datetime,
        limit: int = 10
    ) -> list[AuditLog]:
        """
        Get recent failed login attempts for an email.
        
        Args:
            db: Database session
            email: User email to check
            since: Only return attempts after this timestamp
            limit: Maximum number of records
            
        Returns:
            List of failed login AuditLog entries
            
        Example:
            >>> from datetime import datetime, timedelta
            >>> since = datetime.utcnow() - timedelta(minutes=15)
            >>> failed = await audit_service.get_failed_login_attempts(
            ...     db, "user@example.com", since
            ... )
            >>> len(failed)
            3
        """
        result = await db.execute(
            select(AuditLog)
            .where(
                AuditLog.action == "LOGIN_FAILED",
                AuditLog.details["email"].astext == email,
                AuditLog.timestamp >= since
            )
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


# Singleton instance
audit_service = AuditService()
