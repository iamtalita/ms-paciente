from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.paciente import Paciente
from app.schemas.paciente import PacienteCreate, PacienteResponse, PacienteUpdate

router = APIRouter(prefix="/api/v1/pacientes", tags=["Pacientes"])


@router.post("", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_paciente(payload: PacienteCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra paciente. Nesta versão demonstrativa, a UBS é informada no corpo."""
    if payload.ubs_id is None:
        raise HTTPException(status_code=422, detail="Informe o ubs_id do paciente.")
    existente = await db.execute(
        select(Paciente).where(
            or_(Paciente.cpf == payload.cpf,
                (Paciente.cns == payload.cns) if payload.cns else False)
        )
    )
    if existente.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Já existe paciente com esse CPF ou CNS.")
    paciente = Paciente(**payload.model_dump())
    db.add(paciente)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="CPF ou CNS já cadastrado.") from exc
    await db.refresh(paciente)
    return paciente


@router.get("", response_model=List[PacienteResponse])
async def listar_pacientes(
    busca: str | None = Query(default=None, description="Busca por nome ou CPF"),
    ubs_id: UUID | None = None,
    apenas_ativos: bool = True,
    limite: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Paciente)
    if apenas_ativos:
        stmt = stmt.where(Paciente.ativo.is_(True))
    if ubs_id:
        stmt = stmt.where(Paciente.ubs_id == ubs_id)
    if busca:
        termo = busca.strip()
        stmt = stmt.where(or_(Paciente.nome.ilike(f"%{termo}%"), Paciente.cpf.like(f"%{termo}%")))
    resultado = await db.execute(stmt.order_by(Paciente.nome).limit(limite))
    return list(resultado.scalars().all())


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obter_paciente(paciente_id: UUID, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    paciente = resultado.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente


@router.patch("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(
    paciente_id: UUID, payload: PacienteUpdate, db: AsyncSession = Depends(get_db)
):
    resultado = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    paciente = resultado.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    dados = payload.model_dump(exclude_unset=True)
    if dados.get("cns"):
        outro = await db.execute(select(Paciente).where(Paciente.cns == dados["cns"], Paciente.id != paciente_id))
        if outro.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="CNS já cadastrado para outro paciente.")
    for campo, valor in dados.items():
        setattr(paciente, campo, valor)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Documento já cadastrado.") from exc
    await db.refresh(paciente)
    return paciente


@router.delete("/{paciente_id}", response_model=PacienteResponse)
async def desativar_paciente(paciente_id: UUID, db: AsyncSession = Depends(get_db)):
    """Desativa o cadastro sem apagar o registro."""
    resultado = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    paciente = resultado.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    paciente.ativo = False
    await db.commit()
    await db.refresh(paciente)
    return paciente
