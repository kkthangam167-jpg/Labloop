"""
app/services/email_service.py
─────────────────────────────
Email delivery service for institutional OTP and password resets.
Checks SMTP configuration and prevents false/simulated verification.
"""

from __future__ import annotations

import logging
from flask import current_app
from flask_mail import Message
from app.extensions import mail

logger = logging.getLogger(__name__)


def is_smtp_configured() -> bool:
    """Check if real SMTP credentials are provided in configuration."""
    username = current_app.config.get("MAIL_USERNAME", "").strip()
    password = current_app.config.get("MAIL_PASSWORD", "").strip()
    server = current_app.config.get("MAIL_SERVER", "").strip()
    return bool(username and password and server)


def send_otp_email(recipient_email: str, recipient_name: str, otp_code: str) -> tuple[bool, str]:
    """
    Send OTP verification email to the student's institutional address.

    Returns:
        (success: bool, message: str)
    """
    if not is_smtp_configured():
        msg = (
            "SMTP is not configured in backend/.env. "
            "Please configure MAIL_USERNAME and MAIL_PASSWORD (e.g. Gmail App Password) "
            "on port 587 to dispatch real verification OTP emails to student inboxes."
        )
        logger.warning("Attempted to send OTP to %s but SMTP is unconfigured.", recipient_email)
        return False, msg

    try:
        subject = f"LabLoop – Institutional Verification OTP: {otp_code}"
        sender = current_app.config.get("MAIL_DEFAULT_SENDER", "LabLoop <noreply@francisxavier.ac.in>")

        body = f"""Dear {recipient_name},

Your 6-digit verification code for LabLoop institutional laboratory access is:

    {otp_code}

This code expires in 15 minutes. Enter this code on the verification screen to activate your student account.

If you did not request this registration, please contact your laboratory administrator.

Best regards,
LabLoop Academic Laboratory Team
Francis Xavier Engineering College
"""

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; rounded: 12px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #1e3a8a; margin: 0;">LabLoop Verification</h2>
                <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Institutional Student Access Verification</p>
            </div>
            <p style="color: #334155; font-size: 14px;">Dear <strong>{recipient_name}</strong>,</p>
            <p style="color: #334155; font-size: 14px;">Please enter the following 6-digit One-Time Password (OTP) to verify ownership of your institutional email and activate your account:</p>
            <div style="text-align: center; margin: 24px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1d4ed8; background: #eff6ff; padding: 12px 24px; border-radius: 8px; border: 1px dashed #bfdbfe;">
                    {otp_code}
                </span>
            </div>
            <p style="color: #64748b; font-size: 12px; text-align: center;">This code will expire in <strong>15 minutes</strong>.</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
            <p style="color: #94a3b8; font-size: 11px; text-align: center;">Francis Xavier Engineering College • Smart Laboratory Resource Management</p>
        </div>
        """

        message = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            html=html,
            sender=sender,
        )
        mail.send(message)
        logger.info("OTP verification email sent successfully to %s", recipient_email)
        return True, "Verification OTP has been sent to your institutional email address."

    except Exception as exc:
        logger.exception("Failed to send OTP email to %s: %s", recipient_email, exc)
        return False, f"Failed to send email: {str(exc)}"

