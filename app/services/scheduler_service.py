from datetime import datetime, timedelta
from app.utils.code_generator import generate_random_code
from app.services.seam_service import SeamService
from app.utils.time_utils import iso_to_datetime

class SchedulerService:
    def __init__(self, seam_service=None):
        """
        Initialize the scheduler service
        
        Args:
            seam_service (SeamService, optional): An instance of SeamService.
                                                 If not provided, a new one will be created.
        """
        self.seam_service = seam_service or SeamService()
    
    def schedule_access(self, device_id, start_time, end_time, user_name):
        """
        Create a scheduled access code for a specific time period
        
        Args:
            device_id (str): The ID of the Schlage lock
            start_time (str): ISO8601 formatted string for when access begins
            end_time (str): ISO8601 formatted string for when access ends
            user_name (str): Name of the user for reference
            
        Returns:
            dict: Access code details
        """
        # Generate a random code
        random_code = generate_random_code()
        
        # Create a descriptive name for this access
        code_name = f"Scheduled access for {user_name}"
        
        # Create the timebound access code using Seam API
        access_details = self.seam_service.create_access_code(
            device_id=device_id,
            code=random_code,
            name=code_name,
            starts_at=start_time,
            ends_at=end_time
        )
        
        # Add user information to access details
        access_details["user"] = user_name
        
        return access_details
    
    def check_availability(self, device_id, start_time, end_time):
        """
        Check if the specified time slot is available
        
        Args:
            device_id (str): The ID of the Schlage lock
            start_time (str): ISO8601 formatted string for when access would begin
            end_time (str): ISO8601 formatted string for when access would end
            
        Returns:
            bool: True if the time slot is available, False otherwise
        """
        codes = self.seam_service.get_access_codes(device_id)
        proposed_start = iso_to_datetime(start_time)
        proposed_end = iso_to_datetime(end_time)
        
        for code in codes:
            if hasattr(code, 'starts_at') and hasattr(code, 'ends_at'):
                code_start = iso_to_datetime(code.starts_at)
                code_end = iso_to_datetime(code.ends_at)
                
                # Check for overlap
                if (proposed_start < code_end and proposed_end > code_start):
                    return False
        
        return True
    
    def get_booked_periods(self, device_id):
        """
        Get all booked time periods for a device
        
        Args:
            device_id (str): The ID of the Schlage lock
            
        Returns:
            list: List of booked time periods
        """
        codes = self.seam_service.get_access_codes(device_id)
        
        # Extract the time periods that are already booked
        booked_periods = [
            {"starts_at": code.starts_at, "ends_at": code.ends_at, "name": code.name}
            for code in codes
            if hasattr(code, 'starts_at') and hasattr(code, 'ends_at')
        ]
        
        return booked_periods
    
    def handle_consecutive_bookings(self, device_id):
        """
        Identify and handle consecutive bookings
        
        Args:
            device_id (str): The ID of the Schlage lock
            
        Returns:
            list: List of consecutive booking groups
        """
        codes = self.seam_service.get_access_codes(device_id)
        
        # Sort codes by start time
        sorted_codes = sorted(
            codes,
            key=lambda x: x.starts_at if hasattr(x, 'starts_at') else "0"
        )
        
        # Group consecutive bookings (where one ends and another begins)
        consecutive_groups = []
        current_group = []
        
        for i in range(len(sorted_codes) - 1):
            current = sorted_codes[i]
            next_code = sorted_codes[i + 1]
            
            if hasattr(current, 'ends_at') and hasattr(next_code, 'starts_at'):
                # Parse the datetime objects
                current_end = iso_to_datetime(current.ends_at)
                next_start = iso_to_datetime(next_code.starts_at)
                
                # If bookings are consecutive (within 5 minutes)
                time_diff = (next_start - current_end).total_seconds()
                if abs(time_diff) < 300:  # 5 minutes = 300 seconds
                    if not current_group:
                        current_group.append(current)
                    current_group.append(next_code)
                else:
                    if current_group:
                        consecutive_groups.append(current_group)
                        current_group = []
        
        if current_group:
            consecutive_groups.append(current_group)
        
        return consecutive_groups
