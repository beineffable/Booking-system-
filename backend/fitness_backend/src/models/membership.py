from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from src.models.user import db

class MembershipType(db.Model):
    __tablename__ = 'membership_types'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # Duration in days
    class_credits = db.Column(db.Integer, nullable=True)  # Number of classes included, null for unlimited
    features = db.Column(db.JSON, nullable=True)  # JSON array of features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', back_populates='membership_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<MembershipType {self.name}>'


class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    membership_type_id = db.Column(db.String(36), db.ForeignKey('membership_types.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, paused, expired, cancelled
    remaining_credits = db.Column(db.Integer, nullable=True)  # Remaining class credits
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='memberships')
    membership_type = db.relationship('MembershipType', back_populates='memberships')
    payments = db.relationship('Payment', back_populates='membership', lazy='dynamic')
    
    def __repr__(self):
        return f'<Membership {self.id} - {self.status}>'


class MembershipPause(db.Model):
    __tablename__ = 'membership_pauses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    membership_id = db.Column(db.String(36), db.ForeignKey('memberships.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)  # Null if indefinite pause
    reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    membership = db.relationship('Membership')
    
    def __repr__(self):
        return f'<MembershipPause {self.id}>'


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    membership_id = db.Column(db.String(36), db.ForeignKey('memberships.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='CHF')
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, twint, cash, etc.
    payment_status = db.Column(db.String(20), nullable=False)  # pending, completed, failed, refunded
    transaction_id = db.Column(db.String(255), nullable=True)  # External payment provider ID
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    membership = db.relationship('Membership', back_populates='payments')
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency}>'
