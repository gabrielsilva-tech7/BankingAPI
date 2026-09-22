from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_cliente_atual
from app.models import Cliente as ClienteModel
from app.models import Conta as ContaModel
from app.database import get_db


router = APIRouter()


@router.post("/contas")
def criar_conta(
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    nova_conta = ContaModel(
        cliente_id=cliente_atual.id,
        saldo=0.0
    )

    db.add(nova_conta)
    db.commit()
    db.refresh(nova_conta)

    return nova_conta


@router.get("/contas/{conta_id}")
def buscar_conta(
    conta_id: int,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    conta = db.query(ContaModel).filter(
        ContaModel.id == conta_id
    ).first()

    if conta is None:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada"
        )

    if conta.cliente_id != cliente_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para acessar esta conta"
        )

    return conta