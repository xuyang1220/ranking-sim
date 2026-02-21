from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol

import numpy as np

from ranking_sim.data.schema import Impression


class Predictor(Protocol):
    def predict_pctr(self, impression: Impression) -> Dict[int, float]:
        """Return mapping {ad_id: pCTR} for all candidates in impression."""


@dataclass
class DummyPredictor:
    """
    A simple pCTR generator for Day 1.
    Uses a sigmoid of (ad_quality + user_intent + noise).
    """
    base_rate: float = 0.02
    noise_std: float = 0.5

    def predict_pctr(self, impression: Impression) -> Dict[int, float]:
        rng = np.random.default_rng(impression.imp_id)  # stable per impression
        user_intent = float(impression.context.get("user_intent", 0.0))

        out: Dict[int, float] = {}
        for c in impression.candidates:
            ad_quality = float(c.features.get("ad_quality", 0.0))
            x = np.log(self.base_rate / max(1e-12, 1.0 - self.base_rate)) + 1.2 * ad_quality + 0.8 * user_intent
            x += rng.normal(0.0, self.noise_std)
            p = 1.0 / (1.0 + np.exp(-x))
            out[c.ad_id] = float(np.clip(p, 1e-6, 1.0 - 1e-6))
        return out


# Optional placeholder: swap in your trained model later
@dataclass
class LightGBMPredictor:
    model_path: str

    def __post_init__(self) -> None:
        # Keep skeleton import-light; implement later when you wire your real model.
        self._model = None

    def predict_pctr(self, impression: Impression) -> Dict[int, float]:
        raise NotImplementedError("Wire your LightGBM model here (load in __post_init__).")