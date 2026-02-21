from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, List

import numpy as np

from ranking_sim.data.schema import Impression, SimStepResult, SlotOutcome
from ranking_sim.models.predictor import Predictor
from ranking_sim.ranking.policy import RankingPolicy
from ranking_sim.simulation.user import UserModel
from ranking_sim.evaluation.metrics import MetricsAggregator


@dataclass
class RunOutput:
    metrics: dict
    n_steps: int
    steps: Optional[list[SimStepResult]] = None


def run_simulation(
    impressions: Iterable[Impression],
    predictor: Predictor,
    policy: RankingPolicy,
    user_model: UserModel,
    n_slots: int = 1,
    seed: int = 42,
    keep_steps: bool = False,
) -> RunOutput:
    rng = np.random.default_rng(seed)
    metrics = MetricsAggregator(ndcg_k=n_slots)
    steps: Optional[list[SimStepResult]] = [] if keep_steps else None

    n = 0
    for imp in impressions:
        n += 1
        pctr = predictor.predict_pctr(imp)
        scores = policy.score(imp, pctr)

        ranked: List[int] = sorted(scores.keys(), key=lambda ad_id: scores[ad_id], reverse=True)
        shown = ranked[: max(0, int(n_slots))]

        slot_outcomes: List[SlotOutcome] = []
        total_clicks = 0
        total_revenue = 0.0

        for pos, ad_id in enumerate(shown):
            c = next(x for x in imp.candidates if x.ad_id == ad_id)
            this_pctr = float(pctr[ad_id])

            clicked = user_model.sample_click(this_pctr, position=pos, rng=rng)

            # Minimal pricing: first-price CPC (pay bid if clicked)
            price_cpc = float(c.bid_cpc) if clicked else 0.0
            revenue = price_cpc

            total_clicks += int(clicked)
            total_revenue += revenue

            slot_outcomes.append(
                SlotOutcome(
                    position=pos,
                    ad_id=c.ad_id,
                    advertiser_id=c.advertiser_id,
                    bid_cpc=float(c.bid_cpc),
                    pctr=this_pctr,
                    clicked=clicked,
                    price_cpc=price_cpc,
                    revenue=revenue,
                )
            )

        step = SimStepResult(
            imp_id=imp.imp_id,
            shown_ad_ids=shown,
            slot_outcomes=slot_outcomes,
            total_clicks=total_clicks,
            total_revenue=float(total_revenue),
        )

        metrics.update(step)
        if steps is not None:
            steps.append(step)

    return RunOutput(metrics=metrics.finalize(), n_steps=n, steps=steps)