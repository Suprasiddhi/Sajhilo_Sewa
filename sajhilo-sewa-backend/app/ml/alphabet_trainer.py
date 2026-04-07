import os
import cv2
import mediapipe as mp
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import json

from app.ml.models.alphabet_model import AlphabetModel
from app.ml.config import WEIGHTS_DIR, DEVICE
from app.ml.preprocessing import run_mediapipe, extract_keypoints, normalize_keypoints

# Local hands detector instance for static images
try:
    _hands = mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.5
    )
except AttributeError:
    _hands = None 

def extract_landmarks(image):
    """
    Extract (21, 3) landmarks from an image using logic from preprocessing.py.
    Applies normalization to ensure position/scale invariance.
    """
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = run_mediapipe(rgb, _hands)
    landmarks = extract_keypoints(results)
    
    if np.all(landmarks == 0):
        return None
        
    return normalize_keypoints(landmarks)

def prepare_alphabet_dataset(data_dir: str):
    """
    Scans videos/alphabets/ and extracts landmarks for each image.
    Saves the dataset to a structured format for training.
    """
    labels = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
    label_to_idx = {label: i for i, label in enumerate(labels)}
    
    X = []
    y = []
    
    print(f"--- Dataset Preparation | labels={len(labels)} ---")
    
    for label in labels:
        label_path = os.path.join(data_dir, label)
        image_files = [f for f in os.listdir(label_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"  Processing {label}: {len(image_files)} images...")
        
        for img_file in image_files:
            img_path = os.path.join(label_path, img_file)
            img = cv2.imread(img_path)
            if img is None: continue
            
            landmarks = extract_landmarks(img)
            # Only add if hand was actually detected (not None)
            if landmarks is not None:
                # Flatten the (21,3) landmarks to (63,)
                X.append(landmarks.flatten())
                y.append(label_to_idx[label])
    
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    
    # Save the labels mapping for later inference
    with open(os.path.join(WEIGHTS_DIR, "alphabet_labels.json"), "w") as f:
        json.dump(labels, f)
        
    return X, y, labels

def train_alphabet_model(X, y, num_classes):
    """Trains the MLP on the landmark dataset."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    test_ds = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test))
    
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)
    
    model = AlphabetModel(input_size=63, num_classes=num_classes).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print("\n--- Training Alphabet Model ---")
    
    best_acc = 0
    epochs = 50
    
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            out = model(xb)
            loss = criterion(out, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for xb, yb in test_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                out = model(xb)
                correct += (out.argmax(1) == yb).sum().item()
                total += yb.size(0)
        
        acc = correct / total
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), os.path.join(WEIGHTS_DIR, "alphabet_best.pth"))
            
        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:02d} | Loss: {total_loss/len(train_loader):.4f} | Acc: {acc:.4f}" + (" (best)" if acc == best_acc else ""))
            
    print(f"\n✅ Training complete! Best Accuracy: {best_acc:.4f}")
    
    # Final Report
    model.load_state_dict(torch.load(os.path.join(WEIGHTS_DIR, "alphabet_best.pth")))
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(DEVICE)
            out = model(xb)
            all_preds.extend(out.argmax(1).cpu().numpy())
            all_targets.extend(yb.numpy())
            
    return model

if __name__ == "__main__":
    DATA_PATH = os.path.join("videos", "alphabets")
    if not os.path.exists(DATA_PATH):
        # Handle case where current directory is not root
        DATA_PATH = os.path.join("d:", "Sajhlo_Sewa", "sajhilo-sewa-backend", "videos", "alphabets")
        
    X, y, labels = prepare_alphabet_dataset(DATA_PATH)
    train_alphabet_model(X, y, len(labels))
