"""Payment core business logic for Razorpay integration"""
from typing import Dict, Any
from datetime import datetime
import os
import razorpay

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payment import Payment
from src.models.order import Order


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
        session: AsyncSession,
        order_id: str,
        user_id: str,
        amount: float,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """Create a Razorpay order and Payment record in database"""
        try:
            # Truncate order_id to fit Razorpay's 40 character limit for receipt
            # Format: "ord_" + last 36 chars of order_id
            receipt = f"ord_{order_id[-36:]}" if len(order_id) > 36 else f"ord_{order_id}"
            
            # Create Razorpay order
            razorpay_order = self.razorpay_client.order.create({
                'amount': int(amount * 100),  # Convert to paise
                'currency': currency,
                'receipt': receipt,
                'notes': {
                    'order_id': order_id,
                    'user_id': user_id
                }
            })
            
            # Create Payment record in database
            payment = Payment(
                id=str(__import__('uuid').uuid4()),
                order_id=order_id,
                user_id=user_id,
                razorpay_order_id=razorpay_order['id'],
                amount=amount,
                currency=currency,
                status="PENDING"
            )
            
            session.add(payment)
            await session.commit()
            
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
        session: AsyncSession,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """Verify Razorpay payment signature (or mock in demo mode)"""
        try:
            # Find the payment by razorpayOrderId
            result = await session.execute(
                select(Payment).where(Payment.razorpay_order_id == order_id)
            )
            existing_payment = result.scalar_one_or_none()
            
            if not existing_payment:
                raise Exception(f"Payment not found for order: {order_id}")
            
            # === DEMO MODE: Auto-approve all payments ===
            if self.demo_mode:
                print(f"[DEMO MODE] Auto-approving payment: {order_id}")
                existing_payment.razorpay_payment_id = payment_id
                existing_payment.razorpay_signature = signature
                existing_payment.status = "SUCCESSFUL"
                
                session.add(existing_payment)
                await session.commit()
                
                # Update Order status
                result = await session.execute(select(Order).where(Order.id == existing_payment.order_id))
                order = result.scalar_one_or_none()
                if order:
                    order.payment_status = "SUCCESSFUL"
                    session.add(order)
                    await session.commit()
                
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
                
                # Update Payment record
                existing_payment.razorpay_payment_id = payment_id
                existing_payment.razorpay_signature = signature
                existing_payment.status = "SUCCESSFUL"
                
                session.add(existing_payment)
                await session.commit()
                
                # Update Order status
                result = await session.execute(select(Order).where(Order.id == existing_payment.order_id))
                order = result.scalar_one_or_none()
                if order:
                    order.payment_status = "SUCCESSFUL"
                    session.add(order)
                    await session.commit()
                
                return {
                    'verified': True,
                    'order_id': order_id,
                    'payment_id': payment_id,
                    'status': 'successful'
                }
            else:
                # Mark payment as failed in database
                existing_payment.razorpay_payment_id = payment_id
                existing_payment.status = "FAILED"
                existing_payment.error_message = 'Signature verification failed'
                
                session.add(existing_payment)
                await session.commit()
                
                # Update Order status
                result = await session.execute(select(Order).where(Order.id == existing_payment.order_id))
                order = result.scalar_one_or_none()
                if order:
                    order.payment_status = "FAILED"
                    session.add(order)
                    await session.commit()
                
                return {
                    'verified': False,
                    'order_id': order_id,
                    'payment_id': payment_id,
                    'status': 'failed'
                }
        except Exception as e:
            raise Exception(f"Error in verify_payment: {str(e)}")
    
    async def handle_payment_captured(self, session: AsyncSession, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.captured webhook event"""
        try:
            # Demo mode: skip webhook processing
            if self.demo_mode:
                print("[DEMO MODE] Webhook event skipped in demo mode")
                return {'status': 'success', 'message': 'Demo mode: webhook skipped', 'demo': True}
            
            payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')
            
            # Find payment by razorpayOrderId
            result = await session.execute(
                select(Payment).where(Payment.razorpay_order_id == order_id)
            )
            existing_payment = result.scalar_one_or_none()
            
            if not existing_payment:
                return {'status': 'error', 'message': f'Payment not found for order: {order_id}'}
            
            existing_payment.razorpay_payment_id = payment_id
            existing_payment.status = "SUCCESSFUL"
            
            session.add(existing_payment)
            await session.commit()
            
            # Update Order status
            result = await session.execute(select(Order).where(Order.id == existing_payment.order_id))
            order = result.scalar_one_or_none()
            if order:
                order.payment_status = "SUCCESSFUL"
                session.add(order)
                await session.commit()
            
            return {
                'status': 'success',
                'message': 'Payment captured',
                'order_id': order_id
            }
        except Exception as e:
            raise Exception(f"Error handling payment captured: {str(e)}")
    
    async def handle_payment_failed(self, session: AsyncSession, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment.failed webhook event"""
        try:
            # Demo mode: skip webhook processing
            if self.demo_mode:
                print("[DEMO MODE] Webhook event skipped in demo mode")
                return {'status': 'success', 'message': 'Demo mode: webhook skipped', 'demo': True}
            
            payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            error_message = payment_data.get('error_description', 'Payment failed')
            
            # Find payment by razorpayOrderId
            result = await session.execute(
                select(Payment).where(Payment.razorpay_order_id == order_id)
            )
            existing_payment = result.scalar_one_or_none()
            
            if not existing_payment:
                return {'status': 'error', 'message': f'Payment not found for order: {order_id}'}
            
            existing_payment.status = "FAILED"
            existing_payment.error_message = error_message
            
            session.add(existing_payment)
            await session.commit()
            
            # Update Order status
            result = await session.execute(select(Order).where(Order.id == existing_payment.order_id))
            order = result.scalar_one_or_none()
            if order:
                order.payment_status = "FAILED"
                session.add(order)
                await session.commit()
            
            return {
                'status': 'success',
                'message': 'Payment failure recorded',
                'order_id': order_id
            }
        except Exception as e:
            raise Exception(f"Error handling payment failed: {str(e)}")


# Singleton instance
payment_core = PaymentCore()

