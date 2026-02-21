from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol

from ranking_sim.data.schema import Impression


class RankingPolicy(Protocol):
    def score(self, impression: Impression, pctr: Dict[int, float]) -> Dict[int, float]:
        """Return mapping {ad_id: score} used for ranking."""


@dataclass(frozen=True)
class BidTimesPCTR:
    def score(self, impression: Impression, pctr: Dict[int, float]) -> Dict[int, float]:
        scores: Dict[int, float] = {}
        for c in impression.candidates:
            scores[c.ad_id] = float(c.bid_cpc) * float(pctr[c.ad_id])
        return scores


@dataclass(frozen=True)
class BidTimesPCTRPow:
    alpha: float = 1.0

    def score(self, impression: Impression, pctr: Dict[int, float]) -> Dict[int, float]:
        scores: Dict[int, float] = {}
        for c in impression.candidates:
            scores[c.ad_id] = float(c.bid_cpc) * (float(pctr[c.ad_id]) ** float(self.alpha))
        return scores


@dataclass(frozen=True)
class BidOnly:
    def score(self, impression: Impression, pctr: Dict[int, float]) -> Dict[int, float]:
        return {c.ad_id: float(c.bid_cpc) for c in impression.candidates}