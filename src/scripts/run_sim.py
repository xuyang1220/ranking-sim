from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, List, Dict, Any

import numpy as np

from ranking_sim.data.schema import Impression, AdCandidate
from ranking_sim.models.predictor import DummyPredictor
from ranking_sim.ranking.policy import BidTimesPCTR
from ranking_sim.auction.mechanisms import SecondPriceSingleSlot
from ranking_sim.simulation.user import PositionBiasClickModel
from ranking_sim.simulation.runner import run_simulation


def make_synthetic_impressions(
    n_impressions: int,
    n_candidates: int = 20,
    seed: int = 123,
) -> Iterable[Impression]:
    rng = np.random.default_rng(seed)

    for imp_id in range(n_impressions):
        user_intent = float(rng.normal(0.0, 1.0))
        context: Dict[str, Any] = {"user_intent": user_intent}

        candidates: List[AdCandidate] = []
        for j in range(n_candidates):
            ad_id = imp_id * 10_000 + j
            advertiser_id = int(rng.integers(0, 200))

            # bids: lognormal-ish, clipped
            bid_cpc = float(np.clip(rng.lognormal(mean=-0.2, sigma=0.7), 0.05, 10.0))

            # ad_quality: normal
            ad_quality = float(rng.normal(0.0, 1.0))
            features = {"ad_quality": ad_quality}

            candidates.append(
                AdCandidate(
                    ad_id=ad_id,
                    advertiser_id=advertiser_id,
                    bid_cpc=bid_cpc,
                    features=features,
                )
            )

        yield Impression(imp_id=imp_id, context=context, candidates=candidates)


def main() -> None:
    # Components
    predictor = DummyPredictor(base_rate=0.02, noise_std=0.6)
    policy = BidTimesPCTR()
    auction = SecondPriceSingleSlot()
    user_model = PositionBiasClickModel(position_bias=[1.0])  # single-slot

    impressions = make_synthetic_impressions(n_impressions=50_000, n_candidates=30, seed=7)

    out = run_simulation(
        impressions=impressions,
        predictor=predictor,
        policy=policy,
        auction=auction,
        user_model=user_model,
        seed=42,
        keep_steps=False,
    )

    print("Done.")
    print(out.metrics)


if __name__ == "__main__":
    main()