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
    status_information: bytes
    
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
