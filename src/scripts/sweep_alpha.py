from __future__ import annotations

import csv
import numpy as np

from ranking_sim.models.predictor import DummyPredictor
from ranking_sim.ranking.policy import BidTimesPCTRPow
from ranking_sim.auction.mechanisms import SecondPriceSingleSlot
from ranking_sim.simulation.user import PositionBiasClickModel
from ranking_sim.simulation.runner import run_simulation
from scripts.run_sim import make_synthetic_impressions


def main() -> None:
    alphas = np.linspace(0.2, 2.0, 10)

    predictor = DummyPredictor(base_rate=0.02, noise_std=0.6)
    auction = SecondPriceSingleSlot()
    user_model = PositionBiasClickModel(position_bias=[1.0])

    rows = []

    for alpha in alphas:
        policy = BidTimesPCTRPow(alpha=float(alpha))

        impressions = make_synthetic_impressions(
            n_impressions=50_000,
            n_candidates=30,
            seed=7,  # keep fixed for fair comparison
        )

        out = run_simulation(
            impressions=impressions,
            predictor=predictor,
            policy=policy,
            auction=auction,
            user_model=user_model,
            seed=42,
            keep_steps=False,
        )

        metrics = out.metrics
        rows.append({
            "alpha": float(alpha),
            "ctr": metrics["ctr"],
            "revenue": metrics["revenue"],
            "ecpm": metrics["ecpm"],
        })

        print(f"alpha={alpha:.2f}  CTR={metrics['ctr']:.4f}  Rev={metrics['revenue']:.2f}")

    # Write CSV
    with open("alpha_sweep.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alpha", "ctr", "revenue", "ecpm"])
        writer.writeheader()
        writer.writerows(rows)

    print("\nSaved to alpha_sweep.csv")


if __name__ == "__main__":
    main()