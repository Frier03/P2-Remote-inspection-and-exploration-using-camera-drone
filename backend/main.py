#uvicorn main:app --reload
#pip install "python-jose[cryptography]"
#pip install "passlib[bcrypt]"
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt #jwt & pyjwt
from passlib.context import CryptContext
from pydantic import BaseModel

from starlette.responses import HTMLResponse as starletteHTMLResponse 
from os import getenv

from frontend_origins import add_origins

SECRET_KEY = str(getenv('SECRET_KEY'))

fake_users_db = { #NOTE: Use database
    "admin": {
        "name": "admin",
        "hashed_password": "$bcrypt-sha256$v=2,t=2b,r=12$2716btCwy5q5DcTX9qpMXe$quQWVYmOTtSjC/xT3n7ZXXRgxgL0Th2" #123
    }
}

fake_relay_db = {
    "Relay_4444": ...,
    "Relay_4445": "21313"
}

fake_relay_db = {
    ObjectId: {
        "name": "Relay_4444",
        "key": "biow2hrf9283h892r2h",
        "drones": [
            {
                "ID": "Drone1",
                "LOCAL_IP": "192.168.1.1",
                "other": "data"
            },
            {
                "ID": "Drone2",
                "LOCAL_IP": "192.168.1.2",
                "other": "data"
            },
            {
                "ID": "Drone3",
                "LOCAL_IP": "192.168.1.3",
                "other": "data"
            },
        ]
    },

    ObjectId: {
        "name": "Relay_4446",
        "key": "tuf63f73jt9j3jt6dj",
        "drones": [
            {
                "ID": "Drone1",
                "LOCAL_IP": "192.168.1.1",
                "other": "data"
            },
            {
                "ID": "Drone2",
                "LOCAL_IP": "192.168.1.2",
                "other": "data"
            },
            {
                "ID": "Drone3",
                "LOCAL_IP": "192.168.1.3",
                "other": "data"
            },
        ]
    },
}


blacklisted_tokens = {} #NOTE: Use database

routes_with_authorization = [
    "/v1/auth/protected",
    "/v1/auth/logout"
]

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    name: str
    password: str

class RelayHandshake(BaseModel):
    id: int
    key: str


app = FastAPI()
app = add_origins(app)
bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt_sha256"]) # Apparently more secure than just bcrypt

@app.middleware("http")
async def authorization(request: Request, call_next):
    # Routes with no authentication
    if request.url.path not in routes_with_authorization: # Routes with no authentication
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

@app.post("/v1/api/relay/")
def handle(request: Request):

    # Get json from relaybox from the internet
    payload = request.json()
    name = payload.get('name')
    # key = payload.get('key')
    
    # Validate key

    drones = payload.get('drones')

    # What happens when a drone connects to n relaybox?
    # We need to know the id for the relaybox
    
    ...

@app.post("/v1/auth/ports/relay") # <-- after handshake?
def handle():
    ...

@app.post("/v1/auth/login/relay") # First handshake from relay to backend
def handle(relay: RelayHandshake):
    
    # If relay basemodel has no information
    if not relay:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # If relay key or id is not authorized #NOTE: Vent med det
    #if not authenticate_relay(relay):
    #     raise HTTPException(
    #        status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Generate new HS256 access token
    token = generate_access_token(data={'sub': relay.id}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}


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
        
    # Generate new HS256 access token
    token = generate_access_token(data={"sub": user.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}


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

def authenticate_relay(relay: RelayHandshake) -> bool:
    if relay.id not in fake_relay_db:
        return False
    
    if relay.key != fake_relay_db[relay.id]['key']:
        return False

    return True

def is_user_authorized(access_token: str) -> bool:
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

def generate_access_token(data: dict, minutes: int) -> Token: # Is this right returntype?
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)