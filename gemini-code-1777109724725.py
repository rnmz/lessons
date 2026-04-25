from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


canvas = [["FFFFFF" for _ in range(50)] for _ in range(50)]
connections = []

@app.get("/canvas")
async def get_canvas():
    return canvas

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            # Ждем данные
            data = await websocket.receive_json()
            
            # Обновляем поле
            x, y, color = data["x"], data["y"], data["color"]
            canvas[y][x] = color
            
            # Рассылаем ВСЕМ
            for client in connections:
                try:
                    await client.send_json(data)
                except:
                    continue 
    except WebSocketDisconnect:
        connections.remove(websocket)
