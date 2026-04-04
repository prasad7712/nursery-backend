"""Payment core business logic for Razorpay integration"""
from typing import Dict, Any
from datetime import datetime
import os
import razorpay

from src.plugins.database import db


class PaymentCore:
    """Payment core with Razorpay API and database operations"""
    
    def __init__(self):
        self.razorpay_key_id = os.getenv("RAZORPAY_KEY_ID", "placeholder_key_id")
        self.razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET", "placeholder_key_secret")
        self.razorpay_client = razorpay.Client(
            auth=(self.razorpay_key_id, self.razorpay_key_secret)
        )
        # Demo mode for college project - set DEMO_MODE=true in .env to skip actual payment verification
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        if self.demo_mode:
            print("[DEMO MODE ENABLED] All payments will be auto-approved for testing")
    
    async def create_payment_order(
        self,
        order_id: str,
        user_id: str,
        amount: float,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order and Payment record in database.
        
        Args:
            order_id: Order ID from database
            user_id: User ID
            amount: Amount in rupees
            currency: Currency code
        
        Returns:
            Payment order details with Razorpay order ID
        """
        try:
            # Create Razorpay order
            razorpay_order = self.razorpay_client.order.create({
                'amount': int(amount * 100),  # Convert to paise
                'currency': currency,
                'receipt': f"order_{order_id}",
                'notes': {
                    'order_id': order_id,
                    'user_id': user_id
                }
            })
            
            # Create Payment record in database (async)
            payment = await db.client.payment.create(
                data={
                    'orderId': order_id,
                    'userId': user_id,
                    'razorpayOrderId': razorpay_order['id'],
                    'amount': amount,
                    'currency': currency,
                    'status': 'PENDING'
                }
            )
            
            return {
                'id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'status': razorpay_order['status'],
                'key_id': self.razorpay_key_id,
                'demo_mode': self.demo_mode
            }
        except Exception as e:
            raise Exception(f"Error in create_payment_order: {str(e)}")
    
    async def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify Razorpay payment signature (or mock in demo mode).
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
        
        Returns:
            Verification result with status
        """
        try:
            # First, find the payment by razorpayOrderId
            existing_payment = await db.client.payment.find_first(
                where={'razorpayOrderId': order_id}
            )
            
            if not existing_payment:
                raise Exception(f"Payment not found for order: {order_id}")
            
            # === DEMO MODE: Auto-approve all payments ===
            if self.demo_mode:
                print(f"[DEMO MODE] Auto-approving payment: {order_id}")
                payment = await db.client.payment.update(
                    where={'id': existing_payment.id},
                    data={
                        'razorpayPaymentId': payment_id,
                        'razorpaySignature': signature,
                        'status': 'SUCCESSFUL'
                    }
                )
                
                await db.client.order.update(
                    where={'id': payment.orderId},
                    data={'paymentStatus': 'SUCCESSFUL'}
                )
                
                return {
                    'verified': True,
                    'order_id': order_id,
                    'payment_id': payment_id,
                    'status': 'successful',
                    'demo_mode': True
                }
            
            # === NORMAL MODE: Verify signature with Razorpay ===
            is_valid = self.razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            
            if is_valid:
                # Fetch payment details from Razorpay
                payment_details = self.razorpay_client.payment.fetch(payment_id)
                
                # Update Payment record in database using the found payment's id
                payment = await db.client.payment.update(
                    where={'id': existing_payment.id},
                    data={
                        'razorpayPaymentId': payment_id,
                        'razorpaySignature': signature,
                        'status': 'SUCCESSFUL'
                    }
                )
                
                # Update Order status (async)
                order = await db.client.order.update(
                    where={'id': payment.orderId},
                    data={'paymentStatus': 'SUCCESSFUL'}
                )
                
                return {
                    'verified': True,
                    'order_id': order_id,
                    'payment_id': payment_id,
                    'status': 'successful'
                }
            else:
                # Mark payment as failed in database (async)
                payment = await db.client.payment.update(
                    where={'id': existing_payment.id},
                    data={
                        'razorpayPaymentId': payment_id,
                        'status': 'FAILED',
                        'errorMessage': 'Signature verification failed'
                    }
                )
                
                order = await db.client.order.update(
                    where={'id': payment.orderId},
                    data={'paymentStatus': 'FAILED'}
                )
                
                return {
                    'verified': False,
                    'order_id': order_id,
                    'payment_id': payment_id,
                    'status': 'failed'
                }
        except Exception as e:
            raise Exception(f"Error in verify_payment: {str(e)}")
    
    async def handle_payment_authorized(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.authorized webhook event"""
        try:
            # Demo mode: skip webhook processing
            if self.demo_mode:
                print("[DEMO MODE] Webhook event skipped in demo mode")
                return {'status': 'success', 'message': 'Demo mode: webhook skipped', 'demo': True}
            
            payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')
            
            # Find payment by razorpayOrderId first
            existing_payment = await db.client.payment.find_first(
                where={'razorpayOrderId': order_id}
            )
            
            if not existing_payment:
                return {'status': 'error', 'message': f'Payment not found for order: {order_id}'}
            
            payment = await db.client.payment.update(
                where={'id': existing_payment.id},
                data={
                    'razorpayPaymentId': payment_id,
                    'status': 'SUCCESSFUL'
                }
            )
            
            # Update Order status (async)
            await db.client.order.update(
                where={'id': payment.orderId},
                data={'paymentStatus': 'SUCCESSFUL'}
            )
            
            return {
                'status': 'success',
                'message': 'Payment authorized',
                'order_id': order_id
            }
        except Exception as e:
            raise Exception(f"Error handling payment authorized: {str(e)}")
    
    async def handle_payment_failed(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.failed webhook event"""
        try:
            # Demo mode: skip webhook processing
            if self.demo_mode:
                print("[DEMO MODE] Webhook event skipped in demo mode")
                return {'status': 'success', 'message': 'Demo mode: webhook skipped', 'demo': True}
            
            payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            error_message = payment_data.get('error_description', 'Payment failed')
            
            # Find payment by razorpayOrderId first
            existing_payment = await db.client.payment.find_first(
                where={'razorpayOrderId': order_id}
            )
            
            if not existing_payment:
                return {'status': 'error', 'message': f'Payment not found for order: {order_id}'}
            
            payment = await db.client.payment.update(
                where={'id': existing_payment.id},
                data={
                    'status': 'FAILED',
                    'errorMessage': error_message
                }
            )
            
            # Update Order status (async)
            await db.client.order.update(
                where={'id': payment.orderId},
                data={'paymentStatus': 'FAILED'}
            )
            
            return {
                'status': 'success',
                'message': 'Payment failure recorded',
                'order_id': order_id
            }
        except Exception as e:
            raise Exception(f"Error handling payment failed: {str(e)}")
    
    async def handle_payment_captured(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.captured webhook event"""
        try:
            # Demo mode: skip webhook processing
            if self.demo_mode:
                print("[DEMO MODE] Webhook event skipped in demo mode")
                return {'status': 'success', 'message': 'Demo mode: webhook skipped', 'demo': True}
            
            payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')
            
            # Find payment by razorpayOrderId first
            existing_payment = await db.client.payment.find_first(
                where={'razorpayOrderId': order_id}
            )
            
            if not existing_payment:
                return {'status': 'error', 'message': f'Payment not found for order: {order_id}'}
            
            payment = await db.client.payment.update(
                where={'id': existing_payment.id},
                data={
                    'razorpayPaymentId': payment_id,
                    'status': 'SUCCESSFUL'
                }
            )
            
            # Update Order status (async)
            await db.client.order.update(
                where={'id': payment.orderId},
                data={'paymentStatus': 'SUCCESSFUL'}
            )
            
            return {
                'status': 'success',
                'message': 'Payment captured',
                'order_id': order_id
            }
        except Exception as e:
            raise Exception(f"Error handling payment captured: {str(e)}")


# Singleton instance
payment_core = PaymentCore()

