from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.domain.models import CanalPedidoEnum, PedidoStatusEnum, RoleEnum


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=60)
    consentimento_lgpd: bool


class UserInternalCreate(UserCreate):
    role: RoleEnum


class UserOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    role: RoleEnum
    consentimento_lgpd: bool
    pontos_fidelidade: int

    model_config = {"from_attributes": True}


class UnidadeCreate(BaseModel):
    nome: str
    cidade: str


class UnidadeOut(BaseModel):
    id: int
    nome: str
    cidade: str
    ativo: bool

    model_config = {"from_attributes": True}


class ProdutoCreate(BaseModel):
    nome: str
    descricao: str
    preco: Decimal = Field(gt=0)


class ProdutoOut(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: Decimal
    ativo: bool

    model_config = {"from_attributes": True}


class EstoqueMovimentacaoIn(BaseModel):
    unidade_id: int
    produto_id: int
    tipo: str = Field(pattern="^(ENTRADA|SAIDA)$")
    quantidade: int = Field(gt=0)


class EstoqueSaldoOut(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int


class PedidoItemIn(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class PedidoCreate(BaseModel):
    unidade_id: int
    canalPedido: CanalPedidoEnum
    itens: list[PedidoItemIn]


class PedidoItemOut(BaseModel):
    produto_id: int
    quantidade: int
    preco_unitario: Decimal

    model_config = {"from_attributes": True}


class PedidoOut(BaseModel):
    id: int
    cliente_id: int
    unidade_id: int
    canal_pedido: CanalPedidoEnum
    status: PedidoStatusEnum
    valor_total: Decimal
    criado_em: datetime
    itens: list[PedidoItemOut]

    model_config = {"from_attributes": True}


class PagamentoProcessarIn(BaseModel):
    aprovado: bool
    observacao: str = ""


class PedidoStatusUpdateIn(BaseModel):
    novo_status: PedidoStatusEnum


class FidelidadeResgateIn(BaseModel):
    pontos: int = Field(gt=0)
