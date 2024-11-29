import os
from pymongo import MongoClient
from typing import Dict
from utils.logger import log

# MongoDB connection cache
_clients: Dict[str, MongoClient] = {}

def get_database(industry_id: str):
    """Get MongoDB database for specific industry."""
    if industry_id not in _clients:
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        _clients[industry_id] = MongoClient(mongodb_uri)
    
    return _clients[industry_id][f'industry_{industry_id}']

def cleanup_connections():
    """Close all MongoDB connections."""
    for client in _clients.values():
        client.close()