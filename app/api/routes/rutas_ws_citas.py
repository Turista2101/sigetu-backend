"""Canal WebSocket para recibir eventos de citas en tiempo real."""

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
    """Autentica socket por JWT y suscribe la conexión al gestor realtime."""
    try:
        carga = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = carga.get("sub")
        rol = carga.get("role")
        device_id = carga.get("device_id")

        if not rol:
            await websocket.close(code=1008)
            return

        if rol != "guest" and not email:
            await websocket.close(code=1008)
            return

        if rol == "guest":
            if not device_id:
                await websocket.close(code=1008)
                return
            await gestor_tiempo_real_citas.conectar(
                websocket=websocket,
                role=rol,
                email=None,
                programa_academico_id=None,
                device_id=device_id,
            )
            while True:
                await websocket.receive_text()
            return

        usuario = db.query(User).filter(User.email == email).first()
        if not usuario:
            await websocket.close(code=1008)
            return

        await gestor_tiempo_real_citas.conectar(
            websocket=websocket,
            role=rol,
            email=email,
            programa_academico_id=usuario.programa.id if usuario.programa else None,
        )

        while True:
            await websocket.receive_text()
    except (JWTError, WebSocketDisconnect):
        gestor_tiempo_real_citas.desconectar(websocket)
    except Exception:
        gestor_tiempo_real_citas.desconectar(websocket)
        await websocket.close(code=1011)
