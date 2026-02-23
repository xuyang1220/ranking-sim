from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol, Optional, Any, List

import numpy as np
import pandas as pd

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


@dataclass
class PandasLightGBMPredictor:
    """
    LightGBM predictor for models trained on pandas DataFrame.

    Expectation:
      For each AdCandidate c in impression.candidates:
        c.features is a dict mapping column name -> value
      covering all required columns (feature_names).
    """
    model_path: str
    feature_names: Optional[List[str]] = None  # if None, read from booster
    num_iteration: Optional[int] = None

    def __post_init__(self) -> None:
        try:
            import lightgbm as lgb
        except ImportError as e:
            raise ImportError("lightgbm is not installed. pip install lightgbm") from e

        self._lgb = lgb
        self._booster = lgb.Booster(model_file=self.model_path)

        if self.feature_names is None:
            self.feature_names = list(self._booster.feature_name())

    def predict_pctr(self, impression: Impression) -> Dict[int, float]:
        if not impression.candidates:
            return {}

        rows: List[Dict[str, Any]] = []
        ad_ids: List[int] = []

        assert self.feature_names is not None
        needed = set(self.feature_names)

        for c in impression.candidates:
            if not needed.issubset(c.features.keys()):
                missing = sorted(list(needed - set(c.features.keys())))[:10]
                raise KeyError(
                    f"Candidate {c.ad_id} missing required feature columns. "
                    f"Example missing columns: {missing} (showing up to 10)."
                )

            # Only take model-required columns, in correct order
            row = {k: c.features[k] for k in self.feature_names}
            rows.append(row)
            ad_ids.append(c.ad_id)

        X = pd.DataFrame(rows, columns=self.feature_names)

        p = self._booster.predict(X, num_iteration=self.num_iteration)
        p = np.asarray(p, dtype=np.float64).reshape(-1)
        p = np.clip(p, 1e-6, 1.0 - 1e-6)

        return {ad_id: float(pi) for ad_id, pi in zip(ad_ids, p)}