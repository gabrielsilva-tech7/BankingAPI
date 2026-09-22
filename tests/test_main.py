from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


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
        "/login",
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
    response = client.post(
        "/clientes",
        json={
            "nome": "Cliente Pytest",
            "cpf": "52998224725",
            "email": "pytest@teste.com",
            "senha": "Teste123"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["nome"] == "Cliente Pytest"
    assert dados["email"] == "pytest@teste.com"
    assert "senha" not in dados
    assert "senha_hash" not in dados


def test_login_valido():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Login",
            "cpf": "11144477735",
            "email": "login@teste.com",
            "senha": "Teste123"
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "login@teste.com",
            "senha": "Teste123"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert "access_token" in dados
    assert dados["token_type"] == "bearer"


def test_me_com_token():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Token",
            "cpf": "93541134780",
            "email": "token@teste.com",
            "senha": "Teste123"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "token@teste.com",
            "senha": "Teste123"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "token@teste.com"


def test_criar_conta():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Conta",
            "cpf": "39053344705",
            "email": "conta@teste.com",
            "senha": "Teste123"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "conta@teste.com",
            "senha": "Teste123"
        }
    )

    token = login.json()["access_token"]

    response = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["saldo"] == "0.00" or float(dados["saldo"]) == 0.0


def test_deposito():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Deposito",
            "cpf": "86288366757",
            "email": "deposito@teste.com",
            "senha": "Teste123"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "deposito@teste.com",
            "senha": "Teste123"
        }
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    conta_id = conta.json()["id"]

    response = client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 100.50
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert float(response.json()["saldo"]) == 100.50


def test_saque():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Saque",
            "cpf": "16899535009",
            "email": "saque@teste.com",
            "senha": "Teste123"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "saque@teste.com",
            "senha": "Teste123"
        }
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    conta_id = conta.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 200.00
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 50.00
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert float(response.json()["saldo"]) == 150.00


def test_saque_saldo_insuficiente():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Sem Saldo",
            "cpf": "28001238938",
            "email": "semsaldo@teste.com",
            "senha": "Teste123"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "semsaldo@teste.com",
            "senha": "Teste123"
        }
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    conta_id = conta.json()["id"]

    response = client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 100.00
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Saldo insuficiente"


def test_transferencia():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Origem",
            "cpf": "31415926590",
            "email": "origem@teste.com",
            "senha": "Teste123"
        }
    )

    login1 = client.post(
        "/login",
        json={
            "email": "origem@teste.com",
            "senha": "Teste123"
        }
    )

    token1 = login1.json()["access_token"]

    conta1 = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    client.post(
        "/clientes",
        json={
            "nome": "Cliente Destino",
            "cpf": "27182818205",
            "email": "destino@teste.com",
            "senha": "Teste123"
        }
    )

    login2 = client.post(
        "/login",
        json={
            "email": "destino@teste.com",
            "senha": "Teste123"
        }
    )

    token2 = login2.json()["access_token"]

    conta2 = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    conta1_id = conta1.json()["id"]
    conta2_id = conta2.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta1_id,
            "valor": 300.00
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    response = client.post(
        "/transferencias",
        json={
            "conta_origem_id": conta1_id,
            "conta_destino_id": conta2_id,
            "valor": 100.00
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert float(dados["conta_origem"]["saldo"]) == 200.00
    assert float(dados["conta_destino"]["saldo"]) == 100.00


def test_extrato():
    client.post(
        "/clientes",
        json={
            "nome": "Cliente Extrato",
            "cpf": "14142135651",
            "email": "extrato@teste.com",
            "senha": "Teste123"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "extrato@teste.com",
            "senha": "Teste123"
        }
    )

    token = login.json()["access_token"]

    conta = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    conta_id = conta.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 150.00
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 50.00
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.get(
        f"/contas/{conta_id}/extrato",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert float(dados["saldo"]) == 100.00
    assert len(dados["transacoes"]) == 2


def test_bloquear_saque_conta_alheia():
    client.post(
        "/clientes",
        json={
            "nome": "Dono Conta",
            "cpf": "17320508052",
            "email": "dono@teste.com",
            "senha": "Teste123"
        }
    )

    login_dono = client.post(
        "/login",
        json={
            "email": "dono@teste.com",
            "senha": "Teste123"
        }
    )

    token_dono = login_dono.json()["access_token"]

    conta = client.post(
        "/contas",
        headers={
            "Authorization": f"Bearer {token_dono}"
        }
    )

    conta_id = conta.json()["id"]

    client.post(
        "/depositos",
        json={
            "conta_id": conta_id,
            "valor": 100.00
        },
        headers={
            "Authorization": f"Bearer {token_dono}"
        }
    )

    client.post(
        "/clientes",
        json={
            "nome": "Outro Cliente",
            "cpf": "22360679767",
            "email": "outro@teste.com",
            "senha": "Teste123"
        }
    )

    login_outro = client.post(
        "/login",
        json={
            "email": "outro@teste.com",
            "senha": "Teste123"
        }
    )

    token_outro = login_outro.json()["access_token"]

    response = client.post(
        "/saques",
        json={
            "conta_id": conta_id,
            "valor": 10.00
        },
        headers={
            "Authorization": f"Bearer {token_outro}"
        }
    )

    assert response.status_code == 403