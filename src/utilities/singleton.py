import os
import pymongo
# Connect to database
client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
database_client = client.get_database(os.environ.get("DATABASE"))