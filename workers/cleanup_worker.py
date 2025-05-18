import sys
import os
import time
import json
import requests
from datetime import datetime, timedelta

# Add the parent directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.seam_service import SeamService
from app.models.booking import Booking
from app.utils.time_utils import get_current_utc_iso

class CleanupWorker:
    def __init__(self, config=None):
        """
        Initialize the cleanup worker
        
        Args:
            config (dict, optional): Configuration options
        """
        self.config = config or {
            'check_interval_seconds': 3600,  # Check every hour
            'api_base_url': 'http://localhost:5000/api',
            'devices': ['mock-device-001']  # List of device IDs to check
        }
        
        self.seam_service = SeamService()
    
    def update_booking_statuses(self):
        """Update booking statuses for expired bookings"""
        # In a production application, this would likely use a database
        # For this example, we'll use the API
        try:
            response = requests.get(f"{self.config['api_base_url']}/bookings")
            if response.status_code == 200:
                bookings_data = response.json()
                now = get_current_utc_iso()
                
                for booking_data in bookings_data:
                    # Check if booking is expired but still marked as active
                    if booking_data['status'] == 'active' and booking_data['ends_at'] < now:
                        # Update booking status via API
                        requests.post(
                            f"{self.config['api_base_url']}/cleanup-expired-codes",
                            json={"device_id": booking_data['device_id']}
                        )
        except Exception as e:
            print(f"Error updating booking statuses: {str(e)}")
    
    def cleanup_expired_codes(self):
        """Clean up expired access codes for all configured devices"""
        for device_id in self.config['devices']:
            try:
                deleted_codes = self.seam_service.delete_expired_codes(device_id)
                if deleted_codes:
                    print(f"Deleted {len(deleted_codes)} expired codes for device {device_id}")
            except Exception as e:
                print(f"Error cleaning up codes for device {device_id}: {str(e)}")
    
    def run(self):
        """Run the cleanup worker as a continuous process"""
        print("Starting cleanup worker...")
        
        while True:
            current_time = datetime.now()
            print(f"Running cleanup check at {current_time.isoformat()}")
            
            # Clean up expired codes
            self.cleanup_expired_codes()
            
            # Update booking statuses
            self.update_booking_statuses()
            
            # Sleep until the next check
            print(f"Next check in {self.config['check_interval_seconds']} seconds")
            time.sleep(self.config['check_interval_seconds'])

if __name__ == "__main__":
    worker = CleanupWorker()
    worker.run() 