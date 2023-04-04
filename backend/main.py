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
from mongodb_handler import MongoDB
from relaybox import Relay

SECRET_KEY = str(getenv('SECRET_KEY'))

blacklisted_tokens = {} #NOTE: Use database

active_relays = {}

routes_with_authorization = [
    "/v1/auth/protected",
    "/v1/auth/logout",
    "/v1/auth/relay/new_drone"
]

class TokenModel(BaseModel):
    access_token: str
    token_type: str

class UserModel(BaseModel):
    name: str
    password: str

class RelayModel(BaseModel):
    name: str
    password: str

class NewDroneModel(BaseModel):
    name: str
    parent: str


app = FastAPI()
app = add_origins(app)

bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt_sha256"]) # Apparently more secure than just bcrypt

mongo = MongoDB()
mongo.connect(mongodb_username="admin", mongodb_password="kmEuqHYeiWydyKpc")

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
        new_access_token = generate_access_token(data={"sub": username}, minutes=24*60)

        # Edit authorization header with new access token
        response.headers['WWW-Authenticate'] = f"Bearer {new_access_token}"

    # Create expiration date of 24 hours
    expire = datetime.utcnow() + timedelta(minutes=24*60)
    expire = expire.timestamp()
    
    # Store token and expiration in blacklisted_tokens
    blacklisted_tokens[expire] = access_token

    return response

# Relaybox
@app.post("/v1/auth/relay/new_drone")
def handle(drone: NewDroneModel):
    # Check if drones parent (relay) is online/exist
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Find that relay object now
    relay = active_relays[drone.parent]
    
    # Add new drone to relay
    relay.add_drone(drone.name)
    print(relay.drones[drone.name].name)
    
    # Get available ports!
    ...
    return { "ports": {
        "UDP": 2222,
        "BACKEND": 2223
    } }
    
# Relaybox
@app.post("/v1/auth/relay/handshake")
def handle(relay: RelayModel):
    if not authenticate_relay(relay):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)

    # Initialize new Relaybox Class
    relay = Relay(relay.name)

    # Store new active relay
    active_relays[relay.name] = relay

    # Generate new HS256 access token
    token = generate_access_token(data={'sub': relay.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}

# Frontend
@app.get("/v1/auth/protected")
def handle():
    return { "message": "Authorized" }

# Frontend
@app.post("/v1/auth/logout")
async def handle():
    return { "message": "Logout" }

# Frontend
@app.post("/v1/auth/login")
async def handle(user: UserModel):
    if not authenticate_user(user):
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

def authenticate_user(user: UserModel):
    user_exist = mongo.name_exist({ 'name': user.name }, mongo.users_collection)
    if not user_exist:
        return False
    if not verify_password(user.password, user_exist.get('hashed_password')):
        return False
    return True

def authenticate_relay(relay: RelayModel) -> bool:
    relay_exist = mongo.name_exist({ 'name': relay.name }, mongo.relays_collection)
    if not relay_exist:
        return False
    if not verify_password(relay.password, relay_exist.get('hashed_password')):
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

def generate_access_token(data: dict, minutes: int) -> TokenModel: # Is this right returntype?
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