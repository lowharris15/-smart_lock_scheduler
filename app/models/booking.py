from datetime import datetime
import uuid
from app.utils.time_utils import get_current_utc_iso, is_time_between, is_in_past, is_in_future

class Booking:
    def __init__(self, id=None, device_id=None, user_id=None, 
                 access_code_id=None, code=None, starts_at=None, 
                 ends_at=None, created_at=None, status=None):
        """
        Initialize a Booking object
        
        Args:
            id (str, optional): Unique identifier for the booking
            device_id (str, optional): ID of the lock device
            user_id (str, optional): ID of the user
            access_code_id (str, optional): ID of the access code from Seam
            code (str, optional): The actual access code
            starts_at (str, optional): ISO8601 formatted string for start time
            ends_at (str, optional): ISO8601 formatted string for end time
            created_at (datetime, optional): When the booking was created
            status (str, optional): Status of the booking (active, expired, cancelled)
        """
        self.id = id or str(uuid.uuid4())
        self.device_id = device_id
        self.user_id = user_id
        self.access_code_id = access_code_id
        self.code = code
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.created_at = created_at or datetime.utcnow()
        self.status = status or 'active'
    
    def to_dict(self):
        """
        Convert booking object to dictionary
        
        Returns:
            dict: Dictionary representation of the booking
        """
        return {
            'id': self.id,
            'device_id': self.device_id,
            'user_id': self.user_id,
            'access_code_id': self.access_code_id,
            'code': self.code,
            'starts_at': self.starts_at,
            'ends_at': self.ends_at,
            'created_at': self.created_at.isoformat() + 'Z' if isinstance(self.created_at, datetime) else self.created_at,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Booking object from a dictionary
        
        Args:
            data (dict): Dictionary containing booking data
            
        Returns:
            Booking: A new Booking object
        """
        if data.get('created_at'):
            # Parse ISO format to datetime
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        else:
            created_at = None
            
        return cls(
            id=data.get('id'),
            device_id=data.get('device_id'),
            user_id=data.get('user_id'),
            access_code_id=data.get('access_code_id'),
            code=data.get('code'),
            starts_at=data.get('starts_at'),
            ends_at=data.get('ends_at'),
            created_at=created_at,
            status=data.get('status')
        )
    
    def is_active(self):
        """
        Check if the booking is currently active
        
        Returns:
            bool: True if the booking is active, False otherwise
        """
        if self.status != 'active':
            return False
            
        now = get_current_utc_iso()
        return is_time_between(now, self.starts_at, self.ends_at)
    
    def is_expired(self):
        """
        Check if the booking has expired
        
        Returns:
            bool: True if the booking has expired, False otherwise
        """
        now = get_current_utc_iso()
        return is_in_past(self.ends_at)
    
    def is_future(self):
        """
        Check if the booking is in the future
        
        Returns:
            bool: True if the booking is in the future, False otherwise
        """
        now = get_current_utc_iso()
        return is_in_future(self.starts_at) 