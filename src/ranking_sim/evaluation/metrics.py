from __future__ import annotations

from dataclasses import dataclass

from ranking_sim.data.schema import SimStepResult


@dataclass
class MetricsAggregator:
    impressions: int = 0
    clicks: int = 0
    revenue: float = 0.0

    # Simple diagnostics
    avg_winner_pctr_sum: float = 0.0
    avg_price_sum: float = 0.0

    def update(self, step: SimStepResult) -> None:
        self.impressions += 1
        self.clicks += int(step.clicked)
        self.revenue += float(step.revenue)

        self.avg_winner_pctr_sum += float(step.winner_pctr)
        self.avg_price_sum += float(step.price_cpc)

    def finalize(self) -> dict:
        imps = max(1, self.impressions)
        ctr = self.clicks / imps
        ecpm = (self.revenue / imps) * 1000.0

        return {
            "impressions": self.impressions,
            "clicks": self.clicks,
            "ctr": ctr,
            "revenue": self.revenue,
            "ecpm": ecpm,
            "avg_winner_pctr": self.avg_winner_pctr_sum / imps,
            "avg_price_cpc": self.avg_price_sum / imps,
        }