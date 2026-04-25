from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Конфигурация поля
WIDTH, HEIGHT = 50, 50
canvas = [["FFFFFF" for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Менеджер подключений
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Отправка сообщения всем игрокам"""
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.get("/canvas")
async def get_initial_canvas():
    """Отдаем всё поле при первой загрузке страницы"""
    return {"data": canvas}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Ждем данные от клиента (координаты и цвет)
            data = await websocket.receive_json()
            
            x, y, color = data['x'], data['y'], data['color']
            
            # Проверка границ и обновление данных
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                canvas[y][x] = color.upper()
                
                # Рассылаем обновление ВСЕМ
                await manager.broadcast({
                    "x": x,
                    "y": y,
                    "color": color.upper()
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)