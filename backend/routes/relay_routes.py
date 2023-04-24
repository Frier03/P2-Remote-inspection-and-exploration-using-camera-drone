from fastapi import HTTPException, status, APIRouter, Depends

from helper_functions import generate_access_token
from mongodb_handler import get_mongo
from models import DroneModel, RelayHandshakeModel
from relaybox import Relay

import threading
from VideoServerClass import video_server

relay_router = APIRouter()
active_relays = {}

@relay_router.post("/")
def handle():
    result = {}
    for relay_key in active_relays.keys():
        relay = active_relays[relay_key]
        result[relay_key] = { "drones": relay.drones }
        
    return result

@relay_router.get("/heartbeat")
def handle(relay: RelayHandshakeModel):
    print(f"(!) Heartbeat from {relay.name}")
    print(f"(!) Retrieving all data related to {relay.name}")
    
    data = active_relays.get(relay.name)
    return { "message": f"Hello {relay.name}", f"{relay.name}": { "drones": data.drones } }

@relay_router.post("/drone/disconnected")
def handle(drone: DroneModel):
    # Check if drones parent (relay) is not online/exist
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if drone name does not exist in the relay drones list
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT)
    
    # Find that relay object now
    relay = active_relays[drone.parent]

    # Delete the drone object on relay drones
    del relay.drones[drone.name]

    return { "message": f"Deleted {drone.name} on {relay.name}"}


@relay_router.post("/drones")
def handle(relay: RelayHandshakeModel):
    # Check if relay is online/exist
    if relay.name not in active_relays.keys():
        raise HTTPException(
            detail=f"{relay.name} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # Find that relay object now
    relay = active_relays[relay.name]

    result = {}
    for drone_key in relay.drones.keys():
        drone = relay.drones[drone_key]
        result[drone_key] = { "name": drone.name, "ports": drone.ports }
    
    return result

@relay_router.get("/new_drone")
def handle(drone: DroneModel):
    # Check if drones parent (relay) is not online/exist
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if drone name already exist in the relay drones list
    if drone.name in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} already exist or online",
            status_code=status.HTTP_409_CONFLICT)
        
    # Find that relay object now
    relay = active_relays[drone.parent]
    
    # Add new drone to relay and get available port
    port = relay.add_drone(drone.name)

    # Create a Server instance which handles the video connection
    udp_object = video_server(UDP_port = port)
    stream_thread = threading.Thread(target=udp_object.start(), args=())
    stream_thread.start()

    #print(relay.drones[drone.name].name)
    return { "video_port": port }
    

@relay_router.post("/handshake")
def handle(relay: RelayHandshakeModel, mongo: object = Depends(get_mongo)):
    if not mongo.authenticate(relay):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)

    # Initialize new Relaybox Class
    relay = Relay(relay.name, active_relays)

    # Store new active relay
    active_relays[relay.name] = relay

    # Generate new HS256 access token
    token = generate_access_token(data={'sub': relay.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}