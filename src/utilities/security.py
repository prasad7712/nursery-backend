"""Security utilities for JWT and password hashing"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
import bcrypt

from jose import JWTError, jwt

from src.utilities.config_manager import config


class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt
        Note: Bcrypt has a 72-byte limit. Passwords exceeding this are truncated.
        """
        # Truncate password to 72 bytes as per bcrypt limitation
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate to 72 bytes (may split multi-byte characters)
            password_bytes = password_bytes[:72]
            # Decode back to string, ignoring partial multi-byte characters at end
            password = password_bytes.decode('utf-8', errors='ignore')
        
        # Hash with bcrypt
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # Truncate to 72 bytes as per bcrypt limitation
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            config.jwt_secret_key, 
            algorithm=config.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            config.jwt_secret_key, 
            algorithm=config.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                config.jwt_secret_key, 
                algorithms=[config.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def generate_random_token(length: int = 32) -> str:
        """Generate a random token for various purposes"""
        return secrets.token_urlsafe(length)


# Singleton instance
security = SecurityUtils()
