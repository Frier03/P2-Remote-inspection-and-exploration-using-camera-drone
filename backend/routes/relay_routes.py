from fastapi import HTTPException, status, APIRouter, Depends, Response
import time, copy

from helper_functions import generate_access_token
from mongodb_handler import get_mongo
from models import DroneModel, RelayHandshakeModel, RelayHeartbeatModel, DroneStatusInformationModel
from relaybox import Relay
from VideoServerClass import video_server

relay_router = APIRouter()
active_relays = {} #structured as {relay_name: relay_object}
active_sessions = {} #Structured as {port: server_object}


@relay_router.post("/")
def handle():
    pass

@relay_router.post('/drone/status_information')
def handle(drone: DroneStatusInformationModel):
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

    # get status information from drone model
    status_information = drone.status_information
    
    # Find that drone object now
    drone = relay.drones[drone.name]

    # Update drone object with status information
    drone.status_information = status_information

    return { "message": "OK" }

@relay_router.get('/drone/should_takeoff')
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
    
    # Find that drone object now
    drone = relay.drones[drone.name]

    if not drone.should_takeoff:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Drone should not take off"
        )
    
    try:
        return { "message": "OK" }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    finally:
        drone.should_takeoff = False

@relay_router.post('/drone/successful_takeoff')
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
    
    # Find that drone object now
    drone = relay.drones[drone.name]

    return { "message": "OK" }


@relay_router.get('/cmd_queue')
def handle(relay: RelayHeartbeatModel): # Relay wants every drone cmd_queue that is linked to him
    if relay.name not in active_relays.keys(): # invalid relay name? or not active?
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relay not found",
    )

    drones_cmd = {} # { "drone_01": [vel], "drone_02": [vel]}
    for drone in active_relays[relay.name].drones.values():
        drones_cmd[drone.name] = drone.cmd_queue

    return drones_cmd


@relay_router.get("/heartbeat")
def handle(relay: RelayHeartbeatModel): # Relay should send a heartbeat every 2sec

    # Get utc since 1970
    utc: int = int(time.time())

    # Get specific relay object for the relay who made the heartbeat
    relay = active_relays[relay.name]
    relay.last_heartbeat_received = utc

    print(f"(!) Heartbeat from {relay.name} | timestamp {utc}")
    print(f"(!) Retrieving all data related to {relay.name}")
    
    data = active_relays.get(relay.name)

    return { "message": f"Hello {relay.name}", f"{relay.name}": { "drones": data.drones } }

def timeout_check(relay):
    print(f"Entered Timout Check for {relay}")
    while True:
        if relay.last_heartbeat_received != None:
            time_stamp = copy.deepcopy(relay.last_heartbeat_received)
            time.sleep(5) #Allow a 5 second timeout
            if relay.last_heartbeat_received == time_stamp:
                print(f"Relaybox {relay.name} has Timed Out. Disconnecting items.\n")

                # Remove and Disconnect Every drone connected to the specific relay
                reference_dictionary = relay.drones.copy()

                # We make a copy to avoid iteration through a changing dictionary (Drones are being removed from relay.drones)
                for drone_name in reference_dictionary.keys():
                    disconnect_drone(relay, drone_name)
                
                # Remove Relay object and from active sessions
                active_relays.pop(relay.name)

                del relay
                print(f"Active Relays: {active_relays.keys()} \nActive Sessions: {active_sessions.keys()}\n")
                break


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

    # Call Disconnect function
    disconnect_drone(relay, drone.name)

def disconnect_drone(relay, drone_name): #Includes relay object and specific drone name for compatibility in relay timeout

    # Find the specific port belonging to this drone
    port = relay.drones[drone_name].port

    #Find the specific server object in session dictionary: {'port': objectId}
    server_object = active_sessions[port]

    #Close Socket in the server session
    try:
        print(f"Closing Socket belonging to {server_object}\n")
        server_object.drone_on = False #Stop all continued processing
        server_object.udp_sock.close() #Close the socket and handle exceptions in object
    except:
        print("Could not close socket in Video Server Instance")

    #Delete Server Session Object
    del server_object

    #Remove session from dictionary
    active_sessions.pop(port)
    print(f"Active Relays: {active_relays.keys()} \nActive Sessions: {active_sessions.keys()}\n")
    
    # Delete the drone object on relay drones
    del relay.drones[drone_name]

    return { "message": f"Deleted {drone_name} on {relay.name}"}


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
        result[drone_key] = { "name": drone.name, "port": drone.port }
    
    return result


@relay_router.get("/new_drone")
def handle(drone: DroneModel):
    drone_exists = False

    # Check if drones parent (relay) is not online/exist
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            detail=f"{drone.parent} does not exist or is not online",
            status_code=status.HTTP_400_BAD_REQUEST)
    
    # Check if drone name already exist in the relay drones list
    if drone.name in active_relays[drone.parent].drones:
        drone_exists = True # Marks that the drone is already in the system (In the case that the relay disconnects and reconnects within 2 seconds)
        
    # Find that relay object now
    relay = active_relays[drone.parent]
    
    if drone_exists == True:
        # Remove Exisiting Drone From the System
        print("Removing Existing Drone From System because of relaybox reconnect\n")
        disconnect_drone(relay, drone.name)

    # Add new drone to relay and get available port
    port = relay.add_drone(drone.name)
    print(f"Drone Port {port}")

    # Create a Server instance which handles the video connection
    video_feed_instance = video_server(UDP_port = port)

    #Add object and port to dictionary
    active_sessions[port] = video_feed_instance
    print(f"Active Sessions: {active_sessions}\n")

    #print(relay.drones[drone.name].name)
    return { "video_port": port }
    

@relay_router.post("/handshake")
def handle(relay: RelayHandshakeModel, mongo: object = Depends(get_mongo)):
    if not mongo.authenticate(relay):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)

    if relay.name not in active_relays: #If the Relay box quickly disconnected and reconnected within 5 seconds
        print("New Relay Box Connected \n")
        # Initialize new Relaybox Class
        relay = Relay(relay.name, active_relays)

        # Store new active relay
        active_relays[relay.name] = relay

        timeout_thread = threading.Thread(target=timeout_check, args=(relay,))
        timeout_thread.start()
    else:
        print("Existing Relay Box Connected \n")

    # Generate new HS256 access token
    token = generate_access_token(data={'sub': relay.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}