import os

from dotenv import load_dotenv

load_dotenv()

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

# ── Swagger ───────────────────────────────────
SWAGGER_ENABLED: bool = os.getenv("SWAGGER_ENABLED", "0") == "1"
