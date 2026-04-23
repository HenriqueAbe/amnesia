import pymysql
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from fastapi import Response
import base64
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
    payload["exp"] = datetime.utcnow(
    ) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Setup
app = FastAPI(title="Amnesia – Cinema")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="amnesia_session",
    max_age=50_000,
    same_site="lax",
    https_only=False
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# helpers
def get_current_user(request: Request) -> dict | None:
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


# rotas públicas

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/filmes", status_code=303)

    return templates.TemplateResponse("loginecadastro.html", {
        "request": request,
        "erro_login":       request.session.pop("erro_login", None),
        "erro_cadastro":    request.session.pop("erro_cadastro", None),
        "sucesso_cadastro": request.session.pop("sucesso_cadastro", None),
        "form_nome":        request.session.pop("form_nome", ""),
        "form_email":       request.session.pop("form_email", ""),
        "form_data":        request.session.pop("form_data", ""),
    })


# autenticação e registro

@app.post("/cadastro", name="cadastro")
async def cadastro(
    request: Request,
    nome_usuario: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    data_de_nascimento: str = Form(""),
    db=Depends(get_db),
):
    def salvar_e_redirecionar(erro: str):
        request.session["erro_cadastro"] = erro
        request.session["form_nome"] = nome_usuario
        request.session["form_email"] = email
        request.session["form_data"] = data_de_nascimento
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT ID FROM Perfil WHERE Email = %s", (email,))
            if cursor.fetchone():
                return salvar_e_redirecionar("Este e-mail já está cadastrado.")

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
        return salvar_e_redirecionar(f"Erro ao cadastrar: {str(e)}")
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

        token = create_access_token({
            "sub": str(user["ID"]),
            "nome_usuario": user["Nome_Usuario"],
            "email": user["Email"],
            "tipo": user["Tipo"],
        })
        request.session["token"] = token
        return RedirectResponse(url="/filmes", status_code=303)

    except Exception as e:
        request.session["erro_login"] = f"Erro interno: {str(e)}"
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()


# logout

@app.get("/logout", name="logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# rotas protegidas

@app.get("/filmes", name="filmes", response_class=HTMLResponse)
async def listar_filmes(request: Request, db=Depends(get_db)):
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

            cursor.execute(
                """
                SELECT g.Nome FROM Genero g
                JOIN Filme_Genero fg ON g.ID = fg.Genero_ID
                WHERE fg.Filme_ID = %s
                """,
                (filme_id,),
            )
            generos = [row["Nome"] for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT aa.Nome FROM Ator_Atriz aa
                JOIN Filme_Ator fa ON aa.ID = fa.Ator_ID
                WHERE fa.Filme_ID = %s
                """,
                (filme_id,),
            )
            atores = [row["Nome"] for row in cursor.fetchall()]

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
            cursor.execute(
                "SELECT ID FROM Diretor WHERE Nome = %s", (diretor_nome,))
            diretor = cursor.fetchone()
            if diretor:
                diretor_id = diretor['ID']
            else:
                cursor.execute(
                    "INSERT INTO Diretor (Nome) VALUES (%s)", (diretor_nome,))
                diretor_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO Filme (Titulo, Sinopse, Ano_Lancamento, Capa_URL, Diretor_ID)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (titulo, sinopse, ano, capa_url, diretor_id)
            )
            db.commit()

        return RedirectResponse(url="/filmes", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Erro ao inserir filme: {e}")
        return RedirectResponse(url="/filmes", status_code=303)
    finally:
        db.close()

# --- NOVAS ROTAS DE PERFIL ---

@app.get("/editar-perfil", response_class=HTMLResponse)
async def editar_perfil(request: Request, db=Depends(get_db)):
    user_session = get_current_user(request)
    if not user_session:
        return RedirectResponse(url="/", status_code=303)
    
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Seleciona as colunas conforme o seu script SQL
            cursor.execute("SELECT ID, Nome_Usuario, Email, Tipo FROM Perfil WHERE ID = %s", (user_session["id"],))
            user_data = cursor.fetchone()
    finally:
        db.close()

    return templates.TemplateResponse("editar-perfil.html", {"request": request, "user": user_data})


@app.post("/api/update-profile")
async def update_profile(request: Request, data: dict = Body(...), db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"message": "Não autorizado"})
    
    try:
        with db.cursor() as cursor:
            # Atualiza usando os nomes das colunas do seu banco
            cursor.execute(
                "UPDATE Perfil SET Nome_Usuario = %s WHERE ID = %s",
                (data.get("nome_usuario"), user["id"])
            )
            db.commit()
            
            # Atualiza o token para refletir o novo nome no Header
            new_token = create_access_token({
                "sub": str(user["id"]),
                "nome_usuario": data.get("nome_usuario"),
                "email": user["email"],
                "tipo": user["tipo"],
            })
            request.session["token"] = new_token
            
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()


@app.post("/api/change-password")
async def change_password(request: Request, data: dict = Body(...), db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"message": "Não autorizado"})
    
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT Senha FROM Perfil WHERE ID = %s", (user["id"],))
            result = cursor.fetchone()
            
            if not result or not verify_password(data.get("current_password"), result["Senha"]):
                return JSONResponse(status_code=400, content={"message": "Senha atual incorreta"})
            
            nova_senha_hash = hash_password(data.get("new_password"))
            cursor.execute("UPDATE Perfil SET Senha = %s WHERE ID = %s", (nova_senha_hash, user["id"]))
            db.commit()
            
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()


@app.post("/api/delete-account")
async def delete_account(request: Request, db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"message": "Não autorizado"})
    
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Perfil WHERE ID = %s", (user["id"],))
            db.commit()
        
        request.session.clear()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()

@app.post("/api/upload-avatar")
async def upload_avatar(request: Request, foto: UploadFile = File(...), db=Depends(get_db)):
    # 1. Recupera o usuário logado usando sua função helper
    user_session = get_current_user(request)
    
    if not user_session:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Não autorizado"})
    
    try:
        # 2. Lê os bytes da imagem
        imagem_bytes = await foto.read()
        
        # 3. Atualiza o banco de dados
        with db.cursor() as cursor:
            # Note que usamos 'ID' em maiúsculo conforme seu script SQL
            sql = "UPDATE Perfil SET Foto_Usuario = %s WHERE ID = %s"
            cursor.execute(sql, (imagem_bytes, user_session["id"]))
            db.commit()
            
        return {"status": "success", "message": "Foto atualizada com sucesso!"}
    
    except Exception as e:
        db.rollback()
        print(f"[UPLOAD ERRO]: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        db.close()


@app.get("/editar-perfil", response_class=HTMLResponse)
async def editar_perfil(request: Request, db=Depends(get_db)):
    user_session = get_current_user(request)
    if not user_session:
        return RedirectResponse(url="/", status_code=303)
    
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Adicionei Foto_Usuario no SELECT
            cursor.execute("SELECT ID, Nome_Usuario, Email, Tipo, Foto_Usuario FROM Perfil WHERE ID = %s", (user_session["id"],))
            user_data = cursor.fetchone()
            
            # Converte o BLOB para Base64 se ele existir
            if user_data and user_data["Foto_Usuario"]:
                user_data["Foto_Usuario"] = base64.b64encode(user_data["Foto_Usuario"]).decode('utf-8')
                
    finally:
        db.close()

    return templates.TemplateResponse("editar-perfil.html", {"request": request, "user": user_data})

@app.get("/avatar/{user_id}")
async def get_avatar(user_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT Foto_Usuario FROM Perfil WHERE ID = %s", (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return Response(content=result[0], media_type="image/jpeg")
    # Se não tiver foto, retorna a imagem padrão da sua pasta static
    return RedirectResponse(url="/static/imagens/Usuario.png")