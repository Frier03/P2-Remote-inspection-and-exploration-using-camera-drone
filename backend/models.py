from pydantic import BaseModel

class RelayHandshakeModel(BaseModel):
    name: str
    password: str
    
class RelayHeartbeatModel(BaseModel):
    name: str

class DroneModel(BaseModel):
    name: str
    parent: str
    
class TokenModel(BaseModel):
    access_token: str
    token_type: str
    
class UserModel(BaseModel):
    name: str
    password: str

class NewCMDModel(BaseModel):
    relay_name: str
    drone_name: str
    cmd: str
