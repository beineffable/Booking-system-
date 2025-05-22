from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.class import Booking, Class
from src.models.membership import Membership
from src.routes.auth_middleware import token_required, role_required
from datetime import datetime, timedelta
import uuid

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboards', methods=['GET'])
@token_required
def get_leaderboards(user_id, user_role):
    """Get available leaderboard types"""
    leaderboards = [
        {
            'id': 'attendance',
            'name': 'Class Attendance',
            'description': 'Members with the most classes attended'
        },
        {
            'id': 'streak',
            'name': 'Attendance Streak',
            'description': 'Members with the longest active attendance streaks'
        },
        {
            'id': 'consistency',
            'name': 'Consistency',
            'description': 'Members with the most consistent weekly attendance'
        },
        {
            'id': 'early_bird',
            'name': 'Early Bird',
            'description': 'Members who attend the most morning classes'
        },
        {
            'id': 'night_owl',
            'name': 'Night Owl',
            'description': 'Members who attend the most evening classes'
        },
        {
            'id': 'class_variety',
            'name': 'Class Variety',
            'description': 'Members who attend the most different class types'
        }
    ]
    
    return jsonify({'leaderboards': leaderboards})

@leaderboard_bp.route('/leaderboards/<leaderboard_id>', methods=['GET'])
@token_required
def get_leaderboard(leaderboard_id, user_id, user_role):
    """Get a specific leaderboard"""
    # Get time range
    time_range = request.args.get('time_range', 'month')
    
    if time_range == 'week':
        start_date = datetime.utcnow() - timedelta(days=7)
    elif time_range == 'month':
        start_date = datetime.utcnow() - timedelta(days=30)
    elif time_range == 'year':
        start_date = datetime.utcnow() - timedelta(days=365)
    elif time_range == 'all_time':
        start_date = datetime(2000, 1, 1)  # Effectively all time
    else:
        return jsonify({'error': 'Invalid time_range. Must be week, month, year, or all_time'}), 400
    
    # Get limit
    limit = request.args.get('limit', 10, type=int)
    
    # Process based on leaderboard type
    if leaderboard_id == 'attendance':
        return get_attendance_leaderboard(start_date, limit, user_id)
    elif leaderboard_id == 'streak':
        return get_streak_leaderboard(user_id)
    elif leaderboard_id == 'consistency':
        return get_consistency_leaderboard(start_date, limit, user_id)
    elif leaderboard_id == 'early_bird':
        return get_early_bird_leaderboard(start_date, limit, user_id)
    elif leaderboard_id == 'night_owl':
        return get_night_owl_leaderboard(start_date, limit, user_id)
    elif leaderboard_id == 'class_variety':
        return get_class_variety_leaderboard(start_date, limit, user_id)
    else:
        return jsonify({'error': 'Invalid leaderboard ID'}), 404

def get_attendance_leaderboard(start_date, limit, current_user_id):
    """Get attendance leaderboard"""
    # Query for attendance counts
    attendance_counts = db.session.query(
        Booking.user_id,
        db.func.count(Booking.id).label('attendance_count')
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date
     ) \
     .group_by(Booking.user_id) \
     .order_by(db.desc('attendance_count')) \
     .limit(limit) \
     .all()
    
    # Format results
    leaderboard = []
    user_rank = None
    current_user_count = 0
    
    for rank, (user_id, count) in enumerate(attendance_counts, 1):
        user = User.query.get(user_id)
        if not user:
            continue
        
        entry = {
            'rank': rank,
            'user_id': user_id,
            'name': f"{user.first_name} {user.last_name}",
            'profile_image': user.profile_image,
            'score': count,
            'is_current_user': user_id == current_user_id
        }
        leaderboard.append(entry)
        
        if user_id == current_user_id:
            user_rank = rank
            current_user_count = count
    
    # If current user is not in the top results, get their rank
    if user_rank is None:
        # Get count for current user
        current_user_booking = db.session.query(
            db.func.count(Booking.id).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.user_id == current_user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date
         ) \
         .scalar() or 0
        
        # Get number of users with more attendances
        higher_ranks = db.session.query(
            db.func.count(db.distinct(Booking.user_id)).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.status == 'attended',
            Class.start_time >= start_date
         ) \
         .group_by(Booking.user_id) \
         .having(db.func.count(Booking.id) > current_user_booking) \
         .scalar() or 0
        
        user_rank = higher_ranks + 1
        current_user_count = current_user_booking
    
    # Get total participants
    total_participants = db.session.query(
        db.func.count(db.distinct(Booking.user_id))
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date
     ) \
     .scalar() or 0
    
    return jsonify({
        'leaderboard': leaderboard,
        'user_rank': user_rank,
        'user_score': current_user_count,
        'total_participants': total_participants
    })

def get_streak_leaderboard(current_user_id):
    """Get streak leaderboard"""
    # This is a complex calculation that would typically be done with a more sophisticated algorithm
    # For this example, we'll use a simplified approach
    
    # Get all users
    users = User.query.filter(User.role == 'member').all()
    
    # Calculate streaks for each user
    streaks = []
    
    for user in users:
        # Get all attended bookings ordered by date
        bookings = db.session.query(Class.start_time) \
            .join(Booking, Class.id == Booking.class_id) \
            .filter(
                Booking.user_id == user.id,
                Booking.status == 'attended'
            ) \
            .order_by(Class.start_time) \
            .all()
        
        # Calculate streak
        current_streak = 0
        max_streak = 0
        last_date = None
        
        for booking in bookings:
            class_date = booking.start_time.date()
            
            if last_date is None:
                current_streak = 1
            elif (class_date - last_date).days <= 7:  # Consider classes within 7 days as maintaining streak
                current_streak += 1
            else:
                current_streak = 1
            
            max_streak = max(max_streak, current_streak)
            last_date = class_date
        
        # Check if streak is still active (attended class in last 7 days)
        is_active = False
        if last_date and (datetime.utcnow().date() - last_date).days <= 7:
            is_active = True
        
        if max_streak > 0:
            streaks.append({
                'user_id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'profile_image': user.profile_image,
                'streak': max_streak,
                'is_active': is_active,
                'is_current_user': user.id == current_user_id
            })
    
    # Sort by streak (descending) and then by active status
    streaks.sort(key=lambda x: (x['streak'], x['is_active']), reverse=True)
    
    # Add ranks
    for i, entry in enumerate(streaks, 1):
        entry['rank'] = i
    
    # Get current user's rank and streak
    user_rank = None
    user_streak = 0
    
    for entry in streaks:
        if entry['user_id'] == current_user_id:
            user_rank = entry['rank']
            user_streak = entry['streak']
            break
    
    # If user not found, they have no streak
    if user_rank is None:
        user_rank = len(streaks) + 1
    
    # Limit to top 10
    top_streaks = streaks[:10]
    
    return jsonify({
        'leaderboard': top_streaks,
        'user_rank': user_rank,
        'user_score': user_streak,
        'total_participants': len(streaks)
    })

def get_consistency_leaderboard(start_date, limit, current_user_id):
    """Get consistency leaderboard"""
    # This would typically involve calculating the standard deviation of attendance
    # For this example, we'll use a simplified approach based on weekly attendance
    
    # Get all users
    users = User.query.filter(User.role == 'member').all()
    
    # Calculate consistency scores
    consistency_scores = []
    
    for user in users:
        # Get all weeks since start_date
        weeks = []
        current_date = start_date
        while current_date < datetime.utcnow():
            week_end = current_date + timedelta(days=7)
            weeks.append((current_date, week_end))
            current_date = week_end
        
        # Count attendances per week
        weekly_counts = []
        
        for week_start, week_end in weeks:
            count = db.session.query(db.func.count(Booking.id)) \
                .join(Class, Booking.class_id == Class.id) \
                .filter(
                    Booking.user_id == user.id,
                    Booking.status == 'attended',
                    Class.start_time >= week_start,
                    Class.start_time < week_end
                ) \
                .scalar() or 0
            
            weekly_counts.append(count)
        
        # Skip users with no attendance
        if sum(weekly_counts) == 0:
            continue
        
        # Calculate consistency score (simplified)
        # Higher score means more consistent attendance
        non_zero_weeks = sum(1 for count in weekly_counts if count > 0)
        total_weeks = len(weeks)
        
        if total_weeks == 0:
            consistency = 0
        else:
            consistency = (non_zero_weeks / total_weeks) * 100
        
        consistency_scores.append({
            'user_id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'profile_image': user.profile_image,
            'score': round(consistency, 1),
            'is_current_user': user.id == current_user_id
        })
    
    # Sort by consistency score
    consistency_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Add ranks
    for i, entry in enumerate(consistency_scores, 1):
        entry['rank'] = i
    
    # Get current user's rank and score
    user_rank = None
    user_score = 0
    
    for entry in consistency_scores:
        if entry['user_id'] == current_user_id:
            user_rank = entry['rank']
            user_score = entry['score']
            break
    
    # If user not found, they have no consistency score
    if user_rank is None:
        user_rank = len(consistency_scores) + 1
    
    # Limit to requested number
    top_scores = consistency_scores[:limit]
    
    return jsonify({
        'leaderboard': top_scores,
        'user_rank': user_rank,
        'user_score': user_score,
        'total_participants': len(consistency_scores)
    })

def get_early_bird_leaderboard(start_date, limit, current_user_id):
    """Get early bird leaderboard (morning classes)"""
    # Define morning hours (before noon)
    morning_start = 5  # 5 AM
    morning_end = 12  # 12 PM
    
    # Query for morning class attendance counts
    morning_counts = db.session.query(
        Booking.user_id,
        db.func.count(Booking.id).label('morning_count')
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date,
        db.func.extract('hour', Class.start_time) >= morning_start,
        db.func.extract('hour', Class.start_time) < morning_end
     ) \
     .group_by(Booking.user_id) \
     .order_by(db.desc('morning_count')) \
     .limit(limit) \
     .all()
    
    # Format results
    leaderboard = []
    user_rank = None
    current_user_count = 0
    
    for rank, (user_id, count) in enumerate(morning_counts, 1):
        user = User.query.get(user_id)
        if not user:
            continue
        
        entry = {
            'rank': rank,
            'user_id': user_id,
            'name': f"{user.first_name} {user.last_name}",
            'profile_image': user.profile_image,
            'score': count,
            'is_current_user': user_id == current_user_id
        }
        leaderboard.append(entry)
        
        if user_id == current_user_id:
            user_rank = rank
            current_user_count = count
    
    # If current user is not in the top results, get their rank
    if user_rank is None:
        # Get count for current user
        current_user_morning = db.session.query(
            db.func.count(Booking.id).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.user_id == current_user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= morning_start,
            db.func.extract('hour', Class.start_time) < morning_end
         ) \
         .scalar() or 0
        
        # Get number of users with more morning attendances
        higher_ranks = db.session.query(
            db.func.count(db.distinct(Booking.user_id)).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= morning_start,
            db.func.extract('hour', Class.start_time) < morning_end
         ) \
         .group_by(Booking.user_id) \
         .having(db.func.count(Booking.id) > current_user_morning) \
         .scalar() or 0
        
        user_rank = higher_ranks + 1
        current_user_count = current_user_morning
    
    # Get total participants
    total_participants = db.session.query(
        db.func.count(db.distinct(Booking.user_id))
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date,
        db.func.extract('hour', Class.start_time) >= morning_start,
        db.func.extract('hour', Class.start_time) < morning_end
     ) \
     .scalar() or 0
    
    return jsonify({
        'leaderboard': leaderboard,
        'user_rank': user_rank,
        'user_score': current_user_count,
        'total_participants': total_participants
    })

def get_night_owl_leaderboard(start_date, limit, current_user_id):
    """Get night owl leaderboard (evening classes)"""
    # Define evening hours
    evening_start = 17  # 5 PM
    evening_end = 23  # 11 PM
    
    # Query for evening class attendance counts
    evening_counts = db.session.query(
        Booking.user_id,
        db.func.count(Booking.id).label('evening_count')
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date,
        db.func.extract('hour', Class.start_time) >= evening_start,
        db.func.extract('hour', Class.start_time) < evening_end
     ) \
     .group_by(Booking.user_id) \
     .order_by(db.desc('evening_count')) \
     .limit(limit) \
     .all()
    
    # Format results
    leaderboard = []
    user_rank = None
    current_user_count = 0
    
    for rank, (user_id, count) in enumerate(evening_counts, 1):
        user = User.query.get(user_id)
        if not user:
            continue
        
        entry = {
            'rank': rank,
            'user_id': user_id,
            'name': f"{user.first_name} {user.last_name}",
            'profile_image': user.profile_image,
            'score': count,
            'is_current_user': user_id == current_user_id
        }
        leaderboard.append(entry)
        
        if user_id == current_user_id:
            user_rank = rank
            current_user_count = count
    
    # If current user is not in the top results, get their rank
    if user_rank is None:
        # Get count for current user
        current_user_evening = db.session.query(
            db.func.count(Booking.id).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.user_id == current_user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= evening_start,
            db.func.extract('hour', Class.start_time) < evening_end
         ) \
         .scalar() or 0
        
        # Get number of users with more evening attendances
        higher_ranks = db.session.query(
            db.func.count(db.distinct(Booking.user_id)).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= evening_start,
            db.func.extract('hour', Class.start_time) < evening_end
         ) \
         .group_by(Booking.user_id) \
         .having(db.func.count(Booking.id) > current_user_evening) \
         .scalar() or 0
        
        user_rank = higher_ranks + 1
        current_user_count = current_user_evening
    
    # Get total participants
    total_participants = db.session.query(
        db.func.count(db.distinct(Booking.user_id))
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date,
        db.func.extract('hour', Class.start_time) >= evening_start,
        db.func.extract('hour', Class.start_time) < evening_end
     ) \
     .scalar() or 0
    
    return jsonify({
        'leaderboard': leaderboard,
        'user_rank': user_rank,
        'user_score': current_user_count,
        'total_participants': total_participants
    })

def get_class_variety_leaderboard(start_date, limit, current_user_id):
    """Get class variety leaderboard (different class types attended)"""
    # Query for class type variety
    variety_counts = db.session.query(
        Booking.user_id,
        db.func.count(db.distinct(Class.class_type_id)).label('variety_count')
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date
     ) \
     .group_by(Booking.user_id) \
     .order_by(db.desc('variety_count')) \
     .limit(limit) \
     .all()
    
    # Format results
    leaderboard = []
    user_rank = None
    current_user_count = 0
    
    for rank, (user_id, count) in enumerate(variety_counts, 1):
        user = User.query.get(user_id)
        if not user:
            continue
        
        entry = {
            'rank': rank,
            'user_id': user_id,
            'name': f"{user.first_name} {user.last_name}",
            'profile_image': user.profile_image,
            'score': count,
            'is_current_user': user_id == current_user_id
        }
        leaderboard.append(entry)
        
        if user_id == current_user_id:
            user_rank = rank
            current_user_count = count
    
    # If current user is not in the top results, get their rank
    if user_rank is None:
        # Get count for current user
        current_user_variety = db.session.query(
            db.func.count(db.distinct(Class.class_type_id)).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.user_id == current_user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date
         ) \
         .scalar() or 0
        
        # Get number of users with more variety
        higher_ranks = db.session.query(
            db.func.count(db.distinct(Booking.user_id)).label('count')
        ).join(Class, Booking.class_id == Class.id) \
         .filter(
            Booking.status == 'attended',
            Class.start_time >= start_date
         ) \
         .group_by(Booking.user_id) \
         .having(db.func.count(db.distinct(Class.class_type_id)) > current_user_variety) \
         .scalar() or 0
        
        user_rank = higher_ranks + 1
        current_user_count = current_user_variety
    
    # Get total participants
    total_participants = db.session.query(
        db.func.count(db.distinct(Booking.user_id))
    ).join(Class, Booking.class_id == Class.id) \
     .filter(
        Booking.status == 'attended',
        Class.start_time >= start_date
     ) \
     .scalar() or 0
    
    return jsonify({
        'leaderboard': leaderboard,
        'user_rank': user_rank,
        'user_score': current_user_count,
        'total_participants': total_participants
    })

@leaderboard_bp.route('/user-stats', methods=['GET'])
@token_required
def get_user_stats(user_id, user_role):
    """Get statistics for the current user"""
    # Get time range
    time_range = request.args.get('time_range', 'month')
    
    if time_range == 'week':
        start_date = datetime.utcnow() - timedelta(days=7)
    elif time_range == 'month':
        start_date = datetime.utcnow() - timedelta(days=30)
    elif time_range == 'year':
        start_date = datetime.utcnow() - timedelta(days=365)
    elif time_range == 'all_time':
        start_date = datetime(2000, 1, 1)  # Effectively all time
    else:
        return jsonify({'error': 'Invalid time_range. Must be week, month, year, or all_time'}), 400
    
    # Get total classes attended
    total_attended = db.session.query(db.func.count(Booking.id)) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date
        ) \
        .scalar() or 0
    
    # Get total classes booked
    total_booked = db.session.query(db.func.count(Booking.id)) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(
            Booking.user_id == user_id,
            Class.start_time >= start_date
        ) \
        .scalar() or 0
    
    # Get attendance rate
    attendance_rate = (total_attended / total_booked) * 100 if total_booked > 0 else 0
    
    # Get favorite class type
    favorite_class_type = db.session.query(
        Class.class_type_id,
        db.func.count(Booking.id).label('type_count')
    ).join(Booking, Class.id == Booking.class_id) \
     .filter(
        Booking.user_id == user_id,
        Booking.status == 'attended',
        Class.start_time >= start_date
     ) \
     .group_by(Class.class_type_id) \
     .order_by(db.desc('type_count')) \
     .first()
    
    favorite_type_name = None
    if favorite_class_type:
        from src.models.class import ClassType
        class_type = ClassType.query.get(favorite_class_type[0])
        if class_type:
            favorite_type_name = class_type.name
    
    # Get favorite time of day
    morning_count = db.session.query(db.func.count(Booking.id)) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= 5,
            db.func.extract('hour', Class.start_time) < 12
        ) \
        .scalar() or 0
    
    afternoon_count = db.session.query(db.func.count(Booking.id)) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= 12,
            db.func.extract('hour', Class.start_time) < 17
        ) \
        .scalar() or 0
    
    evening_count = db.session.query(db.func.count(Booking.id)) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended',
            Class.start_time >= start_date,
            db.func.extract('hour', Class.start_time) >= 17,
            db.func.extract('hour', Class.start_time) < 23
        ) \
        .scalar() or 0
    
    favorite_time = 'Morning'
    if afternoon_count > morning_count and afternoon_count > evening_count:
        favorite_time = 'Afternoon'
    elif evening_count > morning_count and evening_count > afternoon_count:
        favorite_time = 'Evening'
    
    # Get current streak
    bookings = db.session.query(Class.start_time) \
        .join(Booking, Class.id == Booking.class_id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended'
        ) \
        .order_by(Class.start_time) \
        .all()
    
    current_streak = 0
    last_date = None
    
    for booking in bookings:
        class_date = booking.start_time.date()
        
        if last_date is None:
            current_streak = 1
        elif (class_date - last_date).days <= 7:  # Consider classes within 7 days as maintaining streak
            current_streak += 1
        else:
            current_streak = 1
        
        last_date = class_date
    
    # Check if streak is still active (attended class in last 7 days)
    is_active_streak = False
    if last_date and (datetime.utcnow().date() - last_date).days <= 7:
        is_active_streak = True
    else:
        current_streak = 0
    
    # Get membership status
    active_membership = Membership.query.filter(
        Membership.user_id == user_id,
        Membership.status == 'active',
        Membership.end_date >= datetime.utcnow()
    ).first()
    
    membership_info = None
    if active_membership:
        from src.models.membership import MembershipType
        membership_type = MembershipType.query.get(active_membership.membership_type_id)
        if membership_type:
            membership_info = {
                'type': membership_type.name,
                'start_date': active_membership.start_date.isoformat(),
                'end_date': active_membership.end_date.isoformat(),
                'remaining_credits': active_membership.remaining_credits,
                'days_remaining': (active_membership.end_date - datetime.utcnow()).days
            }
    
    # Format response
    stats = {
        'total_classes_attended': total_attended,
        'total_classes_booked': total_booked,
        'attendance_rate': round(attendance_rate, 1),
        'favorite_class_type': favorite_type_name,
        'favorite_time': favorite_time,
        'current_streak': current_streak,
        'is_active_streak': is_active_streak,
        'time_distribution': {
            'morning': morning_count,
            'afternoon': afternoon_count,
            'evening': evening_count
        },
        'membership': membership_info
    }
    
    return jsonify({'stats': stats})

@leaderboard_bp.route('/analytics', methods=['GET'])
@role_required(['admin', 'trainer'])
def get_analytics(user_id, user_role):
    """Get analytics data for admins and trainers"""
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
    
    # Get class attendance data
    class_attendance = db.session.query(
        Class.class_type_id,
        db.func.count(Booking.id).label('booking_count')
    ).join(Booking, Class.id == Booking.class_id) \
     .filter(
        Booking.status.in_(['booked', 'attended']),
        Class.start_time >= start_date
     ) \
     .group_by(Class.class_type_id) \
     .all()
    
    class_attendance_data = []
    for class_type_id, count in class_attendance:
        from src.models.class import ClassType
        class_type = ClassType.query.get(class_type_id)
        if class_type:
            class_attendance_data.append({
                'class_type': class_type.name,
                'count': count
            })
    
    # Get time of day distribution
    time_distribution = [
        {
            'time': 'Morning (5-12)',
            'count': db.session.query(db.func.count(Booking.id)) \
                .join(Class, Booking.class_id == Class.id) \
                .filter(
                    Booking.status.in_(['booked', 'attended']),
                    Class.start_time >= start_date,
                    db.func.extract('hour', Class.start_time) >= 5,
                    db.func.extract('hour', Class.start_time) < 12
                ) \
                .scalar() or 0
        },
        {
            'time': 'Afternoon (12-17)',
            'count': db.session.query(db.func.count(Booking.id)) \
                .join(Class, Booking.class_id == Class.id) \
                .filter(
                    Booking.status.in_(['booked', 'attended']),
                    Class.start_time >= start_date,
                    db.func.extract('hour', Class.start_time) >= 12,
                    db.func.extract('hour', Class.start_time) < 17
                ) \
                .scalar() or 0
        },
        {
            'time': 'Evening (17-23)',
            'count': db.session.query(db.func.count(Booking.id)) \
                .join(Class, Booking.class_id == Class.id) \
                .filter(
                    Booking.status.in_(['booked', 'attended']),
                    Class.start_time >= start_date,
                    db.func.extract('hour', Class.start_time) >= 17,
                    db.func.extract('hour', Class.start_time) < 23
                ) \
                .scalar() or 0
        }
    ]
    
    # Get day of week distribution
    day_distribution = []
    for day in range(7):
        day_count = db.session.query(db.func.count(Booking.id)) \
            .join(Class, Booking.class_id == Class.id) \
            .filter(
                Booking.status.in_(['booked', 'attended']),
                Class.start_time >= start_date,
                db.func.extract('dow', Class.start_time) == day
            ) \
            .scalar() or 0
        
        day_name = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][day]
        day_distribution.append({
            'day': day_name,
            'count': day_count
        })
    
    # Get membership distribution
    membership_distribution = db.session.query(
        Membership.membership_type_id,
        db.func.count(Membership.id).label('member_count')
    ).filter(
        Membership.status == 'active',
        Membership.end_date >= datetime.utcnow()
    ).group_by(Membership.membership_type_id).all()
    
    membership_data = []
    for membership_type_id, count in membership_distribution:
        from src.models.membership import MembershipType
        membership_type = MembershipType.query.get(membership_type_id)
        if membership_type:
            membership_data.append({
                'membership_type': membership_type.name,
                'count': count
            })
    
    # Get attendance rate
    total_bookings = db.session.query(db.func.count(Booking.id)) \
        .join(Class, Booking.class_id == Class.id) \
        .filter(
            Class.start_time >= start_date,
            Class.start_time < datetime.utcnow()
        ) \
        .scalar() or 0
    
    attended_bookings = db.session.query(db.func.count(Booking.id)) \
        .filter(
            Booking.status == 'attended',
            Booking.check_in_time >= start_date
        ) \
        .scalar() or 0
    
    no_show_bookings = db.session.query(db.func.count(Booking.id)) \
        .filter(
            Booking.status == 'no-show',
            Booking.booking_time >= start_date
        ) \
        .scalar() or 0
    
    cancelled_bookings = db.session.query(db.func.count(Booking.id)) \
        .filter(
            Booking.status == 'cancelled',
            Booking.cancellation_time >= start_date
        ) \
        .scalar() or 0
    
    attendance_rate = (attended_bookings / total_bookings) * 100 if total_bookings > 0 else 0
    no_show_rate = (no_show_bookings / total_bookings) * 100 if total_bookings > 0 else 0
    cancellation_rate = (cancelled_bookings / total_bookings) * 100 if total_bookings > 0 else 0
    
    # Get trainer popularity
    trainer_popularity = db.session.query(
        Class.trainer_id,
        db.func.count(Booking.id).label('booking_count')
    ).join(Booking, Class.id == Booking.class_id) \
     .filter(
        Booking.status.in_(['booked', 'attended']),
        Class.start_time >= start_date
     ) \
     .group_by(Class.trainer_id) \
     .order_by(db.desc('booking_count')) \
     .all()
    
    trainer_data = []
    for trainer_id, count in trainer_popularity:
        trainer = User.query.get(trainer_id)
        if trainer:
            trainer_data.append({
                'trainer_id': trainer_id,
                'trainer_name': f"{trainer.first_name} {trainer.last_name}",
                'count': count
            })
    
    # Format response
    analytics = {
        'class_attendance': class_attendance_data,
        'time_distribution': time_distribution,
        'day_distribution': day_distribution,
        'membership_distribution': membership_data,
        'attendance_stats': {
            'total_bookings': total_bookings,
            'attended': attended_bookings,
            'no_show': no_show_bookings,
            'cancelled': cancelled_bookings,
            'attendance_rate': round(attendance_rate, 1),
            'no_show_rate': round(no_show_rate, 1),
            'cancellation_rate': round(cancellation_rate, 1)
        },
        'trainer_popularity': trainer_data
    }
    
    return jsonify({'analytics': analytics})

@leaderboard_bp.route('/achievements', methods=['GET'])
@token_required
def get_user_achievements(user_id, user_role):
    """Get achievements for the current user"""
    # This would typically be stored in a database
    # For this example, we'll calculate achievements on the fly
    
    # Get total classes attended
    total_attended = db.session.query(db.func.count(Booking.id)) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended'
        ) \
        .scalar() or 0
    
    # Get class type variety
    class_variety = db.session.query(db.func.count(db.distinct(Class.class_type_id))) \
        .join(Booking, Class.id == Booking.class_id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended'
        ) \
        .scalar() or 0
    
    # Get max streak
    bookings = db.session.query(Class.start_time) \
        .join(Booking, Class.id == Booking.class_id) \
        .filter(
            Booking.user_id == user_id,
            Booking.status == 'attended'
        ) \
        .order_by(Class.start_time) \
        .all()
    
    current_streak = 0
    max_streak = 0
    last_date = None
    
    for booking in bookings:
        class_date = booking.start_time.date()
        
        if last_date is None:
            current_streak = 1
        elif (class_date - last_date).days <= 7:
            current_streak += 1
        else:
            current_streak = 1
        
        max_streak = max(max_streak, current_streak)
        last_date = class_date
    
    # Define achievements
    achievements = [
        {
            'id': 'first_class',
            'name': 'First Step',
            'description': 'Attend your first class',
            'icon': '🏆',
            'earned': total_attended >= 1,
            'progress': min(total_attended, 1),
            'target': 1
        },
        {
            'id': 'ten_classes',
            'name': 'Regular',
            'description': 'Attend 10 classes',
            'icon': '🥉',
            'earned': total_attended >= 10,
            'progress': min(total_attended, 10),
            'target': 10
        },
        {
            'id': 'fifty_classes',
            'name': 'Dedicated',
            'description': 'Attend 50 classes',
            'icon': '🥈',
            'earned': total_attended >= 50,
            'progress': min(total_attended, 50),
            'target': 50
        },
        {
            'id': 'hundred_classes',
            'name': 'Centurion',
            'description': 'Attend 100 classes',
            'icon': '🥇',
            'earned': total_attended >= 100,
            'progress': min(total_attended, 100),
            'target': 100
        },
        {
            'id': 'explorer',
            'name': 'Explorer',
            'description': 'Try 5 different class types',
            'icon': '🧭',
            'earned': class_variety >= 5,
            'progress': min(class_variety, 5),
            'target': 5
        },
        {
            'id': 'variety_master',
            'name': 'Variety Master',
            'description': 'Try 10 different class types',
            'icon': '🌟',
            'earned': class_variety >= 10,
            'progress': min(class_variety, 10),
            'target': 10
        },
        {
            'id': 'streak_starter',
            'name': 'Streak Starter',
            'description': 'Maintain a 3-class streak',
            'icon': '🔥',
            'earned': max_streak >= 3,
            'progress': min(max_streak, 3),
            'target': 3
        },
        {
            'id': 'streak_master',
            'name': 'Streak Master',
            'description': 'Maintain a 10-class streak',
            'icon': '🔥🔥',
            'earned': max_streak >= 10,
            'progress': min(max_streak, 10),
            'target': 10
        }
    ]
    
    # Count earned achievements
    earned_count = sum(1 for a in achievements if a['earned'])
    
    return jsonify({
        'achievements': achievements,
        'earned_count': earned_count,
        'total_count': len(achievements)
    })
