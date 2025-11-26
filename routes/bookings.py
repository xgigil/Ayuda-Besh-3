# routes/bookings.py
from flask import Blueprint, request, jsonify
from lib.mongodb import get_database
from lib.decorators import token_required
from datetime import datetime
from bson.objectid import ObjectId

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/my-bookings', methods=['GET'])
@token_required
def get_my_bookings():
    """Get bookings for current user (customer or provider)"""
    db = get_database()
    user_id = ObjectId(request.current_user['user_id'])
    role = request.current_user['role']
    
    if role == 'customer':
        query = {'customer_id': user_id}
    else:  # provider
        query = {'provider_id': user_id}
    
    bookings = list(db.bookings.find(query))
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        booking['customer_id'] = str(booking['customer_id'])
        booking['provider_id'] = str(booking['provider_id'])
    
    return jsonify(bookings), 200

@bookings_bp.route('/<booking_id>/accept', methods=['POST'])
@token_required
def accept_booking(booking_id):
    """Provider accepts a booking"""
    db = get_database()
    result = db.bookings.update_one(
        {
            '_id': ObjectId(booking_id),
            'provider_id': ObjectId(request.current_user['user_id']),
            'status': 'pending'
        },
        {'$set': {'status': 'accepted', 'accepted_at': datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Booking not found or already accepted'}), 404
    return jsonify({'message': 'Booking accepted'}), 200

@bookings_bp.route('/<booking_id>/complete', methods=['POST'])
@token_required
def complete_booking(booking_id):
    """Mark booking as completed"""
    db = get_database()
    result = db.bookings.update_one(
        {
            '_id': ObjectId(booking_id),
            'customer_id': ObjectId(request.current_user['user_id']),
            'status': 'accepted'
        },
        {'$set': {'status': 'completed', 'completed_at': datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Booking not found or not in accepted state'}), 404
    return jsonify({'message': 'Booking completed'}), 200