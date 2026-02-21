from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol, List

from ranking_sim.data.schema import Impression, AuctionResult


class AuctionMechanism(Protocol):
    def run(self, impression: Impression, scores: Dict[int, float], pctr: Dict[int, float]) -> AuctionResult:
        """Run auction, return winner + price. (Single-slot for now.)"""


@dataclass(frozen=True)
class SecondPriceSingleSlot:
    """
    Second-price *CPC* pricing under a score-based ranking:
      score = bid * pCTR  (or something monotone in bid)
    For CPC, a common conversion is:
      price = second_score / winner_pctr
    capped by winner's bid.

    This is simplified but very useful for simulation experiments.
    """
    eps: float = 1e-12

    def run(self, impression: Impression, scores: Dict[int, float], pctr: Dict[int, float]) -> AuctionResult:
        if not impression.candidates:
            return AuctionResult(winner_ad_id=None, ranked_ad_ids=[], price_cpc=0.0)

        ranked: List[int] = sorted(scores.keys(), key=lambda ad_id: scores[ad_id], reverse=True)
        winner = ranked[0]

        # Determine second score
        if len(ranked) >= 2:
            second = ranked[1]
            second_score = float(scores[second])
        else:
            second_score = float(scores[winner])  # if only one, pay own "threshold" (simplified)

        winner_pctr = max(float(pctr[winner]), self.eps)

        # Convert second score to CPC threshold and cap by bid
        winner_bid = next(c.bid_cpc for c in impression.candidates if c.ad_id == winner)
        raw_price = second_score / winner_pctr
        price_cpc = float(min(winner_bid, raw_price))

        return AuctionResult(winner_ad_id=winner, ranked_ad_ids=ranked, price_cpc=price_cpc)