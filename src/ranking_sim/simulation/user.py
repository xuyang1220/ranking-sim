from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

import numpy as np


class UserModel(Protocol):
    def sample_click(self, pctr: float, position: int, rng: np.random.Generator) -> bool:
        """Return click outcome for shown ad."""


@dataclass(frozen=True)
class PositionBiasClickModel:
    """
    click_prob = pCTR * position_bias[position]
    """
    position_bias: List[float]

    def sample_click(self, pctr: float, position: int, rng: np.random.Generator) -> bool:
        if position < 0 or position >= len(self.position_bias):
            pb = 1.0
        else:
            pb = float(self.position_bias[position])

        click_prob = float(np.clip(float(pctr) * pb, 0.0, 1.0))
        return bool(rng.random() < click_prob)