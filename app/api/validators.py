from datetime import datetime
import re

def validate_iso8601(date_string):
    """
    Validate that a string is in ISO8601 format
    
    Args:
        date_string (str): The string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Try to parse the string as an ISO8601 datetime
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False

def validate_email(email):
    """
    Validate that a string is a valid email address
    
    Args:
        email (str): The email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Simple regex for email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def validate_phone(phone):
    """
    Validate that a string is a valid phone number
    
    Args:
        phone (str): The phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Simple regex for phone validation (allows international formats)
    phone_regex = r'^\+?[0-9]{10,15}$'
    return bool(re.match(phone_regex, phone))

def validate_booking_data(data):
    """
    Validate booking data
    
    Args:
        data (dict): The booking data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['device_id', 'starts_at', 'ends_at', 'user_name', 'user_email']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate time formats
    if not validate_iso8601(data['starts_at']):
        return False, "Invalid start time format. Must be ISO8601."
    
    if not validate_iso8601(data['ends_at']):
        return False, "Invalid end time format. Must be ISO8601."
    
    # Validate email
    if not validate_email(data['user_email']):
        return False, "Invalid email address."
    
    # Validate phone if provided
    if 'user_phone' in data and data['user_phone'] and not validate_phone(data['user_phone']):
        return False, "Invalid phone number."
    
    # Validate time logic
    start_time = datetime.fromisoformat(data['starts_at'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(data['ends_at'].replace('Z', '+00:00'))
    
    if start_time >= end_time:
        return False, "End time must be after start time."
    
    now = datetime.utcnow()
    if start_time < now:
        return False, "Start time cannot be in the past."
    
    # Check duration (optional)
    max_duration_hours = 72  # 3 days
    duration = (end_time - start_time).total_seconds() / 3600
    
    if duration > max_duration_hours:
        return False, f"Booking duration cannot exceed {max_duration_hours} hours."
    
    return True, None 