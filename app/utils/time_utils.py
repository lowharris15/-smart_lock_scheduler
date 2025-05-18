from datetime import datetime, timezone
import pytz
import os

# Try to get the timezone from environment variables, or default to UTC
DEFAULT_TIMEZONE = os.getenv('TIMEZONE', 'UTC')

def get_current_utc_datetime():
    """
    Get the current UTC datetime
    
    Returns:
        datetime: Current time in UTC
    """
    return datetime.now(timezone.utc)

def get_current_utc_iso():
    """
    Get the current UTC time in ISO 8601 format with Z suffix
    
    Returns:
        str: ISO 8601 formatted UTC time (e.g. "2023-05-17T15:30:00Z")
    """
    return get_current_utc_datetime().isoformat().replace('+00:00', 'Z')

def get_current_local_datetime():
    """
    Get the current datetime in the system's timezone
    
    Returns:
        datetime: Current time in system timezone
    """
    try:
        # Try to use the configured timezone
        local_tz = pytz.timezone(DEFAULT_TIMEZONE)
        return datetime.now(local_tz)
    except Exception:
        # Fall back to the system's local time if there's an issue
        return datetime.now()

def iso_to_datetime(iso_string):
    """
    Convert an ISO 8601 string to a datetime object with timezone info
    
    Args:
        iso_string (str): ISO 8601 formatted string
        
    Returns:
        datetime: Datetime object with timezone info
    """
    # Handle both with and without Z suffix
    if iso_string.endswith('Z'):
        iso_string = iso_string.replace('Z', '+00:00')
    return datetime.fromisoformat(iso_string)

def datetime_to_iso(dt):
    """
    Convert a datetime object to ISO 8601 format string with Z suffix for UTC
    
    Args:
        dt (datetime): Datetime object
        
    Returns:
        str: ISO 8601 formatted string
    """
    if dt.tzinfo is None:
        # Assume UTC if no timezone is provided
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace('+00:00', 'Z')

def format_datetime_for_display(iso_string, format_str=None):
    """
    Format an ISO datetime string for human-readable display
    
    Args:
        iso_string (str): ISO 8601 formatted string
        format_str (str, optional): Custom format string
        
    Returns:
        str: Formatted datetime string
    """
    dt = iso_to_datetime(iso_string)
    
    if format_str:
        return dt.strftime(format_str)
    else:
        # Default to a nice human-readable format
        return dt.strftime('%A, %B %d, %Y at %I:%M %p')

def is_time_between(check_time, start_time, end_time):
    """
    Check if a time is between start and end times
    
    Args:
        check_time (str): ISO 8601 string for time to check
        start_time (str): ISO 8601 string for start time
        end_time (str): ISO 8601 string for end time
        
    Returns:
        bool: True if check_time is between start_time and end_time
    """
    check_dt = iso_to_datetime(check_time)
    start_dt = iso_to_datetime(start_time)
    end_dt = iso_to_datetime(end_time)
    
    return start_dt <= check_dt <= end_dt

def add_hours_to_time(iso_string, hours):
    """
    Add specified hours to an ISO datetime string
    
    Args:
        iso_string (str): ISO 8601 formatted string
        hours (int/float): Number of hours to add (can be negative)
        
    Returns:
        str: New ISO 8601 formatted string
    """
    dt = iso_to_datetime(iso_string)
    new_dt = dt + timezone.timedelta(hours=hours)
    return datetime_to_iso(new_dt)

def is_in_past(iso_string):
    """
    Check if a time is in the past
    
    Args:
        iso_string (str): ISO 8601 formatted string
        
    Returns:
        bool: True if the time is in the past
    """
    dt = iso_to_datetime(iso_string)
    return dt < get_current_utc_datetime()

def is_in_future(iso_string):
    """
    Check if a time is in the future
    
    Args:
        iso_string (str): ISO 8601 formatted string
        
    Returns:
        bool: True if the time is in the future
    """
    dt = iso_to_datetime(iso_string)
    return dt > get_current_utc_datetime()
