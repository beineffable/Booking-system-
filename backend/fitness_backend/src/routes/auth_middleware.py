import jwt
from functools import wraps
from flask import request, jsonify, current_app
import os

# Secret key for JWT - in production, this should be an environment variable
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev_secret_key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header is missing or invalid'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Add user_id to kwargs
            kwargs['user_id'] = payload['sub']
            kwargs['user_role'] = payload['role']
            return f(*args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authorization header is missing or invalid'}), 401
            
            token = auth_header.split(' ')[1]
            
            try:
                # Decode token
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_role = payload['role']
                
                # Check if user has required role
                if user_role not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Add user_id to kwargs
                kwargs['user_id'] = payload['sub']
                kwargs['user_role'] = user_role
                return f(*args, **kwargs)
            
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
        
        return decorated_function
    return decorator

# Usage examples:
# @token_required - requires any authenticated user
# @role_required(['admin']) - requires admin role
# @role_required(['admin', 'trainer']) - requires admin or trainer role
