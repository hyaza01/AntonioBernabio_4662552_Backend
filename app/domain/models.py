from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    COZINHA = "COZINHA"
    ATENDENTE = "ATENDENTE"
    CLIENTE = "CLIENTE"


class CanalPedidoEnum(str, Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class PedidoStatusEnum(str, Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGO = "PAGO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"
    PAGAMENTO_RECUSADO = "PAGAMENTO_RECUSADO"


class PagamentoStatusEnum(str, Enum):
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum), nullable=False, default=RoleEnum.CLIENTE)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pontos_fidelidade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cidade: Mapped[str] = mapped_column(String(120), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Estoque(Base):
    __tablename__ = "estoques"
    __table_args__ = (UniqueConstraint("unidade_id", "produto_id", name="uq_unidade_produto"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    canal_pedido: Mapped[CanalPedidoEnum] = mapped_column(SqlEnum(CanalPedidoEnum), nullable=False)
    status: Mapped[PedidoStatusEnum] = mapped_column(SqlEnum(PedidoStatusEnum), nullable=False, default=PedidoStatusEnum.AGUARDANDO_PAGAMENTO)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    itens: Mapped[list["PedidoItem"]] = relationship("PedidoItem", cascade="all, delete-orphan")


class PedidoItem(Base):
    __tablename__ = "pedido_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class PagamentoMock(Base):
    __tablename__ = "pagamentos_mock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), unique=True, nullable=False)
    status: Mapped[PagamentoStatusEnum] = mapped_column(SqlEnum(PagamentoStatusEnum), nullable=False)
    payload_requisicao: Mapped[str] = mapped_column(Text, nullable=False)
    payload_resposta: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[str] = mapped_column(String(60), nullable=False)
    detalhes: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
