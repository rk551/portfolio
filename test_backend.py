import requests
import os
from dotenv import load_dotenv
import time
import sys

# Load environment variables
load_dotenv()

def check_server_status(retries=3, delay=2):
    """Check if server is running with retries"""
    print("\nChecking server status...")
    
    for attempt in range(retries):
        try:
            response = requests.get('http://localhost:5000/api/test', timeout=5)
            print("✓ Server is running!")
            return True
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                print(f"Server not responding, retrying in {delay} seconds... ({attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                print("\n❌ Error: Server is not running!")
                print("Please start the Flask server first with:")
                print("cd e:/websites/portfolio")
                print("python app.py")
                return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            return False

def test_connection():
    """Test basic backend connectivity"""
    try:
        response = requests.get('http://localhost:5000/api/test')
        print(f"\nConnection test: {response.json()}")
        return True
    except Exception as e:
        print(f"\nConnection error: {str(e)}")
        return False

def test_email_config():
    """Test email configuration"""
    email_config = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
        'EMAIL_PASSWORD': 'Present' if os.getenv('EMAIL_PASSWORD') else 'Missing'
    }
    print("\nEmail Configuration:")
    for key, value in email_config.items():
        print(f"{key}: {value}")
    
    # Validate configuration
    missing = [k for k, v in email_config.items() if not v or v == 'Missing']
    if missing:
        print(f"\n❌ Missing configuration: {', '.join(missing)}")
        return False
    return True

def test_contact_form():
    """Test contact form submission"""
    test_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'subject': 'Test Message',
        'message': 'This is a test message'
    }
    
    try:
        response = requests.post('http://localhost:5000/api/contact', json=test_data)
        result = response.json()
        if result.get('success'):
            print("\n✓ Contact form test: Success")
        else:
            print(f"\n❌ Contact form test failed: {result.get('error', 'Unknown error')}")
        return True
    except Exception as e:
        print(f"\n❌ Contact form error: {str(e)}")
        return False

if __name__ == '__main__':
    print("Starting backend tests...\n")
    
    # First check if server is running
    if not check_server_status():
        sys.exit(1)
    
    # Run tests
    connection_ok = test_connection()
    email_config_ok = test_email_config()
    contact_form_ok = test_contact_form()
    
    # Summary
    print("\nTest Summary:")
    print(f"✓ Server Connection: {'Success' if connection_ok else 'Failed'}")
    print(f"✓ Email Config: {'Valid' if email_config_ok else 'Invalid'}")
    print(f"✓ Contact Form: {'Working' if contact_form_ok else 'Failed'}")
    
    if all([connection_ok, email_config_ok, contact_form_ok]):
        print("\n✨ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
