# helper functions will include otp generation,email generation
import logging
import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives



import uuid

logger = logging.getLogger(__name__)

# generate otp for password reset
def generate_otp():
    characters = string.ascii_letters + string.digits
    otp = ''.join(random.choices(characters,k=7))
    # print(otp)
    return otp


# generate random unique tracking id for order
def generate_tracking_id():
    characters = string.ascii_letters.upper() + string.digits
    gen_id = ''.join(random.choices(characters,k=11 ))
    unique_id =f"#{gen_id}"
    # print(unique_id)
    return unique_id
# generate_tracking_id()

# email helper function for sending otp
def otp_mail(otp, email):
    subject = "Your Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}. It expires in 2 minutes."
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        print(f"OTP email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        raise

def send_email(subject, message, html_content, recipient_list):
    # Create the email with both text and HTML content
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        to=recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
