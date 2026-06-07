import smtplib
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
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
        inline_images: Optional[dict[str, bytes]] = None,
        # inline_images = {"cid_name": <raw PNG bytes>, ...}
        # Reference in HTML as:  <img src="cid:cid_name" />
    ) -> bool:
        # Use "related" when we have inline images so CID references resolve,
        # otherwise plain "alternative" is fine.
        if inline_images:
            # Structure: mixed > alternative (text+html) + image parts
            outer = MIMEMultipart("mixed")
            outer["From"]    = settings.SENDER_EMAIL
            outer["To"]      = recipient
            outer["Subject"] = subject

            alternative = MIMEMultipart("alternative")
            alternative.attach(MIMEText(body, "plain"))

            if html_body:
                related = MIMEMultipart("related")
                related.attach(MIMEText(html_body, "html"))

                for cid, img_bytes in inline_images.items():
                    img_part = MIMEImage(img_bytes, _subtype="png")
                    img_part.add_header("Content-ID", f"<{cid}>")
                    img_part.add_header(
                        "Content-Disposition", "inline", filename=f"{cid}.png"
                    )
                    related.attach(img_part)

                alternative.attach(related)

            outer.attach(alternative)
            message = outer

        else:
            message = MIMEMultipart("alternative")
            message["From"]    = settings.SENDER_EMAIL
            message["To"]      = recipient
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            if html_body:
                message.attach(MIMEText(html_body, "html"))

        server = None
        try:
            server = smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SENDER_EMAIL, settings.EMAIL_APP_PASSWORD)
            server.sendmail(
                settings.SENDER_EMAIL,
                recipient,
                message.as_string(),
            )
            return True

        except Exception as exc:
            raise RuntimeError(f"Failed to send email: {str(exc)}")

        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass