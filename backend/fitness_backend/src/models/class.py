from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from src.models.user import db

class ClassType(db.Model):
    __tablename__ = 'class_types'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), nullable=True)  # Hex color code
    duration_minutes = db.Column(db.Integer, nullable=False)
    default_capacity = db.Column(db.Integer, nullable=False, default=20)
    credits_required = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', back_populates='class_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<ClassType {self.name}>'


class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_type_id = db.Column(db.String(36), db.ForeignKey('class_types.id'), nullable=False)
    trainer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_cancelled = db.Column(db.Boolean, default=False)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_type = db.relationship('ClassType', back_populates='classes')
    trainer = db.relationship('User')
    bookings = db.relationship('Booking', back_populates='class_obj', lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.id} - {self.start_time}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='booked')  # booked, cancelled, attended, no-show
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    cancellation_time = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    check_in_time = db.Column(db.DateTime, nullable=True)
    credits_used = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='bookings')
    class_obj = db.relationship('Class', back_populates='bookings')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'class_id', name='unique_user_class_booking'),
    )
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'


class WaitlistEntry(db.Model):
    __tablename__ = 'waitlist_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='waiting')  # waiting, notified, converted, removed
    notification_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    class_obj = db.relationship('Class')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'class_id', name='unique_user_class_waitlist'),
    )
    
    def __repr__(self):
        return f'<WaitlistEntry {self.id} - Position {self.position}>'
