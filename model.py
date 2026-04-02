from enum import Enum
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from sqlalchemy.dialects.postgresql import ENUM
from datetime import date, datetime
from zoneinfo import ZoneInfo

class status_reserva(str, Enum):
    FINALIZADA = "Finalizada"
    EM_ANDAMENTO = "Em andamento"
    CANCELADA = "Cancelada"
    CONFIRMADA = "Confirmada"

class reservas(SQLModel, table=True):
    id_reserva: Optional[int] = Field(default= None, primary_key= True)
    id_cliente: Optional[int] = Field(foreign_key="cliente.id_cliente", ondelete="SET NULL")
    id_sala: Optional[int] = Field(foreign_key="sala.id_sala", ondelete="SET NULL")
    status: status_reserva = Field(default=status_reserva.CONFIRMADA, sa_column=Column(ENUM(status_reserva, name="status_reserva"), nullable=False))
    feito_em: date = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")).date())
    entrada: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    saida: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))