from app.services.EMAIL_SERVICE.email import EmailService
from app.core.config import settings


class NotificationService:

    @staticmethod
    async def send_registration_confirmation(
        recipient_email: str,
        user_name: str,
        event_name: str,
    ):
        subject = f"Registration Confirmed - {event_name}"

        text_body = f"""
Hello {user_name},

Your registration for "{event_name}" has been confirmed.

Thank you.
"""

        html_body = f"""
<html>
<body>
    <h2>Registration Confirmed</h2>

    <p>Hello <strong>{user_name}</strong>,</p>

    <p>
        Your registration for
        <strong>{event_name}</strong>
        has been confirmed.
    </p>

    <p>Thank you.</p>

</body>
</html>
"""

        return EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=html_body,
        )

    @staticmethod
    async def send_account_activated_email(
        recipient_email: str,
        user_name: str,
        token: str,
    ):
        activation_link = f"{settings.DOMAIN}/auth/activate_user/{token}"

        subject = "Welcome - Activate Your Account"

        text_body = f"""
Hello {user_name},

Welcome to our platform.

Please activate your account by visiting:

{activation_link}

If you did not create this account, ignore this email.

Thank you.
"""

        html_body = f"""
<html>
<body>
    <h2>Welcome to Our Platform</h2>

    <p>Hello <strong>{user_name}</strong>,</p>

    <p>Thank you for registering.</p>

    <p>To activate your account click the button below:</p>

    <p>
        <a href="{activation_link}"
           style="
                background:#2563eb;
                color:white;
                padding:12px 24px;
                text-decoration:none;
                border-radius:6px;">
            Activate Account
        </a>
    </p>

    <p>
        If you did not create this account, you can safely ignore this email.
    </p>

</body>
</html>
"""

        return EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=html_body,
        )

    @staticmethod
    async def send_welcome_activation_email(
        recipient_email: str,
        user_name: str,
    ):
        subject = "Account Activated Successfully"

        text_body = f"""
Hello {user_name},

Your account has been activated successfully.

You can now sign in and use all platform features.

Thank you.
"""

        html_body = f"""
<html>
<body>

    <h2>Account Activated</h2>

    <p>Hello <strong>{user_name}</strong>,</p>

    <p>Your account has been activated successfully.</p>

    <p>You can now sign in and use all platform features.</p>

    <p>Thank you.</p>

</body>
</html>
"""

        return EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=html_body,
        )

    @staticmethod
    async def send_reset_password_email(
        recipient_email: str,
        user_name: str,
        token: str,
    ):
        reset_link = f"{settings.DOMAIN}/auth/reset-password/{token}"

        subject = "Reset Your Password"

        text_body = f"""
Hello {user_name},

We received a request to reset your password.

You can reset it using the link below:

{reset_link}

This link expires in 15 minutes.

If you did not request this, you can safely ignore this email.

Thank you.
"""

        html_body = f"""
<html>
<body>

    <h2>Password Reset Request</h2>

    <p>Hello <strong>{user_name}</strong>,</p>

    <p>We received a request to reset your password.</p>

    <p>
        Click the button below to reset it:
    </p>

    <p>
        <a href="{reset_link}"
           style="
                background:#dc2626;
                color:white;
                padding:12px 24px;
                text-decoration:none;
                border-radius:6px;">
            Reset Password
        </a>
    </p>

    <p>This link expires in 15 minutes.</p>

    <p>
        If you did not request this, you can safely ignore this email.
    </p>

</body>
</html>
"""

        return EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=html_body,
        )