from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.domain.models import RoleEnum, User
from app.schemas import FidelidadeResgateIn

router = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])


@router.get("/saldo/{cliente_id}")
def saldo(cliente_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == RoleEnum.CLIENTE and current_user.id != cliente_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    cliente = db.scalar(select(User).where(User.id == cliente_id))
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return {"clienteId": cliente.id, "pontos": cliente.pontos_fidelidade}


@router.post("/resgatar/{cliente_id}")
def resgatar(
    cliente_id: int,
    payload: FidelidadeResgateIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.GERENTE, RoleEnum.ATENDENTE)),
):
    cliente = db.scalar(select(User).where(User.id == cliente_id))
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if cliente.pontos_fidelidade < payload.pontos:
        raise HTTPException(status_code=409, detail="Pontos insuficientes")

    cliente.pontos_fidelidade -= payload.pontos
    db.commit()
    db.refresh(cliente)

    return {"clienteId": cliente.id, "pontosRestantes": cliente.pontos_fidelidade}
