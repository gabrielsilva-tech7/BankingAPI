from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.clientes import router as clientes_router
from app.routes.contas import router as contas_router
from app.routes.transacoes import router as transacoes_router


tags_metadata = [
    {
        "name": "Autenticação",
        "description": "Login e autenticação dos clientes",
    },
    {
        "name": "Clientes",
        "description": "Cadastro e informações dos clientes",
    },
    {
        "name": "Contas",
        "description": "Criação e consulta de contas bancárias",
    },
    {
        "name": "Transações",
        "description": "Depósitos, saques, transferências e extrato",
    },
    {
        "name": "Status",
        "description": "Verificação do funcionamento da API",
    },
]


app = FastAPI(
    title="BankingAPI",
    description="API bancária desenvolvida com FastAPI",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


app.include_router(
    auth_router,
    tags=["Autenticação"],
)

app.include_router(
    clientes_router,
    tags=["Clientes"],
)

app.include_router(
    contas_router,
    tags=["Contas"],
)

app.include_router(
    transacoes_router,
    tags=["Transações"],
)


@app.get("/", tags=["Status"])
def inicio():
    return {"mensagem": "Banking API funcionando"}