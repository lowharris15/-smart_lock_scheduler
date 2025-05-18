from flask import Flask, render_template, redirect, url_for
import os
from datetime import datetime
from dotenv import load_dotenv
from app.api.routes import api_bp

# Load environment variables from .env file
load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """Render the main scheduler page"""
        return render_template('scheduler.html')
    
    @app.route('/confirmation/<booking_id>')
    def confirmation(booking_id):
        """Render the booking confirmation page"""
        return render_template('confirmation.html', booking_id=booking_id)
    
    # Make sure the data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
