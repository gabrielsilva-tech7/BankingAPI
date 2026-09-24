from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_cliente_atual
from app.models import Cliente as ClienteModel
from app.models import Conta as ContaModel
from app.models import Transacao as TransacaoModel
from app.schemas import Deposito, Saque, Transferencia


router = APIRouter()


def buscar_conta_do_cliente(
    conta_id: int,
    cliente_id: int,
    db: Session
):
    conta = db.query(ContaModel).filter(
        ContaModel.id == conta_id,
        ContaModel.cliente_id == cliente_id
    ).first()

    if conta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )

    return conta


@router.post("/depositos")
def depositar(
    deposito: Deposito,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    conta = buscar_conta_do_cliente(
        deposito.conta_id,
        cliente_atual.id,
        db
    )

    conta.saldo += deposito.valor

    transacao = TransacaoModel(
        tipo="deposito",
        conta_id=conta.id,
        valor=deposito.valor
    )

    db.add(transacao)
    db.commit()
    db.refresh(conta)

    return {
        "mensagem": "Depósito realizado com sucesso",
        "conta_id": conta.id,
        "saldo": conta.saldo
    }


@router.post("/saques")
def sacar(
    saque: Saque,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    conta = buscar_conta_do_cliente(
        saque.conta_id,
        cliente_atual.id,
        db
    )

    if conta.saldo < saque.valor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente"
        )

    conta.saldo -= saque.valor

    transacao = TransacaoModel(
        tipo="saque",
        conta_id=conta.id,
        valor=saque.valor
    )

    db.add(transacao)
    db.commit()
    db.refresh(conta)

    return {
        "mensagem": "Saque realizado com sucesso",
        "conta_id": conta.id,
        "saldo": conta.saldo
    }


@router.post("/transferencias")
def transferir(
    transferencia: Transferencia,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    if (
        transferencia.conta_origem_id
        == transferencia.conta_destino_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A conta de origem e destino não podem ser iguais"
        )

    conta_origem = buscar_conta_do_cliente(
        transferencia.conta_origem_id,
        cliente_atual.id,
        db
    )

    conta_destino = db.query(ContaModel).filter(
        ContaModel.id == transferencia.conta_destino_id
    ).first()

    if conta_destino is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de destino não encontrada"
        )

    if conta_origem.saldo < transferencia.valor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente"
        )

    conta_origem.saldo -= transferencia.valor
    conta_destino.saldo += transferencia.valor

    transacao_saida = TransacaoModel(
        tipo="transferencia_saida",
        conta_id=conta_origem.id,
        valor=transferencia.valor
    )

    transacao_entrada = TransacaoModel(
        tipo="transferencia_entrada",
        conta_id=conta_destino.id,
        valor=transferencia.valor
    )

    db.add_all([
        transacao_saida,
        transacao_entrada
    ])

    db.commit()
    db.refresh(conta_origem)

    return {
        "mensagem": "Transferência realizada com sucesso",
        "conta_origem_id": conta_origem.id,
        "saldo": conta_origem.saldo
    }


@router.get("/contas/{conta_id}/extrato")
def consultar_extrato(
    conta_id: int,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    conta = buscar_conta_do_cliente(
        conta_id,
        cliente_atual.id,
        db
    )

    transacoes = db.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id
    ).all()

    return {
        "conta_id": conta.id,
        "saldo": conta.saldo,
        "transacoes": transacoes
    }