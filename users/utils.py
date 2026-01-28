"""user authentication utils."""

import hmac
import hashlib
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets

from users.models import OTP, WebhookSecret, UserKYC
from django_tasks import task
from random import randint


def generate_otp(user) -> str:
    """Generate a 6-digit OTP.
    The method should generate a random 6-digit OTP code
    that will be sent to the user through sent_otp_via_mail task."""

    otp = randint(100000, 999999)
    try:
        if OTP.objects.filter(code=str(otp).zfill(6)).exists():
            return "An active OTP already exists for this user."
        OTP.objects.create(code=str(otp).zfill(6), user=user)
    except Exception as e:
        return str(e)
    return send_otp_via_email.enqueue(user.email, str(otp).zfill(6))


@task(priority=1, queue_name="high_priority")
def send_otp_via_email(email, otp):
    """Send OTP to the user's email address."""
    subject = "Your One-Time Password (OTP)"
    message = f"Your OTP is: {otp}. Click on the link: http://localhost:8000/api/v1/users/verify-otp/?emal={email} to verify your account."

    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


@task(priority=1, queue_name="data_sync")
def activate_user_account(otp_id):
    """Activate the user's account after the user
    has verified their otp received via email."""

    try:
        user = OTP.objects.get(pk=otp_id).user
        user.is_active = True
        user.save()
    except Exception as e:
        raise str(e)

def get_or_create_webhook_secret(user):
    """
    Get webhook secret for a user.
    If expired, regenerate it.
    If none exists but user is KYC verified, create one.
    
    Returns:
        tuple: (secret_key, created) or (None, False) if user not KYC verified
    """
    # Check if user is KYC verified
    try:
        kyc = UserKYC.objects.get(users=user, approved=True)
    except UserKYC.DoesNotExist:
        return None, False
    
    # Get existing secret
    webhook_secret = WebhookSecret.objects.filter(user=user).first()
    
    if webhook_secret:
        # Check if expired
        if webhook_secret.is_expired():
            secret_key = webhook_secret.regenerate()
            return secret_key, False
        return webhook_secret.secret_key, False
    else:
        # Create new secret
        secret_key = f"whsk_{secrets.token_urlsafe(32)}"
        WebhookSecret.objects.create(
            user=user,
            secret_key=secret_key,
            is_active=True,
            expires_at=timezone.now() + timedelta(days=90)
        )
        return secret_key, True


def verify_webhook_signature(api_key, signature, payload):
    """
    Verify webhook signature using HMAC-SHA256.
    
    Args:
        api_key (str): The API key from request headers
        signature (str): The signature from X-Webhook-Signature header
        payload (bytes): The request body
    
    Returns:
        tuple: (is_valid, webhook_secret_obj, error_message)
    """
    if not api_key or not signature:
        return False, None, "Missing authentication headers"
    
    # Get webhook secret from database
    try:
        webhook_secret = WebhookSecret.objects.get(
            secret_key=api_key,
            is_active=True
        )
    except WebhookSecret.DoesNotExist:
        return False, None, "Invalid API key"
    
    # Check if expired
    if webhook_secret.is_expired():
        # Regenerate automatically
        webhook_secret.regenerate()
        return False, webhook_secret, "Webhook secret expired. New secret generated. Please update your configuration."
    
    # Verify signature using constant-time comparison
    expected_signature = hmac.new(
        api_key.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    is_valid = hmac.compare_digest(signature, expected_signature)
    
    if not is_valid:
        return False, webhook_secret, "Invalid signature"
    
    return True, webhook_secret, None