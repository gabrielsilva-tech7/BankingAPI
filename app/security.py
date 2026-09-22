from pwdlib import PasswordHash
import os
import jwt

from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

password_hash = PasswordHash.recommended()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def gerar_hash_senha(senha: str):
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str):
    return password_hash.verify(senha, senha_hash)



def criar_token(cliente_id: int):
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)

    dados = {
        "sub": str(cliente_id),
        "exp": expiracao
    }

    token = jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def verificar_token(token: str):
    try:
        dados = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        cliente_id = int(dados["sub"])

        return cliente_id

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token invalido ou expirado"
        )