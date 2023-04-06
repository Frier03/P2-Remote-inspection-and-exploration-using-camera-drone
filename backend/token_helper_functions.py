from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from os import getenv

SECRET_KEY = str(getenv('SECRET_KEY'))

class TokenModel(BaseModel):
    access_token: str
    token_type: str

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