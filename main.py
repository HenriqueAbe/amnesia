import pymysql
from datetime import datetime

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from db import get_db

#Setup
app = FastAPI(title="Amnesia – Cinema")

app.add_middleware(
    SessionMiddleware,
    secret_key="", #devemos adicionar uma secret key
    session_cookie="amnesia_session",
    max_age=50_000,
    same_site="lax",
    https_only=False
)

# arquivos e templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


#helpers
def get_current_user(request: Request) -> dict | None:
    """Return the session user dict, or None if not logged in."""
    return request.session.get("user")


def redirect_to_login(message: str = "") -> RedirectResponse:
    """Shortcut: redirect to '/' (login page)."""
    response = RedirectResponse(url="/", status_code=303)
    return response


#rotas publicas

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Serve the login / registration page.
    If the user is already authenticated, send them straight to /filmes.
    """
    if get_current_user(request):
        return RedirectResponse(url="/filmes", status_code=303)

    return templates.TemplateResponse("loginecadastro.html", {
        "request": request,
        "erro_login": request.session.pop("erro_login", None),
        "erro_cadastro": request.session.pop("erro_cadastro", None),
        "sucesso_cadastro": request.session.pop("sucesso_cadastro", None),
    })


#autentica'cao e registro

@app.post("/cadastro", name="cadastro")
async def cadastro(
    request: Request,
    nome_usuario: str = Form(...),
    email:        str = Form(...),
    senha:        str = Form(...),
    db=Depends(get_db),
):
    """
    Handle new-user registration.

    Business rules (from project spec):
      - Nome_Usuario and Email must be unique (enforced by DB UNIQUE constraint).
      - Passwords are stored as plain text here; swap `senha` for
        `bcrypt.hash(senha)` when you add password hashing.
    """
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT ID FROM Perfil WHERE Email = %s OR Nome_Usuario = %s",
                (email, nome_usuario),
            )
            existing = cursor.fetchone()

            if existing:
                request.session["erro_cadastro"] = (
                    "E-mail ou nome de usuário já cadastrado."
                )
                return RedirectResponse(url="/?tab=cad", status_code=303)

            # insert de ovo usuario
            # TODO: hash the password before storing, e.g.:
            #   from passlib.hash import bcrypt
            #   senha_hash = bcrypt.hash(senha)
            cursor.execute(
                """
                INSERT INTO Perfil (Nome_Usuario, Email, Senha, Tipo)
                VALUES (%s, %s, %s, 'USER')
                """,
                (nome_usuario, email, senha),
            )
            db.commit()

        request.session["sucesso_cadastro"] = (
            "Conta criada com sucesso! Faça login para continuar."
        )
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        db.rollback()
        request.session["erro_cadastro"] = f"Erro ao cadastrar: {str(e)}"
        return RedirectResponse(url="/?tab=cad", status_code=303)

    finally:
        db.close()


#login auth

@app.post("/login", name="login")
async def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db),
):
    """
    Verify credentials and create the user session.

    The session stores a lightweight dict with the user's ID, username,
    and role so that every protected route can read it without hitting
    the DB again.
    """
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT ID, Nome_Usuario, Email, Senha, Tipo FROM Perfil WHERE Email = %s",
                (email,),
            )
            user = cursor.fetchone()

        #checagem cred
        # TODO: replace the plain-text comparison below with:
        #   bcrypt.verify(senha, user["Senha"])
        if not user or user["Senha"] != senha:
            request.session["erro_login"] = "E-mail ou senha incorretos."
            return RedirectResponse(url="/", status_code=303)

        # populando
        request.session["user"] = {
            "id":           user["ID"],
            "nome_usuario": user["Nome_Usuario"],
            "email":        user["Email"],
            "tipo":         user["Tipo"],   # 'USER' or 'ADMIN'
        }

        return RedirectResponse(url="/filmes", status_code=303)

    except Exception as e:
        request.session["erro_login"] = f"Erro interno: {str(e)}"
        return RedirectResponse(url="/", status_code=303)

    finally:
        db.close()


#logout

@app.get("/logout", name="logout")
async def logout(request: Request):
    """Clear the session and redirect to the login page."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


#rotas protegidas
@app.get("/filmes", name="filmes", response_class=HTMLResponse)
async def listar_filmes(request: Request, db=Depends(get_db)):
    """
    Main movie listing page — requires authentication.

    Fetches all films with their director and average rating.
    """
    # --- Auth guard -------------------------------------------------------
    user = get_current_user(request)
    if not user:
        request.session["erro_login"] = "Faça login para acessar."
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    f.ID,
                    f.Titulo,
                    f.Sinopse,
                    f.Ano_Lancamento,
                    f.Classificacao,
                    f.Capa_URL,
                    d.Nome        AS Diretor,
                    ROUND(AVG(a.Nota), 1) AS Nota_Media,
                    COUNT(a.ID)   AS Total_Avaliacoes
                FROM Filme f
                LEFT JOIN Diretor   d ON f.Diretor_ID = d.ID
                LEFT JOIN Avaliacao a ON f.ID = a.Filme_ID
                GROUP BY f.ID
                ORDER BY f.Titulo
                """
            )
            filmes = cursor.fetchall()

    finally:
        db.close()

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    return templates.TemplateResponse("filmes.html", {
        "request": request,
        "user":    user,
        "filmes":  filmes,
        "hoje":    agora,
    })


@app.get("/filmes/{filme_id}", name="detalhe_filme", response_class=HTMLResponse)
async def detalhe_filme(request: Request, filme_id: int, db=Depends(get_db)):
    """
    Movie detail page — requires authentication.

    Fetches the film, its genres, cast, and all reviews.
    """
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:

            # avalia'cao
            cursor.execute(
                """
                SELECT
                    f.*,
                    d.Nome AS Diretor,
                    ROUND(AVG(a.Nota), 1) AS Nota_Media
                FROM Filme f
                LEFT JOIN Diretor   d ON f.Diretor_ID = d.ID
                LEFT JOIN Avaliacao a ON f.ID = a.Filme_ID
                WHERE f.ID = %s
                GROUP BY f.ID
                """,
                (filme_id,),
            )
            filme = cursor.fetchone()

            if not filme:
                return RedirectResponse(url="/filmes", status_code=303)

            # Genres
            cursor.execute(
                """
                SELECT g.Nome FROM Genero g
                JOIN Filme_Genero fg ON g.ID = fg.Genero_ID
                WHERE fg.Filme_ID = %s
                """,
                (filme_id,),
            )
            generos = [row["Nome"] for row in cursor.fetchall()]

            # Cast
            cursor.execute(
                """
                SELECT aa.Nome FROM Ator_Atriz aa
                JOIN Filme_Ator fa ON aa.ID = fa.Ator_ID
                WHERE fa.Filme_ID = %s
                """,
                (filme_id,),
            )
            atores = [row["Nome"] for row in cursor.fetchall()]

            # Reviews
            cursor.execute(
                """
                SELECT
                    p.Nome_Usuario,
                    a.Nota,
                    a.Comentario,
                    DATE_FORMAT(a.Data_Avaliacao, '%%d/%%m/%%Y') AS Data
                FROM Avaliacao a
                JOIN Perfil p ON a.Perfil_ID = p.ID
                WHERE a.Filme_ID = %s
                ORDER BY a.Data_Avaliacao DESC
                """,
                (filme_id,),
            )
            avaliacoes = cursor.fetchall()

    finally:
        db.close()

    return templates.TemplateResponse("filme_detalhe.html", {
        "request":   request,
        "user":      user,
        "filme":     filme,
        "generos":   generos,
        "atores":    atores,
        "avaliacoes": avaliacoes,
    })


#reviews

@app.post("/avaliar/{filme_id}", name="avaliar_filme")
async def avaliar_filme(
    request:   Request,
    filme_id:  int,
    nota:      float = Form(...),
    comentario: str  = Form(""),
    db=Depends(get_db),
):
    """
    Submit or update a review for a film.

    The DB enforces UNIQUE (Filme_ID, Perfil_ID), so duplicate reviews
    are rejected at the constraint level.
    """
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Avaliacao (Filme_ID, Perfil_ID, Nota, Comentario)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Nota = VALUES(Nota),
                    Comentario = VALUES(Comentario),
                    Data_Avaliacao = CURRENT_TIMESTAMP
                """,
                (filme_id, user["id"], nota, comentario),
            )
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"[AVALIAÇÃO] Erro: {e}")

    finally:
        db.close()

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)