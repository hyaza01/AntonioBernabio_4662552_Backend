from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_roles
from app.application.pedido_service import atualizar_status_pedido, criar_pedido, processar_pagamento_mock
from app.db.session import get_db
from app.domain.models import CanalPedidoEnum, Pedido, PedidoStatusEnum, RoleEnum, User
from app.schemas import PagamentoProcessarIn, PedidoCreate, PedidoOut, PedidoStatusUpdateIn

router = APIRouter(tags=["Pedidos"])


@router.post("/pedidos", response_model=PedidoOut, status_code=201)
def criar(payload: PedidoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return criar_pedido(db, current_user, payload)


@router.get("/pedidos", response_model=list[PedidoOut])
def listar(
    canalPedido: CanalPedidoEnum | None = None,
    status: PedidoStatusEnum | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Pedido).options(selectinload(Pedido.itens))

    if canalPedido:
        query = query.where(Pedido.canal_pedido == canalPedido)
    if status:
        query = query.where(Pedido.status == status)
    if current_user.role == RoleEnum.CLIENTE:
        query = query.where(Pedido.cliente_id == current_user.id)

    return list(db.scalars(query.order_by(Pedido.id.desc())).all())


@router.patch("/pedidos/{pedido_id}/status", response_model=PedidoOut)
def atualizar_status(
    pedido_id: int,
    payload: PedidoStatusUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.GERENTE, RoleEnum.COZINHA)),
):
    return atualizar_status_pedido(db, pedido_id, payload.novo_status, current_user.id)


@router.post("/pagamentos/mock/{pedido_id}", response_model=PedidoOut)
def processar_pagamento(
    pedido_id: int,
    payload: PagamentoProcessarIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.GERENTE, RoleEnum.ATENDENTE)),
):
    return processar_pagamento_mock(db, pedido_id, payload.aprovado, payload.observacao, current_user.id)
