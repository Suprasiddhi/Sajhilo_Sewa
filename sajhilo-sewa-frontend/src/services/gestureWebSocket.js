// src/services/gestureWebSocket.js
// ──────────────────────────────────
// WebSocket service for real-time ASL gesture recognition.
// Connect once per recognition session, send frames at ~15 FPS.

class GestureWebSocket {
    constructor() {
        this.ws = null;
        this.clientId = null;
        this.onResult = null;      // callback(result)
        this.onStatus = null;      // callback(statusMessage)
        this.onConnected = null;   // callback(gestures[])
        this.frameInterval = null;
    }

    // ── Connect ────────────────────────────────────────────────────────────────
    connect(clientId) {
        const url = `ws://localhost:8000/ws/recognition/${clientId}`;
        this.clientId = clientId;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log("✅ WebSocket connected");
        };

        this.ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            this._handleMessage(msg);
        };

        this.ws.onerror = (err) => {
            console.error("❌ WebSocket error", err);
        };

        this.ws.onclose = () => {
            console.log("WebSocket disconnected");
            this.stopCapture();
        };
    }

    // ── Send one frame ─────────────────────────────────────────────────────────
    sendFrame(base64Image) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: "video_frame",
                data: base64Image,
                timestamp: Date.now(),
            }));
        }
    }

    // ── Start capturing from a <video> element ────────────────────────────────
    // videoRef = React ref to <video> element
    // fps      = frames per second to capture (default 15)
    startCapture(videoRef, fps = 15) {
        const canvas = document.createElement("canvas");
        const interval = Math.round(1000 / fps);

        this.frameInterval = setInterval(() => {
            const video = videoRef.current;
            if (!video || video.readyState < 2) return;

            // Manually scale to 640x480 for consistent performance
            canvas.width = 640;
            canvas.height = 480;
            canvas.getContext("2d").drawImage(video, 0, 0, 640, 480);

            // JPEG at 0.5 quality = smaller payload, faster network transfer
            const base64 = canvas.toDataURL("image/jpeg", 0.5);
            this.sendFrame(base64);
        }, interval);
    }

    stopCapture() {
        if (this.frameInterval) {
            clearInterval(this.frameInterval);
            this.frameInterval = null;
        }
    }

    // ── Reset the server-side frame buffer ────────────────────────────────────
    resetBuffer() {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: "reset_buffer" }));
        }
    }

    // ── Disconnect ────────────────────────────────────────────────────────────
    disconnect() {
        this.stopCapture();
        this.ws?.close();
        this.ws = null;
    }

    // ── Internal message router ───────────────────────────────────────────────
    _handleMessage(msg) {
        switch (msg.type) {
            case "connected":
                console.log("Server gestures:", msg.gestures);
                this.onConnected?.(msg.gestures);
                break;

            case "recognition_result":
                if (msg.success && this.onResult) {
                    this.onResult({
                        gesture: msg.data.gesture,
                        confidence: msg.data.confidence,
                        allProbs: msg.data.all_probs,
                        modelVotes: msg.data.model_votes,
                        bufferProgress: msg.data.buffer_progress,
                    });
                } else if (!msg.success && this.onStatus) {
                    this.onStatus(msg.message || "…");
                }
                break;

            case "pong":
                // keep-alive acknowledged
                break;

            case "error":
                console.error("Server error:", msg.message);
                break;

            default:
                break;
        }
    }
}

export default new GestureWebSocket();