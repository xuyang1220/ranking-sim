from __future__ import annotations

from dataclasses import dataclass

from ranking_sim.data.schema import SimStepResult


@dataclass
class MetricsAggregator:
    impressions: int = 0
    clicks: int = 0
    revenue: float = 0.0
    avg_shown: float = 0.0  # avg number of shown ads (K, but keeps you honest)

    def update(self, step: SimStepResult) -> None:
        self.impressions += 1
        self.clicks += int(step.total_clicks)
        self.revenue += float(step.total_revenue)
        self.avg_shown += float(len(step.shown_ad_ids))

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
            "avg_ads_shown": self.avg_shown / imps,
        }