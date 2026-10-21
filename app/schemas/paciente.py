import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def normalizar_documento(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\D", "", value)


class PacienteCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., description="CPF com 11 dígitos; pode ser informado com pontuação")
    data_nascimento: date
    cns: Optional[str] = Field(default=None, description="Cartão Nacional de Saúde, se disponível")
    telefone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = None
    endereco: Optional[str] = Field(default=None, max_length=255)
    # Funcionário da UBS usa automaticamente a UBS do token; ADMIN informa este campo.
    ubs_id: Optional[UUID] = None

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: str) -> str:
        cpf = normalizar_documento(value)
        if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11:
            raise ValueError("CPF deve conter 11 dígitos válidos.")
        return cpf

    @field_validator("cns")
    @classmethod
    def validar_cns(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        cns = normalizar_documento(value)
        if len(cns) != 15:
            raise ValueError("CNS deve conter 15 dígitos.")
        return cns

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_nao_pode_ser_futuro(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")
        return value


class PacienteUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=3, max_length=150)
    data_nascimento: Optional[date] = None
    cns: Optional[str] = None
    telefone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = None
    endereco: Optional[str] = Field(default=None, max_length=255)
    ativo: Optional[bool] = None

    @field_validator("cns")
    @classmethod
    def validar_cns(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        cns = normalizar_documento(value)
        if len(cns) != 15:
            raise ValueError("CNS deve conter 15 dígitos.")
        return cns

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_nao_pode_ser_futuro(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")
        return value


class PacienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    cpf: str
    data_nascimento: date
    cns: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    endereco: Optional[str]
    ubs_id: UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime
