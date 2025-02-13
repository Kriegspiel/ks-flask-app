import os
from flask_pymongo import PyMongo

mongo = PyMongo() 
    
def get_db_uri(db_name):
    return f"mongodb://{os.environ.get('MONGO_USERNAME')}:{os.environ.get('MONGO_PASSWORD')}@mongo:27017/{db_name}"
