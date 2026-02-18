from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.domain.models import RoleEnum, User
from app.schemas import TokenOut, UserCreate, UserInternalCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    user = User(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_password(payload.senha),
        role=RoleEnum.CLIENTE,
        consentimento_lgpd=payload.consentimento_lgpd,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register-interno", response_model=UserOut, status_code=201)
def register_internal(
    payload: UserInternalCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleEnum.ADMIN)),
):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    user = User(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_password(payload.senha),
        role=payload.role,
        consentimento_lgpd=payload.consentimento_lgpd,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return TokenOut(access_token=create_access_token(user.email))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
