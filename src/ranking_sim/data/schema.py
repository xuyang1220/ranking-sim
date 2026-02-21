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
class SlotOutcome:
    position: int
    ad_id: int
    advertiser_id: int
    bid_cpc: float
    pctr: float
    clicked: bool
    price_cpc: float   # realized CPC if clicked else 0
    revenue: float     # same as price_cpc if clicked else 0


@dataclass(frozen=True)
class SimStepResult:
    imp_id: int
    shown_ad_ids: List[int]              # top-K
    slot_outcomes: List[SlotOutcome]     # length <= K
    total_clicks: int
    total_revenue: float