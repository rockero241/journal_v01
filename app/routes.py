from flask import Blueprint, request, jsonify
from app.utils import sanitize_text, validate_length, validate_content_type, validate_headers

bp = Blueprint('routes', __name__)

@bp.route('/submit', methods=['POST'])
def submit_entry():
    if not validate_headers():
        return jsonify({"error": "Invalid request headers"}), 400

    content = request.form.get('journal_entry', '')

    if not validate_length(content):
        return jsonify({"error": "Entry too long or empty"}), 400

    clean_content = sanitize_text(validate_content_type(content))

    return jsonify({"success": True, "content": clean_content})
