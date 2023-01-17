import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
_dbname = os.getenv('DBNAME')
_puzzle_collection = os.getenv('PUZZLE_COLLECTION')
_id_collection = os.getenv('ID_COLLECTION')
CLIENT = pymongo.MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
PUZZLE_COLLECTION = CLIENT[_dbname][_puzzle_collection]
ID_COLLECTION = CLIENT[_dbname][_id_collection]
DATE_FORMAT = '%Y-%m-%d'