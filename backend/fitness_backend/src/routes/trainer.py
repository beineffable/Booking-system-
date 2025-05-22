from flask import Blueprint, request, jsonify
from src.models.class import db, Class, ClassType, Booking
from src.models.user import User
from src.routes.auth_middleware import token_required, role_required
from datetime import datetime, timedelta
import uuid

trainer_bp = Blueprint('trainer', __name__)

@trainer_bp.route('/schedule', methods=['GET'])
@role_required(['trainer', 'admin'])
def get_trainer_schedule(user_id, user_role):
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Determine which trainer's schedule to get
    trainer_id = request.args.get('trainer_id')
    if not trainer_id and user_role == 'trainer':
        trainer_id = user_id
    elif not trainer_id and user_role == 'admin':
        return jsonify({'error': 'Trainer ID is required for admin users'}), 400
    
    # Check if trainer exists
    trainer = User.query.get(trainer_id)
    if not trainer or trainer.role not in ['trainer', 'admin']:
        return jsonify({'error': 'Trainer not found'}), 404
    
    # Base query
    query = Class.query.filter(Class.trainer_id == trainer_id)
    
    # Apply date filters
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(Class.start_time >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(Class.start_time <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Order by start time
    query = query.order_by(Class.start_time)
    
    # Execute query
    classes = query.all()
    
    # Format response
    result = []
    for class_obj in classes:
        # Get booking count
        booking_count = Booking.query.filter(
            Booking.class_id == class_obj.id,
            Booking.status.in_(['booked', 'attended'])
        ).count()
        
        result.append({
            'id': class_obj.id,
            'class_type_id': class_obj.class_type_id,
            'class_type_name': class_obj.class_type.name,
            'start_time': class_obj.start_time.isoformat(),
            'end_time': class_obj.end_time.isoformat(),
            'capacity': class_obj.capacity,
            'booking_count': booking_count,
            'location': class_obj.location,
            'description': class_obj.description,
            'is_cancelled': class_obj.is_cancelled,
            'cancellation_reason': class_obj.cancellation_reason
        })
    
    return jsonify({'classes': result}), 200


@trainer_bp.route('/classes', methods=['POST'])
@role_required(['trainer', 'admin'])
def create_class(user_id, user_role):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['class_type_id', 'start_time', 'end_time', 'capacity', 'location']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Determine trainer ID
    trainer_id = data.get('trainer_id')
    if not trainer_id and user_role == 'trainer':
        trainer_id = user_id
    elif not trainer_id and user_role == 'admin':
        return jsonify({'error': 'Trainer ID is required for admin users'}), 400
    
    # Check if trainer exists
    trainer = User.query.get(trainer_id)
    if not trainer or trainer.role not in ['trainer', 'admin']:
        return jsonify({'error': 'Trainer not found'}), 404
    
    # Check if class type exists
    class_type = ClassType.query.get(data['class_type_id'])
    if not class_type:
        return jsonify({'error': 'Class type not found'}), 404
    
    # Parse dates
    try:
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Validate dates
    if start_time >= end_time:
        return jsonify({'error': 'Start time must be before end time'}), 400
    
    if start_time < datetime.utcnow():
        return jsonify({'error': 'Cannot create a class in the past'}), 400
    
    # Check for scheduling conflicts
    conflicts = Class.query.filter(
        Class.trainer_id == trainer_id,
        Class.is_cancelled == False,
        db.or_(
            db.and_(Class.start_time <= start_time, Class.end_time > start_time),
            db.and_(Class.start_time < end_time, Class.end_time >= end_time),
            db.and_(Class.start_time >= start_time, Class.end_time <= end_time)
        )
    ).all()
    
    if conflicts:
        return jsonify({'error': 'Scheduling conflict with existing classes'}), 409
    
    # Create new class
    new_class = Class(
        id=str(uuid.uuid4()),
        class_type_id=data['class_type_id'],
        trainer_id=trainer_id,
        start_time=start_time,
        end_time=end_time,
        capacity=data['capacity'],
        location=data['location'],
        description=data.get('description')
    )
    
    try:
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            'message': 'Class created successfully',
            'class_id': new_class.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@trainer_bp.route('/classes/<class_id>', methods=['PUT'])
@role_required(['trainer', 'admin'])
def update_class(class_id, user_id, user_role):
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check permissions
    if user_role == 'trainer' and class_obj.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check if class has already started
    if class_obj.start_time < datetime.utcnow():
        return jsonify({'error': 'Cannot update a class that has already started'}), 400
    
    # Update fields
    if 'class_type_id' in data:
        # Check if class type exists
        class_type = ClassType.query.get(data['class_type_id'])
        if not class_type:
            return jsonify({'error': 'Class type not found'}), 404
        class_obj.class_type_id = data['class_type_id']
    
    if 'trainer_id' in data and user_role == 'admin':
        # Check if trainer exists
        trainer = User.query.get(data['trainer_id'])
        if not trainer or trainer.role not in ['trainer', 'admin']:
            return jsonify({'error': 'Trainer not found'}), 404
        class_obj.trainer_id = data['trainer_id']
    
    # Update dates if provided
    new_start_time = class_obj.start_time
    new_end_time = class_obj.end_time
    
    if 'start_time' in data:
        try:
            new_start_time = datetime.fromisoformat(data['start_time'])
        except ValueError:
            return jsonify({'error': 'Invalid start_time format'}), 400
    
    if 'end_time' in data:
        try:
            new_end_time = datetime.fromisoformat(data['end_time'])
        except ValueError:
            return jsonify({'error': 'Invalid end_time format'}), 400
    
    # Validate dates
    if new_start_time >= new_end_time:
        return jsonify({'error': 'Start time must be before end time'}), 400
    
    if new_start_time < datetime.utcnow():
        return jsonify({'error': 'Cannot schedule a class in the past'}), 400
    
    # Check for scheduling conflicts if dates changed
    if new_start_time != class_obj.start_time or new_end_time != class_obj.end_time:
        conflicts = Class.query.filter(
            Class.id != class_id,
            Class.trainer_id == class_obj.trainer_id,
            Class.is_cancelled == False,
            db.or_(
                db.and_(Class.start_time <= new_start_time, Class.end_time > new_start_time),
                db.and_(Class.start_time < new_end_time, Class.end_time >= new_end_time),
                db.and_(Class.start_time >= new_start_time, Class.end_time <= new_end_time)
            )
        ).all()
        
        if conflicts:
            return jsonify({'error': 'Scheduling conflict with existing classes'}), 409
        
        class_obj.start_time = new_start_time
        class_obj.end_time = new_end_time
    
    # Update other fields
    if 'capacity' in data:
        # Check if new capacity is less than current bookings
        booking_count = Booking.query.filter(
            Booking.class_id == class_id,
            Booking.status.in_(['booked', 'attended'])
        ).count()
        
        if data['capacity'] < booking_count:
            return jsonify({'error': f'Cannot reduce capacity below current booking count ({booking_count})'}), 400
        
        class_obj.capacity = data['capacity']
    
    if 'location' in data:
        class_obj.location = data['location']
    
    if 'description' in data:
        class_obj.description = data['description']
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Class updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@trainer_bp.route('/classes/<class_id>/cancel', methods=['POST'])
@role_required(['trainer', 'admin'])
def cancel_class(class_id, user_id, user_role):
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check permissions
    if user_role == 'trainer' and class_obj.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if class is already cancelled
    if class_obj.is_cancelled:
        return jsonify({'error': 'Class is already cancelled'}), 400
    
    # Check if class has already ended
    if class_obj.end_time < datetime.utcnow():
        return jsonify({'error': 'Cannot cancel a class that has already ended'}), 400
    
    # Get cancellation reason
    data = request.get_json() or {}
    cancellation_reason = data.get('reason')
    if not cancellation_reason:
        return jsonify({'error': 'Cancellation reason is required'}), 400
    
    # Update class
    class_obj.is_cancelled = True
    class_obj.cancellation_reason = cancellation_reason
    
    try:
        # Get all bookings for this class
        bookings = Booking.query.filter(
            Booking.class_id == class_id,
            Booking.status == 'booked'
        ).all()
        
        # Cancel all bookings and refund credits
        for booking in bookings:
            booking.status = 'cancelled'
            booking.cancellation_time = datetime.utcnow()
            booking.cancellation_reason = 'Class cancelled by trainer'
            
            # Refund credits if applicable
            if booking.credits_used > 0:
                from src.models.membership import Membership
                
                active_membership = Membership.query.filter(
                    Membership.user_id == booking.user_id,
                    Membership.status == 'active',
                    Membership.end_date >= datetime.utcnow()
                ).first()
                
                if active_membership and active_membership.remaining_credits is not None:
                    active_membership.remaining_credits += booking.credits_used
        
        db.session.commit()
        
        return jsonify({'message': 'Class cancelled successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@trainer_bp.route('/classes/<class_id>/attendees', methods=['GET'])
@role_required(['trainer', 'admin'])
def get_class_attendees(class_id, user_id, user_role):
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check permissions
    if user_role == 'trainer' and class_obj.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get bookings
    bookings = Booking.query.filter(
        Booking.class_id == class_id
    ).all()
    
    # Format response
    result = []
    for booking in bookings:
        user = User.query.get(booking.user_id)
        if not user:
            continue
        
        result.append({
            'booking_id': booking.id,
            'user_id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phone,
            'status': booking.status,
            'booking_time': booking.booking_time.isoformat(),
            'check_in_time': booking.check_in_time.isoformat() if booking.check_in_time else None
        })
    
    return jsonify({'attendees': result}), 200


@trainer_bp.route('/classes/<class_id>/check-in/<booking_id>', methods=['POST'])
@role_required(['trainer', 'admin'])
def check_in_attendee(class_id, booking_id, user_id, user_role):
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking or booking.class_id != class_id:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check permissions
    if user_role == 'trainer' and class_obj.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if booking can be checked in
    if booking.status != 'booked':
        return jsonify({'error': f'Cannot check in booking with status: {booking.status}'}), 400
    
    # Update booking
    booking.status = 'attended'
    booking.check_in_time = datetime.utcnow()
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Attendee checked in successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@trainer_bp.route('/classes/<class_id>/no-show/<booking_id>', methods=['POST'])
@role_required(['trainer', 'admin'])
def mark_no_show(class_id, booking_id, user_id, user_role):
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking or booking.class_id != class_id:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check permissions
    if user_role == 'trainer' and class_obj.trainer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if class has started
    if class_obj.start_time > datetime.utcnow():
        return jsonify({'error': 'Cannot mark no-show before class starts'}), 400
    
    # Check if booking can be marked as no-show
    if booking.status != 'booked':
        return jsonify({'error': f'Cannot mark no-show for booking with status: {booking.status}'}), 400
    
    # Update booking
    booking.status = 'no-show'
    
    try:
        db.session.commit()
        
        return jsonify({'message': 'Attendee marked as no-show successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@trainer_bp.route('/clients', methods=['GET'])
@role_required(['trainer', 'admin'])
def get_trainer_clients(user_id, user_role):
    # Determine which trainer's clients to get
    trainer_id = request.args.get('trainer_id')
    if not trainer_id and user_role == 'trainer':
        trainer_id = user_id
    elif not trainer_id and user_role == 'admin':
        return jsonify({'error': 'Trainer ID is required for admin users'}), 400
    
    # Get all users who have booked classes with this trainer
    client_bookings = db.session.query(Booking.user_id, db.func.count(Booking.id).label('booking_count')) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(Class.trainer_id == trainer_id) \
        .group_by(Booking.user_id) \
        .all()
    
    # Format response
    result = []
    for user_id, booking_count in client_bookings:
        user = User.query.get(user_id)
        if not user:
            continue
        
        # Get last attended class
        last_attended = Booking.query.join(Class) \
            .filter(Booking.user_id == user_id, Class.trainer_id == trainer_id, Booking.status == 'attended') \
            .order_by(Class.start_time.desc()) \
            .first()
        
        # Get next upcoming class
        next_class = Booking.query.join(Class) \
            .filter(
                Booking.user_id == user_id, 
                Class.trainer_id == trainer_id, 
                Booking.status == 'booked',
                Class.start_time > datetime.utcnow()
            ) \
            .order_by(Class.start_time) \
            .first()
        
        result.append({
            'user_id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phone,
            'booking_count': booking_count,
            'last_attended': last_attended.class_obj.start_time.isoformat() if last_attended else None,
            'next_class': next_class.class_obj.start_time.isoformat() if next_class else None
        })
    
    return jsonify({'clients': result}), 200


@trainer_bp.route('/clients/<client_id>', methods=['GET'])
@role_required(['trainer', 'admin'])
def get_client_details(client_id, user_id, user_role):
    # Get client
    client = User.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Determine which trainer's perspective
    trainer_id = request.args.get('trainer_id')
    if not trainer_id and user_role == 'trainer':
        trainer_id = user_id
    elif not trainer_id and user_role == 'admin':
        return jsonify({'error': 'Trainer ID is required for admin users'}), 400
    
    # Get booking history with this trainer
    bookings = Booking.query.join(Class) \
        .filter(Booking.user_id == client_id, Class.trainer_id == trainer_id) \
        .order_by(Class.start_time.desc()) \
        .all()
    
    # Format booking history
    booking_history = []
    for booking in bookings:
        class_obj = booking.class_obj
        booking_history.append({
            'booking_id': booking.id,
            'class_id': class_obj.id,
            'class_type': class_obj.class_type.name,
            'start_time': class_obj.start_time.isoformat(),
            'end_time': class_obj.end_time.isoformat(),
            'status': booking.status,
            'check_in_time': booking.check_in_time.isoformat() if booking.check_in_time else None
        })
    
    # Get attendance statistics
    total_bookings = len(bookings)
    attended = sum(1 for b in bookings if b.status == 'attended')
    no_shows = sum(1 for b in bookings if b.status == 'no-show')
    cancelled = sum(1 for b in bookings if b.status == 'cancelled')
    
    attendance_rate = (attended / total_bookings) * 100 if total_bookings > 0 else 0
    
    # Get client memberships
    from src.models.membership import Membership, MembershipType
    
    memberships = Membership.query.filter(Membership.user_id == client_id).all()
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
            'remaining_credits': membership.remaining_credits
        })
    
    # Format response
    result = {
        'user_id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'email': client.email,
        'phone': client.phone,
        'profile_image': client.profile_image,
        'created_at': client.created_at.isoformat(),
        'last_login': client.last_login.isoformat() if client.last_login else None,
        'booking_history': booking_history,
        'statistics': {
            'total_bookings': total_bookings,
            'attended': attended,
            'no_shows': no_shows,
            'cancelled': cancelled,
            'attendance_rate': round(attendance_rate, 2)
        },
        'memberships': membership_info
    }
    
    return jsonify({'client': result}), 200
