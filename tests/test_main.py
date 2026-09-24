from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def criar_cliente(nome, cpf, email, senha="Teste123"):
    return client.post(
        "/clientes",
        json={
            "nome": nome,
            "cpf": cpf,
            "email": email,
            "senha": senha
        }
    )


def fazer_login(email, senha="Teste123"):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "senha": senha
        }
    )


def test_inicio():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "mensagem": "Banking API funcionando"
    }


def test_me_sem_token():
    response = client.get("/me")

    assert response.status_code == 401


def test_login_invalido():
    response = client.post(
        "/auth/login",
        json={
            "email": "naoexiste@teste.com",
            "senha": "Senha123"
        }
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Email ou senha incorretos"
    }


def test_cadastro_senha_curta():
    response = client.post(
        "/clientes",
        json={
            "nome": "Cliente Teste",
            "cpf": "12345678901",
            "email": "teste@teste.com",
            "senha": "123"
        }
    )

    assert response.status_code == 422


def test_cadastro_cpf_invalido():
    response = client.post(
        "/clientes",
        json={
            "nome": "Cliente Teste",
            "cpf": "12345678901",
            "email": "cpf@teste.com",
            "senha": "Senha123"
        }
    )

    assert response.status_code == 422


def test_criar_cliente():
    response = criar_cliente(
        "Cliente Pytest",
        "52998224725",
        "pytest@teste.com"
    )

    assert response.status_code == 201

    dados = response.json()

    assert dados["nome"] == "Cliente Pytest"
    assert dados["email"] == "pytest@teste.com"
    assert "senha" not in dados
    assert "senha_hash" not in dados


def test_login_valido():
    criar_cliente(
        "Cliente Login",
        "11144477735",
        "login@teste.com"
    )

    response = fazer_login(
        "login@teste.com"
    )

    assert response.status_code == 200

    dados = response.json()

    assert "access_token" in dados
    assert dados["token_type"] == "bearer"


def test_me_com_token():
    criar_cliente(
        "Cliente Token",
        "93541134780",
        "token@teste.com"
    )

    login = fazer_login(
        "token@teste.com"
    )

    token = login.json()["access_token"]

    response = client.get(
        "/me",
        headers=headers(token)
    )

    assert response.status_code == 200
    assert response.json()["email"] == "token@teste.com"


def test_criar_conta():
    criar_cliente(
        "Cliente Conta",
        "39053344705",
        "conta@teste.com"
    )

    login = fazer_login(
        "conta@teste.com"
    )

    token = login.json()["access_token"]

    response = client.post(
        "/contas",
        headers=headers(token)
    )

    assert response.status_code == 201

    dados = response.json()

    assert float(dados["saldo"]) == 0.0


def test_deposito():
    criar_cliente(
        "Cliente Deposito",
        "86288366757",
        "deposito@teste.com"
    )

    login = fazer_login(
        "deposito@teste.com"
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers=headers(token)
    )

    conta_id = conta.json()["id"]

    response = client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 100.50
        },
        headers=headers(token)
    )

    assert response.status_code == 200
    assert float(response.json()["saldo"]) == 100.50


def test_saque():
    criar_cliente(
        "Cliente Saque",
        "16899535009",
        "saque@teste.com"
    )

    login = fazer_login(
        "saque@teste.com"
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers=headers(token)
    )

    conta_id = conta.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 200.00
        },
        headers=headers(token)
    )

    response = client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 50.00
        },
        headers=headers(token)
    )

    assert response.status_code == 200
    assert float(response.json()["saldo"]) == 150.00


def test_saque_saldo_insuficiente():
    criar_cliente(
        "Cliente Sem Saldo",
        "28001238938",
        "semsaldo@teste.com"
    )

    login = fazer_login(
        "semsaldo@teste.com"
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers=headers(token)
    )

    conta_id = conta.json()["id"]

    response = client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 100.00
        },
        headers=headers(token)
    )

    assert response.status_code == 400

    assert response.json()["detail"] == "Saldo insuficiente"


def test_transferencia():
    criar_cliente(
        "Cliente Origem",
        "31415926590",
        "origem@teste.com"
    )

    login_origem = fazer_login(
        "origem@teste.com"
    )

    token_origem = login_origem.json()["access_token"]

    conta_origem = client.post(
        "/contas",
        headers=headers(token_origem)
    )

    criar_cliente(
        "Cliente Destino",
        "27182818205",
        "destino@teste.com"
    )

    login_destino = fazer_login(
        "destino@teste.com"
    )

    token_destino = login_destino.json()["access_token"]

    conta_destino = client.post(
        "/contas",
        headers=headers(token_destino)
    )

    conta_origem_id = conta_origem.json()["id"]
    conta_destino_id = conta_destino.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_origem_id,
            "valor": 300.00
        },
        headers=headers(token_origem)
    )

    response = client.post(
        "/transferencias",
        json={
            "conta_origem_id": conta_origem_id,
            "conta_destino_id": conta_destino_id,
            "valor": 100.00
        },
        headers=headers(token_origem)
    )

    assert response.status_code == 200

    dados = response.json()

    assert float(dados["saldo"]) == 200.00
    assert "conta_destino" not in dados

    conta_destino_atualizada = client.get(
        f"/contas/{conta_destino_id}",
        headers=headers(token_destino)
    )

    assert conta_destino_atualizada.status_code == 200

    assert float(
        conta_destino_atualizada.json()["saldo"]
    ) == 100.00


def test_extrato():
    criar_cliente(
        "Cliente Extrato",
        "14142135651",
        "extrato@teste.com"
    )

    login = fazer_login(
        "extrato@teste.com"
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers=headers(token)
    )

    conta_id = conta.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 150.00
        },
        headers=headers(token)
    )

    client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 50.00
        },
        headers=headers(token)
    )

    response = client.get(
        f"/contas/{conta_id}/extrato",
        headers=headers(token)
    )

    assert response.status_code == 200

    dados = response.json()

    assert float(dados["saldo"]) == 100.00
    assert len(dados["transacoes"]) == 2


def test_bloquear_saque_conta_alheia():
    criar_cliente(
        "Dono Conta",
        "17320508052",
        "dono@teste.com"
    )

    login_dono = fazer_login(
        "dono@teste.com"
    )

    token_dono = login_dono.json()["access_token"]

    conta = client.post(
        "/contas",
        headers=headers(token_dono)
    )

    conta_id = conta.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 100.00
        },
        headers=headers(token_dono)
    )

    criar_cliente(
        "Outro Cliente",
        "22360679767",
        "outro@teste.com"
    )

    login_outro = fazer_login(
        "outro@teste.com"
    )

    token_outro = login_outro.json()["access_token"]

    response = client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 10.00
        },
        headers=headers(token_outro)
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Conta não encontrada"
    }


def test_bloquear_consulta_conta_alheia():
    criar_cliente(
        "Dono Consulta",
        "98765432100",
        "donoconsulta@teste.com"
    )

    login_dono = fazer_login(
        "donoconsulta@teste.com"
    )

    token_dono = login_dono.json()["access_token"]

    conta = client.post(
        "/contas",
        headers=headers(token_dono)
    )

    conta_id = conta.json()["id"]

    criar_cliente(
        "Outro Consulta",
        "01234567890",
        "outroconsulta@teste.com"
    )

    login_outro = fazer_login(
        "outroconsulta@teste.com"
    )

    token_outro = login_outro.json()["access_token"]

    response = client.get(
        f"/contas/{conta_id}",
        headers=headers(token_outro)
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Conta não encontrada"
    }