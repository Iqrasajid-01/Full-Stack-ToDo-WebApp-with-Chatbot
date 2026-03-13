"""
Utility functions for handling bcrypt password limitations
"""
import bcrypt


def ensure_bcrypt_compatible_password(password: str) -> str:
    """
    Ensures a password is compatible with bcrypt's 72-byte limit.
    
    Args:
        password: The input password string
        
    Returns:
        A password string that is guaranteed to be <= 72 bytes when encoded as UTF-8
    """
    # First, check if the password is already within the limit
    encoded = password.encode('utf-8')
    if len(encoded) <= 72:
        return password
    
    # If not, truncate to 72 bytes and decode back to string
    # This handles multi-byte UTF-8 characters properly
    truncated_bytes = encoded[:72]
    
    # Try to decode, handling potential incomplete multibyte sequences
    try:
        return truncated_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # If there's an issue with the truncation, decode with error handling
        return truncated_bytes.decode('utf-8', errors='ignore')


def hash_bcrypt_password(password: str) -> str:
    """
    Hashes a password with bcrypt, ensuring it's within the 72-byte limit.
    """
    compatible_password = ensure_bcrypt_compatible_password(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(compatible_password.encode('utf-8'), salt).decode('utf-8')


def verify_bcrypt_password(password: str, hashed: str) -> bool:
    """
    Verifies a password against a bcrypt hash, ensuring compatibility.
    """
    compatible_password = ensure_bcrypt_compatible_password(password)
    return bcrypt.checkpw(compatible_password.encode('utf-8'), hashed.encode('utf-8'))