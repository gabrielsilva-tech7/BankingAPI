from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_cliente_atual
from app.models import Cliente as ClienteModel
from app.models import Conta as ContaModel
from app.database import get_db


router = APIRouter()


@router.post(
    "/contas",
    status_code=status.HTTP_201_CREATED
)
def criar_conta(
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    nova_conta = ContaModel(
        cliente_id=cliente_atual.id,
        saldo=Decimal("0.00")
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
        ContaModel.id == conta_id,
        ContaModel.cliente_id == cliente_atual.id
    ).first()

    if conta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )

    return conta