# app/services/email_service.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings


class EmailService:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    @classmethod
    async def send_email(
        cls,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        message = MIMEMultipart("alternative")

        message["From"] = settings.SENDER_EMAIL
        message["To"] = recipient
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        if html_body:
            message.attach(MIMEText(html_body, "html"))

        server = None

        try:
            server = smtplib.SMTP(
                cls.SMTP_SERVER,
                cls.SMTP_PORT,
                timeout=30,
            )

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                settings.SENDER_EMAIL,
                settings.EMAIL_APP_PASSWORD,
            )

            server.sendmail(
                settings.SENDER_EMAIL,
                recipient,
                message.as_string(),
            )

            return True

        except Exception as exc:
            raise RuntimeError(
                f"Failed to send email: {str(exc)}"
            )

        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass