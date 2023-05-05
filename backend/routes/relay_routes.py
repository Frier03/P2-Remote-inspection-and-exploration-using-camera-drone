'''The FastAPI routes for the Drone Relay URLs.

This module defines the FastAPI routes and handlers for the drone relay URLs, including the following endpoints:

Routes:
    - /handshake: Handle the handshake process between a relay and the backend.
    - /heartbeat:
    - /cmd_queue:
    - /new_drone: Add a new drone to an existing relay. Returns an available video port for video streaming.
    - /drones: Returns information about all drones currently connected to a relay.
    - /drone/status_information:
    - /drone/should_land:
    - /drone/successful_land:
    - /drone/should_takeoff:
    - /drone/successful_takeoff:
    - /drone/disconnected: Remove a drone from a relay and close the socket connection with the drone.

Note: 
    The code in this module is not a complete implementation of the Drone Relay service. Some parts have been omitted or simplified for clarity.
'''

# Default Python
import threading, time, copy

# FastAPI
from fastapi import (
    HTTPException, 
    APIRouter,
    status, 
    Depends 
)

# For JWT token.
from helper_functions import generate_access_token

# Database. This is how to use MongoBD.
from mongodb_handler import get_mongo

# Own Pydantic models.
from models import (
    DroneModel, 
    RelayHandshakeModel, 
    RelayHeartbeatModel, 
    DroneStatusInformationModel
)

# Own Relay class
from relaybox import Relay

# Own class for drone video
from drone_video_stream import DroneVideoStream

relay_router = APIRouter()
active_relays: dict[str, Relay] = {}
active_sessions: dict[int, DroneVideoStream] = {}



@relay_router.post("/handshake")
def handle(
    relay: RelayHandshakeModel, 
    mongo: object = Depends(get_mongo)
):
    """Handle the handshake process between a relay and the backend.

    Args:
        relay (RelayHandshakeModel): A Pydantic model representing a relay.
        mongo (MongoDB): A MongoDB object.

    Returns: 
        JSON containing an access token for the relay.

    Raises:
        HTTPException(status_code=401): If the authentication fails.
    """
    # Authenticate relay
    if not mongo.authenticate(relay):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # If a new relay has handshaked
    if relay.name not in active_relays:
        # Initialize new Relaybox Class
        relay: Relay = Relay(relay.name, active_relays)

        # Store new active relay
        active_relays[relay.name]: dict[str, Relay] = relay

        timeout: threading.Thread = threading.Thread(target=timeout_check, args=(relay,))
        timeout.start()

    # Else a relay who already has handshaked
    else: 
        print("Existing Relay Box Connected")

    # Generate new access token
    token: str = generate_access_token(data={'sub': relay.name}, minutes=24*60)

    return {"access_token": f"Bearer {token}"}

@relay_router.get("/heartbeat")
def handle(relay: RelayHeartbeatModel):
    """Handles request from relay to confirm its connection using heartbeat and returns information about all drones currently connected to the relay.

    Arguments:
        relay: A RelayHeartbeatModel instance representing the relay that sent the heartbeat.

    Raises:
        HTTPException(status_code=400): If the relay name does not exist or is not online.

    Returns:
        JSON containing a greeting message and a list of all drones currently connected to the relay.
    """
    # Check if relay (drone.parent) is a valid/active relay.
    if relay.name not in active_relays.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relay not found",
    )

    # Get utc since 1970.
    utc: int = int(time.time())

    # Get specific relay object for the relay who made the heartbeat
    relay: Relay = active_relays[relay.name]

    # Update its last received heartbeat
    relay.last_heartbeat_received: int = utc

    print(f"(!) Heartbeat from {relay.name} | timestamp {utc}")
    print(f"(!) Retrieving all data related to {relay.name}")

    return { "message": f"Hello {relay.name}",
             f"{relay.name}": {"drones": relay.drones} }

@relay_router.get('/')
def handle(drone: DroneModel):
    """Returns the command queue of a drone linked to the relay.

    Arguments:
        drone (DroneModel): A data model representing the drone making the request.

    Raises:
        HTTPException(status_code=400): If the drone's parent (relay) does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.

    Returns:
        JSON containing the drone's command queue.
    
    Example:
        >>> { "message": "[0,0,0,0]" }
    """
    # Check if relay (drone.parent) is a valid/active relay.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relay not found"
    )

    # Check if drone (drone.name) is valid/active drone.   
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT)
    
    # Find that relay object now
    relay: Relay = active_relays[drone.parent]
    
    # Find that drone object now
    drone: object = relay.drones[drone.name]

    return { "message": drone.cmd_queue }

@relay_router.get("/new_drone")
def handle(drone: DroneModel):
    """Add a new drone to an existing relay. Returns an available video port for video streaming.

    Arguments:
        drone (DroneModel): A DroneModel representing a drone.

    Raises:
        HTTPException(status_code=400): If the relay name does not exist or is not online.

    Returns:
        JSON containing the video port number for the drone's video stream.

    """
    # Check if drones parent (relay) is not online/exist.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if drone name already exist in the relay drones list
    if drone.name in active_relays[drone.parent].drones:
        # Remove Exisiting Drone From the System
        print("Removing Existing Drone From System because of relaybox reconnect")
        try:
            disconnect_drone(relay, drone.name)
        except Exception:
            print("Exception")
            active_relays[drone.parent].drones.pop(drone.name) #Manually remove drone from list as it has been disconnected
        
    # Find that relay object now.
    relay: Relay = active_relays[drone.parent]

    # Add new drone to relay and get available port
    port: int = relay.add_drone(drone.name)

    # Create a Server instance which handles the video connection
    video_feed_instance: DroneVideoStream = DroneVideoStream(port)

    #Add object and port to dictionary
    active_sessions[port]: dict[int, object] = video_feed_instance

    return { "video_port": port }

@relay_router.post("/drones")
def handle(relay: RelayHandshakeModel):
    """Returns information about all drones currently connected to a relay.

    Arguments:
        relay: A RelayHandshakeModel instance representing the relay whose drones to list.

    Raises:
        HTTPException(status_code=400): If the relay name does not exist or is not online.

    Returns:
        A dictionary containing information about all drones currently connected to the relay.

    Example: 
        >>> {
                "drone_001": {
                    "name": "drone_001",
                    "port": 52333
                },
                "drone_002": {
                    "name:" "drone_002",
                    "port": 52334
                },
                ...
            }
    """
    # Check if relay is a valid/active relay.
    if relay.name not in active_relays.keys():
        raise HTTPException(
            detail=f"{relay.name} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Find that relay object now
    relay: Relay = active_relays[relay.name]

    result: dict[str, dict[str, any]] = {}

    for drone_key in relay.drones.keys():
        drone = relay.drones[drone_key]
        result[drone_key] = { "name": drone.name, "port": drone.port }
    
    return result

@relay_router.post('/drone/status_information')
def handle(drone: DroneStatusInformationModel):
    """Handles status information received from a drone.
    
    Arguments:
        drone (DroneStatusInformationModel): A data model representing status information from a drone.
    
    Raises:
        HTTPException(status_code=400): If the drone's parent relay does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.
    
    Returns:
        JSON with a success message.
    """
    # Check if relay (drone.parent) is a valid/active relay
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if drone (drone.name) is valid/active drone
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT)
    
    # Find that relay object now
    relay: Relay = active_relays[drone.parent]

    # get status information from drone model
    status_information: str = drone.status_information
    
    # Find that drone object now
    drone: object = relay.drones[drone.name]

    # Update drone object with status information
    drone.status_information: str = status_information

    return { "message": "OK" }

@relay_router.get('/drone/should_land')
def handle(drone: DroneModel):
    """Handles a request from a relay to determine if a drone should land.
    
    Arguments:
        drone (DroneModel): A data model representing the drone making the request.
    
    Raises:
        HTTPException(status_code=400): If the drone's parent relay does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.
        HTTPException(status_code=425): If the drone should not land.
    
    Yields:
        JSON containing a success message.
    """
    # Check if relay (drone.parent) is a valid/active relay.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if drone (drone.name) is valid/active drone.
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT)
    
    # Find that relay object now.
    relay: Relay = active_relays[drone.parent]
    
    # Find that drone object now.
    drone: object = relay.drones[drone.name]

    # Check if drone should not land.
    if not drone.should_land:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Drone should not land"
        )
    
    yield { "message": "OK" }

    # Now update the drone to not land.
    drone.should_land = False

@relay_router.post('/drone/successful_land')
def handle(drone: DroneModel):
    """Handles a request from a relay to indicate a successful landing from a drone.
    
    Arguments:
        drone (DroneModel): A data model representing the drone making the request.
    
    Raises:
        HTTPException(status_code=400): If the drone's parent (relay) does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.
    
    Returns:
        JSON containing a success message.
    """
    # Check if relay (drone.parent) is a valid/active relay.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if drone (drone.name) is valid/active drone.   
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT
        )
    
    # Find that relay object now.
    relay: Relay = active_relays[drone.parent]
    
    # Find that drone object now.
    drone: object = relay.drones[drone.name]

    # The drone is now longer airborn.
    drone.airborn: bool = False

    return { "message": "OK"}

@relay_router.get('/drone/should_takeoff')
def handle(drone: DroneModel):
    """Handles a request from a relay to determine if a drone should take off.
    
    Arguments:
        drone (DroneModel): A data model representing the drone making the request.
    
    Raises:
        HTTPException(status_code=400): If the drone's parent (relay) does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.
        HTTPException(status_code=425): If the drone should not take off.
    
    Yields:
        JSON containing a success message.
    """
    
    # Check if relay (drone.parent) is a valid/active relay.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if drone (drone.name) is valid/active drone.   
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT
        )
    
    # Find that relay object now
    relay: Relay = active_relays[drone.parent]
    
    # Find that drone object now
    drone: object = relay.drones[drone.name]

    # Check if drone should not take off
    if not drone.should_takeoff:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Drone should not take off"
        )
    
    # Yield OK
    yield { "message": "OK" }
    
    # The drone should no longer take off
    drone.should_takeoff: bool = False

@relay_router.post('/drone/successful_takeoff')
def handle(drone: DroneModel):
    """Handles a request from a relay to indicate a successful take off from a drone.
    
    Arguments:
        drone (DroneModel): A data model representing the drone making the request.
    
    Raises:
        HTTPException(status_code=400): If the drone's parent (relay) does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.
    
    Returns:
        JSON containing a success message.
    """
    # Check if relay (drone.parent) is a valid/active relay.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if drone (drone.name) is valid/active drone.   
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT
        )

    # Find that relay object now
    relay: Relay = active_relays[drone.parent]
    
    # Find that drone object now
    drone: object = relay.drones[drone.name]

    # The drone is now airborn.
    drone.airborn: bool = True
    
    # This is a return statement. This return statements returns a message. This message is a dict in a format of JSON. The JSON format is a one key-val pair. The key is "message". The val is "OK". This is again a return statement. Please understand that this returns a statement.👌
    return { "message": "OK" }

@relay_router.post("/drone/disconnected")
def handle(drone: DroneModel):
    """Remove a drone from a relay and closes the socket connection with the drone.

    Args:
        drone (DroneModel): A DroneModel instance representing the drone to remove.

    Raises:
        HTTPException(status_code=400): If the drone's parent (relay) does not exist or is not online.
        HTTPException(status_code=409): If the drone does not exist in the relay drones list.

    Returns:
        JSON containing a message confirming the removal of the drone.
    """
    # Check if relay (drone.parent) is a valid/active relay.
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if drone (drone.name) is valid/active drone.   
    if drone.name not in active_relays[drone.parent].drones:
        raise HTTPException(
            detail=f"{drone.name} does not exist in {active_relays[drone.parent].name}",
            status_code=status.HTTP_409_CONFLICT
        )

    # Find that relay object now.
    relay: Relay = active_relays[drone.parent]

    # Now disconnect the drone from the relay.
    disconnect_drone(relay, drone.name)

    return { "message": "OK" }
    
def timeout_check(relay: Relay) -> None:
    """Periodically checks whether a relay has timed out and removes all drones connected to the relay.

    Args:
        relay (Relay): A Relay object representing the relay to check for timeouts.
    """
    print(f"Entered Timout Check for {relay}")

    while True:
        if relay.last_heartbeat_received != None:
            TIME_STAMP = copy.deepcopy(relay.last_heartbeat_received) # We cannot change the same list while looping
            time.sleep(8) # Allow for a 5 second timeout delay.

            if relay.last_heartbeat_received == TIME_STAMP:
                print(f"Relaybox {relay.name} has Timed Out. Disconnecting items.\n")

                # Remove and disconnect every drone connected to the specific relay.
                reference_dictionary = relay.drones.copy()

                # We make a copy to avoid iteration through a changing dictionary (Drones are being removed from relay.drones)
                for drone_name in reference_dictionary.keys():
                    disconnect_drone(relay, drone_name)
                
                # Remove Relay object and from active sessions
                active_relays.pop(relay.name)

                del relay

                print(f"Active Relays: {active_relays.keys()} \nActive Sessions: {active_sessions.keys()}\n")
                break

def disconnect_drone(relay: Relay, drone_name: str) -> dict:
    """Remove a drone from a relay and closes the socket connection with the drone.

    Args:
        relay (Relay): A Relay object representing the relay from which to remove the drone.
        drone_name (str): A string representing the name of the drone to remove.

    Returns:
        A dict containing a message confirming the removal of the drone.
    """
    # Find the specific port belonging to a drone.
    PORT: int = relay.drones[drone_name].port

    #Find the specific server object in session dictionary: {'port': objectId}.
    drone_video_stream: DroneVideoStream = active_sessions[PORT]

    #Close Socket in the server session
    try:
        print(f"Closing Socket belonging to {drone_video_stream}\n")
        drone_video_stream.active = False #Stop all continued processing
        drone_video_stream.socket.close() #Close the socket and handle exceptions in object
    except:
        print("Could not close socket in Video Server Instance")

    #Delete Server Session Object
    del drone_video_stream

    #Remove session from dictionary
    active_sessions.pop(PORT)
    print(f"Active Relays: {active_relays.keys()} \nActive Sessions: {active_sessions.keys()}\n")
    
    # Delete the drone object on relay drones
    del relay.drones[drone_name]

    return { "message": f"Deleted {drone_name} on {relay.name}"}
