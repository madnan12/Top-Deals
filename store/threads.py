
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from django.conf import settings

def send_otp_to_email(user=None, verification_code=None):
    if user is None:
        return
    if verification_code is None:
        return

    html_template = render_to_string('email/verification-code.html',
                                   {'verification_code': verification_code, 'img_link': settings.DOMAIN_NAME})
    text_content = strip_tags(html_template)
    
    email = EmailMultiAlternatives(
        'Email Verification OTP',
        text_content,
        settings.EMAIL_HOST_USER,
        to = [user.email]
    )
    
    email.attach_alternative(html_template, "text/html")
    email.send()
    

def send_welcome_email(user=None):
    if user is None:
        return

    html_template = render_to_string('email/welcome-email.html')
                                   
    text_content = strip_tags(html_template)
    
    email = EmailMultiAlternatives(
        'Welcome to Top-Deals',
        text_content,
        settings.EMAIL_HOST_USER,
        to = [user.email]
    )
    
    email.attach_alternative(html_template, "text/html")
    email.send()


def send_request_email(user=None):
    if user is None:
        return
    html_template = render_to_string('email/business-request.html', {'user':user.username})           

    text_template = strip_tags(html_template)
    email = EmailMultiAlternatives(
        'Business Request Submitted',
        text_template,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_template, "text/html")
    email.send()

   