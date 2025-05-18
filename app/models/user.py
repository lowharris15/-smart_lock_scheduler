from datetime import datetime

class User:
    def __init__(self, id=None, name=None, email=None, phone=None, created_at=None):
        """
        Initialize a User object
        
        Args:
            id (str, optional): Unique identifier for the user
            name (str, optional): User's full name
            email (str, optional): User's email address
            phone (str, optional): User's phone number
            created_at (datetime, optional): When the user was created
        """
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """
        Convert user object to dictionary
        
        Returns:
            dict: Dictionary representation of the user
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() + 'Z'
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a User object from a dictionary
        
        Args:
            data (dict): Dictionary containing user data
            
        Returns:
            User: A new User object
        """
        if data.get('created_at'):
            # Parse ISO format to datetime
            created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        else:
            created_at = None
            
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            created_at=created_at
        ) 