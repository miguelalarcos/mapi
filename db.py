import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv('.env')

MONGO_URL = os.getenv("MONGO_URL")
DATA_BASE= os.getenv("DATA_BASE")
print(MONGO_URL, DATA_BASE)
client = MongoClient(MONGO_URL)
db = client[DATA_BASE]