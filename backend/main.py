#uvicorn main:app --reload
#pip install "python-jose[cryptography]"
#pip install "passlib[bcrypt]"
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt #jwt & pyjwt
from passlib.context import CryptContext
from pydantic import BaseModel
import time

SECRET_KEY = "DuJwTmBr35qLU7HHqg2AMG+jkmx92JZk" #https://cloud.google.com/network-connectivity/docs/vpn/how-to/generating-pre-shared-key

fake_users_db = { #TODO: Use MongoDB
    "admin": {
        "name": "admin",
        "hashed_password": "$2b$12$mE3KlrNxXcdb7Hn4g3Je2ulIcXwQj/vhLa8ez412aojaSJGf/5VIG" #123
    }
}

blacklisted_tokens = {} #NOTE: Better to store in-memory

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    name: str
    password: str


app = FastAPI()
bearer = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
origins = [ # Which request the API will allow
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.1.142:3000",
    "http://172.26.50.10:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def handle():
    return { "blacklisted tokens" : blacklisted_tokens }

@app.get('/v1/auth/protected')
def handle(credentials: HTTPAuthorizationCredentials = Depends(bearer)):

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not is_user_authorized(credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return { "message": "OK" }

@app.post("/v1/auth/logout")
async def handle(credentials: HTTPAuthorizationCredentials = Depends(bearer)):

    # Validate token
    if not is_user_authorized(credentials.credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Create expiration date of 2 hours
    expire = datetime.utcnow() + timedelta(minutes=1440)
    expire = expire.timestamp()
    
    # Store token and expiration in blacklisted_tokens
    blacklisted_tokens[credentials.credentials] = expire
    
    
    return { "message": "OK" }
        

@app.post("/v1/auth/login")
async def handle(user: User):        
        if not authenticate_user(user.name, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Encode user.name
        encoded_name = jwt.encode({'sub': user.name}, SECRET_KEY, algorithm="HS256")
        
        # Remove everything that not the encoded user.name
        encoded_name = encoded_name.split('.')[0]
        
        # Map the encoded user names to their corresponding keys in blacklisted tokens
        header_to_token = {key.split(".")[0]: key for key in blacklisted_tokens}
        
        # Is user.name (encoded in HS256) present in the map?
        if encoded_name in header_to_token:
  
            # Delete blacklisted token
            del blacklisted_tokens[header_to_token[encoded_name]]
            
        
        # Generate new HS256 access token
        token = generate_access_token(data={"sub": user.name})
        return {"access_token": token, "token_type": "bearer"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Placeholder for validating the password
    if len(plain_password) < 3:
        return False
    return pwd_context.verify(plain_password, hashed_password) # True/False depends if both hashes passwords matches

def authenticate_user(username: str, password: str):
    if username not in fake_users_db:
        return False
    if not verify_password(password, fake_users_db[username]['hashed_password']):
        return False
    return True

def is_user_authorized(access_token: str):
    try:
        # Decode access token
        payload = decode_access_token(access_token)

        # Decode username from payload
        username = payload.get('sub')

        if username is None or access_token in blacklisted_tokens:
            return False
        return True
    except JWTError:
        return False
    except AttributeError:
        return False

def generate_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(encoded_jwt: str):
    return jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)