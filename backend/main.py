#uvicorn main:app --reload
#pip install "python-jose[cryptography]"
#pip install "passlib[bcrypt]"
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt #jwt & pyjwt
from passlib.context import CryptContext
from pydantic import BaseModel

from starlette.responses import HTMLResponse as starletteHTMLResponse 
from os import getenv

from frontend_origins import add_origins

SECRET_KEY = str(getenv('SECRET_KEY'))

fake_users_db = { #TODO: Use MongoDB
    "admin": {
        "name": "admin",
        "hashed_password": "$2b$12$mE3KlrNxXcdb7Hn4g3Je2ulIcXwQj/vhLa8ez412aojaSJGf/5VIG" #123
    }
}

blacklisted_tokens = {} #NOTE: Use database

routes_with_middleware = [
    "/v1/auth/protected",
    "/v1/auth/logout"
]

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    name: str
    password: str


app = FastAPI()
bearer = HTTPBearer()
app = add_origins(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.middleware("http")
async def authorization(request: Request, call_next):
    # Routes with no authentication
    if request.url.path not in routes_with_middleware: # Routes with no authentication
        return await call_next(request)
    
    # Get access token from headers
    access_token = request.headers.get('authorization')

    # If no access_token declared, raise 401
    if access_token is None:
        return starletteHTMLResponse(status_code=401)
    
    # Try split "Bearer" from access_token
    try:
        access_token = access_token.split("Bearer ")[1]
    except (ValueError, IndexError): # If token is not formatted correctly
        return starletteHTMLResponse(status_code=400)
    
    # Is token blacklisted?
    if access_token in blacklisted_tokens.values():
        return starletteHTMLResponse(status_code=401)
    
    # Is user not authorized with this access token
    if not is_user_authorized(access_token):
        return starletteHTMLResponse(status_code=401)
    
    # Await endpoint
    response = await call_next(request)

    if request.url.path != "/v1/auth/logout":
        # Decode access token
        payload = decode_access_token(access_token)
        username = payload.get('sub')

        # Generate new HS256 access token
        new_access_token = generate_access_token(data={"sub": username})

        # Edit authorization header with new access token
        response.headers['WWW-Authenticate'] = f"Bearer {new_access_token}"

    # Create expiration date of 24 hours
    expire = datetime.utcnow() + timedelta(minutes=24*60)
    expire = expire.timestamp()
    
    # Store token and expiration in blacklisted_tokens
    blacklisted_tokens[expire] = access_token

    return response

@app.get('/')
def handle():
    return { "blacklisted tokens": blacklisted_tokens }

@app.get("/v1/auth/protected")
def handle():
    return { "message": "Authorized" }

@app.post("/v1/auth/logout")
async def handle():
    return { "message": "Logout" }


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


def verify_password(plain_password: str, hashed_password: str) -> bool: #TODO Make this more secure
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
    except (JWTError, AttributeError):
        return False

def generate_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=24*60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(encoded_jwt: str):
    try:
        return jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=JWTError)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)