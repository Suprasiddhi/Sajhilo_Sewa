"""
routers/ml.py
──────────────
REST API endpoints for the ML subsystem.

Endpoints:
  GET  /api/ml/status        → model status, gestures list, connected WS clients
  POST /api/ml/train         → trigger training pipeline (background task)
  POST /api/ml/process-videos→ extract keypoints from video folder
  POST /api/ml/predict       → single-image prediction (upload file)
  POST /api/ml/predict-base64→ single-frame prediction (base64 from webcam)
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
import io
import numpy as np
from PIL import Image

from app.ml.inference import recognizer
from app.ml.dataset   import process_video_dataset, load_gestures_from_summary
from app.ml.train     import run_train
from app.auth_utils import get_current_user   # your existing auth guard
from app.ml.config import WEIGHTS_DIR
import os
import json

router = APIRouter()


# ── GET /api/ml/status ────────────────────────────────────────────────────────
@router.get("/status", summary="ML system status")
async def ml_status(_=Depends(get_current_user)):
    from app.services.websocket_manager import manager
    return {
        "models_loaded": recognizer.ensemble is not None,
        "device":        str(recognizer.device),
        "gestures":      recognizer.gestures,
        "num_classes":   recognizer.num_classes,
        "ws_clients":    manager.connected_count,
    }


# ── GET /api/ml/analysis ──────────────────────────────────────────────────────
@router.get("/analysis", summary="Get model performance analysis")
async def get_model_analysis(_=Depends(get_current_user)):
    """
    Reads history JSON files from WEIGHTS_DIR and returns the best 
    validation accuracy for each model, plus ensemble info.
    """
    analysis = {}
    
    files = {
        "TCN": "tcn_best_history.json",
        "BiLSTM": "bilstm_best_history.json",
        "ST-GCN": "stgcn_best_history.json",
        "Alphabet": "alphabet_best_history.json"
    }
    
    for model_name, filename in files.items():
        path = os.path.join(WEIGHTS_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                history = json.load(f)
                # Take the max val_acc
                max_acc = max(history.get("val_acc", [0]))
                analysis[model_name] = {
                    "accuracy": round(max_acc * 100, 2),
                    "epochs": len(history.get("epoch", [])),
                    "training_complete": True
                }
        else:
            analysis[model_name] = {
                "accuracy": 0,
                "epochs": 0,
                "training_complete": False
            }

    # Ensemble weights
    ensemble_path = os.path.join(WEIGHTS_DIR, "ensemble_weights.json")
    if os.path.exists(ensemble_path):
        with open(ensemble_path, 'r') as f:
            ensemble_data = json.load(f)
            analysis["Ensemble"] = {
                "weights": ensemble_data.get("weights", []),
                "gestures_count": len(ensemble_data.get("gestures", []))
            }

    return analysis


# ── POST /api/ml/process-videos ───────────────────────────────────────────────
@router.post("/process-videos", summary="Extract keypoints from VIDEO_ROOT")
async def process_videos(
    background_tasks: BackgroundTasks,
    _=Depends(get_current_user),
):
    """
    Kicks off keypoint extraction in the background so the HTTP response
    returns immediately.  Check logs for progress.
    """
    def _run():
        try:
            process_video_dataset()
        except Exception as e:
            print(f"❌ process_video_dataset failed: {e}")

    background_tasks.add_task(_run)
    return {"message": "Video processing started in background. Check server logs."}


# ── POST /api/ml/train ────────────────────────────────────────────────────────
@router.post("/train", summary="Train TCN + BiLSTM + ST-GCN")
async def train_models(
    background_tasks: BackgroundTasks,
    _=Depends(get_current_user),
):
    """
    Triggers the full training pipeline as a background task.
    Training typically takes 5–30 minutes depending on dataset size.
    """
    gestures = load_gestures_from_summary()
    if not gestures:
        raise HTTPException(
            status_code=400,
            detail="No dataset found. Run /api/ml/process-videos first.",
        )

    def _run():
        try:
            run_train(gestures)
            # Reload the ensemble after training
            recognizer.ensemble  = recognizer._load_ensemble()
            recognizer.gestures  = recognizer._load_gesture_list()
            recognizer.num_classes = len(recognizer.gestures)
            print("✅ Models reloaded after training.")
        except Exception as e:
            print(f"❌ Training failed: {e}")

    background_tasks.add_task(_run)
    return {"message": "Training started in background. Check server logs for progress."}


# ── POST /api/ml/predict (file upload) ────────────────────────────────────────
class _TempClient:
    """Temporary single-frame client for REST predictions."""
    ID = "__rest_client__"

@router.post("/predict", summary="Predict gesture from uploaded image")
async def predict_image(
    file: UploadFile = File(...),
    _=Depends(get_current_user),
):
    contents = await file.read()
    pil_img  = Image.open(io.BytesIO(contents)).convert("RGB")
    frame    = np.array(pil_img)

    recognizer.reset_buffer(_TempClient.ID)
    # Feed 30 copies of the same frame to fill the buffer instantly
    result = None
    for _ in range(30):
        result = recognizer.process_frame(_TempClient.ID, frame)
    recognizer.remove_client(_TempClient.ID)
    return result


# ── POST /api/ml/predict-base64 ───────────────────────────────────────────────
class Base64Request(BaseModel):
    image: str   # base64 string, optionally with data URL prefix

@router.post("/predict-base64", summary="Predict gesture from base64 frame")
async def predict_base64(body: Base64Request, _=Depends(get_current_user)):
    recognizer.reset_buffer(_TempClient.ID)
    result = None
    for _ in range(30):
        result = recognizer.process_frame(_TempClient.ID, body.image)
    recognizer.remove_client(_TempClient.ID)
    return result