import pymysql
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config import get_db
from core.security import hash_password, verify_password, create_access_token
from core.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/filmes", status_code=303)

    return templates.TemplateResponse("loginecadastro.html", {
        "request":          request,
        "erro_login":       request.session.pop("erro_login", None),
        "erro_cadastro":    request.session.pop("erro_cadastro", None),
        "sucesso_cadastro": request.session.pop("sucesso_cadastro", None),
        "form_nome":        request.session.pop("form_nome", ""),
        "form_email":       request.session.pop("form_email", ""),
        "form_data":        request.session.pop("form_data", ""),
    })


@router.post("/cadastro", name="cadastro")
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
        request.session["form_nome"]     = nome_usuario
        request.session["form_email"]    = email
        request.session["form_data"]     = data_de_nascimento
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT ID FROM USUARIO WHERE Email = %s", (email,))
            if cursor.fetchone():
                return salvar_e_redirecionar("Este e-mail já está cadastrado.")

            cursor.execute(
                "INSERT INTO USUARIO (Nome_Usuario, Email, Senha, Tipo) VALUES (%s, %s, %s, 'USER')",
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


@router.post("/login", name="login")
async def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db=Depends(get_db),
):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT ID, Nome_Usuario, Email, Senha, Tipo FROM USUARIO WHERE Email = %s",
                (email,),
            )
            user = cursor.fetchone()

        if not user or not verify_password(senha, user["Senha"]):
            request.session["erro_login"] = "E-mail ou senha incorretos."
            return RedirectResponse(url="/", status_code=303)

        token = create_access_token({
            "sub":          str(user["ID"]),
            "nome_usuario": user["Nome_Usuario"],
            "email":        user["Email"],
            "tipo":         user["Tipo"],
        })
        request.session["token"] = token
        return RedirectResponse(url="/filmes", status_code=303)

    except Exception as e:
        request.session["erro_login"] = f"Erro interno: {str(e)}"
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()


@router.get("/logout", name="logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)