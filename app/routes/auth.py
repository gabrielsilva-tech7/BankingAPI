from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas import Login
from app.models import Cliente as ClienteModel
from app.database import get_db
from app.security import verificar_senha, criar_token, verificar_token


router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/auth/login")
def login(
    dados: Login,
    db: Session = Depends(get_db)
):
    cliente = db.query(ClienteModel).filter(
        ClienteModel.email == dados.email
    ).first()

    if cliente is None or not verificar_senha(
        dados.senha,
        cliente.senha_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    token = criar_token(cliente.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def meu_perfil(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    cliente_id = verificar_token(
        credentials.credentials
    )

    if cliente_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    cliente = db.query(ClienteModel).filter(
        ClienteModel.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "email": cliente.email
    }