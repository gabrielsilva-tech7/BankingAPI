from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class Cliente(BaseModel):
    nome: str = Field(
        min_length=3,
        max_length=100
    )

    cpf: str = Field(
        min_length=11,
        max_length=11,
        pattern=r"^\d{11}$"
    )

    email: EmailStr

    senha: str = Field(
        min_length=8,
        max_length=100
    )

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, cpf):
        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido")

        soma = sum(
            int(cpf[i]) * (10 - i)
            for i in range(9)
        )

        resto = (soma * 10) % 11
        primeiro_digito = 0 if resto == 10 else resto

        if primeiro_digito != int(cpf[9]):
            raise ValueError("CPF inválido")

        soma = sum(
            int(cpf[i]) * (11 - i)
            for i in range(10)
        )

        resto = (soma * 10) % 11
        segundo_digito = 0 if resto == 10 else resto

        if segundo_digito != int(cpf[10]):
            raise ValueError("CPF inválido")

        return cpf

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome):
        nome = nome.strip()

        if len(nome) < 3:
            raise ValueError(
                "Nome deve ter pelo menos 3 caracteres"
            )

        return nome

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, senha):
        if not any(
            caractere.isdigit()
            for caractere in senha
        ):
            raise ValueError(
                "A senha deve conter pelo menos um número"
            )

        return senha


class Deposito(BaseModel):
    conta_id: int = Field(gt=0)
    valor: Decimal = Field(gt=0)


class Saque(BaseModel):
    conta_id: int = Field(gt=0)
    valor: Decimal = Field(gt=0)


class Transferencia(BaseModel):
    conta_origem_id: int = Field(gt=0)
    conta_destino_id: int = Field(gt=0)
    valor: Decimal = Field(gt=0)


class Login(BaseModel):
    email: EmailStr
    senha: str


class ClienteResposta(BaseModel):
    id: int
    nome: str
    cpf: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True
    )