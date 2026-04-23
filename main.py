import pymysql
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import bcrypt

import jwt
from jwt.exceptions import InvalidTokenError

from config import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

#Setup
app = FastAPI(title="Amnesia – Cinema")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
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
    # Decodifica o JWT da sessão e retorna os dados do usuario, ou None.
    token = request.session.get("token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "id": payload.get("sub"),
            "nome_usuario": payload.get("nome_usuario"),
            "email": payload.get("email"),
            "tipo": payload.get("tipo"),
        }
    except InvalidTokenError:
        return None


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


#autenticação e registro

@app.post("/cadastro", name="cadastro")
async def cadastro(
    request: Request,
    nome_usuario: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db),
):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT ID FROM Perfil WHERE Email = %s OR Nome_Usuario = %s",
                (email, nome_usuario),
            )
            existing = cursor.fetchone()

            if existing:
                request.session["erro_cadastro"] = "E-mail ou nome de usuário já cadastrado."
                return RedirectResponse(url="/?tab=cad", status_code=303)

            # Inserção do novo usuário
            cursor.execute(
                """
                INSERT INTO Perfil (Nome_Usuario, Email, Senha, Tipo)
                VALUES (%s, %s, %s, 'USER')
                """,
                (nome_usuario, email, hash_password(senha)),
            )
            db.commit()

        request.session["sucesso_cadastro"] = "Conta criada com sucesso! Faça login."
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        db.rollback()
        request.session["erro_cadastro"] = f"Erro ao cadastrar: {str(e)}"
        return RedirectResponse(url="/?tab=cad", status_code=303)
    finally:
        db.close()


@app.post("/login", name="login")
async def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db),
):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT ID, Nome_Usuario, Email, Senha, Tipo FROM Perfil WHERE Email = %s",
                (email,),
            )
            user = cursor.fetchone()

        if not user or not verify_password(senha, user["Senha"]):
            request.session["erro_login"] = "E-mail ou senha incorretos."
            return RedirectResponse(url="/", status_code=303)

        # Gera JWT e armazena na sessão
        token = create_access_token({
            "sub": str(user["ID"]),
            "nome_usuario": user["Nome_Usuario"],
            "email": user["Email"],
            "tipo": user["Tipo"],
        })
        request.session["token"] = token

        # Quando clica em ENTRAR, redireciona para a rota que renderiza o index.html
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
    Página principal de filmes - Agora renderiza o arquivo index.html
    """
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
                    d.Nome AS Diretor,
                    ROUND(AVG(a.Nota), 1) AS Nota_Media,
                    COUNT(a.ID) AS Total_Avaliacoes
                FROM Filme f
                LEFT JOIN Diretor d ON f.Diretor_ID = d.ID
                LEFT JOIN Avaliacao a ON f.ID = a.Filme_ID
                GROUP BY f.ID
                ORDER BY f.Titulo
                """
            )
            filmes = cursor.fetchall()
    finally:
        db.close()

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # CARREGA O INDEX.HTML (O arquivo do Grid)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "filmes": filmes,
        "hoje": agora,
    })


@app.get("/filmes/{filme_id}", name="detalhe_filme", response_class=HTMLResponse)
async def detalhe_filme(request: Request, filme_id: int, db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    f.*,
                    d.Nome AS Diretor,
                    ROUND(AVG(a.Nota), 1) AS Nota_Media
                FROM Filme f
                LEFT JOIN Diretor d ON f.Diretor_ID = d.ID
                LEFT JOIN Avaliacao a ON f.ID = a.Filme_ID
                WHERE f.ID = %s
                GROUP BY f.ID
                """,
                (filme_id,),
            )
            filme = cursor.fetchone()

            if not filme:
                return RedirectResponse(url="/filmes", status_code=303)

            # Busca Gêneros
            cursor.execute(
                """
                SELECT g.Nome FROM Genero g
                JOIN Filme_Genero fg ON g.ID = fg.Genero_ID
                WHERE fg.Filme_ID = %s
                """,
                (filme_id,),
            )
            generos = [row["Nome"] for row in cursor.fetchall()]

            # Busca Elenco
            cursor.execute(
                """
                SELECT aa.Nome FROM Ator_Atriz aa
                JOIN Filme_Ator fa ON aa.ID = fa.Ator_ID
                WHERE fa.Filme_ID = %s
                """,
                (filme_id,),
            )
            atores = [row["Nome"] for row in cursor.fetchall()]

            # Busca Avaliações
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
        "request": request,
        "user": user,
        "filme": filme,
        "generos": generos,
        "atores": atores,
        "avaliacoes": avaliacoes,
    })


@app.post("/avaliar/{filme_id}", name="avaliar_filme")
async def avaliar_filme(
    request: Request,
    filme_id: int,
    nota: float = Form(...),
    comentario: str = Form(""),
    db=Depends(get_db),
):
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

# Rota para Adicionar Filme (Gatilhada pelo Modal do index.html)
@app.post("/adicionar-filme")
async def adicionar_filme(
    request: Request,
    titulo: str = Form(...),
    ano: int = Form(...),
    diretor_nome: str = Form(...),
    capa_url: str = Form(...),
    sinopse: str = Form(""),
    db=Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Lógica do Diretor
            cursor.execute("SELECT ID FROM Diretor WHERE Nome = %s", (diretor_nome,))
            diretor = cursor.fetchone()
            
            if diretor:
                diretor_id = diretor['ID']
            else:
                cursor.execute("INSERT INTO Diretor (Nome) VALUES (%s)", (diretor_nome,))
                diretor_id = cursor.lastrowid

            # Inserir Filme
            sql = """
                INSERT INTO Filme (Titulo, Sinopse, Ano_Lancamento, Capa_URL, Diretor_ID)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (titulo, sinopse, ano, capa_url, diretor_id))
            db.commit()

        return RedirectResponse(url="/filmes", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Erro ao inserir filme: {e}")
        return RedirectResponse(url="/filmes", status_code=303)
    finally:
        db.close()