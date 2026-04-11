"""
ml/config.py
────────────
Central configuration for the entire ML pipeline.
Every other file imports from here — never hardcode values elsewhere.
"""
import os
import torch

# ── Paths ─────────────────────────────────────────────────────────────────────

# Root of the backend project (the folder that contains app/ and videos/)
# Current file is at app/ml/config.py, so we go up 3 levels.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Where your training videos live.
VIDEO_ROOT = os.path.join(BASE_DIR, "videos", "gestures")

# Where extracted .npy keypoint sequences will be saved
DATA_DIR = os.path.join(BASE_DIR, "app", "data")

# Where trained model weights (.pth) are saved/loaded
WEIGHTS_DIR = os.path.join(BASE_DIR, "app", "ml", "saved_models")

# ── Gesture classes ───────────────────────────────────────────────────────────
# Must match the subfolder names inside VIDEO_ROOT exactly
GESTURES = [
    "bathroom", "bill", "bottle", "clean", "coffee", "cold", "food",
    "hello", "hot", "i", "no", "order", "please", "tea", "thank you",
    "wait", "want", "water", "yes"
]

# ── Sequence / landmark constants ─────────────────────────────────────────────
SEQUENCE_LENGTH = 30    # frames per gesture clip
NUM_JOINTS      = 21    # MediaPipe hand joints
COORDS          = 3     # x, y, z per joint
INPUT_DIM       = NUM_JOINTS * COORDS   # = 63, flat feature vector per frame

# Hand skeleton connections (used by ST-GCN adjacency matrix)
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]

# ── Training hyper-parameters ─────────────────────────────────────────────────
EPOCHS        = 50
BATCH_SIZE    = 16
LEARNING_RATE = 1e-3
TEST_SPLIT    = 0.2     # 20 % of data for validation

# Data augmentation
AUGMENT        = True
AUG_MULTIPLIER = 5      # dataset becomes (1 + 5)× larger

# Sliding window extraction from videos
SLIDING_WINDOW = True
WINDOW_STRIDE  = 10     # step between clips (10 → 66 % overlap)

# ── Inference ─────────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.55   # increased for stability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Ensure output directories exist at import time ────────────────────────────
os.makedirs(DATA_DIR,    exist_ok=True)
os.makedirs(WEIGHTS_DIR, exist_ok=True)