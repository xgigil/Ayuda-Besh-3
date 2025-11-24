# lib/auth.py

import os
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from lib.mongodb import get_database
from bson.objectid import ObjectId

SECRET_KEY = os.getenv('SECRET_KEY', 'JesmundIvanClariceGailMayeoh!')

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, password)

def generate_token(user_id: str, role: str, expires_in: int = None) -> str:
    """Generate a JWT token that includes user role"""
    if expires_in is None:
        expires_str = os.getenv('JWT_EXPIRATION', '3600')
        try:
            expires_in = int(expires_str)
        except (ValueError, TypeError):
            expires_in = 3600

    payload = {
        'user_id': str(user_id),
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_user_from_token(token: str) -> dict:
    payload = verify_token(token)
    if not payload:
        return None
    
    try:
        db = get_database()
        user_id = payload.get('user_id')
        if not user_id:
            return None
        user = db.users.find_one({'_id': ObjectId(user_id)})
        return user
    except Exception as e:
        print(f"Error getting user from token: {e}")
        return None