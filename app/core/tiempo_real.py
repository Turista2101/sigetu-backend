from fastapi import WebSocket


class GestorTiempoRealCitas:
    def __init__(self) -> None:
        self._conexiones: list[dict] = []

    async def conectar(self, websocket: WebSocket, role: str, email: str, programa_academico: str | None) -> None:
        await websocket.accept()
        self._conexiones.append(
            {
                "websocket": websocket,
                "role": role,
                "email": email,
                "programa_academico": programa_academico,
            }
        )

    def desconectar(self, websocket: WebSocket) -> None:
        self._conexiones = [item for item in self._conexiones if item["websocket"] is not websocket]

    async def publicar_evento_cita(self, tipo_evento: str, cita) -> None:
        estudiante = getattr(cita, "student", None)
        programa_estudiante = getattr(estudiante, "programa_academico", None)
        email_estudiante = getattr(estudiante, "email", None)

        carga = {
            "event": tipo_evento,
            "appointment": {
                "id": cita.id,
                "status": cita.status,
                "turn_number": cita.turn_number,
                "student_id": cita.student_id,
                "student_name": getattr(estudiante, "full_name", None),
                "programa_academico": programa_estudiante,
            },
        }

        conexiones_obsoletas = []

        for item in self._conexiones:
            rol = item["role"]
            email = item["email"]
            programa = item["programa_academico"]
            websocket: WebSocket = item["websocket"]

            puede_recibir = False

            if rol == "admin":
                puede_recibir = True
            elif rol == "secretaria" and programa is not None and programa_estudiante == programa:
                puede_recibir = True
            elif rol == "estudiante" and email_estudiante is not None and email == email_estudiante:
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
        conexiones_obsoletas = []
        for item in self._conexiones:
            try:
                await item["websocket"].send_json(mensaje)
            except Exception:
                conexiones_obsoletas.append(item["websocket"])
        for websocket in conexiones_obsoletas:
            self.desconectar(websocket)


gestor_tiempo_real_citas = GestorTiempoRealCitas()
