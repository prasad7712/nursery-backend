"""Payment controller for API endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.payment_service import payment_service
from src.data_contracts.api_request_response import (
    CreatePaymentOrderRequest,
    VerifyPaymentRequest,
    PaymentResponse
)
from src.middlewares.auth_middleware import AuthMiddleware, security_scheme
from src.database import get_session

router = APIRouter(prefix="/api/v1", tags=["payments"])
auth_middleware = AuthMiddleware()


# ==================== Endpoints ====================

@router.post("/payments/create-order", response_model=PaymentResponse, status_code=200)
async def create_order(
    request: CreatePaymentOrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a payment order for checkout.
    
    Auth Required: Yes
    
    Request:
    - **order_id**: Database order ID
    - **amount**: Payment amount in rupees
    - **currency**: Currency code (default INR)
    
    Returns:
        - Razorpay order ID
        - Razorpay key ID
        - Amount and currency
    """
    try:
        # Verify auth
        user = await auth_middleware.get_current_user(credentials)
        
        result = await payment_service.create_payment_order(
            session,
            order_id=request.order_id,
            user_id=user.id,
            amount=request.amount,
            currency=request.currency
        )
        
        return PaymentResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/payments/verify", response_model=PaymentResponse, status_code=200)
async def verify_payment(
    request: VerifyPaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Verify a Razorpay payment and update order status.
    
    Auth Required: Yes
    
    Request:
    - **razorpay_order_id**: Razorpay order ID
    - **razorpay_payment_id**: Razorpay payment ID
    - **razorpay_signature**: Razorpay signature
    
    Returns:
        - Verification status
        - Order ID and payment ID
    """
    try:
        # Verify auth
        user = await auth_middleware.get_current_user(credentials)
        
        result = await payment_service.verify_payment(
            session,
            order_id=request.razorpay_order_id,
            payment_id=request.razorpay_payment_id,
            signature=request.razorpay_signature
        )
        
        return PaymentResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify payment: {str(e)}"
        )


@router.post("/webhooks/razorpay", status_code=200)
async def razorpay_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Handle Razorpay webhook events.
    
    This endpoint is called by Razorpay when payment events occur.
    Signature verification ensures authenticity.
    
    Webhook secret should be configured in environment.
    No authentication required - uses signature verification instead.
    """
    try:
        # Get webhook secret from environment
        webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        
        if not webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook secret not configured"
            )
        
        # Get raw body for signature verification
        webhook_body = await request.body()
        webhook_body_str = webhook_body.decode('utf-8')
        
        # Get signature from header
        x_razorpay_signature = request.headers.get('x-razorpay-signature', '')
        
        # Verify webhook signature
        is_valid = payment_service.verify_webhook_signature(
            webhook_body_str,
            x_razorpay_signature,
            webhook_secret
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse webhook event
        event = json.loads(webhook_body_str)
        
        # Process webhook event
        result = await payment_service.handle_webhook(session, event)
        
        return {"status": "received", **result}
    except HTTPException:
        raise
    except Exception as e:
        # Log the error but return 200 to acknowledge receipt
        # Razorpay retries webhooks if we don't return 2xx
        print(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.get("/webhook-secret")
async def get_webhook_secret(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Get webhook secret for Razorpay setup (development only).
    
    Auth Required: Yes
    
    This is for development setup reference only.
    Returns the webhook secret configured in environment.
    """
    try:
        # Verify auth
        user_data = auth_middleware.verify_token(credentials.credentials)
        
        # Check if user is admin (implement based on your auth model)
        webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "not_configured")
        
        return {
            "webhook_secret": webhook_secret if webhook_secret != "not_configured" else None,
            "message": "Configure RAZORPAY_WEBHOOK_SECRET in .env"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/payments/status/{order_id}")
async def get_payment_status(
    order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Get payment status for an order.
    
    Auth Required: Yes
    
    Path Parameters:
    - **order_id**: Database order ID
    
    Returns:
        - Payment status (PENDING, SUCCESSFUL, FAILED, CANCELLED)
        - Payment ID
        - Amount
    """
    try:
        # Verify auth
        user = await auth_middleware.get_current_user(credentials)
        
        from sqlalchemy import select
        from src.models.payment import Payment
        
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )
        
        return {
            "order_id": payment.order_id,
            "payment_id": payment.razorpay_payment_id,
            "status": payment.status.value,
            "amount": payment.amount,
            "currency": payment.currency,
            "created_at": payment.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching payment status: {str(e)}"
        )
