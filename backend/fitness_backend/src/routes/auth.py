from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User, Role, UserRole
import uuid
import jwt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT - in production, this should be an environment variable
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev_secret_key')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        role='member'  # Default role is member
    )
    
    try:
        db.session.add(new_user)
        
        # Assign default member role
        member_role = Role.query.filter_by(name='member').first()
        if not member_role:
            # Create member role if it doesn't exist
            member_role = Role(
                id=str(uuid.uuid4()),
                name='member',
                description='Regular member with basic permissions'
            )
            db.session.add(member_role)
            db.session.flush()
        
        # Create user-role association
        user_role = UserRole(
            id=str(uuid.uuid4()),
            user_id=new_user.id,
            role_id=member_role.id
        )
        db.session.add(user_role)
        
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'role': new_user.role
            },
            'token': token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate token
    token = generate_token(user)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        },
        'token': token
    }), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    # Get token from header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['sub']
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'profile_image': user.profile_image,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    # Get token from header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['sub']
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Don't reveal if user exists or not for security
    if not user:
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200
    
    # In a real implementation, generate a reset token and send email
    # For now, we'll just return a success message
    
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('new_password'):
        return jsonify({'error': 'Token and new password are required'}), 400
    
    # In a real implementation, verify the reset token and update password
    # For now, we'll just return a success message
    
    return jsonify({'message': 'Password has been reset successfully'}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # JWT is stateless, so we don't need to do anything server-side
    # The client should discard the token
    
    return jsonify({'message': 'Logged out successfully'}), 200


# Helper function to generate JWT token
def generate_token(user):
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        'role': user.role
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
