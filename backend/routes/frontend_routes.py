'''
This module contains API routes for controlling drones and accessing data on active relays.
The prefix for all of this is `/v1/api/frontend`.

Routes:
    - /protected: Returns a JSON message indicating successful authorization
    - /login: Authenticates user credentials and generates a new access token
    - /logout: Returns a JSON message indicating successful logout

    - /users/me: Retrieves the current user's username from the access token

    - /relayboxes/all: Retrieves all data the backend has for active relayboxes

    - /drone/takeoff: Sends a command to a drone to take off
    - /drone/land: Sends a command to a drone to land
    - /drone/new_command: Sends a new command to a drone
'''

# FastAPI 
from fastapi import (
    HTTPException,
    APIRouter, # Just like `app = FastAPI()`
    status, # Status code. example `400`
    Depends, 
    Request
)

# The dict for active relays. Se `main.py` for more information.
from routes.relay_routes import active_relays

# Own Pydantic models
from models import (
    UserModel, 
    NewCMDModel, 
    DroneModel
)

# Own functions for JWT
from helper_functions import (
    generate_access_token,
    decode_access_token
)
# Database. This is how to use MongoBD
from mongodb_handler import get_mongo


frontend_router = APIRouter()

@frontend_router.get("/protected")
def handle():
    """Returns a JSON message indicating successful authorization.

    Returns:
        JSON containing a message indicating successful authorization.
        
    Note:
        The logic of logout is a part of `middleware.py`. See it for more detail.
    """
    return { "message": "Authorized" }

@frontend_router.post("/login")
def handle(user: UserModel, mongo: object = Depends(get_mongo)):
    """Authenticates user credentials and generates a new access token.

    Args:
        user (UserModel): A UserModel object representing the user's credentials.
            Se `models.py` for more detail.
        mongo (MongoDB): An MongoDB object representing the MongoDB database connection.

    Raises:
        HTTPException with status code 401, if the provided credentials are invalid.

    Returns:
        JSON containing a new access token.
    """
    if not mongo.authenticate(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"} # Indicate to the client that the access token of type Bearer is required.
        )
        
    # Generate new HS256 access token
    token = generate_access_token(data={"sub": user.name}, minutes=24*60)

    return {"access_token": f"Bearer {token}"}

@frontend_router.post("/logout")
def handle():
    """Returns a JSON message indicating successful logout.

    Returns:
        JSON containing a message indicating successful logout.
    
    Note:
        The logic of logout is a part of `middleware.py`. See it for more detail.
    """
    return { "message": "Logout" }

@frontend_router.get("/users/me")
def handle(req: Request):
    """Retrieves the current user's username from the access token.

    Args:
        req (Request): A Request object representing the current request.

    Returns:
        JSON containing the current user's username.
    """
    # Get the authorization from the html header
    access_header = req.headers.get('authorization')

    # Get the JWT token 
    access_token = access_header.split(' ')[1]
    
    # Decode access token
    payload = decode_access_token(access_token)
    
    # Decode username from payload
    username = payload.get('sub')

    return { "message": username }

@frontend_router.get("/relayboxes/all")
def handle():
    """Retrieves all data the backend has for active relayboxes.

    Returns:
        JSON containing data for each active relaybox and its associated drones.
    
    Example:
        >>> {
                "relay_0001": {
                    "name": "relay_0001",
                    "drones": [
                        "drone_001": {
                            "name": "drone_001",
                            "port": 53222,
                            "airborn": False,
                            "status_information": str
                        },
                        "drone_002": {
                            "name": "drone_002",
                            "port": 53223,
                            "airborn": False,
                            "status_information": str
                        }
                    ]
                }
            }
    """
    result: dict = {}
    
    # Get every relay object in active_relays
    for relay_object in active_relays.values():
        result[relay_object.name]: dict[str, any] = {}
        
        # Get every drone object for a relay object
        for drone_key in relay_object.drones.keys():
            drone: object = relay_object.drones[drone_key]
            
            # Append the attributes to the result dict.
            result[relay_object.name][drone_key]: dict = { 
                "name": drone.name, 
                "port": drone.port, 
                "airborn": drone.airborn,
                "status_information": drone.status_information
            }
    
    return result

@frontend_router.post("/drone/takeoff")
def handle(drone: DroneModel):
    """Flag a drone to take off.

    Args:
        drone (DroneModel): A DroneModel object representing the drone to command.

    Raises:
        HTTPException with status code 404, if the specified relay or drone is not found.
        HTTPException with status code 208, if the specified drone is already trying to take off.

    Returns:
        JSON containing a message indicating successful command transmission.
    
    Note: 
        See `models.py` for more detail.
    """
    # Check if relay (drone.parent) is a valid/active relay
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relay not found"
        )
    
    # Get relay object
    relay: object = active_relays[drone.parent]

    # Check if drone (drone.name) is valid/active drone
    if drone.name not in relay.drones.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        )
    
    # Get drone object
    drone: object = relay.drones[drone.name]

    # Is drone already trying to takeoff?
    if drone.should_takeoff:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail="Drone is already trying to take off"
        )
        
    # Is drone already airborne?
    if drone.airborn:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Drone is already airborn"
        )
    
    # Now the drone should take off.
    drone.should_takeoff = True
 
    return { "message": "ok"}

@frontend_router.post("/drone/land")
def handle(drone: DroneModel):
    """Flag a drone to land.

    Args:
        drone (DroneModel): A DroneModel object representing the drone to command.

    Raises:
        HTTPException with status code 404, if the specified relay or drone is not found.
        HTTPException with status code 208, if the specified drone is already trying to land.

    Returns:
        JSON containing a message indicating successful command transmission.
    
    Note: 
        See `models.py` for more detail.
    """
    # Check if relay (drone.parent) is a valid/active relay
    if drone.parent not in active_relays.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relay not found"
        )
    
    # Get relay object
    relay: object = active_relays[drone.parent]

    # Check if drone (drone.name) is valid/active drone
    if drone.name not in relay.drones.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        )
    
    # Get drone object
    drone: object = relay.drones[drone.name]

    # Is drone already trying to takeoff?
    if drone.should_land:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail="Drone is already trying to land"
        )
        
    # Is drone already airborne?
    if not drone.airborn:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Drone is not airborne"
        )

    # Now the drone should land.
    drone.should_land = True

    return { "message": "ok"}


@frontend_router.post("/drone/new_command")
def handle(cmd_model: NewCMDModel):
    """Updates new command to a drones command queue.

    Args:
        cmd_model (NewCMDModel): A NewCMDModel object representing the new command to send to the drone.

    Raises:
        HTTPException with status code 404: If the specified relay or drone is not found.
        HTTPException with status code 425: If the specified drone is not airborn.

    Returns:
        JSON containing a message indicating successful command transmission.
    
    Note:
        See `models.py` for more detail about model.
    """

    # Simplify syntax
    relay_name: str = cmd_model.relay_name
    drone_name: str = cmd_model.drone_name
    cmd: list[int, int, int, int] = cmd_model.cmd
    
    # Check if relay (drone.parent) is a valid/active relay
    if relay_name not in active_relays.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relay not found"
        )
    
    # Get relay object
    relay: object = active_relays[relay_name]

    # Check if drone (drone.name) is valid/active drone
    if drone_name not in relay.drones.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        )
    
    # Get drone object
    drone: object = relay.drones[drone_name]

    # Is drone not airborne?
    if not drone.airborn:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Drone is not airborn"
        )

    # Update the drones command queue.
    drone.cmd_queue = cmd

    return { "message": "OK" }
