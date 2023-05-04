'''Defines the Pydantic data models used for FastAPI application.

This file defines various Pydantic models (BaseModel) which are used as request/response bodies
in the FastAPI routes. BaseModels are strongtype so every endpoint needs the model. If no model 
is given FastAPI returns a field required exception (HTTP response of 422).

Models:
- RelayHandshakeModel: The Pydantic model for a Relay's handshake.
- RelayHeartbeatModel: The Pydantic model for a Relay's heartbeat.
- DroneModel: The Pydantic model for a drone.
- DroneStatusInformationModel: The Pydantic model for a drone's status information.
- TokenModel: The Pydantic model for an access token.
- UserModel: The Pydantic model for a user.
- NewCMDModel: The Pydantic model for a new command.
'''

from pydantic import BaseModel

class RelayHandshakeModel(BaseModel):
    name: str
    password: str = None


class RelayHeartbeatModel(BaseModel):
    name: str


class DroneModel(BaseModel):
    name: str
    parent: str


class DroneStatusInformationModel(BaseModel):
    name: str
    parent: str
    status_information: str


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class UserModel(BaseModel):
    name: str
    password: str


class NewCMDModel(BaseModel):
    relay_name: str
    drone_name: str
    cmd: list
