from flask import Blueprint, request, jsonify
from src.models.class import db, Class, Booking, WaitlistEntry
from src.models.user import User
from src.models.membership import Membership
from src.routes.auth_middleware import token_required
from datetime import datetime, timedelta
import uuid

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/classes', methods=['GET'])
@token_required
def get_classes(user_id, user_role):
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    class_type = request.args.get('class_type')
    trainer_id = request.args.get('trainer_id')
    
    # Base query
    query = Class.query.filter(Class.is_cancelled == False)
    
    # Apply filters
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
    
    if class_type:
        query = query.filter(Class.class_type_id == class_type)
    
    if trainer_id:
        query = query.filter(Class.trainer_id == trainer_id)
    
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
        
        # Check if user has booked this class
        user_booking = Booking.query.filter(
            Booking.class_id == class_obj.id,
            Booking.user_id == user_id
        ).first()
        
        # Get trainer info
        trainer = User.query.get(class_obj.trainer_id)
        trainer_name = f"{trainer.first_name} {trainer.last_name}" if trainer else "Unknown"
        
        result.append({
            'id': class_obj.id,
            'class_type_id': class_obj.class_type_id,
            'class_type_name': class_obj.class_type.name,
            'trainer_id': class_obj.trainer_id,
            'trainer_name': trainer_name,
            'start_time': class_obj.start_time.isoformat(),
            'end_time': class_obj.end_time.isoformat(),
            'capacity': class_obj.capacity,
            'booking_count': booking_count,
            'available_spots': max(0, class_obj.capacity - booking_count),
            'location': class_obj.location,
            'description': class_obj.description,
            'user_booking_status': user_booking.status if user_booking else None
        })
    
    return jsonify({'classes': result}), 200


@booking_bp.route('/classes/<class_id>', methods=['GET'])
@token_required
def get_class(class_id, user_id, user_role):
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Get booking count
    booking_count = Booking.query.filter(
        Booking.class_id == class_obj.id,
        Booking.status.in_(['booked', 'attended'])
    ).count()
    
    # Check if user has booked this class
    user_booking = Booking.query.filter(
        Booking.class_id == class_obj.id,
        Booking.user_id == user_id
    ).first()
    
    # Get trainer info
    trainer = User.query.get(class_obj.trainer_id)
    trainer_name = f"{trainer.first_name} {trainer.last_name}" if trainer else "Unknown"
    
    # Get waitlist count
    waitlist_count = WaitlistEntry.query.filter(
        WaitlistEntry.class_id == class_obj.id,
        WaitlistEntry.status == 'waiting'
    ).count()
    
    # Check if user is on waitlist
    user_waitlist = WaitlistEntry.query.filter(
        WaitlistEntry.class_id == class_obj.id,
        WaitlistEntry.user_id == user_id,
        WaitlistEntry.status == 'waiting'
    ).first()
    
    result = {
        'id': class_obj.id,
        'class_type_id': class_obj.class_type_id,
        'class_type_name': class_obj.class_type.name,
        'trainer_id': class_obj.trainer_id,
        'trainer_name': trainer_name,
        'start_time': class_obj.start_time.isoformat(),
        'end_time': class_obj.end_time.isoformat(),
        'capacity': class_obj.capacity,
        'booking_count': booking_count,
        'available_spots': max(0, class_obj.capacity - booking_count),
        'location': class_obj.location,
        'description': class_obj.description,
        'is_cancelled': class_obj.is_cancelled,
        'cancellation_reason': class_obj.cancellation_reason,
        'user_booking_status': user_booking.status if user_booking else None,
        'waitlist_count': waitlist_count,
        'user_waitlist_position': user_waitlist.position if user_waitlist else None
    }
    
    return jsonify({'class': result}), 200


@booking_bp.route('/bookings', methods=['POST'])
@token_required
def create_booking(user_id, user_role):
    data = request.get_json()
    
    if not data or not data.get('class_id'):
        return jsonify({'error': 'Class ID is required'}), 400
    
    class_id = data['class_id']
    
    # Get class
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check if class is in the past
    if class_obj.start_time < datetime.utcnow():
        return jsonify({'error': 'Cannot book a class that has already started'}), 400
    
    # Check if class is cancelled
    if class_obj.is_cancelled:
        return jsonify({'error': 'Cannot book a cancelled class'}), 400
    
    # Check if user already has a booking for this class
    existing_booking = Booking.query.filter(
        Booking.class_id == class_id,
        Booking.user_id == user_id,
        Booking.status.in_(['booked', 'attended'])
    ).first()
    
    if existing_booking:
        return jsonify({'error': 'You already have a booking for this class'}), 409
    
    # Check if user has an active membership
    active_membership = Membership.query.filter(
        Membership.user_id == user_id,
        Membership.status == 'active',
        Membership.end_date >= datetime.utcnow()
    ).first()
    
    if not active_membership:
        return jsonify({'error': 'You do not have an active membership'}), 403
    
    # Check if user has enough credits
    credits_required = class_obj.class_type.credits_required
    
    if active_membership.remaining_credits is not None:  # None means unlimited
        if active_membership.remaining_credits < credits_required:
            return jsonify({'error': 'You do not have enough credits'}), 403
    
    # Check if class is full
    booking_count = Booking.query.filter(
        Booking.class_id == class_id,
        Booking.status.in_(['booked', 'attended'])
    ).count()
    
    if booking_count >= class_obj.capacity:
        # Class is full, add to waitlist
        
        # Check if user is already on waitlist
        existing_waitlist = WaitlistEntry.query.filter(
            WaitlistEntry.class_id == class_id,
            WaitlistEntry.user_id == user_id,
            WaitlistEntry.status == 'waiting'
        ).first()
        
        if existing_waitlist:
            return jsonify({'error': 'You are already on the waitlist for this class'}), 409
        
        # Get current max position
        max_position = db.session.query(db.func.max(WaitlistEntry.position)).filter(
            WaitlistEntry.class_id == class_id,
            WaitlistEntry.status == 'waiting'
        ).scalar() or 0
        
        # Create waitlist entry
        waitlist_entry = WaitlistEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            class_id=class_id,
            position=max_position + 1,
            status='waiting'
        )
        
        try:
            db.session.add(waitlist_entry)
            db.session.commit()
            
            return jsonify({
                'message': 'Added to waitlist',
                'waitlist_position': waitlist_entry.position
            }), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Create booking
    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user_id,
        class_id=class_id,
        status='booked',
        credits_used=credits_required
    )
    
    try:
        db.session.add(booking)
        
        # Deduct credits if applicable
        if active_membership.remaining_credits is not None:
            active_membership.remaining_credits -= credits_required
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking_id': booking.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@booking_bp.route('/bookings/<booking_id>/cancel', methods=['POST'])
@token_required
def cancel_booking(booking_id, user_id, user_role):
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if booking belongs to user or user is admin/trainer
    if booking.user_id != user_id and user_role not in ['admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if booking can be cancelled
    if booking.status != 'booked':
        return jsonify({'error': 'Booking cannot be cancelled'}), 400
    
    # Check cancellation timeframe
    class_obj = Class.query.get(booking.class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check if class has already started
    if class_obj.start_time < datetime.utcnow():
        return jsonify({'error': 'Cannot cancel a booking for a class that has already started'}), 400
    
    # Get cancellation reason
    data = request.get_json() or {}
    cancellation_reason = data.get('reason')
    
    # Update booking
    booking.status = 'cancelled'
    booking.cancellation_time = datetime.utcnow()
    booking.cancellation_reason = cancellation_reason
    
    try:
        # Refund credits if applicable
        if booking.credits_used > 0:
            active_membership = Membership.query.filter(
                Membership.user_id == booking.user_id,
                Membership.status == 'active',
                Membership.end_date >= datetime.utcnow()
            ).first()
            
            if active_membership and active_membership.remaining_credits is not None:
                active_membership.remaining_credits += booking.credits_used
        
        db.session.commit()
        
        # Check waitlist and notify next person
        process_waitlist(booking.class_id)
        
        return jsonify({'message': 'Booking cancelled successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@booking_bp.route('/bookings', methods=['GET'])
@token_required
def get_user_bookings(user_id, user_role):
    # Get query parameters
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = Booking.query.filter(Booking.user_id == user_id)
    
    # Apply filters
    if status:
        query = query.filter(Booking.status == status)
    
    # Join with class to filter by date
    query = query.join(Class)
    
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
    
    # Order by class start time
    query = query.order_by(Class.start_time)
    
    # Execute query
    bookings = query.all()
    
    # Format response
    result = []
    for booking in bookings:
        class_obj = booking.class_obj
        trainer = User.query.get(class_obj.trainer_id)
        trainer_name = f"{trainer.first_name} {trainer.last_name}" if trainer else "Unknown"
        
        result.append({
            'id': booking.id,
            'class_id': booking.class_id,
            'class_type_name': class_obj.class_type.name,
            'trainer_name': trainer_name,
            'start_time': class_obj.start_time.isoformat(),
            'end_time': class_obj.end_time.isoformat(),
            'location': class_obj.location,
            'status': booking.status,
            'booking_time': booking.booking_time.isoformat(),
            'cancellation_time': booking.cancellation_time.isoformat() if booking.cancellation_time else None,
            'cancellation_reason': booking.cancellation_reason,
            'check_in_time': booking.check_in_time.isoformat() if booking.check_in_time else None,
            'credits_used': booking.credits_used
        })
    
    return jsonify({'bookings': result}), 200


@booking_bp.route('/waitlist', methods=['GET'])
@token_required
def get_user_waitlist(user_id, user_role):
    # Get waitlist entries for user
    waitlist_entries = WaitlistEntry.query.filter(
        WaitlistEntry.user_id == user_id,
        WaitlistEntry.status == 'waiting'
    ).all()
    
    # Format response
    result = []
    for entry in waitlist_entries:
        class_obj = entry.class_obj
        trainer = User.query.get(class_obj.trainer_id)
        trainer_name = f"{trainer.first_name} {trainer.last_name}" if trainer else "Unknown"
        
        result.append({
            'id': entry.id,
            'class_id': entry.class_id,
            'class_type_name': class_obj.class_type.name,
            'trainer_name': trainer_name,
            'start_time': class_obj.start_time.isoformat(),
            'end_time': class_obj.end_time.isoformat(),
            'location': class_obj.location,
            'position': entry.position,
            'join_time': entry.join_time.isoformat()
        })
    
    return jsonify({'waitlist': result}), 200


@booking_bp.route('/waitlist/<entry_id>/remove', methods=['POST'])
@token_required
def remove_from_waitlist(entry_id, user_id, user_role):
    # Get waitlist entry
    entry = WaitlistEntry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Waitlist entry not found'}), 404
    
    # Check if entry belongs to user or user is admin/trainer
    if entry.user_id != user_id and user_role not in ['admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if entry can be removed
    if entry.status != 'waiting':
        return jsonify({'error': 'Waitlist entry cannot be removed'}), 400
    
    # Update entry
    entry.status = 'removed'
    
    try:
        db.session.commit()
        
        # Reorder waitlist
        reorder_waitlist(entry.class_id)
        
        return jsonify({'message': 'Removed from waitlist successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Helper function to process waitlist when a spot becomes available
def process_waitlist(class_id):
    # Check if class is full
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return
    
    booking_count = Booking.query.filter(
        Booking.class_id == class_id,
        Booking.status.in_(['booked', 'attended'])
    ).count()
    
    if booking_count >= class_obj.capacity:
        return  # Class is still full
    
    # Get next person on waitlist
    next_entry = WaitlistEntry.query.filter(
        WaitlistEntry.class_id == class_id,
        WaitlistEntry.status == 'waiting'
    ).order_by(WaitlistEntry.position).first()
    
    if not next_entry:
        return  # No one on waitlist
    
    # Update waitlist entry status
    next_entry.status = 'notified'
    next_entry.notification_time = datetime.utcnow()
    
    # In a real implementation, send notification to user
    # For now, we'll just update the status
    
    db.session.commit()
    
    # Reorder waitlist
    reorder_waitlist(class_id)


# Helper function to reorder waitlist positions
def reorder_waitlist(class_id):
    # Get all waiting entries
    entries = WaitlistEntry.query.filter(
        WaitlistEntry.class_id == class_id,
        WaitlistEntry.status == 'waiting'
    ).order_by(WaitlistEntry.join_time).all()
    
    # Update positions
    for i, entry in enumerate(entries):
        entry.position = i + 1
    
    db.session.commit()
