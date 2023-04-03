import pymongo
MONGODB_USERNAME="admin"
MONGODB_PASSWORD="kmEuqHYeiWydyKpc"


connection_url = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster.eoaspgc.mongodb.net/?retryWrites=true&w=majority"
print(connection_url)
client = pymongo.MongoClient(connection_url)
database = client['Backend']
print(database.list_collection_names())