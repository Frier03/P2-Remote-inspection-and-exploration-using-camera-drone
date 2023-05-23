'''This module provides helper functions related to token generation, verification and password validation.

Functions:
    generate_access_token: Generate a JWT access token given user data and expiration time.
    decode_access_token: Decode a JWT access token and return the payload.
    verify_password: Verify a plain password against a hashed password.
    is_user_authorized: Verify if an access token is valid and not blacklisted.

Attributes:
    SECRET_KEY: The secret key used to encode and decode JWT tokens.
    pwd_context: The object responsible for password hashing and verification.
'''

# Default Python modules.
from datetime import datetime, timedelta

# FastAPI
from fastapi import HTTPException, status

# Json Web Token
from jose import JWTError, jwt

# Hashing password 
from passlib.context import CryptContext

# JWT encryption key
from os import getenv
from dotenv import load_dotenv

# Own Pydantic Token
from models import TokenModel

load_dotenv()
SECRET_KEY: str = str(getenv('SECRET_KEY'))

if SECRET_KEY == "None":
    raise ValueError("No 'SECRET_KEY' found in dotenv")

pwd_context: CryptContext = CryptContext(schemes=["bcrypt_sha256"])

def generate_access_token(data: dict[str, any], minutes: int) -> TokenModel:
    """Generates a new JWT access token.

    Args:
        data (dict[str, any]): A dictionary with the data to include in the token payload.
        minutes (int): The duration in minutes until the token expires.

    Returns:
        TokenModel: The JWT access token.
    """
    # Copy the token form `sub`, so that we do not change the original provided token.
    to_encode = data.copy()

    # Create an expire date for the token.
    expire: datetime = datetime.utcnow() + timedelta(minutes=minutes)
    
    # Update to_encode dict with expire data
    to_encode.update({"exp": expire})
    
    # Generate the JWT token. 
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt

def decode_access_token(encoded_jwt: str) -> dict[str, any] | HTTPException:
    """Decodes a JWT access token.

    Args:
        encoded_jwt (str): The encoded JWT access token.

    Returns:
        dict[str, any]: The decoded JWT access token payload.
        HTTPException: If the access token is invalid.
    """
    # Try to decode. The token may be invalid!
    try:
        return jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])
    
    # Exception is called if the token provided is invalid while trying to decode it.
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a password matches a hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password from the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """

    # Password policy. The password must be longer than 3.
    if len(plain_password) < 3:
        return False
    
    # `True` or `False` depends if both hashes passwords matches
    return pwd_context.verify(plain_password, hashed_password) 

def is_user_authorized(access_token: str, blacklisted_tokens: dict[datetime, str]) -> bool:
    """Determines if a user is authorized based on their access token.

    Args:
        access_token (str): The JWT access token.
        blacklisted_tokens (dict[datetime, str]): A dictionary containing blacklisted access tokens and their expiration times.

    Returns:
        bool: `True` if the user is authorized, `False` otherwise.
    """
    try:
        # Decode access token
        payload = decode_access_token(access_token)

        # Decode username from payload
        username = payload.get('sub')

        # Validate username and check if access token is in blacklisted tokens
        if username is None or access_token in blacklisted_tokens:
            return False
        
        return True

    except (JWTError, AttributeError):
        return False
