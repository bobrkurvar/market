from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    @staticmethod
    def _order_room(order_id: int) -> str:
        return f"order:{order_id}"

    @staticmethod
    def _dispute_room(dispute_id: int) -> str:
        return f"dispute:{dispute_id}"

    async def _connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        self.active_connections[room_id].append(websocket)

    def _disconnect(self, websocket: WebSocket, room_id: str):
        connections = self.active_connections.get(room_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.active_connections[room_id]

    async def _broadcast(self, room_id: str, message: dict):
        for connection in self.active_connections.get(room_id, []):
            await connection.send_json(message)

    async def connect_to_order(self, websocket: WebSocket, order_id: int):
        await self._connect(websocket, self._order_room(order_id))

    def disconnect_from_order(self, websocket: WebSocket, order_id: int):
        self._disconnect(websocket, self._order_room(order_id))

    async def broadcast_to_order(self, order_id: int, message: dict):
        await self._broadcast(self._order_room(order_id), message)

    async def connect_to_dispute(self, websocket: WebSocket, dispute_id: int):
        await self._connect(websocket, self._dispute_room(dispute_id))

    def disconnect_from_dispute(self, websocket: WebSocket, dispute_id: int):
        self._disconnect(websocket, self._dispute_room(dispute_id))

    async def broadcast_to_dispute(self, dispute_id: int, message: dict):
        await self._broadcast(self._dispute_room(dispute_id), message)


chat_manager = ChatConnectionManager()