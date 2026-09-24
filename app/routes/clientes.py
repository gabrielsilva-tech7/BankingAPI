from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.schemas import Cliente, ClienteResposta
from app.models import Cliente as ClienteModel
from app.database import get_db
from app.security import gerar_hash_senha


router = APIRouter()


@router.post(
    "/clientes",
    response_model=ClienteResposta,
    status_code=status.HTTP_201_CREATED
)
def criar_cliente(
    cliente: Cliente,
    db: Session = Depends(get_db)
):
    cliente_existente = db.query(ClienteModel).filter(
        ClienteModel.email == cliente.email
    ).first()

    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado"
        )

    cpf_existente = db.query(ClienteModel).filter(
        ClienteModel.cpf == cliente.cpf
    ).first()

    if cpf_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF já cadastrado"
        )

    novo_cliente = ClienteModel(
        nome=cliente.nome,
        cpf=cliente.cpf,
        email=cliente.email,
        senha_hash=gerar_hash_senha(cliente.senha)
    )

    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)

    return novo_cliente