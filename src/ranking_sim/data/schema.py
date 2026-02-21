from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AdCandidate:
    ad_id: int
    advertiser_id: int
    bid_cpc: float  # CPC bid
    features: Dict[str, Any]


@dataclass(frozen=True)
class Impression:
    imp_id: int
    context: Dict[str, Any]
    candidates: List[AdCandidate]


@dataclass(frozen=True)
class AuctionResult:
    winner_ad_id: Optional[int]
    ranked_ad_ids: List[int]
    price_cpc: float  # what winner would pay if clicked


@dataclass(frozen=True)
class SimStepResult:
    imp_id: int
    winner_ad_id: Optional[int]
    winner_advertiser_id: Optional[int]
    winner_bid_cpc: float
    winner_pctr: float
    price_cpc: float
    clicked: bool
    revenue: float  # realized revenue (price_cpc if clicked else 0)