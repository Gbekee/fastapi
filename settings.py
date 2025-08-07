from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi_mail import  ConnectionConfig
import os

load_dotenv()
DB_URL = os.getenv("DB_URL")
REDIS_URL = os.getenv("REDIS_URL")
AUTH_SECRET= os.getenv("AUTH_SECRET")
CLOUD_API_NAME = os.getenv("CLOUD_API_NAME")
CLOUD_API_SECRET = os.getenv("CLOUD_API_SECRET ")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY ")


EMAIL_CONF = ConnectionConfig(
    MAIL_USERNAME= os.getenv("EMAIL"),
    MAIL_PASSWORD= os.getenv("EMAIL_APP_PASSWORD"),
    MAIL_FROM=os.getenv("EMAIL"),
    MAIL_PORT= 587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_SSL_TLS= False,
    MAIL_STARTTLS= True,
    USE_CREDENTIALS=True,
)

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,  # auto-decodes to str
)

DOMAIN_URL = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES= 60 * 24 * 7 #1 week
RESET_URL_TTL_IN_SECONDS = 60 * 60 # 1 hour
OTP_EXPIRY_IN_SECONDS = 60 * 60 #1 hour
