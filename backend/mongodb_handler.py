import pymongo, certifi
MONGODB_USERNAME="admin"
MONGODB_PASSWORD="kmEuqHYeiWydyKpc"

# Needed for some computers D: - Simon 
ca = certifi.where()


connection_url = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster.eoaspgc.mongodb.net/?retryWrites=true&w=majority"
print(connection_url)

# tlsCAFile=ca is a part of the fix
client = pymongo.MongoClient(connection_url, tlsCAFile=ca)
database = client['Backend']
print(database.list_collection_names())