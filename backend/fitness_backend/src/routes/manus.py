from flask import Blueprint, request, jsonify
from src.models.user import User
from src.routes.auth_middleware import token_required
import requests
import os

manus_bp = Blueprint("manus", __name__)

# Manus API credentials (using provided key directly for this test environment)
MANUS_API_KEY = "34cb116566bca3e0a6755b3d543aefd1"
MANUS_API_ENDPOINT = "https://api.manus.ai" # Placeholder - Actual endpoint might differ

@manus_bp.route("/connect", methods=["POST"])
@token_required
def connect_manus_account(current_user):
    """Connect user's Manus account to the fitness platform"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
        
    data = request.get_json()
    manus_username = data.get("manus_username")
    
    if not manus_username:
        return jsonify({"message": "Manus username is required"}), 400

    # In a real scenario, verify Manus account via API
    # For this test, we'll assume verification is successful
    # response = requests.post(
    #     f"{MANUS_API_ENDPOINT}/verify_account",
    #     headers={"Authorization": f"Bearer {MANUS_API_KEY}"},
    #     json={"username": manus_username}
    # )
    
    # Mock successful verification for now
    verification_successful = True 

    if verification_successful:
        # Store Manus connection in user profile (assuming db and User model are set up)
        # current_user.manus_username = manus_username
        # current_user.has_manus_integration = True
        # db.session.commit()
        print(f"Simulating connection for user {current_user.id} to Manus account {manus_username}")
        return jsonify({"message": "Manus account connected successfully (simulated)"}), 200
    else:
        return jsonify({"message": "Failed to connect Manus account (simulated)"}), 400

@manus_bp.route("/edit_code", methods=["POST"])
@token_required
def edit_code_via_manus(current_user):
    """Send code editing request to Manus"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
        
    data = request.get_json()
    file_name = data.get("fileName")
    code_content = data.get("code")
    
    if not file_name or not code_content:
        return jsonify({"message": "File name and code content are required"}), 400

    # Simulate sending code to Manus API
    print(f"Simulating code edit request for file: {file_name}")
    # response = requests.post(
    #     f"{MANUS_API_ENDPOINT}/edit_code",
    #     headers={"Authorization": f"Bearer {MANUS_API_KEY}"},
    #     json={"fileName": file_name, "code": code_content}
    # )
    
    # Mock successful response
    return jsonify({"message": "Code submitted to Manus successfully (simulated)", "file_id": "sim_file_123"}), 200

@manus_bp.route("/draft_email", methods=["POST"])
@token_required
def draft_email_via_manus(current_user):
    """Send email drafting request to Manus"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
        
    data = request.get_json()
    subject = data.get("subject")
    body = data.get("body")
    recipient_ids = data.get("recipients") # Expecting list of user IDs
    
    if not subject or not body or not recipient_ids:
        return jsonify({"message": "Subject, body, and recipients are required"}), 400

    # Fetch recipient emails based on IDs (assuming User model)
    # recipients_emails = [user.email for user in User.query.filter(User.id.in_(recipient_ids)).all()]
    recipients_emails = [f"user{id}@example.com" for id in recipient_ids] # Mock emails

    # Simulate sending email draft request to Manus API
    print(f"Simulating email draft request: Subject='{subject}', Recipients={recipients_emails}")
    # response = requests.post(
    #     f"{MANUS_API_ENDPOINT}/draft_email",
    #     headers={"Authorization": f"Bearer {MANUS_API_KEY}"},
    #     json={"subject": subject, "body": body, "recipients": recipients_emails}
    # )
    
    # Mock successful response
    return jsonify({"message": "Email draft submitted to Manus successfully (simulated)", "draft_id": "sim_draft_456"}), 200

