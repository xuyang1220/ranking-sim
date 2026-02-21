from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np

from ranking_sim.data.schema import Impression, SimStepResult
from ranking_sim.models.predictor import Predictor
from ranking_sim.ranking.policy import RankingPolicy
from ranking_sim.auction.mechanisms import AuctionMechanism
from ranking_sim.simulation.user import UserModel
from ranking_sim.evaluation.metrics import MetricsAggregator


@dataclass
class RunOutput:
    metrics: dict
    n_steps: int
    # Optional: store per-step results (turn off by default for speed)
    steps: Optional[list[SimStepResult]] = None


def run_simulation(
    impressions: Iterable[Impression],
    predictor: Predictor,
    policy: RankingPolicy,
    auction: AuctionMechanism,
    user_model: UserModel,
    seed: int = 42,
    keep_steps: bool = False,
) -> RunOutput:
    rng = np.random.default_rng(seed)
    metrics = MetricsAggregator()
    steps: Optional[list[SimStepResult]] = [] if keep_steps else None

    n = 0
    for imp in impressions:
        n += 1
        pctr = predictor.predict_pctr(imp)
        scores = policy.score(imp, pctr)
        auc = auction.run(imp, scores=scores, pctr=pctr)

        if auc.winner_ad_id is None:
            step = SimStepResult(
                imp_id=imp.imp_id,
                winner_ad_id=None,
                winner_advertiser_id=None,
                winner_bid_cpc=0.0,
                winner_pctr=0.0,
                price_cpc=0.0,
                clicked=False,
                revenue=0.0,
            )
        else:
            winner = next(c for c in imp.candidates if c.ad_id == auc.winner_ad_id)
            win_pctr = float(pctr[winner.ad_id])
            clicked = user_model.sample_click(win_pctr, position=0, rng=rng)
            revenue = float(auc.price_cpc) if clicked else 0.0

            step = SimStepResult(
                imp_id=imp.imp_id,
                winner_ad_id=winner.ad_id,
                winner_advertiser_id=winner.advertiser_id,
                winner_bid_cpc=float(winner.bid_cpc),
                winner_pctr=win_pctr,
                price_cpc=float(auc.price_cpc),
                clicked=clicked,
                revenue=revenue,
            )

        metrics.update(step)
        if steps is not None:
            steps.append(step)

    return RunOutput(metrics=metrics.finalize(), n_steps=n, steps=steps)