from fastapi import Request
from core.security import decode_token


def get_current_user(request: Request) -> dict | None:
    token = request.session.get("token")
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    return {
        "id":           payload.get("sub"),
        "nome_usuario": payload.get("nome_usuario"),
        "email":        payload.get("email"),
        "tipo":         payload.get("tipo"),
    }