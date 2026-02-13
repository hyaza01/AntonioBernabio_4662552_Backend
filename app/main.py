from fastapi import FastAPI

from app.api.routes import auth, catalogo, fidelidade, pedidos
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.db.base import Base
from app.db.init_db import seed_initial_data
from app.db.session import SessionLocal, engine

app = FastAPI(
    title=settings.APP_NAME,
    description="API REST para gestão de lanchonete multicanal (APP, TOTEM, BALCAO, PICKUP, WEB)",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(catalogo.router)
app.include_router(pedidos.router)
app.include_router(fidelidade.router)

register_error_handlers(app)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


@app.get("/")
def health():
    return {"status": "ok", "swagger": "/docs"}
