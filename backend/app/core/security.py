"""Security utilities: JWT tokens, password hashing, and RBAC."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()


# ============================================================
# Password Hashing
# ============================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password.

    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Stored hashed password.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT Tokens
# ============================================================


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        data: Payload data to encode.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token.

    Args:
        data: Payload data to encode.

    Returns:
        Encoded JWT refresh token string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token: JWT token string to decode.

    Returns:
        Decoded token payload.

    Raises:
        JWTError: If token is invalid or expired.
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


# ============================================================
# RBAC
# ============================================================


class UserRole(StrEnum):
    """User role enumeration for RBAC."""

    ADMIN = "admin"
    ANALYST = "analyst"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"


# Permission mapping: role -> allowed actions
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN: {
        "read",
        "write",
        "delete",
        "manage_users",
        "generate_reports",
        "manage_investigations",
        "configure_system",
        "view_audit_logs",
    },
    UserRole.INVESTIGATOR: {
        "read",
        "write",
        "generate_reports",
        "manage_investigations",
    },
    UserRole.ANALYST: {
        "read",
        "write",
        "generate_reports",
    },
    UserRole.VIEWER: {
        "read",
    },
}


def has_permission(role: UserRole, permission: str) -> bool:
    """Check if a role has a specific permission.

    Args:
        role: User role to check.
        permission: Permission string to verify.

    Returns:
        True if role has the permission, False otherwise.
    """
    return permission in ROLE_PERMISSIONS.get(role, set())
