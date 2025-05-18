from flask import Blueprint, request, jsonify, abort
from app.services.scheduler_service import SchedulerService
from app.services.notification_service import NotificationService
from app.models.booking import Booking
from app.models.user import User
import uuid
import json
import os

# Create the blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
scheduler_service = SchedulerService()
notification_service = NotificationService()

# In-memory storage for development (would use a database in production)
BOOKINGS_FILE = 'data/bookings.json'
USERS_FILE = 'data/users.json'

def load_data():
    """Load data from JSON files"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    bookings = []
    users = []
    
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, 'r') as f:
                bookings_data = json.load(f)
                bookings = [Booking.from_dict(b) for b in bookings_data]
        except Exception as e:
            print(f"Error loading bookings: {str(e)}")
    
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
                users = [User.from_dict(u) for u in users_data]
        except Exception as e:
            print(f"Error loading users: {str(e)}")
    
    return bookings, users

def save_bookings(bookings):
    """Save bookings to JSON file"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump([b.to_dict() for b in bookings], f, indent=2)

def save_users(users):
    """Save users to JSON file"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    with open(USERS_FILE, 'w') as f:
        json.dump([u.to_dict() for u in users], f, indent=2)

@api_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get a list of available devices"""
    # In a real application, you would get devices from Seam API
    # For demonstration, we'll return a mock device
    return jsonify([
        {
            "device_id": "mock-device-001",
            "name": "Front Door Lock",
            "type": "schlage_lock",
            "status": "online"
        }
    ])

@api_bp.route('/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings"""
    bookings, _ = load_data()
    
    # Convert to dict format for JSON response
    bookings_data = [b.to_dict() for b in bookings]
    
    return jsonify(bookings_data)

@api_bp.route('/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get a specific booking"""
    bookings, _ = load_data()
    
    booking = next((b for b in bookings if b.id == booking_id), None)
    if not booking:
        abort(404, description="Booking not found")
    
    return jsonify(booking.to_dict())

@api_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    data = request.json
    
    # Validate required fields
    required_fields = ['device_id', 'starts_at', 'ends_at', 'user_name', 'user_email']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing required field: {field}")
    
    # Check if time slot is available
    if not scheduler_service.check_availability(
        data['device_id'], 
        data['starts_at'], 
        data['ends_at']
    ):
        abort(409, description="Time slot is not available")
    
    # Find or create user
    bookings, users = load_data()
    
    user = next((u for u in users if u.email == data['user_email']), None)
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            name=data['user_name'],
            email=data['user_email'],
            phone=data.get('user_phone')
        )
        users.append(user)
        save_users(users)
    
    # Schedule the access code
    access_details = scheduler_service.schedule_access(
        data['device_id'],
        data['starts_at'],
        data['ends_at'],
        data['user_name']
    )
    
    # Create booking record
    booking = Booking(
        device_id=data['device_id'],
        user_id=user.id,
        access_code_id=access_details['access_code_id'],
        code=access_details['code'],
        starts_at=access_details['starts_at'],
        ends_at=access_details['ends_at']
    )
    
    bookings.append(booking)
    save_bookings(bookings)
    
    # Send notification
    if user.email:
        notification_service.send_access_code_email(user.email, access_details)
    
    if user.phone:
        notification_service.send_access_code_sms(user.phone, access_details)
    
    return jsonify({
        "success": True,
        "booking": booking.to_dict()
    }), 201

@api_bp.route('/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    bookings, _ = load_data()
    
    booking = next((b for b in bookings if b.id == booking_id), None)
    if not booking:
        abort(404, description="Booking not found")
    
    # Check if booking can be cancelled (e.g., not already active)
    if booking.is_active():
        abort(400, description="Cannot cancel an active booking")
    
    # Delete access code if it's a future booking
    if booking.is_future() and booking.access_code_id:
        try:
            scheduler_service.seam_service.delete_access_code(booking.access_code_id)
        except Exception as e:
            # Log but continue with cancellation
            print(f"Error deleting access code: {str(e)}")
    
    # Update booking status
    booking.status = 'cancelled'
    
    # Save updated bookings
    save_bookings(bookings)
    
    return jsonify({
        "success": True,
        "message": "Booking cancelled successfully"
    })

@api_bp.route('/check-availability', methods=['GET'])
def check_availability():
    """Check if a time slot is available"""
    device_id = request.args.get('device_id')
    start_time = request.args.get('starts_at')
    end_time = request.args.get('ends_at')
    
    if not device_id or not start_time or not end_time:
        abort(400, description="Missing required parameters")
    
    is_available = scheduler_service.check_availability(device_id, start_time, end_time)
    
    return jsonify({
        "is_available": is_available
    })

@api_bp.route('/cleanup-expired-codes', methods=['POST'])
def cleanup_expired_codes():
    """Clean up expired access codes"""
    device_id = request.json.get('device_id')
    
    if not device_id:
        abort(400, description="Device ID is required")
    
    deleted_codes = scheduler_service.seam_service.delete_expired_codes(device_id)
    
    # Update booking statuses
    bookings, _ = load_data()
    updated = False
    
    for booking in bookings:
        if booking.is_expired() and booking.status == 'active':
            booking.status = 'expired'
            updated = True
    
    if updated:
        save_bookings(bookings)
    
    return jsonify({
        "success": True,
        "deleted_codes": deleted_codes
    })

@api_bp.route('/booked-periods', methods=['GET'])
def get_booked_periods():
    """Get all booked time periods for a device"""
    device_id = request.args.get('device_id')
    
    if not device_id:
        abort(400, description="Device ID is required")
    
    booked_periods = scheduler_service.get_booked_periods(device_id)
    
    return jsonify({
        "booked_periods": booked_periods
    })

@api_bp.route('/handle-consecutive-bookings', methods=['POST'])
def handle_consecutive_bookings():
    """Identify and handle consecutive bookings"""
    device_id = request.json.get('device_id')
    
    if not device_id:
        abort(400, description="Device ID is required")
    
    consecutive_groups = scheduler_service.handle_consecutive_bookings(device_id)
    
    # Format the response
    formatted_groups = []
    for group in consecutive_groups:
        formatted_group = []
        for code in group:
            formatted_group.append({
                "access_code_id": code.access_code_id,
                "name": code.name,
                "starts_at": code.starts_at,
                "ends_at": code.ends_at
            })
        formatted_groups.append(formatted_group)
    
    return jsonify({
        "consecutive_booking_groups": formatted_groups
    }) 