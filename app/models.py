from sqlalchemy import Column, Integer, String
from .database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, nullable=False)
    limite = Column(Integer)
    saldo = Column(Integer)


class Transacao(Base):
    __tablename__ = "transacoes"

    id_transacao = Column(Integer, primary_key=True, nullable=False)
    id_cliente = Column(Integer, nullable=False)
    valor = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    descricao = Column(String)
