import io
from datetime import datetime
from typing import Optional

import qrcode

from app.services.EMAIL_SERVICE.email import EmailService
from app.core.config import settings


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_qr_png(data: str) -> bytes:
    """Return raw PNG bytes for a QR code encoding `data`."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6366f1", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _base_html(title: str, accent: str, body_content: str) -> str:
    """Shared email wrapper with animations and branding."""
    year = datetime.now().year
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  @keyframes fadeDown {{ from{{opacity:0;transform:translateY(-18px)}} to{{opacity:1;transform:translateY(0)}} }}
  @keyframes fadeUp   {{ from{{opacity:0;transform:translateY(18px)}}  to{{opacity:1;transform:translateY(0)}} }}
  @keyframes pulse    {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.04)}} }}
  @keyframes shimmer  {{ 0%{{background-position:200% 0}} 100%{{background-position:-200% 0}} }}

  * {{ box-sizing:border-box; margin:0; padding:0; }}

  body {{
    font-family:'Inter',Arial,sans-serif;
    background:#f0f2f8;
    padding:32px 16px;
    -webkit-font-smoothing:antialiased;
  }}
  .wrapper {{
    max-width:560px;
    margin:auto;
    animation:fadeDown .6s ease both;
  }}
  .header {{
    background:linear-gradient(135deg,{accent} 0%,{accent}cc 100%);
    border-radius:16px 16px 0 0;
    padding:32px 36px 28px;
    text-align:center;
    position:relative;
    overflow:hidden;
  }}
  .header::before {{
    content:'';position:absolute;inset:0;
    background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.15) 50%,transparent 70%);
    background-size:200% 100%;
    animation:shimmer 3s infinite linear;
  }}
  .header-icon {{
    width:56px;height:56px;
    background:rgba(255,255,255,.2);
    border-radius:50%;
    display:inline-flex;align-items:center;justify-content:center;
    font-size:26px;margin-bottom:12px;
    animation:pulse 2.5s ease infinite;
  }}
  .header h1 {{ color:#fff;font-size:1.45rem;font-weight:800;letter-spacing:-.3px; }}
  .header p  {{ color:rgba(255,255,255,.85);font-size:.875rem;margin-top:6px; }}

  .card {{
    background:#fff;
    border-radius:0 0 16px 16px;
    padding:36px;
    box-shadow:0 8px 32px rgba(0,0,0,.08);
    animation:fadeUp .6s .15s ease both;
  }}
  .greeting {{ font-size:1rem;color:#374151;margin-bottom:20px;line-height:1.6; }}
  .greeting strong {{ color:#111827; }}

  .info-table {{ width:100%;border-collapse:separate;border-spacing:0 6px;margin:20px 0; }}
  .info-table td {{ padding:11px 14px;font-size:.875rem; }}
  .info-table td:first-child {{
    background:#f4f5f9;border-radius:8px 0 0 8px;
    font-weight:600;color:#374151;white-space:nowrap;width:110px;
  }}
  .info-table td:last-child {{
    background:#fafafa;border-radius:0 8px 8px 0;
    color:#111827;border-left:2px solid #f0f2f8;
  }}

  .btn {{
    display:inline-block;padding:13px 28px;border-radius:10px;
    text-decoration:none;font-weight:700;font-size:.9rem;letter-spacing:.2px;
    background:linear-gradient(135deg,{accent},{accent}cc);color:#fff !important;
  }}
  .btn-wrap {{ text-align:center;margin:24px 0 8px; }}

  .qr-block {{
    background:linear-gradient(135deg,#f4f5f9,#ede9fe22);
    border:1.5px dashed #c7d2fe;
    border-radius:14px;padding:24px;text-align:center;margin:24px 0;
    animation:fadeUp .6s .3s ease both;
  }}
  .qr-block img {{
    width:148px;height:148px;border-radius:10px;
    box-shadow:0 4px 16px rgba(99,102,241,.2);
    display:block;margin:0 auto 14px;
  }}
  .qr-label {{
    font-size:.78rem;font-weight:600;color:#6366f1;
    text-transform:uppercase;letter-spacing:.8px;
  }}
  .qr-hint {{ font-size:.76rem;color:#9ca3af;margin-top:5px; }}

  .badge {{
    display:inline-block;padding:4px 12px;border-radius:99px;
    font-size:.75rem;font-weight:600;letter-spacing:.3px;
  }}
  .badge-success {{ background:#d1fae5;color:#065f46; }}

  .divider {{ border:none;border-top:1.5px solid #f0f2f8;margin:24px 0; }}

  .footer {{
    text-align:center;padding:20px 0 4px;
    color:#9ca3af;font-size:.75rem;line-height:1.7;
  }}
  .footer a {{ color:#6366f1;text-decoration:none; }}
</style>
</head>
<body>
<div class="wrapper">
{body_content}
  <div class="footer">
    <p>EventHub &middot; Sent automatically &middot; <a href="#">Unsubscribe</a></p>
    <p style="margin-top:4px">&copy; {year} EventHub. All rights reserved.</p>
  </div>
</div>
</body>
</html>"""


# ── service ───────────────────────────────────────────────────────────────────

class NotificationService:

    # ── Registration confirmation + QR ───────────────────────────────────────
    @staticmethod
    async def send_registration_confirmation(
        recipient_email: str,
        user_name: str,
        event_name: str,
        user_id: Optional[int] = None,
        event_id: Optional[int] = None,
    ):
        subject = f"You're registered for '{event_name}'"

        qr_url = (
            f"{settings.DOMAIN}/events/check_user_in_event"
            f"/{recipient_email}/{event_id}"
            if user_id is not None and event_id is not None
            else None
        )

        # Build QR PNG and reference it via CID (works in all email clients)
        inline_images: dict[str, bytes] = {}
        qr_block = ""
        if qr_url:
            inline_images["qr_checkin"] = _make_qr_png(qr_url)
            qr_block = """
    <div class="qr-block">
      <img src="cid:qr_checkin" alt="Check-in QR code" width="148" height="148" />
      <div class="qr-label">Check-in QR Code</div>
      <div class="qr-hint">Show this to the event organizer at the entrance</div>
    </div>"""

        text_body = (
            f"Hello {user_name},\n\n"
            f"Your registration for \"{event_name}\" has been confirmed.\n"
            + (f"\nCheck-in link: {qr_url}\n" if qr_url else "")
            + "\nThank you.\n"
        )

        body_content = f"""
  <div class="header">
    <div class="header-icon">🎉</div>
    <h1>Registration Confirmed!</h1>
    <p>You're all set for an amazing event</p>
  </div>
  <div class="card">
    <p class="greeting">
      Hello <strong>{user_name}</strong>,<br/>
      Your spot has been reserved. We can't wait to see you there!
    </p>
    <table class="info-table">
      <tr><td>🎫 Event</td><td><strong>{event_name}</strong></td></tr>
      <tr><td>📧 Email</td><td>{recipient_email}</td></tr>
      <tr><td>📌 Status</td><td><span class="badge badge-success">Confirmed</span></td></tr>
    </table>
{qr_block}
    <hr class="divider" />
    <p style="font-size:.85rem;color:#6b7280;line-height:1.7">
      Keep this email as your registration proof.
      The QR code above will be scanned at the entrance for a fast check-in.
    </p>
  </div>"""

        html_body = _base_html(subject, "#6366f1", body_content)

        return await EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=html_body,
            inline_images=inline_images or None,
        )

    # ── Event reminder (24 h before) ─────────────────────────────────────────
    @staticmethod
    async def send_event_reminder(
        recipient_email: str,
        user_name: str,
        event_name: str,
        event_start: datetime,
        event_location: str,
    ):
        formatted_time = event_start.strftime("%A, %B %d %Y at %H:%M")
        subject = f"Reminder: '{event_name}' is tomorrow!"

        text_body = (
            f"Hello {user_name},\n\n"
            f"Reminder: {event_name} starts tomorrow.\n"
            f"When : {formatted_time}\n"
            f"Where: {event_location}\n\nSee you there!\n"
        )

        body_content = f"""
  <div class="header">
    <div class="header-icon">⏰</div>
    <h1>Event Tomorrow!</h1>
    <p>Don't forget — your event is just around the corner</p>
  </div>
  <div class="card">
    <p class="greeting">
      Hey <strong>{user_name}</strong>!<br/>
      Just a friendly reminder that <strong>{event_name}</strong> is happening
      <strong>tomorrow</strong>. Make sure you're ready!
    </p>
    <table class="info-table">
      <tr><td>🎫 Event</td><td><strong>{event_name}</strong></td></tr>
      <tr><td>📅 When</td><td>{formatted_time}</td></tr>
      <tr><td>📍 Where</td><td>{event_location}</td></tr>
    </table>
    <hr class="divider" />
    <p style="font-size:.85rem;color:#6b7280;line-height:1.7">
      Bring your confirmation email or QR code for a smooth check-in.
    </p>
  </div>"""

        return await EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=_base_html(subject, "#8b5cf6", body_content),
        )

    # ── Account activation request ───────────────────────────────────────────
    @staticmethod
    async def send_account_activated_email(
        recipient_email: str,
        user_name: str,
        token: str,
    ):
        activation_link = f"{settings.DOMAIN}/auth/activate_user/{token}"
        subject = "Welcome — Activate Your Account"

        text_body = (
            f"Hello {user_name},\n\nActivate your account:\n{activation_link}\n\n"
            f"If you did not create this account, ignore this email.\n"
        )

        body_content = f"""
  <div class="header">
    <div class="header-icon">👋</div>
    <h1>Welcome to EventHub!</h1>
    <p>One click to get started</p>
  </div>
  <div class="card">
    <p class="greeting">
      Hello <strong>{user_name}</strong>,<br/>
      Thanks for signing up! Please activate your account to unlock all features.
    </p>
    <div class="btn-wrap">
      <a class="btn" href="{activation_link}">Activate My Account</a>
    </div>
    <hr class="divider" />
    <p style="font-size:.8rem;color:#9ca3af;line-height:1.7;word-break:break-all">
      Or copy this link:<br/>
      <a href="{activation_link}" style="color:#6366f1">{activation_link}</a>
    </p>
    <p style="font-size:.8rem;color:#9ca3af;margin-top:12px">
      If you didn't create an account, you can safely ignore this email.
    </p>
  </div>"""

        return await EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=_base_html(subject, "#2563eb", body_content),
        )

    # ── Account activated welcome ─────────────────────────────────────────────
    @staticmethod
    async def send_welcome_activation_email(
        recipient_email: str,
        user_name: str,
    ):
        subject = "Account Activated — You're in!"

        text_body = (
            f"Hello {user_name},\n\n"
            f"Your account has been activated. You can now sign in.\n\nThank you.\n"
        )

        body_content = f"""
  <div class="header">
    <div class="header-icon">🎊</div>
    <h1>You're all set!</h1>
    <p>Your account is now active</p>
  </div>
  <div class="card">
    <p class="greeting">
      Hello <strong>{user_name}</strong>,<br/>
      Your account has been activated successfully.
      You can now sign in and start exploring events!
    </p>
    <div class="btn-wrap">
      <a class="btn" href="{settings.DOMAIN}/#/login">Sign In Now</a>
    </div>
    <hr class="divider" />
    <p style="font-size:.85rem;color:#6b7280;text-align:center">
      Welcome aboard — we're excited to have you.
    </p>
  </div>"""

        return await EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=_base_html(subject, "#10b981", body_content),
        )

    # ── Password reset ────────────────────────────────────────────────────────
    @staticmethod
    async def send_reset_password_email(
        recipient_email: str,
        user_name: str,
        token: str,
    ):
        reset_link = f"{settings.DOMAIN}/auth/reset-password/{token}"
        subject = "Reset Your Password"

        text_body = (
            f"Hello {user_name},\n\nReset your password here:\n{reset_link}\n\n"
            f"This link expires in 15 minutes.\n"
            f"If you didn't request this, ignore this email.\n"
        )

        body_content = f"""
  <div class="header">
    <div class="header-icon">🔐</div>
    <h1>Password Reset</h1>
    <p>We received a request to reset your password</p>
  </div>
  <div class="card">
    <p class="greeting">
      Hello <strong>{user_name}</strong>,<br/>
      Click the button below to choose a new password.
      This link is valid for <strong>15 minutes</strong>.
    </p>
    <div class="btn-wrap">
      <a class="btn" href="{reset_link}"
         style="background:linear-gradient(135deg,#dc2626,#ef4444cc)">
        Reset My Password
      </a>
    </div>
    <hr class="divider" />
    <p style="font-size:.8rem;color:#9ca3af;line-height:1.7;word-break:break-all">
      Or copy this link:<br/>
      <a href="{reset_link}" style="color:#dc2626">{reset_link}</a>
    </p>
    <p style="font-size:.8rem;color:#9ca3af;margin-top:14px">
      If you didn't request a password reset, you can safely ignore this email.
    </p>
  </div>"""

        return await EmailService.send_email(
            recipient=recipient_email,
            subject=subject,
            body=text_body,
            html_body=_base_html(subject, "#dc2626", body_content),
        )