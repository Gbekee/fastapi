from settings import EMAIL_CONF, RESET_URL_TTL_IN_SECONDS
from fastapi_mail import FastMail, MessageSchema
from services.otpService import OTP_EXPIRY_IN_SECONDS


fast_mail = FastMail(EMAIL_CONF)

async def send_otp_email(email: str, otp: str):
    message = MessageSchema(
        subject="Your OTP Code",
        recipients=[email],
        body=f"Your OTP is: {otp}. Please note that token is valid for {OTP_EXPIRY_IN_SECONDS//60} minutes",
        subtype="plain",
    )
    await fast_mail.send_message(message)

async def set_reset_url(email: str, url: str):
    message = MessageSchema(
        subject="Your OTP Code",
        recipients=[email],
        body=f"Your reset url is: {url}. Please note that url is valid for {RESET_URL_TTL_IN_SECONDS//60} minutes",
        subtype="plain",
    )
    await fast_mail.send_message(message)
