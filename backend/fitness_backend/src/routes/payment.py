from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User
from src.models.membership import Membership, MembershipType, Payment
from src.routes.auth_middleware import token_required, role_required
from datetime import datetime, timedelta
import uuid
import stripe
import os
import json

payment_bp = Blueprint('payment', __name__)

# Initialize Stripe with the API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51OxCvDBXqHVfcDsdfghjklzxcvbnmqwertyuiop1234567890')

@payment_bp.route('/config', methods=['GET'])
def get_publishable_key():
    """Return the Stripe publishable key for frontend initialization"""
    stripe_config = {
        'publishableKey': os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_51OxCvDBXqHVfcDsdfghjklzxcvbnmqwertyuiop1234567890'),
        'country': 'CH',
        'currency': 'chf',
        'supportedPaymentMethods': ['card', 'twint']
    }
    return jsonify(stripe_config)

@payment_bp.route('/create-payment-intent', methods=['POST'])
@token_required
def create_payment_intent(user_id, user_role):
    """Create a payment intent for Stripe checkout"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'amount' not in data or 'currency' not in data:
        return jsonify({'error': 'Amount and currency are required'}), 400
    
    try:
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(data['amount'] * 100),  # Convert to cents
            currency=data['currency'].lower(),
            metadata={
                'user_id': user_id,
                'membership_id': data.get('membership_id', ''),
                'description': data.get('description', 'Fitness Platform Payment')
            },
            payment_method_types=['card'],
            # Add TWINT as a payment method if available in Switzerland
            # Note: This requires special setup with Stripe
            # payment_method_types=['card', 'eps', 'giropay', 'ideal', 'sepa_debit', 'sofort']
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'id': intent.id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # Verify webhook signature and extract the event
    # Note: In production, you should use a webhook secret
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_test')
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_failed_payment(payment_intent)
    
    return jsonify({'status': 'success'})

def handle_successful_payment(payment_intent):
    """Process a successful payment"""
    # Extract metadata
    metadata = payment_intent.get('metadata', {})
    user_id = metadata.get('user_id')
    membership_id = metadata.get('membership_id')
    description = metadata.get('description', 'Stripe Payment')
    
    if not user_id:
        return
    
    # Create payment record
    payment = Payment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        membership_id=membership_id if membership_id else None,
        amount=payment_intent['amount'] / 100,  # Convert from cents
        currency=payment_intent['currency'].upper(),
        payment_method='stripe',
        payment_status='completed',
        transaction_id=payment_intent['id'],
        payment_date=datetime.utcnow(),
        description=description
    )
    
    try:
        db.session.add(payment)
        
        # If this is for a membership, update the membership status
        if membership_id:
            membership = Membership.query.get(membership_id)
            if membership:
                membership.status = 'active'
                
                # If membership was expired, update the dates
                if membership.end_date < datetime.utcnow():
                    membership_type = MembershipType.query.get(membership.membership_type_id)
                    if membership_type:
                        membership.start_date = datetime.utcnow()
                        membership.end_date = datetime.utcnow() + timedelta(days=membership_type.duration_days)
                        membership.remaining_credits = membership_type.class_credits
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error processing payment: {str(e)}")

def handle_failed_payment(payment_intent):
    """Process a failed payment"""
    # Extract metadata
    metadata = payment_intent.get('metadata', {})
    user_id = metadata.get('user_id')
    membership_id = metadata.get('membership_id')
    description = metadata.get('description', 'Stripe Payment')
    
    if not user_id:
        return
    
    # Create payment record for the failed payment
    payment = Payment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        membership_id=membership_id if membership_id else None,
        amount=payment_intent['amount'] / 100,  # Convert from cents
        currency=payment_intent['currency'].upper(),
        payment_method='stripe',
        payment_status='failed',
        transaction_id=payment_intent['id'],
        payment_date=datetime.utcnow(),
        description=f"Failed: {description}"
    )
    
    try:
        db.session.add(payment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error recording failed payment: {str(e)}")

@payment_bp.route('/twint-redirect', methods=['GET'])
def twint_redirect():
    """Handle TWINT payment redirect"""
    # This is a placeholder for TWINT integration
    # In a real implementation, you would handle the redirect from TWINT
    # and verify the payment status
    return jsonify({'message': 'TWINT redirect endpoint'})

@payment_bp.route('/create-twint-payment', methods=['POST'])
@token_required
def create_twint_payment(user_id, user_role):
    """Create a TWINT payment request"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    # This is a placeholder for TWINT integration
    # In a real implementation, you would create a TWINT payment request
    # and return the necessary information for the frontend to redirect
    # the user to the TWINT payment page or open the TWINT app
    
    # For now, we'll simulate a successful TWINT payment
    payment = Payment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        membership_id=data.get('membership_id'),
        amount=data['amount'],
        currency='CHF',
        payment_method='twint',
        payment_status='completed',
        transaction_id=f"twint_{uuid.uuid4()}",
        payment_date=datetime.utcnow(),
        description=data.get('description', 'TWINT Payment')
    )
    
    try:
        db.session.add(payment)
        
        # If this is for a membership, update the membership status
        if data.get('membership_id'):
            membership = Membership.query.get(data['membership_id'])
            if membership:
                membership.status = 'active'
                
                # If membership was expired, update the dates
                if membership.end_date < datetime.utcnow():
                    membership_type = MembershipType.query.get(membership.membership_type_id)
                    if membership_type:
                        membership.start_date = datetime.utcnow()
                        membership.end_date = datetime.utcnow() + timedelta(days=membership_type.duration_days)
                        membership.remaining_credits = membership_type.class_credits
        
        db.session.commit()
        
        return jsonify({
            'message': 'TWINT payment successful',
            'payment_id': payment.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payment-methods', methods=['GET'])
@token_required
def get_payment_methods(user_id, user_role):
    """Get saved payment methods for a user"""
    # In a real implementation, you would retrieve the user's saved payment methods
    # from Stripe or your database
    
    # For now, we'll return a placeholder response
    return jsonify({
        'payment_methods': [
            {
                'id': 'pm_card_visa',
                'type': 'card',
                'card': {
                    'brand': 'visa',
                    'last4': '4242',
                    'exp_month': 12,
                    'exp_year': 2025
                }
            }
        ]
    })

@payment_bp.route('/payment-history', methods=['GET'])
@token_required
def get_payment_history(user_id, user_role):
    """Get payment history for a user"""
    # Get payments for the user
    payments = Payment.query.filter(Payment.user_id == user_id).order_by(Payment.payment_date.desc()).all()
    
    # Format response
    result = []
    for payment in payments:
        result.append({
            'id': payment.id,
            'amount': payment.amount,
            'currency': payment.currency,
            'payment_method': payment.payment_method,
            'payment_status': payment.payment_status,
            'transaction_id': payment.transaction_id,
            'payment_date': payment.payment_date.isoformat(),
            'description': payment.description
        })
    
    return jsonify({'payments': result})

@payment_bp.route('/memberships/<membership_id>/renew', methods=['POST'])
@token_required
def renew_membership(membership_id, user_id, user_role):
    """Renew a membership"""
    # Get membership
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    # Check if membership belongs to user or user is admin
    if membership.user_id != user_id and user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get membership type
    membership_type = MembershipType.query.get(membership.membership_type_id)
    if not membership_type:
        return jsonify({'error': 'Membership type not found'}), 404
    
    # Get payment method
    data = request.get_json() or {}
    payment_method = data.get('payment_method', 'stripe')
    
    if payment_method == 'stripe':
        # Create a payment intent for Stripe
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(membership_type.price * 100),  # Convert to cents
                currency='chf',
                metadata={
                    'user_id': user_id,
                    'membership_id': membership_id,
                    'description': f"Renewal of {membership_type.name} membership"
                },
                payment_method_types=['card']
            )
            
            return jsonify({
                'clientSecret': intent.client_secret,
                'id': intent.id,
                'amount': membership_type.price,
                'currency': 'CHF'
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    elif payment_method == 'twint':
        # For TWINT, we'll simulate a successful payment for now
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            membership_id=membership_id,
            amount=membership_type.price,
            currency='CHF',
            payment_method='twint',
            payment_status='completed',
            transaction_id=f"twint_{uuid.uuid4()}",
            payment_date=datetime.utcnow(),
            description=f"Renewal of {membership_type.name} membership"
        )
        
        try:
            db.session.add(payment)
            
            # Update membership
            membership.status = 'active'
            
            # Calculate new dates
            if membership.end_date < datetime.utcnow():
                # If expired, start from now
                membership.start_date = datetime.utcnow()
            else:
                # If not expired, extend from end date
                membership.start_date = membership.end_date
            
            membership.end_date = membership.start_date + timedelta(days=membership_type.duration_days)
            membership.remaining_credits = membership_type.class_credits
            
            db.session.commit()
            
            return jsonify({
                'message': 'Membership renewed successfully',
                'payment_id': payment.id,
                'membership': {
                    'id': membership.id,
                    'start_date': membership.start_date.isoformat(),
                    'end_date': membership.end_date.isoformat(),
                    'status': membership.status,
                    'remaining_credits': membership.remaining_credits
                }
            }), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    else:
        return jsonify({'error': 'Invalid payment method'}), 400

@payment_bp.route('/memberships/<membership_id>/cancel-auto-renew', methods=['POST'])
@token_required
def cancel_auto_renew(membership_id, user_id, user_role):
    """Cancel auto-renewal for a membership"""
    # Get membership
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    # Check if membership belongs to user or user is admin
    if membership.user_id != user_id and user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update membership
    membership.auto_renew = False
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Auto-renewal cancelled successfully',
            'membership': {
                'id': membership.id,
                'auto_renew': membership.auto_renew
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/memberships/<membership_id>/enable-auto-renew', methods=['POST'])
@token_required
def enable_auto_renew(membership_id, user_id, user_role):
    """Enable auto-renewal for a membership"""
    # Get membership
    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({'error': 'Membership not found'}), 404
    
    # Check if membership belongs to user or user is admin
    if membership.user_id != user_id and user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update membership
    membership.auto_renew = True
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Auto-renewal enabled successfully',
            'membership': {
                'id': membership.id,
                'auto_renew': membership.auto_renew
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
