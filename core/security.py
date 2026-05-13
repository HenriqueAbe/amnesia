import bcrypt
import jwt
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return None


def refresh_access_token(token: str) -> str | None:
    payload = decode_token(token)
    if not payload:
        return None

    return create_access_token({
        "sub": payload.get("sub"),
        "nome_usuario": payload.get("nome_usuario"),
        "email": payload.get("email"),
        "tipo": payload.get("tipo"),
    })
