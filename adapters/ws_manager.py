from fastapi import WebSocket

class ChatConnectionManager:
    def __init__(self):
        # Структура: { order_id: [WebSocket, WebSocket] }
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, order_id: int):
        # Обязательно принимаем соединение
        await websocket.accept()

        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append(websocket)

    def disconnect(self, websocket: WebSocket, order_id: int):
        if order_id in self.active_connections:
            self.active_connections[order_id].remove(websocket)
            # Очищаем память, если комната опустела
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]

    async def broadcast_to_order(self, order_id: int, message: dict):
        # Идем по всем вебсокетам в комнате и шлем им JSON
        if order_id in self.active_connections:
            for connection in self.active_connections[order_id]:
                await connection.send_json(message)

chat_manager = ChatConnectionManager()