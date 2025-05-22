from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='member')  # member, trainer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    memberships = db.relationship('Membership', back_populates='user', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='user', lazy='dynamic')
    achievements = db.relationship('UserAchievement', back_populates='user', lazy='dynamic')
    activities = db.relationship('UserActivity', back_populates='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'


class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('RolePermission', back_populates='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    scope = db.Column(db.String(20), nullable=False, default='all')  # own, assigned, department, all
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    role_permissions = db.relationship('RolePermission', back_populates='permission', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('module', 'action', 'scope', name='unique_permission'),
    )
    
    def __repr__(self):
        return f'<Permission {self.module}:{self.action}:{self.scope}>'


class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = db.Column(db.String(36), db.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    role = db.relationship('Role', back_populates='permissions')
    permission = db.relationship('Permission', back_populates='role_permissions')
    
    __table_args__ = (
        db.UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),
    )
    
    def __repr__(self):
        return f'<RolePermission {self.role_id}:{self.permission_id}>'


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    role = db.relationship('Role')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )
    
    def __repr__(self):
        return f'<UserRole {self.user_id}:{self.role_id}>'
