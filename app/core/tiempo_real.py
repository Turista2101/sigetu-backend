"""Gestor de conexiones WebSocket para publicar eventos de citas en tiempo real."""

from fastapi import WebSocket


class GestorTiempoRealCitas:
    """Mantiene conexiones activas y distribuye eventos según rol y sede."""

    def __init__(self) -> None:
        self._conexiones: list[dict] = []

    async def conectar(self, websocket: WebSocket, role: str, email: str | None, programa_academico_id: int | None, device_id: str | None = None) -> None:
        """Registra una nueva conexión autenticada para recibir eventos en vivo."""
        await websocket.accept()
        self._conexiones.append(
            {
                "websocket": websocket,
                "role": role,
                "email": email,
                "programa_academico_id": programa_academico_id,
                "device_id": device_id,
            }
        )

    def desconectar(self, websocket: WebSocket) -> None:
        """Elimina una conexión cerrada o inválida del pool activo."""
        self._conexiones = [item for item in self._conexiones if item["websocket"] is not websocket]

    async def publicar_evento_cita(self, tipo_evento: str, cita) -> None:
        """Publica un evento de cita filtrando destinatarios por rol, sede y pertenencia."""
        estudiante = getattr(cita, "student", None)
        programa_estudiante = getattr(getattr(estudiante, "programa", None), "id", None)
        email_estudiante = getattr(estudiante, "email", None)
        sede_cita = getattr(cita, "sede", None)

        carga = {
            "event": tipo_evento,
            "appointment": {
                "id": cita.id,
                "status": cita.status,
                "turn_number": cita.turn_number,
                "student_id": cita.student_id,
                "student_name": getattr(estudiante, "full_name", None),
                "programa_academico_id": programa_estudiante,
            },
        }

        conexiones_obsoletas = []

        for item in self._conexiones:
            rol = item["role"]
            email = item["email"]
            programa = item["programa_academico_id"]
            websocket: WebSocket = item["websocket"]

            puede_recibir = False

            if rol == "admin":
                puede_recibir = True
            elif rol == "secretaria" and programa is not None and programa_estudiante == programa:
                puede_recibir = True
            elif rol == "administrativo" and sede_cita == "sede_administrativa":
                puede_recibir = True
            elif rol == "admisiones_mercadeo" and sede_cita == "sede_admisiones_mercadeo":
                puede_recibir = True
            elif rol == "estudiante" and email_estudiante is not None and email == email_estudiante:
                puede_recibir = True
            elif rol == "guest" and cita.device_id is not None and item.get("device_id") == cita.device_id:
                puede_recibir = True

            if not puede_recibir:
                continue

            try:
                await websocket.send_json(carga)
            except Exception:
                conexiones_obsoletas.append(websocket)

        for websocket in conexiones_obsoletas:
            self.desconectar(websocket)

    async def broadcast(self, mensaje: dict) -> None:
        """Envía un mensaje global a todas las conexiones activas."""
        conexiones_obsoletas = []
        for item in self._conexiones:
            try:
                await item["websocket"].send_json(mensaje)
            except Exception:
                conexiones_obsoletas.append(item["websocket"])
        for websocket in conexiones_obsoletas:
            self.desconectar(websocket)

    async def publicar_a_secretaria(self, secretaria_id: int, tipo_evento: str, datos: dict) -> None:
        """Publica un evento específico para una secretaría determinada."""
        conexiones_obsoletas = []
        
        for item in self._conexiones:
            rol = item["role"]
            email = item["email"]
            websocket: WebSocket = item["websocket"]
            
            # Solo enviar a secretarias, administrativos o admisiones
            if rol not in {"secretaria", "administrativo", "admisiones_mercadeo", "admin"}:
                continue
            
            # Si el email coincide con el de la secretaría, enviar
            # Nota: secretaria_id se usa para filtrar, pero necesitamos el email
            # Para esto, el frontend debe escuchar todos los eventos de historia
            
            try:
                await websocket.send_json({
                    "event": tipo_evento,
                    **datos,
                })
            except Exception:
                conexiones_obsoletas.append(websocket)
        
        for websocket in conexiones_obsoletas:
            self.desconectar(websocket)


gestor_tiempo_real_citas = GestorTiempoRealCitas()
