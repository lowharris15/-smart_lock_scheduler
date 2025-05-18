from seam import Seam
from datetime import datetime
from app.utils.time_utils import get_current_utc_iso, is_in_past

class SeamService:
    def __init__(self, api_key=None):
        """
        Initialize the Seam service
        
        Args:
            api_key (str, optional): Seam API key. If not provided, 
                                     it will be loaded from environment variables.
        """
        self.client = Seam(api_key=api_key)
    
    def create_access_code(self, device_id, code, name, starts_at, ends_at):
        """
        Create a timebound access code for a specific device
        
        Args:
            device_id (str): The ID of the Schlage lock
            code (str): The access code to set
            name (str): Name/description for this access code
            starts_at (str): ISO8601 formatted string for when access begins
            ends_at (str): ISO8601 formatted string for when access ends
            
        Returns:
            dict: The created access code details
        """
        access_code = self.client.access_codes.create(
            device_id=device_id,
            code=code,
            name=name,
            starts_at=starts_at,
            ends_at=ends_at
        )
        
        return {
            "access_code_id": access_code.access_code_id,
            "code": code,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "name": name
        }
    
    def get_access_codes(self, device_id):
        """
        Get all access codes for a specific device
        
        Args:
            device_id (str): The ID of the Schlage lock
            
        Returns:
            list: List of access codes
        """
        return self.client.access_codes.list(device_id=device_id)
    
    def delete_access_code(self, access_code_id):
        """
        Delete a specific access code
        
        Args:
            access_code_id (str): The ID of the access code to delete
            
        Returns:
            bool: True if deletion was successful
        """
        self.client.access_codes.delete(access_code_id=access_code_id)
        return True
    
    def delete_expired_codes(self, device_id):
        """
        Delete all expired access codes for a device
        
        Args:
            device_id (str): The ID of the Schlage lock
            
        Returns:
            list: List of deleted access code IDs
        """
        codes = self.client.access_codes.list(device_id=device_id)
        now = get_current_utc_iso()
        deleted_codes = []
        
        for code in codes:
            if hasattr(code, 'ends_at') and is_in_past(code.ends_at):
                self.client.access_codes.delete(access_code_id=code.access_code_id)
                deleted_codes.append(code.access_code_id)
        
        return deleted_codes
    
    def get_device_info(self, device_id):
        """
        Get detailed information about a specific device
        
        Args:
            device_id (str): The ID of the Schlage lock
            
        Returns:
            dict: Device information
        """
        return self.client.devices.get(device_id=device_id)
