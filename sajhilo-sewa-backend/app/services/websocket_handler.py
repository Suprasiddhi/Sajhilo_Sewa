"""
services/websocket_handler.py
──────────────────────────────
Handles the message loop for each WebSocket connection.
Includes authentication and session-end database commits.
"""
from fastapi import WebSocket, WebSocketDisconnect

from app.services.websocket_manager import manager
from app.ml.inference import recognizer, alphabet_recognizer
from app.services.translator import translator_service
from app.database import SessionLocal
from app.auth_utils import decode_token

class WebSocketHandler:
    def __init__(self):
        # Maps client_id to database user_id after auth
        self._user_ids: dict[str, int] = {}

    async def handle(self, websocket: WebSocket, client_id: str):
        """Main loop for full-gesture recognition."""
        await manager.connect(websocket, client_id)
        recognizer.init_client(client_id)

        await manager.send(client_id, {
            "type":      "connected",
            "client_id": client_id,
            "gestures":  recognizer.gestures,
        })

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "auth":
                    token = data.get("token")
                    payload = decode_token(token) if token else None
                    if payload and payload.get("sub"):
                        self._user_ids[client_id] = int(payload["sub"])
                        print(f"🔐 Client {client_id} authenticated as User {self._user_ids[client_id]}")
                        await manager.send(client_id, {"type": "auth_success", "user_id": self._user_ids[client_id]})
                    else:
                        print(f"❌ Auth failed for client {client_id}")
                        await manager.send(client_id, {"type": "error", "message": "Invalid token."})

                elif msg_type == "video_frame":
                    await self._handle_frame(data, client_id)

                elif msg_type == "reset_buffer":
                    recognizer.reset_buffer(client_id)
                    await manager.send(client_id, {"type": "buffer_reset"})

                elif msg_type == "clear_sentence":
                    recognizer.clear_sentence(client_id)
                    await manager.send(client_id, {"type": "sentence_cleared", "sentence": "", "nepali_sentence": ""})

                elif msg_type == "ping":
                    await manager.send(client_id, {"type": "pong"})

        except WebSocketDisconnect: pass
        finally:
            manager.disconnect(client_id)
            recognizer.remove_client(client_id)
            self._user_ids.pop(client_id, None)

    async def _handle_frame(self, data: dict, client_id: str):
        """Inference wrapper for GestureRecognizer."""
        frame_data = data.get("data")
        if not frame_data: return

        result = recognizer.process_frame(client_id, frame_data)
        gesture = result.get("gesture", "")
        sentence = result.get("sentence", "")
        
        nepali_gesture = translator_service.translate(gesture) if gesture else ""
        nepali_sentence = translator_service.translate(sentence) if sentence else ""

        await manager.send(client_id, {
            "type":    "recognition_result",
            "success": result.get("success", False),
            "sentence": sentence,
            "nepali_sentence": nepali_sentence,
            "is_final": result.get("is_final", False),
            "data":    {
                "gesture":         gesture,
                "nepali":          nepali_gesture,
                "confidence":      result.get("confidence"),
                "all_probs":       result.get("all_probs"),
                "model_votes":     result.get("model_votes"),
                "buffer_progress": result.get("buffer_progress"),
            },
            "message":         result.get("message", ""),
            "buffer_progress": result.get("buffer_progress", "0/30"),
        })

        # ── END COMMIT LOGIC REMOVED ──────────────────────────
        pass

    async def handle_alphabet(self, websocket: WebSocket, client_id: str):
        """Main loop for alphabet recognition."""
        await manager.connect(websocket, client_id)
        alphabet_recognizer.init_client(client_id)
        await manager.send(client_id, {
            "type": "connected", 
            "client_id": client_id, 
            "mode": "alphabet",
            "message": "Alphabet recognition active."
        })
        
        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "auth":
                    token = data.get("token")
                    payload = decode_token(token) if token else None
                    if payload and payload.get("sub"):
                        self._user_ids[client_id] = int(payload["sub"])
                        print(f"🔐 Client {client_id} (Alphabet) authenticated as User {self._user_ids[client_id]}")
                        await manager.send(client_id, {"type": "auth_success", "user_id": self._user_ids[client_id]})

                elif msg_type == "video_frame":
                    res = alphabet_recognizer.process_frame(client_id, data.get("data"))
                    gesture = res.get("gesture", "")
                    sentence = res.get("sentence", "")
                    
                    nepali_gesture = translator_service.translate(gesture) if gesture else ""
                    nepali_sentence = translator_service.translate(sentence) if sentence else ""
                    
                    await manager.send(client_id, {
                        "type": "recognition_result",
                        "success": res.get("success"),
                        "sentence": sentence,
                        "nepali_sentence": nepali_sentence,
                        "is_final": res.get("is_final", False),
                        "data": {
                            "gesture": gesture,
                            "nepali": nepali_gesture,
                            "confidence": res.get("confidence")
                        }
                    })

                    # ── END COMMIT LOGIC (ALPHABET) REMOVED ───────────
                    pass

                elif msg_type == "clear_sentence":
                    alphabet_recognizer.clear_sentence(client_id)
                    await manager.send(client_id, {"type": "sentence_cleared", "sentence": ""})

        except WebSocketDisconnect: pass
        finally:
            manager.disconnect(client_id)
            alphabet_recognizer.remove_client(client_id)
            self._user_ids.pop(client_id, None)

# Shared singleton
ws_handler = WebSocketHandler()