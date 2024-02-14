from sqlalchemy import Column, Date, Integer, String
from .database import Base


class Clientes(Base):
    __tablename__ = "clientes"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    limite = Column(Integer)
    saldo = Column(Integer)


class Transacoes(Base):
    __tablename__ = "transacoes"

    id_transacao = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    id_cliente = Column(Integer, nullable=False)
    valor = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    descricao = Column(String)
    realizada_em = Column(Date, nullable=False)
