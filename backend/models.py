from pydantic import BaseModel
class RelayHandshakeModel(BaseModel):
    name: str
    password: str = None

class DroneModel(BaseModel):
    name: str
    parent: str
    
class TokenModel(BaseModel):
    access_token: str
    token_type: str
    
class UserModel(BaseModel):
    name: str
    password: str