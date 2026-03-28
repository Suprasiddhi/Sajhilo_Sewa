"""
ml/ensemble.py
───────────────
EnsembleVoter combines TCN + BiLSTM + ST-GCN predictions via
weighted soft voting (averaging softmax probabilities).

Calibrate weights automatically on the validation set so the best
model gets the most influence.
"""
import json
import os

import numpy as np

from app.ml.config import WEIGHTS_DIR


class EnsembleVoter:
    """
    Combines predictions from three trainer objects.

    Args:
        tcn, bilstm, stgcn : trained *Trainer instances (have a .predict() method)
        gestures            : ordered list of class names
        weights             : [w_tcn, w_bilstm, w_stgcn] — normalised automatically
    """

    def __init__(self, tcn, bilstm, stgcn, gestures: list, weights=None):
        self._trainers = {"TCN": tcn, "BiLSTM": bilstm, "STGCN": stgcn}
        self.gestures  = gestures
        w = np.array(weights or [1.0, 1.0, 1.0], dtype=np.float32)
        self.weights   = w / w.sum()

    # ── Internal helpers ──────────────────────────────────────────

    def _all_probs(self, inputs: dict) -> dict:
        """Get softmax probability arrays from each model."""
        return {
            "TCN":    self._trainers["TCN"].predict(inputs["tcn"]),
            "BiLSTM": self._trainers["BiLSTM"].predict(inputs["bilstm"]),
            "STGCN":  self._trainers["STGCN"].predict(inputs["stgcn"]),
        }

    # ── Public API ────────────────────────────────────────────────

    def predict(self, inputs: dict):
        """
        Weighted average of all model probabilities → argmax.

        Returns:
            preds  : (N,) integer predictions
            probs  : (N, num_classes) ensemble probabilities
            names  : list of predicted gesture names
        """
        p = self._all_probs(inputs)
        probs = (
            self.weights[0] * p["TCN"]
            + self.weights[1] * p["BiLSTM"]
            + self.weights[2] * p["STGCN"]
        )
        preds = probs.argmax(axis=1)
        names = [self.gestures[i] for i in preds]
        return preds, probs, names

    def predict_single(self, inputs: dict) -> dict:
        """
        Predict one sample and return rich metadata (used for live inference).
        """
        all_p = self._all_probs(inputs)
        
        # Weighted average probabilities across models
        probs = (
            self.weights[0] * all_p["TCN"]
            + self.weights[1] * all_p["BiLSTM"]
            + self.weights[2] * all_p["STGCN"]
        )
        
        confidence = float(probs[0].max())
        pred_idx   = int(probs[0].argmax())
        gesture    = self.gestures[pred_idx]

        return {
            "gesture":    gesture,
            "confidence": confidence,
            "all_probs":  {g: float(probs[0][i]) for i, g in enumerate(self.gestures)},
            "model_votes": {
                k: self.gestures[int(v[0].argmax())]
                for k, v in all_p.items()
            },
        }

    def calibrate_weights(self, inputs: dict, y_val: np.ndarray):
        """
        Set ensemble weights proportional to each model's validation accuracy.
        The best model gets the highest weight automatically.
        """
        all_p = self._all_probs(inputs)
        accs  = np.array([
            (all_p[k].argmax(1) == y_val).mean()
            for k in ["TCN", "BiLSTM", "STGCN"]
        ])
        self.weights = accs / accs.sum()
        print(
            f"\n  Calibrated ensemble weights → "
            f"TCN: {self.weights[0]:.3f} | "
            f"BiLSTM: {self.weights[1]:.3f} | "
            f"ST-GCN: {self.weights[2]:.3f}"
        )

    def evaluate(self, inputs: dict, y_true: np.ndarray, label: str = "VALIDATION"):
        """Print per-model and ensemble accuracy."""
        preds, _, _ = self.predict(inputs)
        all_p       = self._all_probs(inputs)

        print("\n" + "=" * 55)
        print(f"  {label} — PER MODEL ACCURACY")
        print("=" * 55)
        for name, probs in all_p.items():
            acc = (probs.argmax(1) == y_true).mean()
            bar = "█" * int(acc * 20)
            print(f"  {name:<10}: {acc * 100:>6.2f}%  |{bar:<20}|")

        ensemble_acc = (preds == y_true).mean()
        bar = "█" * int(ensemble_acc * 20)
        print(f"  {'Ensemble':<10}: {ensemble_acc * 100:>6.2f}%  |{bar:<20}|  ← best")
        print("=" * 55)
        return ensemble_acc