# BankingAPI 🏦

API REST de um sistema bancário desenvolvida em **Python com FastAPI**, criada com foco em estudos de desenvolvimento backend e construção de portfólio.

A aplicação permite cadastrar clientes, autenticar usuários e realizar operações bancárias como criação de contas, depósitos, saques, transferências e consulta de extrato.

##  Tecnologias utilizadas

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Alembic
- JWT
- Pytest
- HTTPX

##  Funcionalidades

- Cadastro de clientes
- Validação de CPF
- Validação de e-mail
- Validação de senha
- Hash seguro de senhas
- Login de usuários
- Autenticação com JWT
- Criação de contas bancárias
- Consulta de conta
- Depósitos
- Saques
- Transferências entre contas
- Consulta de extrato
- Controle de acesso por proprietário da conta
- Registro das transações no PostgreSQL
- Testes automatizados

##  Segurança

As senhas dos usuários não são armazenadas diretamente no banco de dados.

A aplicação utiliza **hash de senha** e autenticação baseada em **JWT (JSON Web Token)**.

Operações protegidas exigem autenticação, e o sistema verifica se a conta pertence ao usuário autenticado antes de permitir determinadas operações.

##  Banco de dados

O projeto utiliza **PostgreSQL** como banco de dados principal e **SQLAlchemy** para comunicação entre a aplicação e o banco.

As alterações na estrutura do banco são controladas utilizando **Alembic**.

Principais entidades:

- Clientes
- Contas
- Transações

##  Principais endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/clientes` | Cadastrar cliente |
| POST | `/login` | Realizar login |
| GET | `/me` | Consultar usuário autenticado |
| POST | `/contas` | Criar conta |
| GET | `/contas/{conta_id}` | Consultar conta |
| POST | `/depositos` | Realizar depósito |
| POST | `/saques` | Realizar saque |
| POST | `/transferencias` | Realizar transferência |
| GET | `/contas/{conta_id}/extrato` | Consultar extrato |

##  Testes

O projeto possui testes automatizados utilizando **Pytest**.

Atualmente são testados fluxos como:

- Cadastro de cliente
- Validações de dados
- Login
- Autenticação JWT
- Criação de conta
- Depósito
- Saque
- Saldo insuficiente
- Transferência
- Extrato
- Bloqueio de operações em contas de outros usuários

Para executar:

```bash
python -m pytest
```

Resultado atual:

```text
15 passed
```

##  API Online

A BankingAPI está publicada e pode ser testada através da documentação interativa do Swagger:

**Swagger:** https://bankingapi-production-db1d.up.railway.app/docs

Através do Swagger é possível testar os endpoints de cadastro, autenticação e operações bancárias diretamente pelo navegador.

##  Como executar o projeto

Clone o repositório:

```bash
git clone https://github.com/gabrielsilva-tech7/BankingAPI.git
```

Entre na pasta:

```bash
cd BankingAPI
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências do projeto.

Configure as variáveis de ambiente no arquivo `.env`:

```env
DATABASE_URL=sua_url_do_postgresql
TEST_DATABASE_URL=sua_url_do_banco_de_testes
SECRET_KEY=sua_chave_secreta
```

Execute as migrations:

```bash
python -m alembic upgrade head
```

Inicie a API:

```bash
uvicorn app.main:app --reload --port 8001
```

A documentação interativa estará disponível em:

```text
http://127.0.0.1:8001/docs
```

##  Objetivo do projeto

Este projeto foi desenvolvido para praticar conceitos utilizados no desenvolvimento backend, incluindo APIs REST, autenticação, autorização, bancos de dados relacionais, migrations, validação de dados e testes automatizados.

##  Autor

**Gabriel Silva**

Estudante de Análise e Desenvolvimento de Sistemas, com foco em desenvolvimento backend com Python.

[LinkedIn](https://www.linkedin.com/in/gabriel-silva-954392360/)