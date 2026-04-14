import pymysql
import base64

from mangum import Mangum
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import date, datetime
from db import get_db

app = FastAPI()

# Configuração de sessão
app.add_middleware(
    SessionMiddleware,
    secret_key="amnesia",
    session_cookie="amnesia_session",
    max_age=50000,
    same_site="lax",
    https_only=False
)

# Configuração de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuração de templates Jinja2
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("loginecadastro.html", {
        "request": request
    })


@app.get("/medListar", name="medListar", response_class=HTMLResponse)
async def listar_medicos(request: Request, db=Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = """
              SELECT M.ID_Medico, \
                     M.CRM, \
                     M.Nome, \
                     E.Nome_Espec AS Especialidade,
                     M.Foto, \
                     M.Dt_Nasc
              FROM Medico AS M
                       JOIN Especialidade AS E ON M.fk_ID_Espec = E.ID_Espec
              ORDER BY M.Nome; \
              """
        cursor.execute(sql)
        medicos = cursor.fetchall()

    hoje = date.today()
    for med in medicos:
        dt_nasc = med["Dt_Nasc"]
        if isinstance(dt_nasc, str):
            ano, mes, dia = map(int, dt_nasc.split("-"))
            dt_nasc = date(ano, mes, dia)

        idade = hoje.year - dt_nasc.year
        if (dt_nasc.month, dt_nasc.day) > (hoje.month, hoje.day):
            idade -= 1
        med["idade"] = idade

        if med["Foto"]:
            med["Foto_base64"] = base64.b64encode(med["Foto"]).decode('utf-8')
        else:
            med["Foto_base64"] = None

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return templates.TemplateResponse("medListar.html", {
        "request": request,
        "medicos": medicos,
        "hoje": agora
    })


# CORREÇÃO: Adicionado name="medIncluir" para o url_for funcionar
@app.get("/medIncluir", name="medIncluir", response_class=HTMLResponse)
async def med_incluir(request: Request, db=Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT ID_Espec, Nome_Espec FROM Especialidade")
        especialidades = cursor.fetchall()
    db.close()

    nome_usuario = request.session.get("nome_usuario", None)
    perfil = request.session.get("perfil", None)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse("medIncluir.html", {
        "request": request,
        "especialidades": especialidades,
        "hoje": agora,
        "nome_usuario": nome_usuario,
        "perfil": perfil
    })


@app.post("/medIncluir_exe", name="medIncluir_exe")
async def med_incluir_exe(
        request: Request,
        Nome: str = Form(...),
        CRM: str = Form(...),
        Especialidade: str = Form(...),
        DataNasc: str = Form(None),
        Imagem: UploadFile = File(None),
        db=Depends(get_db)
):
    foto_bytes = None
    if Imagem and Imagem.filename:
        foto_bytes = await Imagem.read()

    try:
        with db.cursor() as cursor:
            sql = """INSERT INTO Medico (Nome, CRM, fk_ID_Espec, Dt_Nasc, Foto)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (Nome, CRM, Especialidade, DataNasc, foto_bytes))
            db.commit()

        request.session["mensagem_header"] = "Inclusão de Novo Médico"
        request.session["mensagem"] = "Registro cadastrado com sucesso!"
    except Exception as e:
        request.session["mensagem_header"] = "Erro ao cadastrar"
        request.session["mensagem"] = str(e)
    finally:
        db.close()

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return templates.TemplateResponse("medIncluir_exe.html", {
        "request": request,
        "mensagem_header": request.session.get("mensagem_header", ""),
        "mensagem": request.session.get("mensagem", ""),
        "hoje": agora
    })


@app.get("/medExcluir", name="medExcluir", response_class=HTMLResponse)
async def med_excluir(request: Request, id: int, db=Depends(get_db)):
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        sql = ("SELECT M.ID_Medico, M.Nome, M.CRM, M.Dt_Nasc, E.Nome_Espec "
               "FROM Medico M JOIN Especialidade E ON M.fk_ID_Espec = E.ID_Espec "
               "WHERE M.ID_Medico = %s")
        cursor.execute(sql, (id,))
        medico = cursor.fetchone()
    db.close()

    data_nasc = medico["Dt_Nasc"]
    if isinstance(data_nasc, str):
        ano, mes, dia = data_nasc.split("-")
    else:
        ano, mes, dia = data_nasc.year, f"{data_nasc.month:02d}", f"{data_nasc.day:02d}"
    data_formatada = f"{dia}/{mes}/{ano}"

    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

    return templates.TemplateResponse("medExcluir.html", {
        "request": request,
        "med": medico,
        "data_formatada": data_formatada,
        "hoje": hoje
    })


@app.post("/medExcluir_exe", name="medExcluir_exe")
async def med_excluir_exe(request: Request, id: int = Form(...), db=Depends(get_db)):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_delete = "DELETE FROM Medico WHERE ID_Medico = %s"
            cursor.execute(sql_delete, (id,))
            db.commit()

            request.session["mensagem_header"] = "Exclusão de Médico"
            request.session["mensagem"] = f"Médico excluído com sucesso."
    except Exception as e:
        request.session["mensagem_header"] = "Erro ao excluir"
        request.session["mensagem"] = str(e)
    finally:
        db.close()

    return templates.TemplateResponse("medExcluir_exe.html", {
        "request": request,
        "mensagem_header": request.session.get("mensagem_header", ""),
        "mensagem": request.session.get("mensagem", ""),
        "hoje": datetime.now().strftime("%d/%m/%Y %H:%M")
    })