from flask import Blueprint, request, jsonify
from src.models.user import db, User, Role, Permission, RolePermission, UserRole
from src.models.membership import MembershipType, Membership, Payment
from src.models.class import ClassType, Class, Booking, WaitlistEntry
from src.routes.auth_middleware import role_required
from datetime import datetime, timedelta
import uuid

admin_bp = Blueprint('admin', __name__)

# ===== User Management =====

@admin_bp.route('/users', methods=['GET'])
@role_required(['admin'])
def get_users(user_id, user_role):
    # Get query parameters
    role = request.args.get('role')
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Base query
    query = User.query
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if status:
        is_active = status == 'active'
        query = query.filter(User.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Order by name
    query = query.order_by(User.first_name, User.last_name)
    
    # Execute query
    users = query.all()
    
    # Format response
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    
    return jsonify({'users': result}), 200


@admin_bp.route('/users/<user_id>', methods=['GET'])
@role_required(['admin'])
def get_user(user_id, user_role):
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user roles
    user_roles = UserRole.query.filter(UserRole.user_id == user_id).all()
    roles = []
    for user_role in user_roles:
        role = Role.query.get(user_role.role_id)
        if role:
            roles.append({
                'id': role.id,
                'name': role.name,
                'description': role.description
            })
    
    # Get memberships
    memberships = Membership.query.filter(Membership.user_id == user_id).all()
    membership_info = []
    for membership in memberships:
        membership_type = MembershipType.query.get(membership.membership_type_id)
        if not membership_type:
            continue
        
        membership_info.append({
            'id': membership.id,
            'type': membership_type.name,
            'start_date': membership.start_date.isoformat(),
            'end_date': membership.end_date.isoformat(),
            'status': membership.status,
            'remaining_credits': membership.remaining_credits,
            'auto_renew': membership.auto_renew
        })
    
    # Get payment history
    payments = Payment.query.filter(Payment.user_id == user_id).order_by(Payment.payment_date.desc()).all()
    payment_history = []
    for payment in payments:
        payment_history.append({
            'id': payment.id,
            'amount': payment.amount,
            'currency': payment.currency,
            'payment_method': payment.payment_method,
            'payment_status': payment.payment_status,
            'payment_date': payment.payment_date.isoformat(),
            'description': payment.description
        })
    
    # Get booking history
    bookings = Booking.query.filter(Booking.user_id == user_id).all()
    booking_history = []
    for booking in bookings:
        class_obj = booking.class_obj
        if not class_obj:
            continue
        
        booking_history.append({
            'id': booking.id,
            'class_type': class_obj.class_type.name,
            'start_time': class_obj.start_time.isoformat(),
            'status': booking.status,
            'booking_time': booking.booking_time.isoformat(),
            'check_in_time': booking.check_in_time.isoformat() if booking.check_in_time else None
        })
    
    # Format response
    result = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'profile_image': user.profile_image,
        'role': user.role,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'roles': roles,
        'memberships': membership_info,
        'payment_history': payment_history,
        'booking_history': booking_history
    }
    
    return jsonify({'user': result}), 200


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@role_required(['admin'])
def update_user(user_id, user_role):
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'profile_image' in data:
        user.profile_image = data['profile_image']
    
    if 'role' in data:
        # Validate role
        if data['role'] not in ['member', 'trainer', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
        user.role = data['role']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<user_id>/roles', methods=['POST'])
@role_required(['admin'])
def assign_role(user_id, user_role):
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data or 'role_id' not in data:
        return jsonify({'error': 'Role ID is required'}), 400
    
    role_id = data['role_id']
    
    # Check if role exists
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    # Check if user already has this role
    existing_role = UserRole.query.filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if existing_role:
        return jsonify({'error': 'User already has this role'}), 409
    
    # Create user-role association
    user_role = UserRole(
        id=str(uuid.uuid4()),
        user_id=user_id,
        role_id=role_id
    )
    
    try:
        db.session.add(user_role)
        db.session.commit()
        
        return jsonify({'message': 'Role assigned successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<user_id>/roles/<role_id>', methods=['DELETE'])
@role_required(['admin'])
def remove_role(user_id, role_id, user_role):
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if role exists
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    # Get user-role association
    user_role_obj = UserRole.query.filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if not user_role_obj:
        return jsonify({'error': 'User does not have this role'}), 404
    
    try:
        db.session.delete(user_role_obj)
        db.session.commit()
        
        return jsonify({'message': 'Role removed successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users', methods=['POST'])
@role_required(['admin'])
def create_user(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Validate role
    if data['role'] not in ['member', 'trainer', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Create new user
    from werkzeug.security import generate_password_hash
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        profile_image=data.get('profile_image'),
        role=data['role'],
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(new_user)
        
        # Assign role
        role = Role.query.filter_by(name=data['role']).first()
        if not role:
            # Create role if it doesn't exist
            role = Role(
                id=str(uuid.uuid4()),
                name=data['role'],
                description=f'{data["role"].capitalize()} role'
            )
            db.session.add(role)
            db.session.flush()
        
        # Create user-role association
        user_role_obj = UserRole(
            id=str(uuid.uuid4()),
            user_id=new_user.id,
            role_id=role.id
        )
        db.session.add(user_role_obj)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': new_user.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Membership Management =====

@admin_bp.route('/membership-types', methods=['GET'])
@role_required(['admin'])
def get_membership_types(user_id, user_role):
    # Get all membership types
    membership_types = MembershipType.query.filter_by(is_active=True).all()
    
    # Format response
    result = []
    for membership_type in membership_types:
        result.append({
            'id': membership_type.id,
            'name': membership_type.name,
            'description': membership_type.description,
            'price': membership_type.price,
            'duration_days': membership_type.duration_days,
            'class_credits': membership_type.class_credits,
            'features': membership_type.features,
            'is_active': membership_type.is_active
        })
    
    return jsonify({'membership_types': result}), 200


@admin_bp.route('/membership-types', methods=['POST'])
@role_required(['admin'])
def create_membership_type(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'price', 'duration_days']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new membership type
    new_membership_type = MembershipType(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        duration_days=data['duration_days'],
        class_credits=data.get('class_credits'),
        features=data.get('features'),
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(new_membership_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Membership type created successfully',
            'membership_type_id': new_membership_type.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/membership-types/<membership_type_id>', methods=['PUT'])
@role_required(['admin'])
def update_membership_type(membership_type_id, user_id, user_role):
    # Get membership type
    membership_type = MembershipType.query.get(membership_type_id)
    if not membership_type:
        return jsonify({'error': 'Membership type not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'name' in data:
        membership_type.name = data['name']
    
    if 'description' in data:
        membership_type.description = data['description']
    
    if 'price' in data:
        membership_type.price = data['price']
    
    if 'duration_days' in data:
        membership_type.duration_days = data['duration_days']
    
    if 'class_credits' in data:
        membership_type.class_credits = data['class_credits']
    
    if 'features' in data:
        membership_type.features = data['features']
    
    if 'is_active' in data:
        membership_type.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Membership type updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/memberships', methods=['GET'])
@role_required(['admin'])
def get_memberships(user_id, user_role):
    # Get query parameters
    status = request.args.get('status')
    user_id_param = request.args.get('user_id')
    
    # Base query
    query = Membership.query
    
    # Apply filters
    if status:
        query = query.filter(Membership.status == status)
    
    if user_id_param:
        query = query.filter(Membership.user_id == user_id_param)
    
    # Order by end date
    query = query.order_by(Membership.end_date.desc())
    
    # Execute query
    memberships = query.all()
    
    # Format response
    result = []
    for membership in memberships:
        user = User.query.get(membership.user_id)
        membership_type = MembershipType.query.get(membership.membership_type_id)
        
        if not user or not membership_type:
            continue
        
        result.append({
            'id': membership.id,
            'user_id': membership.user_id,
            'user_name': f"{user.first_name} {user.last_name}",
            'membership_type_id': membership.membership_type_id,
            'membership_type_name': membership_type.name,
            'start_date': membership.start_date.isoformat(),
            'end_date': membership.end_date.isoformat(),
            'status': membership.status,
            'remaining_credits': membership.remaining_credits,
            'auto_renew': membership.auto_renew
        })
    
    return jsonify({'memberships': result}), 200


@admin_bp.route('/memberships', methods=['POST'])
@role_required(['admin'])
def create_membership(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_id', 'membership_type_id', 'start_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if membership type exists
    membership_type = MembershipType.query.get(data['membership_type_id'])
    if not membership_type:
        return jsonify({'error': 'Membership type not found'}), 404
    
    # Parse start date
    try:
        start_date = datetime.fromisoformat(data['start_date'])
    except ValueError:
        return jsonify({'error': 'Invalid start_date format'}), 400
    
    # Calculate end date
    end_date = start_date + timedelta(days=membership_type.duration_days)
    
    # Create new membership
    new_membership = Membership(
        id=str(uuid.uuid4()),
        user_id=data['user_id'],
        membership_type_id=data['membership_type_id'],
        start_date=start_date,
        end_date=end_date,
        status=data.get('status', 'active'),
        remaining_credits=membership_type.class_credits,
        auto_renew=data.get('auto_renew', True)
    )
    
    try:
        db.session.add(new_membership)
        
        # Create payment record if price > 0
        if membership_type.price > 0:
            payment = Payment(
                id=str(uuid.uuid4()),
                user_id=data['user_id'],
                membership_id=new_membership.id,
                amount=membership_type.price,
                currency='CHF',
                payment_method=data.get('payment_method', 'manual'),
                payment_status='completed',
                payment_date=datetime.utcnow(),
                description=f"Payment for {membership_type.name} membership"
            )
            db.session.add(payment)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Membership created successfully',
            'membership_id': new_membership.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/memberships/<membership_id>', methods=['PUT'])
@role_required(['admin'])
def update_membership(membership_id, user_id, user_role):
    # Get membership
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'status' in data:
        membership.status = data['status']
    
    if 'end_date' in data:
        try:
            end_date = datetime.fromisoformat(data['end_date'])
            membership.end_date = end_date
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    if 'remaining_credits' in data:
        membership.remaining_credits = data['remaining_credits']
    
    if 'auto_renew' in data:
        membership.auto_renew = data['auto_renew']
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Membership updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/memberships/<membership_id>/cancel', methods=['POST'])
@role_required(['admin'])
def cancel_membership(membership_id, user_id, user_role):
    # Get membership
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    # Check if membership can be cancelled
    if membership.status != 'active':
        return jsonify({'error': f'Cannot cancel membership with status: {membership.status}'}), 400
    
    # Update membership
    membership.status = 'cancelled'
    membership.auto_renew = False
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Membership cancelled successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Class Management =====

@admin_bp.route('/class-types', methods=['GET'])
@role_required(['admin'])
def get_class_types(user_id, user_role):
    # Get all class types
    class_types = ClassType.query.filter_by(is_active=True).all()
    
    # Format response
    result = []
    for class_type in class_types:
        result.append({
            'id': class_type.id,
            'name': class_type.name,
            'description': class_type.description,
            'color': class_type.color,
            'duration_minutes': class_type.duration_minutes,
            'default_capacity': class_type.default_capacity,
            'credits_required': class_type.credits_required,
            'is_active': class_type.is_active
        })
    
    return jsonify({'class_types': result}), 200


@admin_bp.route('/class-types', methods=['POST'])
@role_required(['admin'])
def create_class_type(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'duration_minutes', 'default_capacity']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new class type
    new_class_type = ClassType(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description'),
        color=data.get('color'),
        duration_minutes=data['duration_minutes'],
        default_capacity=data['default_capacity'],
        credits_required=data.get('credits_required', 1),
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(new_class_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Class type created successfully',
            'class_type_id': new_class_type.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/class-types/<class_type_id>', methods=['PUT'])
@role_required(['admin'])
def update_class_type(class_type_id, user_id, user_role):
    # Get class type
    class_type = ClassType.query.get(class_type_id)
    if not class_type:
        return jsonify({'error': 'Class type not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'name' in data:
        class_type.name = data['name']
    
    if 'description' in data:
        class_type.description = data['description']
    
    if 'color' in data:
        class_type.color = data['color']
    
    if 'duration_minutes' in data:
        class_type.duration_minutes = data['duration_minutes']
    
    if 'default_capacity' in data:
        class_type.default_capacity = data['default_capacity']
    
    if 'credits_required' in data:
        class_type.credits_required = data['credits_required']
    
    if 'is_active' in data:
        class_type.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Class type updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Payment Management =====

@admin_bp.route('/payments', methods=['GET'])
@role_required(['admin'])
def get_payments(user_id, user_role):
    # Get query parameters
    status = request.args.get('status')
    user_id_param = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = Payment.query
    
    # Apply filters
    if status:
        query = query.filter(Payment.payment_status == status)
    
    if user_id_param:
        query = query.filter(Payment.user_id == user_id_param)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(Payment.payment_date >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(Payment.payment_date <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Order by payment date
    query = query.order_by(Payment.payment_date.desc())
    
    # Execute query
    payments = query.all()
    
    # Format response
    result = []
    for payment in payments:
        user = User.query.get(payment.user_id)
        if not user:
            continue
        
        result.append({
            'id': payment.id,
            'user_id': payment.user_id,
            'user_name': f"{user.first_name} {user.last_name}",
            'membership_id': payment.membership_id,
            'amount': payment.amount,
            'currency': payment.currency,
            'payment_method': payment.payment_method,
            'payment_status': payment.payment_status,
            'transaction_id': payment.transaction_id,
            'payment_date': payment.payment_date.isoformat(),
            'description': payment.description
        })
    
    return jsonify({'payments': result}), 200


@admin_bp.route('/payments', methods=['POST'])
@role_required(['admin'])
def create_payment(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_id', 'amount', 'payment_method', 'payment_status']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if membership exists if provided
    if data.get('membership_id'):
        membership = Membership.query.get(data['membership_id'])
        if not membership:
            return jsonify({'error': 'Membership not found'}), 404
    
    # Create new payment
    new_payment = Payment(
        id=str(uuid.uuid4()),
        user_id=data['user_id'],
        membership_id=data.get('membership_id'),
        amount=data['amount'],
        currency=data.get('currency', 'CHF'),
        payment_method=data['payment_method'],
        payment_status=data['payment_status'],
        transaction_id=data.get('transaction_id'),
        payment_date=datetime.fromisoformat(data['payment_date']) if data.get('payment_date') else datetime.utcnow(),
        description=data.get('description')
    )
    
    try:
        db.session.add(new_payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment created successfully',
            'payment_id': new_payment.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/payments/<payment_id>', methods=['PUT'])
@role_required(['admin'])
def update_payment(payment_id, user_id, user_role):
    # Get payment
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'payment_status' in data:
        payment.payment_status = data['payment_status']
    
    if 'transaction_id' in data:
        payment.transaction_id = data['transaction_id']
    
    if 'description' in data:
        payment.description = data['description']
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Payment updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== Dashboard and Analytics =====

@admin_bp.route('/dashboard', methods=['GET'])
@role_required(['admin'])
def get_dashboard(user_id, user_role):
    # Get time range
    time_range = request.args.get('time_range', 'month')
    
    if time_range == 'week':
        start_date = datetime.utcnow() - timedelta(days=7)
    elif time_range == 'month':
        start_date = datetime.utcnow() - timedelta(days=30)
    elif time_range == 'year':
        start_date = datetime.utcnow() - timedelta(days=365)
    else:
        return jsonify({'error': 'Invalid time_range. Must be week, month, or year'}), 400
    
    # Get active members count
    active_members = Membership.query.filter(
        Membership.status == 'active',
        Membership.end_date >= datetime.utcnow()
    ).count()
    
    # Get new members count
    new_members = User.query.filter(
        User.created_at >= start_date,
        User.role == 'member'
    ).count()
    
    # Get total revenue
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.payment_date >= start_date,
        Payment.payment_status == 'completed'
    ).scalar() or 0
    
    # Get class attendance
    class_attendance = db.session.query(db.func.count(Booking.id)).filter(
        Booking.status == 'attended',
        Booking.check_in_time >= start_date
    ).scalar() or 0
    
    # Get class bookings
    class_bookings = db.session.query(db.func.count(Booking.id)).filter(
        Booking.booking_time >= start_date
    ).scalar() or 0
    
    # Get no-show rate
    no_shows = db.session.query(db.func.count(Booking.id)).filter(
        Booking.status == 'no-show',
        Booking.booking_time >= start_date
    ).scalar() or 0
    
    no_show_rate = (no_shows / class_bookings) * 100 if class_bookings > 0 else 0
    
    # Get popular class types
    popular_classes = db.session.query(
        ClassType.name,
        db.func.count(Booking.id).label('booking_count')
    ).join(Class, ClassType.id == Class.class_type_id) \
     .join(Booking, Class.id == Booking.class_id) \
     .filter(Booking.booking_time >= start_date) \
     .group_by(ClassType.name) \
     .order_by(db.desc('booking_count')) \
     .limit(5) \
     .all()
    
    popular_class_types = [{'name': name, 'booking_count': count} for name, count in popular_classes]
    
    # Get membership distribution
    membership_distribution = db.session.query(
        MembershipType.name,
        db.func.count(Membership.id).label('member_count')
    ).join(Membership, MembershipType.id == Membership.membership_type_id) \
     .filter(Membership.status == 'active', Membership.end_date >= datetime.utcnow()) \
     .group_by(MembershipType.name) \
     .all()
    
    membership_types = [{'name': name, 'member_count': count} for name, count in membership_distribution]
    
    # Format response
    result = {
        'active_members': active_members,
        'new_members': new_members,
        'total_revenue': total_revenue,
        'class_attendance': class_attendance,
        'class_bookings': class_bookings,
        'no_show_rate': round(no_show_rate, 2),
        'popular_class_types': popular_class_types,
        'membership_types': membership_types
    }
    
    return jsonify({'dashboard': result}), 200


# ===== Role and Permission Management =====

@admin_bp.route('/roles', methods=['GET'])
@role_required(['admin'])
def get_roles(user_id, user_role):
    # Get all roles
    roles = Role.query.all()
    
    # Format response
    result = []
    for role in roles:
        # Get permissions for this role
        role_permissions = RolePermission.query.filter(RolePermission.role_id == role.id).all()
        permissions = []
        
        for role_permission in role_permissions:
            permission = Permission.query.get(role_permission.permission_id)
            if permission:
                permissions.append({
                    'id': permission.id,
                    'module': permission.module,
                    'action': permission.action,
                    'scope': permission.scope,
                    'description': permission.description
                })
        
        result.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions': permissions
        })
    
    return jsonify({'roles': result}), 200


@admin_bp.route('/roles', methods=['POST'])
@role_required(['admin'])
def create_role(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    if not data or 'name' not in data:
        return jsonify({'error': 'Role name is required'}), 400
    
    # Check if role already exists
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Role with this name already exists'}), 409
    
    # Create new role
    new_role = Role(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description')
    )
    
    try:
        db.session.add(new_role)
        db.session.commit()
        
        return jsonify({
            'message': 'Role created successfully',
            'role_id': new_role.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/permissions', methods=['GET'])
@role_required(['admin'])
def get_permissions(user_id, user_role):
    # Get all permissions
    permissions = Permission.query.all()
    
    # Format response
    result = []
    for permission in permissions:
        result.append({
            'id': permission.id,
            'module': permission.module,
            'action': permission.action,
            'scope': permission.scope,
            'description': permission.description
        })
    
    return jsonify({'permissions': result}), 200


@admin_bp.route('/permissions', methods=['POST'])
@role_required(['admin'])
def create_permission(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['module', 'action', 'scope']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if permission already exists
    existing_permission = Permission.query.filter_by(
        module=data['module'],
        action=data['action'],
        scope=data['scope']
    ).first()
    
    if existing_permission:
        return jsonify({'error': 'Permission already exists'}), 409
    
    # Create new permission
    new_permission = Permission(
        id=str(uuid.uuid4()),
        module=data['module'],
        action=data['action'],
        scope=data['scope'],
        description=data.get('description')
    )
    
    try:
        db.session.add(new_permission)
        db.session.commit()
        
        return jsonify({
            'message': 'Permission created successfully',
            'permission_id': new_permission.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roles/<role_id>/permissions', methods=['POST'])
@role_required(['admin'])
def assign_permission_to_role(role_id, user_id, user_role):
    # Get role
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    # Get request data
    data = request.get_json()
    if not data or 'permission_id' not in data:
        return jsonify({'error': 'Permission ID is required'}), 400
    
    permission_id = data['permission_id']
    
    # Check if permission exists
    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'error': 'Permission not found'}), 404
    
    # Check if role already has this permission
    existing_role_permission = RolePermission.query.filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if existing_role_permission:
        return jsonify({'error': 'Role already has this permission'}), 409
    
    # Create role-permission association
    role_permission = RolePermission(
        id=str(uuid.uuid4()),
        role_id=role_id,
        permission_id=permission_id
    )
    
    try:
        db.session.add(role_permission)
        db.session.commit()
        
        return jsonify({'message': 'Permission assigned to role successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roles/<role_id>/permissions/<permission_id>', methods=['DELETE'])
@role_required(['admin'])
def remove_permission_from_role(role_id, permission_id, user_id, user_role):
    # Get role
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    # Check if permission exists
    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'error': 'Permission not found'}), 404
    
    # Get role-permission association
    role_permission = RolePermission.query.filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if not role_permission:
        return jsonify({'error': 'Role does not have this permission'}), 404
    
    try:
        db.session.delete(role_permission)
        db.session.commit()
        
        return jsonify({'message': 'Permission removed from role successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
