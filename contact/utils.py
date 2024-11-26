from django.conf import settings
from django.core.mail import EmailMessage


def send_password_to_mail(user_mail_addr, password):
    try:
        subject = "Forget password"
        body = f"Your new password is {password}\nKeep it securely."
        from_email = settings.EMAIL_HOST_USER
        to_email = [user_mail_addr]

        email = EmailMessage(subject, body, from_email, to_email)
        email.send()
    except Exception:
        raise Exception("Send e-mail failed.")
