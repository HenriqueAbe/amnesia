import pymysql
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config import get_db
from core.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/meus_filmes", name="meus_filmes", response_class=HTMLResponse)
async def listar_meus_filmes(request: Request, db=Depends(get_db)):
    user = get_current_user(request)
    
    if not user:
        request.session["erro_login"] = "Faça login para acessar."
        return RedirectResponse(url="/", status_code=303)

    user_id = user.get("ID") or user.get("id")

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    f.ID,
                    f.Titulo,
                    f.Capa_URL,
                    a.Nota,
                    IF(a.Nota IS NOT NULL, 'assistido', 'quero') AS Status
                FROM Lista_Usuario lu
                JOIN Filme f ON lu.Filme_ID = f.ID
                LEFT JOIN Avaliacao a ON f.ID = a.Filme_ID AND a.Usuario_ID = lu.Usuario_ID
                WHERE lu.Usuario_ID = %s
                ORDER BY lu.Data_Adicao DESC
            """, (user_id,))
            
            filmes = cursor.fetchall()
            
    finally:
        db.close()

    return templates.TemplateResponse("meus_filmes.html", {
        "request": request,
        "user": user,
        "filmes": filmes,
        "total_filmes": len(filmes)
    })