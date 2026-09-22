from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import Deposito, Saque, Transferencia
from app.models import Conta as ContaModel
from app.models import Transacao as TransacaoModel
from app.database import get_db
from app.dependencies import get_cliente_atual
from app.models import Cliente as ClienteModel


router = APIRouter()


# =========================
# DEPÓSITO
# =========================

@router.post("/depositos")
def depositar(
    deposito: Deposito,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    conta = db.query(ContaModel).filter(
        ContaModel.id == deposito.conta_id
    ).first()

    if conta is None:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada"
        )

    if conta.cliente_id != cliente_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para depositar nesta conta"
        )

    conta.saldo += deposito.valor

    nova_transacao = TransacaoModel(
        tipo="deposito",
        conta_id=conta.id,
        valor=deposito.valor
    )

    db.add(nova_transacao)
    db.commit()
    db.refresh(conta)

    return conta

# =========================
# SAQUE
# =========================

@router.post("/saques")
def sacar(
    saque: Saque,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    if saque.valor <= 0:
        raise HTTPException(
            status_code=400,
            detail="O valor do saque deve ser maior que zero"
        )

    conta = db.query(ContaModel).filter(
        ContaModel.id == saque.conta_id
    ).first()

    if conta is None:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada"
        )

    if conta.cliente_id != cliente_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para sacar desta conta"
        )

    if conta.saldo < saque.valor:
        raise HTTPException(
            status_code=400,
            detail="Saldo insuficiente"
        )

    conta.saldo -= saque.valor

    nova_transacao = TransacaoModel(
        tipo="saque",
        conta_id=conta.id,
        valor=saque.valor
    )

    db.add(nova_transacao)
    db.commit()
    db.refresh(conta)

    return conta


# =========================
# TRANSFERÊNCIA
# =========================

@router.post("/transferencias")
def transferir(
    transferencia: Transferencia,
    db: Session = Depends(get_db),
    cliente_atual: ClienteModel = Depends(get_cliente_atual)
):
    if transferencia.valor <= 0:
        raise HTTPException(
            status_code=400,
            detail="O valor da transferência deve ser maior que zero"
        )

    if transferencia.conta_origem_id == transferencia.conta_destino_id:
        raise HTTPException(
            status_code=400,
            detail="A conta de origem e destino não podem ser iguais"
        )

    conta_origem = db.query(ContaModel).filter(
        ContaModel.id == transferencia.conta_origem_id
    ).first()

    conta_destino = db.query(ContaModel).filter(
        ContaModel.id == transferencia.conta_destino_id
    ).first()

    if conta_origem is None:
        raise HTTPException(
            status_code=404,
            detail="Conta de origem não encontrada"
        )

    if conta_origem.cliente_id != cliente_atual.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para transferir desta conta"
        )

    if conta_destino is None:
        raise HTTPException(
            status_code=404,
            detail="Conta de destino não encontrada"
        )

    if conta_origem.saldo < transferencia.valor:
        raise HTTPException(
            status_code=400,
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

    db.add(transacao_saida)
    db.add(transacao_entrada)

    db.commit()

    db.refresh(conta_origem)
    db.refresh(conta_destino)

    return {
        "mensagem": "Transferência realizada com sucesso",
        "conta_origem": {
            "id": conta_origem.id,
            "saldo": conta_origem.saldo
        },
        "conta_destino": {
            "id": conta_destino.id,
            "saldo": conta_destino.saldo
        }
    }


# =========================
# EXTRATO
# =========================

@router.get("/contas/{conta_id}/extrato")
def consultar_extrato(
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
            detail="Você não tem permissão para acessar o extrato desta conta"
        )

    transacoes = db.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta_id
    ).all()

    return {
        "conta_id": conta.id,
        "saldo": conta.saldo,
        "transacoes": transacoes
    }