# Smart Lock Scheduler

A web application that automates the generation and management of temporary access codes for smart locks under the Seam API (https://docs.seam.co/latest).

## Features

- **Scheduling Interface**: Interactive calendar for booking time slots
- **Automatic Code Generation**: Generate secure random access codes
- **Time-bound Access Codes**: Codes only work during scheduled periods
- **Automatic Expiration**: Codes are automatically deleted when they expire
- **Email & SMS Notifications**: Send access codes to users via email and SMS
- **Consecutive Booking Management**: Special handling for back-to-back bookings

## System Requirements

- Python 3.8+
- Flask web framework
- Seam API access credentials

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-lock-scheduler.git
   cd smart-lock-scheduler
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   SEAM_API_KEY=your_seam_api_key
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=587
   SMTP_USERNAME=your_email@example.com
   SMTP_PASSWORD=your_email_password
   FROM_EMAIL=noreply@example.com
   SECRET_KEY=your_secret_key_for_flask
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Access the application in your browser:
   ```
   http://localhost:5000
   ```

3. Start the code cleanup worker (in a separate terminal):
   ```bash
   python -m workers.cleanup_worker
   ```

## How It Works

### Smart Lock Integration

The application uses the Seam API to create, manage, and delete access codes on smart locks. The Seam API provides a unified interface to interact with smart locks, handling the device-specific details.

### Code Generation and Management

1. When a user schedules access, the system:
   - Generates a random numeric code
   - Creates a timebound access code via Seam API
   - Stores the booking details
   - Sends the code to the user via email/SMS

2. Code cleanup:
   - A background worker periodically checks for expired codes
   - Automatically deletes expired codes from locks
   - Updates booking status to "expired"

### Scheduling System

The scheduler provides a user-friendly calendar interface where:
- Available and booked time slots are displayed
- Users can select desired access periods
- Time slot conflicts are automatically prevented
- Consecutive bookings are identified and managed

## Project Structure

```
smart-lock-scheduler/
│
├── app/                        # Main application code
│   ├── models/                 # Database models
│   ├── services/               # Business logic services
│   ├── api/                    # API endpoints
│   └── utils/                  # Utility functions
│
├── static/                     # Static assets (CSS, JS)
├── templates/                  # HTML templates
├── workers/                    # Background workers
├── tests/                      # Test files
├── app.py                      # Application entry point
└── requirements.txt            # Dependencies
```

## Development

### Running Tests

```bash
pytest tests/
```

### Production Deployment

For production deployment, it's recommended to:
1. Use a production WSGI server like Gunicorn
2. Set up a reverse proxy with Nginx
3. Use a proper database instead of JSON files
4. Set up a production-ready task queue for background jobs

Example Gunicorn command:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## License

[MIT License](LICENSE)

## Credits

This project uses the [Seam API](https://docs.seam.co/) for smart lock integration. 