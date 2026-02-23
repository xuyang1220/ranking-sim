from __future__ import annotations

import csv
import numpy as np
import pandas as pd

from ranking_sim.models.predictor import DummyPredictor, PandasLightGBMPredictor
from ranking_sim.ranking.policy import BidTimesPCTRPow
from ranking_sim.auction.mechanisms import SecondPriceSingleSlot
from ranking_sim.simulation.user import PositionBiasClickModel
from ranking_sim.simulation.runner import run_simulation
from scripts.run_sim import make_impressions_from_feature_bank


def main() -> None:
    alphas = np.linspace(0.2, 2.0, 10)

    predictor = PandasLightGBMPredictor(model_path="artifacts/lgb_ctr_model_8M.txt")
    # auction = SecondPriceSingleSlot()
    # user_model = PositionBiasClickModel(position_bias=[1.0])

    rows = []

    for alpha in alphas:
        policy = BidTimesPCTRPow(alpha=float(alpha))

        feature_bank = pd.read_parquet("artifacts/feature_bank.parquet")
        impressions = make_impressions_from_feature_bank(feature_bank, n_impressions=50_000, n_candidates=30, seed=7)

        user_model = PositionBiasClickModel(position_bias=[1.0, 0.7, 0.5, 0.3])
        n_slots = 4

        out = run_simulation(
            impressions=impressions,
            predictor=predictor,
            policy=policy,
            user_model=user_model,
            n_slots=n_slots,
            seed=42,
            keep_steps=False,
        )
        
        metrics = out.metrics
        rows.append({
            "alpha": float(alpha),
            "clicks_per_impression": metrics["clicks_per_impression"],
            "ctr_per_slot": metrics["ctr_per_slot"],
            "revenue": metrics["revenue"],
            "ecpm": metrics["ecpm"],
            "mean_ndcg": metrics["mean_ndcg"],
        })

        print(f"alpha={alpha:.2f}  clicks_per_impression={metrics['clicks_per_impression']:.4f}  ctr_per_slot={metrics['ctr_per_slot']:.4f}  Rev={metrics['revenue']:.2f} ecpm={metrics['ecpm']:.4f} mean_ndcg={metrics['mean_ndcg']:3f}")

    # Write CSV
    with open("alpha_sweep_lightGBM.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alpha", "clicks_per_impression", "ctr_per_slot", "revenue", "ecpm", "mean_ndcg"])
        writer.writeheader()
        writer.writerows(rows)

    print("\nSaved to alpha_sweep.csv")


if __name__ == "__main__":
    main()