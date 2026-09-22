from fastapi import FastAPI

from app.routes.clientes import router as clientes_router
from app.routes.contas import router as contas_router
from app.routes.transacoes import router as transacoes_router
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app import models

app  = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(clientes_router)
app.include_router(contas_router)
app.include_router(transacoes_router)

@app.get("/")
def inicio():
    return {"mensagem": "Banking API funcionando"}
