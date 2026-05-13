import pymysql
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config import get_db
from core.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", name="dashboard") 
async def dashboard_admin(request: Request, db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        request.session["erro_login"] = "Faça login para acessar."
        return RedirectResponse(url="/", status_code=303)

    tipo_usuario = user.get("Tipo") or user.get("tipo")
    if tipo_usuario != "ADMIN":
        return RedirectResponse(url="/filmes", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT COUNT(ID) AS total FROM Usuario")
            res_user = cursor.fetchone()
            total_usuarios = res_user["total"] if res_user else 0

            cursor.execute("SELECT COUNT(ID) AS total FROM Filme")
            res_filme = cursor.fetchone()
            total_filmes = res_filme["total"] if res_filme else 0

            cursor.execute("""
                SELECT ID, Nome_Usuario, Email, Tipo, 
                       DATE_FORMAT(Data_Cadastro, '%d/%m/%Y') AS Data_Formatada
                FROM Usuario 
                ORDER BY Data_Cadastro DESC 
                LIMIT 5
            """)
            usuarios_recentes = cursor.fetchall()

    finally:
        db.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "total_usuarios": total_usuarios,
        "total_filmes": total_filmes,
        "usuarios_recentes": usuarios_recentes
    })