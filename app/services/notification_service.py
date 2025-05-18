import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app.utils.time_utils import format_datetime_for_display

class NotificationService:
    def __init__(self, email_config=None, sms_config=None):
        """
        Initialize the notification service
        
        Args:
            email_config (dict, optional): Email configuration parameters
            sms_config (dict, optional): SMS configuration parameters
        """
        self.email_config = email_config or {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'smtp_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@example.com')
        }
        
        self.sms_config = sms_config or {}
    
    def format_datetime(self, datetime_str):
        """
        Format an ISO8601 datetime string to a more readable format
        
        Args:
            datetime_str (str): ISO8601 formatted datetime string
            
        Returns:
            str: Human-readable datetime string
        """
        return format_datetime_for_display(datetime_str)
    
    def send_access_code_email(self, email, access_details):
        """
        Send an email with access code details
        
        Args:
            email (str): Recipient's email address
            access_details (dict): Access code details including code, start and end times
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        if not self.email_config['smtp_username'] or not self.email_config['smtp_password']:
            print("Email credentials not configured. Email not sent.")
            return False
        
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['Subject'] = 'Your Smart Lock Access Code'
            msg['From'] = self.email_config['from_email']
            msg['To'] = email
            
            # Format the email body
            start_time = self.format_datetime(access_details['starts_at'])
            end_time = self.format_datetime(access_details['ends_at'])
            
            body = f"""
            <html>
            <body>
                <h2>Your Smart Lock Access Code</h2>
                <p>Here is your temporary access code for the smart lock:</p>
                <h1 style="font-size: 36px; color: #0066cc; padding: 10px; border: 2px solid #0066cc; display: inline-block;">{access_details['code']}</h1>
                <p><strong>Valid from:</strong> {start_time}</p>
                <p><strong>Valid until:</strong> {end_time}</p>
                <p>Please do not share this code with anyone else.</p>
                <p>This code will automatically expire at the end time.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def send_access_code_sms(self, phone_number, access_details):
        """
        Send an SMS with access code details (placeholder for SMS integration)
        
        Args:
            phone_number (str): Recipient's phone number
            access_details (dict): Access code details including code, start and end times
            
        Returns:
            bool: True if the SMS was sent successfully, False otherwise
        """
        # This is a placeholder for actual SMS sending logic
        # You would typically integrate with an SMS service like Twilio here
        print(f"SMS notification would be sent to {phone_number} with code {access_details['code']}")
        return True
    
    def send_expiration_reminder(self, email, access_details, hours_before=24):
        """
        Send a reminder about an access code that will expire soon
        
        Args:
            email (str): Recipient's email address
            access_details (dict): Access code details
            hours_before (int): Hours before expiration to send the reminder
            
        Returns:
            bool: True if the reminder was sent successfully, False otherwise
        """
        if not self.email_config['smtp_username'] or not self.email_config['smtp_password']:
            print("Email credentials not configured. Reminder not sent.")
            return False
        
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['Subject'] = 'Your Access Code Will Expire Soon'
            msg['From'] = self.email_config['from_email']
            msg['To'] = email
            
            # Format the email body
            end_time = self.format_datetime(access_details['ends_at'])
            
            body = f"""
            <html>
            <body>
                <h2>Access Code Expiration Reminder</h2>
                <p>Your temporary access code <strong>{access_details['code']}</strong> for the smart lock will expire soon:</p>
                <p><strong>Expiration time:</strong> {end_time}</p>
                <p>This is an automated reminder.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send reminder email: {str(e)}")
            return False
