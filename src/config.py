import os
from pathlib import Path

from dotenv import load_dotenv

# Cherche le .env depuis src/ ou depuis la racine du projet
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ── Application ───────────────────────────────
APP_ENV: str = os.getenv("APP_ENV", "production")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# ── Base de données ───────────────────────────
DATABASE_URL: str = os.environ["DATABASE_URL"]

# ── JWT ───────────────────────────────────────
JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
JWT_ACCESS_TOKEN_TTL_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_TTL_MINUTES", "60"))

# ── Stripe ────────────────────────────────────
STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_CONNECT_RETURN_URL: str = os.getenv("STRIPE_CONNECT_RETURN_URL", "")
STRIPE_CONNECT_REFRESH_URL: str = os.getenv("STRIPE_CONNECT_REFRESH_URL", "")

# ── Documentation ────────────────────────────────────
DOCS_ENABLED: bool = os.getenv("DOCS_ENABLED", "0") == "1"

# ── CORS ─────────────────────────────────────────────
# Liste des origines autorisées, séparées par des virgules
# Ex: http://localhost:3000,https://mon-front.vercel.app
_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS: list[str] = (
    ["*"] if _cors_raw.strip() == "*"
    else [o.strip() for o in _cors_raw.split(",")]
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
