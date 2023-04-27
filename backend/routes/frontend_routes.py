from fastapi import HTTPException, status, APIRouter, Depends, Request
import json

from helper_functions import generate_access_token, decode_access_token
from mongodb_handler import get_mongo
from models import UserModel, NewCMDModel
from routes.relay_routes import active_relays

frontend_router = APIRouter()

@frontend_router.get("/relayboxes/all") # Retrieve all data backend has for relayboxes
def handle():
    # Find that relay object now

    result = {}
    for relay_object in active_relays.values():
        result[relay_object.name] = {}
        for drone_key in relay_object.drones.keys():
            drone = relay_object.drones[drone_key]
            result[relay_object.name][drone_key] = { "name": drone.name, "ports": drone.ports }
            
    return result

@frontend_router.post("/new_cmd_for_drone")
def handle(cmd_model: NewCMDModel): # relay_name, drone_name
    relay_name = cmd_model.relay_name
    drone_name = cmd_model.drone_name
    cmd = cmd_model.cmd
    
    if relay_name not in active_relays.keys(): # invalid relay name? or not active?
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relay not found",
        )
    
    relay = active_relays[relay_name] # gets relay object id

    if drone_name not in relay.drones.keys(): # invalid drone name?
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        )
    drone = relay.drones[drone_name] # gets drone object id from relay object id
    drone.cmd_queue.append(cmd)
    return { "message": "OK" }

@frontend_router.get("/protected")
def handle():
    return { "message": "Authorized" }

@frontend_router.post("/logout")
async def handle():
    return { "message": "Logout" }

@frontend_router.post("/login")
async def handle(user: UserModel, mongo: object = Depends(get_mongo)):
    if not mongo.authenticate(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # Generate new HS256 access token
    token = generate_access_token(data={"sub": user.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}

@frontend_router.get("/users/me")
def handle(req: Request):
    access_token = req.headers.get('authorization')
    access_token = access_token.split(' ')[1]
    # Decode access token
    payload = decode_access_token(access_token)
    
    # Decode username from payload
    username = payload.get('sub')

    return { "message": username }