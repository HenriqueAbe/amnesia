import pymysql
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse

from config import get_db
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/avaliar/{filme_id}", name="avaliar_filme")
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
            cursor.execute("""
                INSERT INTO Avaliacao (Filme_ID, Perfil_ID, Nota, Comentario)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Nota           = VALUES(Nota),
                    Comentario     = VALUES(Comentario),
                    Data_Avaliacao = CURRENT_TIMESTAMP
            """, (filme_id, user["id"], nota, comentario))
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"[AVALIAÇÃO] Erro: {e}")
    finally:
        db.close()

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)