import json
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import (
    CanalPedidoEnum,
    Estoque,
    PagamentoMock,
    PagamentoStatusEnum,
    Pedido,
    PedidoItem,
    PedidoStatusEnum,
    Produto,
    Unidade,
    User,
)
from app.infrastructure.audit import log_action
from app.schemas import PedidoCreate


TRANSICOES_VALIDAS = {
    PedidoStatusEnum.PAGO: {PedidoStatusEnum.EM_PREPARO, PedidoStatusEnum.CANCELADO},
    PedidoStatusEnum.EM_PREPARO: {PedidoStatusEnum.PRONTO, PedidoStatusEnum.CANCELADO},
    PedidoStatusEnum.PRONTO: {PedidoStatusEnum.ENTREGUE, PedidoStatusEnum.CANCELADO},
}


def criar_pedido(db: Session, cliente: User, pedido_in: PedidoCreate) -> Pedido:
    if not pedido_in.itens:
        raise HTTPException(status_code=422, detail="Pedido deve ter ao menos um item")

    unidade = db.scalar(select(Unidade).where(Unidade.id == pedido_in.unidade_id, Unidade.ativo.is_(True)))
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    pedido = Pedido(
        cliente_id=cliente.id,
        unidade_id=pedido_in.unidade_id,
        canal_pedido=CanalPedidoEnum(pedido_in.canalPedido),
        status=PedidoStatusEnum.AGUARDANDO_PAGAMENTO,
        valor_total=Decimal("0.00"),
    )
    db.add(pedido)
    db.flush()

    total = Decimal("0.00")

    for item in pedido_in.itens:
        produto = db.scalar(select(Produto).where(Produto.id == item.produto_id, Produto.ativo.is_(True)))
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")

        estoque = db.scalar(
            select(Estoque).where(Estoque.unidade_id == pedido_in.unidade_id, Estoque.produto_id == item.produto_id)
        )
        if not estoque:
            raise HTTPException(status_code=409, detail=f"Produto {item.produto_id} sem estoque para a unidade")
        if estoque.quantidade < item.quantidade:
            raise HTTPException(status_code=409, detail=f"Estoque insuficiente para produto {item.produto_id}")

        estoque.quantidade -= item.quantidade

        db.add(
            PedidoItem(
                pedido_id=pedido.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )
        total += produto.preco * item.quantidade

    pedido.valor_total = total
    log_action(
        db,
        usuario_id=cliente.id,
        acao="CRIAR_PEDIDO",
        entidade="Pedido",
        entidade_id=str(pedido.id),
        detalhes=f"Pedido criado via canal {pedido.canal_pedido}",
    )
    db.commit()
    db.refresh(pedido)
    return pedido


def processar_pagamento_mock(db: Session, pedido_id: int, aprovado: bool, observacao: str, executor_id: int) -> Pedido:
    pedido = db.scalar(select(Pedido).where(Pedido.id == pedido_id))
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != PedidoStatusEnum.AGUARDANDO_PAGAMENTO:
        raise HTTPException(status_code=409, detail="Pedido não está aguardando pagamento")

    status_pagamento = PagamentoStatusEnum.APROVADO if aprovado else PagamentoStatusEnum.RECUSADO
    payload_req = {
        "pedidoId": pedido.id,
        "valor": str(pedido.valor_total),
        "canalPedido": pedido.canal_pedido,
    }
    payload_resp = {
        "status": status_pagamento,
        "mensagem": "Pagamento aprovado" if aprovado else "Pagamento recusado",
        "observacao": observacao,
    }

    db.add(
        PagamentoMock(
            pedido_id=pedido.id,
            status=status_pagamento,
            payload_requisicao=json.dumps(payload_req, ensure_ascii=False),
            payload_resposta=json.dumps(payload_resp, ensure_ascii=False),
        )
    )

    if aprovado:
        pedido.status = PedidoStatusEnum.PAGO
        cliente = db.scalar(select(User).where(User.id == pedido.cliente_id))
        if cliente:
            cliente.pontos_fidelidade += int(pedido.valor_total)
    else:
        pedido.status = PedidoStatusEnum.PAGAMENTO_RECUSADO

    log_action(
        db,
        usuario_id=executor_id,
        acao="PROCESSAR_PAGAMENTO_MOCK",
        entidade="Pedido",
        entidade_id=str(pedido.id),
        detalhes=f"Pagamento {status_pagamento}",
    )

    db.commit()
    db.refresh(pedido)
    return pedido


def atualizar_status_pedido(db: Session, pedido_id: int, novo_status: PedidoStatusEnum, executor_id: int) -> Pedido:
    pedido = db.scalar(select(Pedido).where(Pedido.id == pedido_id))
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    permitidos = TRANSICOES_VALIDAS.get(pedido.status, set())
    if novo_status not in permitidos:
        raise HTTPException(status_code=409, detail=f"Transição inválida de {pedido.status} para {novo_status}")

    pedido.status = novo_status

    log_action(
        db,
        usuario_id=executor_id,
        acao="ATUALIZAR_STATUS_PEDIDO",
        entidade="Pedido",
        entidade_id=str(pedido.id),
        detalhes=f"Novo status: {novo_status}",
    )

    db.commit()
    db.refresh(pedido)
    return pedido
