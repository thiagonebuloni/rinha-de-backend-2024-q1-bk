from datetime import datetime
from pydantic import BaseModel


class ClientesBase(BaseModel):
    valor: int
    tipo: str
    descricao: str


class TransacoesBase(BaseModel):
    id_cliente: int
    valor: int
    tipo: str
    descricao: str
    realizada_em: datetime
