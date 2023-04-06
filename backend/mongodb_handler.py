import pymongo, certifi
from typing import Union
from helper_functions import verify_password
from models import RelayHandshakeModel, UserModel

class MongoDB:
    def __init__(self) -> None:
        self.client: object = None
        self.users_collection: object = None
        self.relays_collection: object = None
        
    def connect(self, mongodb_username: str, mongodb_password: str):
        certify = certifi.where() # NOTE: some reason, not all users can connect without this
        connection_url = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster.eoaspgc.mongodb.net/?retryWrites=true&w=majority" 

        self.client = pymongo.MongoClient(connection_url, tlsCAFile=certify)
        database = self.client.get_database('Backend')
        self.users_collection = database.get_collection('Users')
        self.relays_collection = database.get_collection('Relays')
        set_mongo(self)
        
    def name_exist(self, name_dict: dict[str, str], collection: object) -> Union[dict, None]:
        if len(name_dict) > 1 or len(name_dict) == 0: #NOTE: dict must only have one key-val pair 
            return
        if 'name' not in name_dict.keys(): #NOTE: dict must be { "name": ... }
            return
        return collection.find_one(name_dict)
    
    def authenticate(self, subject: Union[UserModel, RelayHandshakeModel], mongo: object) -> bool:
        if isinstance(subject, RelayHandshakeModel):
            collection = mongo.relays_collection
        elif isinstance(subject, UserModel):
            collection = mongo.users_collection

        query = { 'name': subject.name }
        subject_exist = collection.find_one(query)

        if not subject_exist:
            return False
        if not verify_password(subject.password, subject_exist.get('hashed_password')):
            return False
        return True

# Essential when working with Dependencies in main.py @ relay_router and frontend_router 
def set_mongo(object):
    global mongo
    mongo = object
def get_mongo():
    return mongo

if __name__ == '__main__':
    mongo = MongoDB()
    mongo.connect(mongodb_username="admin", mongodb_password="kmEuqHYeiWydyKpc")
    
    user = mongo.name_exist({ 'name': 'JohnWick' }, mongo.users_collection)
    print("Hello World")