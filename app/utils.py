from bleach import clean
from werkzeug.utils import secure_filename
from flask import request

def sanitize_text(text):
    """Sanitize user input to remove harmful HTML tags."""
    allowed_tags = ['p', 'br', 'strong', 'em']
    return clean(text, tags=allowed_tags, strip=True)

def validate_length(text, max_length=5000):
    """Ensure text input is within the required length."""
    return len(text.strip()) <= max_length and len(text.strip()) > 0

def validate_content_type(content):
    """Remove null bytes and control characters from content."""
    content = content.replace('\x00', '')
    content = ''.join(char for char in content if ord(char) >= 32)
    return content

def validate_headers():
    """Ensure request headers are correctly formatted."""
    content_type = request.headers.get('Content-Type')
    return content_type in ['application/json', 'application/x-www-form-urlencoded']
