"""Payment service for handling Razorpay operations"""
from typing import Dict, Any
import hmac
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.payment_core import payment_core


class PaymentService:
    """Payment service with error handling"""
    
    async def create_payment_order(
        self,
        session: AsyncSession,
        order_id: str,
        user_id: str,
        amount: float,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order for payment.
        
        Args:
            order_id: Order ID from database
            user_id: User ID
            amount: Payment amount in rupees
            currency: Currency code (default INR)
        
        Returns:
            {
                'id': razorpay_order_id,
                'amount': 5000,
                'currency': 'INR',
                'status': 'created',
                'key_id': razorpay_key_id
            }
        """
        try:
            result = await payment_core.create_payment_order(
                session, order_id, user_id, amount, currency
            )
            return result
        except Exception as e:
            raise Exception(f"Error creating payment order: {str(e)}")
    
    async def verify_payment(
        self,
        session: AsyncSession,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify Razorpay payment signature and update order status.
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
        
        Returns:
            {
                'verified': True/False,
                'order_id': order_id,
                'payment_id': payment_id,
                'status': 'successful' or 'failed'
            }
        """
        try:
            result = await payment_core.verify_payment(
                session, order_id, payment_id, signature
            )
            return result
        except Exception as e:
            raise Exception(f"Error verifying payment: {str(e)}")
    
    async def handle_webhook(
        self,
        session: AsyncSession,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle Razorpay webhook events for payment updates.
        
        Args:
            event: Webhook event data from Razorpay
        
        Returns:
            {
                'status': 'success' or 'error',
                'message': description,
                'order_id': order_id
            }
        """
        try:
            event_type = event.get('event')
            
            if event_type == 'payment.authorized':
                return await payment_core.handle_payment_authorized(session, event)
            elif event_type == 'payment.failed':
                return await payment_core.handle_payment_failed(session, event)
            elif event_type == 'payment.captured':
                return await payment_core.handle_payment_captured(session, event)
            else:
                return {'status': 'unknown_event', 'message': f'Event: {event_type}'}
        except Exception as e:
            raise Exception(f"Error handling webhook: {str(e)}")
    
    @staticmethod
    def verify_webhook_signature(
        webhook_body: str,
        webhook_signature: str,
        webhook_secret: str
    ) -> bool:
        """
        Verify Razorpay webhook signature to ensure authenticity.
        
        Args:
            webhook_body: Raw webhook body as string
            webhook_signature: Signature from Razorpay header
            webhook_secret: Your webhook secret from Razorpay
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                webhook_body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, webhook_signature)
        except Exception as e:
            print(f"Error verifying webhook signature: {str(e)}")
            return False


# Singleton instance
payment_service = PaymentService()

