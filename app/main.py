from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


# https://github.com/zanfranceschi/rinha-de-backend-2024-q1
# https://rinha-de-backend-2024-q1.herokuapp.com/docs


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Clientes(BaseModel):
    valor: int
    tipo: str
    descricao: str


@app.get("/")
def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}


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


@app.post("/clientes/{id}/transacoes", response_model=None)
def transacoes(id: int, valor: int, tipo: str, descricao: str) -> dict | HTTPException:
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

    cliente_id = busca_cliente(id)
    if cliente_id[0] == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )

    cliente = cliente_id[1]

    saldo: int = 0
    if tipo == "c":
        saldo = cliente["saldo"]["total"] + valor
    elif tipo == "d":
        if cliente["limite"] <= valor and cliente["saldo"]["total"] <= valor:
            saldo = cliente["saldo"]["total"] - valor
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Limite insuficiente",
            )

    cliente["saldo"]["total"] = saldo
    cliente["saldo"]["ultimas_transacoes"].append(
        {
            "valor": valor,
            "tipo": tipo,
            "descricao": descricao,
            "realizada_em": datetime.now().isoformat(),
        }
    )

    return {"limite": cliente["limite"], "saldo": cliente["saldo"]["total"]}


@app.get("/clientes/{id}/extrato", response_model=None)
def extrato(id: int) -> dict | HTTPException:
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

    cliente_id = busca_cliente(id)
    if cliente_id[0] == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )

    cliente = cliente_id[1]

    transacoes: list = []
    index: int = 0
    while index < len(cliente["saldo"]["ultimas_transacoes"]):
        transacoes.append(cliente["saldo"]["ultimas_transacoes"][index])
        index += 1
        if index >= 10:
            break

    extrato = {
        "saldo": {
            "total": cliente["saldo"]["total"],
            "data_extrato": datetime.now().isoformat(),
            "limite": cliente["saldo"]["limite"],
        },
        "ultimas_transacoes": transacoes,
    }

    return extrato
