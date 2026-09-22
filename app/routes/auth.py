from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas import Login
from app.models import Cliente as ClienteModel
from app.database import get_db
from app.security import verificar_senha, criar_token, verificar_token

router = APIRouter()
security = HTTPBearer()


@router.post("/login")
def login(
    dados: Login,
    db: Session = Depends(get_db)
):
    cliente = db.query(ClienteModel).filter(
        ClienteModel.email == dados.email
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

    if not verificar_senha(dados.senha, cliente.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

    token = criar_token(cliente.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def meu_perfil(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    cliente_id = verificar_token(token)

    cliente = db.query(ClienteModel).filter(
        ClienteModel.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "email": cliente.email
    }