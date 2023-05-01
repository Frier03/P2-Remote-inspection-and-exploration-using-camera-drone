from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from os import getenv
from passlib.context import CryptContext

from models import TokenModel

SECRET_KEY = str(getenv('SECRET_KEY'))
pwd_context = CryptContext(schemes=["bcrypt_sha256"])

def generate_access_token(data: dict, minutes: int) -> TokenModel:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(encoded_jwt: str):
    try:
        return jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=JWTError)
    
def verify_password(plain_password: str, hashed_password: str) -> bool: #TODO Make this more secure
    # Placeholder for validating the password
    if len(plain_password) < 3:
        return False
    return pwd_context.verify(plain_password, hashed_password) # True/False depends if both hashes passwords matches

def is_user_authorized(access_token: str, blacklisted_tokens: dict[datetime, str]) -> bool:
    try:
        # Decode access token
        payload = decode_access_token(access_token)

        # Decode username from payload
        username = payload.get('sub')
    
        if username is None or access_token in blacklisted_tokens:
            return False

        return True
    except (JWTError):
        return False
