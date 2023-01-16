import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
_dbname = os.getenv('DBNAME')
_collection = os.getenv('COLLECTION')
CLIENT = pymongo.MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
COLLECTION = CLIENT[_dbname][_collection]
DATE_FORMAT = '%Y-%m-%d'