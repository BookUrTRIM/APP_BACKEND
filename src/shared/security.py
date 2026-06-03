import jwt
from datetime import datetime, timedelta, timezone
import config

def create_email_verification_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {"sub": email, "type": "verify_email", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

def decode_email_verification_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        if payload.get("type") != "verify_email":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None