# routes/admin.py
from flask import Blueprint, request, jsonify
from lib.mongodb import get_database
from lib.decorators import admin_required
from datetime import datetime, timedelta
from bson.objectid import ObjectId

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/verify-provider/<provider_id>', methods=['POST'])
@admin_required
def verify_provider(provider_id):
    """Admin verifies a provider"""
    db = get_database()
    result = db.users.update_one(
        {'_id': ObjectId(provider_id), 'role': 'provider'},
        {'$set': {'is_verified': True, 'verified_at': datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Provider not found'}), 404
    return jsonify({'message': 'Provider verified'}), 200

@admin_bp.route('/disputes', methods=['GET', 'POST'])
@admin_required
def manage_disputes():
    """Get or create disputes"""
    db = get_database()
    if request.method == 'POST':
        data = request.get_json()
        dispute = {
            'booking_id': ObjectId(data['booking_id']),
            'customer_id': ObjectId(data['customer_id']),
            'provider_id': ObjectId(data['provider_id']),
            'description': data['description'],
            'status': 'open',
            'created_at': datetime.utcnow()
        }
        result = db.disputes.insert_one(dispute)
        return jsonify({'dispute_id': str(result.inserted_id)}), 201
    else:
        disputes = list(db.disputes.find())
        for dispute in disputes:
            dispute['_id'] = str(dispute['_id'])
            dispute['booking_id'] = str(dispute['booking_id'])
            dispute['customer_id'] = str(dispute['customer_id'])
            dispute['provider_id'] = str(dispute['provider_id'])
        return jsonify(disputes), 200

@admin_bp.route('/reports/daily-bookings', methods=['GET'])
@admin_required
def daily_bookings_report():
    """Generate daily bookings report"""
    db = get_database()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    bookings = list(db.bookings.find({'created_at': {'$gte': today}}))
    
    # Enhance with customer/provider names
    for booking in bookings:
        customer = db.users.find_one({'_id': booking['customer_id']})
        provider = db.users.find_one({'_id': booking['provider_id']})
        booking['customer_name'] = customer['fullName'] if customer else 'Unknown'
        booking['provider_name'] = provider['fullName'] if provider else 'Unknown'
        booking['_id'] = str(booking['_id'])
        booking['customer_id'] = str(booking['customer_id'])
        booking['provider_id'] = str(booking['provider_id'])
    
    return jsonify(bookings), 200

@admin_bp.route('/reports/provider-activity', methods=['GET'])
@admin_required
def provider_activity_report():
    """Provider activity report"""
    db = get_database()
    providers = list(db.users.find({'role': 'provider'}))
    
    report = []
    for provider in providers:
        bookings = list(db.bookings.find({
            'provider_id': provider['_id'],
            'status': 'completed'
        }))
        
        total_jobs = len(bookings)
        if total_jobs > 0:
            avg_rating = sum(b.get('rating', 0) for b in bookings) / total_jobs
        else:
            avg_rating = 0
            
        report.append({
            'provider_id': str(provider['_id']),
            'provider_name': provider['fullName'],
            'total_jobs': total_jobs,
            'avg_rating': round(avg_rating, 2)
        })
    
    return jsonify(report), 200