'''For talking to MongoDB.

This module defines the MongoDB class that manages the connection to a MongoDB Atlas cloud database.
It also provides helper functions to interact with user and relay collections and authenticate users.

Classes:
    MongoDB: Manages the connection to a MongoDB Atlas cloud database.

Functions:
    set_mongo: Essential when working with Dependencies in main.py @ relay_router and frontend_router.
    get_mongo: Returns the current MongoDB object.

    Both functions are not a part of the MongoDB class. See `set_mongo()` for more details.

Dependencies:
    - pymongo
    - certifi
    - helper_functions
    - models

Example:
    To use this module, simply create an instance of the MongoDB class and call the connect method with your
    MongoDB Atlas cloud database username and password. You can then use the helper functions to perform operations
    on the user and relay collections, and authenticate users.

    >>> mongo = MongoDB()
    >>> mongo.connect(mongodb_username="admin", mongodb_password="123")
    >>> user = mongo.name_exist({ 'name': 'JohnWick' }, mongo.users_collection)
'''

# PyMongoDB
import pymongo
import certifi  # For Windows users.

# Pydantic models
from models import RelayHandshakeModel, UserModel

# Own function
from helper_functions import verify_password


class MongoDB:
    """A MongoDB class to communicate to the database.

    This class is to communicate to the MongoDB.

    Example:
        >>> mongo = MongoDB()
        >>> mongo.connect(mongodb_username="admin", mongodb_password="123")
        >>> user = mongo.name_exist({ 'name': 'JohnWick' }, mongo.users_collection)
    """

    def __init__(self) -> None:
        self.client: object = None
        self.users_collection: object = None
        self.relays_collection: object = None

    def connect(self, mongodb_username: str, mongodb_password: str) -> None:
        """Connect to a database

        Args:
            mongodb_username (str): The username of the MonoDB user
            mongodb_password (str): The password

        Example:
            >>> Mongo.connect(mongodb_username="admin", mongodb_password="123")

        """
        certify = certifi.where()  # For Windows users.
        connection_url = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster.eoaspgc.mongodb.net/?retryWrites=true&w=majority"

        # Pymongo method to connect
        self.client = pymongo.MongoClient(connection_url, tlsCAFile=certify)

        # We have a document call `Backend` that we use.
        database = self.client.get_database('Backend')

        # Load `Users` into memory.
        self.users_collection = database.get_collection('Users')

        # Load `Rlays` into memory.
        self.relays_collection = database.get_collection('Relays')

        set_mongo(self)

    def name_exist(self, name_dict: dict[str: str], collection: object) -> dict | None:
        """Check if a users name is in the database.

        Args:
            name_dict (dict[str, str]): A dict like with name: `John`.
            collection (object): The MongoDB user collection.

        Returns:
            dict: With the user if found
            None: else None

        Example:
            >>> mongo.name_exist({'name': 'JohnWick'}, mongo.users_collection)
            {'name': 'JohnWick'}
        """

        # NOTE: dict must only have one key-val pair.
        if len(name_dict) > 1 or len(name_dict) == 0:
            return

        # NOTE: dict must be { "name": ... }
        if 'name' not in name_dict.keys():
            return

        # Return the user
        return collection.find_one(name_dict)

    def authenticate(self, subject: UserModel | RelayHandshakeModel) -> bool:
        """Authenticate a user or a relay.

        Args:
            subject (UserModel | RelayHandshakeModel): A usermodel or a relaymodel.

        Returns:
            bool: True if the user or relay is authenticated, False otherwise.

        Note:
            See `models.py` for more detail about the models.
        """

        # If the subject is type of RelayHandshakeModel
        if isinstance(subject, RelayHandshakeModel):
            collection: object = self.relays_collection

        # Else if the subject is type of UserModel.
        elif isinstance(subject, UserModel):
            collection: object = self.users_collection

        # Query for database.
        query: dict[str: str] = {'name': subject.name}

        # Check in the database.
        subject_exist: bool = collection.find_one(query)

        # Does the subject exist?
        if not subject_exist:
            return False

        # Does the subject have the right password?
        if not verify_password(subject.password, subject_exist.get('hashed_password')):
            return False

        # All else then they are authenticated.
        return True


# Essential when working with Dependencies in main.py @ relay_router and frontend_router
def set_mongo(instance) -> None:
    """Set MongoDB instance.

    Note:
        MongoDB instance must not be declared inside the MongoDB class.
    """
    global mongo
    mongo = instance


def get_mongo() -> MongoDB:
    """Get MongoDB instance.
    
    Note:
        See `set_mongo()` notes.
    """
    return mongo


if __name__ == '__main__':
    mongo = MongoDB()
    mongo.connect(mongodb_username="admin", mongodb_password="kmEuqHYeiWydyKpc")
    user = mongo.name_exist({'name': 'JohnWick'}, mongo.users_collection)
