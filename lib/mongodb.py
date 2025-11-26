# lib/mongodb.py

from pymongo import MongoClient
from flask import Flask
import os

db = None

def init_db(app: Flask):
    """Initialize MongoDB connection"""
    global db
    
    try:
        uri = os.getenv('MONGODB_URI')
        
        if not uri:
            raise ValueError("MONGODB_URI is not set in environment variables")
        
        # Extract database name from URI or use default
        if '/ayudabesh' in uri:
            db_name = 'ayudabesh'
        else:
            # If URI doesn't specify database, use ayudabesh as default
            db_name = 'ayudabesh'
            # Append database name to URI if not present
            if uri.endswith('/') or ':' in uri.split('/')[-1]:
                uri = uri.rstrip('/') + '/ayudabesh'
        
        client = MongoClient(uri)
        db = client[db_name]
        client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB database: {db_name}")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise


def get_database():
    """Returns the MongoDB database instance"""
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first in your app startup.")
    return db