from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domain.models import Estoque, Produto, RoleEnum, Unidade, User


def seed_initial_data(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == "admin@lanchonete.com"))
    if not admin:
        db.add(
            User(
                nome="Administrador",
                email="admin@lanchonete.com",
                senha_hash=hash_password("admin123"),
                role=RoleEnum.ADMIN,
                consentimento_lgpd=True,
            )
        )

    unidade = db.scalar(select(Unidade).where(Unidade.nome == "Unidade Centro"))
    if not unidade:
        unidade = Unidade(nome="Unidade Centro", cidade="Curitiba", ativo=True)
        db.add(unidade)
        db.flush()

    produto = db.scalar(select(Produto).where(Produto.nome == "X-Burger"))
    if not produto:
        produto = Produto(nome="X-Burger", descricao="Pão, carne e queijo", preco=22.5, ativo=True)
        db.add(produto)
        db.flush()

    estoque = db.scalar(select(Estoque).where(Estoque.unidade_id == unidade.id, Estoque.produto_id == produto.id))
    if not estoque:
        db.add(Estoque(unidade_id=unidade.id, produto_id=produto.id, quantidade=100))

    db.commit()
