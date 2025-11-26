# routes/services.py
from flask import Blueprint, request, jsonify
from lib.mongodb import get_database
from lib.decorators import token_required
from datetime import datetime
from bson.objectid import ObjectId

services_bp = Blueprint('services', __name__)

@services_bp.route('/services', methods=['GET'])
def get_services():
    """Get all available service categories"""
    db = get_database()
    services = list(db.services.find({}, {'_id': 0}))
    if not services:
        # Initialize default services if empty
        default_services = [
            {"name": "Domestic Cleaning", "category": "cleaning", "description": "Home cleaning services"},
            {"name": "Plumbing", "category": "plumbing", "description": "Pipe and fixture repairs"},
            {"name": "Electrical Work", "category": "electrical", "description": "Wiring and electrical installations"},
            {"name": "Pest Control", "category": "pest_control", "description": "Insect and rodent removal"},
            {"name": "Appliance Installation", "category": "appliance", "description": "Installation of household appliances"},
            {"name": "General Maintenance", "category": "maintenance", "description": "General home repair services"}
        ]
        db.services.insert_many(default_services)
        services = default_services
    return jsonify(services), 200

@services_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get available providers with filtering"""
    db = get_database()
    service_type = request.args.get('service')
    location = request.args.get('location')
    
    query = {'role': 'provider', 'is_verified': True}
    if service_type:
        query['services_offered'] = {'$in': [service_type]}
    if location:
        query['location'] = location
    
    providers = list(db.users.find(query, {
        'password': 0,
        'is_verified': 0
    }))
    return jsonify(providers), 200

@services_bp.route('/book', methods=['POST'])
def book_service():
    """Customer books a service"""
    data = request.get_json()
    if not data or not all(k in data for k in ('provider_id', 'service_type', 'booking_time', 'price')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_database()
    booking = {
        'customer_id': data['customer_id'],
        'provider_id': ObjectId(data['provider_id']),
        'service_type': data['service_type'],
        'booking_time': datetime.fromisoformat(data['booking_time']),
        'status': 'pending',
        'price': data['price'],
        'created_at': datetime.utcnow()
    }
    
    result = db.bookings.insert_one(booking)
    return jsonify({'booking_id': str(result.inserted_id)}), 201

@services_bp.route('/update-profile', methods=['POST'])
@token_required
def update_provider_profile():
    """Update provider's service profile"""
    if request.current_user.get('role') != 'provider':
        return jsonify({'error': 'Only providers can update profile'}), 403
    
    data = request.get_json()
    db = get_database()
    
    update_data = {
        'services_offered': data.get('services', []),
        'hourly_rate': data.get('hourly_rate', 500),
        'location': data.get('location', ''),
        'description': data.get('description', '')
    }
    
    result = db.users.update_one(
        {'_id': ObjectId(request.current_user['user_id'])},
        {'$set': update_data}
    )
    
    if result.modified_count > 0:
        return jsonify({'message': 'Profile updated successfully'}), 200
    return jsonify({'error': 'Failed to update profile'}), 500