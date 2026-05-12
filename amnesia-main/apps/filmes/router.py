import pymysql
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config import get_db
from core.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/filmes", name="filmes", response_class=HTMLResponse)
async def listar_filmes(request: Request, db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        request.session["erro_login"] = "Faça login para acessar."
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
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
            """)
            filmes = cursor.fetchall()
    finally:
        db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user":    user,
        "filmes":  filmes,
        "hoje":    datetime.now().strftime("%d/%m/%Y %H:%M"),
    })


@router.get("/filmes/{filme_id}", name="detalhe_filme", response_class=HTMLResponse)
async def detalhe_filme(request: Request, filme_id: int, db=Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT
                    f.*,
                    d.Nome AS Diretor,
                    ROUND(AVG(a.Nota), 1) AS Nota_Media
                FROM Filme f
                LEFT JOIN Diretor d ON f.Diretor_ID = d.ID
                LEFT JOIN Avaliacao a ON f.ID = a.Filme_ID
                WHERE f.ID = %s
                GROUP BY f.ID
            """, (filme_id,))
            filme = cursor.fetchone()

            if not filme:
                return RedirectResponse(url="/filmes", status_code=303)

            cursor.execute("""
                SELECT g.Nome FROM Genero g
                JOIN Filme_Genero fg ON g.ID = fg.Genero_ID
                WHERE fg.Filme_ID = %s
            """, (filme_id,))
            generos = [row["Nome"] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT aa.Nome FROM Ator_Atriz aa
                JOIN Filme_Ator fa ON aa.ID = fa.Ator_ID
                WHERE fa.Filme_ID = %s
            """, (filme_id,))
            atores = [row["Nome"] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT
                    p.Nome_Usuario,
                    a.Nota,
                    a.Comentario,
                    DATE_FORMAT(a.Data_Avaliacao, '%%d/%%m/%%Y') AS Data
                FROM Avaliacao a
                JOIN Perfil p ON a.Perfil_ID = p.ID
                WHERE a.Filme_ID = %s
                ORDER BY a.Data_Avaliacao DESC
            """, (filme_id,))
            avaliacoes = cursor.fetchall()
    finally:
        db.close()

    return templates.TemplateResponse("filmes.html", {
        "request":    request,
        "user":       user,
        "filme":      filme,
        "generos":    generos,
        "atores":     atores,
        "avaliacoes": avaliacoes,
    })


@router.post("/adicionar-filme")
async def adicionar_filme(
    request: Request,
    titulo: str = Form(...),
    ano: int = Form(...),
    diretor_nome: str = Form(...),
    capa_url: str = Form(...),
    sinopse: str = Form(""),
    db=Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT ID FROM Diretor WHERE Nome = %s", (diretor_nome,))
            diretor = cursor.fetchone()

            if diretor:
                diretor_id = diretor["ID"]
            else:
                cursor.execute("INSERT INTO Diretor (Nome) VALUES (%s)", (diretor_nome,))
                diretor_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO Filme (Titulo, Sinopse, Ano_Lancamento, Capa_URL, Diretor_ID)
                VALUES (%s, %s, %s, %s, %s)
            """, (titulo, sinopse, ano, capa_url, diretor_id))
            db.commit()

        return RedirectResponse(url="/filmes", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Erro ao inserir filme: {e}")
        return RedirectResponse(url="/filmes", status_code=303)
    finally:
        db.close()