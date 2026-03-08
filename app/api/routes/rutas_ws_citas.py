from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.configuracion import ALGORITHM, SECRET_KEY
from app.core.tiempo_real import gestor_tiempo_real_citas
from app.db.sesion import obtener_db
from app.models.modelo_usuario import User


router = APIRouter(tags=["Appointments WS"])


@router.websocket("/appointments/ws")
async def websocket_citas(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(obtener_db),
):
    try:
        carga = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = carga.get("sub")
        rol = carga.get("role")

        if not email or not rol:
            await websocket.close(code=1008)
            return

        usuario = db.query(User).filter(User.email == email).first()
        if not usuario:
            await websocket.close(code=1008)
            return

        await gestor_tiempo_real_citas.conectar(
            websocket=websocket,
            role=rol,
            email=email,
            programa_academico=usuario.programa_academico,
        )

        while True:
            await websocket.receive_text()
    except (JWTError, WebSocketDisconnect):
        gestor_tiempo_real_citas.desconectar(websocket)
    except Exception:
        gestor_tiempo_real_citas.desconectar(websocket)
        await websocket.close(code=1011)
