from flask import Flask, request, jsonify, render_template
try:
    from flask_cors import CORS
except ImportError:
    print("Warning: flask-cors not installed. CORS functionality will be limited.")
    def CORS(app): return app

from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',  # Specify the template folder
    static_folder='static'       # Specify the static files folder
)

# Configure CORS to allow requests from your frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(text):
    """Basic input sanitization"""
    if not isinstance(text, str):
        return ''
    return text.strip()


@app.route('/')
def index():
    """Render the main portfolio page"""
    return render_template('index.html')


@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        # Add even more detailed logging
        logger.info("\n========== New Contact Form Submission ==========")
        logger.info("1. Configuration Check:")
        logger.info(f"SMTP_SERVER: {SMTP_SERVER}")
        logger.info(f"SMTP_PORT: {SMTP_PORT}")
        logger.info(f"SENDER_EMAIL: {SENDER_EMAIL}")
        logger.info(f"EMAIL_PASSWORD length: {len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'No password set'}")
        
        data = request.get_json()
        logger.info("\n2. Received Data:")
        logger.info(f"Data: {data}")

        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # Sanitize inputs
        name = sanitize_input(data['name'])
        email = sanitize_input(data['email'])
        subject = sanitize_input(data['subject'])
        message = sanitize_input(data['message'])

        # Validate inputs
        if not all([name, email, subject, message]):
            return jsonify({
                'success': False,
                'error': 'All fields must not be empty'
            }), 400

        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = SENDER_EMAIL
        msg['Subject'] = f"Portfolio Contact: {subject}"

        # Format email body
        body = f"""
        New contact from portfolio website:

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}

        Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        msg.attach(MIMEText(body, 'plain'))

        # More detailed SMTP debugging
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            logger.info("\n3. Starting SMTP Process:")
            logger.info("3.1 Establishing connection...")
            server.set_debuglevel(2)  # Increase debug level
            
            logger.info("3.2 Starting TLS...")
            server.starttls()
            
            logger.info("3.3 Attempting login...")
            logger.info(f"Using email: {SENDER_EMAIL}")
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            
            logger.info("3.4 Sending message...")
            logger.info(f"Message details: From={msg['From']}, To={msg['To']}, Subject={msg['Subject']}")
            server.send_message(msg)
            logger.info("3.5 Message sent successfully!")

        logger.info("\n4. Process Completed Successfully!")
        logger.info("===========================================")
        
        return jsonify({
            'success': True,
            'message': 'Email sent successfully'
        }), 200

    except Exception as e:
        logger.error("\n========== ERROR DETAILS ==========")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        logger.error("===================================")
        
        return jsonify({
            'success': False,
            'error': f"Error: {type(e).__name__} - {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Check if email configuration is set
    if not all([SENDER_EMAIL, EMAIL_PASSWORD]):
        logger.error("Email configuration missing. Please check .env file.")
        exit(1)

    # Run the app on port 5000
    app.run(debug=True, port=5000)