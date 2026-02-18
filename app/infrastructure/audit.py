from sqlalchemy.orm import Session

from app.domain.models import AuditLog


def log_action(db: Session, usuario_id: int | None, acao: str, entidade: str, entidade_id: str, detalhes: str) -> None:
    db.add(
        AuditLog(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            detalhes=detalhes,
        )
    )
