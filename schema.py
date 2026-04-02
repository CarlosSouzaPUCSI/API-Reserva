from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from model import status_reserva

# Criando um schema que vai ser o de entrada
class reservaEntrada(BaseModel):
    id_cliente: int
    id_sala: int
    entrada: datetime
    saida: datetime

# Criando um schema que vai ser o de edição pontual
class reservaEdicao(BaseModel):
    id_cliente: Optional[int] = None
    id_sala: Optional[int] = None
    status: Optional[status_reserva] = None
    entrada: Optional[datetime] = None
    saida: Optional[datetime] = None