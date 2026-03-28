"""
services/websocket_manager.py
──────────────────────────────
Tracks all active WebSocket connections in a simple in-memory dictionary.

Responsibilities:
  - accept()  a new WebSocket and register it by client_id
  - disconnect() and unregister when a client leaves
  - send JSON messages back to a specific client
"""
from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        # Maps client_id → WebSocket object
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept the WebSocket handshake and register the connection."""
        await websocket.accept()
        self.active[client_id] = websocket
        print(f"✅ WS client connected: {client_id}  (total: {len(self.active)})")

    def disconnect(self, client_id: str):
        """Remove a client from the registry."""
        self.active.pop(client_id, None)
        print(f"❌ WS client disconnected: {client_id}  (total: {len(self.active)})")

    async def send(self, client_id: str, message: dict):
        """Send a JSON message to a specific client (no-op if not connected)."""
        ws = self.active.get(client_id)
        if ws:
            await ws.send_json(message)

    @property
    def connected_count(self) -> int:
        return len(self.active)


# Shared singleton — imported by both the router and the handler
manager = ConnectionManager()