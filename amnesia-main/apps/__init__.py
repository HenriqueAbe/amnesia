import base64
import pymysql
from fastapi import APIRouter, Request, File, UploadFile, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from config import get_db
from core.security import verify_password, hash_password, create_access_token
from core.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/editar-perfil", response_class=HTMLResponse)
async def editar_perfil(request: Request, db=Depends(get_db)):
    user_session = get_current_user(request)
    if not user_session:
        return RedirectResponse(url="/", status_code=303)

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT ID, Nome_Usuario, Email, Tipo, Foto_Usuario FROM Perfil WHERE ID = %s",
                (user_session["id"],),
            )
            user_data = cursor.fetchone()

            if user_data and user_data["Foto_Usuario"]:
                user_data["Foto_Usuario"] = base64.b64encode(
                    user_data["Foto_Usuario"]
                ).decode("utf-8")
    finally:
        db.close()

    return templates.TemplateResponse("editar-perfil.html", {
        "request": request,
        "user":    user_data,
    })


@router.post("/api/update-profile")
async def update_profile(
    request: Request,
    data: dict = Body(...),
    db=Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"message": "Não autorizado"})

    try:
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE Perfil SET Nome_Usuario = %s WHERE ID = %s",
                (data.get("nome_usuario"), user["id"]),
            )
            db.commit()

        new_token = create_access_token({
            "sub":          str(user["id"]),
            "nome_usuario": data.get("nome_usuario"),
            "email":        user["email"],
            "tipo":         user["tipo"],
        })
        request.session["token"] = new_token
        return {"status": "success"}

    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()


@router.post("/api/change-password")
async def change_password(
    request: Request,
    data: dict = Body(...),
    db=Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"message": "Não autorizado"})

    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT Senha FROM Perfil WHERE ID = %s", (user["id"],))
            result = cursor.fetchone()

            if not result or not verify_password(data.get("current_password"), result["Senha"]):
                return JSONResponse(status_code=400, content={"message": "Senha atual incorreta"})

            cursor.execute(
                "UPDATE Perfil SET Senha = %s WHERE ID = %s",
                (hash_password(data.get("new_password")), user["id"]),
            )
            db.commit()

        return {"status": "success"}

    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        db.close()


@router.post("/api/delete-account")
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


@router.post("/api/upload-avatar")
async def upload_avatar(
    request: Request,
    foto: UploadFile = File(...),
    db=Depends(get_db),
):
    user_session = get_current_user(request)
    if not user_session:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Não autorizado"})

    try:
        imagem_bytes = await foto.read()

        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE Perfil SET Foto_Usuario = %s WHERE ID = %s",
                (imagem_bytes, user_session["id"]),
            )
            db.commit()

        return {"status": "success", "message": "Foto atualizada com sucesso!"}

    except Exception as e:
        db.rollback()
        print(f"[UPLOAD ERRO]: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        db.close()


@router.get("/avatar/{user_id}")
async def get_avatar(user_id: int, db=Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT Foto_Usuario FROM Perfil WHERE ID = %s", (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return Response(content=result[0], media_type="image/jpeg")

    return RedirectResponse(url="/static/imagens/Usuario.png")