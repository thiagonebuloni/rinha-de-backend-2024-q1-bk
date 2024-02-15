from datetime import datetime
from typing import Any, Dict
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db


# https://github.com/zanfranceschi/rinha-de-backend-2024-q1
# https://rinha-de-backend-2024-q1.herokuapp.com/docs


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/sqlalchemy")
def test_clientes(db: Session = Depends(get_db)):
    cliente = db.query(models.Clientes).all()
    return {"data": cliente}


@app.post("/clientes/{id}/transacoes", response_model=None)
def transacoes(
    id: int, valor: int, tipo: str, descricao: str, db: Session = Depends(get_db)
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
    cliente_atualizado: Dict[Any, Any] = {
        "id": id,
        "limite": cliente.limite,
        "saldo": saldo,
    }
    # commit update tabela cliente
    cliente_query.update(cliente_atualizado, synchronize_session=False)

    nova_transacao = models.Transacoes(
        id_cliente=id,
        valor=valor,
        tipo=tipo,
        descricao=descricao,
        realizada_em=datetime.now().isoformat(),
    )

    db.add(nova_transacao)
    db.commit()
    db.refresh(nova_transacao)

    transacao_formatada = {
        "limite": cliente.limite,
        "saldo": cliente.saldo,
    }

    return transacao_formatada


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
        db.query(models.Transacoes)
        .filter(models.Transacoes.id_cliente == id)
        .order_by(desc(models.Transacoes.realizada_em))
        .all()
    )

    # formatada para padrao solicitado e limitada em 10 transacoes
    trans: list = []

    for t in transacoes[:10]:
        transacoes_formatadas: dict = {}
        transacoes_formatadas["valor"] = t.valor
        transacoes_formatadas["tipo"] = t.tipo
        transacoes_formatadas["descricao"] = t.descricao
        transacoes_formatadas["realizada_em"] = t.realizada_em
        trans.append(transacoes_formatadas)

    extrato = {
        "saldo": {
            "total": cliente.saldo,
            "data_extrato": datetime.now().isoformat(),
            "limite": cliente.limite,
        },
        "ultimas_transacoes": trans,
    }

    return extrato
