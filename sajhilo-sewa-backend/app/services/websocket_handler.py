"""
services/websocket_handler.py
──────────────────────────────
Handles the message loop for each WebSocket connection.

Message types the client can send:
  { "type": "video_frame", "data": "<base64 image>" }
  { "type": "reset_buffer" }
  { "type": "clear_sentence" }
  { "type": "ping" }

Message types the server sends back:
  { "type": "recognition_result", "success": bool, "data": {...}, "sentence": "..." }
  { "type": "pong" }
  { "type": "error", "message": "..." }
  { "type": "connected", "client_id": "...", "gestures": [...] }
"""
from fastapi import WebSocket, WebSocketDisconnect

from app.services.websocket_manager import manager
from app.ml.inference import recognizer, alphabet_recognizer
from app.services.translator import translator_service

class WebSocketHandler:

    async def handle(self, websocket: WebSocket, client_id: str):
        """
        Main loop for one WebSocket connection.

        1. Registers client with ConnectionManager and GestureRecognizer.
        2. Reads JSON messages in a loop.
        3. Dispatches to the appropriate handler method.
        4. Cleans up on disconnect.
        """
        await manager.connect(websocket, client_id)
        recognizer.init_client(client_id)

        # Confirm connection to the client
        await manager.send(client_id, {
            "type":      "connected",
            "client_id": client_id,
            "gestures":  recognizer.gestures,
        })

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "video_frame":
                    await self._handle_frame(data, client_id)

                elif msg_type == "reset_buffer":
                    recognizer.reset_buffer(client_id)
                    await manager.send(client_id, {"type": "buffer_reset"})

                elif msg_type == "clear_sentence":
                    recognizer.clear_sentence(client_id)
                    await manager.send(client_id, {"type": "sentence_cleared", "sentence": "", "nepali_sentence": ""})

                elif msg_type == "ping":
                    await manager.send(client_id, {"type": "pong"})

                else:
                    await manager.send(client_id, {
                        "type":    "error",
                        "message": f"Unknown message type: {msg_type}",
                    })

        except WebSocketDisconnect:
            pass   # normal close
        except Exception as e:
            print(f"❌ WebSocket error [{client_id}]: {e}")
            try:
                await manager.send(client_id, {"type": "error", "message": str(e)})
            except Exception:
                pass
        finally:
            manager.disconnect(client_id)
            recognizer.remove_client(client_id)

    async def _handle_frame(self, data: dict, client_id: str):
        """Process one video frame and send the prediction result."""
        frame_data = data.get("data")
        if not frame_data:
            await manager.send(client_id, {
                "type": "error", "message": "Empty frame data."
            })
            return

        result = recognizer.process_frame(client_id, frame_data)
        
        # Add translation to the results
        gesture = result.get("gesture", "")
        sentence = result.get("sentence", "")
        
        # Only translate if there's actually a gesture
        nepali_gesture = translator_service.translate(gesture) if gesture else ""
        nepali_sentence = translator_service.translate(sentence) if sentence else ""

        await manager.send(client_id, {
            "type":    "recognition_result",
            "success": result.get("success", False),
            "sentence": sentence,
            "nepali_sentence": nepali_sentence,
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

    async def handle_alphabet(self, websocket: WebSocket, client_id: str):
        """WebSocket loop for single-alphabet recognition."""
        await manager.connect(websocket, client_id)
        alphabet_recognizer.init_client(client_id)
        await manager.send(client_id, {"type": "connected", "client_id": client_id, "mode": "alphabet"})
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "video_frame":
                    res = alphabet_recognizer.process_frame(client_id, data.get("data"))
                    
                    gesture = res.get("gesture", "")
                    sentence = res.get("sentence", "")
                    
                    # Translate
                    nepali_gesture = translator_service.translate(gesture) if gesture else ""
                    nepali_sentence = translator_service.translate(sentence) if sentence else ""
                    
                    await manager.send(client_id, {
                        "type": "recognition_result",
                        "success": res.get("success"),
                        "sentence": sentence,
                        "nepali_sentence": nepali_sentence,
                        "data": {
                            "gesture": gesture,
                            "nepali": nepali_gesture,
                            "confidence": res.get("confidence")
                        }
                    })
                elif data.get("type") == "clear_sentence":
                    alphabet_recognizer.clear_sentence(client_id)
                    await manager.send(client_id, {"type": "sentence_cleared"})
        except WebSocketDisconnect: pass
        finally:
            manager.disconnect(client_id)
            alphabet_recognizer.remove_client(client_id)


# Shared singleton
ws_handler = WebSocketHandler()