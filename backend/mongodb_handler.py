import pymongo, certifi
from typing import Union
from bson.objectid import ObjectId


MONGODB_USERNAME="admin"
MONGODB_PASSWORD="kmEuqHYeiWydyKpc"
connection_url = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster.eoaspgc.mongodb.net/?retryWrites=true&w=majority" 


class MongoDB:
    def __init__(self) -> None:
        certify = certifi.where() # NOTE: some reason, not all users can connect without this (from xX_Simon_Xx)
        client = pymongo.MongoClient(connection_url, tlsCAFile=certify)
        database = client.get_database('Backend')
        self.users_collection = database.get_collection('Users')
        self.relays_collection = database.get_collection('Relays')
        self.jwt_blacklist_collection = database.get_collection('JWT Blacklist')

    def user_exist(self, name_dict: dict[str, str] = None) -> Union[dict, None]:
        if len(name_dict) > 1 or len(name_dict) == 0: #NOTE: dict must only have one key-val pair 
            return
        if 'name' not in name_dict.keys(): #NOTE: dict must be { "name": ... }
            return
        return self.users_collection.find_one(name_dict)

    def insert_relay_instance(self, relay_name) -> ObjectId: #NOTE: Insert new instance of a relay to document with no data for now
        relay = self.relays_collection.insert_one({'name': relay_name})
        return relay.inserted_id


    def delete_relay_instance(self, _id) -> None:
        self.relays_collection.delete_one({'_id' : ObjectId(_id)})

    def relay_id_filter(self, _id) -> str: 
        relay_id = _id[-4:]
        return relay_id



    
    
if __name__ == '__main__':
    mongo = MongoDB()
    #print(mongo.user_exist(name_dict={'name': 'JohnWick'}))
    #_id = mongo.insert_relay_instance()
    print(mongo.relay_id("642c0810707dfacc27b750e8"))