from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.domain.models import Estoque, Produto, RoleEnum, Unidade, User
from app.schemas import EstoqueMovimentacaoIn, EstoqueSaldoOut, ProdutoCreate, ProdutoOut, UnidadeCreate, UnidadeOut

router = APIRouter(tags=["Catálogo"])


@router.post("/unidades", response_model=UnidadeOut, status_code=201)
def criar_unidade(
    payload: UnidadeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.GERENTE)),
):
    unidade = Unidade(nome=payload.nome, cidade=payload.cidade, ativo=True)
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


@router.get("/unidades", response_model=list[UnidadeOut])
def listar_unidades(db: Session = Depends(get_db)):
    return list(db.scalars(select(Unidade).where(Unidade.ativo.is_(True))).all())


@router.post("/produtos", response_model=ProdutoOut, status_code=201)
def criar_produto(
    payload: ProdutoCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.GERENTE)),
):
    produto = Produto(nome=payload.nome, descricao=payload.descricao, preco=payload.preco, ativo=True)
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=422, detail="Paginação inválida")
    offset = (page - 1) * limit
    query = select(Produto).where(Produto.ativo.is_(True)).offset(offset).limit(limit)
    return list(db.scalars(query).all())


@router.post("/estoque/movimentacoes", response_model=EstoqueSaldoOut)
def movimentar_estoque(
    payload: EstoqueMovimentacaoIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.GERENTE, RoleEnum.ATENDENTE)),
):
    unidade = db.scalar(select(Unidade).where(Unidade.id == payload.unidade_id, Unidade.ativo.is_(True)))
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    produto = db.scalar(select(Produto).where(Produto.id == payload.produto_id, Produto.ativo.is_(True)))
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    estoque = db.scalar(
        select(Estoque).where(Estoque.unidade_id == payload.unidade_id, Estoque.produto_id == payload.produto_id)
    )
    if not estoque:
        estoque = Estoque(unidade_id=payload.unidade_id, produto_id=payload.produto_id, quantidade=0)
        db.add(estoque)
        db.flush()

    if payload.tipo == "ENTRADA":
        estoque.quantidade += payload.quantidade
    else:
        if estoque.quantidade < payload.quantidade:
            raise HTTPException(status_code=409, detail="Saldo insuficiente para saída")
        estoque.quantidade -= payload.quantidade

    db.commit()
    db.refresh(estoque)
    return EstoqueSaldoOut(unidade_id=estoque.unidade_id, produto_id=estoque.produto_id, quantidade=estoque.quantidade)


@router.get("/estoque/saldo", response_model=EstoqueSaldoOut)
def consultar_saldo(unidadeId: int, produtoId: int, db: Session = Depends(get_db)):
    estoque = db.scalar(select(Estoque).where(Estoque.unidade_id == unidadeId, Estoque.produto_id == produtoId))
    if not estoque:
        raise HTTPException(status_code=404, detail="Saldo não encontrado")
    return EstoqueSaldoOut(unidade_id=estoque.unidade_id, produto_id=estoque.produto_id, quantidade=estoque.quantidade)
