"""user authentication utils."""

from django.core.mail import send_mail
from django.conf import settings
from users.models import OTP
from django.tasks import task
from random import randint


def generate_otp(user) -> str:
    """Generate a 6-digit OTP.

    The method should generate a random 6-digit OTP code
    that will be sent to the user through sent_otp_via_mail task.
    """
    otp_code = str(randint(100000, 999999))
    if OTP.objects.filter(code=otp_code, is_used=False).exists():
        return generate_otp(user)

    OTP.objects.create(code=otp_code, user=user)
    return send_otp_via_email.enqueue(user.email, otp_code)


@task(priority=1, queue_name="high_priority")
def send_otp_via_email(email, otp):
    """Send OTP to the user's email address."""
    subject = "Your One-Time Password (OTP)"
    message = (
        f"Your OTP is: {otp}. "
        f"Click on the link: http://localhost:8000/api/v1/users/verify-otp/?email={email} "
        f"to verify your account."
    )

    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


@task(priority=1, queue_name="data_sync")
def activate_user_account(otp_id):
    """Activate the user's account after the user
    has verified their otp received via email."""

    try:
        otp = OTP.objects.select_related("user").get(pk=otp_id)
        user = otp.user
        user.is_active = True
        user.save()
    except OTP.DoesNotExist:
        pass
