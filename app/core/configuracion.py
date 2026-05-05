"""Carga y expone la configuración base de la aplicación desde variables de entorno."""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
RESEND_FROM_NAME = os.getenv("RESEND_FROM_NAME", "SIGETU")

RESET_PASSWORD_BASE_URL = os.getenv("RESET_PASSWORD_BASE_URL", "")
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))
RESET_REQUEST_LIMIT_WINDOW_MINUTES = int(os.getenv("RESET_REQUEST_LIMIT_WINDOW_MINUTES", "15"))
RESET_REQUEST_LIMIT_MAX = int(os.getenv("RESET_REQUEST_LIMIT_MAX", "15"))
