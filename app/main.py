from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db


# https://github.com/zanfranceschi/rinha-de-backend-2024-q1
# https://rinha-de-backend-2024-q1.herokuapp.com/docs


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Clientes(BaseModel):
    valor: int
    tipo: str
    descricao: str


clientes: list = [
    {
        "id": 1,
        "limite": 100000,
        "saldo": {
            "total": 0,
            "data_extrato": "",
            "limite": 100000,
            "ultimas_transacoes": [
                {
                    "valor": 10,
                    "tipo": "c",
                    "descricao": "descrito",
                    "realizada_em": "2024-01-17T02:34:38.543030Z",
                },
                {
                    "valor": 90000,
                    "tipo": "d",
                    "descricao": "debitooooo",
                    "realizada_em": "2024-01-17T02:34:38.543030Z",
                },
            ],
        },
    },
    {
        "id": 2,
        "limite": 80000,
        "saldo": {
            "total": 0,
            "data_extrato": "",
            "limite": 100000,
            "ultimas_transacoes": [],
        },
    },
    {
        "id": 3,
        "limite": 1000000,
        "saldo": {
            "total": 0,
            "data_extrato": "",
            "limite": 100000,
            "ultimas_transacoes": [],
        },
    },
    {
        "id": 4,
        "limite": 10000000,
        "saldo": {
            "total": 0,
            "data_extrato": "",
            "limite": 100000,
            "ultimas_transacoes": [],
        },
    },
    {
        "id": 5,
        "limite": 500000,
        "saldo": {
            "total": 0,
            "data_extrato": "",
            "limite": 100000,
            "ultimas_transacoes": [],
        },
    },
]


def busca_cliente(id: int) -> tuple[int, dict]:
    for cliente in clientes:
        if cliente["id"] == id:
            return (1, cliente)
    return (-1, {})


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/sqlalchemy")
def test_clientes(db: Session = Depends(get_db)):
    cliente = db.query(models.Clientes).all()
    return {"data": cliente}


@app.post("/clientes/{id}/transacoes", response_model=None)
def transacoes(
    id: int, tipo: str, valor: int, descricao: str, db: Session = Depends(get_db)
) -> dict | HTTPException:
    """
    {
        "valor": 1000,
        "tipo" : "c",
        "descricao" : "descricao"
    }

    Args:
        - [id] (na URL) deve ser um número inteiro representando a identificação do cliente.
        - valor deve um número inteiro positivo que representa centavos (não vamos trabalhar com frações de centavos). Por exemplo, R$ 10 são 1000 centavos.
        - tipo deve ser apenas c para crédito ou d para débito.
        - descricao deve ser uma string de 1 a 10 caractéres.

    Returns:
        limite: deve ser o limite cadastrado do cliente.
        saldo: deve ser o novo saldo após a conclusão da transação.
    """
    # id, tipo, valor, descricao = (*transacao.model_dump().values(),)

    cliente_query = db.query(models.Clientes).filter(models.Clientes.id == id)
    cliente = cliente_query.first()

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )

    saldo = 0
    if tipo == "c":
        saldo = cliente.saldo + valor
    elif tipo == "d":
        if cliente.limite <= valor:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Limite insuficiente",
            )
        elif cliente.saldo >= valor:  # type: ignore
            saldo = cliente.saldo - valor
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Saldo insuficiente",
            )

    print(saldo)
    cliente_atualizado: Dict[_DMLColumnArgument, Any] = {
        "id": id,
        "limite": cliente.limite,
        "saldo": saldo,
    }
    # commit update tabela cliente
    cliente_query.update(cliente_atualizado, synchronize_session=False)

    # commit update tabela transacoes
    # cliente["saldo"]["ultimas_transacoes"].append(
    #     {
    #         "valor": valor,
    #         "tipo": tipo,
    #         "descricao": descricao,
    #         "realizada_em": datetime.now().isoformat(),
    #     }
    # )
    nova_transacao = models.Transacoes(
        id_cliente=id,
        valor=valor,
        tipo=tipo,
        descricao=descricao,
        realizada_em=datetime.now().isoformat(),
    )
    print(nova_transacao)

    db.add(nova_transacao)
    db.commit()
    db.refresh(nova_transacao)

    return {"data": nova_transacao}


@app.get("/clientes/{id}/extrato", response_model=None)
def extrato(id: int, db: Session = Depends(get_db)) -> dict | HTTPException:
    """
    {
        "saldo": {
            "total": -9098,
            "data_extrato": "2024-01-17T02:34:41.217753Z",
            "limite": 100000
        },
        "ultimas_transacoes": [
            {
            "valor": 10,
            "tipo": "c",
            "descricao": "descricao",
            "realizada_em": "2024-01-17T02:34:38.543030Z"
            },
            {
            "valor": 90000,
            "tipo": "d",
            "descricao": "descricao",
            "realizada_em": "2024-01-17T02:34:38.543030Z"
            }
        ]
    }
    """

    cliente = db.query(models.Clientes).filter(models.Clientes.id == id).first()
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )

    transacoes = (
        db.query(models.Transacoes).filter(models.Transacoes.id_cliente == 1).all()
    )

    # transacoes: list = []
    # index: int = 0
    # while index < len(cliente["saldo"]["ultimas_transacoes"]):
    #     transacoes.append(cliente["saldo"]["ultimas_transacoes"][index])
    #     index += 1
    #     if index >= 10:
    #         break

    extrato = {
        "saldo": {
            "total": cliente.saldo,
            "data_extrato": datetime.now().isoformat(),
            "limite": cliente.limite,
        },
        "ultimas_transacoes": transacoes,
    }

    return extrato
