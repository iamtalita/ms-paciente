from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as paciente_router
from app.database import Base, engine
from app.models.paciente import Paciente  # noqa: F401 - registra o modelo no metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Microsserviço de Pacientes (PET-Saúde Digital)",
    description="Cadastro e consulta de pacientes vinculados à UBS, com isolamento por unidade.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(paciente_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"service": "ms-paciente", "status": "ok"}
