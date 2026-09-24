import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TEMPO_TOKEN_MINUTOS = 30

password_hash = PasswordHash.recommended()


if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não configurada")


def gerar_hash_senha(senha: str):
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str):
    return password_hash.verify(
        senha,
        senha_hash
    )


def criar_token(cliente_id: int):
    agora = datetime.now(timezone.utc)

    dados = {
        "sub": str(cliente_id),
        "iat": agora,
        "exp": agora + timedelta(
            minutes=TEMPO_TOKEN_MINUTOS
        )
    }

    return jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verificar_token(token: str):
    try:
        dados = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        cliente_id = dados.get("sub")

        if cliente_id is None:
            return None

        return int(cliente_id)

    except (InvalidTokenError, ValueError):
        return None