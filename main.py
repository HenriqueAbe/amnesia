from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import SECRET_KEY
from apps.auth.router import router as auth_router
from apps.filmes.router import router as filmes_router
from apps.perfil.router import router as perfil_router
from apps.avaliacoes.router import router as avaliacoes_router
from apps.meus_filmes.router import router as meus_filmes_router
from apps.dashboard.router import router as dashboard_router

app = FastAPI(title="Amnesia – Cinema")

# Middleware de sessão

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="amnesia_session",
    max_age=86_400,
    same_site="lax",
    https_only=False,
)

# Arquivos estáticos

app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers por domínio

app.include_router(auth_router)
app.include_router(filmes_router)
app.include_router(perfil_router)
app.include_router(avaliacoes_router)
app.include_router(meus_filmes_router)
app.include_router(dashboard_router)