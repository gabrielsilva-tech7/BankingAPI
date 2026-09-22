from sqlalchemy import Column, Integer, String, Float, Numeric, ForeignKey, DateTime
from app.database import Base
from datetime import datetime

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    senha_hash = Column(String, nullable=False)

class Conta(Base):
    __tablename__ = "contas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    saldo = Column(Numeric(12, 2), nullable=False, default=0.00)

class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    conta_id = Column(Integer, ForeignKey("contas.id"), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    data = Column(DateTime, default=datetime.now)
